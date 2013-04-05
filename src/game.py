'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import time

from combat import *
from command import *
from location import *
from network import *
from server import *
from const import *
from gamescreen import GameScreen
from theorycraft import TheoryCraft
from world import *
from region import Region
import trap
import shop
from keybindings import keystate

import levelup as lvl

clock = pygame.time.Clock()

# Move to const:
LEVEL_MAX = 5

class Game(object):
    def __init__(self, port, serverip=None, state=None, player=None, **kwargs):
        '''
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

        # if not state:  # This is a hack, should be getting seed from host
            # state = {SEED_KEY: 'fdsa'}
        # assert player

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
        self.musicState = "overworld"

        # Levelup state
        self.levelup = None

        # Shop state
        self.currentShop = None

        # Selection state
        #Ability.targetType can be "friendly", "hostile", "self", "location"
        self.currentTargetId = None
        self.panePersonIdList = []
        self.currentAbility = None
        self.abilityList = []
        self.currentItem = None
        self.itemList = []
        self.playerSaveFile = None

        self.turnTime = kwargs.get('turnlength')

        # Setup server if host
        self.port = port
        if serverip:
            self.serverip = serverip
        else:
            self.serverip = "localhost"
            self.gs = GameServer(self.world, self.port, self.turnTime)
            Combat.gameServer = self.gs

        self.CDF = ClientDataFactory()
        reactor.connectTCP(self.serverip, self.port, self.CDF)

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
        if not self.CDF.port:
            return

        if self.id == -2:
            self.CDF.send(person)
            self.id = -1

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

        pygame.mixer.music.set_volume(0.1)

        self.setup.stop()
        LoopingCall(self.game_loop).start(1.0 / DESIRED_FPS)

    def game_loop(self):
        clock.tick()
        self.screen.set_fps(clock.get_fps())
        if hasattr(self, 'combatTurnStart'):
            turnTime = 1 - (time.time() - self.combatTurnStart) / self.turnTime if self.turnTime > 0 \
                    else 0
            self.screen.set_turntime(turnTime)

        self.check_queue()
        self.handle_events()
        self.play_music()
        self.screen.update()

    def play_music(self, state=None, stop=False):
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
        while not self.CDF.queue.empty():
            command = self.CDF.queue.get()

            ###### CreatePerson ######
            if command.type == "PERSON" and (command.action == "CREATE" or command.action == "LOAD"):
                if self.id == -1:  # Need to setup the pane
                    self.id = command.id
                    if self.combat:
                        self.switch_panes(command.cPane, self.combat)
                    else:
                        self.switch_panes(command.location)

                if command.action == "LOAD":
                    self.pane.person[command.id] = TheoryCraft.rehydratePlayer(command.details)
                elif command.action == "CREATE":
                    self.pane.person[command.id] = TheoryCraft.convertFromDetails(command.details)

                p = self.pane.person[command.id]
                p.location = command.location

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
                if command.id == self.id and self.currentAbility:
                    self.show_range(False)
                if 'details' in command.__dict__:
                    if self.pane.person[command.id].anim:
                        self.pane.person[command.id].anim.stop()
                        self.pane.person[command.id].anim = None
                    self.screen.update_person(command.id, {'location': command.location})
                else:
                    self.animate(command.id, self.pane.person[command.id].location, command.location, \
                            1.0 / self.pane.person[command.id].movementSpeed)

                self.pane.person[command.id].location = command.location
                if command.id == self.id and self.currentAbility:
                    self.show_range(True)

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

                    if self.currentTargetId == command.id:
                        loc = self.pane.person[command.id].location
                        tile = self.pane.get_tile(loc.tile)
                        self.screen.update_tile(tile, loc)

                    self.screen.remove_person(command.id)
                    if command.id == self.currentTargetId:
                        self.currentTargetId = None
                    del self.pane.person[command.id]

            ###### StopRunning ######
            if command.type == "PERSON" and command.action == "STOP":
                if command.id == self.id:
                    self.running = False

            ###### Levelup Player ######
            if command.type == "PERSON" and command.action == "REPLACE" and command.id != self.id:
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
                #id, status, turns, image
                self.pane.person[command.id].addClientStatus(command.status, command.image, \
                        command.turns)
                statsdict = {'stealth': self.pane.person[command.id].inStealth(True)}
                self.screen.update_person(command.id, statsdict)

            ###### Remove Person Status ######
            if command.type == "PERSON" and command.action == "REMOVESTATUS":
                self.pane.person[command.id].removeClientStatus(command.status)
                statsdict = {'stealth': self.pane.person[command.id].inStealth(True)}
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
                    self.currentTargetId = None
                    self.panePersonIdList = []
                    self.currentAbility = None
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
                    #print "Animating entities at " + str(command.location)
                if command.action == "REMOVE":
                    #Remove from pane
                    self.remove_entities(command.location)
                    self.screen.update_tile(self.pane.get_tile(command.location.tile), command.location)
                    #print "Removing entities at " + str(command.location.tile)

            elif command.type == "CHEST":
                if command.action == "ADD":
                    #print "Adding chest to " + str(command.location)
                    self.pane.add_chest(command.chestType, command.level, command.location.tile)

                if command.action == "REMOVE":
                    # print "Removing chest from " + str(command.location)
                    self.remove_entities(command.location)
                    #self.pane.remove_chest(command.location.tile)
                self.screen.update_tile(self.pane.get_tile(command.location.tile), command.location)

            elif command.type == "ABILITY" and command.action == "PLACE_TRAP":
                placer = self.pane.person[command.id]
                thisTrap = trap.Trap(name=command.abilityName, player=placer, location=command.targetLoc)
                self.pane.addTrap(command.targetLoc, thisTrap)
                self.screen.set_overlay(command.targetLoc, overlay=['red'])

            elif command.type == "TRAP" and command.action == "DISCOVER":
                thisTrap = trap.Trap(name=command.trapName, level=command.trapLevel, location=command.targetLoc)
                self.pane.addTrap(command.targetLoc, thisTrap)
                self.screen.set_overlay(command.targetLoc, overlay=['red'])

            elif command.type == "TRAP" and command.action == "REMOVE":
                self.pane.removeTrap(command.location)
                self.screen.set_overlay(command.location, overlay=None)

            elif command.type == "CLIENT" and command.action == "QUIT":
                self.save_and_quit()

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

    def quit(self):
        reactor.stop()

    def handle_events(self):
        if hasattr(self, 'pane') and hasattr(self.pane, 'person') and self.id in self.pane.person and \
                not self.pane.person[self.id].anim and keystate.direction("MOVEMENT"):
            self.move_person(keystate.direction("MOVEMENT"), 1)

        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
            #### General commands ####
            if event.type == QUIT:
                self.save_and_quit()
            if event.type == KEYUP:
                keystate(event)
            if event.type == KEYDOWN:
                e = keystate(event)
#                if e:
#                    print "Keyboard Event: %s" % e
                if e == "QUIT":
                    #TODO: Open Menu Here
                    self.save_and_quit()
                elif keystate.direction("MOVEMENT"):
                    self.move_person(keystate.direction("MOVEMENT"), 1)
                elif keystate.direction("DIALOG"):
                    self.screen.move_dialog(keystate.direction("DIALOG"))
                elif keystate.direction("TARGET"):
                    self.attempt_attack(targetingLocation=keystate.direction("TARGET"))
                elif e == "TARGETCANCEL":
                    self.screen.show_text("Cancelled trap placement.", color='white')
                    keystate.inputState = "COMBAT"
                    self.currentAbility = None
                elif e == "SCROLLTOP":
                    self.screen.scroll_up(1000)
                elif e == "SCROLLUP":
                    self.screen.scroll_up(1)
                elif e == "SCROLLDOWN":
                    self.screen.scroll_down(1)
                elif e == "SCROLLBOTTOM":
                    self.screen.scroll_down(1000)

                ### Character Sheet ###
                elif e == "CHARSHEETOPEN":
                    self.display_character_sheet()
                    keystate.inputState = "CHARSHEET"
                elif e == "CHARSHEETCLOSE":
                    self.screen.hide_dialog()
                    keystate.inputState = "OVERWORLD"
                elif e == "CHARSHEETMAIN":
                    self.screen.hide_dialog()
                    self.display_character_sheet()
                elif e == "CHARSHEETABILITIES":
                    self.screen.hide_dialog()
                    self.display_character_abilities()
                elif e == "CHARSHEETSPELLS":
                    self.screen.hide_dialog()
                    self.display_character_spells()
                elif e == "CHARSHEETPASSIVES":
                    self.screen.hide_dialog()
                    self.display_character_passives()
                elif e == "CHARSHEETTRAITS":
                    self.screen.hide_dialog()
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

                elif e == "SHOPOPEN":
                    self.request_shop()
                elif e == "SHOPTRANSACTION":
                    if self.screen.get_dialog_selection()[0] == 0:
                        self.currentShop.sell(self.screen.get_dialog_selection()[1])
                    else:
                        self.currentShop.buy(self.screen.get_dialog_selection()[1])
                elif e == "SHOPCLOSE":
                    hero = self.currentShop.close()
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
                            self.screen.get_dialog_selection()[2], self.screen)
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
                    self.select_self()
                    keystate.inputState = "COMBAT"

                ### Combat Only Commands ###
                elif e == "ABILITIESOPEN":
                    keystate.inputState = "ABILITIES"
                    self.choose_ability()
                elif e == "ABILITIESSELECT":
                    self.currentAbility = self.pane.person[self.id].abilities[self.screen.hide_dialog()]
                    if "Trap" in self.currentAbility.name:
                        keystate.inputState = "TARGET"
                    else:
                        keystate.inputState = "COMBAT"

                    if self.currentAbility.range == 0:
                        self.select_self()
                    else:
                        self.show_range(True)

                elif e == "SPELLSOPEN":
                    keystate.inputState = "SPELLS"
                    self.choose_spell()
                elif e == "SPELLSSELECT":
                    self.currentAbility = self.pane.person[self.id].spellList[self.screen.hide_dialog()]
                    keystate.inputState = "COMBAT"
                    if self.currentAbility.range == 0:
                        self.select_self()
                    else:
                        self.show_range(True)

                elif e == "SWITCHGEAR":
                    self.switch_gear()
                elif e == "CYCLETARGETF":
                    self.cycle_targets()
                elif e == "CYCLETARGETB":
                    self.cycle_targets(reverse=True)
                elif e == "ACTIVATESELECTED":
                    if self.currentItem:
                        self.use_item()
                    else:
                        self.attempt_attack()
                elif e == "ENDTURN":
                    self.force_end_turn()
                elif e == "SELECTSELF":
                    self.select_self()
                elif e == "ANALYZETARGET":
                    self.display_target_details()

                ### Strictly non-combat commands ###
                elif e == "GETITEM":
                    self.get_item()
                elif e == "BASHCHEST":
                    #self.break_in() -- Will bash/pick-lock chests.  Will attempt a picklock first if
                    # you are a thief primary class.  If that fails, all other attempts will be bashes.
                    pass
                elif e == "STARTLEVELUP":
                    self.request_levelup(True)
                #elif e == "STARTRESPEC":
                #    self.respec()
                elif e == "HELPMENU":
                    pass #TODO Implement help menu
                elif e == "SHOWINPUTSTATE":
                    print "Keyboard input state: %s" % keystate.inputState
                elif e == "CHEAT CODE":
                    print "You found the secret code!"

    def get_item(self):
        self.CDF.send(Command("PERSON", "OPEN", id=self.id))
        # If player is on an item, pick it up (the top item).
        # If player is on a treasure chest, attempt to open it.
        # If the chest is locked, send a message to the screen.
        # If the chest is unlocked, distribute treasure to this player
        #    and all others on this pane.

    def request_levelup(self, debug=False):
        # Remove EXP code left for testing, TODO
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
            #print "DEBUG: " + `player.experience` + " exp " + `player.getExpForNextLevel()` + " needed " + `player.level` + " level "


    def respec(self):
        player = self.pane.person[self.id]
        if player.ironman:
            self.screen.show_text("You are an ironman, and are thus too cool to respec!", color='magenta')
        elif player.level > 1:
            oldLevel = player.level
            oldExp = player._experience
            player.level -= 1
            remainderExp = oldExp - player.getExpForNextLevel()
            player._experience = 0

            newHero = TheoryCraft.resetPlayerLevel(player)
            newHero.location = self.pane.person[self.id].location
            newHero.id = self.id
            self.pane.person[self.id] = newHero

            for _ in range(oldLevel - 1):
                keystate.inputState = "LEVELUP"
                self.pane.person[self.id]._experience = self.pane.person[self.id].getExpForNextLevel()
                self.pane.person[self.id].level += 1
                self.levelup = lvl.Levelup(self.pane.person[self.id], self.screen)
                self.levelup.next()

            self.pane.person[self.id].addExperience(remainderExp)

    def request_shop(self):
        player = self.pane.person[self.id]
        # if player is actually on a shop tile or whatever... TODO
        if player.inventory.allItems:
            keystate.inputState = "SHOP"
            self.currentShop = shop.Shop(player, self.screen) # Using all default parameters at the moment TODO
            self.currentShop.open()

    def open_inventory(self):
        keystate.inputState = "INVENTORY"
        player = self.pane.person[self.id]
        isEquipment = True
        text = "Looking in your bag..."
        eq = player.equippedItems.allGear
        if not eq:
            eq = []
        inv = player.inventory.allItems
        if not inv:
            inv = []
        capacity = `player.inventoryWeight` + "/" + `player.inventoryCapacity`
        if not eq and not inv:
            keystate.inputState = "OVERWORLD"
            return
        self.screen.show_item_dialog(text, inv, eq, isEquipment, bgcolor='tan', capacity=capacity)

    def open_consumables(self):
        keystate.inputState = "CONSUMABLE"
        player = self.pane.person[self.id]
        cons = player.inventory.allConsumables
        if cons:
            isEquipment = False
            text = "Select a consumable"
            self.screen.show_item_dialog(text, cons, [], isEquipment, bgcolor='tan')
        else:
            keystate.inputState = "COMBAT"

    def choose_ability(self):
        text = "Select an Ability"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].abilities
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def choose_spell(self):
        text = "Select a Spell"
        bgcolor = "lightblue"
        itemslist = self.pane.person[self.id].spellList
        if not itemslist:
            keystate.inputState = "OVERWORLD"
            return
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def move_person(self, direction, distance):
        if self.running:
            self.CDF.send(Command("PERSON", "STOP", id=self.id))
            self.running = False

        newloc = self.pane.person[self.id].location.move(direction, distance)
        if self.combat and newloc.pane != (0, 0):
            return False
        if not self.pane.person[self.id].anim and ((self.pane.person[self.id].location.pane == \
                newloc.pane and self.pane.is_tile_passable(newloc) and \
                newloc.tile not in [x.location.tile for x in self.pane.person.values()]) or \
                self.pane.person[self.id].location.pane != newloc.pane):

            if "SHIFT" in keystate and not self.combat:
                self.CDF.send(Command("PERSON", "RUN", id=self.id, direction=direction))
                self.running = True

            elif not self.combat or (self.pane.person[self.id].remainingMovementTiles > 0 or \
                    self.pane.person[self.id].AP >= self.pane.person[self.id].totalMovementAPCost):
                self.CDF.send(Command("PERSON", "MOVE", id=self.id, location=newloc))
                if self.pane.person[self.id].location.pane == newloc.pane:
                    self.animate(self.id, self.pane.person[self.id].location, newloc, \
                            1.0 / self.pane.person[self.id].movementSpeed)
                    self.pane.person[self.id].location = newloc
        elif self.pane.person[self.id].location.direction != direction:
            self.pane.person[self.id].location.direction = direction

            statsdict = {}
            statsdict['location'] = self.pane.person[self.id].location
            self.screen.update_person(self.id, statsdict)

            self.CDF.send(Command("PERSON", "MOVE", id=self.id, \
                    location=self.pane.person[self.id].location))


    def display_character_sheet(self):
        player = self.pane.person[self.id]
        self.screen.show_character_dialog(player) # TODO: Custom menu keys here.
        self.screen.show_character_dialog(player, abilitykey='A', spellkey='S',
                                                  passivekey='P', traitkey='T')

    def display_character_abilities(self):
        text = "Active Abilities (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].abilities
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def display_character_passives(self):
        text = "Passive Abilities (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].passiveAbilities
        if not itemslist:
            self.display_character_sheet()
            return
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def display_character_spells(self):
        if self.pane.person[self.id].growthType == "Non-Caster":
            self.display_character_sheet()
            return
        text = "Learned Spells (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].spellList
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def display_character_traits(self):
        if self.pane.person[self.id].level == 1:
            self.display_character_sheet()
            return
        text = "Chosen Traits (Press 'C' to return to main statistics)"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].traits
        self.screen.show_tiling_dialog(text, itemslist, bgcolor=bgcolor)

    def force_end_turn(self):
        ap = self.pane.person[self.id].AP
        movesLeft = self.pane.person[self.id].remainingMovementTiles
        if ap > 0 or movesLeft > 0:
            action = Command("ABILITY", "END_TURN", id=self.id)
            self.CDF.send(action)

    def attempt_attack(self, targetingLocation=None):
        if not self.currentTargetId and not targetingLocation:
            print "No target selected."
            return
        if not self.currentAbility:
            print "No ability selected."
            return
        if not targetingLocation:
            self.CDF.send(Command("ABILITY", "ATTACK", id=self.id, targetId=self.currentTargetId,
                abilityName=self.currentAbility.name))
        else:
            self.CDF.send(Command("ABILITY", "PLACE_TRAP", id=self.id, \
                    targetLoc=self.pane.person[self.id].location.move(targetingLocation), \
                    abilityName=self.currentAbility.name))

    def use_item(self):
        if not self.currentItem or \
          self.currentItem not in self.pane.person[self.id].inventory.allConsumables:
            self.screen.show_text("No item selected", color='white')
            return
        self.CDF.send(Command("ITEM", "USE", id=self.id, itemName=self.currentItem.name))
        self.currentItem = None

    def switch_gear(self):
        player = self.pane.person[self.id]
        if not player.equippedItems.alternateWeapon:
            print "DEBUG: No weapon found"
            return
        else:
            self.CDF.send(Command("ABILITY", "SWITCH_GEAR", id=self.id))

    def cycle_targets(self, reverse=False):
        # Cycles through the current persons in the current combat pane.
        if not self.combat:
            return

        if self.currentTargetId:
            if self.currentTargetId not in self.pane.person.keys():
                self.currentTargetId = None
            else:
                self.screen.set_overlay(self.pane.person[self.currentTargetId].location, None)

        resetNeeded = False
        for x in self.panePersonIdList:
            if x not in self.pane.person:
                resetNeeded = True
        if not self.panePersonIdList or not self.currentTargetId \
           or self.currentTargetId not in self.pane.person or \
           resetNeeded:
            self.panePersonIdList = [x for x in self.pane.person]
            self.currentTargetId = self.panePersonIdList[0]
        elif not reverse:
            if self.currentTargetId == self.panePersonIdList[-1]:
                self.currentTargetId = self.panePersonIdList[0]
            else:
                currentTargetPlace = self.panePersonIdList.index(self.currentTargetId)
                self.currentTargetId = self.panePersonIdList[currentTargetPlace + 1]
        else:
            if self.currentTargetId == self.panePersonIdList[0]:
                self.currentTargetId = self.panePersonIdList[-1]
            else:
                currentTargetPlace = self.panePersonIdList.index(self.currentTargetId)
                self.currentTargetId = self.panePersonIdList[currentTargetPlace - 1]

        self.screen.set_overlay(self.pane.person[self.currentTargetId].location, ['red'])

    def show_range(self, show, loc=None):
        if not loc:
            loc = self.pane.person[self.id].location
        R = Region()

        R("ADD", "DIAMOND", loc, self.currentAbility.range \
                if self.currentAbility.range != -1 else self.pane.person[self.id].attackRange)
        for l in [x for x in R if x.pane == (0, 0)]:
            self.screen.set_overlay(l, overlay=['blue'] if show else None)
        self.screen.update()

    def select_self(self):
        if not self.combat or self.id not in self.pane.person:
            return
        if not self.panePersonIdList:
            self.panePersonIdList = [x for x in self.pane.person]
        selfIndex = self.panePersonIdList.index(self.id)
        self.currentTargetId = self.panePersonIdList[selfIndex]
        self.screen.show_text("Targeting: yourself", color='lightblue')

    def display_target_details(self):
        if not self.currentTargetId or self.currentTargetId not in self.pane.person:
            return
        target = self.pane.person[self.currentTargetId]
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

            if id == self.id and self.currentAbility:
                self.show_range(False, source)
                self.show_range(True)
        self.screen.update_person(id, statsdict)

    def animate_entity(self, location):
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
        #TODO: make this delayed. (maybe use DelayedCall?)
        self.pane.remove_entities(location.tile)

    def switch_panes(self, location, combat=False):
        #TODO we can add transitions here.
        if combat:
            self.pane = self.pane.get_combat_pane(location)
        else:
            self.pane = self.world.get_pane(location.pane)
        self.screen.set_pane(self.pane)

