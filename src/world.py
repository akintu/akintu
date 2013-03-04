'''
World generation tools and representation
'''

import os
import math
import random, time

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

    def __init__(self, world_state):
        self.seed = world_state[SEED_KEY]
        self.panes = dict()
        #TODO: Unbox/Open world_state in whatever form it is given
        self.world_state = world_state

    def get_pane(self, location, is_server=False):
        surrounding_locations = Location(location, None).get_surrounding_panes()
        for key, loc in surrounding_locations.iteritems():
            if not loc in self.panes:
                self.panes[loc] = Pane(self.seed, loc)

        #This is the pane we will return, current pane
        state = None
        if self.world_state:
            if location in self.world_state:
                state = self.world_state[location]
        self.panes[location] = Pane(self.seed, location, load_entities=True, pane_state=state)
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

    def __init__(self, seed, location, load_entities=True, pane_state=None):
        self.seed = seed
        self.location = location
        self.pane_state = pane_state
        self.curr_state = dict()
        self.tiles = dict()
        self.objects = dict()
        self.person = {}
        self.background_key = Sprites.get_background(self.seed + str(self.location))

        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)] = Tile(None, True)
                if load_entities:
                    self.add_obstacle((i, j), RAND_ENTITIES)

        if load_entities:
            if self.pane_state:
                self.load_state(self.pane_state)
            else:
                self.load_monsters()
                #self.load_items()

    def __repr__(self):
        s = ""
        for j in range(PANE_Y):
            for i in range(PANE_X):
                if (i, j) in self.objects:
                    s += "X"
                else:
                    s += " "
            s += "|\n"
        return s

    def load_monsters(self, monsters=None):
        '''
        Parameters:
            monsters:   A list of monster tuples in the following format:
                        ("Name", "Level", "Location", "Region", "AI")
                        Where: 
                            Name and Level are strings
                            Location is the tile tuple (x, y)
                            Region and AI will be some sort of hash that their
                                respective classes can use to rehydrate them
        '''
    
        if monsters:
            for monster in monsters:
                person = TheoryCraft.getMonster(name=monster[0], level=monster[1])
                person.location = Location(self.location, monster[2])
                r = Region()#region=monster[3])
                #TODO: Rehydrate r with monsters[3]
                #TODO: Somehow rehydrate AI...
                #person.ai(monster[4])
                self.person[id(person)] = person
                assert False
        else:   #TODO: Make this better. We're creating monsters from scratch here
            random.seed(self.seed + str(self.location) + "load_monsters")
            for i in range(3):
                lvl = max(abs(self.location[0]), abs(self.location[1]))
                tolerance = 1
                if lvl == 0:
                    lvl = 1
                    tolerance = 0
                person = TheoryCraft.getMonster(level=lvl, tolerance=tolerance)#TODO, pass in random here
                person.location = Location(self.location, (random.randrange(PANE_X), random.randrange(PANE_Y)))
                r = Region()
                r("ADD", "CIRCLE", person.location, PANE_Y/4)
                #r.build("SUB", "CIRCLE", Location(self.location, CENTER), int(PANE_Y/6))
                person.ai.add("WANDER", person.ai.wander, person.movementSpeed, pid=id(person), region=r, move_chance=1.0 / (person.movementSpeed))
                self.person[id(person)] = person

    def load_items(self, items=None):
        '''
        Parameters:
            items:  A list of item tuples in the following format:
                    ("Name", "Location", ...)
                    
                    TODO: STILL UNIMPLEMENTED, need info on creating items from name...
        '''

        print "load_items() currently does nothing :)"
        if items:
            for item in items:
                #TODO: Do something with this item
                pass
        pass

    def load_images(self):
        self.images = Sprites.get_images_dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)].set_image(Sprites.get_background_tile(self.background_key, (i, j)))
        for tile, entity_key in self.objects.iteritems():
            obstacle = Sprites.get_object(entity_key, self.seed, self.location, tile)
            self.tiles[tile].entities.append(Entity(tile, image=obstacle))

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
        if not tile in self.tiles:
            self.tiles[tile] = Tile(None, True)
        if not entity_type:
            random.seed(str(self.seed) + str(self.location) + str(tile))
            if random.randrange(100) <= percentage*100:
                index = random.randrange(len(ENTITY_KEYS))
                self.objects[tile] = ENTITY_KEYS[index]
                self.tiles[tile].passable = False
        else:
            self.objects[tile] = entity_type
            self.tiles[tile].passable = False
        if tile in self.objects:
            return self.objects[tile]

    def add_region(self, location, size, percentage, entity_type=None):
        r = Region()
        r("ADD", "CIRCLE", location, size)
        entity_type = self.add_obstacle(location.tile, percentage, entity_type)
        if entity_type:
            for loc in r:
                if not loc in self.tiles:
                    self.tiles[loc] = Tile(None, True)
                    self.add_obstacle(loc.tile, 1, entity_type)

    def get_combat_pane(self, focus_tile, monster = None):
        return CombatPane(self, focus_tile, monster)

    def load_state(self, state):
        if state:
            #Get Monsters
            if MONSTER_KEY in state:
                self.load_monsters(monsters=state[MONSTER_KEY])
            #Get Items
            if ITEM_KEY in state:
                self.load_items(items=state[ITEM_KEY])
            #Get Anything Else
            pass

    def save_state(self, person_dict):
        '''
        Saves the current panes monsters and items to a dictionary.
        Returns a dictionary with the following attributes:
            {MONSTER_KEY: [(name, level, location, region, ai), (...)],
                ITEM_KEY: [(name, attributes, location, ...), (...)]}
        The server can then add this dictionary to its master dictionary using
        this pane's (x, y) coordinate as the key.
        '''
        
        save_dict = dict()
        monster_list = []
        item_list = []
        
        #Save Monsters.  
        #Using pane's person list which contains the keys to 
        #pull the people from supplied dictionary
        for id in self.person:
            if not id in person_dict:
                print "ID (" + str(id) + ") not found in person_dict."
                assert False
            monster = person_dict[id]
            monster_list.append((monster.name, monster.level, \
                monster.location, monster.region, monster.ai))
        save_dict[MONSTER_KEY] = monster_list
        
        #SAVE ITEMS
        #TODO: loop through tile entity lists to pull these items and 
        #add their representation to item_list.
        pass
        

