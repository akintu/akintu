'''
World generation tools and representation
'''

import os

from const import*
from sprites import*



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

        background = crop_helper(GRASS2)
        treesheet = SpriteSheet(TREES, self.seed + str(location))
        rocksheet = SpriteSheet(ROCKS, self.seed + str(location))
        images = dict(background.images.items() + treesheet.images.items() + rocksheet.images.items())
        tiles = dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                tiles[(i, j)] = Tile(background.getimage((i, j)), True)
                tree = treesheet.get_random_entity(str((i,j)), RAND_TREES)
                rock = rocksheet.get_random_entity(str((i,j)), RAND_ROCKS)
                if tree:
                    tiles[(i, j)].entities.append(Entity(tree, False))
                    # tmp = Entity(tree, False)
                    # tiles[(i, j)].entities[hash(tmp)] = tmp
                if rock:
                    tiles[(i, j)].entities.append(Entity(rock, False))
                    # tmp = Entity(rock, False)
                    # tiles[(i, j)].entities[hash(tmp)] = tmp
        
        return (Pane(self.seed, location, tiles), images)
                
class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        tiles: Dictionary of coordinate tuples (e.g. (0,1)) to tile objects
    '''

    def __init__(self, seed, location, tiles):#, startpoint = None):
        self.seed = seed
        self.tiles = tiles
        self.location = location

        # if not startpoint:
            # self.startpoint = (16, 10)
        # else:
            # self.startpoint = startpoint
            
class Tile(object):
    def __init__(self, image = grassimage, passable = True):
        self.entities = []
        self.image = image
        self.passable = passable
        
class Entity(object):
    def __init__(self, image = rockimage, passable = False):
        self.image = image
        self.passable = passable
      