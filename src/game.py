'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys
import time
import datetime
import pickle

from combat import *
from command import *
from location import *
from network import *
from server import *
from const import *
from gamescreen import GameScreen
from theorycraft import TheoryCraft
from world import *

import ability
import passiveability
import trait
import spell

clock = pygame.time.Clock()

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
        if not state:  # This is a hack, should be getting seed from host
            state = {SEED_KEY: 'fdsa'}
        assert player

        if isinstance(state, dict):     #This means we're creating a new game
            self.state = state
        else:                           #This means we're loading the state from a save file
            unpickled_state = pickle.load( open( state, "rb" ) )
            self.state = unpickled_state

        Sprites.load(self.state[SEED_KEY])  #Static method call to load sprites
        self.world = World(world_state=self.state)
        self.pane = None

        # Game state
        self.id = -1
        self.keystate = []
        self.running = False
        self.combat = False
        self.performingLevelup = False
        
        # Levelup state
        self.levelup = None
        
        # Selection state
        self.selectionMode = "targeting"
        self.currentTargetId = None
        self.panePersonIdList = []
        self.currentAbility = None
        self.abilityList = []
        self.currentItem = None
        self.itemList = []
        self.playerSaveFile = None
        
        # Setup server if host
        self.port = port
        if serverip:
            self.serverip = serverip
        else:
            self.serverip = "localhost"
            Combat.gameServer = GameServer(self.world, self.port)

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
            dehydrated_string = self.load_player(self.playerSaveFile)
            person = Command("PERSON", "LOAD", id=None, \
                    location=Location((0, 0), (PANE_X/2, PANE_Y/2)), \
                    details=dehydrated_string)

        self.setup = LoopingCall(self.setup_game, person)
        self.setup.start(0)

        reactor.run()

    def setup_game(self, person):
        if not self.CDF.port:
            return

        # Set up game engine
        self.screen = GameScreen()
        Combat.screen = self.screen

        self.CDF.send(person)

        self.setup.stop()
        LoopingCall(self.game_loop).start(1.0 / DESIRED_FPS)

    def game_loop(self):
        clock.tick()
        self.screen.set_fps(clock.get_fps())

        self.check_queue()
        self.handle_events()
        self.screen.update()

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
                    ##SAVE PERSON##
                    save = Command("PERSON", "SAVE", id= -1)
                    self.CDF.send(save)
                
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

            if command.type == "PERSON" and command.id not in self.pane.person:
                continue

            ###### MovePerson ######
            if command.type == "PERSON" and command.action == "MOVE":
                if 'details' in command.__dict__:
                    if self.pane.person[command.id].anim:
                        self.pane.person[command.id].anim.stop()
                        self.pane.person[command.id].anim = None
                    self.screen.update_person(command.id, {'location': command.location})
                else:
                    self.animate(command.id, self.pane.person[command.id].location, command.location, \
                            1.0 / self.pane.person[command.id].movementSpeed)
                self.pane.person[command.id].location = command.location

            ###### RemovePerson ######
            if command.type == "PERSON" and command.action == "REMOVE":
                if command.id == self.id:
                    self.id = -1
                    for person in self.pane.person.values():
                        if person.anim:
                            person.anim.stop()
                    self.pane.person = {}
                else:
                    self.screen.remove_person(command.id)
                    if command.id == self.currentTargetId:
                        self.currentTargetId = None
                    del self.pane.person[command.id]

            ###### StopRunning ######
            if command.type == "PERSON" and command.action == "STOP":
                if command.id == self.id:
                    self.running = False
                    
            ###### SAVE PERSON ######
            if command.type == "PERSON" and command.action == "SAVE":
                self.save_player()

            ###### Update Person Stats ######
            if command.type == "PERSON" and command.action == "UPDATE":
                for k, v in command.__dict__.iteritems():
                    if k not in ['type', 'action', 'id']:
                        setattr(self.pane.person[command.id], k, v)
                        if k in ['HP', 'MP', 'AP']:
                            self.screen.update_person(command.id, {k: v, \
                                    'team': self.pane.person[command.id].team})
                        
            ###### Character Progression ######
            if command.type == "PERSON" and command.action == "ADD_EXPERIENCE":
                self.pane.person[command.id].addExperience(command.experience)
                        
            ###### Update Text #####
            elif command.type == "UPDATE" and command.action == "TEXT":
                self.screen.show_text(command.text, color=command.color)
            
            ###### Initiate Combat ######
            elif command.type == "UPDATE" and command.action == "COMBAT":
                self.combat = command.combat
            
            ###### Update HP Buffers ######
            elif command.type == "UPDATE" and command.action == "HP_BUFFER":
                self.screen.update_person(command.id, {'buffedHP' : command.bufferSum, \
                        'totalHP' : self.pane.person[command.id].totalHP, \
                        'team' : self.pane.person[command.id].team})
            
            ###### Remove Item ######
            elif command.type == "ITEM" and command.action == "REMOVE":
                self.pane.person[command.id].inventory.removeItem(itemName=command.itemName)

            ###### Get Item ######
            elif command.type == "ITEM" and command.action == "CREATE":
                item = TheoryCraft.rehydrateTreasure(command.itemIdentifier)
                self.pane.person[command.id].inventory.addItem(item)
                
            elif command.type == "ITEM" and command.action == "EQUIP":
                item = TheoryCraft.rehydrateTreasure(command.itemIdentifier)
                self.pane.person[command.id].equip(item)
                
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
                    print "Removing entities at " + str(command.location.tile)
            
            elif command.type == "CHEST":
                if command.action == "ADD":
                    self.pane.add_chest(command.location.tile, command.chestType, command.level)
                if command.action == "REMOVE":
                    self.remove_entities(command.location)
                    #self.pane.remove_chest(command.location.tile)
            
            elif command.type == "CLIENT" and command.action == "RESET_TARGETING" and command.id == self.id:
                self.selectionMode = "targeting"
                self.currentTargetId = None
                self.panePersonIdList = []
                self.currentAbility = None
                self.abilityList = []
                self.currentItem = None
                self.itemList = []
    
    def save_player(self):
        '''
        Dehydrates our current player and saves it.
        '''
    
        if not self.id in self.pane.person:
            return

        player = self.pane.person[self.id]
        player_string = player.dehydrate()
        file_name = self.playerSaveFile
        if not file_name:
            saved_list = os.listdir(CHAR_SAVE_PATH)
            max_save = 0
            if saved_list:
                increment_list = []
                for filename in saved_list:
                    split_list = filename.split(".")
                    increment_list.append(int(split_list[-1]))   #Get last element from list (the incremental save number)
                max_save = max(increment_list)
            max_save += 1
            file_name = str(player.name) + "_" + str(player.race) + "_" + str(player.characterClass) + "." + str("%03d" % max_save)
            self.playerSaveFile = file_name
        path_to_file = os.path.join(CHAR_SAVE_PATH, file_name)
        print "Saving Character To " + str(path_to_file)
        
        file = open(path_to_file, "ab")
        file.write("\n" + player_string)
        file.close()
        
    def load_player(self, file_name):
        path_to_file = os.path.join(CHAR_SAVE_PATH, file_name)
        file = open(path_to_file, "r")
        for line in file:
            pass
        last = line
        file.close()
        print "Loading player from " + str(path_to_file)
        return last
    
    def save_and_quit(self):
        '''
        Calls self.save_player() and then quits
        '''
        
        # now = datetime.datetime.now()
        # savetime = "." + now.strftime("%Y-%m-%d %H:%M")
        #player = self.pane.person[self.id]
        #player_string =player.dehydrate()

        self.save_player()#player_string)
        reactor.stop()
    
    def handle_events(self):
        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
            #### General commands ####
            if event.type == QUIT:
                self.save_and_quit()
            if event.type == KEYUP:
                if event.key in MODIFIER_KEYS:
                    if event.key in self.keystate:
                        self.keystate.remove(event.key)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    #TODO: Open Menu Here
                    ##SAVE PERSON##
                    self.save_player()
                    save = Command("PERSON", "SAVE", id=self.id)
                    self.CDF.send(save)
                    
                elif event.key in MODIFIER_KEYS:
                    self.keystate.append(event.key)
                elif event.key in MOVE_KEYS and not self.performingLevelup or \
                     (self.combat and (self.selectionMode == "abilities" or self.selectionMode == "spells")):
                    self.move_person(MOVE_KEYS[event.key], 1)
                elif event.key == K_EQUALS or event.key == K_PAGEUP:
                    self.screen.scroll_up(1 if not any(mod in [K_LSHIFT, K_RSHIFT] \
                            for mod in self.keystate) else 1000)
                elif event.key == K_MINUS or event.key == K_PAGEDOWN:
                    self.screen.scroll_down(1 if not any(mod in [K_LSHIFT, K_RSHIFT] \
                            for mod in self.keystate) else 1000)

                ### Levelup Commands ###
                if self.performingLevelup:
                    upgradedHero = self.levelup.input(event.key)
                    if upgradedHero:
                        # Upgraded Hero is "False" until the levelup is finished. Then it is a dehydrated hero.
                        self.pane.person[self.id] = TheoryCraft.rehydratePlayer(upgradedHero)
                        self.performingLevelup = False
                        #self.CDF.send(Command("PERSON", "REPLACE", id=self.id, location=self.pane.person[self.id])TODO HALP!
                        
                ### Combat Only Commands ###
                elif self.combat:
                
                    #### Ability/Spell Selection ####
                    if self.selectionMode == "abilities" or self.selectionMode == "spells":
                        if event.key == K_RIGHT or event.key == K_KP6:
                            self.screen.move_dialog(6)
                        elif event.key == K_LEFT or event.key == K_KP4:
                            self.screen.move_dialog(4)
                        elif event.key == K_UP or event.key == K_KP8:
                            self.screen.move_dialog(8)
                        elif event.key == K_DOWN or event.key == K_KP2:
                            self.screen.move_dialog(2)
                        elif event.key == K_SPACE or event.key == K_a:
                            if self.selectionMode == "spells":
                                self.currentAbility = self.pane.person[self.id].spellList[self.screen.hide_dialog()]
                            else:
                                self.currentAbility = self.pane.person[self.id].abilities[self.screen.hide_dialog()]
                            self.selectionMode = "targeting"
                            if self.currentAbility.range == 0:
                                self.select_self()
                                    
                    elif event.key == K_e:
                        if self.selectionMode == "targeting":
                            self.cycle_targets()
                        elif self.selectionMode == "items":
                            self.cycle_items()
                    elif event.key == K_w: 
                        if self.selectionMode == "targeting":
                            self.cycle_targets(reverse=True)
                        elif self.selectionMode == "items":
                            self.cycle_items(reverse=True)
                    elif event.key == K_a:
                        if self.selectionMode == "items":
                            self.use_item()
                        else:
                            self.attempt_attack()
                    elif event.key == K_n:
                        self.force_end_turn()
                    elif event.key == K_s:
                        self.select_self()
                        pass
                    elif event.key == K_i:
                        self.selectionMode = "items"
                        self.screen.show_text("Selection mode: items", color="darkred")
                        pass
                    elif event.key == K_PERIOD:
                        self.display_target_details()
                        pass
                    elif event.key == K_SPACE:
                        self.selectionMode = "abilities"
                        self.choose_ability()
                    elif event.key == K_b:
                        self.selectionMode = "spells"
                        self.choose_spell()
                ### Strictly non-combat commands ###
                if not self.combat:
                    if event.key == K_g:
                        self.get_item()
                    elif event.key == K_b:
                        #self.break_in() -- Will bash/pick-lock chests.  Will attempt a picklock first if
                        # you are a thief primary class.  If that fails, all other attempts will be bashes.
                        pass
                    elif event.key == K_c:
                        self.display_character_sheet()
                    elif event.key == K_y:
                        self.performingLevelup = True
                        self.request_levelup()
                    
    def get_item(self):
        self.CDF.send(Command("PERSON", "OPEN", id=self.id))
        # If player is on an item, pick it up (the top item).
        # If player is on a treasure chest, attempt to open it.
        # If the chest is locked, send a message to the screen.
        # If the chest is unlocked, distribute treasure to this player
        #    and all others on this pane.
            
    def request_levelup(self):
        # Ask server if this character may levelup. TODO
        # Remove EXP code left for testing, TODO
        player = self.pane.person[self.id]
        player._experience = 175
        player.level = 2
        self.levelup = Levelup(player, self.screen)
        self.levelup.next()
            
    def choose_ability(self):
        text = "Select an Ability"
        bgcolor = "cadetblue"
        itemslist = self.pane.person[self.id].abilities
        self.screen.show_dialog(text, itemslist, bgcolor=bgcolor)
            
    def choose_spell(self):
        text = "Select a Spell"
        bgcolor = "lightblue"
        itemslist = self.pane.person[self.id].spellList
        if not itemslist:
            self.selectionMode = "targeting"
            return
        self.screen.show_dialog(text, itemslist, bgcolor=bgcolor)
            
    def move_person(self, direction, distance):
        if self.running:
            self.CDF.send(Command("PERSON", "STOP", id=self.id))
            self.running = False

        newloc = self.pane.person[self.id].location.move(direction, distance)
        if not self.pane.person[self.id].anim and ((self.pane.person[self.id].location.pane == \
                newloc.pane and self.pane.is_tile_passable(newloc) and \
                newloc.tile not in [x.location.tile for x in self.pane.person.values()]) or \
                self.pane.person[self.id].location.pane != newloc.pane):

            if any(mod in [K_LSHIFT, K_RSHIFT] for mod in self.keystate) and not self.combat:
                self.CDF.send(Command("PERSON", "RUN", id=self.id, direction=direction))
                self.running = True
            
            elif self.pane.person[self.id].remainingMovementTiles > 0 or \
                 self.pane.person[self.id].AP >= self.pane.person[self.id].totalMovementAPCost:
                self.CDF.send(Command("PERSON", "MOVE", id=self.id, location=newloc))
                if self.pane.person[self.id].location.pane == newloc.pane:
                    self.animate(self.id, self.pane.person[self.id].location, newloc, \
                        1.0 / self.pane.person[self.id].movementSpeed)
                    self.pane.person[self.id].location = newloc

    def display_character_sheet(self):
        player = self.pane.person[self.id]
        player.printCharacterSheet()
                    
    def force_end_turn(self):
        ap = self.pane.person[self.id].AP
        movesLeft = self.pane.person[self.id].remainingMovementTiles
        if ap > 0 or movesLeft > 0:
            action = Command("ABILITY", "END_TURN", id=self.id)
            self.CDF.send(action)

    def attempt_attack(self):
        if not self.currentTargetId:
            print "No target selected."
            return
        self.CDF.send(Command("ABILITY", "ATTACK", id=self.id, targetId=self.currentTargetId,
                abilityName=self.currentAbility.name))
       
    def use_item(self):
        if not self.currentItem or \
          self.currentItem not in self.pane.person[self.id].inventory.allConsumables:
            self.screen.show_text("No item selected", color='white')
            return
        self.CDF.send(Command("ITEM", "USE", id=self.id, itemName=self.currentItem.name))
        self.selectionMode = "abilities"
        self.itemList = []
                    
    def begin_select_consumable(self):
        pass
                      
    def cycle_items(self, reverse=False):
        if not self.combat:
            return
        if not self.itemList or not self.currentItem or self.currentItem not in self.itemList:
            self.itemList = self.pane.person[self.id].inventory.allConsumables
            if not self.itemList:
                return
            self.currentItem = self.itemList[0]
        elif not reverse:
            if self.currentItem == self.itemList[-1]:
                self.currentItem = self.itemList[0]
            else:
                itemIndex = self.itemList.index(self.currentItem)
                self.currentItem = self.itemList[itemIndex + 1]
        else:
            if self.currentItem == self.itemList[0]:
                self.currentItem = self.itemList[-1]
            else:
                itemIndex = self.itemList.index(self.currentItem)
                self.currentItem = self.itemList[itemIndex - 1]
        self.screen.show_text("Selected item: " + self.currentItem.name, color='lightblue')
                      
    def cycle_abilities(self, reverse=False):
        if not self.combat:
            return
        if not self.abilityList or not self.currentAbility or self.currentAbility not in self.abilityList:
            self.abilityList = self.pane.person[self.id].abilities
            self.abilityList.extend(self.pane.person[self.id].spellList)
            self.currentAbility = self.abilityList[0]
        elif not reverse:
            if self.currentAbility == self.abilityList[-1]:
                self.currentAbility = self.abilityList[0]
            else:
                abilityIndex = self.abilityList.index(self.currentAbility)
                self.currentAbility = self.abilityList[abilityIndex + 1]
        else:
            if self.currentAbility == self.abilityList[0]:
                self.currentAbility = self.abilityList[-1]
            else:
                abilityIndex = self.abilityList.index(self.currentAbility)
                self.currentAbility = self.abilityList[abilityIndex - 1]
        self.screen.show_text("Selected: " + self.currentAbility.name + " AP COST: " + 
                                str(self.currentAbility.APCost),
                                color='lightblue')
        
    def cycle_targets(self, reverse=False):
        # Cycles through the current persons in the current combat pane.
        if not self.combat:
            return
        if not self.panePersonIdList or not self.currentTargetId \
           or self.currentTargetId not in self.pane.person:
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
        if self.id == self.currentTargetId:
            self.screen.show_text("Targeting: yourself", color='lightblue')
        else:
            self.screen.show_text("Targeting: " + self.pane.person[self.currentTargetId].name, 
                                color='lightblue')

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
        for element in allElements:
            detail = target.getCombatDetails(element)
            if detail:
                self.screen.show_text(detail, color='greenyellow')
                                
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
        self.screen.update_person(id, statsdict)

    def animate_entity(self, location):
        tile = self.pane.get_tile(location.tile)
        tile.anim_start = time.time()

        items = tile.get_items()
        if items:
            item = items[0]
            images = item.getAnimationImages()
            steps = 0
            if images:
                steps = len(images)
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

        
class Levelup(object):
    def __init__(self, player, screen):
        self.player = player
        self.screen = screen
        self.phase = None
        self.phaseList = []
        self.skill = None
        self.spellA = None
        self.spellB = None
        self.trait = None
        self.summary = []
        
        self.traitOptions = []
        self.skillOptions = []
        self.spellOptions = []
        
    def next(self):
        if not self.phase:
            self._determinePhaseList()
            self.phase = self.phaseList[0]
        if self.phase == "TRAIT":
            text = "Select a new trait or upgrade an existing one."
            self.traitOptions = self.player.getLevelupTraitOptions()
            self.screen.show_dialog(text, self.traitOptions, bgcolor="cadetblue")
        elif self.phase == "SKILL":
            text = "Select a new skill."
            self.skillOptions = self.player.getLevelupSkillOptions()
            self.screen.show_dialog(text, self.skillOptions, bgcolor="cadetblue")
        elif self.phase == "SPELL_1":
            text = "Select a new spell."
            self.spellOptions = self.player.getLevelupSpellOptions()
            self.screen.show_dialog(text, self.spellOptions, bgcolor="blue")
        elif self.phase == "SPELL_2":
            text = "Select another new spell."
            self.spellOptions = self.player.getLevelupSpellOptions()
            self.screen.show_dialog(text, self.spellOptions, bgcolor="blue")
        elif self.phase == "COMBO":
            text = "Additionally you have earned these unique skills."
            combos = self.player.getLevelupCombos()
            self.screen.show_dialog(text, combos, bgcolor="darkred")
        elif self.phase == "SUMMARY":
            text = "This is a summary of the statistics and abilities you have gained."
            self.summary.append(self.trait)
            if self.skill:
                self.summary.append(self.skill)
            if self.spellA:
                self.summary.append(self.spellA)
            if self.spellB:
                self.summary.append(self.spellB)
            self.summary.append(self.player.getLevelupStats())
            self.screen.show_dialog(text, self.summary, bgcolor="red")
        
    def input(self, keystroke):
        '''Returns True if this levelup is complete.'''
        if keystroke == K_RIGHT or keystroke == K_KP6:
            self.screen.move_dialog(6)
            return False
        elif keystroke == K_LEFT or keystroke == K_KP4:
            self.screen.move_dialog(4)
            return False
        elif keystroke == K_UP or keystroke == K_KP8:
            self.screen.move_dialog(8)
            return False
        elif keystroke == K_DOWN or keystroke == K_KP2:
            self.screen.move_dialog(2)
            return False
        elif keystroke == K_SPACE or keystroke == K_a:
            if self.phase == "TRAIT":
                self.trait = self.traitOptions[self.screen.hide_dialog()]
                self._advancePhase()
                return False
            elif self.phase == "SKILL":
                self.skill = self.skillOptions[self.screen.hide_dialog()]
                self._advancePhase()
                return False
            elif self.phase == "SPELL_1":
                self.spellA = self.spellOptions[self.screen.hide_dialog()]
                self.spellOptions.remove(self.spellA)
                self._advancePhase()
                return False
            elif self.phase == "SPELL_2":
                self.spellB = self.spellOptions[self.screen.hide_dialog()]
                self._advancePhase()
                return False
            elif self.phase == "COMBO":
                self.summary.extend(self.player.getLevelupCombos())
                self._advancePhase()
                return False
            elif self.phase == "SUMMARY":
                self._modifyHero()
                self.screen.hide_dialog()
                self.reset()
                return self.player.dehydrate()
                
    def _modifyHero(self):
        if self.skill:
            self.player.abilities.append(ability.Ability(self.skill.name, self.player))
        if self.spellA:
            self.player.spellList.append(spell.Spell(self.spellA.name, self.player))
        if self.spellB:
            self.player.spellList.append(spell.Spell(self.spellB.name, self.player))
        if self.trait.name in [x.name for x in self.player.traits]:
            for t in self.player.traits:
                if t.name == self.trait.name:
                    t.advanceTier()
        else:
            self.player.traits.append(trait.Trait(self.trait.name, self.player))
        for item in self.summary:
            if isinstance(item, ability.AbilityStub):
                self.player.abilities.append(ability.Ability(item.name, self.player))
            elif isinstance(item, passiveability.PassiveAbilityStub):
                self.player.passiveAbilities.append(passiveability.PassiveAbility(item.name, self.player))
        # Stats have already been added.
                
    def _advancePhase(self):
        currentPhaseIndex = self.phaseList.index(self.phase)
        self.phase = self.phaseList[currentPhaseIndex + 1]
        self.next()
        
    def _determinePhaseList(self):
        self.phaseList = ["TRAIT"]
        if self.player.level in self.player.skillLevels:
            self.phaseList.append("SKILL")
        if self.player.level in self.player.spellLevels:
            if self.player.spellLevels[self.player.level] == 1:
                self.phaseList.append("SPELL_1")
            elif self.player.spellLevels[self.player.level] == 2:
                self.phaseList.append("SPELL_1")
                self.phaseList.append("SPELL_2")
        self.phaseList.append("COMBO")
        self.phaseList.append("SUMMARY")
        
    def reset(self):
        self.phase = None
        self.phaseList = []
        self.skill = None
        self.spellA = None
        self.spellB = None
        self.trait = None
        self.summary = []
        
        self.traitOptions = []
        self.skillOptions = []
        self.spellOptions = []