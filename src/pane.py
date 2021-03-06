
import random
import trap

from const import*
from sprites import*
from building_overworld import*
from entity import*
from treasurechest import*
from tile import Tile
from theorycraft import TheoryCraft
from state import State
from dice import *
from stamps import *
from fields import Fields
from path import Path

class Pane(object):
    '''
    Represents a single screen of the world

    Member Variables
        seed:           Game seed chosen by host
        location:       Usually a tuple object, but can also be a Location
        load_entities:  Boolean indicating the need to load this pane's consumables
        pane_state:     The dictionary of consumables if loading from file
    '''

    PaneCorners = {1:TILE_BOTTOM_LEFT, 3:TILE_BOTTOM_RIGHT, 7:TILE_TOP_LEFT, 9:TILE_TOP_RIGHT}
    PaneEdges = {2:TILES_BOTTOM, 4:TILES_LEFT, 6:TILES_RIGHT, 8:TILES_TOP}

    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        if isinstance(location, Location):
            self.location = location.pane
        else:
            self.location = location
        self.seed = seed
        self.is_server = is_server
        self.load_entities = load_entities
        self.pane_state = pane_state
        self.tiles = dict()
        self.objects = dict()
        self.person = {}
        self.fields = Fields()
        self.background_key = Sprites.get_background(self.seed + str(self.location))
        self.hostileTraps = []

        if not level:
            self.paneLevel = max(abs(self.location[0]), abs(self.location[1]))
        else:
            self.paneLevel = level

        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)] = Tile(None, True)

        if self.load_entities:
            if self.is_server:
                self.load_chests()
                self.load_monsters()
                #self.load_items()

    def __repr__(self):
        s = "\nPane " + str(self.location) + "\n"
        for j in range(PANE_Y):
            for i in range(PANE_X):
                if (i, j) in self.objects:
                    s += "X"
                else:
                    s += " "
            s += "|\n"
        return s

    def __del__(self):
        if not self.is_server:
            pass#print "Calling __del__ on client's Pane object at " + str(self.location)
        else:   #We are the server, save the pane's state to disk
            # "Calling __del__ on server's Pane object at " + str(self.location)
            self.save_state()

    def get_tile(self, location):
        if location in self.tiles:
            return self.tiles[location]
        else:
            print "Could not find tile at " + str(location) + " on pane " + str(self.location)

    def remove_entities(self, location):
        if location in self.tiles:
            self.tiles[location].remove_items()

    def add_entities(self, entities_dict):
        for loc, entity in entities_dict.iteritems():
            if not loc in self.tiles:
                self.tiles[loc] = Tile(None, True)
            self.tiles[loc].add_entity(entity)

    def load_monsters(self, monsters=None):
        '''
        Parameters:
            monsters:   A list of tuples with a monster dehydrated string and location object:
                [("dehydrated_string", Location()), ...]

        '''

        if monsters != None:
            for monster in monsters:
                person = TheoryCraft.rehydrateMonster(monster[0], save=True)
                person.location = monster[1]
                self.person[id(person)] = person
        else:   #TODO: Make this better. We're creating monsters from scratch here
            pass
            random.seed(self.seed + str(self.location) + "load_monsters")
            for i in range(0):
                self.add_monster()

    def add_monster(self, name=None, level=None, tolerance=None, location=None, region=None, ai=None):
        #Handle Default Objects
        if not level:
            level = self.paneLevel
        if not tolerance:
            if level == 0:
                tolerance = 0
                level = 1
            else:
                tolerance = 1
        if not location:
            location = Location(self.location, (random.randrange(PANE_X), random.randrange(PANE_Y)))

        ignore_max = True if level > 9 else False

        level = min(level, 9) if name != "Devil" else level
        # print ignore_max
        person = TheoryCraft.getMonster(level=level, name=name, tolerance=tolerance, ignoreMaxLevel=ignore_max)
        person.location = location
        if not region:
            region = Region()
            region("ADD", "CIRCLE", person.location, PANE_Y/4)
        if ai:
            print "add_monster(ai) not implemented"

        person.ai.add("wander", person.movementSpeed, pid=id(person), region=region, move_chance=1.0 / (person.movementSpeed))
        self.person[id(person)] = person

    def save_items(self):
        '''
        item_list = [(name, attributes, location, ...), (...)]
        '''

        item_list = []
        for tile_loc, tile in self.tiles.iteritems():
            for item in tile.get_items():
                item_list.append((item.name, item.attributes, tile_loc))
        return item_list

    def load_items(self, items=None):
        '''
        Parameters:
            items:  A list of item tuples in the following format:
                    ("Name", "Attributes", "tile_location", ...)

                    UNIMPLEMENTED, No items directly on the overworld
        '''

        print "load_items() currently does nothing :)"
        if items != None:
            for item in items:
                self.add_item(item[0], item[1], item[2])
        else:
            print "LOAD ITEMS HERE (Pane.load_items())"

    def add_item(self, name, attributes, location):
        self.tiles[location].add_item(Item(name, attributes))

    def get_chest_list(self):
        '''
        Returns a list of chests in the following format:
            [(type, level, location, ...), (...)]
        '''
        chest_list = []
        for tile_loc, tile in self.tiles.iteritems():
            chest = tile.get_chest()
            if chest:
                chest_list.append((chest.type, chest.treasureLevel, tile_loc))
        return chest_list

    def load_chests(self, chests=None):
        '''
        Parameters:
            chests:  A list of chest tuples in the following format:
                    [(type, level, location, ...), (...)]
        '''

        if chests != None:
            for chest in chests:
                self.add_chest(chest[0], chest[1], chest[2])
        else:
            #Adds a random Chest
            loc_list = []
            for i in range(3):
                loc_list.append((TreasureChest.CHEST_TYPE[random.randrange(len(TreasureChest.CHEST_TYPE))], \
                                (random.randrange(1, PANE_X-1), random.randrange(1, PANE_Y-1))))
            for type, loc in loc_list:
                self.add_chest(type, None, loc)

    def add_chest(self, chest_type=None, level=None, tile=None):
        if not chest_type:
            chest_type = TreasureChest.CHEST_TYPE[random.randrange(len(TreasureChest.CHEST_TYPE))]
        if not level:
            level = max(abs(self.location[0]), abs(self.location[1]))
            level = max(level, 1)
        if not tile:
            tile = (random.randrange(1, PANE_X-1), random.randrange(1, PANE_Y-1))
        self.tiles[tile].add_chest(TreasureChest(chest_type, level, tile))
        self.load_images(load_all=False)

    def load_images(self, load_all=True):
        self.images = Sprites.get_images_dict()
        if load_all:
            for i in range(PANE_X):
                for j in range(PANE_Y):
                    self.tiles[(i, j)].set_image(Sprites.get_background_tile(self.background_key, (i, j)))
        for tile, entity_key in self.objects.iteritems():
            passable = False
            image = None
            if entity_key in OBSTACLES:
                image = Sprites.get_obstacle(entity_key, self.seed, self.location, tile)
            elif entity_key in DUNGEON_OBSTACLES:
                image = Sprites.get_dungeon_obstacle(entity_key, self.seed, self.location, tile)
            elif entity_key in PATHS:
                image = Sprites.get_path(entity_key, self.seed, self.location, tile)
                passable = True
            elif entity_key == 'house':
                house = ShopOverworld(Location(self.location, tile))
                self.add_entities(house.entities)
                continue
            elif entity_key == 'shop':
                shop = ShopOverworld(Location(self.location, tile))
                self.add_entities(shop.entities)
                continue
            elif entity_key == 'dungeon':
                dungeon = DungeonOverworld(Location(self.location, tile))
                self.add_entities(dungeon.entities)
                continue
            elif entity_key == 'portal':
                portal = PortalOverworld(Location(self.location, tile))
                self.add_entities(portal.entities)
                continue
            if not image:
                print "Entity Key NOT FOUND: " + str(entity_key)
            self.tiles[tile].entities.append(Entity(tile, image=image, passable=passable))

    def is_tile_passable(self, location, check_entity_keys=False):
        return self.tiles[location.tile].is_passable(check_entity_keys)

    def add_obstacle(self, tile, percentage, entity_type=None):
        if not tile in self.tiles:
            self.tiles[tile] = Tile(None, True)
        if not entity_type:
            random.seed(str(self.seed) + str(self.location) + str(tile))
            if random.randrange(100) <= percentage*100:
                index = random.randrange(len(OBSTACLE_KEYS))
                self.objects[tile] = OBSTACLE_KEYS[index]
                self.tiles[tile].add_entity_key(self.objects[tile])
        else:
            self.objects[tile] = entity_type
            self.tiles[tile].add_entity_key(self.objects[tile])
        if tile in self.objects:
            return self.objects[tile]

    def remove_obstacles(self, tile):
        if tile in self.objects:
            del self.objects[tile]
        if tile in self.tiles:
            self.tiles[tile].clear_all_entities()

    def remove_chest(self, location):
        if isinstance(location, Location):
            loc = location.tile
        elif isinstance(location, tuple):
            loc = location
        self.tiles[loc].remove_chest()

    def get_treasure_chest(self, location):
        '''
        Loops through the surrounding tiles and returns the first chest it finds.
        Currently it looks for chests in front of the player as the first option
        but remaining checks are undefined.

        '''

        if location.pane != self.location:
            print "Tried to get chest from pane " + str(location.pane) + ","
            print "but requested it from " + str(self.location)
            print "pane.get_treasure_chest(self, location)"
            return (None, None)

        tiles = location.get_surrounding_tiles()

        #First attempt to get a chest in front of you
        facing = tiles[location.direction]
        if facing in self.tiles:
            chest = self.tiles[facing].get_chest()
            if chest:
                #print "Found chest in front of you on tile " + str(facing)
                return (chest, Location(self.location, facing))

        #If there was no chest, look on surrounding tiles
        for key, tile in tiles.iteritems():
            if tile in self.tiles:
                chest = self.tiles[tile].get_chest()
                if chest:
                    #print "Found chest on tile " + str(tile)
                    #self.tiles[tile].remove_chest()
                    return (chest, Location(self.location, tile))
        return (None, None)

    def get_item(self, location):
        '''

        '''

        if location.pane != self.location:
            print "Tried to get item from pane " + str(location.pane) + ","
            print "but requested it from " + str(self.location)
            print "pane.get_item(self, location)"
            return (None, None)

        tiles = location.get_surrounding_tiles()
        assert False, "pane.get_item(location) is not yet implemented"

    def get_item_list(self):
        pass

    def load_stamps(self, loc_stamp_dict, clear_region=True):
        for location, stamp in loc_stamp_dict.iteritems():
            if location.pane != self.location:
                print "Location.pane=" + str(location.pane)
                print "Self.location=" + str(self.location)
                return
            if not isinstance(location, Location):
                print "location not a Location " + str(location)
            location2 = location.move(6, stamp.width-1).move(2, stamp.height-1)

            if clear_region:
                clear = Region()
                clear("ADD", "SQUARE", location, location2)
                self.clear_region(clear)

            obst = random.choice(sorted(OBSTACLES))
            for loc, type in stamp.getEntityLocations(location).iteritems():
                #CONSUMABLES, ITEMS, AND MONSTERS (REMOVED AFTER USE OR DEATH)
                if type in [CHEST_KEY, MONSTER_KEY, ITEM_KEY, BOSS_KEY]:
                    if not self.pane_state and self.is_server:
                        if type == CHEST_KEY:
                            self.add_chest(tile=loc.tile)
                        if type == MONSTER_KEY and loc.pane == location.pane:
                                self.add_monster(location=loc)
                        if type == ITEM_KEY:
                            self.add_item(tile=loc.tile)
                        if type == BOSS_KEY:
                            self.add_monster(location=loc, name="Devil", level=20)
                    continue
                if type == 'obstacle':
                    type = obst
                #OBSTACLES AND PATHS
                if loc.pane == self.location and type != None:
                    self.add_obstacle(loc.tile, 1, entity_type=type)
            #Load the state
            if self.load_entities:
                if self.pane_state:
                    self.load_state(self.pane_state)

    def load_region(self, region, entity_type=None):
        if entity_type:
            for loc in region:
                if not loc in self.tiles:
                    self.tiles[loc] = Tile(None, True)
                if loc.pane == self.location:
                    self.add_obstacle(loc.tile, 1, entity_type)

    def clear_region(self, region):
        for loc in region:
            self.remove_obstacles(loc.tile)

    def get_combat_pane(self, focus_tile, monster = None, num_players=1):
        return CombatPane(self, focus_tile, monster, num_players)

    def get_inside(self, portal_location, portal_type):
        return Inside.getInside(portal_type)

    def save_state(self):
        '''
        Saves the current panes monsters and items to a dictionary.
        Calls State.save to the worlds dir using this pane's location.
        Returns a dictionary with the following attributes:
            {MONSTER_KEY: [(dehydrated_string, Location()), (...)],
                ITEM_KEY: [(name, attributes, location, ...), (...)]
                CHEST_KEY: [(type, level, location, ...)}
        The server can then add this dictionary to its master dictionary using
        this pane's (x, y) coordinate as the key.
        '''
        save_dict = self.get_state()
        State.save_pane(self.location, save_dict)


    def get_state(self):
        save_dict = dict()
        monster_list = []

        #Save Monsters.
        # print self.person
        for key, monster in self.person.iteritems():
            monster_list.append((monster.dehydrate(save=True), monster.location))
        save_dict[MONSTER_KEY] = monster_list

        #Save Items.
        #save_dict[ITEM_KEY] = self.save_items()

        #Save Chests.
        save_dict[CHEST_KEY] = self.get_chest_list()
        return save_dict

    def load_state(self, state):
        #print "Pane.load_state(state) " + str(state)
        if state:
            #Get Monsters
            if MONSTER_KEY in state:
                self.load_monsters(monsters=state[MONSTER_KEY])
            #Get Items
            if ITEM_KEY in state:
                self.load_items(items=state[ITEM_KEY])
            #Get Chests
            if CHEST_KEY in state:
                chests = state[CHEST_KEY]
                #print "Loading chests from state: " + str(chests)
                self.load_chests(chests=state[CHEST_KEY])

    def addTrap(self, location, trap):
        loc = location.tile
        if not loc in self.tiles:
            self.tiles[loc] = Tile(None, True)
        self.tiles[loc].addTrap(trap)
        if trap.team == "Monsters":
            self.hostileTraps.append(trap)
            # Only used for checking for traps.  We don't even need to bother
            # removing anything from this list.

    def removeTrap(self, location, hostile=False):
        loc = location.tile
        if loc in self.tiles:
            self.tiles[loc].removeTrap()

    def get_trigger_entities(self, location):
        if isinstance(location, Location):
            loc = location.tile
        else:
            loc = location
        return self.tiles[loc].get_trigger_entities()

    def getTileContents(self, location, monsters=None):
        '''
        Method used to determine if a trap can be placed here
        Member Variables:
            location:   a Location object to check
            monsters:   a dictionary of Monster objects to check against
        '''

        loc = location.tile

        if monsters:
            for id in self.persons:
                if id in monsters:
                    if loc == monsters[id].location.tile:
                        return "Monster"

        if not loc in self.tiles:
            self.tiles[loc] = Tile(None, True)
            return "Nothing"
        tile = self.tiles[loc]

        if not tile.is_passable():
            return "Obstacle"
        trap = tile.getTrap()
        if trap:
            if trap.team == "Players":
                return "Trap-Friendly"
            elif trap.team == "Monsters":
                return "Trap-Hostile"
        return "Nothing"


