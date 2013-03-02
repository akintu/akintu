'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys
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


clock = pygame.time.Clock()

class Game(object):
    def __init__(self, seed, serverip=None, state=None):
        #seed = "CorrectHorseStapleBattery"
        TheoryCraft.loadAll()   #Static method call, Devin's stuff.
        Sprites.load(seed)
        self.world = World(seed, world_state=state)
        self.pane = None
        
        # Game state
        self.id = -1
        self.keystate = 0
        self.running = False
        self.combat = False
        
        # Setup server if host
        self.serverip = "localhost"
        if serverip:
            self.serverip = sys.argv[1]
        else:
            Combat.gameServer = GameServer(self.world)
            
        # if len(sys.argv) == 1:
            # GameServer(self.world)
        # else:
            # self.serverip = sys.argv[1]

        self.CDF = ClientDataFactory()
        reactor.connectTCP(self.serverip, 1337, self.CDF)

        self.setup = LoopingCall(self.setup_game)
        self.setup.start(0)

        reactor.run()

    def setup_game(self):
        if not self.CDF.port:
            return

        # Set up game engine
        self.screen = GameScreen()
        Combat.screen = self.screen

        self.CDF.send(Person(PersonActions.CREATE, None, Location((0, 0), (PANE_X/2, PANE_Y/2)), \
            ("Player", "Human", "Barbarian")))

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
                    'level': p.level}
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
                    del self.pane.person[command.id]
                    
            ###### StopRunning ######
            if isinstance(command, Person) and command.action == PersonActions.STOP:
                if command.id == self.id:
                    self.running = False
                    
            ###### Initiate Combat ######
            if isinstance(command, Update) and command.property == UpdateProperties.COMBAT:
                self.combat = command.value
            ###### Update AP ######    
            if isinstance(command, Update) and command.property == UpdateProperties.AP:
                self.pane.person[command.id].AP = command.value
                self.screen.update_person(command.id, {'AP': command.value, 'team': self.pane.person[command.id].team})
            ###### Update MP ######
            if isinstance(command, Update) and command.property == UpdateProperties.MP:
                self.pane.person[command.id].MP = command.value
                self.screen.update_person(command.id, {'MP': command.value, 'team': self.pane.person[command.id].team})
            ###### Update HP ######
            if isinstance(command, Update) and command.property == UpdateProperties.HP:
                self.pane.person[command.id].HP = command.value
                self.screen.update_person(command.id, {'HP': command.value, 'team': self.pane.person[command.id].team})
                
    def handle_events(self):
        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
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
                
            elif self.pane.person[self.id].AP >= self.pane.person[self.id].totalMovementAPCost:
                self.CDF.send(Person(PersonActions.MOVE, self.id, newloc))
                if self.pane.person[self.id].location.pane == newloc.pane:
                    self.animate(self.id, self.pane.person[self.id].location, newloc, \
                        1.0 / self.pane.person[self.id].movementSpeed)
                    self.pane.person[self.id].location = newloc

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
