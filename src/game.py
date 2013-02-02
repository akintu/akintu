'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys
import threading

from network import *
from const import *
from gamescreen import GameScreen
from world import *
import sys
clock = pygame.time.Clock()


class Game(object):
    def __init__(self):
        if len(sys.argv) == 1:
            self.server = True
            self.SDF = ServerDataFactory()
            reactor.callInThread(start_server, self.SDF, 1337)
        else:
            self.server = False
            self.CDF = ClientDataFactory()
            ipaddress = sys.argv[1]
            reactor.callInThread(start_client, self.CDF, ipaddress, 1337)
            
        # Set up game engine
        self.screen = GameScreen()
        self.world = World("CorrectHorseStapleBattery")

        self.pane, imagedict = self.world.get_pane((0, 0))

        # TEST code
        self.screen.set_pane(self.pane, imagedict)
        location = self.screen.add_player("Colton", None)
        self.player = ["Colton", location]

        
        reactor.callInThread(self.game_loop)
        #reactor.run()
        self.game_loop()

    def game_loop(self):
        fps_counter = 0
        fps = 0

        while True:
            clock.tick()
            fps_counter += 1
            if fps_counter > fps:
                fps = clock.get_fps()
                if(fps >= 1000000000):
                    fps = 0
                self.screen.set_fps(fps)
                fps_counter = 0
            pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit(0)
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sys.exit(0)
                    elif event.key == K_LEFT:
                        self.move_player(-1, 0)
                    elif event.key == K_RIGHT:
                        self.move_player(1, 0)
                    elif event.key == K_UP:
                        self.move_player(0, -1)
                    elif event.key == K_DOWN:
                        self.move_player(0, 1)
            self.screen.update()

    def move_player(self, dx, dy):
        newloc = (self.player[1][0] + dx, self.player[1][1] + dy)
        if self.passable(newloc):
            self.player[1] = newloc
            self.screen.update_player(self.player[0], self.player[1])

    def passable(self, newloc):
        tupleloc = tuple(newloc)
        if not tupleloc in self.pane.tiles:
            return False
        if not self.pane.tiles[tupleloc].passable:
            return False
        tile = self.pane.tiles[tupleloc]
        for ent in tile.entities:
            if not ent.passable:
                return False
        return True

    def switch_panes(self, location, startpoint):
        pass