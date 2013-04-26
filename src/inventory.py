#!/usr/bin/python

import sys
import theorycraft
import wealth
import consumable
import equippeditems

# inventory.py
# Author: Devin Ekins -- G. Cube
#
# inventory.py is used to manage basic character inventory interactions.
# It also contains a method to populate new characters with their starting
# gear.  Note that this module does not, itself, manage items currently
# equipped on a player.  (See: equippeditems.py)

class Inventory(object):
    MAX_SLOTS = 20

    def __init__(self, presetItems=None, presetGoldAmount=None, ccName=None):
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
        self.addItem(consumable.Consumable("Antidote"))
        self.gold = 325
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
            for i in range(8):
                self.addItem(consumable.Consumable("Basic Poison"))
            self.addItem(consumable.Consumable("Vile Poison"))
        elif ccName == "Tactician":
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Shortbow"))
            self.addItem(theorycraft.TheoryCraft.getWeaponByName("Flail"))
            self.addItem(theorycraft.TheoryCraft.getArmorByName("Medium Shield"))
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
        ''' A public view of all items '''
        return self._allItems

    @property
    def allConsumables(self):
        ''' A view of a subset of the inventory containing only consumables.'''
        return [x for x in self._allItems if isinstance(x, consumable.Consumable)]

    def addItem(self, item):
        ''' Add an item to the inventory'''
        if isinstance(item, int):
            self.gold += item
        else:
            self._allItems.append(item)
            item.location = None

    def removeItem(self, item=None, itemName=None):
        '''Removes and returns a given item from this
        inventory, if it is in it.  Otherwise returns
        None.'''
        if not itemName and item:
            if item in self._allItems:
                self._allItems.remove(item)
                return item
            # toReturn = None
            # for x in self._allItems:
                # if item is x:
                    # toReturn = x
                    # break
            # if toReturn:
                # self._allItems.remove(toReturn)
                # return toReturn
            # else:
                # return None 
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
        # Caller needs to provide a location for this object if it was dropped.

    @property
    def totalWeight(self):
        ''' The weight of all items NOT equipped.'''
        tWeight = 0
        for item in self._allItems:
            tWeight += int(item.weight)
        return tWeight




