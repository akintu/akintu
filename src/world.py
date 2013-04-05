'''
World generation tools and representation
'''

import os
import math
import random, time

from entity import*
from const import*
from pane import*
from location import Location
from theorycraft import TheoryCraft
from region import *
from ai import AI
from treasurechest import *


class World(object):
    '''
    Represents the world

    Member Variables
        seed: the random seed for this world
    '''

    def __init__(self, seed, nearestTown=Location(0,0)):
        self.seed = seed
        self.panes = dict()
        self.pane_items = dict()
        self.pane_chests = dict()
        self.curr_pane = None
        
    def is_town_pane(self, location):
        if isinstance(location, Location):
            loc = location.pane
        else:
            loc = location
        if loc in self._listTowns(loc):
            return True
        else:
            return False

    def is_dungeon_pane(self, location):
        pass

    def get_pane(self, location, is_server=False):
        if isinstance(location, Location):
            surrounding_locations = location.get_surrounding_panes()
        else:
            surrounding_locations = Location(location, None).get_surrounding_panes()
        for key, loc in surrounding_locations.iteritems():
            if not loc in self.panes:
                if loc in self._listTowns(loc):
                    self.panes[loc] = self._getTown(loc, False, False, None)
                else:
                    self.panes[loc] = Pane(self.seed, loc)
        #Check State For Pane
        state = None
        if is_server:
            state = State.load_pane(location)
            
        if not location in self._listTowns(location):
            self.panes[location] = Pane(self.seed, location, is_server=is_server, load_entities=True, pane_state=state)
        else:
            self.panes[location] = self._getTown(location, is_server, True, state)
            
        self._merge_tiles(surrounding_locations)
        self.panes[location].load_images()
        if not is_server:
            self.panes[location].person = {}
        return self.panes[location]
            
    def _getTown(self, location, is_server, load_entities, pane_state):
        town = Town(self.seed, location, is_server, load_entities, pane_state)
        
        # for tile in town.tiles:
            # town.remove_chest(tile):
        return town
    
    def _listTowns(self, location):
        '''
        location is an object
        '''
        if isinstance(location, Location):
            loc = location.pane
        else:
            loc = location
        #TODO: We can do some deterministic, dynamic placement here
        #but for now just return a static list of Towns
        return [(0, 0), (0, -2)]
        

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

if __name__ == "__main__":
    '''
    Test World
    '''
    a = Pane((0,0), "SomeSeed", False)
    #a.get_combat_pane(Location((0,0), (4,10)))

