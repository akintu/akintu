#!/usr/bin/python

import sys
import re
import equipment
import statuseffectsparser



class WeaponsParser(object):

    def __init__(self):
        """Prepares the parser.  
        Possible states are:
          "Expecting Name" -- not currently parsing an object, 
             may have just finished parsing an object.
          "Expecting Type"
          "Expecting Class"
          "Expecting Damage Base"
          "Expecting Damage Gradient"
          "Expecting Damage Type"
          "Expecting Force"
          "Expecting Crit Mult"
          "Expecting Bonus Tendency"
          "Expecting Gold Value"
          "Expecting Weight"
          "Expecting Range"
          """
        self.state = "Expecting Name"
    
    weaponList = []
    
    def parseAll(self, fileName):
        nameTag = re.compile("(?:\[NAME: )(.*)(?:\])", re.I)
        typeTag = re.compile("(?:\[TYPE: )(.*)(?:\])", re.I)
        wepClassTag = re.compile("(?:\[CLASS: )(.*)(?:\])", re.I)
        dBaseTag = re.compile("(?:\[DAMAGE_BASE: )(.*)(?:\])", re.I)
        dGradTag = re.compile("(?:\[DAMAGE_GRADIENT: )(.*)(?:\])", re.I)
        dTypeTag = re.compile("(?:\[DAMAGE_TYPE: )(.*)(?:\])", re.I)
        forceTag = re.compile("(?:\[FORCE: )(.*)\%(?:\])", re.I)
        critTag = re.compile("(?:\[CRITICAL_MULTIPLIER: )(.*)\%(?:\])", re.I)
        bonusTendencyTag = re.compile("(?:\[BONUS_TENDENCY: )(.*)\%(?:\])", re.I)
        bonusModTag = re.compile("(?:\[BONUS_MOD: )(.*)(?:\])", re.I)
        goldTag = re.compile("(?:\[GOLD_VALUE: )(.*)(?:\])", re.I)
        weightTag = re.compile("(?:\[WEIGHT: )(.*)(?:\])", re.I)
        rangeTag = re.compile("(?:\[RANGE: )(.*)(?:\])", re.I)
        
        f = open(fileName, 'r')
        
        name = None
        wType = None
        wepClass = None
        dBase = None
        dGrad = None
        dType = None
        force = None
        crit = None
        bonusTendencyList = None
        bonusMod = None
        gold = None
        weight = None
        wRange = None
        
        for line in f:
            line = line.strip()
            
            if(self.state == "Expecting Name"):
                name = None
                wType = None
                wepClass = None
                dBase = None
                dGrad = None
                dType = None
                force = None
                crit = None
                bonusTendencyList = []
                bonusMod = None
                gold = None
                weight = None
                wRange = None
                if( statuseffectsparser.StatusEffectsParser.isEmptyText(line) ):
                    continue
                name = nameTag.match(line).group(1)
                self.state = "Expecting Type"
                continue
                
            if(self.state == "Expecting Type"):
                wType = typeTag.match(line).group(1)
                self.state = "Expecting Class"
                continue
                
            if(self.state == "Expecting Class"):
                wepClass = wepClassTag.match(line).group(1)
                if(wepClass == "1H-"):
                    wepClass = "One-Handed"
                elif(wepClass == "1HX"):
                    wepClass = "One-Handed Exclusive"
                elif(wepClass == "2H"):
                    wepClass = "Two-Handed"
                self.state = "Expecting Damage Base"
                continue
                
            if(self.state == "Expecting Damage Base"):
                dBase = dBaseTag.match(line).group(1)
                self.state = "Expecting Damage Gradient"
                continue
                
            if(self.state == "Expecting Damage Gradient"):
                dGrad = dGradTag.match(line).group(1)
                self.state = "Expecting Damage Type"
                continue
                
            if(self.state == "Expecting Damage Type"):
                dType = dTypeTag.match(line).group(1)
                self.state = "Expecting Force"
                continue
                
            if(self.state == "Expecting Force"):
                force = forceTag.match(line).group(1)
                self.state = "Expecting Crit Mult"
                continue
                
            if(self.state == "Expecting Crit Mult"):
                crit = critTag.match(line).group(1)
                self.state = "Expecting Bonus Tendency"
                continue
        
            if(self.state == "Expecting Bonus Tendency"):
                if( bonusTendencyTag.match(line) ):
                    bonusTendencyList.append(bonusTendencyTag.match(line).group(1))
                elif( bonusModTag.match(line) ):
                    bonusMod = bonusModTag.match(line).group(1)
                    self.state = "Expecting Gold Value"
                continue
                
            if(self.state == "Expecting Gold Value"):
                gold = goldTag.match(line).group(1)
                self.state = "Expecting Weight"
                continue
                
            if(self.state == "Expecting Weight"):
                weight = weightTag.match(line).group(1)
                self.state = "Expecting Range"
                continue
                
            if(self.state == "Expecting Range"):
                wRange = rangeTag.match(line).group(1)
                self.state = "Expecting Name"
                weapon = equipment.Weapon(name, gold, weight, wType, wepClass, dBase, dGrad, dType,
                                force, crit, bonusTendencyList, bonusMod, wRange)
                WeaponsParser.weaponList.append(weapon)
                continue
                
            raise statuseffectsparser.InvalidDataFileSyntax("Unknown Tag: " + line + " .")
                    
        f.close()
        
if __name__ == "__main__":
    parser = WeaponsParser()
    parser.parseAll("./data/Weapon_Data.txt")
    for wep in WeaponsParser.weaponList:
        print wep.name
        print wep.criticalMultiplier
        print wep.goldValue
        print wep.bonusTendencyList
        