#!/usr/bin/python

import sys
import theorycraft
import wealth
import consumable
import equippeditems


class Inventory(object):
    MAX_SLOTS = 20

    def __init__(self, presetItems=None, presetGoldAmount=0, ccName=None):
        self._allItems = []
        if presetItems:
            self._allItems = presetItems
        self.gold = presetGoldAmount
        if ccName:
            self._addStartingItems(ccName)

    def _addStartingItems(self, ccName):
        '''Adds starting equipment to this inventory appropriate
        to the character class name provided (as a new character.)'''
        for i in range(3):
            self.addItem(consumable.Consumable("Basic Healing Potion"))
        for i in range(2):
            self.addItem(consumable.Consumable("Antidote"))
        self.gold = 75
        if ccName == "Barbarian":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Great Axe"))
        elif ccName == "Dragoon":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Spear"))
        elif ccName == "Weapon Master":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Long Sword"))
            self.addItem(theorycraft.TheoryCraft.getArmorByName("Heavy Shield"))
        elif ccName == "Spellsword":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Great Sword"))
        elif ccName == "Anarchist":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Hatchet"))
            self.addItem(theorycraft.TheoryCraft.getArmorByName("Medium Shield"))
        elif ccName == "Marksman":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Longbow"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Shortbow"))
        elif ccName == "Druid":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Shortbow"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Staff"))
        elif ccName == "Tactician":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Shortbow"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Flail"))
        elif ccName == "Ninja":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Katana"))
        elif ccName == "Assassin":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Crossbow"))
        elif ccName == "Shadow":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Stiletto"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Dagger"))
        elif ccName == "Nightblade":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Long Sword"))
        elif ccName == "Battle Mage":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Morning Star"))
            self.addItem(theorycraft.TheoryCraft.getArmorByName("Medium Shield"))
        elif ccName == "Arcane Archer":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Longbow"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Crossbow"))
        elif ccName == "Trickster":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Dagger"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Dagger"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Sling"))
        elif ccName == "Sorcerer":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Sling"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Staff"))
        else:
            print "Warning: character class: '" + ccName + "' is unknown for item generation."


    @property
    def allItems(self):
        return self._allItems

    @property
    def allConsumables(self):
        return [x for x in self._allItems if isinstance(x, consumable.Consumable)]
        
    #def depositGold(self, goldAmount):
        # if isinstance(goldObject, wealth.Wealth) and goldObject.name == "Gold":
            # self.gold += goldObject.goldValue
        # else:
            # print "Warning: Attempted to deposit non-gold object to inventory!"

    def addItem(self, item):
        if isinstance(item, int):
            self.gold += item
        else:
            self._allItems.append(item)
            item.location = None
            # Check for weight here?

    def removeItem(self, item=None, itemName=None):
        '''Removes and returns a given item from this
        inventory, if it is in it.  Otherwise returns
        None.'''
        if not itemName and item:
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
        elif not item and itemName:
            toReturn = None
            for x in self._allItems:
                if itemName == x.identifier:
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




