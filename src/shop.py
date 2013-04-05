#!/usr/bin/python

import sys
from dice import *
from theorycraft import *
from consumable import Consumable
from equipment import GambleItem

class Shop(object):
    '''A seed may be used here to ensure deterministic shop content.
    Additionally, the coordinates may swapped with a location or 
    pane or somesuch.'''
    def __init__(self, player, screen, seed=None, coords=(0,0), level=1):
        self.player = player
        self.screen = screen
        self.seed = seed
        self.level = level
        if not seed:
            self.seed = Dice.roll(0, 200000)
        self.coords = coords
        self.stock = []
        self._generateStock()

    def open(self):
        isEquipment = False
        text = "Welcome to my shop! (You have " + `self.player.inventory.gold` + " gold.)"
        inv = self.player.inventory.allItems
        capacity = `self.player.inventoryWeight` + "/" + `self.player.inventoryCapacity` + ' lbs'
        gold = `self.player.inventory.gold` + " gold"
        discount = `self.player.totalShopBonus` + "% discount"
        valuemod = self._getPriceMods()
        self.screen.show_item_dialog(text, inv, self.stock, isEquipment, bgcolor='mistyrose', capacity=capacity,
                                        gold=gold, discount=discount, valuemod=valuemod)
        
    def buy(self, index):
        item = self.stock[index]
        if item.value > self.player.inventory.gold:
            capacity = `self.player.inventoryWeight` + "/" + `self.player.inventoryCapacity` + ' lbs'
            gold = `self.player.inventory.gold` + " gold"
            self.screen.update_item_dialog_text("You don't have enough money for that!", capacity=capacity, gold=gold)
        else:
            self.player.inventory.gold -= self._getBuyingPrice(item)
            if isinstance(item, GambleItem):
                self.player.inventory.addItem(self._revealGambleItem(item))
            else:
                self.player.inventory.addItem(item)
            capacity = `self.player.inventoryWeight` + "/" + `self.player.inventoryCapacity` + ' lbs'
            gold = `self.player.inventory.gold` + " gold"
            self.screen.update_item_dialog_items(self.player.inventory.allItems, self.stock)
            self.screen.update_item_dialog_text("Thank you for your purchase!", capacity=capacity, gold=gold)
                                                
    def sell(self, index):
        item = self.player.inventory.allItems[index]
        self.player.inventory.gold += self._getSellingPrice(item)
        self.player.inventory.removeItem(item)
        capacity = `self.player.inventoryWeight` + "/" + `self.player.inventoryCapacity` + ' lbs'
        gold = `self.player.inventory.gold` + " gold"
        self.screen.update_item_dialog_items(self.player.inventory.allItems, self.stock)
        self.screen.update_item_dialog_text("Thank you for your sale!", capacity=capacity, gold=gold)
            
    def close(self):
        self.screen.hide_dialog()
        return self.player.dehydrate()
        
    def _getPriceMods(self):
        sellMod = 0.5 * (1 + self.player.totalShopBonus * 0.01)
        buyMod = 1.5 * (1 - self.player.totalShopBonus * 0.01)
        return (sellMod, buyMod)
        
    def _getBuyingPrice(self, item):
        '''Returns the price of buying or selling an 
        item based on the player's shop discount.'''
        price = item.value
        price *= 1.50
        price *= (1 - self.player.totalShopBonus * 0.01)
        return int(price)
        
    def _getSellingPrice(self, item):
        price = item.value
        price *= 0.50
        price *= (1 + self.player.totalShopBonus * 0.01)
        return int(price)
        
    # For now we'll just generate a balanced list of goods.  This can be customized later.  TODO
        
    def _generateStock(self):
        '''Populates this shop's stock with random (deterministic?)
        items appropriate to the level of this shop.'''
        ip = (self.level - 1) * 2
        if self.level > 5:
            ip = int(ip * 1.5)
        if self.level > 10:
            ip = int(ip * 1.5)
        # Note this is worse than treasure chests for levels 19, 20 because that kind of gear 
        # should only be obtainable in a dungeon.
        
        self.stock = self._generateAllStock(ip)
        self.stock.extend(self._generateAllStock(ip + 2))
        self.stock.extend(self._generateBasicConsumables())
        self.stock.extend(self._generateGambleItems(ip + 6))
        
    def _generateGambleItems(self, ip):
        '''Generate expensive mystery items that only become
        identified upon purchasing them.'''
        subList = []
        subList.append(GambleItem(ip, "Armor"))
        subList.append(GambleItem(ip, "Weapon"))
        return subList
        
    def _generateBasicConsumables(self):
        '''Generate cheap consumables'''
        subList = []
        
        subList.append(Consumable("Basic Healing Potion"))
        subList.append(Consumable("Basic Mana Potion"))
        subList.append(Consumable("Antidote"))
        subList.append(Consumable("Thawing Potion"))
        subList.append(Consumable("Rock Potion"))
        subList.append(Consumable("Basic Poison"))
        
        return subList
        
    def _generateAllStock(self, ip):
        '''Generate stock that is on-par for the level.'''
        subList = []
        
        # Weapons
        
        subList.append(TheoryCraft.getWeaponByName("Short Sword", ip))
        subList.append(TheoryCraft.getWeaponByName("Long Sword", ip))
        subList.append(TheoryCraft.getWeaponByName("Great Sword", ip))
        subList.append(TheoryCraft.getWeaponByName("Hatchet", ip))
        subList.append(TheoryCraft.getWeaponByName("Battle Axe", ip))
        subList.append(TheoryCraft.getWeaponByName("Great Axe", ip))
        subList.append(TheoryCraft.getWeaponByName("Dagger", ip))
        subList.append(TheoryCraft.getWeaponByName("Stiletto", ip))
        subList.append(TheoryCraft.getWeaponByName("Katana", ip))
        subList.append(TheoryCraft.getWeaponByName("Halberd", ip))
        subList.append(TheoryCraft.getWeaponByName("Spear", ip))
        subList.append(TheoryCraft.getWeaponByName("Mace", ip))
        subList.append(TheoryCraft.getWeaponByName("Flail", ip))
        subList.append(TheoryCraft.getWeaponByName("Morning Star", ip))
        subList.append(TheoryCraft.getWeaponByName("Warhammer", ip))
        subList.append(TheoryCraft.getWeaponByName("Staff", ip))
        subList.append(TheoryCraft.getWeaponByName("Scepter", ip))
        subList.append(TheoryCraft.getWeaponByName("Shortbow", ip))
        subList.append(TheoryCraft.getWeaponByName("Longbow", ip))
        subList.append(TheoryCraft.getWeaponByName("Crossbow", ip))
        subList.append(TheoryCraft.getWeaponByName("Sling", ip))
        subList.append(TheoryCraft.getWeaponByName("Shuriken", ip))
        
        # Heavy Armor
        
        subList.append(TheoryCraft.getArmorByName("Platemail Breastplate", ip))
        subList.append(TheoryCraft.getArmorByName("Platemail Helm", ip))
        subList.append(TheoryCraft.getArmorByName("Platemail Greaves", ip))
        subList.append(TheoryCraft.getArmorByName("Platemail Boots", ip))
        subList.append(TheoryCraft.getArmorByName("Platemail Gauntlets", ip))
        
        # Medium Armor
        
        subList.append(TheoryCraft.getArmorByName("Scalemail Breastplate", ip))
        subList.append(TheoryCraft.getArmorByName("Scalemail Helm", ip))
        subList.append(TheoryCraft.getArmorByName("Scalemail Greaves", ip))
        subList.append(TheoryCraft.getArmorByName("Scalemail Boots", ip))
        subList.append(TheoryCraft.getArmorByName("Scalemail Gauntlets", ip))
        
        # Light Armor
        
        subList.append(TheoryCraft.getArmorByName("Leather Breastplate", ip))
        subList.append(TheoryCraft.getArmorByName("Leather Helm", ip))
        subList.append(TheoryCraft.getArmorByName("Leather Pants", ip))
        subList.append(TheoryCraft.getArmorByName("Leather Boots", ip))
        subList.append(TheoryCraft.getArmorByName("Leather Gloves", ip))
    
        # Robe Armor
        
        subList.append(TheoryCraft.getArmorByName("Robes", ip))
        subList.append(TheoryCraft.getArmorByName("Cap", ip))
        subList.append(TheoryCraft.getArmorByName("Leggings", ip))
        subList.append(TheoryCraft.getArmorByName("Shoes", ip))
        subList.append(TheoryCraft.getArmorByName("Cloth Bracer", ip))
    
        # Shields
        
        subList.append(TheoryCraft.getArmorByName("Heavy Shield", ip))
        subList.append(TheoryCraft.getArmorByName("Medium Shield", ip))
    
        # Jewlery
        
        subList.append(TheoryCraft.getArmorByName("Ring", ip))
        subList.append(TheoryCraft.getArmorByName("Amulet", ip))
    
        return subList
    
    def _revealGambleItem(self, gItem):
        '''Turn a GambleItem into an actual item to be
        given to a player after he pays money for it.'''
        item = None
        if gItem.underlyingType == "Weapon":
            itemDict = Dice.choose(TheoryCraft.weapons)
            name = itemDict['name']
            item = TheoryCraft.getWeaponByName(name, gItem.ip)
        else:
            itemDict = Dice.choose(TheoryCraft.armors)
            name = itemDict['name']
            item = TheoryCraft.getArmorByName(name, gItem.ip)
        return item
        
        
        
        
        
    
    
        