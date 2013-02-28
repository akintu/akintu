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
        self.team = "Monsters"
        # TODO: Find a way to distinguish between summons and monsters for the 'team'. Perhaps inherit from Person seperately?
        self.level = Monster.setFrom(argDict, 'minLevel')
        self.minLevel = self.level
        self.maxLevel = Monster.setFrom(argDict, 'maxLevel')
        self.name = Monster.setFrom(argDict, 'name')
        self.experienceGiven = Monster.setFrom(argDict, 'experience')
        self.GP = Monster.setFrom(argDict, 'GP')

        self.type = Monster.setFrom(argDict, 'type')
        
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
        
        self.levelupArmorPenetration = Monster.setFrom(argDict, 'levelupArmorPenetration')
        self.levelupCunning = Monster.setFrom(argDict, 'levelupCunning')
        self.levelupDexterity = Monster.setFrom(argDict, 'levelupDexterity')
        self.levelupMinDamage = Monster.setFrom(argDict, 'levelupMinDamage')
        self.levelupMaxDamage = Monster.setFrom(argDict, 'levelupMaxDamage')
        self.levelupDR = Monster.setFrom(argDict, 'levelupDR')
        self.levelupHP = Monster.setFrom(argDict, 'levelupHP')
        self.levelupMP = Monster.setFrom(argDict, 'levelupMP')
        self.levelupArcaneResistance = Monster.setFrom(argDict, 'levelupArcaneResistance')
        self.levelupBludgeoningResistance = Monster.setFrom(argDict, 'levelupBludgeoningResistance')
        self.levelupColdResistance = Monster.setFrom(argDict, 'levelupColdResistance')
        self.levelupDivineResistance = Monster.setFrom(argDict, 'levelupDivineResistance')
        self.levelupElectricResistance = Monster.setFrom(argDict, 'levelupElectricResistance')
        self.levelupFireResistance = Monster.setFrom(argDict, 'levelupFireResistance')
        self.levelupPiercingResistance = Monster.setFrom(argDict, 'levelupPiercingResistance')
        self.levelupPoisonResistance = Monster.setFrom(argDict, 'levelupPoisonResistance')
        self.levelupShadowResistance = Monster.setFrom(argDict, 'levelupShadowResistance')
        self.levelupSlashingResistance = Monster.setFrom(argDict, 'levelupSlashingResistance')
        self.levelupMagicResist = Monster.setFrom(argDict, 'levelupMagicResist')
        self.levelupPoisonTolerance = Monster.setFrom(argDict, 'levelupPoisonTolerance')
        self.levelupSpellpower = Monster.setFrom(argDict, 'levelupSpellpower')
        self.levelupStrength = Monster.setFrom(argDict, 'levelupStrength')
        
        self.levelSet = False
        
    def setLevel(self, level):
        '''Method should only be called once after creation to set the level of a 
        monster.  Will print a warning message if this is called more than once.'''
        if self.levelSet:
            print "WARNING: Level for this monster has been set previously.  Statistics will be incorrect."
        if level < self.minLevel:
            print "Level specified is below this monster's minimum level of " + str(self.minLevel) + "."
            return
        self.levelSet = True
        diff = level - self.minLevel
        self.baseArmorPenetration += self.levelupArmorPenetration * diff
        self.baseCunning += self.levelupCunning * diff
        self.baseDexterity += self.levelupDexterity * diff
        self.attackMinDamage += self.levelupMinDamage * diff
        self.attackMaxDamage += self.levelupMaxDamage * diff
        self.baseDR += self.levelupDR * diff
        self.baseHP += self.levelupHP * diff
        self.HP = self.totalHP
        self.baseMP += self.levelupMP * diff
        self.MP = self.totalMP
        self._baseArcaneResistance += self.levelupArcaneResistance * diff
        self._baseBludgeoningResistance += self.levelupBludgeoningResistance * diff
        self._baseColdResistance += self.levelupColdResistance * diff
        self._baseDivineResistance += self.levelupDivineResistance * diff
        self._baseElectricResistance += self.levelupElectricResistance * diff
        self._baseFireResistance += self.levelupFireResistance * diff
        self._basePiercingResistance += self.levelupPiercingResistance * diff
        self._basePoisonResistance += self.levelupPoisonResistance * diff
        self._baseShadowResistance += self.levelupShadowResistance * diff
        self._baseSlashingResistance += self.levelupSlashingResistance * diff
        self.baseMagicResist += self.levelupMagicResist * diff
        self.basePoisonTolerance += self.levelupPoisonTolerance * diff
        self.baseSpellpower += self.levelupSpellpower * diff
        self.baseStrength += self.levelupStrength * diff
        
        
    def adjustMaxHP(self, numberOfPlayers):
        if numberOfPlayers == 1:
            pass
        elif numberOfPlayers == 2:
            self.baseHP = round(self.baseHP * 1.5)
        elif numberOfPlayers == 3:
            self.baseHP = round(self.baseHP * 2)
        elif numberOfPlayers == 4:
            self.baseHP = round(self.baseHP * 2.5)
        
    def getDetailTuple(self):
        '''First argument should represent which type of object this is.'''
        return ("Monster", self.name, self.level)
        
    def getIdentifier(self):
        tup = self.getDetailTuple()
        return tup[0] + ": " + tup[1] + " " + tup[2]
        # Insert location here?