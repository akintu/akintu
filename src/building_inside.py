'''
Insides of buildings
'''

from pane import *
from sprites import *
from fields import *

class Inside(object):
    @staticmethod
    def getInside(type, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        if type == Portal.HOUSE:
            return House(seed, location, is_server, load_entities, pane_state, level)
        if type == Portal.DUNGEON:
            return Dungeon(seed, location, is_server, load_entites, pane_state, level)
        if type == Portal.SHOP:
            return Shop(seed, location, is_server, load_entities, pane_state, level)
        return None


class Building(Pane):
    '''
    Generic inside of a building or dungeon
    '''

    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None, background_image=None):
        '''
        Pane init signature:
        def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        '''

        super(Building, self).__init__(seed, location, is_server, load_entities, pane_state, level)

        print "INSIDE OF BUILDING: LOCATION = " + str(location)
        random.seed(self.seed + str(self.location) + "INSIDE")

        if not hasattr(self, "path_sheet"):
            self.path_sheet = Sprites.get_sheet(PATH_SHEET)
        if not hasattr(self, "path_image"):
            self.path_image = self.path_sheet.getimage((random.randrange(0, 4), 3))
        if not hasattr(self, "wall_sheet"):
            self.wall_sheet = Sprites.get_sheet(WALL_KEY)
        if not hasattr(self, "door_sheet"):
            self.door_sheet = Sprites.get_sheet(DOOR_KEY)

        self.load_background()

    def is_tile_passable(self, location, check_entity_keys=False):
        passable = self.tiles[location.tile].is_passable(check_entity_keys)
        #assert passable, 
        return passable

    def load_background(self):
        self.images = Sprites.get_images_dict()
        for i in range(PANE_X):
            for j in range(PANE_Y):
                if i in [0, 1, PANE_X-1, PANE_X-2] or j in [0, 1, PANE_Y-1, PANE_Y-2]:
                    self.tiles[(i, j)] = Tile(None, False)
                    self.tiles[(i, j)].set_image(self.wall_sheet.getimage((1,0)))
                else:
                    self.tiles[(i, j)] = Tile(None, True)
                    self.tiles[(i, j)].set_image(self.path_image)


class House(Building):
    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        self.path_sheet = Sprites.get_sheet(PATH_KEY)
        self.path_image = self.path_sheet.getimage((random.randrange(0, 4), 3))

        super(House, self).__init__(seed, location, is_server, load_entities, pane_state, level)

        #Add Door With Exit
        loc = (PANE_X/2, PANE_Y-2)
        door_image = self.door_sheet.getimage((3,0))
        iLocation = Location(location.pane, location.tile, z=-1, direction=location.direction)
        location.z = 0
        location.move(1, 2)
        door_portal = Portal(iLocation, portal_type=Portal.OVERWORLD, new_location=location , image=door_image, passable=True)
        self.tiles[loc] = Tile(None, True)
        self.tiles[loc].set_image(door_image)
        self.tiles[loc].add_entity = door_portal

class Dungeon(Building):
    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        print "Dungeon call"
        super(Dungeon, self).__init__(seed, location, is_server, load_entities, pane_state, level)
        #Add Door With Exit
        loc = (PANE_X/2, PANE_Y-2)
        door_image = self.door_sheet.getimage((3,0))
        door_portal = Portal(location, portal_type=Portal.OVERWORLD, location=loc, image=door_image, passable=True)
        self.tiles[loc] = Tile(None, True)
        self.tiles[loc].set_image(door_image)
        self.tiles[loc].add_entity = door_portal
        
class Shop(Building):
    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        print "Shop call"
        super(Shop, self).__init__(seed, location, is_server, load_entities, pane_state, level)
        #Add Door With Exit
        loc = (PANE_X/2, PANE_Y-2)
        door_image = self.door_sheet.getimage((3,0))
        door_portal = Portal(location, portal_type=Portal.OVERWORLD, location=loc, image=door_image, passable=True)
        self.tiles[loc] = Tile(None, True)
        self.tiles[loc].set_image(door_image)
        self.tiles[loc].add_entity = door_portal
