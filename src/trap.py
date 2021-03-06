#!/usr/bin/python

import sys
import os
from dice import *
from combat import *
from const import *
import entity as e
import broadcast

# trap.py
# Author: Devin Ekins -- G. Cube
#
# Trap is a child of Entity that represents traps placed in combat, both
# friendly, and hostile.  The module contains a small interface consisting
# of a couple of methods through which all outer interactions should be 
# performed.  It also contains a dict with all of the traps in game, according
# to, and documented by, the wiki of official game rules.
#

class Trap(e.Entity):

    totalWeight = 0

    def __init__(self, name, level=None, player=None, location=None, image=None):
        """Constructor for Traps.  Should only be used with
        keyword arguments."""
        if not image:
            image = os.path.join(TRAPS_IMAGES_PATH, "trap.png")
        e.Entity.__init__(self, location=location, image=image, passable=True)
        if player:
            self.name = name
            trapDict = Trap.playerTraps[name]
            if 'image' in trapDict:
                self.image = trapDict['image']
            self.level = player.level
            self.trapRating = int(trapDict['rating'] * (1 + trapDict['ratingScale'] * player.totalCunning) + player.bonusTrapRating)
            self.owner = player
            self.rarityWeight = 0 # Not used by player traps
            self.effect = trapDict['effect']
            self.team = "Players"
            self.isFavor = trapDict['isFavor']
            self.charges = trapDict['charges']
            self.visible = True
        else:
            self.name = name
            trapDict = Trap.monsterTraps[name]
            if 'image' in trapDict:
                self.image = trapDict['image']
            self.level = level
            self.owner = None
            if not level:
                self.level = 1
            self.trapRating = int(trapDict['rating'] * (1 + trapDict['ratingScale'] * self.level))
            self.rarityWeight = trapDict['rarityWeight']
            self.effect = trapDict['effect']
            self.team = "Monsters"
            self.isFavor = False # Monsters do not place Favors
            self.charges = 1 # Monster traps only have one charge
            self.visible = False

    # Player traps
    def _shrapnelTrap(self, target):
        minDamage = int(5 * (1 + self.owner.totalCunning * 0.017))
        maxDamage = int(14 * (1 + self.owner.totalCunning * 0.017))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Piercing"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        Combat.sendCombatMessage("Trap dealt " + str(damage) + " total damage.", self.owner, color="yellow")

    def _stickyTrap(self, target):
        duration = 3
        if target.hasStatus("Sticky Trap"):
            sticky = [x for x in target._statusList if x.name == "Sticky Trap"][0]
            stickyDuration = sticky.turnsLeft
            if stickyDuration > 3:
                return
        Combat.addStatus(target, "Sticky Trap", duration)
        Combat.sendCombatMessage("Trap lowered movement speed.", self.owner, color="yellow")
        
    def _boulderPitTrap(self, target):
        minDamage = int(4 * (1 + self.owner.totalCunning * 0.02))
        maxDamage = int(11 * (1 + self.owner.totalCunning * 0.02))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Bludgeoning"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        if (target.size == "Small" or target.size == "Medium") and Dice.rollBeneath(30):
            Combat.addStatus(target, "Stun", duration=2)
            Combat.sendCombatMessage("Trap Stunned " + target.name, self.owner, color="yellow")
        Combat.sendCombatMessage("Trap dealt " + `damage` + " total damage.", self.owner, color="yellow")

    def _poisonThornTrap(self, target):
        minDamage = int(6 * (1 + self.owner.totalPoisonBonusDamage * 0.01))
        maxDamage = int(12 * (1 + self.owner.totalPoisonBonusDamage * 0.01))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Poison"
        damage = self.calcTrapDamage(target, dieRoll, element)
        poisonHit = Combat.calcPoisonHit(self.owner, target, rating=(22 + self.owner.level))
        if poisonHit != "Miss":
            Combat.lowerHP(target, damage)
            Combat.sendCombatMessage("Trap dealt " + `damage` + " damage.", self.owner, color="yellow")
        # Apply DoT
        poisonRating = 22 + self.owner.totalPoisonRatingBonus + self.owner.level
        minDot = int((3 + self.owner.totalCunning / 4) * (1 + self.owner.totalPoisonBonusDamage * 0.01))
        maxDot = int((6 + self.owner.totalCunning / 4) * (1 + self.owner.totalPoisonBonusDamage * 0.01))
        dot = Dice.roll(minDot, maxDot)
        duration = min(4, 3 + self.owner.totalCunning / 30)
        dotHit = Combat.calcPoisonHit(self.owner, target, rating=(22 + self.owner.level))
        if dotHit != "Miss":
            Combat.addStatus(target, "Poison Thorn Trap", duration, dot)

    def _explosiveTrap(self, target):
        minDamage = int(9 * (1 + self.owner.totalFireBonusDamage * 0.01))
        maxDamage = int(18 * (1 + self.owner.totalFireBonusDamage * 0.01))
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Fire"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        Combat.sendCombatMessage("Trap dealt " + `damage` + " primary damage.", self.owner, color="yellow")
        # Secondary Targets
        splashMin = int(minDamage * 0.75)
        splashMax = int(maxDamage * 0.75)
        targetGroup = Combat.getAOETargets(target.cPane, target.cLocation, radius=1)
        for tar in targetGroup:
            dieRoll = Dice.roll(splashMin, splashMax)
            dam = self.calcTrapDamage(tar, dieRoll, element)
            Combat.lowerHP(tar, dam)
            Combat.sendCombatMessage("Trap dealt " + `dam` + " secondary damage.", self.owner, color="yellow")
            
    def _accuracyFavor(self, target):
        accuracyBonus = 3 + self.owner.totalCunning / 4
        duration = 2
        Combat.addStatus(target, "Accuracy Favor", duration, accuracyBonus)

    def _manaFavor(self, target):
        manaRecovered = 5 + self.owner.totalCunning / 6
        Combat.modifyResource(target, "MP", manaRecovered)

    def _magicalDampeningTrap(self, target):
        spellpowerReduction = 6 + self.owner.totalCunning / 4
        duration = 4
        Combat.addStatus(target, "Magical Dampening Trap", duration, spellpowerReduction)

    def _nearsightedTrap(self, target):
        if target.attackRange <= 4:
            return
        target.attackRange = max(4, target.attackRange - 2)

    # Monster traps
    def _bearTrap(self, target):
        ''' Common monster trap that deals light damage '''
        minDamage = 5 + 2 * self.level
        maxDamage = 15 + 5 * self.level
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Slashing"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")

    def _snakePit(self, target):
        ''' Uncommon trap that poisons and summons a snake? (overworld) '''
        minDamage = 2 + 2 * self.level
        maxDamage = 8 + 4 * self.level
        dieRoll = Dice.roll(minDamage, maxDamage)
        if target.equippedItems.armorLevel == "Heavy":
            dieRoll = int(dieRoll * 1.40)
        elif target.equippedItems.armorLevel == "Medium":
            dieRoll = int(dieRoll * 1.25)
        element = "Bludgeoning"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")
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
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")

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
        pHit = "Miss"
        while( count > 0 ):
            pHit = Combat.calcPoisonHit(self, target, pRating)
            if pHit == "Normal Hit":
                break
            count -= 1
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Piercing"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        if pHit == "Normal Hit":
            pass
            # TODO: Apply toxin
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")

    def _fireTrap(self, target):
        ''' Uncommon trap that deals a large amount of fire damage. '''
        minDamage = 8 + self.level * 3
        maxDamage = 20 + self.level * 6
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Fire"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")

    def _iceTrap(self, target):
        ''' Rare trap that deals a moderate amount of cold damage and
        lowers movement tiles. '''
        minDamage = 4 + round(self.level * 1.5)
        maxDamage = 10 + self.level * 3
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Cold"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        duration = 5
        magnitude = 1
        Combat.addStatus(target, "Hostile Trap Slow", duration, magnitude)
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")

    def _lightningTrap(self, target):
        ''' Rare trap that deals moderate amount of electric damage and
        causes blindness.'''
        minDamage = 5 + self.level * 2
        maxDamage = 14 + self.level * 4
        dieRoll = Dice.roll(minDamage, maxDamage)
        element = "Electric"
        damage = self.calcTrapDamage(target, dieRoll, element)
        Combat.lowerHP(target, damage)
        duration = 20
        magnitude = 50
        Combat.addStatus(target, "Hostile Trap Blind", duration, magnitude)
        Combat.sendCombatMessage(self.name + " dealt " + `damage` + " damage to " + target.name, target, color="red")

    def _manaSiphonTrap(self, target):
        ''' Ultra-rare trap that drains all mana from a player. '''
        drainAmount = target.totalMP / 2
        Combat.modifyResource(target, "MP", -drainAmount)
        Combat.sendCombatMessage(self.name + " drained " + `drainAmount` + " mana from " + target.name, target, color="red")

    # Utility methods
    def trigger(self, target):
        '''This method will attempt to trigger the trap.
        It should only be called when a hostile target steps on
        it.  However, if this is a "favor" trap, it should only
        be called if a friendly target steps on it.'''
        if self.isFavor:
            # Print some message.
            self.effect(self, target)
            self.charges -= 1
        else:
            if Dice.rollTrapHit(self, target):
                self.effect(self, target)
                Combat.sendCombatMessage(target.name + " sprung a " + self.name + "! (" + 
                                        `self.trapRating` + " vs. " + `target.totalTrapEvade` + ")", 
                                        target, color='lightblue')
                if self.team == "Players":
                    self.owner.record.recordTrapSuccess()
                self._shout(target, didHit=True)
            else:
                Combat.sendCombatMessage(target.name + " evaded a " + self.name + ". (" + 
                                        `self.trapRating` + " vs. " + `target.totalTrapEvade` + ")",
                                        target, color='lightblue')
                if self.team == "Players":
                    self.owner.record.recordTrapFailure()
                self._shout(target, didHit=False)
            self.charges -= 1
            if self.charges == 0 and self.team == "Players":
                self.owner.record.recordTrapRemoval()

    def shouldTrigger(self, target):
        '''Determines if this trap should attempt to
        go off when stepped on by the target.
        Inputs:
          self
          target -- Person stepping on trap/favor
        Outputs:
          True or False'''
        if self.isFavor and self.team == target.team:
            return True
        elif not self.isFavor and self.team != target.team:
            return True
        return False

    def _shout(self, victim, didHit):
        vString = "Player"
        if victim.team == "Monsters":
            vString = "Monster"
        bundle = {'victim' : vString, 'didHit' : didHit, 'trap' : self}
        bc = broadcast.TrapBroadcast(bundle)
        if self.owner:
            bc.shout(self.owner)
        bc.shout(victim)
        
    def calcTrapDamage(self, target, amount, element):
        endAmount = 0
        if element == "Fire":
            endAmount = int(amount * (1 - (float(target.totalFireResistance) / 100)))
        elif element == "Cold":
            endAmount = int(amount * (1 - (float(target.totalColdResistance) / 100)))
        elif element == "Electric":
            endAmount = int(amount * (1 - (float(target.totalElectricResistance) / 100)))
        elif element == "Poison":
            endAmount = int(amount * (1 - (float(target.totalPoisonResistance) / 100)))
        elif element == "Shadow":
            endAmount = int(amount * (1 - (float(target.totalShadowResistance) / 100)))
        elif element == "Divine":
            endAmount = int(amount * (1 - (float(target.totalDivineResistance) / 100)))
        elif element == "Arcane":
            endAmount = int(amount * (1 - (float(target.totalArcaneResistance) / 100)))
        elif element == "Bludgeoning":
            endAmount1 = int(amount * (1 - target.totalBludgeoningResistance * 0.01))
            endAmount = int(endAmount1 * (1 - max(0, min(80, target.totalDR)) * 0.01))
        elif element == "Piercing":
            endAmount1 = int(amount * (1 - target.totalPiercingResistance * 0.01))
            endAmount = int(endAmount1 * (1 - max(0, min(80, target.totalDR)) * 0.01))
        elif element == "Slashing":
            endAmount1 = int(amount * (1 - target.totalSlashingResistance * 0.01))
            endAmount = int(endAmount1 * (1 - max(0, min(80, target.totalDR)) * 0.01))
            
        if target.team == "Players":
            return int(endAmount * (1 - target.totalTrapDamageReduction * 0.01))
            
        if self.team == "Players":
            return int(endAmount * (1 + self.owner.bonusTrapDamage * 0.01))
        return endAmount

    @staticmethod
    def getRandomTrap(level, loc):
        ''' Returns a random hostile trap of the given level. '''
        if Trap.totalWeight == 0:
            # Hasn't been initialized.
            for hTrap in Trap.monsterTraps:
                Trap.totalWeight += Trap.monsterTraps[hTrap]['rarityWeight']

        choice = Dice.roll(0, Trap.totalWeight)
        for hTrap in Trap.monsterTraps:
            choice -= Trap.monsterTraps[hTrap]['rarityWeight']
            if choice <= 0:
                return Trap(hTrap, level=level, location=loc)

    playerTraps = {
        'Shrapnel Trap':
            {
            'rating' : 16,
            'ratingScale' : 0.015,
            'effect' : _shrapnelTrap,
            'isFavor' : False,
            'charges' : 1
            },
        'Sticky Trap':
            {
            'rating' : 24,
            'ratingScale' : 0.007,
            'effect' : _stickyTrap,
            'isFavor' : False,
            'charges' : 2, 
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'sticky-trap.png')
            },
        'Boulder Pit Trap':
            {
            'rating' : 30,
            'ratingScale' : 0.007,
            'effect' : _boulderPitTrap,
            'isFavor' : False,
            'charges' : 1,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'boulder-pit-trap.png')
            },

        # Druid only traps
        'Poison Thorn Trap':
            {
            'rating' : 23,
            'ratingScale' : 0.01,
            'effect' : _poisonThornTrap,
            'isFavor' : False,
            'charges' : 1,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'poison-thorn-trap.png')
            },

        # Anarchist only traps
        'Explosive Trap':
            {
            'rating' : 25,
            'ratingScale' : 0.01,
            'effect' : _explosiveTrap,
            'isFavor' : False,
            'charges' : 1,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'explosive-trap.png')
            },
            
        # Tactician only traps
        'Accuracy Favor':
            {
            'rating' : 0,
            'ratingScale' : 0.0,
            'effect' : _accuracyFavor,
            'isFavor' : True,
            'charges' : 3
            },
        'Mana Favor':
            {
            'rating' : 0,
            'ratingScale' : 0.0,
            'effect' : _manaFavor,
            'isFavor' : True,
            'charges' : 3
            },
        'Magical Dampening Trap':
            {
            'rating' : 30,
            'ratingScale' : 0.01,
            'effect' : _magicalDampeningTrap,
            'isFavor' : False,
            'charges' : 1
            },
        'Nearsighted Trap':
            {
            'rating' : 30,
            'ratingScale' : 0.01,
            'effect' : _nearsightedTrap,
            'isFavor' : False,
            'charges' : 1
            }
    }

    monsterTraps = {
        'Bear Trap':
            {
            'rating' : 10,
            'ratingScale' : 0.2,
            'effect' : _bearTrap,
            'rarityWeight' : 12,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'bear-trap.png')
            },
        #'Snake Pit':
        #    {
        #    'rating' : 14,
        #    'ratingScale' : 0.285,
        #    'effect' : _snakePit,
        #    'rarityWeight' : 5
        #    },
        'Standard Dart Trap':
            {
            'rating' : 14,
            'ratingScale' : 0.285,
            'effect' : _standardDartTrap,
            'rarityWeight' : 10,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'standard-dart-trap.png')
            },
        #'Poisonous Dart Trap':
        #    {
        #    'rating' : 14,
        #    'ratingScale' : 0.285,
        #    'effect' : _poisonousDartTrap,
        #    'rarityWeight' : 2
        #    },
        'Fire Trap':
            {
            'rating' : 15,
            'ratingScale' : 0.25,
            'effect' : _fireTrap,
            'rarityWeight' : 5,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'fire-trap.png')
            },
        'Ice Trap' :
            {
            'rating' : 30,
            'ratingScale' : 0.2,
            'effect' : _iceTrap,
            'rarityWeight' : 2,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'ice-trap.png')
            },
        'Lightning Trap' :
            {
            'rating' : 16,
            'ratingScale' : 0.25,
            'effect' : _lightningTrap,
            'rarityWeight' : 2,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'lightning-trap.png')
            },
        'Mana Siphon Trap' :
            {
            'rating' : 40,
            'ratingScale' : 0.2,
            'effect' : _manaSiphonTrap,
            'rarityWeight' : 1,
            'image' : os.path.join(TRAPS_IMAGES_PATH, 'mana-siphon-trap.png')
            }
    }





