'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys
import time
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


clock = pygame.time.Clock()

class Game(object):
    def __init__(self, port, serverip=None, state=None, player=None):
        '''
        Parameters:
            port:       required for both host and client
            serverip:   None if hosting, required for client
            state:      state={SEED_KEY: "seed"} if new game, or
                        state="SaveFile.###" if loading game
            player:     player=("Name", "Race", "Class") if new player
                        player="PlayerRepresentation.whatever" if loading
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
        self.keystate = 0
        self.running = False
        self.combat = False

        # Selection state
        self.selectionMode = "targeting"
        self.currentTargetId = None
        self.panePersonIdList = []
        self.currentAbility = None
        self.abilityList = []

        # Setup server if host
        self.port = port
        if serverip:
            self.serverip = serverip
        else:
            self.serverip = "localhost"
            Combat.gameServer = GameServer(self.world, self.port)

        self.CDF = ClientDataFactory()
        reactor.connectTCP(self.serverip, self.port, self.CDF)
        
        if isinstance(player, tuple):
            person = Person(PersonActions.CREATE, None, Location((0, 0), (PANE_X/2, PANE_Y/2)), \
            ("Player", player[0], player[1], player[2]))
        else: 
            #TODO: Might need to unpickle a player/rehydrate it
            person = player
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
            if isinstance(command, Person) and command.action == PersonActions.CREATE:
                if self.id == -1:  # Need to setup the pane
                    self.id = command.id
                    self.switch_panes(command.location, self.combat)

                self.pane.person[command.id] = TheoryCraft.convertFromDetails(command.details)
                self.pane.person[command.id].location = command.location

                imagepath = os.path.join('res', 'images', 'sprites', self.pane.person[command.id].image)
                p = self.pane.person[command.id]
                persondict = {'location': command.location, 'image': imagepath, 'team': p.team, \
                    'HP': p.HP, 'totalHP': p.totalHP, 'MP': p.MP, \
                    'totalMP': p.totalMP, 'AP': p.AP, 'totalAP': p.totalAP, \
                    'level': p.level, 'name' : p.name}
                self.screen.add_person(command.id, persondict)

            if isinstance(command, Person) and command.id not in self.pane.person:
                continue

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                if command.details:
                    if self.pane.person[command.id].anim:
                        self.pane.person[command.id].anim.stop()
                        self.pane.person[command.id].anim = None
                    self.screen.update_person(command.id, {'location': command.location})
                else:
                    self.animate(command.id, self.pane.person[command.id].location, command.location, \
                            1.0 / self.pane.person[command.id].movementSpeed)
                self.pane.person[command.id].location = command.location

            ###### RemovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
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
            if isinstance(command, Person) and command.action == PersonActions.STOP:
                if command.id == self.id:
                    self.running = False

            ###### Initiate Combat ######
            elif isinstance(command, Update) and command.property == UpdateProperties.COMBAT:
                self.combat = command.value
            ###### Update AP ######
            elif isinstance(command, Update) and command.property == UpdateProperties.AP:
                self.pane.person[command.id].AP = command.value
                self.screen.update_person(command.id, {'AP': command.value, 'team': self.pane.person[command.id].team})
            ###### Update MP ######
            elif isinstance(command, Update) and command.property == UpdateProperties.MP:
                self.pane.person[command.id].MP = command.value
                self.screen.update_person(command.id, {'MP': command.value, 'team': self.pane.person[command.id].team})
            ###### Update HP ######
            elif isinstance(command, Update) and command.property == UpdateProperties.HP:
                self.pane.person[command.id].HP = command.value
                self.screen.update_person(command.id, {'HP': command.value, 'team': self.pane.person[command.id].team})
            ###### Update Text #####
            elif isinstance(command, Update) and command.property == UpdateProperties.TEXT:
                self.screen.show_text(command.value, color=command.details)
            ###### Update Movement AP Cost ####
            elif isinstance(command, Update) and command.property == UpdateProperties.MOVE_AP_COST:
                self.pane.person[command.id].overrideMovementAPCost = command.value
            ###### Update Movement Tiles #####
            elif isinstance(command, Update) and command.property == UpdateProperties.MOVE_TILES:
                self.pane.person[command.id].remainingMovementTiles = command.value
            ###### Update HP Buffers ######
            elif isinstance(command, Update) and command.property == UpdateProperties.HP_BUFFER:
                self.screen.update_person(command.id, {'buffedHP' : command.value, 'totalHP' : self.pane.person[command.id].totalHP,
                                                    'team' : self.pane.person[command.id].team})
            
            
    def handle_events(self):
        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
            #### General commands ####
            if event.type == QUIT:
                reactor.stop()
            if event.type == KEYUP:
                if event.key in [K_LSHIFT, K_RSHIFT]:
                    self.keystate = 0
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    reactor.stop()
                elif event.key in [K_LSHIFT, K_RSHIFT]:
                    self.keystate = event.key
                elif event.key in MOVE_KEYS:
                    self.move_person(MOVE_KEYS[event.key], 1)
                elif event.key == K_EQUALS or event.key == K_PAGEUP:
                        self.screen.scroll_up()
                elif event.key == K_MINUS or event.key == K_PAGEDOWN:
                        self.screen.scroll_down()
                elif event.key == K_UNDERSCORE:
                        self.screen.scroll_down(1000)
                elif event.key == K_PLUS:
                        self.screen.scroll_up(1000)   
                        
                ### Combat Only Commands ###
                if self.combat:
                    if event.key == K_f:
                        if self.selectionMode == "targeting":
                            self.selectionMode = "abilities"
                            self.screen.show_text("Selection mode: ability selection", color='yellow')
                        elif self.selectionMode == "abilities":
                            self.selectionMode = "targeting"
                            self.screen.show_text("Selection mode: targeting", color="yellow")
                    elif event.key == K_e:
                        if self.selectionMode == "targeting":
                            self.cycle_targets()
                        else:
                            self.cycle_abilities()
                    elif event.key == K_w: 
                        if self.selectionMode == "targeting":
                            self.cycle_targets(reverse=True)
                        else:
                            self.cycle_abilities(reverse=True)
                    elif event.key == K_a:
                        self.attempt_attack()
                    elif event.key == K_n:
                        self.force_end_turn()
                    elif event.key == K_s:
                        #self.select_self()
                        pass
                    elif event.key == K_i:
                        #self.begin_select_consumable() -- Cycling will be used as well as A for accept and
                        # C for cancel.
                        pass
                    elif event.key == K_PERIOD:
                        #self.display_target_details()
                        pass
                    elif event.key == K_SLASH:
                        #self.toggle_size_display()
                        pass
                ### Strictly non-combat commands ###
                if not self.combat:
                    if event.key == K_g:
                        self.get_item()
                    if event.key == K_b:
                        #self.break_in() -- Will bash/pick-lock chests.  Will attempt a picklock first if
                        # you are a thief primary class.  If that fails, all other attempts will be bashes.
                        pass
                    
    def get_item(self):
        self.CDF.send(Person(PersonActions.OPEN, self.id))
        # If player is on an item, pick it up (the top item).
        # If player is on a treasure chest, attempt to open it.
        # If the chest is locked, send a message to the screen.
        # If the chest is unlocked, distribute treasure to this player
        #    and all others on this pane.
            
    def move_person(self, direction, distance):
        if self.running:
            self.CDF.send(Person(PersonActions.STOP, self.id))
            self.running = False

        newloc = self.pane.person[self.id].location.move(direction, distance)
        if not self.pane.person[self.id].anim and ((self.pane.person[self.id].location.pane == \
                newloc.pane and self.pane.is_tile_passable(newloc) and \
                newloc.tile not in [x.location.tile for x in self.pane.person.values()]) or \
                self.pane.person[self.id].location.pane != newloc.pane):

            if self.keystate in [K_LSHIFT, K_RSHIFT] and not self.combat:
                self.CDF.send(Person(PersonActions.RUN, self.id, direction))
                self.running = True
            
            elif self.pane.person[self.id].remainingMovementTiles > 0 or \
                 self.pane.person[self.id].AP >= self.pane.person[self.id].totalMovementAPCost:
                self.CDF.send(Person(PersonActions.MOVE, self.id, newloc))
                if self.pane.person[self.id].location.pane == newloc.pane:
                    self.animate(self.id, self.pane.person[self.id].location, newloc, \
                        1.0 / self.pane.person[self.id].movementSpeed)
                    self.pane.person[self.id].location = newloc

    def force_end_turn(self):
        ap = self.pane.person[self.id].AP
        movesLeft = self.pane.person[self.id].remainingMovementTiles
        if ap > 0 or movesLeft > 0:
            action = AbilityAction(AbilityActions.END_TURN, self.id, self.id)
            self.CDF.send(action)

    def attempt_attack(self):
        if not self.currentTargetId:
            print "No target selected."
            return
        self.CDF.send(AbilityAction(AbilityActions.ATTACK, self.id, self.currentTargetId, 
                      self.currentAbility.name))

    def display_size(self):
        pass
        # Switch between displaying monster levels and monster sizes
                      
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
        self.screen.show_text("Targeting: " + self.pane.person[self.currentTargetId].name, 
                                color='lightblue')

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

    def switch_panes(self, location, combat=False):
        #TODO we can add transitions here.
        if combat:
            self.pane = self.pane.get_combat_pane(location)
        else:
            self.pane = self.world.get_pane(location.pane)
        self.screen.set_pane(self.pane)
