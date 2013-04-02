'''
Keybindings utility module
'''

from pygame.locals import *
import pygame

class Keystate():
    def __init__(self):
        self.keystate = []
        self.inputState = "MOVEMENT" # "MOVEMENT", "LEVELUP", "INVENTORY", "CONSUMABLE", "TARGET", "SHOP",
                                     # "ABILITIES", "SPELLS", "ITEMS"

        self.mod_keys = {"SHIFT": [K_LSHIFT, K_RSHIFT],
                        "CTRL": [K_LCTRL, K_RCTRL],
                        "ALT": [K_LALT, K_RALT]}

        self.move_keys = {"UP": 8,
                        "DOWN": 2,
                        "LEFT": 4,
                        "RIGHT": 6,
                        "UPLEFT": 7,
                        "UPRIGHT": 9,
                        "DOWNLEFT": 1,
                        "DOWNRIGHT": 3}

        self.bindings = {"UP": [K_UP, K_KP8, "k"],
                        "DOWN": [K_DOWN, K_KP2, "j"],
                        "LEFT": [K_LEFT, K_KP4, "h"],
                        "RIGHT": [K_RIGHT, K_KP6, "l"],
                        "UPLEFT": [K_KP7, "y"],
                        "UPRIGHT": [K_KP9, "u"],
                        "DOWNLEFT": [K_KP1, "b"],
                        "DOWNRIGHT": [K_KP3, "n"],
                        "TEST1": "CTRL SHIFT o",
                        }

    def __call__(self, e):
        if e:
            if isinstance(e, basestring):
                self.inputState = e
            else:
                if e.type == KEYUP and e.key in self.keystate:
                    self.keystate.remove(e.key)
                if e.type == KEYDOWN and e.key not in self.keystate:
                    self.keystate.append(e.key)
    #            print self.keystate

        events = [k for k, v in self.bindings.iteritems() if v in self]
        return events[0] if events else None

    def __contains__(self, combolist):
        if not isinstance(combolist, list):
            combolist = [combolist]
        return any(all(key in self.keystate or key in [pygame.key.name(k) for k in self.keystate] or \
                (key in self.mod_keys and \
                any(mod in self.keystate for mod in self.mod_keys[key])) and \
                not any(key in self.keystate for k, v in self.mod_keys.iteritems() for key in v \
                if k not in combo) \
                for key in (combo.split() if isinstance(combo, basestring) else [combo])) \
                for combo in combolist)

    def __str__(self):
        return str(self.keystate)

    def direction(self, strict=True):
        dir = self()
        if dir and (dir in ["UP", "DOWN", "LEFT", "RIGHT"] or \
                (not strict and dir in ["UPLEFT", "UPRIGHT", "DOWNLEFT", "DOWNRIGHT"])):
            return self.move_keys[dir]
        return None


keystate = Keystate()