'''
Main game control loop
'''

import pygame
from pygame.locals import *

import os
import time

from command import *
from location import *
from network import *
from server import *
from const import *
from gamescreen import *
from theorycraft import TheoryCraft
from world import *
from region import Region
import trap
import shop
import random
from keybindings import keystate

import levelup as lvl
import helpmenu

clock = pygame.time.Clock()

# Move to const:
LEVEL_MAX = 5

class Game(object):
    def __init__(self, port, serverip=None, state=None, player=None, **kwargs):
        '''
        This initializer sets up a ton of variables for tracking game state in many different categories,
            and initiates the connection to the server.  Then it kicks off a looping call to setup_game,
            which contains further initialization code that cannot run until the client has an active
            connection to the server.
        Parameters:
            port:       required for both host and client
            serverip:   None if hosting, required for client
            state:      state={SEED_KEY: "seed"} if new game, or
                        state="SaveFile.###" if loading game
            player:     player=("Name", "Race", "Class") if new player
                        player="SaveFile.###" if loading
        '''

        TheoryCraft.loadAll()   #Static method call, Devin's stuff.
        Sprites.load_all()      #Static method call to load sprites

        if state:   #We are the server here, setup state and pull out seed.
            loaded_state = State.load_world(state)
            self.seed = loaded_state[SEED_KEY]
            self.world = World(self.seed)
        else:       #We are a client, we'll need to get the seed from server
            self.seed = None
            self.world = None

        self.pane = None

        # Game state
        self.id = -2
        self.keystate = []
        self.running = False
        self.combat = False
        self.inside = False
        self.musicState = "overworld"
        self.fullScreen = False

        # Levelup state
        self.levelup = None

        # Help menu state
        self.helpTitle = None
        self.helpPageList = []
        self.helpPageIndex = 0

        # Shop state
        self.currentShop = None
        self.dialog_selection = 0

        # Selection state
        self.currentTarget = None
        self.panePersonIdList = []
        self.currentAbility = None
        self.abilityList = []
        self.currentItem = None
        self.itemList = []
        self.playerSaveFile = None

        self.rangeRegion = Region()
        self.targetRegion = Region()
        self.trapsRegion = Region()
        self.fieldsRegion = Region()

        self.turnTime = kwargs.get('turnlength')

        # Setup server if host
        self.port = port
        if serverip:
            self.serverip = serverip
        else:
            self.serverip = "localhost"
            self.gs = GameServer(self.world, self.port, self.turnTime)

        self.CDF = ClientDataFactory()
        reactor.connectTCP(self.serverip, self.port, self.CDF) #This is the connection to the server

        hardcore = False
        if kwargs.get('hardcore'):
            hardcore = True
        ironman = False
        if kwargs.get('ironman'):
            ironman = True

        if isinstance(player, tuple):
            person = Command("PERSON", "CREATE", id=None, \
                    location=Location((0, 0), (PANE_X/2, PANE_Y/2)), \
                    details=TheoryCraft.getNewPlayerCharacter(
                            name=player[0], race=player[1], characterClass=player[2],
                            ironman=ironman, hardcore=hardcore).dehydrate())
        else:
            self.playerSaveFile = player
            dehydrated_string = State.load_player(player)
            person = Command("PERSON", "LOAD", id=None, \
                    location=Location((0, 0), (PANE_X/2, PANE_Y/2)), \
                    details=dehydrated_string)

        self.setup = LoopingCall(self.setup_game, person)
        self.setup.start(0)

        reactor.run()

    def setup_game(self, person):
        '''
        This method keeps getting called until the client has a connection to the server, then sends
        its first request which is to create the player's character.  Then it waits for the world
        seed to be sent from the server, constructs the game world, and sets up the display.
        '''
        if not self.CDF.port:
            return

        # Create person on server
        if self.id == -2:
            self.CDF.send(person)
            self.id = -1

        # Obtain world seed from server
        if not self.CDF.queue.empty():
            command = self.CDF.queue.get()
            if command.type == "UPDATE" and command.action == "SEED":
                self.seed = command.seed

        if not self.seed:
            return

        self.world = World(self.seed)

        # Set up game engine
        self.screen = GameScreen()
        Combat.screen = self.screen

        # Start music
        pygame.mixer.music.set_volume(0.1)

        self.setup.stop()
        LoopingCall(self.game_loop).start(1.0 / DESIRED_FPS)

    def game_loop(self):
        '''
        I always thought the MAIN GAME LOOP would be a little bit hairier than this.  But this is what
        drives all the events and handling for the entire game.
        '''
        clock.tick()
        self.screen.set_fps(clock.get_fps())
        if hasattr(self, 'combatTurnStart'):
            turnTime = 1 - (time.time() - self.combatTurnStart) / self.turnTime if self.turnTime > 0 \
                    else 0
            self.screen.set_turntime(turnTime)

        self.check_queue()
        if self.pane:
            self.handle_events()
            self.handle_non_events()
            self.play_music()
            self.screen.update()

    def play_music(self, state=None, stop=False):
        '''
        Accepts one of 'overworld', 'battle', or 'town' for the state and plays music appropriate
            to that game state.
        If stop == True, will interrupt the currently playing track to move to the new state.
        '''

        if state and state != self.musicState:
            self.musicState = state
        musicDir = os.path.join('res', 'music', self.musicState)
        if not os.access(musicDir, os.F_OK):
            return

        if stop:
            pygame.mixer.music.fadeout(500)

        if not pygame.mixer.music.get_busy():
            music = os.path.join(musicDir, random.choice(os.listdir(musicDir)))
            pygame.mixer.music.load(music)
            pygame.mixer.music.play()

    def check_queue(self):
        '''
        Simply empties the queue that network.py fills up with commands from the server, and handles them
        '''

        while not self.CDF.queue.empty():
            command = self.CDF.queue.get()

            ###### CreatePerson ######
            if command.type == "PERSON" and (command.action == "CREATE" or command.action == "LOAD"):
                if self.id == -1:  # Need to setup the pane
                    self.id = command.id
                    if self.combat:
                        self.switch_panes(command.cPane, combat=self.combat)
                    else:
                        self.switch_panes(command.location)

                if command.action == "LOAD":
                    self.pane.person[command.id] = TheoryCraft.rehydratePlayer(command.details)
                elif command.action == "CREATE":
                    self.pane.person[command.id] = TheoryCraft.convertFromDetails(command.details)

                p = self.pane.person[command.id]
                p.location = command.location

                if command.id == self.id and self.combat:
                    self.currentAbility = self.pane.person[self.id].abilities[0]
                self.update_regions()

                imagepath = os.path.join(SPRITES_IMAGES_PATH, p.image)
                sizeAbbr = "M"
                if self.pane.person[command.id].team == "Monsters":
                    if self.pane.person[command.id].size == "Small":
                        sizeAbbr = "S"
                    elif self.pane.person[command.id].size == "Large":
                        sizeAbbr = "L"
                    elif self.pane.person[command.id].size == "Huge":
                        sizeAbbr = "H"
                persondict = {'location': command.location, 'image': imagepath, 'team': p.team, \
                    'HP': p.HP, 'totalHP': p.totalHP, 'MP': p.MP, \
                    'totalMP': p.totalMP, 'AP': p.AP, 'totalAP': p.totalAP, \
                    'level': p.level, 'name' : p.name, 'size' : sizeAbbr}
                self.screen.add_person(command.id, persondict)

                if hasattr(command, 'checkLevelup') and command.checkLevelup == True:
                    self.request_levelup()

            if command.type == "PERSON" and command.id not in self.pane.person:
                continue

            ###### MovePerson ######
            if command.type == "PERSON" and command.action == "MOVE":
                if hasattr(command, 'details'):
                    if self.pane.person[command.id].anim:
                        self.pane.person[command.id].anim.stop()
                        self.pane.person[command.id].anim = None
                    self.screen.update_person(command.id, {'location': command.location})
                else:
                    self.animate(command.id, self.pane.person[command.id].location, command.location, \
                            1.0 / self.pane.person[command.id].movementSpeed)

                self.pane.person[command.id].location = command.location
                self.update_regions()
                if self.combat and not self.valid_target():
                    self.cycle_targets()

            ###### RemovePerson ######
            if command.type == "PERSON" and command.action == "REMOVE":
                if command.id == self.id:
                    self.id = -1
                    for person in self.pane.person.values():
                        if person.anim:
                            person.anim.stop()
                    self.pane.person = {}
                else:
                    if self.pane.person[command.id].anim:
                        self.pane.person[command.id].anim.stop()

                    if self.currentTarget == command.id:
                        loc = self.pane.person[command.id].location
                        tile = self.pane.get_tile(loc.tile)
                        self.screen.update_tile(tile, loc)

                    self.screen.remove_person(command.id)
                    if command.id == self.currentTarget:
                        self.currentTarget = None
                    del self.pane.person[command.id]
                self.update_regions()
                if self.combat and not self.valid_target():
                    self.cycle_targets()

            ###### Hardcore Death Screen #####
            if command.type == "CLIENT" and command.action == "DEATH":
                if command.id == self.id:
                    keystate.inputState = "DEATH"
                    self.screen.show_menu_dialog(["Aw, shucks."], 'red', "You have died -- restart a new character.")

            ###### Levelup Player ######
            if command.type == "PERSON" and command.action == "REPLACE":
                if self.pane.person[command.id].anim:
                    self.pane.person[command.id].anim.stop()
                    self.pane.person[command.id].anim = None
                newPerson = TheoryCraft.rehydratePlayer(command.player)
                newPerson.location = self.pane.person[command.id].location
                newPerson.id = command.id
                self.pane.person[command.id] = newPerson

                self.screen.update_person(command.id, {'team' : self.pane.person[command.id].team,
                        'level': self.pane.person[command.id].level,
                        'HP' : self.pane.person[command.id].HP,
                        'totalHP' : self.pane.person[command.id].totalHP,
                        'MP' : self.pane.person[command.id].MP,
                        'totalMP' : self.pane.person[command.id].totalMP,
                        'totalAP' : self.pane.person[command.id].totalAP,
                        'AP' : self.pane.person[command.id].AP})

            ###### SAVE PERSON ######
            if command.type == "PERSON" and command.action == "SAVE":
                self.save_player()

            ###### DELETE PERSON -- HARDCORE DEATH ######
            if command.type == "PERSON" and command.action == "DELETE":
                State.delete_player()

            ###### Update Person Stats ######
            if command.type == "PERSON" and command.action == "UPDATE":
                for k, v in command.__dict__.iteritems():
                    if k not in ['type', 'action', 'id']:
                        if k != 'totalAP':
                            setattr(self.pane.person[command.id], k, v)
                        else:
                            self.pane.person[command.id].refreshAP()
                        if k in ['HP', 'MP', 'AP', 'totalAP']:
                            self.screen.update_person(command.id, {k: v, \
                                    'team': self.pane.person[command.id].team})

            ###### Switch Gear #####
            if command.type == "ABILITY" and command.action == "SWITCH_GEAR":
                self.pane.person[command.id].switchGear()

            ###### Character Progression ######
            if command.type == "PERSON" and command.action == "ADD_EXPERIENCE":
                self.pane.person[command.id].addExperience(command.experience)

            ###### Add Person Status ######
            if command.type == "PERSON" and command.action == "ADDSTATUS":
                #id, status, turns, image, displayText
                self.pane.person[command.id].addClientStatus(command.status, command.image, \
                        command.turns, command.displayText)
                statsdict = {'team' : self.pane.person[command.id].team,
                             'statusList' : self.pane.person[command.id].clientStatusView}
                self.screen.update_person(command.id, statsdict)

            ###### Remove Person Status ######
            if command.type == "PERSON" and command.action == "REMOVESTATUS":
                self.pane.person[command.id].removeClientStatus(command.status)
                statsdict = {'team' : self.pane.person[command.id].team,
                             'statusList' : self.pane.person[command.id].clientStatusView}
                self.screen.update_person(command.id, statsdict)

            ###### Update Statuses ######
            if command.type == "PERSON" and command.action == "DECREMENT_STATUSES":
                self.pane.person[command.id].decrementClientStatuses()
                statsdict = {'team' : self.pane.person[command.id].team,
                             'statusList' : self.pane.person[command.id].clientStatusView}
                self.screen.update_person(command.id, statsdict)

            ###### Update Text #####
            elif command.type == "UPDATE" and command.action == "TEXT":
                self.screen.show_text(command.text, color=command.color)

            ###### Start combat turn ######
            elif command.type == "UPDATE" and command.action == "TURNTIME":
                if hasattr(command, 'turnTime'):
                    self.turnTime = command.turnTime
                else:
                    self.combatTurnStart = time.time()
                    self.pane.fields.turn()
                    self.update_regions()

            ###### Initiate Combat ######
            elif command.type == "UPDATE" and command.action == "COMBAT":
                self.combat = command.combat
                if self.combat:
                    for each in self.pane.person:
                        each._clientStatusView = []
                    self.play_music("battle", True)
                    self.combatTurnStart = time.time()
                    keystate.inputState = "COMBAT"
                else:
                    self.screen.hide_dialog()
                    self.screen.set_turntime(0)
                    del self.combatTurnStart
                    for each in self.pane.person:
                        each._clientStatusView = []
                    self.play_music("overworld", True)
                    keystate.inputState = "OVERWORLD"
                    self.currentTarget = None
                    self.currentAbility = None
                    self.update_regions()
                    self.panePersonIdList = []
                    self.abilityList = []
                    self.currentItem = None
                    self.itemList = []

            ###### Update HP Buffers ######
            elif command.type == "UPDATE" and command.action == "HP_BUFFER":
                self.screen.update_person(command.id, {'buffedHP' : command.bufferSum, \
                        'totalHP' : self.pane.person[command.id].totalHP, \
                        'team' : self.pane.person[command.id].team})

            ###### Remove Item ######
            elif command.type == "ITEM" and command.action == "REMOVE":
                self.pane.person[command.id].inventory.removeItem(itemName=command.itemName)
                self.screen.update_person(command.id, {'totalAP' : self.pane.person[command.id].totalAP,
                                                       'AP' : self.pane.person[command.id].AP,
                                                       'team' : self.pane.person[command.id].team})
            ###### Get Item ######
            elif command.type == "ITEM" and command.action == "CREATE":
                item = TheoryCraft.rehydrateTreasure(command.itemIdentifier)
                self.pane.person[command.id].inventory.addItem(item)
                self.screen.update_person(command.id, {'totalAP' : self.pane.person[command.id].totalAP,
                                                       'AP' : self.pane.person[command.id].AP,
                                                       'team' : self.pane.person[command.id].team})

            elif command.type == "ITEM" and command.action == "EQUIP":
                item = TheoryCraft.rehydrateTreasure(command.itemIdentifier)
                self.pane.person[command.id].equip(item)
                self.screen.update_person(command.id, {'totalAP' : self.pane.person[command.id].totalAP,
                                                       'AP' : self.pane.person[command.id].AP,
                                                       'team' : self.pane.person[command.id].team})

            ###### Entity Operations ######

            elif command.type == "ENTITY":
                if command.action == "ANIMATE":
                    #Animate obstacle
                    self.animate_entity(command.location)
                if command.action == "REMOVE":
                    #Remove from pane
                    self.remove_entities(command.location)
                    self.screen.update_tile(self.pane.get_tile(command.location.tile), command.location)

            elif command.type == "CHEST":
                if command.action == "ADD":
                    self.pane.add_chest(command.chestType, command.level, command.location.tile)

                if command.action == "REMOVE":
                    self.remove_entities(command.location)
                self.screen.update_tile(self.pane.get_tile(command.location.tile), command.location)

            elif command.type == "ABILITY" and command.action == "PLACE_TRAP":
                placer = self.pane.person[command.id]
                command.abilityName = command.abilityName.replace("+", "")
                thisTrap = trap.Trap(name=command.abilityName, player=placer, location=command.targetLoc)
                self.pane.addTrap(command.targetLoc, thisTrap)
                self.update_regions()

            elif command.type == "TRAP" and command.action == "DISCOVER":
                thisTrap = trap.Trap(name=command.trapName, level=command.trapLevel, location=command.targetLoc)
                self.pane.addTrap(command.targetLoc, thisTrap)
                self.update_regions()

            elif command.type == "TRAP" and command.action == "REMOVE":
                self.pane.removeTrap(command.location)
                self.update_regions()

            elif command.type == "FIELD" and command.action == "ADD":
                self.pane.fields.add_field(command.name, command.location, command.radius, command.duration)
                self.update_regions()

            elif command.type == "FIELD" and command.action == "REMOVE":
                self.pane.fields.remove_field(command.location, command.name, command.all)
                self.update_regions()

            elif command.type == "CLIENT" and command.action == "QUIT":
                self.save_and_quit()

            elif command.type == "SHOP" and command.action == "OPEN":
                self.currentShop = shop.Shop(command.shopLevel, command.shopSeed)
                keystate.inputState = "SHOP"
                player = self.pane.person[self.id]
                self.currentShop.open(player, self.screen)

    def save_player(self):
        '''
        Calls State.save_player with our client side player object
        '''

        if not self.id in self.pane.person:
            return
        State.save_player(self.pane.person[self.id])

    def save_and_quit(self):
        '''
        Calls self.save_player() and then quits
        '''

        if hasattr(self, 'gs'):
            self.gs.save_all()
        self.save_player()#player_string)
        self.quit()

    def save_no_quit(self):
        '''
        Send the signal to the server to save the gamestate, but don't quit just yet
        '''
        if hasattr(self, 'gs'):
            self.gs.save_all(shutdown=False)
        self.save_player()#player_string)

    def quit(self):
        '''
        Does this really need documentation?
        '''
        reactor.stop()

    def handle_non_events(self):
        '''
        I wasn't sure what else to call this method, but it checks for things that need to happen
        even if no events have fired to initiate them.  Things like starting another run animation
        if the character is running, or handling an arrow key that is still held down get called here
        '''
        if self.running:
            self.move_person()
        if hasattr(self, 'pane') and hasattr(self.pane, 'person') and self.id in self.pane.person and \
                not self.pane.person[self.id].anim and keystate.direction("MOVEMENT"):
            self.move_person(keystate.direction("MOVEMENT"), 1)
        if keystate.direction("DIALOG") and time.time() >= keystate.keyTime + keystate.typematicRate:
            self.screen.move_dialog(keystate.direction("DIALOG"))
            keystate.keyTime = time.time()
            if keystate.inputState == "BINDINGS":
                sel = self.screen.get_dialog_selection()
                if sel[0] == 0 and keystate.direction("DIALOG") in [2, 8]:
                    self.dialog_selection = sel[1]
                    self.update_bindings()

    def handle_events(self):
        '''
        Update the current key state information, get back any applicable event strings, and then
        act on them.
        '''
