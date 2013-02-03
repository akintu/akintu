#!/usr/bin/python

import sys
import combat
import dice
import playercharacter

class Spell(en.Entity):

    allSpells = {
        {'Arcane Dart':
            {
            'tier' : 1,
            'school' : 'Mystic',
            'MPCost' : 2,
            'APCost' : 5',
            'range' : 8,
            'target' : 'hostile',
            'action' : _arcaneDart
            }
        },
        {'Arcane Ward':
            {
            'tier' : 1,
            'school' : 'Mystic',
            'MPCost' : 7,
            'APCost' : 9,
            'range' : 0,
            'target' : 'self',
            'action' : _arcaneWard
            }
        }
    }
            

    def __init__(self, name, owner):
        self.name = name
	    info = Spell.allSpells[name]
        self.tier = info['tier']
		self.school = info['school']
        self.MPCost = info['MPCost']
        self.APCost = info['APCost']
        self.range = info['range']
        self.targetType = info['target']
        self.action = info['action']
        self.cooldown = None
        if info['cooldown']:
            self.cooldown = info['cooldown']
        self.owner = owner
    
    def canCast(self, target):
        '''
        target: Person (later, Location?)
        '''
        
        # Check for modifications to spells costs here from listeners TODO
        mod = 0 # dummy code
        if self.owner.MP < self.MPCost - mod:
            return (False, "Insufficient Mana")
        if self.owner.AP < self.APCost - mod:
            return (False, "Insufficient AP")
        if self.targetType == "self" and owner is not target:
            return (False, "Spell is self-only, and the given target is not the caster.")
        if self.targetType == "hostile" and self.owner.team == target.team:
            return (False, "Cannot target own team with hostile spell.")
        if self.targetType == "friendly" and self.owner.team != target.team:
            return (False, "Cannot target hostile with beneficial spell.")
        # Do we need any check for AoE spells?
        if self.range < (Location.calcDistance(self.owner.location, target.location))
            return (False, "Target is out of range.")
        # TODO calcDistance is a placeholder function
        if self.name in self.owner.cooldownList:
            return (False, "Spell is on Cooldown.")
        return (True, "")
        
        
    def castSpell(self, target):
    ''' Casts the given spell on or around the given target Person (Location?)
        Performs a check if this is possible, but this is not where the canCast
        check should be made.  If caught here, it will raise an exception!'''
        if self.canCast(target)[0]:
            Combat.modifyResource(self.owner, "MP", -self.MPCost)
            Combat.modifyResource(self.owner, "AP", -self.APCost)
            if self.cooldown:
                Combat.applyCooldown(self.owner, self.name, self.cooldown)
            self.action(self, target)
        else:
            return 
            # TODO! Make this raise an exception rather than silently return.
            
    def _arcaneDart(self, target):
        hitType = Combat.calcHit(source, target, "Magical")
        damage = 0 - Combat.calcDamage(source, target, 
        Combat.modifyResource(target, "HP", 
        
        
   Combat.modifyresource(target, "HP", 
   0-Combat.calcDamage(source, target, min=2, max=4, element="Arcane", hitValue=hit, critical=1.2, scalesWith="Spellpower", scaleFactor=0.03))

        
        
        