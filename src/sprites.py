'''
Sprite Related Objects and Helper Functions

'''
import os
import random

from const import *
from PIL import Image


#(Path, Name, Tilesize, Cropsize, Size)
TREE = (OBSTACLES_IMAGES_PATH, "tree_green.png", TILE_SIZE, None, TILE_SIZE)
ROCKS = (OBSTACLES_IMAGES_PATH, "rocks1.png", TILE_SIZE, None, TILE_SIZE)

GRASS1 = (BACKGROUND_IMAGES_PATH, "grass1.jpg", TILE_SIZE, None, None)
GRASS2 = (BACKGROUND_IMAGES_PATH, "grass2.jpg", TILE_SIZE, None, None)
GRASS3 = (BACKGROUND_IMAGES_PATH, "grass3.jpg", TILE_SIZE, None, None)
GRASS4 = (BACKGROUND_IMAGES_PATH, "grass4.jpg", TILE_SIZE, None, None)
GRAVEL1 = (BACKGROUND_IMAGES_PATH, "gravel1.jpg", TILE_SIZE, None, None)

ENTITY_KEYS = ['tree', 'rocks']
ENTITIES = {'tree': TREE, 'rocks': ROCKS}
#BACKGROUNDS = [GRASS1, GRASS2, GRASS3, GRASS4, GRASS5, GRAVEL1]
BACKGROUNDS = {'summer': GRASS2, 'fall': GRASS3, 'desert': GRAVEL1}

class Sprites(object):
    
    hasLoaded = False
    trees = []
    rocks = []
    background = dict()
    objects = dict()
    images = dict()
    
    @staticmethod
    def load(seed):
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
        Sprites.hasLoaded = True

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
    def get_object(key, seed, pane, tile):
        return Sprites.objects[key].get_random_image(seed, pane, tile)
        
    @staticmethod
    def get_zoomed_image(key, tile_loc):
        return Sprites.objects[key].get_zoomed_image(tile_loc)

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
        random.seed(seed + str(pane) + self.name + str(tile))
        i = random.randrange(self.crop.x)# / percentage)
        j = random.randrange(self.crop.y)# / percentage)
        image = None
        if i <= self.crop.x and j <= self.crop.x:
            image = self.crop.getimage((i,j))
        return image
        
