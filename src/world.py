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
        random.seed(self.seed + str(location))
        i = random.randrange(len(BACKGROUNDS))

        background = crop_helper(BACKGROUNDS[i])
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
                if rock:
                    tiles[(i, j)].entities.append(Entity(rock, False))
        
        return (Pane(self.seed, location, tiles), images)
                
class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        tiles: Dictionary of coordinate tuples (e.g. (0,1)) to tile objects
    '''

    def __init__(self, seed, location, tiles):
        self.seed = seed
        self.tiles = tiles
        self.location = location
        
    def is_tile_passable(self, location):
        return self.tiles[location.tile].is_passable()
            
class Tile(object):
    def __init__(self, image = grassimage, passable = True):
        self.entities = []
        self.image = image
        self.passable = passable
    
    def is_passable(self):
        if self.passable == False:
            return False
        for ent in self.entities:
            if ent.passable == False:
                return False
        return True
        
class Entity(object):
    def __init__(self, image = rockimage, passable = False):
        self.image = image
        self.passable = passable
      