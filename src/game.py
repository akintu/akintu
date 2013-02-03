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
from const import *
from gamescreen import GameScreen
from world import *
import sys
clock = pygame.time.Clock()

class Game(object):
    def __init__(self):
        self.serverip = "localhost"
        self.server = False
        if len(sys.argv) == 1:
            self.server = True
            self.SDF = ServerDataFactory()
            reactor.listenTCP(1337, self.SDF)
        else:
            self.serverip = sys.argv[1]

        #Always start a client, if you are the server, you serve yourself.
        self.CDF = ClientDataFactory()
        reactor.connectTCP(self.serverip, 1337, self.CDF)

        # Set up game engine
        self.screen = GameScreen()
        self.world = World("CorrectHorseStapleBattery")
        
        location = Location((0,0), (PANE_X/2, PANE_Y/2))
        self.switch_panes(location)
        position = self.screen.add_player("Colton", None, location)
        self.player = ["Colton", location]
        
        if self.server:
            LoopingCall(self.server_loop).start(0)
        LoopingCall(self.game_loop).start(1.0 / DESIRED_FPS)
        
        reactor.run()
        
        
    def server_loop(self):
        #Check queue
        while not self.SDF.queue.empty():
            command = self.SDF.queue.get()
            
        #Verify command requests
        
        #Send Reply

    def game_loop(self):
        fps = clock.get_fps()
        self.screen.set_fps(fps)
        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
            if event.type == QUIT:
                reactor.stop()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    reactor.stop()
                elif event.key in [K_LEFT, K_KP4, K_h]:
                    self.move_player(4, 1)
                elif event.key in [K_RIGHT, K_KP6, K_l]:
                    self.move_player(6, 1)
                elif event.key in [K_UP, K_KP8, K_k]:
                    self.move_player(8, 1)
                elif event.key in [K_DOWN, K_KP2, K_j]:
                    self.move_player(2, 1)
                elif event.key in [K_KP7, K_y]: #UP LEFT
                    self.move_player(7, 1)
                elif event.key in[K_KP9, K_u]: #UP RIGHT
                    self.move_player(9, 1)
                elif event.key in [K_KP3, K_n]: #DOWN RIGHT
                    self.move_player(3, 1)
                elif event.key in [K_KP1, K_b]: #DOWN LEFT
                    self.move_player(1, 1)
        self.screen.update()

    def move_player(self, direction, distance):
        newloc = self.player[1].move(direction, distance)#(self.player[1][1][0] + dx, self.player[1][1][1] + dy)
        if self.passable(newloc):
            self.CDF.send(MovePlayer(self.CDF.port, newloc))
            if self.player[1].pane != newloc.pane:
                self.switch_panes(newloc)
            self.player[1] = newloc
            self.screen.update_player(self.player[0], self.player[1])

    def passable(self, newloc):
        tupleloc = newloc.tile
        if not tupleloc in self.pane.tiles:
            return False
        if not self.pane.tiles[tupleloc].passable:
            return False
        tile = self.pane.tiles[tupleloc]
        for ent in tile.entities:
            if not ent.passable:
                return False
        return True

    def switch_panes(self, location):
        self.pane, imagedict = self.world.get_pane(location.pane)

        self.screen.set_pane(self.pane, imagedict)
    
        