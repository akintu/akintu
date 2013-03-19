'''
Constants for use in Akintu
'''

from pygame.locals import *
import os

def enum(**enums):
    return type('Enum', (), enums)

CAPTION = "Akintu r01"
SHOW_FPS = True

TILE_SIZE = 32
PANE_X = 32
PANE_Y = 20
CENTER = (PANE_X/2, PANE_Y/2)

TOWNSHIP_X = TOWNSHIP_Y = 5
COUNTRY_X = COUNTRY_Y = 5

SIDEBAR_X = PANE_X * TILE_SIZE
SIDEBAR_Y = 0

TILE_TOP_LEFT = (0, 0)
TILE_TOP_RIGHT = (PANE_X-1, 0)
TILE_BOTTOM_LEFT = (0, PANE_Y-1)
TILE_BOTTOM_RIGHT = (PANE_X-1, PANE_Y-1)

TILES_LEFT = (TILE_TOP_LEFT, TILE_BOTTOM_LEFT)
TILES_TOP = (TILE_TOP_LEFT, TILE_TOP_RIGHT)
TILES_RIGHT = (TILE_TOP_RIGHT, TILE_BOTTOM_RIGHT)
TILES_BOTTOM = (TILE_BOTTOM_LEFT, TILE_BOTTOM_RIGHT)

DESIRED_FPS = 120

#=======================PATHS=============================
#     =====================SAVES (AND RELATED)============
SAVES_PATH = os.path.join("res", "saves")
CHAR_SAVE_PATH = os.path.join(SAVES_PATH, "characters")
WORLD_SAVE_PATH = os.path.join(SAVES_PATH, "worlds")
TMP_WORLD_SAVE_PATH = os.path.join(SAVES_PATH, "tmp")
CHAR_SAVE_EXT = ".akinc"
WORLD_SAVE_EXT = ".akinw"

#     =====================IMAGES=========================
#Coverage Percentage (.1 = 10%)
RAND_ENTITIES = .06

IMAGES_PATH = os.path.join("res", "images")
OBSTACLES_IMAGES_PATH = os.path.join(IMAGES_PATH, "obstacles")
BACKGROUND_IMAGES_PATH = os.path.join(IMAGES_PATH, "background")
MONSTERS_IMAGES_PATH = os.path.join(IMAGES_PATH, "monsters")
SPRITES_IMAGES_PATH = os.path.join(IMAGES_PATH, "sprites")
ITEMS_IMAGES_PATH = os.path.join(IMAGES_PATH, "items")

#======================SAVE/LOAD KEYS==========================
SEED_KEY = "seed"
MONSTER_KEY = "monsters"
ITEM_KEY = "items"
CHEST_KEY = "chests"    #Also used with images

#=====================CMD TYPES/ACTIONS========================


#======================KEY COMMANDS==========================
MODIFIER_KEYS = [K_LSHIFT, K_RSHIFT, K_LCTRL, K_RCTRL, K_LALT, K_RALT]
MOVE_KEYS = {K_LEFT: 4, K_KP4: 4, K_h: 4, K_RIGHT: 6, K_KP6: 6, K_l: 6, K_UP: 8, K_KP8: 8, K_k: 8, \
                K_DOWN: 2, K_KP2: 2, K_j: 2}
#MOVE_KEYS = {K_LEFT: 4, K_KP4: 4, K_h: 4, K_RIGHT: 6, K_KP6: 6, K_l: 6, K_UP: 8, K_KP8: 8, K_k: 8, \
#                K_DOWN: 2, K_KP2: 2, K_j: 2, K_KP7: 7, K_y: 7, K_KP9: 9, K_u: 9, K_KP3: 3, K_n: 3, \
#                K_KP1: 1, K_b: 1}
