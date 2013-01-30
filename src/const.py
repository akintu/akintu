'''
Constants for use in Akintu
'''

import os

TILE_SIZE = 32
PANE_X = 32
PANE_Y = 20

#Coverage Percentage (.1 = 10%)
RAND_TREES = .20 
RAND_ROCKS = .1

IMAGES_PATH = os.path.join("res", "images")
BACKGROUND_IMAGES_PATH = os.path.join(IMAGES_PATH, "background")


#(Path, Name, Tilesize, Cropsize, Size)
TREES = (IMAGES_PATH, "trees1.png", TILE_SIZE, None, None)    
ROCKS = (IMAGES_PATH, "rocks1.png", TILE_SIZE, None, None)

GRASS1 = (BACKGROUND_IMAGES_PATH, "grass1.jpg", TILE_SIZE, None, None)
GRASS2 = (BACKGROUND_IMAGES_PATH, "grass2.jpg", TILE_SIZE, None, None)
GRASS3 = (BACKGROUND_IMAGES_PATH, "grass3.jpg", TILE_SIZE, None, None)
GRASS4 = (BACKGROUND_IMAGES_PATH, "grass4.jpg", TILE_SIZE, None, None)
GRASS5 = (BACKGROUND_IMAGES_PATH, "grass5.jpg", TILE_SIZE, None, None)

ENTITIES = {'trees': TREES, 'rocks': ROCKS}
BACKGROUNDS = [GRASS1, GRASS2, GRASS3, GRASS4, GRASS5]