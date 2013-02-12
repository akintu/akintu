#!/usr/bin/python

import sys
import dice
import combat
import entity as e
import magicalproperty
import copy

class Equipment(e.Entity):

    ERROR = "INITIALIZATION_FAILURE"
    
    @staticmethod
    def setFrom(argDict, variableName, defaultValue=ERROR):
        if( (variableName not in argDict) or (argDict[variableName] == "None") ):
            if defaultValue == Equipment.ERROR:
                raise IncompleteDataInitialization( "The parameter: " + variableName + " must be specified, but isn't.")
            else:
                return defaultValue
        else:
            return argDict[variableName]

    def __init__(self, name, goldValue, weight):
        e.Entity.__init__(self)
        self.name = name
        self.goldValue = int(goldValue)
        self.weight = weight
        self.identifier = "TODO"
        self.bonusTendencyList = None        
    
    def cloneWithMagicalProperties(self, ip):
        """Method applys random magical properties.  This method WILL adjust the gold value,
        possibly the damage Min and Max, and definitely the 'identifier'.
        Inputs:
          ip -- int; the number of item points to use when determining the magical properties
                     of this item.
        Outputs:
          Equipment of the same type as was input (as self)"""
        propertyList = magicalproperty.MagicalProperty.generateProperties(self, ip)
          
        newIdentifier = self.name
        goldModSum = 0
        for property in propertyList:
            goldModSum += property.goldMod * property.counts
            newIdentifier += " ; mProp: " + property.name + " counts: " + str(property.counts)  

        newCopy = copy.copy(self)
        print self.goldValue
        newCopy.goldValue = round(self.goldValue * (1 + float(goldModSum / 100)))
        newCopy.identifier = newIdentifier
        for property in propertyList:
            property.item = newCopy
            if property.name == "Damage":
                property.effect(property, None) # No 'Owner' needed, thus None is passed.
            elif property.name == "DR":
                property.effect(property, None) # No 'Owner' needed, thus None is passed.       
        newPropertyList = [x for x in propertyList if x.name != "Damage" and x.name != "DR"]
        newCopy.propertyList = newPropertyList
        return newCopy
        
class Armor(Equipment):
    def __init__(self, argDict):
        Equipment.__init__(self, argDict['name'], argDict['goldValue'], argDict['weight'])
        self.type = Equipment.setFrom(argDict, 'type')
        self.grade = Equipment.setFrom(argDict, 'grade')
        self.gradePoints = Armor.convertToGradePoints(self.grade, self.type)
        self.dodgeMod = Equipment.setFrom(argDict, 'dodgeMod')
        self.stealthMod = Equipment.setFrom(argDict, 'stealthMod')
        self.DR = Equipment.setFrom(argDict, 'DR')
        
        gradientBundle = Equipment.setFrom(argDict, 'DRGradient')
        self.DRGradient = int(gradientBundle.split(",")[0])
        self.DRGradientPoints = int(gradientBundle.split(",")[1])
                
        self.bonusMod = Equipment.setFrom(argDict, 'bonusMod')
        bonusOne = Equipment.setFrom(argDict, 'bonusTendencyOne', None)
        bonusTwo = Equipment.setFrom(argDict, 'bonusTendencyTwo', None)
        bonusThree = Equipment.setFrom(argDict, 'bonusTendencyThree', None)
        bonusFour = Equipment.setFrom(argDict, 'bonusTendencyFour', None)
        bonusFive = Equipment.setFrom(argDict, 'bonusTendencyFive', None)
        bonusSix = Equipment.setFrom(argDict, 'bonusTendencySix', None)
        self.bonusTendencyList = []
        if bonusOne:
            self.bonusTendencyList.append(bonusOne)
        if bonusTwo:
            self.bonusTendencyList.append(bonusTwo)
        if bonusThree:
            self.bonusTendencyList.append(bonusThree)
        if bonusFour:
            self.bonusTendencyList.append(bonusFour)
        if bonusFive:
            self.bonusTendencyList.append(bonusFive)
        if bonusSix:
            self.bonusTendencyList.append(bonusSix)
            
        self.propertyList = []
        self.identifier = "TODO: " + self.name
        
        self.DRBonus = 0
            
    @staticmethod
    def convertToGradePoints(grade, type):
        points = 0
        if grade == "Heavy":
            points = 3
        elif grade == "Medium":
            points = 2
        elif grade == "Light":
            points = 1
            
        if type == "Head" or type == "Hands" or type == "Feet":
            pass
        elif type == "Legs" or type == "Shield":
            points *= 2
        elif type == "Chest":
            points *= 3
        return points
        
class Weapon(Equipment):
    def __init__(self, name, goldValue, weight, type, handsRequired, 
                 damageBase, damageGradient, damageType,
                 force, criticalMultiplier, bonusTendencyList, 
                 bonusMod, range):
        Equipment.__init__(self, name, goldValue, weight)
        self.type = type
        self.handsRequired = handsRequired
        baseList = damageBase.split("-")
        self.damageMin = baseList[0]
        self.damageMax = baseList[1]
        gradList = damageGradient.split("-")  # 1-2,3     --> "1" "2,3"
        self.gradientMin = gradList[0]
        gradSubList = gradList[1].split(",")  # "1" "2,3" --> "2,3" --> "2" "3"
        self.gradientMax = gradSubList[0]
        self.gradientPoints = gradSubList[1]
        self.damageType = damageType
        self.force = force
        self.criticalMultiplier = criticalMultiplier
        self.bonusTendencyList = bonusTendencyList
        self.bonusMod = bonusMod
        self.range = range
        self.identifier = "TODO: " + self.name
        self.propertyList = []
        
        self.damageMinBonus = 0
        self.damageMaxBonus = 0
        

        
        
        
        
        
        
        
        
        