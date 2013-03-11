import sys
import ability
import broadcast
import cctemplatesparser
import combat
import consumable
import dice
import entity
import equipment
import equippeditems
import internalstatus
import inventory
import listener
import magicalproperty
import monster
import onhiteffect
import passiveability
import person
import playercharacter
import spell
import status
import trait
import theorycraft
import trap
import treasurechest
import wealth

class Testy(object):

    @staticmethod
    def methodOne(A, **params):
        print A
        print params['B']
        print params['C']
        params['B'] = "Jello"
        Testy.methodTwo(**params)

    @staticmethod
    def methodTwo(**params):
        print params['B']
        print params['C']

    @staticmethod
    def actionOne():
        print "Sample Output"

if __name__ == "__main__":
    theorycraft.TheoryCraft.loadAll()
    char = None
    # for i in range(96):
        # raceName = theorycraft.TheoryCraft.classes[i]['name'].split(' ', 1)[0]
        # className = theorycraft.TheoryCraft.classes[i]['name'].split(' ', 1)[1]
        # char = theorycraft.TheoryCraft.getNewPlayerCharacter(raceName, className)
        # if i % 12 == 0:
            # print "\n" + char.characterClass
            # for abil in char.abilities:
                # print abil.name + " " + str(abil.APCost)
        #print "   " + char.equippedItems.equippedWeapon.name
    # char = theorycraft.TheoryCraft.getNewPlayerCharacter("Elf", "Battle Mage")
    #char.printCharacterSheet()
    
    print `False`
    print `True`
    
    # saved = char.dehydrate()
    # with open('./data/testSaveFile.txt', 'wb') as f:
        # f.write(saved)
    
    # print saved
    
    # loaded = ''
    # with open("./data/testSaveFile.txt", 'r') as f:
        # loaded = f.read()
    # char = theorycraft.TheoryCraft.rehydratePlayer(loaded)
    # char.printCharacterSheet()
    
    #tc = treasurechest.TreasureChest("Small", 1, None, 12)
    # for i in range(15):
        # tc.generateTreasure(char)
        # for all in char.inventory.allItems:
            # if isinstance(all, equipment.Equipment):
                # for mag in all.propertyList:
                    # print mag.name + ":  " + str(mag.counts)
                # print " ----- " + all.displayName
    # print char.equippedItems.equippedWeapon.displayName

    # initMonster = theorycraft.TheoryCraft.getMonster(level=4)
    # mList = theorycraft.TheoryCraft.generateMonsterGroup(initMonster)
    # for m in mList:
        # print "\n" + m.name
        # for abil in m.abilityList:
            # print abil.name + " " + str(abil.APCost)
        # print "Dodge: " + str(m.totalDodge)
        # print "Dex: " + str(m.totalDexterity)




