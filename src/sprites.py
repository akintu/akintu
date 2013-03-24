'''
Sprite Related Objects and Helper Functions

'''
import os
import random

from const import *
from PIL import Image

#OBSTACLES
#(Path, Name, Tilesize, Cropsize, Size)
TREE = (OBSTACLES_IMAGES_PATH, "tree_green.png", TILE_SIZE, None, TILE_SIZE)
TREE_ZOOM = TREE
ROCK = (OBSTACLES_IMAGES_PATH, "rock.png", TILE_SIZE, None, TILE_SIZE)
ROCK_ZOOM = (OBSTACLES_IMAGES_PATH, "rock_zoom.png", TILE_SIZE, None, TILE_SIZE)

#BACKGROUNDS
GRASS1 = (BACKGROUND_IMAGES_PATH, "grass1.jpg", TILE_SIZE, None, None)
GRASS2 = (BACKGROUND_IMAGES_PATH, "grass2.jpg", TILE_SIZE, None, None)
GRASS3 = (BACKGROUND_IMAGES_PATH, "grass3.jpg", TILE_SIZE, None, None)
GRASS4 = (BACKGROUND_IMAGES_PATH, "grass4.jpg", TILE_SIZE, None, None)
GRAVEL1 = (BACKGROUND_IMAGES_PATH, "gravel1.jpg", TILE_SIZE, None, None)

OBSTACLES = {'tree': TREE, 'rock': ROCK}
ENTITIES = dict(OBSTACLES.items())  #ADD MORE ITEMS HERE
ZOOMED_ENTITIES = {'rock_zoom': ROCK_ZOOM, 'tree_zoom': TREE_ZOOM}
BACKGROUNDS = {'summer': GRASS2, 'fall': GRASS3, 'desert': GRAVEL1}
ENTITY_KEYS = sorted(ENTITIES.keys())
OBSTACLE_KEYS = sorted(OBSTACLES.keys())

#ITEMS AND SUCH
CHEST = (ITEMS_IMAGES_PATH, "treasure_chest.png", TILE_SIZE, None, None)
HOUSE = (ITEMS_IMAGES_PATH, "house.png", TILE_SIZE, None, None)

PATHS = (BACKGROUND_IMAGES_PATH, "paths.png", TILE_SIZE, None, None)

#KEYS
HOUSE_KEY = "house"
PATH_KEY = "path"

SHEETS = {CHEST_KEY: CHEST, HOUSE_KEY: HOUSE, PATH_KEY: PATHS}

class Sprites(object):

    hasLoaded = False
    background = dict()
    objects = dict()
    zoomed_objects = dict()
    images = dict()
    sheets = dict()

    @staticmethod
    def load_all():
        if Sprites.hasLoaded:
            print "Sprites.load() has already been called."

        for key, image in BACKGROUNDS.iteritems():
            background = crop_helper(image)
            Sprites.background[key] = background
            Sprites.images.update(background.images.items())
        for key, image in ENTITIES.iteritems():
            spritesheet = SpriteSheet(image)
            Sprites.objects[key] = spritesheet
            Sprites.images.update(spritesheet.images.items())
        for key, image in ZOOMED_ENTITIES.iteritems():
            spritesheet = SpriteSheet(image)
            Sprites.objects[key] = spritesheet
            Sprites.images.update(spritesheet.images.items())
            
        for key, image in SHEETS.iteritems():
            Sprites.load_sheet(key, image)
        Sprites.hasLoaded = True

    @staticmethod
    def load_sheet(key, image):
        spritesheet = crop_helper(image)
        Sprites.sheets[key] = spritesheet
        Sprites.images.update(spritesheet.images.items())
    
    @staticmethod
    def get_background(seed):
        random.seed(seed)
        return random.choice(list(Sprites.background.keys()))

    @staticmethod
    def get_background_tile(key, tile):
        return Sprites.background[key].getimage(tile)

    @staticmethod
    def get_images_dict():
        return Sprites.images

    @staticmethod
    def get_obstacle(key, seed, pane, tile):
        # if not seed:
            # print "Seed is None in Sprites.get_obstacle"
        return Sprites.objects[key].get_random_image(seed, pane, tile)

    @staticmethod
    def get_zoomed_image(key, tile_loc):
        return Sprites.objects[key].get_zoomed_image(tile_loc)
    
    @staticmethod
    def get_sheet(key):
        return Sprites.sheets[key]
        
    @staticmethod
    def make_transparent(image, opacity=.5):
        if opacity < 0:
            opacity = 0
        if opacity > 1:
            opacity = 1
            
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        else:
            image = image.copy()
        alpha = image.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        image.putalpha(alpha)
        return image


