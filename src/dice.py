#!/usr/bin/python

import sys
import random

class Dice(object):
    """A utility class used for purely chance events."""

    useGivenSeed = False
    oldGenerator = None

    @staticmethod
    def stashGen():
        """Saves the old position in the RNG and loads a new position."""
        if not Dice.useGivenSeed:
            Dice.oldGenerator = random.getstate()
            random.seed()

    @staticmethod
    def popGen():
        """Loads the old position in the RNG"""
        if not Dice.useGivenSeed:
            random.setstate(Dice.oldGenerator)

    @staticmethod
    def rollSuccess(chanceOfSuccess):
        """rolls between [1 and 100]  If the roll is <= chanceOfSuccess,
           returns "Normal Hit", otherwise "Miss".
           Inputs:
             chanceOfSuccess -- int from 1 to 100
           Outputs:
             "Normal Hit" or "Miss" """
        Dice.stashGen()
        if (random.randint(1, 100) <= chanceOfSuccess):
            Dice.popGen()
            return "Normal Hit"
        else:
            Dice.popGen()
            return "Miss"

    @staticmethod
    def scale(scaleAttributeValue, value, scale, cap=0):
        """Returns a modified version of the given value based on the scaling
        factor and the attribute it should be scaled from.
        Inputs:
          scaleAttributeValue: int from a statistic that magnifies this ability
          value: int base value of this ability.
          scale: float the amount per point of the scaling attribute this should
            be multiplied by
          cap: optional int representing the largest amount that can be returned
        Outpus:
          integer"""
        Dice.stashGen()
        rValue = None
        if cap != 0:
            rValue = round(min(value * (1 + scaleAttributeValue * scale), cap))
        else:
            rValue = round(value * (1 + scaleAttributeValue * scale))
        Dice.popGen()
        return rValue

    @staticmethod
    def choose(list):
        '''Returns a random selection from a given list.'''
        if not list:
            return None
        Dice.stashGen()
        rValue = random.choice(list)
        Dice.popGen()
        return rValue

    @staticmethod
    def roll(minimum, maximum):
        """Returns an integer somewhere between the minimum and maximum (as an integer)."""
        if minimum == maximum:
            return minimum
        Dice.stashGen()
        rValue = random.randint(minimum, maximum)
        Dice.popGen()
        return rValue

    @staticmethod
    def rollFloat(minFloat, maxFloat):
        Dice.stashGen()
        rValue = random.uniform(minFloat, maxFloat)
        Dice.popGen()
        return rValue

    @staticmethod
    def rollBeneath(targetRoll):
        """rolls between [1 and 100]  If the roll is <= chanceOfSuccess,
           returns True, otherwise False.
           Inputs:
             chanceOfSuccess -- int from 1 to 100
           Outputs:
             True or False """
        Dice.stashGen()
        rValue = random.randint(1,100) <= targetRoll
        Dice.popGen()
        return rValue

    @staticmethod
    def chanceFromSize(target, sizeRules, defaultChance=0):
        """Returns either True or False based upon the given size rules, the size of the
        target, and the default chance if the size isn't defined in the size rules.
        Inputs:
          target -- Person to grab size from
          sizeRules -- List of duples of the form ["Small", 0.8] that define
            that Small targets should have a chance of 80% to succeed.
          defaultChace -- optional float indicating the default chance if the target's size
            is not in the list.  Defaults to 0%.
        Outputs:
          True or False"""
        Dice.stashGen()
        size = target.size
        chance = defaultChance
        for rule in sizeRules:
            if size == rule[0]:
                chance = rule[1]
        if random.random() <= chance:
            Dice.popGen()
            return True
        else:
            Dice.popGen()
            return False

    @staticmethod
    def rollTrapHit(trap, target):
        """Determines if the target is hit by the trap, or if he evades it.
        Inputs:
          trap -- Trap; the trap that is being triggered
          target -- Person; the victim of the trap
        Outputs:
          False -- The trap failed to harm the target.
          True -- The trap successfully hit the target."""
        Dice.stashGen()
        adjustedEva = round(target.totalTrapEvade * random.uniform(0.5, 1.0))
        adjustedRating = round(trap.trapRating * random.uniform(0.5, 1.0))
        Dice.popGen()
        if adjustedEva >= adjustedRating:
            return False
        else:
            return True

    @staticmethod
    def rollTrapDetect(trap, player):
        '''Determines if the player detects the trap this turn.
        Returns True or False.'''
        Dice.stashGen()
        adjustedDifficulty = round((trap.level * 3 + 13) * random.uniform(0.75, 1.0))
        adjustedDetection = round(max(player.totalAwareness, player.totalIntuition) * random.uniform(0.75, 1.0))
        wasDetected = False
        if adjustedDetection >= adjustedDifficulty:
            wasDetected = True
        Dice.popGen()
        return wasDetected
            
    @staticmethod
    def rollPresetChance(source, target, chance):
        """Rolls the level-adjusted present chance roll as defined on the Misc. page of the wiki.
        Inputs:
          source -- Person doing ability
          target -- Person receiving ability
          chance -- a preset chance string, possible values:
            Reliable, Frequent, Occasional, Unlikely, Rarely
        Outputs:
          True or False"""
        Dice.stashGen()
        rValue = None
        name = chance.capitalize()
        endChance = 0
        if name == "Reliable" or name == "Reliably":
            endChance = 80
            if( source.level > target.level ):
                endChance += 10 * (source.level - target.level)
            else:
                endChance -= 5 * (target.level - source.level)
            rValue = Dice.roll(1, 100) <= endChance
        elif name == "Frequent" or name == "Frequently":
            endChance = 60
            if( source.level > target.level ):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 5 * (target.level - source.level)
            rValue = Dice.roll(1,100) <= min(endChance, 90)
        elif name == "Occasional" or name == "Occasionally":
            endChance = 50
            if( source.level > target.level ):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 10 * (target.level - source.level)
            rValue = Dice.roll(1,100) <= min(endChance, 80)
        elif name == "Unlikely":
            endChance = 30
            if( source.level > target.level):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 10 * (target.level - source.level)
            rValue =  Dice.roll(1,100) <= min(endChance, 70)
        elif name == "Rarely" or name == "Rare":
            endChance = 15
            if source.level > target.level:
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 10 * (source.level - target.level)
            rValue = Dice.roll(1,100) <= min(endChance, 50)
        Dice.popGen()
        return rValue

    @staticmethod
    def rollNumberOfTraps(level, reductionPercent=0):
        '''Determines the number of traps to be placed on a combat
        pane.'''
        Dice.stashGen()
        # TODO: Smaller combat panes will need a reductionPercent.
        maximum = 10
        minimum = 2
        if level < 3:
            maximum = 4
        if level > 8:
            minimum = 5
        selectionList = ['2', '2', '3', '3', '3', '4', '4', '4', '5', '5', '6', '7', '8', '9', '10']
        rValue = int(random.choice(selectionList))
        if rValue > maximum:
            rValue = maximum
        elif rValue < minimum:
            rValue = minimum
        Dice.popGen()
        return rValue


