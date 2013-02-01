#!/usr/bin/python

import sys
import person as p

class Monster(p.Person):

    ERROR = "INITIALIZATION_FAILURE"

    @staticmethod
    def setFrom(argDict, variableName, defaultValue=ERROR):
        if( (variableName not in argDict) or (argDict[variableName] == "None") ):
            if defaultValue == Monster.ERROR:
                raise p.IncompleteDataInitialization( "The parameter: " + variableName + " must be specified, but isn't.")
            else:
                return defaultValue
        else:
            return argDict[variableName]


    def __init__(self, argDict):
        p.Person.__init__(self, argDict)
        self.attackPower = 100
        # TODO: Make sure internalstatuses are hooked into attackPower
        self.team = "Monsters"
        # TODO: Find a way to distinguish between summons and monsters for the 'team'.
        
        self.level = Monster.setFrom(argDict, 'level')
        self.name = Monster.setFrom(argDict, 'name')
        self.experienceGiven = Monster.setFrom(argDict, 'experience')
        self.GP = Monster.setFrom(argDict, 'GP')
        
        self.specialAttackOne = Monster.setFrom(argDict, 'specialAttackOne', None)
        self.specialAttackTwo = Monster.setFrom(argDict, 'specialAttackTwo', None)
        self.specialAttackThree = Monster.setFrom(argDict, 'specialAttackThree', None)
        self.specialProperty = Monster.setFrom(argDict, 'specialProperty', None)
        
        self.attackElement = Monster.setFrom(argDict, 'attackElement')
        self.attackMinDamage = Monster.setFrom(argDict, 'attackMin')
        self.attackMaxDamage = Monster.setFrom(argDict, 'attackMax')
        self.attackRange = Monster.setFrom(argDict, 'attackRange')
        
    def adjustMaxHP(self, numberOfPlayers):
        if numberOfPlayers == 1:
            pass
        elif numberOfPlayers == 2:
            self.baseHP = round(self.baseHP * 1.5)
        elif numberOfPlayers == 3:
            self.baseHP = round(self.baseHP * 2)
        elif numberOfPlayers == 4:
            self.baseHP = round(self.baseHP * 2.5)
            
        