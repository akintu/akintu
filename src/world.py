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
from township import *
from country import *
from building_inside import *


class World(object):
    '''
    Represents the world and handles what to load and when.
    The world consists of Panes, Townships, and Counties. A
    Country contains a 5x5 grid of Townships and a Township
    contains a 5x5 grid of panes.
    
    Since the world is *infinite* we don't want to generate 
    everything at once. In order to facilitate this, you must
    provide a pane location. Unlike Township tuple locations, 
    Country and Pane locations are not recycled.

    Member Variables
        seed: The random seed for this world
        pane: The pane location we want to generate first
    '''

    def __init__(self, seed, pane=Location(0,0)):
        self.seed = seed
        self.panes = dict()
        self.pane_items = dict()
        self.pane_chests = dict()
        self.curr_pane = None
        self.countries = dict()
        self._generate_world(pane)

    def is_town_pane(self, location):
        if isinstance(location, Location):
            loc = location.pane
        else:
            loc = location
        if loc in self._listTowns(loc):
            return True
        else:
            return False

    def get_pane(self, location, is_server=False):
        '''
        Given a location tuple or object, returns the pane object for that
        position in the world.
        Member Variables:
            is_server:  Boolean value indicating whether the caller is the server
            portal:     Currently unimplemented, but will be used for indoor locations
        '''

        state = None
        if is_server:
            state = State.load_pane(location)
        if not location in self._listTowns(location):
            self.panes[location] = Pane(self.seed, location, is_server=is_server, load_entities=True, pane_state=state)
        else:
            self.panes[location] = self._getTown(location, is_server, True, state)
        self._loadStamps(location=location)
        self.panes[location].load_images()

        if not is_server:
            self.panes[location].person = {}
        return self.panes[location]

    def _loadStamps(self, location):
        if isinstance(location, Location):
            pane = location.pane
        else:
            pane = location

        country_loc, township_loc = Township.getTownshipLocation(pane)
        if not country_loc in self.countries:
            self._generate_world(pane)
        stamps = self.countries[country_loc].getStamps(pane)
        if stamps:
            self.panes[location].load_stamps(loc_stamp_dict=stamps, clear_region=True)

    def _getTown(self, location, is_server, load_entities, pane_state):
        return Town(self.seed, location, is_server, load_entities, pane_state)
    
    def _listTowns(self, location):
        '''
        Returns a list of towns in the country that contains
        the pane given by location.
        '''

        if isinstance(location, Location):
            loc = location.pane
        else:
            loc = location
        country_loc, township_loc = Township.getTownshipLocation(loc)
        if not country_loc in self.countries:
            self._generate_world(loc)
        return self.countries[country_loc].towns
        

    def _generate_world(self, pane):
        if isinstance(pane, Location):
            pane = pane.pane
        country_loc, township_loc = Township.getTownshipLocation(pane)
        c = Country(self.seed, country_loc)
        self.countries[country_loc] = c 

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

