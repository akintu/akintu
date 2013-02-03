'''
Class for communicating map sync actions
'''

def enum(**enums):
    return type('Enum', (), enums)

InventoryActions = enum(PICKUP = 1, PUTDOWN = 2)

class Command:
    def __init__(self):#, hash, location, action):
        pass
        # self.hash = index
        # self.location = location
        # self.action = action
        
class MovePlayer(Command):
    def __init__(self, playerport, dest):
        #super(MovePlayer,self).__init__()
        self.dest = dest
    
class InventoryAction(Command):
    def __init__(self, action, item_hash):
        self.action = action
        self.item_hash = item_hash
        
class AbilityAction(Command):
    def __init__(self, ability, targetLocation):
        self.ability = ability
        self.targetLocation = targetLocation