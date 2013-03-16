#!/usr/bin/python

import sys
import dice
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
            try:
                return int(argDict[variableName])
            except:
                return argDict[variableName]

    def __init__(self, name, value, weight):
        e.Entity.__init__(self)
        self.name = name
        self.displayName = self.name
        self.value = int(value)
        self.weight = weight
        self.identifier = "Uninitialized"
        self.bonusTendencyList = None
        self.details = "Uninitialized"
        self.prefix = ""
        self.suffix = ""

    def __eq__(self, other):
        if not isinstance(other, Equipment):
            return False
        if isinstance(self, Armor) and not isinstance(other, Armor):
            return False
        if isinstance(self, Weapon) and not isinstance(other, Weapon):
            return False
        if self.name != other.name:
            return False
        propNameList_1 = [(x.name, x.counts) for x in self.propertyList]
        propNameList_2 = [(x.name, x.counts) for x in other.propertyList]
        propNameSet_1 = set(propNameList_1)
        propNameSet_2 = set(propNameList_2)
        if propNameSet_1 != propNameSet_2:
            return False
        return True
        
    def __ne__(self, other):
        if self == other:
            return False
        return True
        
    def cloneWithMagicalProperties(self, ip, propList=None):
        """Method applys random magical properties.  This method WILL adjust the gold value,
        possibly the damage Min and Max, and definitely the 'identifier'.
        Inputs:
          ip -- int; the number of item points to use when determining the magical properties
                     of this item.
        Outputs:
          Equipment of the same type as was input (as self)"""
        propertyList = propList
        if not propList:
            propertyList = magicalproperty.MagicalProperty.generateProperties(self, ip)

        goldModSum = 0
        for property in propertyList:
            goldModSum += property.goldMod * property.counts

        newCopy = copy.copy(self)
        newCopy.value = round(self.value * (1 + float(goldModSum / 100)))
        for property in propertyList:
            property.item = newCopy
            if property.name == "Damage":
                property.effect(property, None) # No 'Owner' needed, thus None is passed.
            elif property.name == "DR":
                property.effect(property, None) # No 'Owner' needed, thus None is passed.
        newPropertyList = [x for x in propertyList if x.name != "Damage" and x.name != "DR"]
        newCopy.propertyList = newPropertyList
        newCopy.assignDisplayName()
        newCopy.assignIdentifier()
        newCopy.assignText()
        return newCopy

    def assignIdentifier(self):
        longName = []
        longName.append(self.name)
        for prop in self.propertyList:
            longName.append("$")
            longName.append(prop.name + "#" + `prop.counts`)
        self.identifier = ''.join(longName)
        
    def assignText(self):
        longText = []
        if self.prefix:
            longText.append(self.prefix + "\n")
        longText.append(self.name + "\n")
        if self.suffix:
            longText.append(self.suffix + "\n")
        longText.append("\n")
        if isinstance(self, Armor):
            longText.append("Grade: " + self.grade + "\n")
            longText.append("Type: " + self.type + "\n")
            longText.append("Damage Reduction (DR): " + `self.DR` + "%\n")
            longText.append("Dodge Modifier: " + `self.dodgeMod` + "\n")
            longText.append("Stealth Modifier: " + `self.stealthMod` + "\n")
            longText.append("Weight: " + `self.weight` + " lbs.\n")
            longText.append("Value: " + `int(self.value)` + " gold\n")
            for mProp in self.propertyList:
                longText.append(">> " + mProp.name + "  x " + `mProp.counts` + "\n")
        elif isinstance(self, Weapon):
            longText.append("Type: " + self.type + "\n")
            longText.append("Hands: " + self.handsRequired + "\n")
            longText.append("Base Damage: " + `(self.damageMin + self.damageMinBonus)` +
                        "-" + `(self.damageMax + self.damageMaxBonus)` + "\n")
            longText.append("Damage Type: " + self.damageType + "\n")
            longText.append("Force: " + `int(self.force)` + "%\n")
            longText.append("Critical Multiplier: " + `int(self.criticalMultiplier)` + "%\n")
            longText.append("Range: " + (`self.range` if self.range != 1 else "Melee") + "\n")
            longText.append("Weight: " + self.weight + " lbs.\n")
            longText.append("Value: " + `int(self.value)` + " gold\n")
            for mProp in self.propertyList:
                longText.append(">> " + mProp.name + "  x " + `mProp.counts` + "\n")
        self.details = ''.join(longText)
            
            
            
    def assignDisplayName(self):
        ''' Assigns a more colorful name to this item
        based on its magical properties.  If the item
        has no magical properties, it will not assign
        a different name. '''
        firstProperty = None
        secondProperty = None
        maxValue = 0
        for prop in self.propertyList:
            value = prop.cost * prop.counts
            if value > maxValue or \
              (firstProperty and value == maxValue and prop.name > firstProperty.name):
                secondProperty = firstProperty
                firstProperty = prop
                maxValue = value
        if firstProperty and secondProperty:
            self.displayName = secondProperty.prefix + " " + self.name + " " + firstProperty.suffix
            self.prefix = secondProperty.prefix
            self.suffix = firstProperty.suffix
        elif firstProperty:
            self.displayName = self.name + " " + firstProperty.suffix
            self.suffix = firstProperty.suffix
        else:
            self.displayName = self.name
            
            
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
    def __init__(self, argDict):
        Equipment.__init__(self, argDict['name'], argDict['goldValue'], argDict['weight'])
        self.type = argDict['type']
        self.handsRequired = Equipment.setFrom(argDict, 'handsRequired')
        baseList = Equipment.setFrom(argDict, 'damageBase').split("-")
        self.damageMin = int(baseList[0])
        self.damageMax = int(baseList[1])
        gradList = Equipment.setFrom(argDict, 'damageGradient').split("-")  # 1-2,3     --> "1" "2,3"
        self.gradientMin = int(gradList[0])
        gradSubList = gradList[1].split(",")  # "1" "2,3" --> "2,3" --> "2" "3"
        self.gradientMax = int(gradSubList[0])
        self.gradientPoints = int(gradSubList[1])
        self.damageType = Equipment.setFrom(argDict, 'damageType')
        self.force = Equipment.setFrom(argDict, 'force')
        self.criticalMultiplier = Equipment.setFrom(argDict, 'criticalMultiplier')
        self.bonusTendencyList = Equipment.setFrom(argDict, 'bonusTendencyList')
        self.bonusMod = Equipment.setFrom(argDict, 'bonusMod')
        self.range = Equipment.setFrom(argDict, 'range')
        self.identifier = "TODO: " + self.name
        self.propertyList = []

        self.damageMinBonus = 0
        self.damageMaxBonus = 0











