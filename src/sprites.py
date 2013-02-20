'''
Sprite Related Objects and Helper Functions

'''
import os
import random

from const import *
from PIL import Image

# rockimage = os.path.join("res", "images", "rocks1.png")
# tree_sheet = os.path.join("res", "images", "trees1.png")

class Sprites(object):
    
    hasLoaded = False
    trees = []
    rocks = []
    background = []
    objects = dict()
    images = dict()
    
    @staticmethod
    def load(seed):
        if Sprites.hasLoaded:
            print "Sprites.load() has already been called."
        
        for image in BACKGROUNDS:
            background = crop_helper(image)
            Sprites.background.append(background)
            Sprites.images.update(background.images.items())
        for key, image in ENTITIES.iteritems():
            spritesheet = SpriteSheet(image)
            Sprites.objects[key] = spritesheet
            Sprites.images.update(spritesheet.images.items())
        Sprites.hasLoaded = True

    @staticmethod
    def get_background(seed, tile):
        random.seed(seed)
        i = random.randrange(len(Sprites.background))
        return Sprites.background[i].getimage(tile)
    
    @staticmethod
    def get_images_dict():
        return Sprites.images
    # @staticmethod
    # def get_random_image(key, seed, pane, tile):
        # random.seed(seed)
        # i = random.randrange(len(Sprites.objects))
        # return Sprites.objects[key].get_random_image(seed, pane, tile)
    @staticmethod
    def get_object(key, seed, pane, tile):
        return Sprites.objects[key].get_random_image(seed, pane, tile)

def crop_helper(const):
    return Crop(const[0], const[1], const[2], const[3], const[4])
    
class Crop(object):
    def __init__(self, pathDIR, name, tilesize, cropsize = None, size = None):
        if not cropsize:
            cropsize = tilesize
        self.name = name
        self.tile_id = dict()
        self.images = dict()
        path = os.path.join(pathDIR, name)
        self.backimage = Image.open(path)

        if size:
            self.backimage.resize(size)
        self.x = self.backimage.size[0]/cropsize
        self.y = self.backimage.size[1]/cropsize
        currx = 0
        for i in range(self.x):
            curry = 0
            for j in range(self.y):
                id = name + str(i) + "_" + str(j)
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
        
class SpriteSheet(object):
    def __init__(self, sheet):
        self.images = dict()
        self.sheet = crop_helper(sheet)
        self.images = self.sheet.images
        self.name = self.sheet.name
        #self.seed = seed
        
    def get_random_image(self, seed, pane, tile):#, percentage):
        random.seed(seed + str(pane) + self.name + str(tile))
        i = random.randrange(self.sheet.x)# / percentage)
        j = random.randrange(self.sheet.y)# / percentage)
        image = None
        if i <= self.sheet.x and j <= self.sheet.x:
            image = self.sheet.getimage((i,j))
        return image
        
