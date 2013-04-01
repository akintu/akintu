"""Keybindings utility module"""

from pygame.locals import *

MODIFIER_KEYS = {"SHIFT": [K_LSHIFT, K_RSHIFT],
                "CTRL": [K_LCTRL, K_RCTRL],
                "ALT": [K_LALT, K_RALT]}

ARROW_KEYS = {"UP": [K_UP, K_KP8, K_k],
            "DOWN": [K_DOWN, K_KP2, K_j],
            "LEFT": [K_LEFT, K_KP4, K_h],
            "RIGHT": [K_RIGHT, K_KP6, K_l],
            "UPLEFT": [K_KP7, K_y],
            "UPRIGHT": [K_KP9, K_u],
            "DOWNLEFT": [K_KP1, K_b],
            "DOWNRIGHT": [K_KP3, K_n]}

MOVE_KEYS = {"UP": 8,
            "DOWN": 2,
            "LEFT": 4,
            "RIGHT": 6,
            "UPLEFT": 7,
            "UPRIGHT": 9,
            "DOWNLEFT": 1,
            "DOWNRIGHT": 3}

KEYS = {key: k for k, v in ARROW_KEYS.iteritems() for key in v}
print KEYS