class Town(Pane):

    def __init__(self, seed, location, is_server=False, load_entities=False, pane_state=None):
        super(Town, self).__init__(seed, location, is_server, False, pane_state)
        self.buildings = []
        if load_entities:
            self.add_buildings()
        if is_server:
            self.add_npcs()
            if load_entities:
                if self.pane_state:
                    super(Town, self).load_state(pane_state)

    def add_buildings(self):
        seed = self.seed + str(self.location) + "Building"
        random.seed(seed)
        #Generate a rectangle region within bounds

        bounds = (7, 14, 5, 9)

    def add_npcs(self):
        for building in self.buildings:
            self.person.update(building.npcs)


class CombatPane(Pane):

    CombatEntrances = [TILE_LEFT, TILE_TOP, TILE_RIGHT, TILE_BOTTOM, TILE_TOP_LEFT, TILE_TOP_RIGHT, TILE_BOTTOM_LEFT, TILE_BOTTOM_RIGHT]
    def __init__(self, pane, pane_focus, monster, num_players):
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
        super(CombatPane, self).__init__(pane.seed, (0,0), False)
        self.objects = dict()           #Fixed combat/overworld passability bug
        self.paneCharacterLevel = 1

        self.open_region = Region("SQUARE", Location(self.location, (0, 0)), Location(self.location, (PANE_X-1, PANE_Y-1)))

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

        self.focus_location = Location(PANE_X/2 + dx*3, PANE_Y/2 + dy*3)
        fx = max(0, min(PANE_X - 1, self.focus_location.tile[0]))
        fy = max(0, min(PANE_Y - 1, self.focus_location.tile[1]))
        self.focus_location = Location(fx, fy)

        i = 2
        for x in range(loc_x-4, loc_x+6):
            j = 2
            for y in range(loc_y-2, loc_y+4):
                # print "(" + str(x) + ", " + str(y) + ")"
                if (x,y) in pane.objects:
                    self.add_zoomed_obstacle((i, j), pane.objects[(x,y)])
                    #Remove areas where there are obstacles
                    self.open_region("SUB", "SQUARE", Location(self.location, (i-1, j-1)), Location(self.location, (i+1, j+1)))
                j+=3
            i+=3

        self.load_background_images()
        if monster:
            monsters = TheoryCraft.generateMonsterGroup(monster, numberOfPlayers=num_players)
            self.place_monsters(monsters, self.focus_location)
            # for id, monster in self.person.iteritems():
                # loc = monster.location
                # self.traps_region("SUB", "SQUARE", loc, loc)
            #Remove areas where players can enter
            for (x, y) in CombatPane.CombatEntrances:
                self.open_region("SUB", "SQUARE", Location(self.location, (x-1, y-1)), Location(self.location, (x+1, y+1)))

            self.place_traps(num_players)


    def place_monsters(self, monsters, start_location):
        loc = start_location
        #print monsters
        for person in monsters:
            self.paneCharacterLevel = max(self.paneCharacterLevel, person.level)
            #Try to place monsters "near" eachother, but prevent placement off pane
            loc = self.rand_move_within_pane(loc, [1,9], [1,5], 3)
            person.location = loc
            self.person[id(person)] = person
            loc = self.rand_move_within_pane(loc, [1,9], [2,5], 3)


    def place_traps(self, number):
        ''' Number indicates the number of players '''

        numberOfTraps = Dice.rollNumberOfTraps(self.paneCharacterLevel)
        if 2 <= number <= 3:
            numberOfTraps += 1
        elif number == 4:
            numberOfTraps += 2

        for i in range(numberOfTraps):
            location = random.choice(list(self.open_region))

            #Place a trap here
            hostileTrap = trap.Trap.getRandomTrap(self.paneCharacterLevel, location)
            self.addTrap(location, hostileTrap)

            #Ensure we don't place a trap in the same spot
            self.open_region -= Region("SQUARE", location, location)


    def rand_move_within_pane(self, location, dir_range, dist_range, bounds):
        random.seed()
        i = 0
        while True:
            i += 1
            dir = random.randint(dir_range[0], dir_range[1])
            if dir == 5:    #Can't move in direction 5
                continue
            dist = random.randint(dist_range[0], dist_range[1])
            new_loc = location.move(dir, dist)
            if i >= 100:
                # print "Prevent infinite loop"
                new_loc = random.choice(list(self.open_region.locations))
            if not self.is_passable(new_loc):           #Can't place whith obstacles
                continue
            if not self.is_within_bounds(new_loc):  #Can't move off the pane
                continue
            if not new_loc in self.open_region:    #Location must be accessable
                continue
            if not self.has_path_to_edge(new_loc):  #Eliminate unreachable locations 
                self.open_region("SUB", "SQUARE", new_loc, new_loc)
                continue
            #We've found a suitable location, remove it from available list
            self.open_region("SUB", "SQUARE", new_loc, new_loc)
            return new_loc

    def is_passable(self, location):
        for key, person in self.person.iteritems():
            if person.location == location:
                return False
        return super(CombatPane, self).is_tile_passable(location)

    def has_path_to_edge(self, location):
        #Check location against a known accessable location (0, 0)
        start = Location(location.pane, location.tile)
        end = Location(self.location, (0, 0))
        pane_locations = Region("SQUARE", Location(self.location, (0, 0)), Location(self.location, (PANE_X - 1, PANE_Y - 1))).locations
        open_locations = self.open_region.locations
        has_path = Path.has_path(start, end, open_locations, pane_locations)
        # print "Path from " + str(start) + " to " + str(end) + ": " + str(has_path)
        return has_path

    def is_within_bounds(self, location):
        #Outside of current pane
        if self.location != location.pane:
            return False
        return True


    def add_zoomed_obstacle(self, tile_center, entity_key, zoomed=True):
        '''
        Zooms the given obstacle to a 3x3 obstacle and centers it on the given tile.
        '''

        entity_key += "_zoom" if entity_key.find("_zoom") == -1 else ""
        for di in range(0,3):
            for dj in range(0,3):
                tile = (tile_center[0]+(di-1), tile_center[1]+(dj-1))
                if not tile in self.tiles:
                    self.tiles[tile] = Tile(None, True)
                self.objects[tile] = entity_key

                image = None
                passable = False
                #These are separated in case we split up the work in sprites.py
                if entity_key in ZOOMED_OBSTACLES:
                    image = Sprites.get_zoomed_image(entity_key, (di,dj))
                elif entity_key in ZOOMED_PATHS:
                    image = Sprites.get_zoomed_image(entity_key, (di,dj))
                    passable = True
                else:
                    print "KEY NOT FOUND " + entity_key
                self.tiles[tile].entities.append(Entity(tile, image=image, passable=passable))


    def load_background_images(self):
        self.images = Sprites.get_images_dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                self.tiles[(i, j)].set_image(Sprites.get_background_tile(self.background_key, (i, j)))
