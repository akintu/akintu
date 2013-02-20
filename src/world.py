'''
World generation tools and representation
'''

import os
import math

from entity import*
from const import*
from sprites import*
from location import Location
from theorycraft import TheoryCraft
from region import *
from ai import AI

class World(object):
    '''
    Represents the world

    Member Variables
        seed: the random seed for this world
    '''

    def __init__(self, seed):
        self.seed = seed

    def get_pane(self, location, is_server=False):
        self.panes = dict()
        surrounding_locations = Location(location, None).get_surrounding_panes()
        for key, loc in surrounding_locations.iteritems():
            if not loc in self.panes:
                self.panes[loc] = Pane(self.seed, loc)

        #This is the pane we will return, current pane
        self.panes[location] = Pane(self.seed, location)
        self._merge_tiles(surrounding_locations)
        
        self.panes[location].load_images()
        if not is_server:
            self.panes[location].person = {}
        return self.panes[location]
    
    def _generate_world(self):
        pass
    
    def _verify_path(self, start_location, end_location):
        pass
        
    def _merge_tiles(self, pane_locations):
        '''
        Merges the edge tiles of the surrounding panes with the current pane
        
        Member Variables
            pane_locations:  A dictionary of tuples that represent the panes to be merged.
                    This is given from Location.get_surrounding_panes()
        '''
        curr_pane = self.panes[pane_locations[5]]  #Get our current pane
        for key, value in pane_locations.iteritems():
            surrounding_pane = self.panes[value]
            edge_tiles = surrounding_pane.get_edge_tiles(10-key)#We request the opposite side
            curr_pane.merge_tiles(edge_tiles)    

class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        tiles: Dictionary of coordinate tuples (e.g. (0,1)) to tile objects
    '''
    PaneCorners = {1:TILE_BOTTOM_LEFT, 3:TILE_BOTTOM_RIGHT, 7:TILE_TOP_LEFT, 9:TILE_TOP_RIGHT}
    PaneEdges = {2:TILES_BOTTOM, 4:TILES_LEFT, 6:TILES_RIGHT, 8:TILES_TOP}

    def __init__(self, seed, location):
        self.seed = seed
        self.location = location
        self.tiles = dict()
        self.objects = dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)] = Tile(None, True)
                self.add_obstacle((i, j), RAND_ENTITIES)

    def load_images(self):
        
        self.images = Sprites.get_images_dict()
        self.person = {}
        
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)].set_image(Sprites.get_background(self.seed + str(self.location), (i, j)))

        for tile, entity_key in self.objects.iteritems():
            obstacle = Sprites.get_object(entity_key, self.seed, self.location, tile)
            self.tiles[tile].entities.append(Entity(tile, image=obstacle))
                
        #person = TheoryCraft.getNewPlayerCharacter("Human", "Barbarian")
        person = TheoryCraft.getMonster()
        person.location = Location(self.location, (PANE_X/2, PANE_Y/4))
        r = Region()
        r.build(RAct.ADD, RShape.CIRCLE, Location(self.location, CENTER), PANE_Y/4 + 1)
        r.build(RAct.SUBTRACT, RShape.CIRCLE, Location(self.location, CENTER), int(PANE_Y/6))
        person.ai.add("WANDER", person.ai.wander, 1, pid=id(person), region=r, move_chance=0.4)
        self.person[id(person)] = person
        
    def is_tile_passable(self, location):
        return self.tiles[location.tile].is_passable()
    
    def get_edge_tiles(self, edge):
        passable_list = dict()
        #Get the corner that edge represents
        if edge in Pane.PaneCorners:
            tile_loc = Pane.PaneCorners[edge]
            opposite = Location(None, tile_loc).get_opposite_tile(edge).tile
            if not self.is_tile_passable(Location(self.location, tile_loc)):
                passable_list[opposite] = self.objects[tile_loc]
        #Get the edge
        if edge in Pane.PaneEdges:
            edge_range = Pane.PaneEdges[edge]
            for x in range(edge_range[0][0], edge_range[1][0]+1):
                for y in range(edge_range[0][1], edge_range[1][1]+1):
                    opposite = Location(None, (x, y)).get_opposite_tile(edge).tile
                    if not self.is_tile_passable(Location(self.location, (x, y))):
                        passable_list[opposite] = self.objects[(x, y)]
        return passable_list

    def merge_tiles(self, tiles):
        if tiles:
            for tile, entity_key in tiles.iteritems():
                self.add_obstacle(tile, 1, entity_key)

    def add_obstacle(self, tile, percentage, entity_type=None):
        if not entity_type:
            random.seed(self.seed + str(self.location) + str(tile))
            if random.randrange(100) <= percentage*100:
                index = random.randrange(len(ENTITY_KEYS))
                self.objects[tile] = ENTITY_KEYS[index]
                self.tiles[tile].passable = False
        else:
            print "Merged " + str(entity_type)
            self.objects[tile] = entity_type
            self.tiles[tile].passable = False
            
class Tile(object):
    def __init__(self, image = os.path.join("res", "images", "background", "grass.png"), passable = True):
        self.entities = []
        self.image = image
        self.passable = passable
    
    def __repr__(self):
        return "(%s, %s, %s)" % (self.passable, self.image, self.entities)
    
    def set_image(self, image):
        self.image = image
        
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
    