'''
Class for communicating map sync actions
'''

def enum(**enums):
    return type('Enum', (), enums)

InventoryActions = enum(PICKUP = 1, PUTDOWN = 2)

class Command:
    def __init__(self, hash, location, action):
        self.hash = hash
        self.location = location
        self.action = action
        
class Action(object):
    pass
    
class MoveAction(Action):
    def __init__(self, dest):
        self.dest = dest
        
class InventoryAction(Action):
    def __init__(self, action, item_hash):
        self.action = action
        self.item_hash = item_hash
        
class AbilityAction(Action):
    def __init__(self, ability, targetLocation):
        self.ability = ability
        self.targetLocation = targetLocation