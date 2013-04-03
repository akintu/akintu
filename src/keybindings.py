'''
Keybindings utility module
'''

from pygame.locals import *
import pygame

class Keystate():
    def __init__(self):
        self.keystate = []
        self.inputState = "OVERWORLD" # "OVERWORLD", "LEVELUP", "INVENTORY", "CONSUMABLE", "TARGET", "SHOP",
                                     # "ABILITIES", "SPELLS", "COMBAT"

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

        self.ALL = ["OVERWORLD", "LEVELUP", "INVENTORY", "CONSUMABLE", "TARGET", "SHOP", "ABILITIES", "SPELLS", "COMBAT"]
        self.MOVEMENT = ["OVERWORLD", "COMBAT"]
        self.DIALOG = ["LEVELUP", "INVENTORY", "CONSUMABLE", "SHOP", "ABILITIES", "SPELLS"]

        self.bindings = {"QUIT": (["CTRL+q", "CTRL+x"], self.ALL),
            "CLOSEMENU": ("escape", self.DIALOG),

            "UP": ([K_UP, K_KP8, "k"], self.MOVEMENT),
            "DOWN": ([K_DOWN, K_KP2, "j"], self.MOVEMENT),
            "LEFT": ([K_LEFT, K_KP4, "h"], self.MOVEMENT),
            "RIGHT": ([K_RIGHT, K_KP6, "l"], self.MOVEMENT),

            "DIALOGUP": ([K_UP, K_KP8, "k"], self.DIALOG),
            "DIALOGDOWN": ([K_DOWN, K_KP2, "j"], self.DIALOG),
            "DIALOGLEFT": ([K_LEFT, K_KP4, "h"], self.DIALOG),
            "DIALOGRIGHT": ([K_RIGHT, K_KP6, "l"], self.DIALOG),

            "TARGETUP": ([K_UP, K_KP8, "k"], "TARGET"),
            "TARGETDOWN": ([K_DOWN, K_KP2, "j"], "TARGET"),
            "TARGETLEFT": ([K_LEFT, K_KP4, "h"], "TARGET"),
            "TARGETRIGHT": ([K_RIGHT, K_KP6, "l"], "TARGET"),
            "TARGETUPLEFT": ([K_KP7, "y"], "TARGET"),
            "TARGETUPRIGHT": ([K_KP9, "u"], "TARGET"),
            "TARGETDOWNLEFT": ([K_KP1, "b"], "TARGET"),
            "TARGETDOWNRIGHT": ([K_KP3, "n"], "TARGET"),

            "SCROLLTOP": (["SHIFT+page up", "SHIFT+="], self.MOVEMENT),
            "SCROLLUP": (["page up", "="], self.MOVEMENT),
            "SCROLLDOWN": (["page down", "-"], self.MOVEMENT),
            "SCROLLBOTTOM": (["SHIFT+page down", "SHIFT+-"], self.MOVEMENT),

            "LEVELUPADVANCE": ([" ", "a"], "LEVELUP"),

            "TEST1": ("CTRL+SHIFT+o", self.MOVEMENT),
            "CHEAT CODE": ("[+]", self.MOVEMENT)
            }

    def __call__(self, e=None):
        if e:
            if e.type == KEYUP and e.key in self.keystate:
                self.keystate.remove(e.key)
            if e.type == KEYDOWN and e.key not in self.keystate:
                self.keystate.append(e.key)
#            print self.keystate

        events = [k for k, v in self.bindings.iteritems() if v[0] in self and \
                (self.inputState == v[1] or self.inputState in v[1] or v[1] == "ALL")]
        return events[0] if events else None

    def __contains__(self, combolist):
        if not isinstance(combolist, list):
            combolist = [combolist]
        return any(all(key in self.keystate or key in [pygame.key.name(k) for k in self.keystate] or \
                (key in self.mod_keys and \
                any(mod in self.keystate for mod in self.mod_keys[key])) and \
                not any(key in self.keystate for k, v in self.mod_keys.iteritems() for key in v \
                if k not in combo) \
                for key in (combo.split('+') if isinstance(combo, basestring) else [combo])) \
                for combo in combolist)

    def __str__(self):
        return str(self.keystate)

    def direction(self, state):
        dir = self()
        if not dir:
            return False
        if state == "MOVEMENT" and self.inputState in self.MOVEMENT and any(k == dir for k in self.move_keys.keys()):
            return self.move_keys[dir]
        if state == "DIALOG" and self.inputState in self.DIALOG and any(k == dir[6:] for k in self.move_keys.keys()):
            return self.move_keys[dir[6:]]
        if state == "TARGET" and self.inputState == state and any(k == dir[6:] for k in self.move_keys.keys()):
            return self.move_keys[dir[6:]]
        return False


keystate = Keystate()