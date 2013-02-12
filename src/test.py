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
import trapsparser
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
    char = theorycraft.TheoryCraft.getNewPlayerCharacter("Human", "Spellsword")
    tc = treasurechest.TreasureChest("Small", 1, None, 12)
    for i in range(100):
        item = tc.generateTreasure()
        print item
    print char
    print tc
    
    