def crop_helper(const):
    return Crop(const[0], const[1], const[2], const[3], const[4])

class Crop(object):
    def __init__(self, pathDIR, name, tilesize, cropsize = None, size = None, zoom = False):
        if not cropsize:
            cropsize = tilesize
        self.name = name
        self.tile_id = dict()
        self.images = dict()
        path = os.path.join(pathDIR, self.name)
        self.backimage = Image.open(path)
        if zoom:
            if not size:
                size = tilesize*3
        self._crop(tilesize, cropsize, size, zoom)

    def _crop(self, tilesize, cropsize = None, size = None, zoom = False):
        if size:
            self.backimage = self.backimage.resize((size, size))
        zoom_str = "zoom"
        if not zoom:
            zoom_str = ""
        self.x = self.backimage.size[0]/cropsize
        self.y = self.backimage.size[1]/cropsize
        currx = 0
        for i in range(self.x):
            curry = 0
            for j in range(self.y):
                id = self.name + zoom_str + str(i) + "_" + str(j)
                if zoom:
                    self.tile_id[str((i,j))] = id
                else:
                    self.tile_id[(i, j)] = id
                self.images[id] = self.backimage.crop(
                    (currx, curry, currx + cropsize, curry + cropsize))
                if not cropsize == tilesize:
                    self.images[id].resize((tilesize, tilesize))
                curry += cropsize
            currx += cropsize

    def getimage(self, location):
        i = location[0] % self.x
        j = location[1] % self.y
        return self.tile_id[(i, j)]

    def get_zoomed_image(self, location):
        return self.tile_id[str(location)]

    def get_row(self, y):
        image_list = []
        x = 0
        while x < self.x:
            image_list.append(self.getimage((x, y)))
            x+=1
        return image_list
        
    def get_column(self, x):
        image_list = []
        y = 0
        while y < self.y:
            image_list.append(self.getimage((x, y)))
            y += 1
        return image_list

class SpriteSheet(object):
    def __init__(self, sheet):
        self.images = dict()
        self.crop = crop_helper(sheet)
        self.images.update(self.crop.images.items())

        self.zoom = Crop(sheet[0], sheet[1], sheet[2], sheet[3], TILE_SIZE*3, True)
        self.images.update(self.zoom.images.items())

        self.name = self.crop.name
        self.sheet = sheet

    def get_zoomed_image(self, tile_loc):
        '''
        Returns the cropped image of size TILE_SIZE given a tile_loc

        Member Variables
            tile_loc:   an tuple representing the portion of an image
                        that is divided into 9 pieces:
                        (0,0)   (1,0)   (2,0)
                        (0,1)   (1,1)   (2,1)
                        (0,2)   (1,2)   (2,2)
        '''
        return self.zoom.get_zoomed_image(tile_loc)

    def get_random_image(self, seed, pane, tile):#, percentage):
        random.seed(str(seed) + str(pane) + self.name + str(tile))
        i = random.randrange(self.crop.x)# / percentage)
        j = random.randrange(self.crop.y)# / percentage)
        image = None
        if i <= self.crop.x and j <= self.crop.x:
            image = self.crop.getimage((i,j))
        return image
