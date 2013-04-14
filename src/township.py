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
        self.town_loc = None
        
        assert township_loc[0] < TOWNSHIP_X and \
                township_loc[1] < TOWNSHIP_Y, \
                str(township_loc) + " is outside of " + str((TOWNSHIP_X, TOWNSHIP_Y))

        self.topLeft = Township.getTownshipTopLeftPane(country_loc, township_loc)
        self.center = ((self.topLeft[0] + TOWNSHIP_X/2), (self.topLeft[1]+TOWNSHIP_Y/2))

        self.width_tiles = (PANE_X-1) * TOWNSHIP_X
        self.height_tiles = (PANE_Y-1) * TOWNSHIP_Y

        self.bounding_rect = pygame.Rect(0, 0, self.width_tiles, self.height_tiles)
        self.stamp_array = [x[:] for x in [[" "]*self.width_tiles]*self.height_tiles]

        self.rect_list = []

    def loadStamps(self, dungeons=5, coverage=.7, monsters=1.5, treasure=1.5):
        
        if not self.stampsLoaded:
            self.addTown()
            self.addDungeons(dungeons)
            self.addLandscape(coverage)
            self.addMonsters(monsters)
            self.addTreasure(treasure)
            self._splitStampArray()
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
        #Account for padding when we place the town rectangle
        self.town_rect = pygame.Rect(town_x*(PANE_X-1)-1, town_y*(PANE_Y-1)-1, x, y)
        assert self.bounding_rect.contains(self.town_rect), "Bounding Rectangle doesn't contain the town"
        self._placeTownStamps()

    def _placeTownStamps(self):
        stamps_rect = []
        stamps = dict()
        for key in [Stamp.SHOP, Stamp.RESPEC, Stamp.HOUSE, Stamp.GARDEN, Stamp.HOUSE, Stamp.GARDEN, Stamp.HOUSE]:
            stamp_dict = Stamp.getStamps(key)
            size = random.choice(list(stamp_dict.keys()))
            stamp = random.choice(stamp_dict[size])
            self._placeStamp(stamp, threshhold=100, pane=self.town_loc)
        self.rect_list.append(self.town_rect)

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
            self._placeDungeonStamp(dungeon_loc)

    def _placeDungeonStamp(self, dungeon_pane):
        self.dungeons.append(dungeon_pane)
        #Choose a stamp from our dungeons
        stamp_dict = Stamp.getStamps(Stamp.DUNGEON)
        size = random.choice(list(stamp_dict.keys()))
        stamp = random.choice(stamp_dict[size])
        self._placeStamp(stamp, threshhold=100, pane=dungeon_pane)

    def addLandscape(self, coverage):
        random.seed(self.seed + "LANDSCAPE")
        stamp_dict = Stamp.getStamps(Stamp.LANDSCAPE)
        i = 0
        threshhold = 1000

        # Add Landscape Stamps Until Coverage Is Reached
        while coverage > self.areaCoverage():
            if i >= threshhold:
                break
            i += 1
            self._addLandscapeStamp(stamp_dict)
        # print "Reached  " + str(i) + " restarts"
        # print "Total of " + str(len(self.rect_list)) + " rectangles"
        # print "Achieved " + str(self.areaCoverage()*100) + "% Coverage"

    def _addLandscapeStamp(self, stamp_dict):
        # Choose a Stamp
        size = random.choice(list(stamp_dict.keys()))
        stamp = random.choice(stamp_dict[size])
        self._placeStamp(stamp, threshhold=100)

    def addMonsters(self, monster):
        for i in range(int(monster*TOWNSHIP_X*TOWNSHIP_Y)):
            self._placeStamp(Stamp((1, 1), "m"))

    def addTreasure(self, treasure):
        for i in range(int(treasure*TOWNSHIP_X*TOWNSHIP_Y)):
            self._placeStamp(Stamp((1, 1), "$"))

    def _placeStamp(self, stamp, threshhold=100, pane=None):
        size = stamp.size
        if pane:
            bound_x, bound_y = (PANE_X-1), (PANE_Y-1)
        else:
            bound_x, bound_y = (self.bounding_rect.width-1), (self.bounding_rect.height-1)
        # Pick some threshhold to prevent an infinite loop
        i = 0
        while i < threshhold:
        
            # Choose a point on our bounding rect that will fit our stamp
            loc_x = random.randrange(1, bound_x-size[0])
            loc_y = random.randrange(1, bound_y-size[1])

            if pane:
                # Offset our point with the pane
                location = Location(pane, (loc_x, loc_y))
                loc_x, loc_y = self._getAbsoluteLocation(location)
            else:
                location = (loc_x, loc_y)

            candidate = pygame.Rect(loc_x-1, loc_y-1, size[0]+1, size[1]+1)
            if candidate.collidelist(self.rect_list) == -1:
                self.rect_list.append(candidate)
                self._joinStamps(location, stamp)
                return
            i += 1

    def _joinStamps(self, loc, stamp):
        if isinstance(loc, Location):
            loc = self._getAbsoluteLocation(loc)
        width = stamp.width
        height = stamp.height

        #Replace all "+" with an obstacle other than water
        obst_key = "water"
        while obst_key == "water":
            obst_key = random.choice(sorted(OBSTACLES))
        char = Stamp.obst_dict[obst_key] if obst_key in Stamp.obst_dict or obst_key == "water" else "+"

        i = 0
        for y in range(loc[1], loc[1]+height):
            # Get our start/end points of the stamp string
            start = i*width
            end = start+width
            string = stamp.data[start:end]
            j = 0
            for x in range(loc[0], loc[0]+width):
                # Replace character in stamp_array with character from string
                self.stamp_array[y][x] = string[j].replace("+", char)
                j += 1
            i += 1

    def _splitStampArray(self):
        # Duplicate *Pane* edges in the array
        # VERTICAL EDGES
        for y in range(len(self.stamp_array)):
            for i in range(TOWNSHIP_X-1):
                x = (i+1)*(PANE_X-1) + i
                self.stamp_array[y].insert(x, self.stamp_array[y][x])

        # HORIZONTAL EDGES
        # Just duplicate and insert the entire row
        for i in range(TOWNSHIP_Y-1):
            y = (i+1)*(PANE_Y-1) + i
            self.stamp_array.insert(y, self.stamp_array[y])

        # Split into pane sized chunks and load into self.stamps
        #[x[:] for x in [[" "]*self.height_tiles]*self.width_tiles]
        for j in range(TOWNSHIP_Y):
            for i in range(TOWNSHIP_X):
                x = i*PANE_X
                y = j*PANE_Y
                chunk = [list[x:x+PANE_X] for list in self.stamp_array[y:y+PANE_Y]]
                pane = (self.topLeft[0]+i, self.topLeft[1]+j)
                # Convert chunk into string for Stamp
                stamp_string = ""
                for line in chunk:
                    stamp_string += (''.join(line) + " "*PANE_X)[:PANE_X]
                stamp_string += (" "*PANE_X)[:PANE_X]
                stamps = dict()
                self.stamps[pane] = {Location(pane, (0, 0)):Stamp((PANE_X, PANE_Y), stamp_string)}
                
    def _getAbsoluteLocation(self, location):
        x = location.pane[0] - self.topLeft[0]
        y = location.pane[1] - self.topLeft[1]
        rect_x, rect_y = (x*(PANE_X-1) + location.tile[0], y*(PANE_Y-1) + location.tile[1])
        return (rect_x, rect_y)

    def areaCoverage(self):
        area_placed = 0.0
        total_area = (self.bounding_rect.width)*(self.bounding_rect.height)
        for rect in self.rect_list:
            area_placed += (rect.width)*(rect.height)
        return area_placed/total_area

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
    # print t.stamp_array
    
    # print "TOWN LOCATION: " + str(t.town_loc)
    # print "  DUNGEON LOCATIONS: " + str(t.dungeons)
    # print "  STAMPS: " + str(t.stamps.keys())
    # print str(t.stamps[(2, -2)])