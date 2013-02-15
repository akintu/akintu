#!/usr/bin/python

import sys
import entity
from dice import *
from theorycraft import *
import wealth
import equipment
import consumable

class TreasureChest(entity.Entity):

    GOLD_PER_IP = 25
    CHANCE_OF_LOCK = 20
    
    def __init__(self, type, treasureLevel, location, ip=None, locked=None):
        entity.Entity.__init__(self, location)
        if type.capitalize() not in ["Small", "Large", "Gilded"]:
            raise TypeError("Invalid Chest Type: " + type + ".")
        self.ip = ip
        self.baseIp = self.ip # Used for treasure chest bashing reductions.
        self.type = type
        if treasureLevel < 1:
            treasureLevel = 1
        self.treasureLevel = treasureLevel
        if not ip:
            self.ip = (treausureLevel - 1) * 2
            if treasureLevel > 5:
                self.ip = round(self.ip * 1.5)
            if treaureLevel > 10:
                self.ip = round(self.ip * 1.5)
            if treasureLevel > 18:
                self.ip = round(self.ip * 1.5)
        self.locked = locked
        self.lockComplexity = 0
        if locked is None:
            locked = Dice.rollBeneath(TreasureChest.CHANCE_OF_LOCK)
        if locked:
            if self.treasureLevel <= 10:
                self.lockComplexity = 11 + self.treasureLevel * 3
            else:
                self.lockComplexity = 21 + self.treasureLevel * 2
        
    def generateTreasure(self, openingPlayer=None):
        if self.type == "Gilded" and not openingPlayer:
            print "TreasureChest.generateTreasure -- Warning: No player specified for this treasure!"
            return
        if self.type == "Small":
            return self._generateSmallTreasure()
        elif self.type == "Large":
            return self._generateLargeTreasure()
        else:
            return self._generateGildedTreasure(openingPlayer)
            
    def _generateSmallTreasure(self):
        selection = Dice.roll(1, 100)
        if selection <= 20:
            # One piece of gear
            return [TreasureChest._selectGear(self.ip)]
        elif selection <= 40:
            # Only Gold
            return [TreasureChest._selectGold(self.ip)]
        else:
            # 1-3 Consumables and gold
            currentIp = self.ip
            consList = []
            while(currentIp > 0 and len(consList) < 3):
                item = TreasureChest._selectCons(currentIp, self.treasureLevel)
                if not item:
                    break
                consList.append(item)
                currentIp -= item.ip
            if currentIp > 0:
                consList.append(TreasureChest._selectGold(currentIp))
            return consList
            
    @staticmethod
    def _selectCons(givenIp, givenLevel):
        selectionDict = None
        selection = Dice.roll(1, 100)
        # Ideal distribution: 
        #
        # Potions  : 65%
        # Poisons  : 15%
        # Essences : 10%
        # Oils     : 5%
        # Scrolls  : 5%
        # TODO: Add all of these items so we can use that distribution.
        if selection <= 15:
            selectionDict = consumable.Consumable.allPoisons
        else:
            selectionDict = consumable.Consumable.allPotions
        possibleItems = [x for x in selectionDict
                         if selectionDict[x]['level'] <= givenLevel + 1 and selectionDict[x]['level'] >= givenLevel - 1
                         and selectionDict[x]['ip'] <= givenIp]
        if len(possibleItems) == 0:
            return None
        else:
            choice = Dice.roll(0, len(possibleItems) - 1)
            return consumable.Consumable(possibleItems[choice])
   
    
    @staticmethod
    def _selectGear(givenIp):
        selectedItem = None
        giveWeapon = Dice.rollBeneath(40)
        if giveWeapon:
            baseWeaponSelection = Dice.roll(0, len(TheoryCraft.weapons) - 1)
            selectedItem = equipment.Weapon(**TheoryCraft.weapons[baseWeaponSelection])
        else:
            baseArmorSelection = Dice.roll(0, len(TheoryCraft.armors) - 1)
            selectedItem = equipment.Armor(TheoryCraft.armors[baseArmorSelection])
        return selectedItem.cloneWithMagicalProperties(givenIp)
        
    @staticmethod
    def _selectGold(givenIp):
        modifier = Dice.rollFloat(0.6, 1.4)
        gold = round(givenIp * modifier * TreasureChest.GOLD_PER_IP)
        return wealth.Wealth("Gold", gold)
        
    def _generateLargeTreasure(self):
        selection = Dice.roll(1, 100)
        if selection <= 60:
            # Two pieces of gear ip=50/50
            return [TreasureChest.selectGear(self.ip // 2), TreasureChest.selectGear(self.ip / 2)] 
        elif selection <= 90:
            # Two pieces of gear and gold, ip=40/40/20
            return [TreasureChest.selectGear(round(self.ip * 0.4)),
                    TreasureChest.selectGear(round(self.ip * 0.4)),
                    TreasureChest.selectGold((self.ip * 2) // 10)]
        else:
            # One piece of gear ip=100
            return [TreasureChest._selectGear(self.ip)]
           
            
    def _generateGildedTreasure(self, player):
        return []
        # TODO: Two pieces of class-approriate gear.
        
    def bash(self, player):
        ''' Attempts to have the player bash open the lock on this
        chest.  Will lower the IP content of the chest appropriately.
        If the bash is successful, will return True otherwise it will
        return False.  If the chest has already been unlocked, or was
        never locked, will return True. '''
        if not self.locked:
            print "This chest is already unlocked."
            return True
        lowerAmount = min(5, round(self.baseIp * 0.1))
        self.ip -= lowerAmount
        if self.ip < round(self.baseIp * 0.5):
            self.ip = round(self.baseIp * 0.5)
            print "Chest IP unaffected."
        else:
            print "Chest IP reduced by " + lowerAmount + "."        
        success = min(100, max(10, 25 + player.totalStrength - self.lockComplexity))
        if Dice.rollBeneath(success):
            return True
        else:
            return False
    
    def pickLock(self, player):
        ''' Attempts to have the player unlock the chest via 
        lockpicking.  Will return True if the chest was already
        unlocked or if successful, otherwise will return False. '''
        if not self.locked:
            print "This chest is already unlocked."
            return True
        if player.lockpicking < self.lockComplexity:
            return False
        print "Lock picking successful."
        # TODO: Give experience?  Decide.
        return True
            
    
    
    
    
    
        
        
        