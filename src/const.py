'''
Constants for use in Akintu
'''

from pygame.locals import *

SHOW_FPS = True

CAPTION = "Akintu r01"

import os

def enum(**enums):
    return type('Enum', (), enums)

TILE_SIZE = 32
PANE_X = 32
PANE_Y = 20

TILE_TOP_LEFT = (0, 0)
TILE_TOP_RIGHT = (PANE_X-1, 0)
TILE_BOTTOM_LEFT = (0, PANE_Y-1)
TILE_BOTTOM_RIGHT = (PANE_X-1, PANE_Y-1)

TILES_LEFT = (TILE_TOP_LEFT, TILE_BOTTOM_LEFT)
TILES_TOP = (TILE_TOP_LEFT, TILE_TOP_RIGHT)
TILES_RIGHT = (TILE_TOP_RIGHT, TILE_BOTTOM_RIGHT)
TILES_BOTTOM = (TILE_BOTTOM_LEFT, TILE_BOTTOM_RIGHT)

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
GRASS2 = (BACKGROUND_IMAGES_PATH, "grass2.jpg", TILE_SIZE, None, None)
GRASS3 = (BACKGROUND_IMAGES_PATH, "grass3.jpg", TILE_SIZE, None, None)
GRASS4 = (BACKGROUND_IMAGES_PATH, "grass4.jpg", TILE_SIZE, None, None)
GRASS5 = (BACKGROUND_IMAGES_PATH, "grass5.jpg", TILE_SIZE, None, None)
GRAVEL1 = (BACKGROUND_IMAGES_PATH, "gravel1.jpg", TILE_SIZE, None, None)

ENTITIES = {'trees': TREES, 'rocks': ROCKS}
BACKGROUNDS = [GRASS1, GRASS2, GRASS3, GRASS4, GRASS5, GRAVEL1]

MOVE_KEYS = {K_LEFT: 4, K_KP4: 4, K_h: 4, K_RIGHT: 6, K_KP6: 6, K_l: 6, K_UP: 8, K_KP8: 8, K_k: 8, \
                K_DOWN: 2, K_KP2: 2, K_j: 2, K_KP7: 7, K_y: 7, K_KP9: 9, K_u: 9, K_KP3: 3, K_n: 3, \
                K_KP1: 1, K_b: 1}
