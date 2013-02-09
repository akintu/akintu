#!/usr/bin/python

import sys
from dice import *
from combat import *

class OnHitEffect(object):
    def __init__(self, count, function, elementalDamageType=None):
        self.count = count
        self.function = function
        self.name = str(function).replace("apply", "")
        if elementalDamageType:
            self.name += " " + elementalDamageType
        self.element = elementalDamageType
        if self.elementalDamageType in ['Bludgeoning', 'Slashing', 'Piercing']:
            print "Invalid physical elemental damage type: " + self.elementalDamageType + "."
        
    def apply(self, source, target):
        self.function(self.count, source, target)
        
    def applyElementalDamage(self, magnitude, source, target):
        damage = 0
        if self.elementalDamageType == "Poison":
            damage = magnitude
        elif self.elementalDamageType == "Divine":
            damage = Dice.roll(magnitude, magnitude * 3)
        else:
            damage = Dice.roll(magnitude, magnitude * 2)
        return [self.elementalDamageType, damage]
        
    def applyAcidic(self, magnitude, source, target):
        # Magnitude determines chance.
        chance = magnitude
        if Dice.rollBeneath(chance):
            duration = 4
            Combat.addStatus(target, "Acidic Magic Weapon", duration)
        return None
        
    def applyEvil(self, magnitude, source, target):        
        # Magnitude determines damage.
        HPLoss = round(source.totalHP * 0.08)
        if HPLoss >= source.HP:
            HPLoss = source.HP - 1
        Combat.modifyResource(source, "HP", -HPLoss)
        damage = magnitude * 12
        return ["Shadow", damage]
        
    def applyHoly(self, magnitude, source, target):
        # Magnitude determines chance.
        chance = magnitude
        duration = -1 # Does not end.
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Holy Magic Weapon", duration)
            if Dice.rollBeneath(50):
                Combat.addStatus(target, "Stun", 1)
            return ["Divine", 20]
        else:
            return None
            
    def applyIgnite(self, magnitude, source, target):
        # magnitude determines damage.
        duration = 3
        damageMag = Dice.roll(1, 5) * magnitude
        Combat.addStatus(target, "Ignite Magic Weapon", duration, damageMag)
        return None
        
    def applySlowing(self, magnitude, source, target):
        # Magnitude determines chance.
        duration = 2
        chance = magnitude
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Slowing Magic Weapon", duration)
        return None
        
    def applySpellhunger(self, magnitude, source, target):
        # Magnitude determines MP destroyed.
        MPLoss = magnitude
        target.MP -= MPLoss
        return None
        
    def applyStunning(self, magnitude, source, target):
        # Magnitude determines chance.
        chance = max(20, magnitude)
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Stun", 1)
        return None
        
    def applyMinorBleeding(self, magnitude, source, target):
        # Magnitude increases chance.
        chance = magnitude
        duration = 3
        magnitude = 5
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Bleeding", duration, magnitude, overwrite=False)
        return None
        
    def applyModerateBleeding(self, magnitude, source, target):
        # Magnitude increases chance.
        chance = magnitude
        duration = 3
        magnitude = 10
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Bleeding", duration, magnitude, overwrite=False)
        return None
        
    def applySeriousBleeding(self, magnitude, source, target):
        # Magnitude increases chance.
        chance = magnitude
        duration = 3
        magnitude = 15
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Bleeding", duration, magnitude, overwrite=False)
        # TODO: Make different sources of bleeding stack.
        return None
        
    def applyHealthSteal(self, magnitude, source, target):
        # Magnitude increases amount.
        amount = magnitude
        Combat.healTarget(source, source, min(target.HP, amount))
        return ["Divine", amount]
        
    def applyManaSteal(self, magnitude, source, target):
        amount = magnitude
        restoration = min(amount, target.MP)
        Combat.modifyResource(target, "MP", -amount)
        Combat.modifyResource(source, "MP", restoration)
        return None
        
    def applyToxic(self, magnitude, source, target):
        pRating = magnitude + 5
        damage = Dice.roll(2,4)
        duration = 5
        hitType = Combat.calcHit(source, target, "Poison", rating=pRating)
        if hitType != "Miss":
            Combat.addStatus(target, "Toxic Magic Weapon", duration, damage)
        return None
    
    def applyWeakeningFire(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Fire Magic Weapon", duration)
        return None
        
    def applyWeakeningCold(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Cold Magic Weapon", duration)
        return None        
        
    def applyWeakeningElectric(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Electric Magic Weapon", duration)
        return None
        
    def applyWeakeningPoison(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Poison Magic Weapon", duration)
        return None
        
    def applyWeakeningDivine(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Divine Magic Weapon", duration)
        return None
        
    def applyWeakeningShadow(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Shadow Magic Weapon", duration)
        return None
        
    def applyWeakeningArcane(self, magnitude, source, target):
        chance = magnitude
        duration = 3
        if Dice.rollBeneath(chance):
            Combat.addStatus(target, "Weakening Arcane Magic Weapon", duration)
        return None
        
    def applyMageHunting(self, magnitude, source, target):
        success = Dice.rollPreset(source, target, "Frequent")
        if success and target.MP > 0:
            duration = 3
            Combat.addStatus(target, "Hunted", duration, magnitude)
        return None

    def applyFlatElementalDamage(self, magnitude, source, target):
        return [self.element, magnitude]
    
    
    
    
    