'''
Has multiple building types defined here using Building as the 
super class.
Some Ideas:
	Shops
	Dungeons
	Respec Areas
	...
'''

import random

from const import*
from region import*

class Building(object):
    def __init__(self, boundary_type, bounds, pane_loc):
        '''
        bounds: (min_x, max_x, min_y, max_y)
        '''
        
        # (x, y) size of outer border
        size = (random.randrange(bounds[0], bounds[1]), random.randrange(bounds[2], bounds[3]))
        loc = (random.randrange(0, PANE_X-size[0]), random.randrange(0, PANE_Y-size[1]))
        bound = (loc[0]+size[0], loc[1]+size[1])
        
        innerloc = (loc[0]+1, loc[1]+1)
        innerbound = (bound[0]-1, bound[1]-1)

        boundary = Region()
        boundary("ADD", "SQUARE", Location(pane_loc, loc), Location(pane_loc, bound) )
        boundary("SUB", "SQUARE", Location(pane_loc, innerloc), Location(pane_loc, innerbound))
        
        path = Region()
        center = (loc[0] + size[0]/2, loc[1] + size[1]/2)
        opening = (center[0], loc[1]) #Top middle
        boundary("SUB", "LINE", Location(pane_loc, center), Location(pane_loc, opening), 2)
        path("ADD", "LINE", Location(pane_loc, center), Location(pane_loc, opening), 2)
        self.path = path
        self.boundary = boundary
        self.bounds = (loc[0], loc[1], bound[0], bound[1])
        self.center = center
    
class Shop(Building):
    pass
    
class House(Building):
    pass
    
class Garden(Building):
    pass
    
class Respec(Building):
    pass