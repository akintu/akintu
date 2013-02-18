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

    @staticmethod
    def baseAndLevel(data, baseKey, levelKey):
        if re.match("[0-9]+\+[0-9]+"):
            baseKey = int(data.partition("+")[0])
            levelKey = int(data.partition("+")[2])
        else:
            baseKey = int(data)
            levelKey = 0           
           
    @staticmethod
    def associate(file, currentLine, tag, baseKey, levelKey=None)
        data = MonstersParser.getFromText(file, currentLine, tag)
        if levelKey:
            MonstersParser.baseAndLevel(data, baseKey, levelKey)
        else:
            baseKey = data
            
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
        bludgeoningResistTag = re.compile("(?:\[BLUDGEONING RESIST: )(.*)(?:\])", re.I)
        coldResistTag = re.compile("(?:\[ELEMENTAL RESIST COLD: )(.*)(?:\])", re.I)
        divineResistTag = re.compile("(?:\[ELEMENTAL RESIST DIVINE: )(.*)(?:\])", re.I)
        electricResistTag = re.compile("(?:\[ELEMENTAL RESIST ELECTRIC: )(.*)(?:\])", re.I)
        fireResistTag = re.compile("(?:\[ELEMENTAL RESIST FIRE: )(.*)(?:\])", re.I)
        piercingResistTag = re.compile("(?:\[PIERCING RESIST: )(.*)(?:\])", re.I)
        poisonResistTag = re.compile("(?:\[ELEMENTAL RESIST POISON: )(.*)(?:\])", re.I)
        shadowResistTag = re.compile("(?:\[ELEMENTAL RESIST SHADOW: )(.*)(?:\])", re.I)
        slashingResistTag = re.compile("(?:\[SLASHING RESIST: )(.*)(?:\])", re.I)
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
                MonstersParser.associate(f, f.readline(), nameTag, mDict['name'])
                if mDict['name'] == "EOF":
                    break
                MonstersParser.associate(f, f.readline(), APTag, mDict['AP'])
                MonstersParser.associate(f, f.readline(), armorPenetrationTag, mDict['startingArmorPenetration'], 
                                                                               mDict['levelupArmorPenetration'])
                MonstersParser.associate(f, f.readline(), attackElementTag, mDict['attackElement'])
                MonstersParser.associate(f, f.readline(), attackMinTag, mDict['attackMin'], mDict['levelupAttackMin')
                MonstersParser.associate(f, f.readline(), attackMaxTag, mDict['attackMax'], mDict['levelupAttackMax'])
                MonstersParser.associate(f, f.readline(), attackRangeTag, mDict['attackRange'])
                MonstersParser.associate(f, f.readline(), cunningTag, mDict['startingCunning'], mDict['levelupCunning'])
                MonstersParser.associate(f, f.readline(), dexterityTag, mDict['startingDexterity'], mDict['levelupDexterity'])
                MonstersParser.associate(f, f.readline(), DRTag, mDict['startingDR'], mDict['levelupDR'])
                MonstersParser.associate(f, f.readline(), arcaneResistTag, mDict['startingArcaneResistance'],
                                                                           mDict['levelupArcaneResistance'])
                MonstersParser.associate(f, f.readline(), bludgeoningResistTag, mDict['startingBludgeoningResistance'],
                                                                                mDict['levelupBludgeoningResistance'])
                MonstersParser.associate(f, f.readline(), coldResistTag, mDict['startingColdResistance'],
                                                                         mDict['levelupColdResistance'])
                mDict['startingDivineResistance'] = MonstersParser.associate(f, f.readline(), divineResistTag)
                mDict['startingElectricResistance'] = MonstersParser.associate(f, f.readline(), electricResistTag)
                mDict['startingFireResistance'] = MonstersParser.associate(f, f.readline(), fireResistTag)
                mDict['startingPoisonResistance'] = MonstersParser.associate(f, f.readline(), poisonResistTag)
                mDict['startingShadowResistance'] = MonstersParser.associate(f, f.readline(), shadowResistTag)
                mDict['experience'] = MonstersParser.associate(f, f.readline(), experienceTag)
                mDict['GP'] = MonstersParser.associate(f, f.readline(), GPTag)
                mDict['startingHP'] = MonstersParser.associate(f, f.readline(), HPTag)
                mDict['image'] = MonstersParser.associate(f, f.readline(), imageTag)
                mDict['level'] = MonstersParser.associate(f, f.readline(), levelTag)
                mDict['magicResist'] = MonstersParser.associate(f, f.readline(), magicResistTag)
                mDict['meleeAP'] = MonstersParser.associate(f, f.readline(), meleeAPTag)
                mDict['moveAP'] = MonstersParser.associate(f, f.readline(), moveAPTag)
                mDict['movementTiles'] = MonstersParser.associate(f, f.readline(), moveTilesTag)
                mDict['startingMP'] = MonstersParser.associate(f, f.readline(), MPTag)
                mDict['startingPoisonTolerance'] = MonstersParser.associate(f, f.readline(), poisonToleranceTag)
                mDict['rangedAP'] = MonstersParser.associate(f, f.readline(), rangedAPTag)
                mDict['size'] = MonstersParser.associate(f, f.readline(), sizeTag)
                mDict['specialAttackOne'] = MonstersParser.associate(f, f.readline(), specialAttackOneTag)
                mDict['specialAttackTwo'] = MonstersParser.associate(f, f.readline(), specialAttackTwoTag)
                mDict['specialAttackThree'] = MonstersParser.associate(f, f.readline(), specialAttackThreeTag)
                mDict['specialProperty'] = MonstersParser.associate(f, f.readline(), specialPropertyTag)
                mDict['startingSpellpower'] = MonstersParser.associate(f, f.readline(), spellpowerTag)
                mDict['startingStrength'] = MonstersParser.associate(f, f.readline(), strengthTag)
                self.allMonsters.append(mDict)

        return self.allMonsters

if __name__ == "__main__":
    parser = MonstersParser()
    parser.parseAll("./data/Monster_Data.txt")
    for monster in self.allMonsters:
        for k in monster.keys():
            print k + " : " + str(monster[k])
        print "\n"




