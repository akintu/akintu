#!/usr/bin/python

import sys
import random

class Dice(object):
    """A utility class used for purely chance events."""
    
    @staticmethod
    def rollSuccess(chanceOfSuccess):
        """rolls between [1 and 100]  If the roll is <= chanceOfSuccess, 
           returns "Normal Hit", otherwise "Miss".
           Inputs:
             chanceOfSuccess -- int from 1 to 100
           Outputs:
             "Normal Hit" or "Miss" """
        if (random.randint(1, 100) <= chanceOfSuccess):
            return "Normal Hit"
        else:
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
        if cap != 0:
            return round(min(value * (1 + scaleAttributeValue * scale), cap))
        else:
            return round(value * (1 + scaleAttributeValue * scale))
    
    @staticmethod
    def roll(minimum, maximum):
        """Returns an integer somewhere between the minimum and maximum (as an integer)."""
        if minimum == maximum:
            return minimum
        return random.randint(minimum, maximum)
        
    @staticmethod
    def rollFloat(minFloat, maxFloat):
        return random.uniform(minFloat, maxFloat)
        
    @staticmethod
    def rollBeneath(targetRoll):
        """rolls between [1 and 100]  If the roll is <= chanceOfSuccess, 
           returns True, otherwise False.
           Inputs:
             chanceOfSuccess -- int from 1 to 100
           Outputs:
             True or False """
        return random.randint(1,100) <= targetRoll
            
    
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
        size = target.size
        chance = defaultChance
        for rule in sizeRules:
            if size == rule[0]:
                chance = rule[1]
        if random.random() <= chance:
            return True
        else:
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
        adjustedEva = round(target.totalTrapEvade * random.uniform(0.5, 1.0))
        adjustedRating = round(trap.trapRating * random.uniform(0.5, 1.0))
        if adjustedEva >= adjustedRating:
            return False
        else:
            return True
    
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
        name = chance.capitalize()
        endChance = 0
        if (name == "Reliable" or name == "Reliably"):
            endChance = 80
            if( source.level > target.level ):
                endChance += 10 * (source.level - target.level)
            else:
                endChance -= 5 * (target.level - source.level)
            return (roll(1, 100) <= endChance)
                
        if (name == "Frequent" or name == "Frequently"):
            endChance = 60
            if( source.level > target.level ):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 5 * (target.level - source.level)
            return (roll(1,100) <= min(endChance, 90))

        if (name == "Occasional" or name == "Occasionally"):
            endChance = 50
            if( source.level > target.level ):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 10 * (target.level - source.level)
            return (roll(1,100) <= min(endChance, 80))

        if (name == "Unlikely"):
            endChance = 30
            if( source.level > target.level):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 10 * (target.level - source.level)
            return (roll(1,100) <= min(endChance, 70))

        if (name == "Rarely" or name == "Rare"):
            endChance = 15
            if( source.level > target.level):
                endChance += 5 * (source.level - target.level)
            else:
                endChance -= 10 * (source.level - target.level)
            return (roll(1,100) <= min(endChance, 50))
                        
                
                
                