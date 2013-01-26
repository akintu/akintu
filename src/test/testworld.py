import pygame
from PIL import Image
from pygame.locals import *

import sys
import os

imagespath = os.path.join("res", "images", "background")
tmpimages = os.path.join("res", "images", "background", "tmp")
grassimage = os.path.join("test", "grass.png")
backgroundimage = os.path.join(imagespath, "grass2.jpg")

class Pane(object):
    def __init__(self, location, tiles = None, startpoint = None):
        if not tiles:
            self.tiles = dict()
            background = BackgroundTiles(backgroundimage, (512, 512), (32, 32))
            for i in range(32):
                for j in range(20):
                    self.tiles[(i, j)] = background.gettile((i, j))
        if not startpoint:
            self.startpoint = (0, 0)

class Tile(object):
    def __init__(self, image = grassimage, passable = True):
        self.entities = []
        self.image = image
        self.passable = passable

class BackgroundTiles(object):
    def __init__(self, path, imagesize, tilesize):
        self.tiles = dict()
        self.images = dict()
        self.backimage = Image.open(path)
        self.backimage.resize(imagesize)
        self.x = imagesize[0]/tilesize[0]
        self.y = imagesize[1]/tilesize[1]
        currx = 0
        for i in range(self.x):
            curry = 0
            for j in range(self.y):
                id = "background_" + str(i) + "_" + str(j)
                self.tiles[(i, j)] = Tile(id, True)
                self.images[id] = self.backimage.crop(
                    (currx, curry, currx+tilesize[0], curry+tilesize[1]))
                
                curry += tilesize[1]
            currx += tilesize[0]
            
    def gettile(self, location):
        i = location[0] % self.x
        j = location[1] % self.y
        return self.tiles[(i, j)]
        
            