#        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
#            print "Event: ", event
            #### General commands ####
            if event.type == QUIT:
                self.save_and_quit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 3 and keystate.inputState == "TARGET":
                self.currentTarget = Location(event.pos[0] / TILE_SIZE, event.pos[1] / TILE_SIZE)
                self.attempt_attack()
                keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                self.currentAbility = self.pane.person[self.id].abilities[0]
                self.update_regions()
                if not self.valid_target():
                    self.cycle_targets()
            elif event.type == KEYUP:
                #Update the current key state information
                keystate(event)
            elif event.type == KEYDOWN:
                #Update the current key state information
                e = keystate(event)
                if e == "QUIT":
                    self.display_save_menu()
                if e == "FORCEQUIT":
                    self.save_and_quit()

                #This is a family of events that happen when the character is in a movement state
                elif keystate.direction("MOVEMENT"):
                    self.move_person(keystate.direction("MOVEMENT"))

                #This is a family of events that allow cursor movement inside of any dialog menu
                elif keystate.direction("DIALOG"):
                    self.screen.move_dialog(keystate.direction("DIALOG"))
                    keystate.keyTime = time.time() + 2 * keystate.typematicRate
                    if keystate.inputState == "BINDINGS":
                        sel = self.screen.get_dialog_selection()
                        if sel[0] == 0 and keystate.direction("DIALOG") in [2, 8]:
                            self.dialog_selection = sel[1]
                            self.update_bindings()

                #This is a family of events that allow cursor movement when targeting a spell or ability
                elif keystate.direction("TARGET"):
                    newloc = self.currentTarget.move(keystate.direction("TARGET"))
                    if newloc.pane == self.currentTarget.pane and newloc in self.rangeRegion:
                        self.currentTarget = newloc
                        self.update_regions()
                elif e in ["TARGETACCEPT", "TARGETCANCEL"]:
                    if e == "TARGETACCEPT":
                        self.attempt_attack()
                    keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                    self.currentAbility = self.pane.person[self.id].abilities[0]
                    self.update_regions()
                    if not self.valid_target():
                        self.cycle_targets()

                elif e == "SCROLLTOP":
                    self.screen.scroll_up(1000)
                elif e == "SCROLLUP":
                    self.screen.scroll_up(1)
                elif e == "SCROLLDOWN":
                    self.screen.scroll_down(1)
                elif e == "SCROLLBOTTOM":
                    self.screen.scroll_down(1000)
                elif e == "TOGGLEFULLSCREEN":
                    pygame.display.set_mode((PANE_X * TILE_SIZE + 256, \
                            max(PANE_Y * TILE_SIZE, 20 * TILE_SIZE)), \
                            pygame.FULLSCREEN if not self.fullScreen else 0)
                    self.fullScreen = not self.fullScreen
                    self.screen.redraw()

                elif e == "DEATHCONTINUE":
                    self.screen.hide_dialog()
                    keystate.inputState = "OVERWORLD"
                    self.screen.show_text("You have begun anew, at level 1.")

                ### Save Menu ###
                elif e == "HELPMENUOPEN":
                    keystate.inputState = "HELPMENU"
                    topPage = helpmenu.topPages['Akintu Help Menu']
                    self.helpTitle = topPage['title']
                    self.screen.show_menu_dialog(topPage['options'], topPage['color'], topPage['title'])

                elif e == "SAVEMENUACCEPT":
                    selection = self.screen.hide_dialog()
                    # 0 -- 'Save and Return',
                    # 1 -- 'Save and Quit',
                    # 2 -- 'Return without Saving'
                    # 3 -- 'Help Menu'
                    if selection == 0:
                        self.save_no_quit()
                        keystate.inputState = "OVERWORLD"
                        self.screen.show_text("Game Saved.", color='white')
                    elif selection == 1:
                        self.save_and_quit()
                    elif selection == 2:
                        keystate.inputState = "OVERWORLD"
                    elif selection == 3:
                        keystate.inputState = "HELPMENU"
                        topPage = helpmenu.topPages['Akintu Help Menu']
                        self.helpTitle = topPage['title']
                        self.screen.show_menu_dialog(topPage['options'], topPage['color'], topPage['title'])
                elif e == "SAVEMENUCANCEL":
                    self.screen.hide_dialog()
                    keystate.inputState = "OVERWORLD"
                    self.screen.show_text("Save Aborted.", color='white')

                elif e == "HELPMENUACCEPT":
                    selectionNum = self.screen.get_dialog_selection()
                    selection = None
                    if selectionNum is not None:
                        resultDuple = helpmenu.navigateDownPage(self.helpTitle, selectionNum, keystate)
                        if resultDuple[1] == "Dict":
                            currentPage = resultDuple[0]
                            self.helpTitle = currentPage['title']
                            self.screen.show_menu_dialog(currentPage['options'], currentPage['color'], currentPage['title'])
                        elif resultDuple[1] == "Path":
                            self.helpTitle = resultDuple[2]
                            self.helpPageList = resultDuple[0]
                            self.helpPageIndex = 0
                            self.screen.show_text_dialog(self.helpPageList[self.helpPageIndex], self.helpTitle)
                        else:
                            self.helpTitle = "Status Effect Listing"
                            self.helpPageList = resultDuple[0]
                            self.helpPageIndex = 0
                            text = "All Status Effects; press B for back or N for next."
                            self.screen.show_tiling_dialog(text, self.helpPageList[self.helpPageIndex], bgcolor='lightblue')

                elif e == "HELPMENUTOP":
                    self.helpPageList = []
                    pageDict = helpmenu.navigateUpPage(self.helpTitle)
                    if not pageDict:
                        if self.combat:
                            self.screen.hide_dialog()
                            keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                        else:
                            menuItems = ['Save and Return', 'Save and Quit', 'Return without Saving', 'In-Game Help']
                            self.screen.show_menu_dialog(menuItems)
                            keystate.inputState = "SAVEMENU"
                    else:
                        self.helpTitle = pageDict['title']
                        self.screen.show_menu_dialog(pageDict['options'], pageDict['color'], pageDict['title'])

                elif e == "HELPMENUNEXT":
                    if self.helpPageList:
                        if self.helpPageIndex + 1 < len(self.helpPageList):
                            self.helpPageIndex += 1
                        else:
                            self.helpPageIndex = 0
                        if self.helpTitle == "Status Effect Listing":
                            text = "All Status Effects; press B for back or N for next."
                            self.screen.show_tiling_dialog(text, self.helpPageList[self.helpPageIndex], bgcolor='lightblue')
                        else:
                            self.screen.show_text_dialog(self.helpPageList[self.helpPageIndex], self.helpTitle)

                elif e == "HELPMENUPREVIOUS":
                    if self.helpPageList:
                        if self.helpPageIndex - 1 >= 0:
                            self.helpPageIndex -= 1
                        else:
                            self.helpPageIndex = len(self.helpPageList) - 1
                        if self.helpTitle == "Status Effect Listing":
                            text = "All Status Effects; press B for back or N for next."
                            self.screen.show_tiling_dialog(text, self.helpPageList[self.helpPageIndex], bgcolor='lightblue')
                        else:
                            self.screen.show_text_dialog(self.helpPageList[self.helpPageIndex], self.helpTitle)

                ### Character Sheet ###
                elif e == "CHARSHEETOPEN":
                    self.display_character_sheet()
                    keystate.inputState = "CHARSHEET"
                elif e == "CHARSHEETCLOSE":
                    self.screen.hide_dialog()
                    keystate.inputState = "OVERWORLD" if not self.combat else "COMBAT"
                elif e == "CHARSHEETMAIN":
                    self.display_character_sheet()
                elif e == "CHARSHEETABILITIES":
                    self.display_character_abilities()
                elif e == "CHARSHEETSPELLS":
                    self.display_character_spells()
                elif e == "CHARSHEETPASSIVES":
                    self.display_character_passives()
                elif e == "CHARSHEETTRAITS":
                    self.display_character_traits()

                ### Levelup Commands ###
                elif e == "LEVELUPADVANCE":
                    upgradedHero = self.levelup.advance()
                    if upgradedHero:
                        # Upgraded Hero is "False" until the levelup is finished. Then it is a dehydrated hero.
                        newHero = TheoryCraft.rehydratePlayer(upgradedHero)
                        newHero.location = self.pane.person[self.id].location
                        newHero.id = self.id
                        self.pane.person[self.id] = newHero
                        keystate.inputState = "OVERWORLD"
                        self.CDF.send(Command("PERSON", "REPLACE", id=self.id, player=upgradedHero))
                        self.screen.update_person(self.id, {'team' : "Players",
                                                            'level': self.pane.person[self.id].level,
                                                            'HP' : self.pane.person[self.id].HP,
                                                            'totalHP' : self.pane.person[self.id].totalHP,
                                                            'MP' : self.pane.person[self.id].MP,
                                                            'totalMP' : self.pane.person[self.id].totalMP,
                                                            'totalAP' : self.pane.person[self.id].totalAP,
                                                            'AP' : self.pane.person[self.id].AP})

                ### Shop Commands ###
                elif e == "SHOPOPEN":
                    self.request_shop()
                elif e == "SHOPTRANSACTION":
                    if self.screen.get_dialog_selection()[0] == 0:
                        self.currentShop.sell(self.screen.get_dialog_selection()[1], self.pane.person[self.id], self.screen)
                    else:
                        self.currentShop.buy(self.screen.get_dialog_selection()[1], self.pane.person[self.id], self.screen)
                elif e == "SHOPCLOSE":
                    if self.pane.person[self.id].anim:
                        self.pane.person[self.id].anim.stop()
                        self.pane.person[self.id].anim = None
                    self.screen.update_person(self.id, {'location': self.pane.person[self.id].location})
                    hero = self.currentShop.close(self.pane.person[self.id], self.screen)
                    if hero:
                        # Hero is None until the shop phase is finished.  Then it is a dehydrated hero.
                        newHero = TheoryCraft.rehydratePlayer(hero)
                        newHero.location = self.pane.person[self.id].location
                        newHero.id = self.id
                        self.pane.person[self.id] = newHero
                        keystate.inputState = "OVERWORLD"
                        self.CDF.send(Command("PERSON", "REPLACE", id=self.id, player=hero))
                        self.screen.update_person(self.id, {'team' : "Players",
                                                            'level': self.pane.person[self.id].level,
                                                            'HP' : self.pane.person[self.id].HP,
                                                            'totalHP' : self.pane.person[self.id].totalHP,
                                                            'MP' : self.pane.person[self.id].MP,
                                                            'totalMP' : self.pane.person[self.id].totalMP,
                                                            'totalAP' : self.pane.person[self.id].totalAP,
                                                            'AP' : self.pane.person[self.id].AP})

                ### Inventory Management ###
                elif e == "INVENTORYOPEN":
                    self.open_inventory()
                elif e == "INVENTORYEQUIPMH" and self.screen.get_dialog_selection()[0] == 0:
                    self.pane.person[self.id].equipMainHand(self.screen.get_dialog_selection()[1], self.screen)
                elif e == "INVENTORYEQUIPMHALT" and self.screen.get_dialog_selection()[0] == 0:
                    self.pane.person[self.id].equipMainHand(self.screen.get_dialog_selection()[1], self.screen, alternate=True)
                elif e == "INVENTORYDROP" and self.screen.get_dialog_selection()[0] == 0:
                    self.pane.person[self.id].dropItem(self.screen.get_dialog_selection()[1], self.screen)
                elif e == "INVENTORYUNEQUIP" and self.screen.get_dialog_selection()[0] == 1:
                    self.pane.person[self.id].unequipGear(self.screen.get_dialog_selection()[1], \
                            self.screen.get_dialog_selection()[2], self.screen, color=self.screen.get_dialog_selection()[3])
                elif e == "INVENTORYEQUIPOH" and self.screen.get_dialog_selection()[0] == 0:
                    self.pane.person[self.id].equipOffHand(self.screen.get_dialog_selection()[1], self.screen)
                elif e == "INVENTORYEQUIPOHALT" and self.screen.get_dialog_selection()[0] == 0:
                    self.pane.person[self.id].equipOffHand(self.screen.get_dialog_selection()[1], self.screen, alternate=True)
                elif e == "INVENTORYCLOSE":
                    self.screen.hide_dialog()
                    newlyEquippedPlayer = self.pane.person[self.id].dehydrate()
                    if newlyEquippedPlayer:
                        self.CDF.send(Command("PERSON", "REPLACE", id=self.id, player=newlyEquippedPlayer))
                        keystate.inputState = "OVERWORLD"
                        self.screen.update_person(self.id, {'team' : "Players",
                                                            'level': self.pane.person[self.id].level,
                                                            'HP' : self.pane.person[self.id].HP,
                                                            'totalHP' : self.pane.person[self.id].totalHP,
                                                            'MP' : self.pane.person[self.id].MP,
                                                            'totalMP' : self.pane.person[self.id].totalMP,
                                                            'totalAP' : self.pane.person[self.id].totalAP,
                                                            'AP' : self.pane.person[self.id].AP})

                ## Consumable Use ###
                elif e == "CONSUMABLEOPEN":
                    self.open_consumables()
                elif e == "CONSUMABLEUSE":
                    self.currentItem = self.pane.person[self.id].inventory.allConsumables[self.screen.hide_dialog()[1]]
                    self.use_item()
                    keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                elif e == "CONSUMABLECANCEL":
                    self.screen.hide_dialog()
                    self.screen.show_text("Item use cancelled.")
                    keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"

                ### Combat Only Commands ###
                elif e == "ABILITIESOPEN":
                    keystate.inputState = "ABILITIES"
                    self.choose_ability()
                elif e == "SPELLSOPEN":
                    keystate.inputState = "SPELLS"
                    self.choose_spell()
                elif e in ["ABILITIESSELECT", "SPELLSSELECT"]:
                    if e == "ABILITIESSELECT":
                        self.currentAbility = self.pane.person[self.id].abilities[self.screen.hide_dialog()]
                    elif e == "SPELLSSELECT":
                        self.currentAbility = self.pane.person[self.id].spellList[self.screen.hide_dialog()]

                    if self.currentAbility.targetType in ["location", "trap"]:
                        keystate.inputState = "TARGET"
                        self.currentTarget = self.pane.person[self.id].location
                    else:
                        keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                    self.update_regions()
                    if not self.valid_target():
                        self.cycle_targets()

                #### Miscellaneous events ###
                elif e == "SWITCHGEAR":
                    self.switch_gear()
                elif e == "CYCLETARGETF":
                    self.cycle_targets()
                elif e == "CYCLETARGETB":
                    self.cycle_targets(reverse=True)
                elif e == "ACTIVATESELECTED":
                    self.attempt_attack()
                elif e == "ENDTURN":
                    self.force_end_turn()
                elif e == "SELECTSELF":
                    self.select_self()
                elif e == "ANALYZETARGET":
                    self.display_target_details()
                elif e == "DISPLAYCOMBATSTATUS":
                    self.display_combat_status()
                elif e == "CLOSECOMBATSTATUS":
                    self.screen.hide_dialog()
                    if self.combat:
                        keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                    else:
                        keystate.inputState = "OVERWORLD"

                ### Keybinding dialog ###
                elif e == "BINDINGSOPEN":
                    keystate.inputState = "BINDINGS"
                    text = "Select an event, then press Insert or Delete to modify key bindings"
                    self.screen.show_dual_pane_dialog(text, [Item("", "")], [Item("", "")], 'gray')
                    self.update_bindings()
                elif e == "BINDINGSCLOSE":
                    keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
                    self.dialog_selection = 0
                    self.screen.hide_dialog()
                elif e == "BINDINGSADD":
                    self.screen.update_dual_pane_dialog_text("Please enter new key combination")
                    keystate.inputState = "BINDINGSADD"
                elif e == "BINDINGSADDED":
                    text = "Select an event, then press Insert or Delete to modify key bindings"
                    self.screen.update_dual_pane_dialog_text(text)
                    keystate.inputState = "BINDINGS"
                    keystate.add_binding(keystate.bindings.keys()[self.dialog_selection])
                    self.update_bindings()
                elif e == "BINDINGSDELETE":
                    sel = self.screen.get_dialog_selection()
                    if sel[0] == 1:
                        keystate.delete_binding(keystate.bindings.keys()[self.dialog_selection], sel[1])
                        self.update_bindings()

                ### Strictly non-combat commands ###
                elif e == "GETITEM":
                    self.get_item()
                elif e == "BASHCHEST":
                    self.break_in()
                elif e == "STARTLEVELUP":
                    self.request_levelup(False)
                elif e == "STARTRESPEC":
                    self.request_respec()
                elif e == "CHEATLEVELUP":
                    self.request_levelup(True)

                ### Debug codes ###
                elif e == "CHEAT CODE":
                    print "You found the secret code!"
                elif e == "SHOWINPUTSTATE":
                    print "Keyboard input state: %s" % keystate.inputState
                elif e == "SHOWPANEPIDS":
                    print "Person IDs on pane: %s" % str(self.pane.person.keys())
                elif e == "SHOWPATHS":
                    if len(self.fieldsRegion):
                        self.pane.fields.remove_field(self.fieldsRegion[0])
                        self.update_regions()
                    spell = random.choice(["Smoke Screen", "Zone of Silence", "Pit"])
                    p = self.pane.person[self.id].location.pane
                    loc1 = Location(p, (random.randint(0, PANE_X - 1), random.randint(0, PANE_Y - 1)))
                    loc2 = Location(p, (random.randint(0, PANE_X - 1), random.randint(0, PANE_Y - 1)))
