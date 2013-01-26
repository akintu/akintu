'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys

from const import *
from gamescreen import GameScreen
from world import *


class Game(object):
    def __init__(self):
        # Set up game engine
        self.screen = GameScreen()
        self.world = World()

        self.pane, imagedict = self.world.get_pane((0,0))

        # TEST code
        self.screen.update_images(imagedict)
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
        if not self.pane.tiles.has_key(tupleloc):
            return False
        if not self.pane.tiles[tupleloc].passable:
            return False
            tile = self.pane.tiles[tupleloc]
            for ent in tile.entities:
                if not ent.passable:
                    return False
        return True
