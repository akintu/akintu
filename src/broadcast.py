#!/usr/bin/python

import sys

# broadcast.py
# Author: Devin Ekins -- G. Cube
#
# Broadcasts are objects sent to players and monsters' Listener objects.
# They are used to simulate a multithreaded, event-driven environment which
# allows for special rules to impact the normal flow of game logic in combat.
#
# The various kinds of Broadcasts are used to include different messages which
# are listened for by specific listeners.  Different Broadcasts are capable of
# carrying different information as well.  
#
# Broadcasts are never actually sent over the network; all Broadcasting logic
# is handled on the server.


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

#
# Attack Broadcasts are used for melee/ranged attacks in various stages of
# completion.
#
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

#
# Spell Broadcasts are the magical analouge to AttackBroadcasts
#
class SpellBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.direction = argDict['direction']
        self.suffix = argDict['suffix']

        self.message = (self.direction + " Spell Cast")
        if self.suffix:
            self.message += " " + self.suffix

        self.spell = argDict['spell']

#
# Spell Resist Broadcasts are used only when a spell is fully resisted.
#
class SpellResistBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)
        
        self.message = "Outgoing Spell Resisted"
        self.spell = argDict['spell']
        
#
# Damage Broadcasts are sent every time damage is dealt to a monster or
# player.
#
class DamageBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.direction = argDict['direction']
        self.message = self.direction + " Damage"
        self.amount = argDict['amount']

#
# Status Broadcasts are sent whenever a status effect is applied to a 
# player or monster.
#
class StatusBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.message = "Incoming Status Applied"
        self.statusName = argDict['statusName']

#
# Whenever a resource (MP, AP, or HP) is changed, this broadcast is sent.
# Currently, AP changes are not broadcast for efficiency purposes and because
# no abilities in the game care about AP changes.
#
class ResourceLevelBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.resourceType = argDict['resource']
        self.resourceLevel = argDict['percent']
        self.message = "Player " + self.resourceType + " level changed"

#
# When an attack is dodged, a Dodge Broadcast is sent.
#
class DodgeBroadcast(Broadcast):
    def __init__(self):
        Broadcast.__init__(self)

        self.message = "Attack Dodged"

#
# At the start of a player or monster turn, this broadcast is sent.
#
class TurnBroadcast(Broadcast):
    def __init__(self, argDict):
        Broadcast.__init__(self)

        self.turn = argDict['turn']
        self.message = self.turn + " Turn Start"

#
# A trap broadcast is sent whenever a Trap is triggered, on either side.
#
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
        
#
# A trap chaos broadcast is only sent when an Anarchist playercharacter lays
# a trap directly on top of an enemy.
#
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
        
        

