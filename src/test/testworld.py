import pygame
from PIL import Image
from pygame.locals import *

import sys
import os

grassimage = os.path.join("test", "grass.png")
gravelbackground = os.path.join("test", "gravel.jpg")

class Pane(object):
    def __init__(self, location, tiles = None, startpoint = None):
        if not tiles:
            self.tiles = dict()
            background = backgroundImage(gravelbackground, (512, 512), (32, 32))
            for i in range(32):
                for j in range(20):
                    self.tiles[(i, j)] = Tile(background.getTile((i, j)), True)
        if not startpoint:
            self.startpoint = (0, 0)

class Tile(object):
    def __init__(self, image = grassimage, passable = True):
        self.image = image
        self.passable = passable

class backgroundImage(object):
	def __init__(self, path, imagesize, tilesize):
		self.tiles = dict()
		self.backimage = Image.open(path)
		self.backimage.resize(imagesize)
		self.x = imagesize[0]/tilesize[0]
		self.y = imagesize[1]/tilesize[1]
		currx = 0
		for i in range(self.x):
			curry = 0
			for j in range(self.y):
				tmp = path + str(i) + "_" + str(j) + ".png"
				self.tiles[(i, j)] = tmp
				image = self.backimage.crop((currx, curry, currx+tilesize[0], curry+tilesize[1]))
				image.save(tmp, "PNG")
				
				curry += tilesize[1]
			currx += tilesize[0]
				
	def getTile(self, location):
		i = location[0] % self.x
		j = location[1] % self.y
		return self.tiles[(i, j)]
		
			