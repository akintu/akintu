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
    def baseAndLevel(mDict, data, baseKey, levelKey):
        if re.match("[0-9]+\+[0-9]+", str(data)):
            mDict[baseKey] = int(data.partition("+")[0])
            mDict[levelKey] = int(data.partition("+")[2])
        else:
            mDict[baseKey] = int(data)
            mDict[levelKey] = 0

    @staticmethod
    def associate(file, currentLine, tag, mDict, baseKey, levelKey=None):
        data = MonstersParser.getFromText(file, currentLine, tag)
        if levelKey:
            MonstersParser.baseAndLevel(mDict, data, baseKey, levelKey)
        else:
            mDict[baseKey] = data

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
        GPTag = re.compile("(?:\[GP: )(.*)(?:\])", re.I)
        HPTag = re.compile("(?:\[HP: )(.*)(?:\])", re.I)
        imageTag = re.compile("(?:\[IMAGE: )(.*)(?:\])", re.I)
        magicResistTag = re.compile("(?:\[MAGIC RESIST: )(.*)(?:\])", re.I)
        maxLevelTag = re.compile("(?:\[MAX LEVEL: )(.*)(?:\])", re.I)
        meleeAPTag = re.compile("(?:\[MELEE ATTACK AP: )(.*)(?:\])", re.I)
        minLevelTag = re.compile("(?:\[MIN LEVEL: )(.*)(?:\])", re.I)
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
        typeTag = re.compile("(?:\[TYPE: )(.*)(?:\])", re.I)

        with open(fileName, 'r') as f:
            while( True ):
                mDict = {}
                MonstersParser.associate(f, f.readline(), nameTag, mDict, 'name')
                if mDict['name'] == "EOF":
                    break
                MonstersParser.associate(f, f.readline(), APTag, mDict, 'AP')
                MonstersParser.associate(f, f.readline(), armorPenetrationTag, mDict, 'startingArmorPenetration',
                                                                               'levelupArmorPenetration')
                MonstersParser.associate(f, f.readline(), attackElementTag, mDict, 'attackElement')
                MonstersParser.associate(f, f.readline(), attackMinTag, mDict, 'attackMin', 'levelupMinDamage')
                MonstersParser.associate(f, f.readline(), attackMaxTag, mDict, 'attackMax', 'levelupMaxDamage')
                MonstersParser.associate(f, f.readline(), attackRangeTag, mDict, 'attackRange')
                MonstersParser.associate(f, f.readline(), cunningTag, mDict, 'startingCunning', 'levelupCunning')
                MonstersParser.associate(f, f.readline(), dexterityTag, mDict, 'startingDexterity', 'levelupDexterity')
                MonstersParser.associate(f, f.readline(), DRTag, mDict, 'startingDR', 'levelupDR')
                MonstersParser.associate(f, f.readline(), arcaneResistTag, mDict, 'startingArcaneResistance',
                                                                            'levelupArcaneResistance')
                MonstersParser.associate(f, f.readline(), bludgeoningResistTag, mDict, 'startingBludgeoningResistance',
                                                                                'levelupBludgeoningResistance')
                MonstersParser.associate(f, f.readline(), coldResistTag, mDict, 'startingColdResistance',
                                                                         'levelupColdResistance')
                MonstersParser.associate(f, f.readline(), divineResistTag, mDict, 'startingDivineResistance',
                                                                           'levelupDivineResistance')
                MonstersParser.associate(f, f.readline(), electricResistTag, mDict, 'startingElectricResistance',
                                                                             'levelupElectricResistance')
                MonstersParser.associate(f, f.readline(), fireResistTag, mDict, 'startingFireResistance',
                                                                         'levelupFireResistance')
                MonstersParser.associate(f, f.readline(), piercingResistTag, mDict, 'startingPiercingResistance',
                                                                                'levelupPiercingResistance')
                MonstersParser.associate(f, f.readline(), poisonResistTag, mDict, 'startingPoisonResistance',
                                                                           'levelupPoisonResistance')
                MonstersParser.associate(f, f.readline(), shadowResistTag, mDict, 'startingShadowResistance',
                                                                           'levelupShadowResistance')
                MonstersParser.associate(f, f.readline(), slashingResistTag, mDict, 'startingSlashingResistance',
                                                                           'levelupSlashingResistance')
                MonstersParser.associate(f, f.readline(), GPTag, mDict, 'GP')
                MonstersParser.associate(f, f.readline(), HPTag, mDict, 'startingHP', 'levelupHP')
                MonstersParser.associate(f, f.readline(), imageTag, mDict, 'image')
                MonstersParser.associate(f, f.readline(), magicResistTag, mDict, 'magicResist', 'levelupMagicResist')
                MonstersParser.associate(f, f.readline(), maxLevelTag, mDict, 'maxLevel')
                MonstersParser.associate(f, f.readline(), meleeAPTag, mDict, 'meleeAP')
                MonstersParser.associate(f, f.readline(), minLevelTag, mDict, 'minLevel')
                MonstersParser.associate(f, f.readline(), moveAPTag, mDict, 'moveAP')
                MonstersParser.associate(f, f.readline(), moveTilesTag, mDict, 'movementTiles')
                MonstersParser.associate(f, f.readline(), MPTag, mDict, 'startingMP', 'levelupMP')
                MonstersParser.associate(f, f.readline(), poisonToleranceTag, mDict, 'startingPoisonTolerance',
                                                                              'levelupPoisonTolerance')
                MonstersParser.associate(f, f.readline(), rangedAPTag, mDict, 'rangedAP')
                MonstersParser.associate(f, f.readline(), sizeTag, mDict, 'size')
                MonstersParser.associate(f, f.readline(), specialAttackOneTag, mDict, 'specialAttackOne')
                MonstersParser.associate(f, f.readline(), specialAttackTwoTag, mDict, 'specialAttackTwo')
                MonstersParser.associate(f, f.readline(), specialAttackThreeTag, mDict, 'specialAttackThree')
                MonstersParser.associate(f, f.readline(), specialPropertyTag, mDict, 'specialProperty')
                MonstersParser.associate(f, f.readline(), spellpowerTag, mDict, 'startingSpellpower',
                                                                         'levelupSpellpower')
                MonstersParser.associate(f, f.readline(), strengthTag, mDict, 'startingStrength',
                                                                       'levelupStrength')
                MonstersParser.associate(f, f.readline(), typeTag, mDict, 'type')
                self.allMonsters.append(mDict)

        return self.allMonsters

if __name__ == "__main__":
    parser = MonstersParser()
    parser.parseAll("./data/Monster_Data.txt")
    for monster in self.allMonsters:
        for k in monster.keys():
            print k + " : " + str(monster[k])
        print "\n"




