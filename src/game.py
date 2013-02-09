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
from world import *

clock = pygame.time.Clock()

class Game(object):
    def __init__(self):
        self.world = World("CorrectHorseStapleBattery")
        self.keystate = 0
        self.running = 0
        self.people = []
        self.index = -1
        
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


        self.CDF.send(Person(PersonActions.CREATE, None, Location((0, 0), (PANE_X/2, PANE_Y/2))))
        
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
                if self.index == -1:  # Pane setup, player already drawn
                    self.index = command.index
                    self.switch_panes(command.location)
                    self.location = command.location
                else:
                    self.people.append(command.location)
                    self.screen.add_person(len(self.people) - 1, None, command.location)

            ###### MovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.MOVE:
                self.people[command.index] = command.location
                self.screen.update_person(command.index, command.location)
                if self.index == command.index:
                    self.location = command.location

            ###### RemovePerson ######
            if isinstance(command, Person) and command.action == PersonActions.REMOVE:
                if command.index == self.index:
                    self.index = -1
                    self.people = []
                else:
                    self.screen.remove_person(command.index)
                    for i in range(command.index + 1, len(self.people)):
                        self.screen.remove_person(i)
                        self.screen.add_person(i - 1, None, self.people[i])
                    if command.index < self.index:
                        self.index -= 1
                    self.people.pop(command.index)

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
                elif event.key in [K_LEFT, K_KP4, K_h]:
                    self.move_person(4, 1)
                elif event.key in [K_RIGHT, K_KP6, K_l]:
                    self.move_person(6, 1)
                elif event.key in [K_UP, K_KP8, K_k]:
                    self.move_person(8, 1)
                elif event.key in [K_DOWN, K_KP2, K_j]:
                    self.move_person(2, 1)
                elif event.key in [K_KP7, K_y]:  # UP LEFT
                    self.move_person(7, 1)
                elif event.key in[K_KP9, K_u]:  # UP RIGHT
                    self.move_person(9, 1)
                elif event.key in [K_KP3, K_n]:  # DOWN RIGHT
                    self.move_person(3, 1)
                elif event.key in [K_KP1, K_b]:  # DOWN LEFT
                    self.move_person(1, 1)

    def move_person(self, direction, distance):
        newloc = self.location.move(direction, distance)
        if (self.location.pane == newloc.pane and self.pane.is_tile_passable(newloc) and \
                newloc.tile not in [x.tile for x in self.people]) or self.location.pane != newloc.pane:
            if self.running:
                self.CDF.send(Person(PersonActions.STOP, self.index))
                self.running = False
            if self.keystate in [K_LSHIFT, K_RSHIFT]:
                self.CDF.send(Person(PersonActions.RUN, self.index, direction))
                self.running = True
            else:
                self.CDF.send(Person(PersonActions.MOVE, self.index, newloc))
                if self.location.pane == newloc.pane:
                    self.location = newloc
                    self.screen.update_person(self.index, self.location)

    def switch_panes(self, location):
        #TODO we can add transitions here.
        self.pane, imagedict = self.world.get_pane(location.pane)
        self.screen.set_pane(self.pane, imagedict)