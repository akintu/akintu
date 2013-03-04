'''
Class for communicating map sync actions
'''

from const import enum

PersonActions = enum(CREATE = 1, MOVE = 2, REMOVE = 3, RUN = 4, STOP = 5)
InventoryActions = enum(PICKUP = 1, PUTDOWN = 2)
UpdateProperties = enum(HP = 1, MP = 2, AP = 3, COMBAT = 4, TEXT = 5)
AbilityActions = enum(ATTACK = 1, END_TURN = 2)

class Command:
    def __init__(self):
        self.id = None

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join([attr + ": " + str(val) for attr, val in \
            self.__dict__.iteritems() if val != None]) + ")"

class Person(Command):
    def __init__(self, action, id, location=None, details=None):
        self.action = action
        self.id = id
        self.location = location
        self.details = details

class Update(Command):
    def __init__(self, id, property, value, location=None, details=None):
        self.id = id
        self.property = property
        self.value = value
        self.location = location
        self.details = details

class InventoryAction(Command):
    def __init__(self, action, item_hash):
        self.action = action
        self.item_hash = item_hash

class AbilityAction(Command):
    def __init__(self, ability, sourceId, targetId):
        self.ability = ability
        self.id = sourceId
        self.targetId = targetId
