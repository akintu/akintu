'''
Sprite Related Objects and Helper Functions

'''
import os
import random

from PIL import Image
grassimage = os.path.join("res", "images", "background", "grass.png")
rockimage = os.path.join("res", "images", "rock1.png")
tree_sheet = os.path.join("res", "images", "trees1.png")

def crop_helper(const):
    return Crop(const[0], const[1], const[2], const[3], const[4])

class Crop(object):
    def __init__(self, pathDIR, name, tilesize, cropsize = None, size = None):
        if not cropsize:
            cropsize = tilesize
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
        
    def get_random_entity(self, percentage):
        i = random.randrange(self.sheet.x / percentage)
        j = random.randrange(self.sheet.y / percentage)
        image = None
        if i <= self.sheet.x and j <= self.sheet.x:
            image = self.sheet.getimage((i,j))
        return image
        
