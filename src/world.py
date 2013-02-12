'''
World generation tools and representation
'''

import os

from entity import*
from const import*
from sprites import*
from theorycraft import TheoryCraft

class World(object):
    '''
    Represents the world

    Member Variables
        seed: the random seed for this world
    '''

    def __init__(self, seed):
        self.seed = seed

    def get_pane(self, location):
        return Pane(self.seed, location)
                
class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        tiles: Dictionary of coordinate tuples (e.g. (0,1)) to tile objects
    '''

    def __init__(self, seed, location):
        self.seed = seed
        self.location = location
        
        random.seed(self.seed + str(location))
        i = random.randrange(len(BACKGROUNDS))

        background = crop_helper(BACKGROUNDS[i])
        treesheet = SpriteSheet(TREES, self.seed + str(location))
        rocksheet = SpriteSheet(ROCKS, self.seed + str(location))
        
        self.images = dict(background.images.items() + treesheet.images.items() + rocksheet.images.items())
        self.tiles = dict()
        self.people = []
        
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)] = Tile(background.getimage((i, j)), True)
                tree = treesheet.get_random_entity(str((i,j)), RAND_TREES)
                rock = rocksheet.get_random_entity(str((i,j)), RAND_ROCKS)
                if tree:
                    self.tiles[(i, j)].entities.append(Entity((i, j), image=tree))
                if rock:
                    self.tiles[(i, j)].entities.append(Entity((i, j), image=rock))
        
    def is_tile_passable(self, location):
        return self.tiles[location.tile].is_passable()
        
    def generate_creatures(self):
        #self.people.append(TheoryCraft.getNewPlayerCharacter("Human", "Barbarian", len(self.people)))
        self.people.append(TheoryCraft.getMonster(len(self.people)))
            
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
      