#                    loc1 = Location(0, 0)
#                    loc2 = Location(PANE_X - 1, PANE_Y - 1)
                    path = Region(self.gs.find_path(loc1, loc2, self.id if self.combat else None))
                    self.pane.fields.add_field(spell, path)
                    self.update_regions()

    def get_item(self):
        '''
        If player is on an item, pick it up (the top item).
        If player is next to a treasure chest, attempt to open it.
        If the chest is locked, send a message to the screen.
        If you are a thief, attempt to unlock it.
        If the chest is unlocked, distribute treasure to this player
           and all others on this pane.
        '''
        self.CDF.send(Command("PERSON", "OPEN", id=self.id))

    def break_in(self):
        '''
        Used to attempt to bash a locked chest.
        '''
        self.CDF.send(Command("PERSON", "BASHCHEST", id=self.id))

    def request_levelup(self, debug=False):
        '''
        Used to start the levelup process; includes a shortcut for debugging
        purposes.
        '''
        player = self.pane.person[self.id]
        if player.experience >= player.getExpForNextLevel() and player.level < LEVEL_MAX:
            player.level += 1
            keystate.inputState = "LEVELUP"
            self.levelup = lvl.Levelup(player, self.screen)
            self.levelup.next()
        elif debug:
            player.addExperience(75)
            if player.experience >= player.getExpForNextLevel() and player.level < LEVEL_MAX:
                self.screen.show_text("LEVEL UP!" , color='magenta')
        else:
            pass

    def request_respec(self):
        '''
        Begins the respecialization process.
        '''
        action = Command("RESPEC", "REQUESTRESPEC", id=self.id)
        self.CDF.send(action)

    def request_shop(self):
        '''
        Asks the server for a shop to open.
        '''
        action = Command("SHOP", "REQUESTSHOP", id=self.id)
        self.CDF.send(action)

    def display_save_menu(self):
        '''
        Display the top (overworld) menu.
        '''
        menuItems = ['Save and Return', 'Save and Quit', 'Return without Saving', 'In-Game Help']
        self.screen.show_menu_dialog(menuItems)
        keystate.inputState = "SAVEMENU"

    def open_inventory(self):
        '''
        Opens the character's inventory.
        '''
        keystate.inputState = "INVENTORY"
        player = self.pane.person[self.id]
        isEquipment = True
        text = "Looking in your bag..."
        eq = player.equippedItems.allGear
        gold = `player.inventory.gold` + " gold"
        if not eq:
            eq = []
        inv = player.inventory.allItems
        if not inv:
            inv = []
        capacity = `player.inventoryWeight` + "/" + `player.inventoryCapacity`
        if not eq and not inv:
            keystate.inputState = "OVERWORLD"
            return
        self.screen.show_item_dialog(text, inv, eq, isEquipment, bgcolor='tan', capacity=capacity, gold=gold)

    def open_consumables(self):
        '''
        Opens a subset of the character's inventory while in combat so
        he or she can select and use consumable items.
        '''
        keystate.inputState = "CONSUMABLE"
        player = self.pane.person[self.id]
        cons = player.inventory.allConsumables
        if cons:
            isEquipment = False
            text = "Select a consumable"
            self.screen.show_item_dialog(text, cons, [], isEquipment, bgcolor='tan')
        else:
            keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"

    def choose_ability(self):
        '''
        Opens the ability selection screen in combat.
        '''
        text = "Select an Ability"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].abilities
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def choose_spell(self):
        '''
        Opens the spell selection screen in combat.
        '''
        text = "Select a Spell"
        bgcolor = "lightblue"
        itemslist = self.pane.person[self.id].spellList
        if not itemslist:
            keystate.inputState = "COMBAT" if self.combat else "OVERWORLD"
            return
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def move_person(self, direction=0, distance=1):
        '''
        Accept a direction and distance, then validate a movement in that direction, send the request
        to the server, start animations, update running state
        '''
        if self.running:
            if direction:
                self.running = 0
            else:
                direction = self.running

        if self.pane.person[self.id].anim:
            return False

        newloc = self.pane.person[self.id].location.move(direction, distance)
        if self.combat and newloc.pane != (0, 0):
            return False
        if (not self.pane.person[self.id].anim) and ((self.pane.person[self.id].location.pane == \
                newloc.pane and self.pane.is_tile_passable(newloc) and \
                newloc.tile not in [x.location.tile for x in self.pane.person.values()]) or \
                self.pane.person[self.id].location.pane != newloc.pane):

            if "SHIFT" in keystate and not self.combat:
                self.running = direction

            if not self.combat or (self.pane.person[self.id].remainingMovementTiles > 0 or \
                    self.pane.person[self.id].AP >= self.pane.person[self.id].totalMovementAPCost):
                self.CDF.send(Command("PERSON", "MOVE", id=self.id, location=newloc))
                if self.pane.person[self.id].location.pane == newloc.pane:
                    self.animate(self.id, self.pane.person[self.id].location, newloc, \
                            1.0 / self.pane.person[self.id].movementSpeed)
                    self.pane.person[self.id].location = newloc
        elif self.pane.person[self.id].location.direction != direction \
                and self.pane.is_tile_passable(self.pane.person[self.id].location):
            self.pane.person[self.id].location.direction = direction

            statsdict = {}
            statsdict['location'] = self.pane.person[self.id].location
            self.screen.update_person(self.id, statsdict)

            self.CDF.send(Command("PERSON", "MOVE", id=self.id, \
                    location=self.pane.person[self.id].location))

        if self.combat:
            self.update_regions()
            if not self.valid_target():
                self.cycle_targets()

    def display_character_sheet(self):
        '''
        Displays the client's view of the character sheet.
        '''
        player = self.pane.person[self.id]
        self.screen.show_character_dialog(player, abilitykey=keystate.get_key("CHARSHEETABILITIES"),
                spellkey=keystate.get_key("CHARSHEETSPELLS"),
                passivekey=keystate.get_key("CHARSHEETPASSIVES"),
                traitkey=keystate.get_key("CHARSHEETTRAITS"))

    def display_character_abilities(self):
        '''
        Within the character sheet, display the active abilities this
        character knows.
        '''
        text = "Active Abilities (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].abilities
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def display_character_passives(self):
        '''
        Within the character sheet, display the passive abilities this
        character knows.
        '''
        text = "Passive Abilities (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].passiveAbilities
        itemslist = [x for x in itemslist if "--IGNORE--" not in x.name]
        if not itemslist:
            self.display_character_sheet()
            return
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def display_character_spells(self):
        '''
        Within the character sheet, display the spells this
        character knows.
        '''
        if self.pane.person[self.id].growthType == "Non-Caster":
            self.display_character_sheet()
            return
        text = "Learned Spells (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].spellList
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def display_character_traits(self):
        '''
        Within the character sheet, display the traits this
        character has learned.
        '''
        if self.pane.person[self.id].level == 1:
            self.display_character_sheet()
            return
        text = "Chosen Traits (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].traits
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def force_end_turn(self):
        '''
        Send a command to the server to end this players turn (early?)
        '''
        ap = self.pane.person[self.id].AP
        movesLeft = self.pane.person[self.id].remainingMovementTiles
        if ap > 0 or movesLeft > 0:
            action = Command("ABILITY", "END_TURN", id=self.id)
            self.CDF.send(action)

    def attempt_attack(self):
        '''
        Ask the server to make this player use an attack (ability/spell).
        '''
        if not self.currentTarget:
            print "No target selected."
            return
        if not self.currentAbility:
            print "No ability selected."
            return
        tempTarget = [pid for pid, p in self.pane.person.iteritems() \
                if p.location == self.currentTarget and p.team == "Monsters"]
        tempTarget = tempTarget[0] if len(tempTarget) > 0 else None
        anarchistTrap = self.pane.person[self.id].characterClass == "Anarchist" and tempTarget
        if self.currentAbility.targetType == "trap" and not anarchistTrap:
            self.CDF.send(Command("ABILITY", "PLACE_TRAP", id=self.id, \
                    targetLoc=self.currentTarget, \
                    abilityName=self.currentAbility.name))
        else:
            self.CDF.send(Command("ABILITY", "ATTACK", id=self.id, targetId=self.currentTarget \
                    if not anarchistTrap else tempTarget, abilityName=self.currentAbility.name))

    def use_item(self):
        '''
        Actually use a selected item.
        '''
        if not self.currentItem or \
          self.currentItem not in self.pane.person[self.id].inventory.allConsumables:
            self.screen.show_text("No item selected", color='white')
            return
        self.CDF.send(Command("ITEM", "USE", id=self.id, itemName=self.currentItem.name))
        self.currentItem = None

    def switch_gear(self):
        '''
        Swap gear between main and alternate sets of wepaons/shield
        '''
        player = self.pane.person[self.id]
        if not player.equippedItems.alternateWeapon:
            print "DEBUG: No weapon found"
            return
        else:
            self.CDF.send(Command("ABILITY", "SWITCH_GEAR", id=self.id))

    def cycle_targets(self, reverse=False):
        '''
        Cycles through the current persons in the current combat pane.
        '''
        if not self.combat or not self.pane.person:
            return

        if not self.valid_target():
            self.currentTarget = None

        if not self.panePersonIdList or not self.currentTarget \
                or self.currentTarget not in self.pane.person or \
                any(x not in self.pane.person for x in self.panePersonIdList):
            self.panePersonIdList = self.pane.person.keys()
            self.currentTarget = self.panePersonIdList[0]

        dir = -1 if reverse else 1
        persons = len(self.panePersonIdList)
        for _ in range(persons):
            currentTargetPlace = self.panePersonIdList.index(self.currentTarget)
            self.currentTarget = self.panePersonIdList[(currentTargetPlace + dir) % persons]
            if self.valid_target():
                break

        if not self.valid_target():
            self.currentTarget = None
        self.update_regions()

    def valid_target(self):
        '''
        Checks to see if the current target has been invalidated.  Used in target cycling updating
        overlay regions
        '''
        if not self.currentTarget:
            return False
        if isinstance(self.currentTarget, Location):
            if self.currentTarget not in self.rangeRegion:
                return False
            if self.currentAbility.targetType not in ["location", "trap"]:
                return False
            if self.currentAbility.targetType == "trap" and \
                    self.pane.person[self.id].characterClass != "Anarchist" and \
                    any(self.currentTarget == p.location for p in self.pane.person.values() if \
                    p.team == "Monsters"):
                return False
        else:
            if self.currentTarget not in self.pane.person:
                return False
            if self.pane.person[self.currentTarget].location not in self.rangeRegion:
                return False
            if self.currentAbility.targetType == "hostile" and self.pane.person[self.currentTarget].team != "Monsters":
                return False
            if self.currentAbility.targetType == "friendly" and self.pane.person[self.currentTarget].team != "Players":
                return False
            if self.currentAbility.targetType == "self" and self.currentTarget != self.id:
                return False
        return True

    def update_regions(self):
        '''
        Update the current range based on your ability and position, and your target.
        XOR with previous range and target regions to obtain dirty tiles, and then redraw them all
        according to their current states.
        '''
        if self.id < 0:
            return

        dirty = Region()
        dirty("ADD", "CIRCLE", self.pane.person[self.id].location, 0)

        range = Region()
        if self.currentAbility:
            r = self.currentAbility.range if self.currentAbility.range != -1 else \
                    self.pane.person[self.id].attackRange
            if self.currentAbility.specialTargeting == "DEFAULT":
                range("ADD", "DIAMOND" if r != 1 else "CIRCLE", self.pane.person[self.id].location, r)
            if self.currentAbility.specialTargeting == "BORDER":
                range("ADD", "DIAMOND", self.pane.person[self.id].location, r)
                range("SUB", "DIAMOND", self.pane.person[self.id].location, r - 1)
            if self.currentAbility.targetType == "trap" and \
                    self.pane.person[self.id].characterClass != "Anarchist":
                for p in [x for x in self.pane.person.values() \
                        if x.team == "Monsters" and x.location in range]:
                    range("SUB", "CIRCLE", p.location, 0)
        dirty += self.rangeRegion ^ range
        self.rangeRegion = range

        target = Region()
        if self.currentTarget:
            if isinstance(self.currentTarget, Location):
                dirty("ADD", "CIRCLE", self.currentTarget, 0)
                if not self.valid_target():
                    self.currentTarget = None
            else:
                dirty("ADD", "CIRCLE", self.pane.person[self.currentTarget].location, 0)

        for l in self.rangeRegion + self.targetRegion:
            ovl = self.screen.get_overlay(l)
            if ovl != list(set(ovl)) or ('red' in ovl and not self.currentTarget):
                dirty("ADD", "CIRCLE", l, 0)

        if self.currentAbility and self.currentTarget:
            r = self.currentAbility.radius
            if isinstance(self.currentTarget, Location):
                target("ADD", "CIRCLE", self.currentTarget, r)
            else:
                target("ADD", "CIRCLE", self.pane.person[self.currentTarget].location, r)
        dirty += self.targetRegion ^ target
        self.targetRegion = target

        trapList = [l for l in Region("SQUARE", Location(self.pane.person[self.id].location.pane, \
                (0, 0)), Location(self.pane.person[self.id].location.pane, (PANE_X - 1, PANE_Y - 1))) \
                if self.pane.tiles[l.tile].trap]
        traps = Region(trapList)
        dirty += self.trapsRegion ^ traps
        self.trapsRegion = traps

        fields = self.pane.fields.get_region()
        dirty += self.fieldsRegion ^ fields
        self.fieldsRegion = fields

        for l in (l for l in dirty if l.pane == self.pane.person[self.id].location.pane):
            overlay = []
            if l == self.pane.person[self.id].location and self.combat:
                overlay.append('blue')
            if l in self.rangeRegion:
                overlay.append('blue')
            if l in self.targetRegion:
                overlay.append('red')
            if l == self.currentTarget or (self.currentTarget in self.pane.person \
                    and l == self.pane.person[self.currentTarget].location):
                overlay.append('red')
            if self.pane.tiles[l.tile].trap:
                overlay.append('red' if self.pane.tiles[l.tile].trap.team == "Monsters" else 'green')
            if l in self.fieldsRegion and "Pit" in self.pane.fields.get_fields(l):
                overlay.append('black')
            if l in self.fieldsRegion and "Zone of Silence" in self.pane.fields.get_fields(l):
                overlay.append('cyan')
            if l in self.fieldsRegion and "Smoke Screen" in self.pane.fields.get_fields(l):
                overlay.append('orange')
            if self.screen.get_overlay(l) != overlay:
                self.screen.set_overlay(l, overlay)
        self.screen.update()

    def select_self(self):
        '''
        Quickly select yourself in combat.
        '''
        if not self.combat or self.id < 0:
            return
        self.currentTarget = self.id

    def display_combat_status(self):
        '''
        Display all status effects currently in play in combat.
        If there are no status effects currently in play, do nothing.
        '''
        class Anon(object):
            def __init__(x, a, b, c):
                x.image = a
                x.name = b
                x.text = c

        combatStatuses = []
        for char in self.pane.person.values():
            for x in char.clientStatusView:
                image = char.clientStatusView[x]['image']
                name = x
                text = char.clientStatusView[x]['displayText']
                combatStatuses.append(Anon(image, name, text))
        if not combatStatuses:
            return
        if len(combatStatuses) > 48:
            combatStatuses = combatStatuses[:47]
        text = "List of current status effects in combat."
        self.screen.show_tiling_dialog(text, combatStatuses, bgcolor='lightblue')
        keystate.inputState = "COMBATSTATUS"

    def display_target_details(self):
        '''
        Print a message to the in game text box containing details on the
        strengths and weaknesses of the current target.
        '''
        if not self.currentTarget or self.currentTarget not in self.pane.person:
            return
        target = self.pane.person[self.currentTarget]
        self.screen.show_text("Details of " + target.name + ":", color='greenyellow')
        allElements = ['Arcane', 'Bludgeoning', 'Cold', 'Divine', 'Electric', 'Fire', 'Piercing',
                        'Poison', 'Shadow', 'Slashing', 'Physical']
        atLeastOneDetail = False
        for element in allElements:
            detail = target.getCombatDetails(element)
            if detail:
                atLeastOneDetail = True
                self.screen.show_text(detail, color='greenyellow')
        if not atLeastOneDetail:
            self.screen.show_text("Nothing remarkable.", color='greenyellow')

    def animate(self, id, source, dest, length):
        '''
        Perform all the calculations that are needed to setup a looping call that will animate people
        '''
        xdist = (dest.tile[0] - source.tile[0]) * TILE_SIZE
        ydist = (dest.tile[1] - source.tile[1]) * TILE_SIZE
        steps = max(abs(xdist), abs(ydist))
        source.direction = dest.direction

        self.pane.person[id].anim_start = time.time()
        if self.pane.person[id].anim:
            self.pane.person[id].anim.stop()
        self.pane.person[id].anim = LoopingCall(self.do_animation, id, source, dest, xdist, ydist, length)
        if steps > 0:
            self.pane.person[id].anim.start(float(length) / steps)
        else:
            self.pane.person[id].anim.start(1)

    def do_animation(self, id, source, dest, xdist, ydist, length):
        '''
        Based on the intended duration (length) of the animation and the time since the animation has
        begun, update the display to the appropriate position and image and redraw.
        '''
        completion = min((time.time() - self.pane.person[id].anim_start) / float(length), 1)
        statsdict = {}
        if completion < 1:
            statsdict['location'] = source
            statsdict['xoffset'] = int(completion * xdist)
            statsdict['yoffset'] = int(completion * ydist)
            statsdict['foot'] = 1 if completion < 0.5 else 0
        else:
            statsdict['location'] = dest
            statsdict['xoffset'] = 0
            statsdict['yoffset'] = 0
            statsdict['foot'] = 1
            if self.pane.person[id].anim:
                self.pane.person[id].anim.stop()
            self.pane.person[id].anim = None
            self.pane.person[id].anim_start = 0
        self.screen.update_person(id, statsdict)

    def animate_entity(self, location):
        '''
        Similar to self.animate, this is used for animating
        non player objects, such as chests. As long as the
        entity provides an attribute 'getAnimationImages'
        along with a list of images to animate, this will
        work with it.
        '''
        tile = self.pane.get_tile(location.tile)
        tile.anim_start = time.time()

        items = tile.get_items()
        if items:
            item = items[0]
            images = None
            if hasattr(item, 'getAnimationImages'):
                images = item.getAnimationImages()
            steps = 0
            if images:
                steps = len(images)
            length = 0
            if hasattr(item, 'getAnimationDuration'):
                length = item.getAnimationDuration()
            item.anim = LoopingCall(self.do_animation_entity, location, time.time(), length, steps, images)
            if steps > 0:
                item.anim.start(float(length) / (steps*2))

    def do_animation_entity(self, location, start_time, length, steps, images):
        '''
        Similar to self.do_animation, method is to be
        called using a looping call from animate_entity.
        Used for chest entities primarily, but can be
        used for any non-player game object.
        '''
        tile = self.pane.get_tile(location.tile)
        elapsed = time.time() - start_time
        time_step = length/steps
        i = int(elapsed / time_step)
        #print "Step " + str(i)

        if elapsed > length or i > steps - 1:
            if hasattr(tile, 'anim'):#tile.anim:
                tile.anim.stop()
            return
        tile.image = images[i]
        self.screen.update_tile(tile, location)

    def remove_entities(self, location):
        '''
        Helper method to remove the entities from a
        specific tile in a pane object.  Removes chests
        after they are opened.
        '''
        self.pane.remove_entities(location.tile)

    def switch_panes(self, location, combat=False):
        '''
        Main call to change the pane we want to view.
        Handles regular panes as well as combat panes.
        '''
        self.rangeRegion = Region()
        self.targetRegion = Region()
        self.trapsRegion = Region()
        self.fieldsRegion = Region()

        if combat:
            self.pane = self.pane.get_combat_pane(location)
        else:
            # If panes had an accessor method for cartesian coordinates, I wouldn't have to
            # code this in here!
            paneName = str(location.pane)
            # Example Format: (+x, -y)
            paneX = paneName.partition(", ")[0] + paneName.partition(", ")[1]
            paneY = paneName.partition(", ")[2]
            if paneY[0] == '-':
                paneY = paneY[1:]
            elif paneY[0] != "0":
                paneY = '-' + paneY[:]
            displayName = paneX + paneY
            self.screen.show_text('Entering ' + displayName)
            self.pane = self.world.get_pane(location.pane)
            if self.world.is_town_pane(location.pane) and self.musicState != "town":
                self.play_music("town", True)
            if not self.world.is_town_pane(location.pane) and self.musicState != "overworld":
                self.play_music("overworld", True)

        self.screen.set_pane(self.pane)

    def update_bindings(self):
        '''
        Populate lists with the key bound events and their current bindings, and send them to the
        GUI dual-pane dialog
        '''
        left = [Item(e, "\n".join(b[1]) if isinstance(b[1], list) else b[1]) \
                for e, b in keystate.bindings.iteritems()]
        e = keystate.bindings.keys()[self.dialog_selection]
        right = [Item(b.upper(), "\n".join(keystate.get_states(e))) for b in keystate.get_key(e, all=True)]
        self.screen.update_dual_pane_dialog_items(left, right)
