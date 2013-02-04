#!/usr/bin/python

import sys

class Broadcast(object):
    def __init__(self):
        self.message = None
    
    def shout(self, target):
        for ear in target.listeners:
            ear.hear(self)
    
class AttackBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)
        
        self.direction = argDict['direction']
        self.type = argDict['type']
        self.inRange = argDict['inRange']
        self.suffix = argDict['suffix']
        
        self.message = (self.direction + " " + self.type + " Attack ")
        if self.inRange:
            self.message += "in range " + str(self.inRange) + " "
        if self.suffix:
            self.message += self.suffix
            
        self.otherPerson = argDict['otherPerson']
    
class SpellBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)
        
        self.direction = argDict['direction']
        self.suffix = argDict['suffix']

        self.message = (self.direction + " Spell Cast")
        if self.suffix:
            self.message += " " + self.suffix
        
        self.spell = argDict['spell']
        