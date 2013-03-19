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
from theorycraft import TheoryCraft

class Building(object):
    
    def __init__(self, boundary_type, bounds, pane_loc, size=None, location=None):
        '''
        bounds: (min_x, max_x, min_y, max_y)
        '''
        
        if not size:
            size = (random.randrange(bounds[0], bounds[1]), random.randrange(bounds[2], bounds[3]))
            
        if location:
            loc = location.tile
        else:
            loc = (random.randrange(0, PANE_X-size[0]), random.randrange(0, PANE_Y-size[1]))
        
        self.location = Location(pane_loc, loc)
        self.boundary_type = boundary_type
        self.npcs = dict()
        
        corner = (loc[0]+size[0], loc[1]+size[1])
        
        self.bounds = (loc[0], loc[1], corner[0], corner[1])
        self.center = (loc[0] + size[0]/2, loc[1] + size[1]/2)
        
        
        innerloc = (loc[0]+1, loc[1]+1)
        innerbound = (corner[0]-1, corner[1]-1)

        self.boundary = Region()
        self.boundary("ADD", "SQUARE", Location(pane_loc, loc), Location(pane_loc, corner) )
        self.boundary("SUB", "SQUARE", Location(pane_loc, innerloc), Location(pane_loc, innerbound))
        
        #This is the inner area that we need to clear out
        self.clear = Region()
        self.clear("ADD", "SQUARE", Location(pane_loc, innerloc), Location(pane_loc, innerbound))
        
        #We need to clear out an opening
        opening = (self.center[0], loc[1]-1) #Top middle
        
        self.path = Region()
        self.path("ADD", "LINE", Location(pane_loc, self.center), Location(pane_loc, opening), 2)
        self.boundary("SUB", "LINE", Location(pane_loc, self.center), Location(pane_loc, opening), 2)
        
        self.add_npc()
        
    def add_npc(self):
        # tolerance = 1
        # lvl = 1
        # person = TheoryCraft.getMonster(level=lvl, tolerance=tolerance)
        # person.location = Location(self.location.pane, self.center)
        # person.ai.add("WANDER", person.ai.wander, person.movementSpeed, pid=id(person), region=self.clear, move_chance=1.0 / (person.movementSpeed))
        # self.npcs[id(person)] = person
        pass

    
class Shop(Building):
    pass
    
class House(Building):
    pass
    
class Garden(Building):
    pass
    
class Respec(Building):
    pass
    
class Dungeon(Building):
    pass