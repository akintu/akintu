'''
Class for communicating map sync actions
'''

def enum(**enums):
    return type('Enum', (), enums)

InventoryActions = enum(PICKUP = 1, PUTDOWN = 2)

class Command:
    def __init__(self):#, hash, location, action):
        pass
        
    def __repr__(self):
        result = "(" + self.__class__.__name__ + ": ["
        for attr, val in self.__dict__.iteritems():
            result += attr + ": " + str(val) + " "
        result += "])"
        return result
        
class CreatePerson(Command):
    def __init__(self, index, location):
        self.index = index
        self.location = location
        
class MovePerson(Command):
    def __init__(self, index, dest):
        self.index = index
        self.dest = dest
        
class RemovePerson(Command):
    def __init__(self, index):
        self.index = index
        
class UpdateIndex(Command):
    def __init__(self, index):
        self.index = index
    
class InventoryAction(Command):
    def __init__(self, action, item_hash):
        self.action = action
        self.item_hash = item_hash
        
class AbilityAction(Command):
    def __init__(self, ability, targetLocation):
        self.ability = ability
        self.targetLocation = targetLocation
