import pygame
from pygame.locals import *

import sys
import os

grassimage = os.path.join("test", "grass.png")

class Pane(object):
    def __init__(self, location, tiles = None, startpoint = None):
        if not tiles:
            self.tiles = dict()
            for i in range(32):
                for j in range(20):
                    self.tiles[(i, j)] = Tile(grassimage, True)
        if not startpoint:
            self.startpoint = (0, 0)

class Tile(object):
    def __init__(self, image = grassimage, passable = True):
        self.image = image
        self.passable = passable
