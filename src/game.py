'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys

from gamescreen import GameScreen

# TEST
sys.path.append("test")
from testworld import *

class Game(object):
    def __init__(self):
        # Set up game engine
        self.screen = GameScreen()

        # TEST code
        self.pane = Pane((0,0))
        self.screen.set_pane(self.pane)
        location = self.screen.add_player("Colton", None)
        self.player = ["Colton", location]

        while True:
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
        if self.pane.tiles.has_key(tupleloc) and self.pane.tiles[tupleloc].passable:
            return True
        return False
