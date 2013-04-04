#!/usr/bin/python

import sys

class Broadcast(object):
    def __init__(self):
        self.message = None

    def shout(self, target):
        interruptCodes = []
        for ear in target.listeners:
            code = ear.hear(self)
            if code:
                interruptCodes.append(code)
        if interruptCodes:
            return interruptCodes

class AttackBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.direction = argDict['direction']
        self.type = argDict['type']
        if 'inRange' in argDict:
            self.inRange = argDict['inRange']
        else:
            self.inRange = None
        if 'suffix' in argDict:
            self.suffix = argDict['suffix']
        else:
            self.suffix = None

        self.message = (self.direction + " " + self.type + " Attack ")
        if self.inRange:
            self.message += "in range " + str(self.inRange) + " "
        if self.suffix:
            self.message += self.suffix

        self.otherPerson = argDict['otherPerson']
        self.noCounter = False
        if 'noCounter' in argDict:
            self.noCounter = argDict['noCounter']


class SpellBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.direction = argDict['direction']
        self.suffix = argDict['suffix']

        self.message = (self.direction + " Spell Cast")
        if self.suffix:
            self.message += " " + self.suffix

        self.spell = argDict['spell']

class SpellResistBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)
        
        self.message = "Outgoing Spell Resisted"
        self.spell = argDict['spell']
        
class DamageBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.direction = argDict['direction']
        self.message = self.direction + " Damage"
        self.amount = argDict['amount']

class StatusBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.message = "Incoming Status Applied"
        self.statusName = argDict['statusName']

class ResourceLevelBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.resourceType = argDict['resource']
        self.resourceLevel = argDict['percent']
        self.message = "Player " + self.resourceType + " level changed"

class DodgeBroadcast(Broadcast):
    def __init__(self):
        Broadcast.__init__(self)

        self.message = "Attack Dodged"

class TurnBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.turn = argDict['turn']
        self.message = self.turn + " Turn Start"

class TrapBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)
        
        self.victim = argDict['victim']
        self.didHit = argDict['didHit']
        if self.didHit:
            self.hitString = " Hit By "
        else:
            self.hitString = " Avoided "
        if "suffix" in argDict:
            self.suffix = " " + argDict['suffix']
        else:
            self.suffix = ""
            
        if "trap" in argDict:
            self.trap = argDict['trap']
        else:
            self.trap = None
        self.message = self.victim + self.hitString + "Trap" + self.suffix
        
class TrapChaosBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)
        
        if "other" in argDict:
            self.other = argDict['other']
        else:
            self.other = None
        if "suffix" in argDict:
            self.suffix = " " + argDict['suffix']
        else:
            self.suffix = ""
            
        self.message = "Trap Chaos" + self.suffix
        
        

