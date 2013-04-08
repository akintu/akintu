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

class Township(object):
    def __init__(self, seed, township_loc, country_loc):
        self.seed = seed + str(country_loc) + str(township_loc)
        self.loc = (country_loc, township_loc)
        self.stampsLoaded = False
        self.town = None
        self.dungeons = []
        
        assert township_loc[0] < TOWNSHIP_X or \
                township_loc[1] < TOWNSHIP_Y, \
                str(township_loc) + " is outside of " + str((TOWNSHIP_X, TOWNSHIP_Y))

        self.topLeft = Township.getTownshipTopLeftPane(country_loc, township_loc)
        self.center = ((self.topLeft[0] + TOWNSHIP_X/2), (self.topLeft[1]+TOWNSHIP_Y/2))

        self.tile_width = (PANE_X-1) * TOWNSHIP_X
        self.tile_height = (PANE_Y-1) * TOWNSHIP_Y

        self.bounding_rect = pygame.Rect(0, 0, self.tile_width, self.tile_height)
        self.rect_list = []

    def addTown(self):
        random.seed(self.seed + "TOWN")
        #PICK OUR TOWN'S LOCATION
        country_loc, township_loc = self.loc
        if country_loc == (0, 0) and township_loc == (COUNTRY_X/2, COUNTRY_Y/2):
            self.town = self.center
        else:
            #we do a smaller box so town isn't on edge of township
            #if a Township is 5x5 panes, the town will be placed
            #in a 3x3 box inset.
            self.town = (random.randrange(1, TOWNSHIP_X-1)+self.topLeft[0], \
                            random.randrange(1, TOWNSHIP_Y-1)+self.topLeft[1])

    def addDungeons(self, number=2):
        random.seed(self.seed + "DUNGEON")
        #PICK OUR TOWN'S LOCATION
        for i in range(number):
            dungeon_loc = (random.randrange(0, TOWNSHIP_X) + self.topLeft[0], \
                            random.randrange(0, TOWNSHIP_Y) + self.topLeft[1])
            while dungeon_loc == self.town or dungeon_loc in self.dungeons:
                dungeon_loc = (random.randrange(0, TOWNSHIP_X) + self.topLeft[0], \
                                random.randrange(0, TOWNSHIP_Y) + self.topLeft[1])
            self.dungeons.append(dungeon_loc)

    def loadStamps(self):
        if self.stampsLoaded:
            print "Township.loadStamps has already been called"
            return
        self.stampsLoaded = True
        print "loadStamps not implemented yet"

    def getPaneRegion(self, pane):
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
    t.addTown()
    t.addDungeons(5)
    
    print "TOWN LOCATION: " + str(t.town)
    print "  DUNGEON LOCATIONS: " + str(t.dungeons)