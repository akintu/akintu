'''
Constants for use in Akintu
'''
SHOW_FPS = True

CAPTION = "Akintu r01"

import os

TILE_SIZE = 32
PANE_X = 32
PANE_Y = 20

DESIRED_FPS = 120

#Coverage Percentage (.1 = 10%)
RAND_TREES = .20 
RAND_ROCKS = .1

IMAGES_PATH = os.path.join("res", "images")
BACKGROUND_IMAGES_PATH = os.path.join(IMAGES_PATH, "background")
MONSTERS_IMAGES_PATH = os.path.join(IMAGES_PATH, "monsters")

#(Path, Name, Tilesize, Cropsize, Size)
TREES = (IMAGES_PATH, "trees1.png", TILE_SIZE, None, None)    
ROCKS = (IMAGES_PATH, "rocks1.png", TILE_SIZE, None, None)

GRASS1 = (BACKGROUND_IMAGES_PATH, "grass1.jpg", TILE_SIZE, None, None)
GRASS2 = (BACKGROUND_IMAGES_PATH, "grass2.jpg", TILE_SIZE, None, (128, 128))
GRASS3 = (BACKGROUND_IMAGES_PATH, "grass3.jpg", TILE_SIZE, None, (128, 128))
GRASS4 = (BACKGROUND_IMAGES_PATH, "grass4.jpg", TILE_SIZE, None, (128, 128))
GRASS5 = (BACKGROUND_IMAGES_PATH, "grass5.jpg", TILE_SIZE, None, (128, 128))
GRAVEL1 = (BACKGROUND_IMAGES_PATH, "gravel1.jpg", TILE_SIZE, None, None)

ENTITIES = {'trees': TREES, 'rocks': ROCKS}
BACKGROUNDS = [GRASS1, GRASS2, GRASS3, GRASS4, GRASS5, GRAVEL1]
