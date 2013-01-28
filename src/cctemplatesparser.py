#!/usr/bin/python

import sys
import re
import playercharacter
import statuseffectsparser as sep



class CCTemplatesParser(object):

    def __init__(self):
        """Prepares the parser.  
        Possible states are:
          "Expecting Name" -- not currently parsing an object, 
             may have just finished parsing an object.
          "Expecting..."
          """
        self.state = "Expecting Name"
        self.NUM_CHARACTER_CLASSES = 16
    
    characterClassTemplates = []
    
    @staticmethod
    def getFromText(file, currentLine, tag):
        if( currentLine == "" ): 
            # This is EOF
            return "EOF"
        currentLine = currentLine.strip()
        while( sep.StatusEffectsParser.isEmptyText(currentLine) ):
            currentLine = file.readline().strip()
        if( tag.match(currentLine) ):
            return tag.match(currentLine).group(1)
        else:
            return "Parsing Error: " + currentLine
            
    
    def parseAll(self, fileName):
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
                CCTemplatesParser.characterClassTemplates.append(ccDict)
                
        f.close()        
        
if __name__ == "__main__":
    parser = CCTemplatesParser()
    parser.parseAll("./data/Character_Class_Data.txt")
    for ccDict in CCTemplatesParser.characterClassTemplates:
        print ccDict['name']
        print ccDict['skillGrowth']
        print ccDict['moveAP']
        print ccDict['levelupMP']
    
                
        
        