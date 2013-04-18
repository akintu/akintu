#!/usr/bin/python

import sys
import re
import equipment as eq
import statuseffectsparser as sep

# armorparser.py
# Author: Devin Ekins -- G. Cube
#
# This module simply parses the Armor_Data.txt file in such a fashion that
# Akintu will be able to make use of it after one execution.  It contains
# only one method that matters to the outside, parseAll() which will 
# load all data at startup time.

class EOFReached(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ArmorParser(object):

    def __init__(self):
        """Prepares the parser."""
        self.MAX_ARMORS = 24
        self.armorList = []


    @staticmethod
    def getFromText(file, currentLine, tag):
        currentLine = currentLine.strip()
        while( sep.StatusEffectsParser.isEmptyText(currentLine) ):
            currentLine = file.readline().strip()
        if( tag.match(currentLine) ):
            value = tag.match(currentLine).group(1)
            try:
                value = int(value)
            except ValueError:
                pass
            return value
        else:
            print "Parsing Error: " + currentLine
            return "ERROR!"


    def parseAll(self, fileName):
        nameTag = re.compile("(?:\[Name: )(.*)(?:\])", re.I)
        bonusModTag = re.compile("(?:\[Bonus Mod: )(.*)(?:\])", re.I)
        bonusTendencyOneTag = re.compile("(?:\[Bonus Tendency 1: )(.*)(?:\])", re.I)
        bonusTendencyTwoTag = re.compile("(?:\[Bonus Tendency 2: )(.*)(?:\])", re.I)
        bonusTendencyThreeTag = re.compile("(?:\[Bonus Tendency 3: )(.*)(?:\])", re.I)
        bonusTendencyFourTag = re.compile("(?:\[Bonus Tendency 4: )(.*)(?:\])", re.I)
        bonusTendencyFiveTag = re.compile("(?:\[Bonus Tendency 5: )(.*)(?:\])", re.I)
        bonusTendencySixTag = re.compile("(?:\[Bonus Tendency 6: )(.*)(?:\])", re.I)
        dodgeModTag = re.compile("(?:\[Dodge Mod: )(.*)(?:\])", re.I)
        DRTag = re.compile("(?:\[DR: )(.*)(?:\])", re.I)
        DRGradientTag = re.compile("(?:\[DR Gradient: )(.*)(?:\])", re.I)
        goldValueTag = re.compile("(?:\[Gold Value: )(.*)(?:\])", re.I)
        stealthModTag = re.compile("(?:\[Stealth Mod: )(.*)(?:\])", re.I)
        typeTag = re.compile("(?:\[Type: )(.*)(?:\])", re.I)
        gradeTag = re.compile("(?:\[Grade: )(.*)(?:\])", re.I)
        weightTag = re.compile("(?:\[Weight: )(.*)(?:\])", re.I)

        with open(fileName, 'r') as f:
            for i in range(self.MAX_ARMORS):
                armorDict = {}
                armorDict['name'] = ArmorParser.getFromText(f, f.readline(), nameTag)
                armorDict['bonusMod'] = ArmorParser.getFromText(f, f.readline(), bonusModTag)
                armorDict['bonusTendencyOne'] = ArmorParser.getFromText(f, f.readline(), bonusTendencyOneTag)
                armorDict['bonusTendencyTwo'] = ArmorParser.getFromText(f, f.readline(), bonusTendencyTwoTag)
                armorDict['bonusTendencyThree'] = ArmorParser.getFromText(f, f.readline(), bonusTendencyThreeTag)
                armorDict['bonusTendencyFour'] = ArmorParser.getFromText(f, f.readline(), bonusTendencyFourTag)
                armorDict['bonusTendencyFive'] = ArmorParser.getFromText(f, f.readline(), bonusTendencyFiveTag)
                armorDict['bonusTendencySix'] = ArmorParser.getFromText(f, f.readline(), bonusTendencySixTag)
                armorDict['dodgeMod'] = ArmorParser.getFromText(f, f.readline(), dodgeModTag)
                armorDict['DR'] = ArmorParser.getFromText(f, f.readline(), DRTag)
                armorDict['DRGradient'] = ArmorParser.getFromText(f, f.readline(), DRGradientTag)
                armorDict['goldValue'] = ArmorParser.getFromText(f, f.readline(), goldValueTag)
                armorDict['stealthMod'] = ArmorParser.getFromText(f, f.readline(), stealthModTag)
                armorDict['type'] = ArmorParser.getFromText(f, f.readline(), typeTag)
                armorDict['grade'] = ArmorParser.getFromText(f, f.readline(), gradeTag)
                armorDict['weight'] = ArmorParser.getFromText(f, f.readline(), weightTag)
                self.armorList.append(armorDict)

        return self.armorList

if __name__ == "__main__":
    parser = ArmorParser()
    parser.parseAll("./data/Armor_Data.txt")
    for armorDict in parser.armorList:
        for k in armorDict.keys():
            print k + " : " + str(armorDict[k])
        print "\n"





