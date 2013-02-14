#!/usr/bin/python

import sys
import person
import ability
import passiveability
import spell
from const import *

class Monster(person.Person):

    ERROR = "INITIALIZATION_FAILURE"

    @staticmethod
    def setFrom(argDict, variableName, defaultValue=ERROR):
        if( (variableName not in argDict) or (argDict[variableName] == "None") ):
            if defaultValue == Monster.ERROR:
                raise person.IncompleteDataInitialization( "The parameter: " + variableName + " must be specified, but isn't.")
            else:
                return defaultValue
        else:
            return argDict[variableName]


    def __init__(self, argDict):
        person.Person.__init__(self, argDict)
        self.attackPower = 100
        # TODO: Make sure internalstatuses are hooked into attackPower
        self.team = "Monsters"
        # TODO: Find a way to distinguish between summons and monsters for the 'team'.
        
        self.level = Monster.setFrom(argDict, 'level')
        self.name = Monster.setFrom(argDict, 'name')
        self.experienceGiven = Monster.setFrom(argDict, 'experience')
        self.GP = Monster.setFrom(argDict, 'GP')

        self.abilityList = []
        self.spellList = []
        self.passiveAbility = None
        
        self.specialAttackOneName = Monster.setFrom(argDict, 'specialAttackOne', None)
        if self.specialAttackOneName:
            if "Spell: " in self.specialAttackOneName:
                spellName = self.specialAttackOneName[7:]
                self.spellList.append(spell.Spell(spellName, self))
            else:
                self.abilityList.append(ability.Ability(self.specialAttackOneName, self))
            
        self.specialAttackTwoName = Monster.setFrom(argDict, 'specialAttackTwo', None)
        if self.specialAttackTwoName:
            if "Spell: " in self.specialAttackTwoName:
                spellName = self.specialAttackTwoName[7:]
                self.spellList.append(spell.Spell(spellName, self))
            else:
                self.abilityList.append(ability.Ability(self.specialAttackTwoName, self))
            
        self.specialAttackThreeName = Monster.setFrom(argDict, 'specialAttackThree', None)
        if self.specialAttackThreeName:
            if "Spell: " in self.specialAttackThreeName:
                spellName = self.specialAttackThreeName[7:]
                self.spellList.append(spell.Spell(spellName, self))
            else:
                self.abilityList.append(ability.Ability(self.specialAttackThreeName, self))
            
        self.specialPropertyName = Monster.setFrom(argDict, 'specialProperty', None)
        if self.specialPropertyName:
            self.passiveAbility = passiveability.PassiveAbility(self.specialPropertyName, self)
        
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
        
        
        
        