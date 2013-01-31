#!/usr/bin/python

import sys
import dice
import combat
import entity as e

class Equipment(e.Entity):

    ERROR = "INITIALIZATION_FAILURE"
    
    @staticmethod
    def setFrom(argDict, variableName, defaultValue):
        if( (variableName not in argDict) or (argDict[variableName] == "None") ):
            if defaultValue == Person.ERROR:
                raise IncompleteDataInitialization( "The parameter: " + variableName + " must be specified, but isn't.")
            else:
                return defaultValue
        else:
            return argDict[variableName]

    def __init__(self, name, goldValue, weight):
        e.Entity.__init__(self)
        self.name = name
        self.goldValue = goldValue
        self.weight = weight
        self.identifier = "TODO"    
    
class Armor(Equipment):
    def __init__(self, argDict):
        Equipment.__init__(self, argDict['name'], argDict['goldValue'], argDict['weight'])
        # TODO
    
        
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
        
    def cloneWithMagicalProperties(self, propertyList):
        """Method applys magical properties to a clone of the item according 
        to the properties passed to it.  This method will not select which
        properties are given.  This method WILL adjust the gold value,
        possibly the damage Min and Max, and definitely the 'identifier'.
        Inputs:
          propertyList -- MagicalProperty[]; the list of properties to apply
        Outputs:
          Weapon"""
        pass 
        #TODO
        
        
        
        
        
        
        
        