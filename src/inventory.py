#!/usr/bin/python

import sys
import wealth

class Inventory(object):
    MAX_SLOTS = 20
    
    def __init__(self, presetItems=[], presetGoldAmount=0):
	    self._allItems = presetItems
	    self.gold = presetGoldAmount
        
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