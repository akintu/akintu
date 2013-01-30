'''
Constants for use in Akintu
'''

import os

TILE_SIZE = 32
PANE_X = 32
PANE_Y = 20
RAND_TREES = .40 #Coverage Percentage

IMAGES_PATH = os.path.join("res", "images")
BACKGROUND_IMAGES_PATH = os.path.join(IMAGES_PATH, "background")


#(Path, Name, Tilesize, Cropsize, Size)
GRASS1 = (BACKGROUND_IMAGES_PATH, "grass1.jpg", TILE_SIZE, None, None)
GRASS2 = (BACKGROUND_IMAGES_PATH, "grass2.jpg", TILE_SIZE, None, None)
TREES = (IMAGES_PATH, "trees1.png", TILE_SIZE, None, None)    
ROCKS = (IMAGES_PATH, "rocks1.png", TILE_SIZE, None, None)
