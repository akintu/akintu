'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys
import threading
import command

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

        self.pane, imagedict = self.world.get_pane((0, 0))

        # TEST code
        self.screen.set_pane(self.pane, imagedict)
        location = self.screen.add_player("Colton", None)
        self.player = ["Colton", location]
        
        LoopingCall(self.server_loop).start(.0001)
        LoopingCall(self.game_loop).start(1.0 / DESIRED_FPS)
        
        reactor.run()
        
    def server_loop(self):
        #Check queue
        while not SDF.queue.empty():
            command = SDF.queue.get()
            
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
    
        