import random
import pygame
from const import *
from region import *
from pane import *
from location import Location

class Township(object):
    '''
    TOWNSHIP: 
        Contains a set number of panes with the size
        defined in const.py (TOWNSHIP_X, TOWNSHIP_Y)
        Each territory contains 1 Town (Pane) object.
        This class handles the placement of "Stamps" 
        in the world. Everything is added to a 2-D
        list data structure, then split up into pane
        sized stamps. Country objects manage the creation
        and querying of this Township.
    '''
    def __init__(self, seed, township_loc, country_loc):
        self.seed = seed + str(country_loc) + str(township_loc)
        self.loc = (country_loc, township_loc)
        self.stampsLoaded = False
        self.dungeons = []
        self.boss = []
        self.stamps = dict()
        self.town_loc = None
        self.spawn_loc = None
        
        assert township_loc[0] < TOWNSHIP_X and \
                township_loc[1] < TOWNSHIP_Y, \
                str(township_loc) + " is outside of " + str((TOWNSHIP_X, TOWNSHIP_Y))

        # This is the top left Pane location in the world.
        self.topLeft = Township.getTownshipTopLeftPane(country_loc, township_loc)
        self.center = ((self.topLeft[0] + TOWNSHIP_X/2), (self.topLeft[1]+TOWNSHIP_Y/2))

        # Need the width and height of each pane to be one less than
        # the original height. This allows for object replication on
        # the edges.
        self.width_tiles = (PANE_X-1) * TOWNSHIP_X
        self.height_tiles = (PANE_Y-1) * TOWNSHIP_Y

        # Contains the bounds of this township. All rectangles will 
        # be added to this bounding rectangle. Used for collision
        # detection when placing stamps.
        self.bounding_rect = pygame.Rect(0, 0, self.width_tiles, self.height_tiles)
        self.stamp_array = [x[:] for x in [[" "]*self.width_tiles]*self.height_tiles]

        self.rect_list = []

    def loadStamps(self, dungeons=5, coverage=.7, monsters=1.5, treasure=0.5):
        '''
        This method must be explicitly called after the creation of the 
        Township object. The optional parameters can then be manipulated
        directly for variation of the world. Should only be called once.
        '''
        if not self.stampsLoaded:
            self.addTown()
            #self.addDungeons(dungeons) #To be added when dungeons are functional
            self.addBoss()
            self.addLandscape(coverage)
            self.addMonsters(monsters)
            self.addTreasure(treasure)
            self._splitStampArray()
            self.stampsLoaded = True
        else:
            print "Township.loadStamps has already been called"

    def addTown(self):
        '''
        One town is added to each Township. First we block out that area and
        add that rectangle to the bounding rectangle, then we add the individual
        stamps to the town to give it variety.
        '''
        random.seed(self.seed + "TOWN")
        #PICK OUR TOWN'S LOCATION
        country_loc, township_loc = self.loc
        #PANE (0,0) is always a town. This is where we start.
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
        self._placeTownStamps()

    def _placeTownStamps(self):
        '''
        Always add at least a shop to the town, it is the first stamp to be placed.
        '''
        stamps_rect = []
        stamps = dict()
        for key in [Stamp.SHOP, Stamp.RESPEC, Stamp.GARDEN, Stamp.GARDEN, Stamp.SHOP, Stamp.GARDEN, Stamp.HOUSE]:
            stamp_dict = Stamp.getStamps(key)
            size = random.choice(list(stamp_dict.keys()))
            stamp = random.choice(stamp_dict[size])
            loc = self._placeStamp(stamp, threshhold=100, pane=self.town_loc)
        self.rect_list.append(self.town_rect)

    def addBoss(self, number=1):
        '''
        Each Township can have a boss, but this can be explicitly 
        manipulated to spread them out.
        '''
        random.seed(self.seed + "BOSS")
        #PICK OUR PANE TO PLACE A BOSS
        for i in range(number):
            stamps = dict()
            boss_loc = (random.randrange(0, TOWNSHIP_X) + self.topLeft[0], \
                            random.randrange(0, TOWNSHIP_Y) + self.topLeft[1])
            #make sure it isn't in a town or an existing dungeon pane
            while boss_loc == self.town_loc or boss_loc in self.boss:
                boss_loc = (random.randrange(0, TOWNSHIP_X) + self.topLeft[0], \
                                random.randrange(0, TOWNSHIP_Y) + self.topLeft[1])
            self._placeBossStamp(boss_loc)

    def _placeBossStamp(self, boss_pane):
        '''
        Loads a boss stamp from file.
        '''
        self.boss.append(boss_pane)
        #Choose a stamp from our dungeons
        stamp_dict = Stamp.getStamps(Stamp.BOSS)
        size = random.choice(list(stamp_dict.keys()))
        stamp = random.choice(stamp_dict[size])
        self._placeStamp(stamp, threshhold=100, pane=boss_pane)

    def addDungeons(self, number):
        '''
        Adds dungeons to the world.
        '''
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
        '''
        Handles the placement of dungeon stamps
        '''
        self.dungeons.append(dungeon_pane)
        #Choose a stamp from our dungeons
        stamp_dict = Stamp.getStamps(Stamp.DUNGEON)
        size = random.choice(list(stamp_dict.keys()))
        stamp = random.choice(stamp_dict[size])
        self._placeStamp(stamp, threshhold=100, pane=dungeon_pane)

    def addLandscape(self, coverage):
        '''
        Adds variety to the world.
        '''
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

    def _addLandscapeStamp(self, stamp_dict):
        '''
        Handles adding landscape stamps to the world.
        '''
        # Choose a Stamp
        size = random.choice(list(stamp_dict.keys()))
        stamp = random.choice(stamp_dict[size])
        self._placeStamp(stamp, threshhold=100)

    def addMonsters(self, monster):
        '''
        Should be called after town, boss, and landscape
        stamps have already been placed.
        '''
        for i in range(int(monster*TOWNSHIP_X*TOWNSHIP_Y)):
            self._placeStamp(Stamp((1, 1), "m"))

    def addTreasure(self, treasure):
        '''
        Like addMonsters, should be called after the other
        stamps have been placed.
        '''
        for i in range(int(treasure*TOWNSHIP_X*TOWNSHIP_Y)):
            self._placeStamp(Stamp((1, 1), "$"))

    def _placeStamp(self, stamp, threshhold=100, pane=None):
        '''
        Generic method used to place a stamp in the world. Threshhold
        parameter can be manipulated to shorten the load time vs. 
        try new placement locations. As we add more stamps, finding 
        an open location that will fit the stamp gets harder. We loop
        through a list of rectangles already added to the Township to 
        do this check, rather than the Region class (much faster).
        '''
        size = stamp.size
        if pane:
            bound_x, bound_y = (PANE_X-1), (PANE_Y-1)
        else:
            bound_x, bound_y = (self.bounding_rect.width-1), (self.bounding_rect.height-1)
        # Check threshhold to prevent an infinite loop
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
                return location
            i += 1

    def _joinStamps(self, loc, stamp):
        '''
        Once we've placed a stamp, this is called to add it to the
        "superstamp". e.g. the 2-D array that represents the entire
        township. When we put it into the array, we check that a 
        generic 'object' is replaced with one we choose at random
        with the caveat that it is NOT water. Some stamps just look
        wierd with water.
        '''
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
        '''
        Once all stamps have been placed, this method is used to replicate
        objects located on the edge boundaries of where a pane would be. 
        It then splits the "superstamp" into pane sized chunks and loads
        them into the self.stamps dictionary with the location of the pane
        it represents as the key. This means that every pane will have a 
        single pane-sized stamp that it will load.
        '''
        # Duplicate *Pane* edges in the array
        # VERTICAL EDGES
        for y in range(len(self.stamp_array)):
            for i in range(TOWNSHIP_X-1):
                x = (i+1)*(PANE_X-1) + i
                char = self.stamp_array[y][x]
                char = " " if char == 'm' else char
                self.stamp_array[y].insert(x, char)

        # HORIZONTAL EDGES
        # Just duplicate and insert the entire row
        for i in range(TOWNSHIP_Y-1):
            y = (i+1)*(PANE_Y-1) + i
            line = self.stamp_array[y]
            line = [x.replace('m', " ") for x in line]
            self.stamp_array.insert(y, line)

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
        '''
        When we are dealing with the 2-d array "superstamp" this
        method allows us to get the index into that array given a 
        specific location object.  Since a township object places
        (0,0) as the center pane, we must offset it by the top left
        pane tuple. e.g. for a 5x5 township object, if you were
        trying to get the index of pane (0, 0), you would subtract
        the top-left pane (-2, -2) from (0, 0) giving (2, 2). We then
        multiply those by the number of tiles in a pane (-1 to account
        for a smaller sized pane for edge duplication) then add to it
        the tile portion of the Location object.
        '''
        x = location.pane[0] - self.topLeft[0]
        y = location.pane[1] - self.topLeft[1]
        rect_x, rect_y = (x*(PANE_X-1) + location.tile[0], y*(PANE_Y-1) + location.tile[1])
        return (rect_x, rect_y)

    def areaCoverage(self):
        '''
        Used to determine the amount of stamp coverage in this township.
        Returns a decimal percentage.
        '''
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
