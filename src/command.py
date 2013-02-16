'''
Class for communicating map sync actions
'''


from const import enum

PersonActions = enum(CREATE = 1, MOVE = 2, REMOVE = 3, RUN = 4, STOP = 5)
CreatureTypes = enum(PLAYER = 1, MONSTER = 2)
InventoryActions = enum(PICKUP = 1, PUTDOWN = 2)


class Command:
    def __init__(self):
        pass

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join([attr + ": " + str(val) for attr, val in \
            self.__dict__.iteritems() if val != None]) + ")"

class Person(Command):
    def __init__(self, action, index, location = None, details = None):
        self.action = action
        self.index = index
        self.location = location
        self.details = details

class InventoryAction(Command):
    def __init__(self, action, item_hash):
        self.action = action
        self.item_hash = item_hash

class AbilityAction(Command):
    def __init__(self, ability, targetLocation):
        self.ability = ability
        self.targetLocation = targetLocation
