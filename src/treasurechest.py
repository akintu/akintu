#!/usr/bin/python

import sys
import entity
from dice import *
from theorycraft import *
import wealth
import equipment

class TreasureChest(entity.Entity):

    GOLD_PER_IP = 25

    def __init__(self, type, treasureLevel, location, ip=None):
        entity.Entity.__init__(self, location)
        if type.capitalize() not in ["Small", "Large", "Gilded"]:
            raise TypeError("Invalid Chest Type: " + type + ".")
        self.ip = ip
        self.type = type
        if treasureLevel < 1:
            treasureLevel = 1
        if not ip:
            self.ip = (treausureLevel - 1) * 2
            if treasureLevel > 5:
                self.ip = round(self.ip * 1.5)
            if treaureLevel > 10:
                self.ip = round(self.ip * 1.5)
            if treasureLevel > 18:
                self.ip = round(self.ip * 1.5)            
    
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
            pass
            # TODO: 1-3 Consumables and gold
    
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
        