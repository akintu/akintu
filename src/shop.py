#!/usr/bin/python

import sys
from dice import *
from theorycraft import *
from consumable import Consumable
from equipment import GambleItem
import random

# shop.py
# Author: Devin Ekins -- G. Cube
# 
# Shop is a UI hook/interaction module by functionality.  By structure,
# it is also an object that will hold specific items generated on first
# visit.  Elsewhere (server.py) these shops are cached according to town,
# making towns have specific and certain items such that players can save
# up for desired items and still have them be there when they return with
# enough money to buy them.
#

class Shop(object):
    '''Shops are created by the server.'''
    def __init__(self, level=1, seed=None):
        self.level = max(1, level)
        self.stock = []
        if not seed:
            self.seed = Dice.roll(0, 200000)
        else:
            self.seed = seed
        self._generateStock()
        
    def open(self, player, screen):
        ''' Initialize the store'''
        isEquipment = False
        text = "Welcome to my shop!"
        inv = player.inventory.allItems
        capacity = `player.inventoryWeight` + "/" + `player.inventoryCapacity` + ' lbs'
        gold = `player.inventory.gold` + " gold"
        discount = `player.totalShopBonus` + "% discount"
        valuemod = self._getPriceMods(player)
        screen.show_item_dialog(text, inv, self.stock, isEquipment, bgcolor='mistyrose', capacity=capacity,
                                        gold=gold, discount=discount, valuemod=valuemod)
        
    def buy(self, index, player, screen):
        ''' Purchase an item from the store.'''
        item = self.stock[index]
        if item.value > player.inventory.gold:
            capacity = `player.inventoryWeight` + "/" + `player.inventoryCapacity` + ' lbs'
            gold = `player.inventory.gold` + " gold"
            screen.update_item_dialog_text("You don't have enough money for that!", capacity=capacity, gold=gold)
        else:
            player.inventory.gold -= self._getBuyingPrice(item, player)
            if isinstance(item, GambleItem):
                player.inventory.addItem(self._revealGambleItem(item))
            else:
                player.inventory.addItem(item)
            capacity = `player.inventoryWeight` + "/" + `player.inventoryCapacity` + ' lbs'
            gold = `player.inventory.gold` + " gold"
            screen.update_item_dialog_items(player.inventory.allItems, self.stock)
            screen.update_item_dialog_text("Thank you for your purchase!", capacity=capacity, gold=gold)
                                                
    def sell(self, index, player, screen):
        ''' Sell an item to the store.'''
        item = player.inventory.allItems[index]
        player.inventory.gold += self._getSellingPrice(item, player)
        player.inventory.removeItem(item)
        capacity = `player.inventoryWeight` + "/" + `player.inventoryCapacity` + ' lbs'
        gold = `player.inventory.gold` + " gold"
        screen.update_item_dialog_items(player.inventory.allItems, self.stock)
        screen.update_item_dialog_text("Thank you for your sale!", capacity=capacity, gold=gold)
            
    def close(self, player, screen):
        ''' Shut down the store.'''
        screen.hide_dialog()
        return player.dehydrate()
        
    def _getPriceMods(self, player):
        ''' Determine the markup-markdown for the items in the store.'''
        sellMod = 0.5 * (1 + player.totalShopBonus * 0.01)
        buyMod = 1.5 * (1 - player.totalShopBonus * 0.01)
        return (sellMod, buyMod)
        
    def _getBuyingPrice(self, item, player):
        '''Returns the price of buying or selling an 
        item based on the player's shop discount.'''
        price = item.value
        price *= 1.50
        price *= (1 - player.totalShopBonus * 0.01)
        return int(price)
        
    def _getSellingPrice(self, item, player):
        price = item.value
        price *= 0.50
        price *= (1 + player.totalShopBonus * 0.01)
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
        
        Dice.useGivenSeed = True
        oldSeed = random.getstate()
        random.seed(self.seed)
        
        self.stock = self._generateAllStock(ip)
        self.stock.extend(self._generateAllStock(ip + 2))
        self.stock.extend(self._generateBasicConsumables())
        self.stock.extend(self._generateGambleItems(ip + 6))
        
        random.setstate(oldSeed)
        Dice.useGivenSeed = False
        
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
        
        
        
        
        
    
    
        