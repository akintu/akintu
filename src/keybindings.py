'''
Keybindings utility module
'''

from pygame.locals import *
import collections
import pygame
import os

class Keystate():
    def __init__(self):
        self.keystate = []
        self.typematicRate = 0.1
        self.keyTime = 0
        self.newBinding = None

        self.inputState = "OVERWORLD"

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

        self.ALL = ["OVERWORLD", "LEVELUP", "INVENTORY", "CONSUMABLE", "TARGET", "SHOP", "ABILITIES", \
                "SPELLS", "COMBAT", "CHARSHEET", "SAVEMENU", "HELPMENU", "DEATH", "BINDINGS", "COMBATSTATUS"]
        self.MOVEMENT = ["OVERWORLD", "COMBAT"]
        self.DIALOG = ["LEVELUP", "INVENTORY", "CONSUMABLE", "SHOP", "ABILITIES", "SPELLS", \
                "CHARSHEET", "SAVEMENU", "HELPMENU", "DEATH", "BINDINGS", "COMBATSTATUS"]

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

        b = collections.OrderedDict()
        self.bindings = b

        b["QUIT"] = (["escape", "CTRL+q", "CTRL+x", "META+q", "META+x"], "OVERWORLD")
        b["SAVEMENUACCEPT"] = (["a", "space", "return", "keypad enter"], "SAVEMENU")
        b["SAVEMENUCANCEL"] = ("escape", "SAVEMENU")
        b["TOGGLEFULLSCREEN"] = (["ALT+return", "ALT+keypad enter"], "ALL")

        b["DEATHCONTINUE"] = (["a", "space", "return", "keypad enter", "escape"], "DEATH")

        b["FORCEQUIT"] = (["CTRL+SHIFT+q", "CTRL+SHIFT+x", "META+q+x"], self.ALL)

        b["UP"] = ([K_UP, K_KP8, "k", "SHIFT+up", "SHIFT+[8]", "SHIFT+k"], self.MOVEMENT)
        b["DOWN"] = ([K_DOWN, K_KP2, "j", "SHIFT+down", "SHIFT+[2]", "SHIFT+j"], self.MOVEMENT)
        b["LEFT"] = ([K_LEFT, K_KP4, "h", "SHIFT+left", "SHIFT+[4]", "SHIFT+h"], self.MOVEMENT)
        b["RIGHT"] = ([K_RIGHT, K_KP6, "l", "SHIFT+right", "SHIFT+[6]", "SHIFT+l"], self.MOVEMENT)

        b["DIALOGUP"] = ([K_UP, K_KP8, "k"], self.DIALOG)
        b["DIALOGDOWN"] = ([K_DOWN, K_KP2, "j"], self.DIALOG)
        b["DIALOGLEFT"] = ([K_LEFT, K_KP4, "h"], self.DIALOG)
        b["DIALOGRIGHT"] = ([K_RIGHT, K_KP6, "l"], self.DIALOG)

        b["HELPMENUOPEN"] = (["F1", "SHIFT+/"], self.MOVEMENT)
        b["HELPMENUACCEPT"] = (["a", "space", "return", "keypad enter"], "HELPMENU")
        b["HELPMENUTOP"] = ("escape", "HELPMENU")
        b["HELPMENUNEXT"] = ("n", "HELPMENU")
        b["HELPMENUPREVIOUS"] = ("b", "HELPMENU")

        b["TARGETUP"] = ([K_UP, K_KP8, "k"], "TARGET")
        b["TARGETDOWN"] = ([K_DOWN, K_KP2, "j"], "TARGET")
        b["TARGETLEFT"] = ([K_LEFT, K_KP4, "h"], "TARGET")
        b["TARGETRIGHT"] = ([K_RIGHT, K_KP6, "l"], "TARGET")
        b["TARGETUPLEFT"] = ([K_KP7, "y"], "TARGET")
        b["TARGETUPRIGHT"] = ([K_KP9, "u"], "TARGET")
        b["TARGETDOWNLEFT"] = ([K_KP1, "b"], "TARGET")
        b["TARGETDOWNRIGHT"] = ([K_KP3, "n"], "TARGET")
        b["TARGETACCEPT"] = (["a", "space", "return", "keypad enter"], "TARGET")
        b["TARGETCANCEL"] = ([K_KP5, "escape"], "TARGET")

        b["SCROLLTOP"] = (["SHIFT+page up", "SHIFT+="], self.MOVEMENT)
        b["SCROLLUP"] = (["page up", "="], self.MOVEMENT)
        b["SCROLLDOWN"] = (["page down", "-"], self.MOVEMENT)
        b["SCROLLBOTTOM"] = (["SHIFT+page down", "SHIFT+-"], self.MOVEMENT)

        b["LEVELUPADVANCE"] = (["space", "a", "return", "keypad enter"], "LEVELUP")

        # b["SHOPOPEN"] = ("F2", "OVERWORLD")
        b["SHOPTRANSACTION"] = (["a", "return", "keypad enter"], "SHOP")
        b["SHOPCLOSE"] = (["space", "escape"], "SHOP")

        b["INVENTORYOPEN"] = ("i", "OVERWORLD")
        b["INVENTORYEQUIPMH"] = ("e", "INVENTORY")
        b["INVENTORYEQUIPMHALT"] = ("ALT+e", "INVENTORY")
        b["INVENTORYDROP"] = ("d", "INVENTORY")
        b["INVENTORYUNEQUIP"] = ("u", "INVENTORY")
        b["INVENTORYEQUIPOH"] = ("o", "INVENTORY")
        b["INVENTORYEQUIPOHALT"] = ("ALT+o", "INVENTORY")
        b["INVENTORYCLOSE"] = (["space", "i", "escape"], "INVENTORY")

        b["CHARSHEETOPEN"] = ("c", self.MOVEMENT)
        b["CHARSHEETCLOSE"] = (["space", "escape"], "CHARSHEET")
        b["CHARSHEETABILITIES"] = ("a", "CHARSHEET")
        b["CHARSHEETSPELLS"] = ("s", "CHARSHEET")
        b["CHARSHEETPASSIVES"] = ("p", "CHARSHEET")
        b["CHARSHEETTRAITS"] = ("t", "CHARSHEET")
        b["CHARSHEETMAIN"] = ("c", "CHARSHEET")

        b["BINDINGSOPEN"] = ("CTRL+k", self.MOVEMENT)
        b["BINDINGSCLOSE"] = (["space", "escape"], "BINDINGS")
        b["BINDINGSADD"] = (["a", "insert"], "BINDINGS")
        b["BINDINGSDELETE"] = (["d", "delete"], "BINDINGS")

        b["CONSUMABLEOPEN"] = ("i", "COMBAT")
        b["CONSUMABLEUSE"] = (["space", "a", "return", "keypad enter"], "CONSUMABLE")
        b["CONSUMABLECANCEL"] = ("escape", "CONSUMABLE")

        b["ABILITIESOPEN"] = ("space", "COMBAT")
        b["ABILITIESSELECT"] = (["space", "a", "return", "keypad enter"], "ABILITIES")

        b["SPELLSOPEN"] = ("b", "COMBAT")
        b["SPELLSSELECT"] = (["space", "a", "return", "keypad enter"], "SPELLS")

        b["SWITCHGEAR"] = ("o", "COMBAT")
        b["CYCLETARGETF"] = ("e", "COMBAT")
        b["CYCLETARGETB"] = ("w", "COMBAT")
        b["ACTIVATESELECTED"] = ("a", "COMBAT")
        b["ENDTURN"] = ("n", "COMBAT")
        b["SELECTSELF"] = ("s", "COMBAT")
        b["ANALYZETARGET"] = (".", "COMBAT")
        b["DISPLAYCOMBATSTATUS"] = ("F3", "COMBAT")
        b["CLOSECOMBATSTATUS"] = ("escape", "COMBATSTATUS")

        b["GETITEM"] = ("g", "OVERWORLD")
        b["BASHCHEST"] = ("b", "OVERWORLD")
        b["STARTLEVELUP"] = ("y", "OVERWORLD")
        b["CHEATLEVELUP"] = ("CTRL+SHIFT+y", "OVERWORLD")
        b["STARTRESPEC"] = ("r", "OVERWORLD")
        b["CHEAT CODE"] = ("[+]", self.MOVEMENT)

        b["SHOWINPUTSTATE"] = ("CTRL+SHIFT+k", self.MOVEMENT)
        b["SHOWPANEPIDS"] = ("CTRL+SHIFT+p", self.MOVEMENT)
        b["SHOWPATHS"] = ("CTRL+SHIFT+\\", self.MOVEMENT)

        self.load_keys()

    def __call__(self, e=None):
        '''
        Calls to the keystate object update the currently pressed key list, and then match them to the
            list of keybindings to find and return any events that should be handled.
        If a valid new key combination is being pressed, that combination is stored for later
            event association.
        The keystate object is called and an event e passed in from pygame via game.py
        It is also called via the direction method, in order to ascertain direction events
        '''
        if e:
