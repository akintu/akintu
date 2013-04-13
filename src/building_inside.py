'''
Insides of buildings
'''

from pane import *
from sprites import *
from fields import *

class Building(Pane):
    '''
    Generic inside of a building or dungeon
    '''

    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        '''
        Pane init signature:
        def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        '''

        self.seed = seed
        self.location = location
        self.is_server = is_server
        self.pane_state = pane_state
        self.tiles = dict()
        self.objects = dict()
        self.person = {}
        self.hostileTraps = []
        self.fields = Fields()
        self.path_sheet = Sprites.get_sheet(PATH_KEY)   
        random.seed(self.seed + str(self.location))
        self.floor_image = self.path_sheet.getimage((random.randrange(0, 4), 3))
        self.wall_sheet = Sprites.get_sheet(WALL_KEY)
        self.door_sheet = Sprites.get_sheet(DOOR_KEY)
        self.images = Sprites.get_images_dict()
        if not level:
            self.paneLevel = max(abs(self.location.pane[0]), abs(self.location.pane[1]))
        else:
            self.paneLevel = level

        for i in range(PANE_X):
            for j in range(PANE_Y):
                if i in [0, 1, PANE_X-1, PANE_X-2] or j in [0, 1, PANE_Y-1, PANE_Y-2]:
                    self.tiles[(i, j)] = Tile(None, False)
                    self.tiles[(i, j)].set_image(self.wall_sheet.getimage((1,0)))
                else:
                    self.tiles[(i, j)] = Tile(None, True)
                    self.tiles[(i, j)].set_image(self.floor_image)

    def is_tile_passable(self, location, check_entity_keys=False):
        passable = self.tiles[location.tile].is_passable(check_entity_keys)
        #assert passable, 
        return passable

class House(Building):
    def __init__(self, seed, location, is_server=False, load_entities=True, pane_state=None, level=None):
        print "House call"
        super(House, self).__init__(seed, location, is_server, load_entities, pane_state, level)
        #Add Door With Exit
        loc = (PANE_X/2, PANE_Y-2)
        door_image = self.door_sheet.getimage((3,0))
        door_portal = Portal(location, portal_type=Portal.OVERWORLD, location=loc, image=door_image, passable=True)
        self.tiles[loc] = Tile(None, True)
        self.tiles[loc].set_image(door_image)
        self.tiles[loc].add_entity = door_portal

