'''
World generation tools and representation
'''

import os

from PIL import Image
from const import*

grassimage = os.path.join("res", "images", "background", "grass.png")
rockimage = os.path.join("res", "images", "rock.png")

class World(object):
    '''
    Represents the world

    Member Variables
        seed: the random seed for this world
    '''

    def __init__(self, seed):
        self.seed = seed

    def get_pane(self, location, position = None):
        # TODO: use seed to generate pane and tiles on pane
        imagespath = os.path.join("res", "images", "background")
        backgroundimage = os.path.join(imagespath, "grass2.jpg")
        background = BackgroundTiles(backgroundimage)
        tiles = dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                tiles[(i, j)] = Tile(background.getimage((i, j)), True)
        
        return (Pane(self.seed, location, tiles), background.images)

class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        tiles: Dictionary of coordinate tuples (e.g. (0,1)) to tile objects
    '''

    def __init__(self, seed, location, tiles, startpoint = None):
        self.tiles = tiles
        for x in range(PANE_X):
            for y in range(PANE_Y):
                if x == 0 or x == PANE_X-1 or y == 0 or y == PANE_Y-1:
                    self.tiles[(x,y)].entities.append(Entity(rockimage, False))
        
        del self.tiles[(0,PANE_Y/2)].entities[:]    #LEFT
        del self.tiles[(PANE_X/2, 0)].entities[:]   #TOP
        del self.tiles[(PANE_X-1,PANE_Y/2)].entities[:] #RIGHT
        del self.tiles[(PANE_X/2,PANE_Y-1)].entities[:] #BOTTOM
        
        if not startpoint:
            self.startpoint = (16, 10)
        else:
            self.startpoint = startpoint
            
class Tile(object):
    def __init__(self, image = grassimage, passable = True):
        self.entities = []
        self.image = image
        self.passable = passable
        
class Entity(object):
    def __init__(self, image = rockimage, passable = False):
        self.image = image
        self.passable = passable

class BackgroundTiles(object):
    def __init__(self, path):
        self.tile_id = dict()
        self.images = dict()
        self.backimage = Image.open(path)
        self.x = self.backimage.size[0]/TILE_SIZE
        self.y = self.backimage.size[1]/TILE_SIZE
        currx = 0
        for i in range(self.x):
            curry = 0
            for j in range(self.y):
                id = "background_" + str(i) + "_" + str(j)
                self.tile_id[(i, j)] = id
                self.images[id] = self.backimage.crop(
                    (currx, curry, currx + TILE_SIZE, curry + TILE_SIZE))
                
                curry += TILE_SIZE
            currx += TILE_SIZE
            
    def getimage(self, location):
        i = location[0] % self.x
        j = location[1] % self.y
        return self.tile_id[(i, j)]