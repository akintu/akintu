'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys

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
    def __init__(self):
        seed = "CorrectHorseStapleBattery"
        TheoryCraft.loadAll()   #Static method call, Devin's stuff.
        Sprites.load(seed)
        self.world = World(seed)
        self.keystate = 0
        self.running = False
        self.id = -1

        self.serverip = "localhost"
        if len(sys.argv) == 1:
            GameServer(self.world)
        else:
            self.serverip = sys.argv[1]

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

        self.CDF.send(Person(PersonActions.CREATE, None, Location((0, 0), (PANE_X/2, PANE_Y/2)), \
            (CreatureTypes.PLAYER, "Human", "Assassin")))

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
                    self.switch_panes(command.location)
                    self.location = command.location
            
                if command.details[0] == CreatureTypes.PLAYER:
                    self.pane.person[command.id] = \
                        TheoryCraft.getNewPlayerCharacter(command.details[1], command.details[2])
                if command.details[0] == CreatureTypes.MONSTER:
                    self.pane.person[command.id] = TheoryCraft.getMonster()
                self.pane.person[command.id].location = command.location
                    
                imagepath = os.path.join('res', 'images', 'sprites', self.pane.person[command.id].image)
                persondict = {'location': command.location, 'image': imagepath, 'team': 'Players'}
                self.screen.add_person(command.id, persondict)

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.pane.person[command.id].location = command.location
                self.screen.update_person(command.id, {'location': command.location})
                if self.id == command.id:
                    self.location = command.location

            ###### RemovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
                if command.id == self.id:
                    self.id = -1
                    self.pane.person = {}
                else:
                    self.screen.remove_person(command.id)
                    del self.pane.person[command.id]
                    
            ###### StopRunning ######
            if isinstance(command, Person) and command.action == PersonActions.STOP:
                if command.id == self.id:
                    self.running = False
                    
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
        newloc = self.location.move(direction, distance)
        if (self.location.pane == newloc.pane and self.pane.is_tile_passable(newloc) and \
                newloc.tile not in [x.location.tile for x in self.pane.person.values()]) or \
                self.location.pane != newloc.pane:
            if self.running:
                self.CDF.send(Person(PersonActions.STOP, self.id))
                self.running = False
            if self.keystate in [K_LSHIFT, K_RSHIFT]:
                self.CDF.send(Person(PersonActions.RUN, self.id, direction))
                self.running = True
            else:
                self.CDF.send(Person(PersonActions.MOVE, self.id, newloc))
                if self.location.pane == newloc.pane:
                    self.location = newloc
                    self.screen.update_person(self.id, {'location': self.location})

    def switch_panes(self, location):
        #TODO we can add transitions here.
        self.pane = self.world.get_pane(location.pane)
        self.screen.set_pane(self.pane)
