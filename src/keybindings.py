'''
Keybindings utility module
'''

from pygame.locals import *
import pygame

class Keystate():
    def __init__(self):
        self.keystate = []
        self.typematicRate = 0.1
        self.keyTime = 0

        self.inputState = "OVERWORLD" # "OVERWORLD", "LEVELUP", "INVENTORY", "CONSUMABLE", "TARGET", "SHOP",
                                     # "ABILITIES", "SPELLS", "COMBAT"

        self.mod_keys = {"SHIFT": [K_LSHIFT, K_RSHIFT],
                        "CTRL": [K_LCTRL, K_RCTRL],
                        "ALT": [K_LALT, K_RALT],
                        "META": [K_LMETA, K_RMETA]}

        self.move_keys = {"UP": 8,
                        "DOWN": 2,
                        "LEFT": 4,
                        "RIGHT": 6,
                        "UPLEFT": 7,
                        "UPRIGHT": 9,
                        "DOWNLEFT": 1,
                        "DOWNRIGHT": 3}

        self.ALL = ["OVERWORLD", "LEVELUP", "INVENTORY", "CONSUMABLE", "TARGET", "SHOP", "ABILITIES", "SPELLS", "COMBAT", "CHARSHEET"]
        self.MOVEMENT = ["OVERWORLD", "COMBAT"]
        self.DIALOG = ["LEVELUP", "INVENTORY", "CONSUMABLE", "SHOP", "ABILITIES", "SPELLS", "CHARSHEET"]

        '''
        The bindings data structure is a bit involved, so get your thinking cap on for this.

        The key is the name of an event that is kicked off when the conditions are met.  This event
        should be caught and handled in game.py handle_events().

        The value is a duple.
         - The first element of the duple can be either a list, or a singleton.
            * The singleton, or all elements of the list must be pygame key constants
              (http://www.pygame.org/docs/ref/key.html) or strings representing an entire key combo.
            * Key combo strings use the names of the keyboard keys as listed under "Common Name" on the
              previous website, and all keys that comprise a key combo are delimited by a '+' sign.
            * If the element is a list with multiple key combos in it, then the event will be fired off
              if and only if every key in one of the combos is pressed.
            * No key combo will trigger its event if there are additional keyboard modifiers (CTRL,
              SHIFT, ALT) pressed that are not part of the combo.  Thus, you can have both a
              Ctrl+S, and a Ctrl+Shift+S, and the Ctrl+Shift+S will never generate a false positive for
              the Ctrl+S binding.

         - The second element of the duple can be either a list, or a singleton.
            * The singleton or list elements represent input states.  These are changed by the game
              depending on whether the player is in the overworld, combat, or various dialog boxes.
              Only one of them needs to be the current input state for the event to fire.
            * There are a few predefined sets of related states.  These are MOVEMENT, DIALOG, and ALL
        '''
        self.bindings = {"QUIT": (["CTRL+q", "CTRL+x", "META+q", "META+x"], self.ALL),

            "UP": ([K_UP, K_KP8, "k", "SHIFT+up", "SHIFT+keypad 8", "SHIFT+k"], self.MOVEMENT),
            "DOWN": ([K_DOWN, K_KP2, "j", "SHIFT+down", "SHIFT+keypad 2", "SHIFT+j"], self.MOVEMENT),
            "LEFT": ([K_LEFT, K_KP4, "h", "SHIFT+left", "SHIFT+keypad 4", "SHIFT+h"], self.MOVEMENT),
            "RIGHT": ([K_RIGHT, K_KP6, "l", "SHIFT+right", "SHIFT+keypad 6", "SHIFT+l"], self.MOVEMENT),

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
            "TARGETCANCEL": ([K_KP5, "space", "escape"], "TARGET"),

            "SCROLLTOP": (["SHIFT+page up", "SHIFT+="], self.MOVEMENT),
            "SCROLLUP": (["page up", "="], self.MOVEMENT),
            "SCROLLDOWN": (["page down", "-"], self.MOVEMENT),
            "SCROLLBOTTOM": (["SHIFT+page down", "SHIFT+-"], self.MOVEMENT),

            "LEVELUPADVANCE": (["space", "a"], "LEVELUP"),

            "SHOPOPEN": ("F2", "OVERWORLD"),
            "SHOPTRANSACTION": ("a", "SHOP"),
            "SHOPCLOSE": (["space", "escape"], "SHOP"),

            "INVENTORYOPEN": ("i", "OVERWORLD"),
            "INVENTORYEQUIPMH": ("e", "INVENTORY"),
            "INVENTORYEQUIPMHALT": (["ALT+e", "ALT+e"], "INVENTORY"),
            "INVENTORYDROP": ("d", "INVENTORY"),
            "INVENTORYUNEQUIP": ("u", "INVENTORY"),
            "INVENTORYEQUIPOH": ("o", "INVENTORY"),
            "INVENTORYEQUIPOHALT": (["ALT+o", "ALT+o"], "INVENTORY"),
            "INVENTORYCLOSE": (["space", "i", "escape"], "INVENTORY"),

            "CHARSHEETOPEN": ("c", "OVERWORLD"),
            "CHARSHEETCLOSE": (["space", "escape"], "CHARSHEET"),
            "CHARSHEETABILITIES": ("a", "CHARSHEET"),
            "CHARSHEETSPELLS": ("s", "CHARSHEET"),
            "CHARSHEETPASSIVES": ("p", "CHARSHEET"),
            "CHARSHEETTRAITS": ("t", "CHARSHEET"),
            "CHARSHEETMAIN": ("c", "CHARSHEET"),

            "CONSUMABLEOPEN": ("i", "COMBAT"),
            "CONSUMABLEUSE": (["space", "a"], "CONSUMABLE"),

            "ABILITIESOPEN": ("space", "COMBAT"),
            "ABILITIESSELECT": (["space", "a"], "ABILITIES"),

            "SPELLSOPEN": ("b", "COMBAT"),
            "SPELLSSELECT": (["space", "a"], "SPELLS"),

            "SWITCHGEAR": ("o", "COMBAT"),
            "CYCLETARGETF": ("e", "COMBAT"),
            "CYCLETARGETB": ("w", "COMBAT"),
            "ACTIVATESELECTED": ("a", "COMBAT"),
            "ENDTURN": ("n", "COMBAT"),
            "SELECTSELF": ("s", "COMBAT"),
            "ANALYZETARGET": (".", "COMBAT"),

            "GETITEM": ("g", "OVERWORLD"),
            "BASHCHEST": ("b", "OVERWORLD"),
            "STARTLEVELUP": ("y", "OVERWORLD"),
            "STARTRESPEC": ("r", "OVERWORLD"),
            "HELPMENU": ("F1", "OVERWORLD"),

            "SHOWINPUTSTATE": ("backspace", "ALL"),
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
        return any(all((key in self.keystate or str(key).lower() in \
                [pygame.key.name(k) for k in self.keystate] or (key in self.mod_keys and \
                any(mod in self.keystate for mod in self.mod_keys[key]))) and \
                not any(key in self.keystate for k, v in self.mod_keys.iteritems() for key in v \
                if k not in (combo.split('+') if isinstance(combo, basestring) else [combo])) \
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