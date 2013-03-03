#!/usr/bin/python

import sys
import re
import playercharacter
import statuseffectsparser as sep
import theorycraft

class CCTemplatesParser(object):

    def __init__(self):
        """Prepares the parser."""
        self.NUM_CHARACTER_CLASSES = 16
        self.NUM_RACES = 6
        self.combos = []

    characterClassTemplates = []
    races = []

    @staticmethod
    def getFromText(file, currentLine, tag):
        if( currentLine == "" ):
            # An empty string indicates the EOF.
            return "EOF"
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

    def parseAllRaces(self, fileName):
        nameTag = re.compile("(?:\[NAME: )(.*)(?:\])", re.I)
        startingAwarenessTag = re.compile("(?:\[STARTING_AWARENESS: )(.*)(?:\])", re.I)
        startingConstitutionTag = re.compile("(?:\[STARTING_CON: )(.*)(?:\])", re.I)
        startingCunningTag = re.compile("(?:\[STARTING_CUN: )(.*)(?:\])", re.I)
        startingDROutsideTag = re.compile("(?:\[STARTING_DAMAGE_REDUCTION_OUTSIDE: )(.*)(?:\])", re.I)
        startingDexterityTag = re.compile("(?:\[STARTING_DEX: )(.*)(?:\])", re.I)
        startingHPTag = re.compile("(?:\[STARTING_HP: )(.*)(?:\])", re.I)
        startingMagicResistTag =  re.compile("(?:\[STARTING_MAGIC_RESIST: )(.*)(?:\])", re.I)
        startingMPTag = re.compile("(?:\[STARTING_MP: )(.*)(?:\])", re.I)
        startingPietyTag = re.compile("(?:\[STARTING_PIE: )(.*)(?:\])", re.I)
        startingPoisonToleranceTag = re.compile("(?:\[STARTING_POISON_TOLERANCE: )(.*)(?:\])", re.I)
        startingRangedAccuracyTag = re.compile("(?:\[STARTING_RANGED_ACCURACY: )(.*)(?:\])", re.I)
        startingSneakTag = re.compile("(?:\[STARTING_SNEAK: )(.*)(?:\])", re.I)
        startingSorceryTag = re.compile("(?:\[STARTING_SOR: )(.*)(?:\])", re.I)
        startingStrengthTag = re.compile("(?:\[STARTING_STR: )(.*)(?:\])", re.I)

        with open(fileName, 'r') as f:
            for i in range(self.NUM_RACES):
                raceDict = {}
                raceDict['name'] = CCTemplatesParser.getFromText(f, f.readline(), nameTag)
                raceDict['startingAwareness'] = CCTemplatesParser.getFromText(f, f.readline(), startingAwarenessTag)
                raceDict['startingConstitution'] = CCTemplatesParser.getFromText(f, f.readline(), startingConstitutionTag)
                raceDict['startingCunning'] = CCTemplatesParser.getFromText(f, f.readline(), startingCunningTag)
                raceDict['startingDROutside'] = CCTemplatesParser.getFromText(f, f.readline(), startingDROutsideTag)
                raceDict['startingDexterity'] = CCTemplatesParser.getFromText(f, f.readline(), startingDexterityTag)
                raceDict['startingHP'] = CCTemplatesParser.getFromText(f, f.readline(), startingHPTag)
                raceDict['startingMagicResist'] = CCTemplatesParser.getFromText(f, f.readline(), startingMagicResistTag)
                raceDict['startingMP'] = CCTemplatesParser.getFromText(f, f.readline(), startingMPTag)
                raceDict['startingPiety'] = CCTemplatesParser.getFromText(f, f.readline(), startingPietyTag)
                raceDict['startingPoisonTolerance'] = CCTemplatesParser.getFromText(f, f.readline(), startingPoisonToleranceTag)
                raceDict['startingRangedAccuracy'] = CCTemplatesParser.getFromText(f, f.readline(), startingRangedAccuracyTag)
                raceDict['startingSneak'] = CCTemplatesParser.getFromText(f, f.readline(), startingSneakTag)
                raceDict['startingSorcery'] = CCTemplatesParser.getFromText(f, f.readline(), startingSorceryTag)
                raceDict['startingStrength'] = CCTemplatesParser.getFromText(f, f.readline(), startingStrengthTag)
                CCTemplatesParser.races.append(raceDict)




    def parseAllCC(self, fileName):
        nameTag = re.compile("(?:\[NAME: )(.*)(?:\])", re.I)
        baseCCTag = re.compile("(?:\[BASE_CLASS: )(.*)(?:\])", re.I)
        secondaryCCTag = re.compile("(?:\[SEC_CLASS: )(.*)(?:\])", re.I)
        skillGrowthTag = re.compile("(?:\[SKILL_GROWTH: )(.*)(?:\])", re.I)
        armorToleranceTag = re.compile("(?:\[ARMOR_TOLERANCE: )(.*)(?:\])", re.I)
        moveAPTag = re.compile("(?:\[MOVE_AP: )(.*)(?:\])", re.I)
        meleeAPTag = re.compile("(?:\[MELEE_AP: )(.*)(?:\])", re.I)
        rangedAPTag = re.compile("(?:\[RANGED_AP: )(.*)(?:\])", re.I)
        spellOneTag = re.compile("(?:\[STARTING_SPELL_1: )(.*)(?:\])", re.I)
        spellTwoTag = re.compile("(?:\[STARTING_SPELL_2: )(.*)(?:\])", re.I)
        spellThreeTag = re.compile("(?:\[STARTING_SPELL_3: )(.*)(?:\])", re.I)
        # Starting gear -- TODO
        startingStrengthTag = re.compile("(?:\[STARTING_STR: )(.*)(?:\])", re.I)
        startingDexterityTag = re.compile("(?:\[STARTING_DEX: )(.*)(?:\])", re.I)
        startingCunningTag = re.compile("(?:\[STARTING_CUN: )(.*)(?:\])", re.I)
        startingSorceryTag = re.compile("(?:\[STARTING_SOR: )(.*)(?:\])", re.I)
        startingPietyTag = re.compile("(?:\[STARTING_PIE: )(.*)(?:\])", re.I)
        startingConstitutionTag = re.compile("(?:\[STARTING_CON: )(.*)(?:\])", re.I)
        startingHPTag = re.compile("(?:\[STARTING_HP: )(.*)(?:\])", re.I)
        startingMPTag = re.compile("(?:\[STARTING_MP: )(.*)(?:\])", re.I)
        levelupStrengthTag = re.compile("(?:\[LEVELUP_STR: )(.*)(?:\])", re.I)
        levelupDexterityTag = re.compile("(?:\[LEVELUP_DEX: )(.*)(?:\])", re.I)
        levelupCunningTag = re.compile("(?:\[LEVELUP_CUN: )(.*)(?:\])", re.I)
        levelupSorceryTag = re.compile("(?:\[LEVELUP_SOR: )(.*)(?:\])", re.I)
        levelupPietyTag = re.compile("(?:\[LEVELUP_PIE: )(.*)(?:\])", re.I)
        levelupConstitutionTag = re.compile("(?:\[LEVELUP_CON: )(.*)(?:\])", re.I)
        levelupHPTag = re.compile("(?:\[LEVELUP_HP: )(.*)(?:\])", re.I)
        levelupMPTag = re.compile("(?:\[LEVELUP_MP: )(.*)(?:\])", re.I)
        imageTag = re.compile("(?:\[IMAGE: )(.*)(?:\])")

        with open(fileName, 'r') as f:
            for i in range(self.NUM_CHARACTER_CLASSES):
                ccDict = {}
                ccDict['name'] = CCTemplatesParser.getFromText(f, f.readline(), nameTag)
                ccDict['baseCC'] = CCTemplatesParser.getFromText(f, f.readline(), baseCCTag)
                ccDict['secondaryCC'] = CCTemplatesParser.getFromText(f, f.readline(), secondaryCCTag)
                ccDict['skillGrowth'] = CCTemplatesParser.getFromText(f, f.readline(), skillGrowthTag)
                ccDict['armorTolerance'] = CCTemplatesParser.getFromText(f, f.readline(), armorToleranceTag)
                ccDict['moveAP'] = CCTemplatesParser.getFromText(f, f.readline(), moveAPTag)
                ccDict['meleeAP'] = CCTemplatesParser.getFromText(f, f.readline(), meleeAPTag)
                ccDict['rangedAP'] = CCTemplatesParser.getFromText(f, f.readline(), rangedAPTag)
                ccDict['spellOne'] = CCTemplatesParser.getFromText(f, f.readline(), spellOneTag)
                ccDict['spellTwo'] = CCTemplatesParser.getFromText(f, f.readline(), spellTwoTag)
                ccDict['spellThree'] = CCTemplatesParser.getFromText(f, f.readline(), spellThreeTag)
                ccDict['startingStrength'] = CCTemplatesParser.getFromText(f, f.readline(), startingStrengthTag)
                ccDict['startingDexterity'] = CCTemplatesParser.getFromText(f, f.readline(), startingDexterityTag)
                ccDict['startingCunning'] = CCTemplatesParser.getFromText(f, f.readline(), startingCunningTag)
                ccDict['startingSorcery'] = CCTemplatesParser.getFromText(f, f.readline(), startingSorceryTag)
                ccDict['startingPiety'] = CCTemplatesParser.getFromText(f, f.readline(), startingPietyTag)
                ccDict['startingConstitution'] = CCTemplatesParser.getFromText(f, f.readline(), startingConstitutionTag)
                ccDict['startingHP'] = CCTemplatesParser.getFromText(f, f.readline(), startingHPTag)
                ccDict['startingMP'] = CCTemplatesParser.getFromText(f, f.readline(), startingMPTag)
                ccDict['levelupStrength'] = CCTemplatesParser.getFromText(f, f.readline(), levelupStrengthTag)
                ccDict['levelupDexterity'] = CCTemplatesParser.getFromText(f, f.readline(), levelupDexterityTag)
                ccDict['levelupCunning'] = CCTemplatesParser.getFromText(f, f.readline(), levelupCunningTag)
                ccDict['levelupSorcery'] = CCTemplatesParser.getFromText(f, f.readline(), levelupSorceryTag)
                ccDict['levelupPiety'] = CCTemplatesParser.getFromText(f, f.readline(), levelupPietyTag)
                ccDict['levelupConstitution'] = CCTemplatesParser.getFromText(f, f.readline(), levelupConstitutionTag)
                ccDict['levelupHP'] = CCTemplatesParser.getFromText(f, f.readline(), levelupHPTag)
                ccDict['levelupMP'] = CCTemplatesParser.getFromText(f, f.readline(), levelupMPTag)
                ccDict['image'] = CCTemplatesParser.getFromText(f, f.readline(), imageTag)
                CCTemplatesParser.characterClassTemplates.append(ccDict)

    def combineRaceAndClass(self):
        comboDict = {}
        for ccDict in CCTemplatesParser.characterClassTemplates:
            for raceDict in CCTemplatesParser.races:
                comboDict = {}
                comboDict['name'] = raceDict['name'] + " " + ccDict['name']
                comboDict = self.combineNotName(ccDict, raceDict, comboDict)
                self.combos.append(comboDict)


    def combineNotName(self, dictA, dictB, resultDict):
        for keyA in dictA:
            for keyB in dictB:
                if (keyA != "name") and (keyA == keyB):
                    resultDict[keyA] = int(dictA[keyA]) + int(dictB[keyB])
                elif keyB not in dictA.keys():
                    resultDict[keyB] = dictB[keyB]
                elif keyA not in dictB.keys():
                    resultDict[keyA] = dictA[keyA]
        return resultDict

    def parseAll(self, ccFileName, raceFileName):
        self.parseAllCC(ccFileName)
        self.parseAllRaces(raceFileName)
        self.combineRaceAndClass()
        return self.combos

if __name__ == "__main__":
    parser = CCTemplatesParser()
    parser.parseAll("./data/Character_Class_Data.txt", "./data/Race_Data.txt")
    for combo in parser.combos:
        for k in combo.keys():
            print k + " : " + str(combo[k])
        print "\n"



