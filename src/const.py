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

TILE_LEFT = (0, PANE_Y/2)
TILE_TOP = (PANE_X/2, 0)
TILE_RIGHT = (PANE_X-1, PANE_Y/2)
TILE_BOTTOM = (PANE_X/2, PANE_Y-1)

TILES_LEFT = (TILE_TOP_LEFT, TILE_BOTTOM_LEFT)
TILES_TOP = (TILE_TOP_LEFT, TILE_TOP_RIGHT)
TILES_RIGHT = (TILE_TOP_RIGHT, TILE_BOTTOM_RIGHT)
TILES_BOTTOM = (TILE_BOTTOM_LEFT, TILE_BOTTOM_RIGHT)

DESIRED_FPS = 120

#=======================PATHS=============================
#     =====================STAMPS=========================
STAMP_PATH = os.path.join("res", "stamps")
STAMP_DUNGEON_PATH = os.path.join(STAMP_PATH, "dungeon")
STAMP_HOUSE_PATH = os.path.join(STAMP_PATH, "house")
STAMP_TOWN_PATH = os.path.join(STAMP_PATH, "town")
STAMP_PANE_PATH = os.path.join(STAMP_PATH, "pane")
STAMP_GENERATED_PATH = os.path.join(STAMP_PATH, "generated")

#     =====================SAVES (AND RELATED)============
SAVES_PATH = os.path.join("res", "saves")
CHAR_SAVE_PATH = os.path.join(SAVES_PATH, "characters")
WORLD_SAVE_PATH = os.path.join(SAVES_PATH, "worlds")
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
TRAPS_IMAGES_PATH = os.path.join(ITEMS_IMAGES_PATH, "traps")

#        ======================MISC=================
HELP_PATH = os.path.join("data", "help_menu")

#======================SAVE/LOAD KEYS==========================
SEED_KEY = "seed"
MONSTER_KEY = "monsters"
ITEM_KEY = "items"
CHEST_KEY = "chests"    #Also used with images
