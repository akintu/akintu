'''
Class for communicating map sync actions
'''

def enum(**enums):
    return type('Enum', (), enums)

PersonActions = enum(CREATE = 1, MOVE = 2, REMOVE = 3)
InventoryActions = enum(PICKUP = 1, PUTDOWN = 2)


class Command:
    def __init__(self):
        pass

    def __repr__(self):
        result = "(" + self.__class__.__name__ + ": ["
        #for attr, val in self.__dict__.iteritems():
        #    result += attr + ": " + str(val) + " "
        result += ", ".join([attr + ": " + str(val) for attr, val in self.__dict__.iteritems()])
        result += "])"
        return result

class Person(Command):
    def __init__(self, action, index, location):
        self.action = action
        self.index = index
        self.location = location

class InventoryAction(Command):
    def __init__(self, action, item_hash):
        self.action = action
        self.item_hash = item_hash

class AbilityAction(Command):
    def __init__(self, ability, targetLocation):
        self.ability = ability
        self.targetLocation = targetLocation
