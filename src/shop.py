#!/usr/bin/python

import sys
from dice import *
from theorycraft import *

class Shop(object):
    '''A seed may be used here to ensure deterministic shop content.
    Additionally, the coordinates may swapped with a location or 
    pane or somesuch.'''
    def __init__(self, seed=None, coords=(0,0), level=1):
	    self.seed = seed
        if not seed:
            self.seed = Dice.roll(0, 200000)
        self.coords = coords
        self.stock = None
        self.generateStock()

    # For now we'll just generate a balanced list of goods.  This can be customized later.  TODO
        
    def generateStock(self):
        '''Populates this shop's stock with random (deterministic?)
        items appropriate to the level of this shop.'''
        ip = (self.level - 1) * 2
        if self.level > 5:
            ip = int(self.ip * 1.5)
        if self.level > 10:
            ip = int(self.ip * 1.5)
        # Note this is worse than treasure chests for levels 19, 20 because that kind of gear 
        # should only be obtainable in a dungeon.
        
        self.stock = self.generateAllStock(ip)
        self.stock.extend(self.generateAllStock(ip + 2))
        
    def generateAllStock(self, ip)
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
        
        subList.append(TheoryCraft.getWeaponByName("Platemail Breastplate", ip))
        subList.append(TheoryCraft.getWeaponByName("Platemail Helm", ip))
        subList.append(TheoryCraft.getWeaponByName("Platemail Greaves", ip))
        subList.append(TheoryCraft.getWeaponByName("Platemail Boots", ip))
        subList.append(TheoryCraft.getWeaponByName("Platemail Gauntlets", ip))
        
        # Medium Armor
        
        subList.append(TheoryCraft.getWeaponByName("Scalemail Breastplate", ip))
        subList.append(TheoryCraft.getWeaponByName("Scalemail Helm", ip))
        subList.append(TheoryCraft.getWeaponByName("Scalemail Greaves", ip))
        subList.append(TheoryCraft.getWeaponByName("Scalemail Boots", ip))
        subList.append(TheoryCraft.getWeaponByName("Scalemail Gauntlets", ip))
        
        # Light Armor
        
        subList.append(TheoryCraft.getWeaponByName("Leather Breastplate", ip))
        subList.append(TheoryCraft.getWeaponByName("Leather Helm", ip))
        subList.append(TheoryCraft.getWeaponByName("Leather Pants", ip))
        subList.append(TheoryCraft.getWeaponByName("Leather Boots", ip))
        subList.append(TheoryCraft.getWeaponByName("Leather Gloves", ip))
    
        # Robe Armor
        
        subList.append(TheoryCraft.getWeaponByName("Robes", ip))
        subList.append(TheoryCraft.getWeaponByName("Cap", ip))
        subList.append(TheoryCraft.getWeaponByName("Leggings", ip))
        subList.append(TheoryCraft.getWeaponByName("Shoes", ip))
        subList.append(TheoryCraft.getWeaponByName("Cloth Bracer", ip))
    
        # Shields
        
        subList.append(TheoryCraft.getWeaponByName("Heavy Shield", ip))
        subList.append(TheoryCraft.getWeaponByName("Medium Shield", ip))
    
        # Jewlery
        
        subList.append(TheoryCraft.getWeaponByName("Ring", ip))
        subList.append(TheoryCraft.getWeaponByName("Amulet", ip))
    
    
    
    
    
        