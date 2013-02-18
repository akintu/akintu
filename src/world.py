'''
World generation tools and representation
'''

import os

from entity import*
from const import*
from sprites import*
from location import Location
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
        self.panes = dict()
        surrounding_panes = Location(location, None).get_surrounding_panes()
        for key, loc in surrounding_panes.iteritems():
            if not loc in self.panes:
                self.panes[loc] = Pane(self.seed, loc)
        self._merge_tiles(surrounding_panes)
        
        self.panes[location] = Pane(self.seed, location)
        return self.panes[location]
    
    def _generate_world(self):
        pass
    
    def _verify_path(self, start_location, end_location):
        pass
        
    def _merge_tiles(self, panes):
        '''
        Merges the edge tiles of the surrounding panes with the current pane
        
        Member Variables
            panes:  A dictionary of tuples that represent the panes to be merged.
                    This is given from Location.get_surrounding_panes()
        '''
        curr_pane = self.panes[panes[5]]  #Get our current pane
        for key, value in panes.iteritems():
            surr_pane = self.panes[value]
            edge_tiles = surr_pane.get_edge_tiles(10-key)
            curr_pane.merge_tiles(key, edge_tiles)    #We request the opposite side

class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        tiles: Dictionary of coordinate tuples (e.g. (0,1)) to tile objects
    '''
    PaneCorners = {1:TILE_BOTTOM_LEFT, 3:TILE_BOTTOM_RIGHT, 7:TILE_TOP_LEFT, 9:TILE_TOP_RIGHT}
    PaneEdges = {'2':TILES_BOTTOM, '4':TILES_LEFT, '6':TILES_RIGHT, '8':TILES_TOP}

    def __init__(self, seed, location):
        self.seed = seed
        self.location = location
        self.load_images()
    
    def load_images(self):
        background = Sprites.get_random_background(self.seed + str(self.location))
        
        self.treesheet = SpriteSheet(TREES, self.seed + str(self.location))
        self.rocksheet = SpriteSheet(ROCKS, self.seed + str(self.location))
        
        self.images = dict()
        self.images.update(background.images.items())
        self.images.update(self.treesheet.images.items())
        self.images.update(self.rocksheet.images.items())
        self.tiles = dict()
        self.people = {}
        
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)] = Tile(background.getimage((i, j)), True)
                tree = self.treesheet.get_random_entity(str((i, j)), RAND_TREES)
                rock = self.rocksheet.get_random_entity(str((i, j)), RAND_ROCKS)
                if tree:
                    self.tiles[(i, j)].entities.append(Entity((i, j), image=tree))
                if rock:
                    self.tiles[(i, j)].entities.append(Entity((i, j), image=rock))
                #self.add_obstacle((i, j))
    def is_tile_passable(self, location):
        return self.tiles[location.tile].is_passable()
        
    def generate_creatures(self):
        #self.people.append(TheoryCraft.getNewPlayerCharacter("Human", "Barbarian", len(self.people)))
        person = TheoryCraft.getMonster()
        self.people[id(person)] = person
    
    def get_edge_tiles(self, edge):
        passable_list = []
        if edge in Pane.PaneCorners:
            tile_loc = Pane.PaneCorners[edge]
            passable_list.append(self.is_tile_passable(Location(self.location, tile_loc)))
            return passable_list
        if edge in Pane.PaneEdges:
            return passable_list
        
    def merge_tiles(self, edge_id, tiles):
        if tiles and edge_id in [2, 4, 6, 8]: #Edge Tiles
            #print "MERGE_TILES: EDGE"
            assert False
            pass
        if tiles and edge_id in [1, 3, 7, 9]: #Corner Tiles
            #print "MERGE_TILES: CORNER"
            for passable in tiles:
                if not passable:
                    #print "NOT PASSABLE"
                    self.add_obstacle(Pane.PaneCorners[edge_id])

    def add_obstacle(self, location):
        object = Sprites.get_random_object(self.seed + str(location))
        self.tiles[location].entities.append(Entity(location, image=object))
        self.tiles[location].passable = False
    
class Tile(object):
    def __init__(self, image = os.path.join("res", "images", "background", "grass.png"), passable = True):
        self.entities = []
        self.image = image
        self.passable = passable
    
    def __repr__(self):
        return "(%s, %s, %s)" % (self.passable, self.image, self.entities)
    
    def is_passable(self):
        if self.passable == False:
            return False
        for ent in self.entities:
            if ent.passable == False:
                return False
        return True

if __name__ == "__main__":
    '''
    Test World
    '''
    print "Pass"
    