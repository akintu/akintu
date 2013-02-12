#!/usr/bin/python

import sys
import re
import monster
import statuseffectsparser as sep

class MonstersParser(object):

    def __init__(self):
        self.allMonsters = []

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
    
    def parseAll(self, fileName):
        nameTag = re.compile("(?:\[NAME: )(.*)(?:\])", re.I)
        APTag = re.compile("(?:\[AP: )(.*)(?:\])", re.I)
        armorPenetrationTag = re.compile("(?:\[BASIC ATTACK ARMOR PENETRATION: )(.*)(?:\])", re.I)
        attackElementTag = re.compile("(?:\[BASIC ATTACK ELEMENT: )(.*)(?:\])", re.I)
        attackMinTag = re.compile("(?:\[BASIC ATTACK MIN: )(.*)(?:\])", re.I)
        attackMaxTag = re.compile("(?:\[BASIC ATTACK MAX: )(.*)(?:\])", re.I)
        attackRangeTag = re.compile("(?:\[BASIC ATTACK RANGE: )(.*)(?:\])", re.I)
        cunningTag = re.compile("(?:\[CUNNING: )(.*)(?:\])", re.I)
        dexterityTag = re.compile("(?:\[DEXTERITY: )(.*)(?:\])", re.I)
        DRTag = re.compile("(?:\[DR: )(.*)(?:\])", re.I)
        arcaneResistTag = re.compile("(?:\[ELEMENTAL RESIST ARCANE: )(.*)(?:\])", re.I)
        coldResistTag = re.compile("(?:\[ELEMENTAL RESIST COLD: )(.*)(?:\])", re.I)
        divineResistTag = re.compile("(?:\[ELEMENTAL RESIST DIVINE: )(.*)(?:\])", re.I)
        electricResistTag = re.compile("(?:\[ELEMENTAL RESIST ELECTRIC: )(.*)(?:\])", re.I)
        fireResistTag = re.compile("(?:\[ELEMENTAL RESIST FIRE: )(.*)(?:\])", re.I)
        poisonResistTag = re.compile("(?:\[ELEMENTAL RESIST POISON: )(.*)(?:\])", re.I)
        shadowResistTag = re.compile("(?:\[ELEMENTAL RESIST SHADOW: )(.*)(?:\])", re.I)
        experienceTag = re.compile("(?:\[EXPERIENCE GIVEN: )(.*)(?:\])", re.I)
        GPTag = re.compile("(?:\[GP: )(.*)(?:\])", re.I)
        HPTag = re.compile("(?:\[HP: )(.*)(?:\])", re.I)
        imageTag = re.compile("(?:\[IMAGE: )(.*)(?:\])", re.I)
        levelTag = re.compile("(?:\[LEVEL: )(.*)(?:\])", re.I)
        magicResistTag = re.compile("(?:\[MAGIC RESIST: )(.*)(?:\])", re.I)
        meleeAPTag = re.compile("(?:\[MELEE ATTACK AP: )(.*)(?:\])", re.I)
        moveAPTag = re.compile("(?:\[MOVE AP: )(.*)(?:\])", re.I)
        moveTilesTag = re.compile("(?:\[MOVE TILES: )(.*)(?:\])", re.I)
        MPTag = re.compile("(?:\[MP: )(.*)(?:\])", re.I)
        poisonToleranceTag = re.compile("(?:\[POISON TOLERANCE: )(.*)(?:\])", re.I)
        rangedAPTag = re.compile("(?:\[RANGED ATTACK AP: )(.*)(?:\])", re.I)
        sizeTag = re.compile("(?:\[SIZE: )(.*)(?:\])", re.I)
        specialAttackOneTag = re.compile("(?:\[SPECIAL ATTACK 1: )(.*)(?:\])", re.I)
        specialAttackTwoTag = re.compile("(?:\[SPECIAL ATTACK 2: )(.*)(?:\])", re.I)
        specialAttackThreeTag = re.compile("(?:\[SPECIAL ATTACK 3: )(.*)(?:\])", re.I)
        specialPropertyTag = re.compile("(?:\[SPECIAL PROPERTY: )(.*)(?:\])", re.I)
        spellpowerTag = re.compile("(?:\[SPELLPOWER: )(.*)(?:\])", re.I)
        strengthTag = re.compile("(?:\[STRENGTH: )(.*)(?:\])", re.I)
        
        
        with open(fileName, 'r') as f:
            while( True ):
                mDict = {}
                mDict['name'] = MonstersParser.getFromText(f, f.readline(), nameTag)
                if mDict['name'] == "EOF":
                    break
                mDict['AP'] = MonstersParser.getFromText(f, f.readline(), APTag)
                mDict['startingArmorPenetration'] = MonstersParser.getFromText(f, f.readline(), armorPenetrationTag)
                mDict['attackElement'] = MonstersParser.getFromText(f, f.readline(), attackElementTag)
                mDict['attackMin'] = MonstersParser.getFromText(f, f.readline(), attackMinTag)
                mDict['attackMax'] = MonstersParser.getFromText(f, f.readline(), attackMaxTag)
                mDict['attackRange'] = MonstersParser.getFromText(f, f.readline(), attackRangeTag)
                mDict['startingCunning'] = MonstersParser.getFromText(f, f.readline(), cunningTag)
                mDict['startingDexterity'] = MonstersParser.getFromText(f, f.readline(), dexterityTag)
                mDict['startingDR'] = MonstersParser.getFromText(f, f.readline(), DRTag)
                mDict['startingArcaneResistance'] = MonstersParser.getFromText(f, f.readline(), arcaneResistTag)
                mDict['startingColdResistance'] = MonstersParser.getFromText(f, f.readline(), coldResistTag)
                mDict['startingDivineResistance'] = MonstersParser.getFromText(f, f.readline(), divineResistTag)
                mDict['startingElectricResistance'] = MonstersParser.getFromText(f, f.readline(), electricResistTag)
                mDict['startingFireResistance'] = MonstersParser.getFromText(f, f.readline(), fireResistTag)
                mDict['startingPoisonResistance'] = MonstersParser.getFromText(f, f.readline(), poisonResistTag)
                mDict['startingShadowResistance'] = MonstersParser.getFromText(f, f.readline(), shadowResistTag)
                mDict['experience'] = MonstersParser.getFromText(f, f.readline(), experienceTag)
                mDict['GP'] = MonstersParser.getFromText(f, f.readline(), GPTag)
                mDict['startingHP'] = MonstersParser.getFromText(f, f.readline(), HPTag)
                mDict['image'] = MonstersParser.getFromText(f, f.readline(), imageTag)
                mDict['level'] = MonstersParser.getFromText(f, f.readline(), levelTag)
                mDict['magicResist'] = MonstersParser.getFromText(f, f.readline(), magicResistTag)
                mDict['meleeAP'] = MonstersParser.getFromText(f, f.readline(), meleeAPTag)
                mDict['moveAP'] = MonstersParser.getFromText(f, f.readline(), moveAPTag)
                mDict['movementTiles'] = MonstersParser.getFromText(f, f.readline(), moveTilesTag)
                mDict['startingMP'] = MonstersParser.getFromText(f, f.readline(), MPTag)
                mDict['startingPoisonTolerance'] = MonstersParser.getFromText(f, f.readline(), poisonToleranceTag)
                mDict['rangedAP'] = MonstersParser.getFromText(f, f.readline(), rangedAPTag)
                mDict['size'] = MonstersParser.getFromText(f, f.readline(), sizeTag)
                mDict['specialAttackOne'] = MonstersParser.getFromText(f, f.readline(), specialAttackOneTag)
                mDict['specialAttackTwo'] = MonstersParser.getFromText(f, f.readline(), specialAttackTwoTag)
                mDict['specialAttackThree'] = MonstersParser.getFromText(f, f.readline(), specialAttackThreeTag)
                mDict['specialProperty'] = MonstersParser.getFromText(f, f.readline(), specialPropertyTag)
                mDict['startingSpellpower'] = MonstersParser.getFromText(f, f.readline(), spellpowerTag)
                mDict['startingStrength'] = MonstersParser.getFromText(f, f.readline(), strengthTag)
                self.allMonsters.append(monster.Monster(mDict))
        
        return self.allMonsters
    
if __name__ == "__main__":
    parser = MonstersParser()
    parser.parseAll("./data/Monster_Data.txt")
    for monster in self.allMonsters:
        for k in monster.keys():
            print k + " : " + str(monster[k])
        print "\n"
        
        
        
        