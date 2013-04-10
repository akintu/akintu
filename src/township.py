'''
TOWNSHIP: 
    Contains a set number of panes with the size
    defined in const.py (TOWNSHIP_X, TOWNSHIP_Y)
    Each territory contains 1 Town (Pane) object
    and will have at least 1 dungeon
'''

import random
import pygame
from const import *
from region import *
from pane import *
from location import Location

class Township(object):
    def __init__(self, seed, township_loc, country_loc):
        self.seed = seed + str(country_loc) + str(township_loc)
        self.loc = (country_loc, township_loc)
        self.stampsLoaded = False
        self.dungeons = []
        self.stamps = dict()
        
        assert township_loc[0] < TOWNSHIP_X and \
                township_loc[1] < TOWNSHIP_Y, \
                str(township_loc) + " is outside of " + str((TOWNSHIP_X, TOWNSHIP_Y))

        self.topLeft = Township.getTownshipTopLeftPane(country_loc, township_loc)
        self.center = ((self.topLeft[0] + TOWNSHIP_X/2), (self.topLeft[1]+TOWNSHIP_Y/2))

        self.width_tiles = (PANE_X-1) * TOWNSHIP_X
        self.height_tiles = (PANE_Y-1) * TOWNSHIP_Y

        self.bounding_rect = pygame.Rect(0, 0, self.width_tiles, self.height_tiles)
        self.rect_list = []

    def loadStamps(self, dungeons=5, coverage=.5):
        if not self.stampsLoaded:
            self.addTown()
            self.addDungeons(dungeons)
            self.addLandscape(coverage)
            self.stampsLoaded = True
        else:
            print "Township.loadStamps has already been called"

    def addTown(self):
        random.seed(self.seed + "TOWN")
        #PICK OUR TOWN'S LOCATION
        country_loc, township_loc = self.loc
        #PANE (0,0) is always a town
        if country_loc == (0, 0) and township_loc == (COUNTRY_X/2, COUNTRY_Y/2):
            town_x = town_y = 2
            self.town_loc = self.center
        else:
            #we do a smaller box so town isn't on edge of township
            #if a Township is 5x5 panes, the town will be placed
            #in a 3x3 box inset.
            town_x = random.randrange(1, TOWNSHIP_X-1)
            town_y = random.randrange(1, TOWNSHIP_Y-1)
            self.town_loc = (town_x+self.topLeft[0], town_y+self.topLeft[1])
        #Pad the town rect (to prevent stamps from creeping up on it)
        x = town_x + PANE_X + 2
        y = town_y + PANE_Y + 2
        #Account for padding when we place the rect
        self.town_rect = pygame.Rect(town_x*(PANE_X-1)-1, town_y*(PANE_Y-1)-1, x, y)
        assert self.bounding_rect.contains(self.town_rect), "Bounding Rectangle doesn't contain the town"
        self.rect_list.append(self.town_rect)
        self._placeTownStamps()

    def _placeTownStamps(self):
        stamps_rect = []
        stamps = dict()
        for key in [Stamp.SHOP, Stamp.RESPEC, Stamp.HOUSE, Stamp.GARDEN, Stamp.HOUSE, Stamp.GARDEN, Stamp.HOUSE]:
            stamp_dict = Stamp.getStamps(key)
            size = random.choice(list(stamp_dict.keys()))
            stamp = random.choice(stamp_dict[size])

            #Pick some threshhold to prevent an infinite loop
            i = 0
            threshhold = 100
            while i < threshhold:
                #Choose a point 
                loc_x = random.randrange(1, (PANE_X-1)-size[0])
                loc_y = random.randrange(1, (PANE_Y-1)-size[1])

                #Check if the rectangle will collide with any others
                candidate = pygame.Rect(loc_x, loc_y, size[0]+1, size[1]+1)
                if candidate.collidelist(stamps_rect) == -1:
                    stamps_rect.append(candidate)
                    stamps[Location(self.town_loc, (loc_x, loc_y))] = stamp
                    break
                i += 1
        self.stamps[self.town_loc] = stamps

    def addDungeons(self, number):
        random.seed(self.seed + "DUNGEON")
        
        #PICK OUR PANE TO PLACE A DUNGEON
        for i in range(number):
            stamps = dict()
            dungeon_loc = (random.randrange(0, TOWNSHIP_X) + self.topLeft[0], \
                            random.randrange(0, TOWNSHIP_Y) + self.topLeft[1])
            #make sure it isn't in a town or an existing dungeon pane
            while dungeon_loc == self.town_loc or dungeon_loc in self.dungeons:
                dungeon_loc = (random.randrange(0, TOWNSHIP_X) + self.topLeft[0], \
                                random.randrange(0, TOWNSHIP_Y) + self.topLeft[1])
            location, stamp = self._placeDungeonStamp(dungeon_loc)
            stamps[location] = stamp
            self.stamps[dungeon_loc] = stamps

    def _placeDungeonStamp(self, dungeon_pane):
        self.dungeons.append(dungeon_pane)
        #Choose a stamp from our dungeons
        stamp_dict = Stamp.getStamps(Stamp.DUNGEON)
        size = random.choice(list(stamp_dict.keys()))
        stamp = random.choice(stamp_dict[size])

        #Pick some threshhold to prevent an infinite loop
        i = 0
        threshhold = 100
        while i < threshhold:
        
            #Choose a point 
            loc_x = random.randrange(1, (PANE_X-1)-size[0])
            loc_y = random.randrange(1, (PANE_Y-1)-size[1])

            candidate = pygame.Rect(loc_x*(PANE_X-1)-1, loc_y*(PANE_Y-1)-1, size[0]+1, size[1]+1)
            if candidate.collidelist(self.rect_list) == -1:
                    self.rect_list.append(candidate)
                    self.stamps[Location(self.town_loc, (loc_x, loc_y))] = stamp
                    location = Location(dungeon_pane, (loc_x, loc_y))
                    break
        return (location, stamp)#self.stamps[location] = stamp

    def addLandscape(self, coverage):
        pass


    @staticmethod
    def getTownshipLocation(pane):
        '''
        The x,y coordinate of this township. i.e. if a township is
        a 5x5 group of panes, pane (0, 0) is in the center.

        For Example:

            TOWNSHIP (2,2)          TOWNSHIP (3,2)          TOWNSHIP (4,2)
        (-2,-2) # (0,-2)#   #    (3,-2) #   #   #   #    (8,-2) #   #   #   #
            #   #   #   #   #       #   #   #   #   #       #   #   #   #   #
            #   # (0,0) #   #       #   # (5,0) #   #       #   #(10,0) #   #
            #   #   #   #   #       #   #   #   #   #       #   #   #   #   #
            #   #   #   #   #       #   #   #   #   #       #   #   #   #   #

        '''

        loc_x = ((pane[0] + TOWNSHIP_X/2)/TOWNSHIP_X) + TOWNSHIP_X/2
        loc_y = ((pane[1] + TOWNSHIP_Y/2)/TOWNSHIP_Y) + TOWNSHIP_Y/2

        country_x = loc_x/COUNTRY_X
        country_y = loc_y/COUNTRY_Y

        loc_x %= COUNTRY_X
        loc_y %= COUNTRY_Y

        return ((country_x, country_y),(loc_x, loc_y))

    @staticmethod
    def getTownshipTopLeftPane(country_loc, township_loc):
        '''
        Given a country location tuple and a township location tuple
        returns the top left pane of that township
        
        For Example:
            township_loc((0,0))
        '''
        cx, cy = country_loc
        tx, ty = township_loc

        #Justify center
        tx -= COUNTRY_X/2
        ty -= COUNTRY_X/2

        loc_x = (tx+TOWNSHIP_X*cx)*TOWNSHIP_X - TOWNSHIP_X/2
        loc_y = (ty+TOWNSHIP_Y*cy)*TOWNSHIP_Y - TOWNSHIP_Y/2

        return (loc_x, loc_y)

if __name__=="__main__":
    t = Township("SOME_SEED", township_loc=(2,2), country_loc=(0,0))
    t.loadStamps()
    
    print "TOWN LOCATION: " + str(t.town_loc)
    print "  DUNGEON LOCATIONS: " + str(t.dungeons)
    print "  STAMPS: " + str(t.stamps.keys())
    print str(t.stamps[(2, -2)])