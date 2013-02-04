#!/usr/bin/python

import sys
import combat
import dice

class Ability(object):
    
    allAbilities = {
        {'Mighty Blow':
            {
            'level' : 1,
            'class' : 'Fighter',
            'HPCost' : 0,
            'APCost' : 9',
            'range' : 1,
            'target' : 'hostile',
            'action' : _mightyBlow,
            'cooldown' : None,
            'checkFunction' : _mightyBlowCheck
            'breakStealth' : 100
            }
        },
        {'Brace':
            {
            'level' : 1,
            'class' : 'Fighter',
            'HPCost' : 0,
            'APCost' : 2,
            'range' : 0,
            'target' : 'self',
            'action' : _brace,
            'cooldown' : None,
            'checkFunction' : None
            'breakStealth' : 100
            }
        },
        {'Dash':
            {
            'level' : 1,
            'class' : 'Fighter',
            'HPCost' : 0,
            'APCost' : 2,
            'range' : 0,
            'target' : 'self',
            'action' : _dash,
            'cooldown' : None,  
            'checkFunction' : None
            'breakStealth' : 100            
            }
        }
    }
    
    def __init__(self, name, owner):
        self.name = name
	    info = Ability.allAbilities[name]
        self.level = info['level']
        self.HPCost = info['HPCost']
        self.APCost = info['APCost']
        self.range = info['range']
        self.targetType = info['target']
        self.action = info['action']
        self.cooldown = info['cooldown']
        self.checkFunction = info['checkFunction']
        self.breakStealth = info['breakStealth']
        self.owner = owner
        
        
        
    def canUse(self, target):
        '''
        target: Person (later, Location?)
        '''
        
        # Check for modifications to ability costs here from listeners TODO
        mod = 0 # dummy code
        if self.owner.AP < self.APCost - mod:
            return (False, "Insufficient AP")
            
        messageCode = (True, "")
        if self.checkFunction:
            messageCode = self.checkFunction(self.owner, target)
        if not messageCode[0]:
            return messageCode
            
        if self.targetType == "self" and owner is not target:
            return (False, "Ability is self-only, and the given target is not the user.")
        if self.targetType == "hostile" and self.owner.team == target.team:
            return (False, "Cannot target own team with hostile ability.")
        if self.targetType == "friendly" and self.owner.team != target.team:
            return (False, "Cannot target hostile with beneficial ability.")
        # Do we need any check for AoE spells?
        if self.range < (Location.calcDistance(self.owner.location, target.location))
            return (False, "Target is out of range.")
        # TODO calcDistance is a placeholder function
        if self.name in self.owner.cooldownList:
            return (False, "Ability is on Cooldown.")
        return (True, "")
        
        
     def use(self, target):
        ''' Uses the given ability on or around the given target Person (Location?)
        Performs a check if this is possible, but this is not where the canUse
        check should be made.  If caught here, it will raise an exception!'''
        if self.canUse(target)[0]:
            Combat.modifyResource(self.owner, "HP", -self.HPCost)
            Combat.modifyResource(self.owner, "AP", -self.APCost)
            if self.cooldown:
                Combat.applyCooldown(self.owner, self.name, self.cooldown)
            self.action(self, target)
            if Dice.rollBeneath(self.breakStealth):
                Combat.removeStealth(self.owner)
        else:
            return 
            # TODO! Make this raise an exception rather than silently return.
        
    
    def _mightyBlow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-5)
        Combat.basicAttack(source, target, hit, forceMod=1.5)
        
    def _mightyBlowCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")
        
    def _brace(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)
        Combat.endTurn(source)
        
    def _dash(self, target):
        newCost = 0
        numberOfMoves = 1
        Combat.setMovementCost(target, newCost, numberOfMoves)
        
        