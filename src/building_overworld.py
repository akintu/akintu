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
from sprites import*
from entity import*
from portal import Portal
from theorycraft import TheoryCraft

class BuildingOverworld(object):
    
    def __init__(self, boundary_type, bounds, pane_loc, size=None, location=None):
        '''
        bounds: (min_x, max_x, min_y, max_y)
        '''
        
        self.path_sheet = Sprites.get_sheet(PATH_KEY)
        self.entities = dict()
        
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
        #self.boundary("SUB", "LINE", Location(pane_loc, self.center), Location(pane_loc, opening), 2)
        
        self.add_npc()
        
    def add_npc(self):
        # tolerance = 1
        # lvl = 1
        # person = TheoryCraft.getMonster(level=lvl, tolerance=tolerance)
        # person.location = Location(self.location.pane, self.center)
        # person.ai.add("WANDER", person.ai.wander, person.movementSpeed, pid=id(person), region=self.clear, move_chance=1.0 / (person.movementSpeed))
        # self.npcs[id(person)] = person
        pass

    
class ShopOverworld(BuildingOverworld):
    pass
    
class HouseOverworld(BuildingOverworld):
    def __init__(self, location):
        '''
        House has size (4, 2)
        Will use outdoor paths from path_sheet (set in building)
            Row 0: Outdoor Rocks
            Row 1: Outdoor cement/Brick
            Row 2: Tile or specialty (in or out)
            Row 3: Indoor Wood/Carpet
        '''
        #self.entities = dict() #IN SUPER CLASS BUILDING
        
        super(HouseOverworld, self).__init__(boundary_type="tree", bounds=None, pane_loc=location.pane, size=(7, 5), location=location)
        house_sheet = Sprites.get_sheet(HOUSE_KEY)
        
        
        house_loc = (location.tile[0], location.tile[1])
        
        for x in range(4):
            for y in range(2):
                loc = (house_loc[0]+x, house_loc[1]+y)
                if x == y and x == 1:
                    self.door = loc
                    passable = True
                    self.entities[loc] = Portal(Location((0, 0), (PANE_X/2, PANE_Y-3), z=-1, direction=8), portal_type=Portal.HOUSE, location=loc, image=house_sheet.getimage((x, y)), passable=passable)
                else:
                    passable = False
                    self.entities[loc] = Entity(location=loc, image=house_sheet.getimage((x, y)), passable=passable)
            y = 0
            
        self.opening = (self.door[0], self.door[1]+2)
        self.path = Region()
        self.path("ADD", "LINE", Location(location.pane, (self.door[0], self.door[1]+1)), Location(location.pane, self.opening), 1)
        self.boundary("SUB", "LINE", Location(location.pane, (self.door[0], self.door[1]+1)), Location(location.pane, self.opening), 1)
        
        #Choose the type of path that we want, probably from rows 0 to 2 (from self.path_sheet)
        row = random.randrange(0, 3)
        col = random.randrange(0, 4)
        path_image = self.path_sheet.getimage((col, row))
        for loc in self.path:
            if loc.pane == location.pane:
                self.entities[loc.tile] = Entity(location=loc.tile, image=path_image, passable=True)
                #TODO: Add outer edge entities here (to give edge to path)
    
    def add_npc(self, information=None):
        '''
        Add a random npc here that might talk to you
        '''
        # tolerance = 1
        # lvl = 1
        # person = TheoryCraft.getMonster(level=lvl, tolerance=tolerance)
        # person.location = Location(self.location.pane, self.center)
        # person.ai.add("WANDER", person.ai.wander, person.movementSpeed, pid=id(person), region=self.clear, move_chance=1.0 / (person.movementSpeed))
        # self.npcs[id(person)] = person
        pass

class GardenOverworld(BuildingOverworld):
    pass
    
class RespecOverworld(BuildingOverworld):
    pass
    
class DungeonOverworld(BuildingOverworld):
    '''
    Dungeon-hand has size (3, 4)
    '''
    def __init__(self, location):
        super(DungeonOverworld, self).__init__(boundary_type="shrub", bounds=None, pane_loc=location.pane, size=(6, 7), location=location)
        
        
        dungeon_sheet = Sprites.get_sheet(random.choice(list(DUNGEONS.keys())))

        house_loc = (location.tile[0], location.tile[1])
        
        for x in range(3):
            for y in range(4):
                loc = (house_loc[0]+x, house_loc[1]+y)
                if x == 1 and y == 3:   #Door opening
                    self.door = loc
                    passable = True
                    self.entities[loc] = Portal(Location((0, -3), (17, 10), z=-1, direction=8), portal_type=Portal.DUNGEON, location=loc, image=dungeon_sheet.getimage((x, y)), passable=passable)
                else:
                    passable = False
                    self.entities[loc] = Entity(location=loc, image=dungeon_sheet.getimage((x, y)), passable=passable)
            y = 0
            
        self.opening = (self.door[0], self.door[1])
        self.path = Region()
        # self.path("ADD", "LINE", Location(location.pane, (self.door[0], self.door[1]+1)), Location(location.pane, self.opening), 1)
        self.boundary("SUB", "LINE", Location(location.pane, (self.door[0], self.door[1]+1)), Location(location.pane, self.opening), 1)
        
        #Choose the type of path that we want, probably from rows 0 to 2 (from self.path_sheet)
        row = random.randrange(0, 3)
        col = random.randrange(0, 4)
        path_image = self.path_sheet.getimage((col, row))
        for loc in self.path:
            if loc.pane == location.pane:
                self.entities[loc.tile] = Entity(location=loc.tile, image=path_image, passable=True)
                #TODO: Add outer edge entities here (to give edge to path)
        
