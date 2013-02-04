#!/usr/bin/python

import sys
import combat
import dice

class Spell(object):

    
    
 

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
        if self.range < (Location.calcDistance(self.owner.location, target.location)):
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
            spellSuccess = Dice.rollSuccess(100 - self.owner.statusSpellFailureChance)
            if spellSuccess:
                self._shoutSpellCast(self.owner, target)
                self.action(self, target)
                if self.targetType != "friendly" and self.targetType != "self":
                    Combat.removeStealth(self.owner)
                self._shoutSpellCastComplete(self.owner, target)
            else:
                return
                # TODO, notify of spell failure?
        else:
            return 
            # TODO! Make this raise an exception rather than silently return.
            
    def _arcaneDart(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = (Combat.calcDamage(source, target, min=2, max=4, element="Arcane", 
                                    hitValue=hitType, critical=1.2, scalesWith="Spellpower", scaleFactor=0.03)) 
        Combat.lowerHP(target, damage)
        
    def _arcaneWard(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 3, 0.1, cap=6)
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.01)
        Combat.addStatus(target, self.name, duration, magnitude)
        
    def _mysticShield(self, target):
        source = self.owner
        duration = 5
        magnitude = Dice.scale(source.totalSpellpower, 10, 0.06)
        Combat.addStatus(target, self.name, duration, magnitude)        
    
    def _flickerOfLife(self, target):
        source = self.owner
        magnitude = Dice.scale(source.totalSpellpower, Dice.roll(10,20), 0.02)
        Combat.healTarget(source, target, magnitude)

    def _stoneGuard(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 4, 0.05, cap=6)
        magnitude = Dice.scale(source.totalSpellpower, 10, 0.008)
        Combat.addStatus(target, self.name, duration, magnitude)
        
    def _singe(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = (Combat.calcDamage(source, target, min=2, max=9, element="Fire",
                                    hitValue=hitType, critical=1.2, partial=0.5,
                                    scalesWith="Spellpower", scaleFactor=0.05))
        Combat.lowerHP(target, damage)
        
    def _chill(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, min=1, max=12, element="Cold",
                                   hitValue=hitType, scalesWith="Spellpower",
                                   scaleFactor=0.01)
        duration = 2
        chance = Dice.rollPresetChance(source, target, "Frequent")
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.012),
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType, chance=chance)
        
    def _shock(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, min=15, max=22, element="Electric", hitValue=hitType,
                                   scalesWith="Spellpower", scaleFactor=0.014)
        Combat.lowerHP(target, damage)
        
    def _suggestLaziness(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        pass
        # TODO: this status requires AI -- we don't have that yet.

    def _stutter(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        duration = 5
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.02)
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)
        
    def _cloudVision(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        duration = Dice.scale(source.totalSpellpower, 5, 0.02)
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.012)
        if hitType == "Partially Resisted":
            magnitude /= 2
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)
        
    def _haunt(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, min=13, max=20, element="Shadow", hitValue=hitType,
                                   scalesWith="Spellpower", scaleFactor=0.01)
        Combat.lowerHP(target, damage)
        
        duration = Dice.scale(source.totalSpellpower, 3, 0.02, cap=4)
        magnitude = round(Dice.roll(2,8) * (1 + source.totalSpellpower * 0.005))
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)
        # TODO: Deal with the fact that this damage is not being rolled every turn...
        
    def _zoneOfSilence(self, target):
        pass
        # TODO!!
        
    def _blurry(self, target):
        source = self.owner
        duration = 1
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.02)
        Combat.addStatus(target, self.name, duration, magnitude)

    def _weaponEnhance(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 3, 0.03, cap=7)
        magnitudeA = Dice.scale(source.totalSpellpower, 3, 0.07) # Accuracy/Penetration
        magnitudeB = Dice.scale(source.totalSpellpower, 5, 0.05) # Crit mag
        magnitudeC = Dice.scale(source.totalSpellpower, 1, 0.035) # Crit chance
        Combat.addStatus(target, "Weapon Enhance Striking", duration, magnitudeA)
        Combat.addStatus(target, "Weapon Enhance Punishing", duration, magnitudeB)
        Combat.addStatus(target, "Weapon Enhance Precision", duration, magnitudeC)
        
    def _flamingWeapon(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 3, 0.03, cap=7)
        magnitude = round(Dice.roll(1,8) * (1 + source.totalSpellpower * 0.01))
        Combat.addStatus(target, self.name, duration, magnitude)
        # TODO: Deal with the fact that this damage is not being rolled every turn...
    
    

    
    allSpells = {
        'Arcane Dart':
        {
        'tier' : 1,
        'school' : 'Mystic',
        'MPCost' : 2,
        'APCost' : 5,
        'range' : 8,
        'target' : 'hostile',
        'action' : _arcaneDart,
        'cooldown' : None
        },
        
        'Arcane Ward':
        {
        'tier' : 1,
        'school' : 'Mystic',
        'MPCost' : 7,
        'APCost' : 9,
        'range' : 0,
        'target' : 'self',
        'action' : _arcaneWard,
        'cooldown' : None
        },
        
        'Mystic Shield':
        {
        'tier' : 1,
        'school' : 'Mystic',
        'MPCost' : 15,
        'APCost' : 12,
        'range' : 0,
        'target' : 'self',
        'action' : _mysticShield,
        'cooldown' : 4
        },
        
        'Flicker of Life':
        {
        'tier' : 1,
        'school' : 'Natural',
        'MPCost' : 15,
        'APCost' : 9,
        'range' : 6,
        'target' : 'friendly',
        'action' : _flickerOfLife,
        'cooldown' : None
        },
        
        'Stone Guard':
        {
        'tier' : 1,
        'school' : 'Natural',
        'MPCost' : 15,
        'APCost' : 9,
        'range' : 4,
        'target' : 'friendly',
        'action' : _stoneGuard,
        'cooldown' : None
        },
        
        'Singe':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 6,
        'APCost' : 7,
        'range' : 7,
        'target' : 'hostile',
        'action' : _singe,
        'cooldown' : None
        },
        
        'Chill':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 10,
        'APCost' : 6,
        'range' : 6,
        'target' : 'hostile',
        'action' : _chill,
        'cooldown' : None
        },
        
        'Shock':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 13,
        'APCost' : 7,
        'range' : 2,
        'target' : 'hostile',
        'action' : _shock,
        'cooldown' : 1
        },
        
        'Suggest Laziness':
        {
        'tier' : 1,
        'school' : 'Mental',
        'MPCost' : 5,
        'APCost' : 5,
        'range' : 12,
        'target' : 'hostile',
        'action' : _suggestLaziness,
        'cooldown' : None
        },
        
        'Stutter':
        {
        'tier' : 1,
        'school' : 'Mental',
        'MPCost' : 14,
        'APCost' : 9,
        'range' : 6,
        'target' : 'hostile',
        'action' : _stutter,
        'cooldown' : None
        },
        
        'Cloud Vision':
        {
        'tier' : 1,
        'school' : 'Bane',
        'MPCost' : 9,
        'APCost' : 9,
        'range' : 6,
        'target' : 'hostile',
        'action' : _cloudVision,
        'cooldown' : None
        },
        
        'Haunt':
        {
        'tier' : 1,
        'school' : 'Bane',
        'MPCost' : 20,
        'APCost' : 11,
        'range' : 5,
        'target' : 'hostile',
        'action' : _haunt,
        'cooldown' : 3
        },
        
        'Zone of Silence':
        {
        'tier' : 1,
        'school' : 'Illusion',
        'MPCost' : 20,
        'APCost' : 6,
        'range' : 3,
        'target' : 'terrain',
        'action' : _zoneOfSilence,
        'cooldown' : None
        },
    
        'Blurry':
        {
        'tier' : 1,
        'school' : 'Illusion',
        'MPCost' : 6,
        'APCost' : 3,
        'range' : 0,
        'target' : 'self',
        'action' : _blurry,
        'cooldown' : None
        },
        
        'Weapon Enhance':
        {
        'tier' : 1,
        'school' : 'Enchantment',
        'MPCost' : 9,
        'APCost' : 5,
        'range' : 3,
        'target' : 'friendly',
        'action' : _weaponEnhance,
        'cooldown' : None
        },
        
        'Flaming Weapon':
        {
        'tier' : 1,
        'school' : 'Enchantment',
        'MPCost' : 12,
        'APCost' : 8,
        'range' : 3,
        'target' : 'friendly',
        'action' : _flamingWeapon,
        'cooldown' : None
        }
        
        
    }      

    def _shoutSpellCast(self, source, target):
        s = self
        direction = None
        double = None
        hearer = None
        if source.team == "Players" and target.team != "Players":
            direction = "Outgoing"
            hearer = source
        elif source.team == "Monsters" and target.team == "Players":
            direction = "Incoming"
            hearer = target
        elif source.team == "Players" and target.team == "Players":
            direction = "Outgoing"
            double = "Incoming"
            hearer = source
        bundle = {'direction' : direction, 'suffix' : None, 'spell' : s}
        bc = broadcast.SpellBroadcast(bundle)
        bc.shout(hearer)
        if double:
            bundle = {'direction' : double, 'suffix' : None, 'spell' : s)
            bc = broadcast.SpellBroadcast(bundle)
            hearer = source
            bc.shout(hearer)
        
    def _shoutSpellCastComplete(self, source, target):
        s = self
        direction = None
        double = None
        hearer = None
        if source.team == "Players" and target.team != "Players":
            direction = "Outgoing"
            hearer = source
        elif source.team == "Monsters" and target.team == "Players":
            direction = "Incoming"
            hearer = target
        elif source.team == "Players" and target.team == "Players":
            direction = "Outgoing"
            double = "Incoming"
            hearer = source
        bundle = {'direction' : direction, 'suffix' : 'Complete', 'spell' : s}
        bc = broadcast.SpellBroadcast(bundle)
        bc.shout(hearer)
        if double:
            bundle = {'direction' : double, 'suffix' : 'Complete', 'spell' : s)
            bc = broadcast.SpellBroadcast(bundle)
            hearer = source
            bc.shout(hearer)    
    