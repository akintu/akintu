#!/usr/bin/python

import sys
import wealth
import consumables
import equippeditems
from theorycraft import *

class Inventory(object):
    MAX_SLOTS = 20
    
    def __init__(self, presetItems=[], presetGoldAmount=0, ccName=None):
	    self._allItems = presetItems
	    self.gold = presetGoldAmount
        if ccName:
            self._addStartingItems(ccName)
        
    def _addStartingItems(self, ccName):
        '''Adds starting equipment to this inventory appropriate
        to the character class name provided (as a new character.)'''
        for i in range(3):
            self.addItem(consumables.Consumables("Basic Healing Potion"))
        for i in range(2):
            self.addItem(consumables.Consumables("Antidote"))
        self.gold = 75
        if ccName == "Barbarian":
            self.addItem(TheoryCraft.getWeaponByName("Great Axe"))
        elif ccName == "Dragoon":
            self.addItem(TheoryCraft.getWeaponByName("Spear"))
        elif ccName == "Weapon Master":
            self.addItem(TheoryCraft.getWeaponByName("Long Sword"))
            self.addItem(TheoryCraft.getArmorByName("Heavy Shield"))
        elif ccName == "Spellsword":
            self.addItem(TheoryCraft.getWeaponByName("Great Sword"))
        elif ccName == "Anarchist":
            self.addItem(TheoryCraft.getWeaponByName("Hatchet"))
            self.addItem(TheoryCraft.getArmorByName("Medium Shield"))
        elif ccName == "Marksman":
            self.addItem(TheoryCraft.getWeaponByName("Longbow"))
            self.addItem(TheoryCraft.getWeaponByName("Shortbow"))
        elif ccName == "Druid":
            self.addItem(TheoryCraft.getWeaponByName("Shortbow"))
            self.addItem(TheoryCraft.getWeaponByName("Staff"))
        elif ccName == "Tactician":
            self.addItem(TheoryCraft.getWeaponByName("Shortbow"))
            self.addItem(TheoryCraft.getWeaponByName("Flail"))
        elif ccName == "Ninja":
            self.addItem(TheoryCraft.getWeaponByName("Katana"))
        elif ccName == "Assassin":
            self.addItem(TheoryCraft.getWeaponByName("Crossbow"))
        elif ccName == "Shadow":
            self.addItem(TheoryCraft.getWeaponByName("Stiletto"))
            self.addItem(TheoryCraft.getWeaponByName("Dagger"))
        elif ccName == "Nightblade":
            self.addItem(TheoryCraft.getWeaponByName("Short Sword"))
        elif ccName == "Battle Mage":
            self.addItem(TheoryCraft.getWeaponByName("Morning Star"))
            self.addItem(TheoryCraft.getWeaponByName("Medium Shield"))
        elif ccName == "Arcane Archer":
            self.addItem(TheoryCraft.getWeaponByName("Longbow"))
            self.addItem(TheoryCraft.getWeaponByName("Crossbow"))
        elif ccName == "Trickster":
            self.addItem(TheoryCraft.getWeaponByName("Dagger"))
            self.addItem(TheoryCraft.getWeaponByName("Dagger"))
            self.addItem(TheoryCraft.getWeaponByName("Sling"))
        elif ccName == "Sorcerer":
            self.addItem(TheoryCraft.getWeaponByName("Sling"))
            self.addItem(TheoryCraft.getWeaponByName("Staff"))
        else:
            print "Warning: character class: '" + ccName + "' is unknown for item generation."
        
        
    @property
    def allItems(self):
        return self._allItems
        
    def depositGold(self, goldObject):
        if goldObject.isinstance(Wealth) and goldObject.name == "Gold":
            self.gold += goldObject.goldValue
        else:
            print "Warning: Attempted to deposit non-gold object to inventory!"
    
    def addItem(self, item):
        if item.isinstance(Wealth) and item.name == "Gold":
            self.depositGold(item)
        else:
            self._allItems.append(item)
            item.location = None
            if len(self._allItems) > MAX_SLOTS:
                print "Warning: Item added to inventory caused the inventory to exceed the MAX_SLOTS of " + MAX_SLOTS + " items."
            # Check for weight here?
            
    def removeItem(self, item):
        '''Removes and returns a given item from this
        inventory, if it is in it.  Otherwise returns
        None.'''
        toReturn = None
        for x in self._allItems:
            if item.identifier == x.identifier:
                toReturn = x
                break
        if toReturn:
            self._allItems.remove(toReturn)
            return toReturn
        else:
            return None
        # Check for weight here?
        # Caller needs to provide a location for this object if it was dropped.
        
    @property
    def totalWeight(self):
        tWeight = 0
        for item in self._allItems:
            tWeight += item.weight
        return tWeight
        

        
        