#            if hasattr(e, 'unicode'):
#                print "UNICODE: ", e.unicode
            if e.type == KEYUP and e.key in self.keystate:
                self.keystate.remove(e.key)
            if e.type == KEYDOWN and e.key not in self.keystate:
                self.keystate.append(e.key)
#            print self.keystate

            if self.inputState == "BINDINGSADD" and \
                    any(all(key not in keylist for keylist in self.mod_keys.values()) \
                    for key in self.keystate):
                self.newBinding = self.keystate[:]
                return "BINDINGSADDED"

        events = [k for k, v in self.bindings.iteritems() if v[0] in self and \
                (self.inputState == v[1] or self.inputState in v[1] or v[1] == "ALL")]
        return events[0] if events else None

    def __contains__(self, combolist):
        '''
        This magic method does the heavy lifting to see if a keybinding is constituted by the current
        set of keys being held down.
        A key will still match if there are other keys being held down, unless one of the other keys
        is a modifier (CTRL, SHIFT, ALT, META).  Modifiers must match exactly with no extras being
        pressed.

        I'm sorry it's so convoluted -- it was simple when I started it!  At this point, it would take
        me a lot more time to unravel this comprehension than I have, and it seems to work correctly
        '''
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
        '''
        Takes a class of input states (state) and checks to see if:
            * The inputState variable is in the class of states (e.g., "OVERWORLD" is in the
                "MOVEMENT" class of input states)
            * A direction key is held down
        If both of those are true, it returns the direction indicated as an integer in [2, 4, 6, 8]
        '''
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

    def get_key(self, event, shortest=True, all=False):
        '''
        Takes an event as a string, and returns the first, shortest, or all keybindings
        that will trigger that event.
        '''
        if event not in self.bindings:
            return False
        combos = self.bindings[event][0]
        if not isinstance(combos, list):
            combos = [combos]
        combos = [pygame.key.name(k) if isinstance(k, int) else k for k in combos]

        if shortest:
            combos = sorted(combos, key=lambda combo: len(combo.split('+')) * 100 + len(combo))

        if all:
            return combos
        else:
            return combos[0]

    def get_states(self, event):
        '''
        Returns a list of inputStates in which the specified event can trigger
        '''
        return self.bindings[event][1] if isinstance(self.bindings[event][1], list) else \
                [self.bindings[event][1]]

    def add_binding(self, event):
        '''
        Takes an event as a string, and then associates the binding stored in the new binding buffer
        with the event.
        '''
        keys = self.get_key(event, all=True)
        for i, key in enumerate(self.newBinding):
            if any(key in keylist for keylist in self.mod_keys.values()):
                self.newBinding[i] = [k for k, v in self.mod_keys.iteritems() if key in v][0]
        keys.append("+".join([pygame.key.name(key) if isinstance(key, int) else key for key in self.newBinding]))
        self.newBinding = None
        self.bindings[event] = (keys, self.bindings[event][1])
        self.save_keys()

    def delete_binding(self, event, combo):
        '''
        Deletes the specific keybinding 'combo' from the binding for the specified event.
        '''
        keys = self.get_key(event, all=True)
        del keys[combo]
        self.bindings[event] = (keys, self.bindings[event][1])
        self.save_keys()

    def save_keys(self):
        '''
        Saves all keybindings to a text file for long-term storage
        '''
        file = os.path.join('res', 'keybindings.txt')
        pass

    def load_keys(self):
        '''
        After processing the bindings data structure above, overwrites actual key binding values
        with those from the key file.
        '''
        pass

keystate = Keystate()