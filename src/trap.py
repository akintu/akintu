#!/usr/bin/python

import sys
from dice import *
from combat import *
import entity as e

class Trap(e.Entity):
    
    
    def __init__(self, name, level=None, player=None, charges=1, location=None, image=None):
        """Constructor for Traps.  Should only be used with
        keyword arguments."""
        e.Entity.__init__(self, location=location, image=image, passable=True)
        if player:
            self.name = name
            trapDict = Trap.playerTraps[name]
            self.level = player.level
            self.trapRating = round(trapDict['rating'] * (1 + trapDict['ratingScale'] * player.totalCunning))
            self.owner = player
            self.rarityWeight = 0 # Not used by player traps
            self.effect = trapDict['effect']
            self.team = "Players"
        else:
            self.name = name
            trapDict = Trap.monsterTraps[name]
            self.level = level
            self.owner = None
            if not level:
                self.level = 1
            self.trapRating = round(trapDict['rating'] * (1 + trapDict['ratingScale'] * self.level))
            self.rarityWeight = trapDict['rarityWeight']
            self.effect = trapDict['effect']
            self.team = "Monsters"
        self.charges = charges
    
    # Player traps
    def _shrapnelTrap(self, target):
        minDamage = round(5 * (1 + self.owner.totalCunning * 0.017))
        maxDamage = round(12 * (1 + self.owner.totalCunning * 0.017))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Piercing"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        
    def _stickyTrap(self, target):
        duration = 2
        Combat.addStatus(target, "Sticky Trap", duration)
        
    def _boulderPitTrap(self, target):
        minDamage = round(3 * (1 + self.owner.totalCunning * 0.02))
        maxDamage = round(8 * (1 + self.owner.totalCunning * 0.02))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Bludgeoning"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        if (target.size == "Small" or target.size == "Medium") and Dice.rollBeneath(20):
            Combat.addStatus(target, "Stun", duration=1)
        
    def _poisonThornTrap(self, target):
        minDamage = round(5 * (1 + self.owner.totalPoisonBonusDamage))
        maxDamage = round(10 * (1 + self.owner.totalPoisonBonusDamage))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Poison"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        # Apply DoT
        poisonRating = 22 + self.owner.totalPoisonRatingBonus
        minDot = round((3 + self.owner.totalCunning / 4) * (1 + self.owner.totalPoisonBonusDamage))
        maxDot = round((6 + self.owner.totalCunning / 4) * (1 + self.owner.totalPoisonBonusDamage))
        dot = Dice.roll(minDot, maxDot)
        duration = min(4, 3 + self.owner.totalCunning / 30)
        Combat.addStatus(target, "Poison Thorn Trap", duration, dot)
    
    # Monster traps
    def _bearTrap(self, target):
        ''' Common monster trap that deals light damage '''
        minDamage = 5 + 2 * self.level
        maxDamage = 15 + 5 * self.level
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Slashing"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
      
    def _snakePit(self, target):
        ''' Uncommon trap that poisons and summons a snake? (overworld) '''
        minDamage = 2 + 2 * self.level
        maxDamage = 8 + 4 * self.level
        dieRoll = Dice.roll(minDamage, maxDamage)
        if target.equippedItems.armorLevel == "Heavy":
            dieRoll = round(dieRoll * 1.40)
        elif target.equippedItems.armorLevel == "Medium":
            dieRoll = round(dieRoll * 1.25)
        element = "Bludgeoning"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        # Poison via toxin TODO
        # Summon snake ever?

    def _standardDartTrap(self, target):
        ''' Common trap that fires multiple darts.  Deals
        less damage to players with high dodge. '''
        count = 1
        if target.totalDodge < self.trapRating * 3:
            count += 1
        if target.totalDodge < self.trapRating * 2:
            count += 1
        if target.totalDodge < round(self.trapRating * 1.5):
            count += 1
        if target.totalDodge < self.trapRating:
            count += 1
        minDamage = (1 + self.level) * count
        maxDamage = (4 + self.level * 3) * count
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Piercing"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
      
    def _poisonousDartTrap(self, target):
        ''' Rare trap that fires multiple darts and deals poison.  
        Deals less damage to players with high dodge. '''
        count = 1
        if target.totalDodge < self.trapRating * 3:
            count += 1
        if target.totalDodge < self.trapRating * 2:
            count += 1
        if target.totalDodge < round(self.trapRating * 1.5):
            count += 1
        if target.totalDodge < self.trapRating:
            count += 1
        minDamage = (1 + self.level) * count
        maxDamage = (4 + self.level * 3) * count
        pRating = 8 + 2 * self.level
        shouldPoison = False
        while( count > 0 ):
            shouldPoison = Combat.calcPoisonHit(self, target, pRating)
            if shouldPoison:
                break
            count -= 1
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Piercing"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        if shouldPoison:
            pass
            # TODO: Apply toxin
      
    def _fireTrap(self, target):
        ''' Uncommon trap that deals a large amount of fire damage. '''
        minDamage = 8 + self.level * 3
        maxDamage = 20 + self.level * 6
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Fire"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        
    def _iceTrap(self, target):
        ''' Rare trap that deals a moderate amount of cold damage and
        lowers movement tiles. '''
        minDamage = 4 + round(self.level * 1.5)
        maxDamage = 10 + self.level * 3
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Cold"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        duration = 5
        magnitude = 1
        Combat.addStatus(target, "Hostile Trap Slow", duration, magnitude)
        
    def _lightningTrap(self, target):
        ''' Rare trap that deals moderate amount of electric damage and
        causes blindness.'''
        minDamage = 5 + self.level * 2
        maxDamage = 14 + self.level * 4
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Electric"
        damage = Trap.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        duration = 20
        magnitude = 50
        Combat.addStatus(target, "Hostile Trap Blind", duration, magnitude)
        
    def _manaSiphonTrap(self, target):
        ''' Ultra-rare trap that drains all mana from a player. '''
        Combat.modifyResource(target, "MP", -target.totalMP)
        
    # Utility methods      
    def trigger(self, target):
        print self.name + " Sprung!"
        if Dice.rollTrapHit(self, target):
            self.effect(target)
            self.charges -= 1
            # If self.charges <= 0, remove from tile. TODO
        
    @staticmethod
    def calcTrapDamage(target, amount, element):
        if element == "Fire":
            amount = round(amount * (1 - (float(target.totalFireResistance) / 100)))
        elif element == "Cold":
            amount = round(amount * (1 - (float(target.totalColdResistance) / 100)))           
        elif element == "Electric":
            amount = round(amount * (1 - (float(target.totalElectricResistance) / 100)))
        elif element == "Poison":
            amount = round(amount * (1 - (float(target.totalPoisonResistance) / 100)))    
        elif element == "Shadow":
            amount = round(amount * (1 - (float(target.totalShadowResistance) / 100)))
        elif element == "Divine":
            amount = round(amount * (1 - (float(target.totalDivineResistance) / 100)))
        elif element == "Arcane":
            amount = round(amount * (1 - (float(target.totalArcaneResistance) / 100)))
        elif element == "Bludgeoning":
            amount = round(amount * (1 - (float(target.totalBludgeoningResistance) / 100)))
            amount = round(amount * (1 - max(0, min(80, target.totalDR))))
        elif element == "Piercing":
            amount = round(amount * (1 - (float(target.totalPiercingResistance) / 100)))
            amount = round(amount * (1 - max(0, min(80, target.totalDR))))
        elif element == "Slashing":
            amount = round(amount * (1 - (float(target.totalSlashingResistance) / 100)))
            amount = round(amount * (1 - max(0, min(80, target.totalDR))))
        return amount
        
    playerTraps = {
        'Shrapnel Trap':
            {
            'rating' : 13,
            'ratingScale' : 0.015,
            'effect' : _shrapnelTrap,
            },
        'Sticky Trap':
            {
            'rating' : 20,
            'ratingScale' : 0.007,
            'effect' : _stickyTrap
            },
        'Boulder Pit Trap':
            {
            'rating' : 25,
            'ratingScale' : 0.007,
            'effect' : _boulderPitTrap
            },
        
        'Poison Thorn Trap':
            {
            'rating' : 18,
            'ratingScale' : 0.01,
            'effect' : _poisonThornTrap
            }
    
    }
    
    monsterTraps = {
        'Bear Trap':
            {
            'rating' : 5,
            'ratingScale' : 0.2,
            'effect' : _bearTrap,
            'rarityWeight' : 12
            },
        'Snake Pit':
            {
            'rating' : 7,
            'ratingScale' : 0.285,
            'effect' : _snakePit,
            'rarityWeight' : 5
            },
        'Standard Dart Trap':
            {
            'rating' : 7,
            'ratingScale' : 0.285,
            'effect' : _standardDartTrap,
            'rarityWeight' : 10
            },
        'Poisonous Dart Trap':
            {
            'rating' : 7,
            'ratingScale' : 0.285,
            'effect' : _poisonousDartTrap,
            'rarityWeight' : 2
            },
        'Fire Trap':
            {
            'rating' : 8,
            'ratingScale' : 0.25,
            'effect' : _fireTrap,
            'rarityWeight' : 5
            },
        'Ice Trap' :
            {
            'rating' : 15,
            'ratingScale' : 0.2,
            'effect' : _iceTrap,
            'rarityWeight' : 2
            },
        'Lightning Trap' : 
            {
            'rating' : 8,
            'ratingScale' : 0.25,
            'effect' : _lightningTrap,
            'rarityWeight' : 2
            },
        'Mana Siphon Trap' : 
            {
            'rating' : 25,
            'ratingScale' : 0.2,
            'effect' : _manaSiphonTrap,
            'rarityWeight' : 1
            }     
    }
        
        
        
    
        