class CombatPane(Pane):

    def __init__(self, pane, pane_focus, monster):
        '''
        A subpane of the current pane.  It will contain 10x6 of the original
        tiles which turn into 3x3 grids on the CombatPane.
        Dimensions are 30x18 (there will be a border around the pane)
        Member Variables:
            pane_focus:     a Location object with the current pane and the
                            tile of the monster of focus.  This is the location
                            from which we entered combat.  If this location is
                            far enough away from a border, sub pane will be centered
                            from here.

        '''
        super(CombatPane, self).__init__(pane.seed, pane.location, False)

        loc_x = pane_focus.tile[0]
        loc_y = pane_focus.tile[1]

        dx_min = min(loc_x - 5, 0)     #yields 0 if far enough away from edge,
        dy_min = min(loc_y - 3, 0)     #and negative if too close
        # print "dx_min, dy_min: " + str(dx_min) + ", " + str(dy_min)
        dx_max = max(loc_x - 26, 0)    #yields 0 if far enough away from edge,
        dy_max = max(loc_y - 14, 0)    #and positive if too close
        # print "dx_max, dy_max: " + str(dx_max) + ", " + str(dy_max)
        dx = dx_min + dx_max - 1
        dy = dy_min + dy_max - 1
        loc_x -= dx
        loc_y -= dy

        self.focus_location = Location(pane.location, (PANE_X/2 + dx*3, PANE_Y/2 + dy*3))
        fx = max(0, min(PANE_X - 1, self.focus_location.tile[0]))
        fy = max(0, min(PANE_Y - 1, self.focus_location.tile[1]))
        self.focus_location.tile = (fx, fy)

        i = 2
        for x in range(loc_x-4, loc_x+6):
            j = 2
            for y in range(loc_y-2, loc_y+4):
                # print "(" + str(x) + ", " + str(y) + ")"
                if (x,y) in pane.objects:
                    self.add_zoomed_obstacle((i, j), pane.objects[(x,y)])
                j+=3
            i+=3

        self.load_background_images()
        if monster:
            monsters = TheoryCraft.generateMonsterGroup(monster)
            self.place_monsters(monsters, self.focus_location)


    def place_monsters(self, monsters, start_location):
        loc = temp = start_location
        #print monsters
        for person in monsters:
            while not self.is_passable(loc) or not self.is_within_bounds(loc, 3):
                #Choose a new location
                #print str(loc) + " New Location"
                loc = self.rand_move_within_pane(loc, [1,9], [1,5], 3)
            #print str(loc) + " Passable Location"
            person.location = loc
            self.person[id(person)] = person
            temp = loc
            loc = self.rand_move_within_pane(loc, [1,9], [2,5], 3)


    def rand_move_within_pane(self, location, dir_range, dist_range, bounds):
        random.seed()
        while True:
            dir = random.randint(dir_range[0], dir_range[1])
            if dir == 5:
                #print "Cant move in direction 5"
                continue
            dist = random.randint(dist_range[0], dist_range[1])
            new_loc = location.move(dir, dist)
            if new_loc.pane != location.pane:
                #print "Off the pane"
                continue
            return new_loc


    def is_passable(self, location):
        for key, person in self.person.iteritems():
            if person.location == location:
                return False
        return super(CombatPane, self).is_tile_passable(location)


    def is_within_bounds(self, location, edge):
        #Outside of current pane
        if self.location != location.pane:
            return False
        return True


    def add_zoomed_obstacle(self, tile_center, entity_key):
        '''
        Zooms the given obstacle to a 3x3 obstacle and centers it on the given tile.
        '''

        entity_key += "_zoom"
        for di in range(0,3):
            for dj in range(0,3):
                tile = (tile_center[0]+(di-1), tile_center[1]+(dj-1))
                if not tile in self.tiles:
                    self.tiles[tile] = Tile(None, True)
                self.objects[tile] = entity_key
                self.tiles[tile].passable = False
                obstacle = Sprites.get_zoomed_image(entity_key, (di,dj))
                self.tiles[tile].entities.append(Entity(tile, image=obstacle))


    def load_background_images(self):
        self.images = Sprites.get_images_dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)].set_image(Sprites.get_background_tile(self.background_key, (i, j)))


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
    a = Pane((0,0), "SomeSeed", False)
    #a.get_combat_pane(Location((0,0), (4,10)))

