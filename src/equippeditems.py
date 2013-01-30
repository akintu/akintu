#!/usr/bin/python

import sys
import equipment

class EquippedItems(object):
    def __init__(self, startingGearDict):
	    #TODO actually use startingGearDict
        self._allGear = {'Chest' : None,
                        'Head' : None,
                        'Hands' : None,
                        'Legs' : None,
                        'Feet' : None,
                        'Left Finger' : None,
                        'Right Finger' : None,
                        'Neck' : None,
                        'Main Hand' : None,
                        'Off Hand' : None}
        self._moreRecentFinger = 'Left'
    
    def equip(self, newPiece):
        oldPiece = None
        if newPiece.type == "Chest":
            oldPiece = self._allGear['Chest']
            self._allGear['Chest'] = newPiece
        elif newPiece.type == "Head":
            oldPiece = self._allGear['Head']
            self._allGear['Head'] = newPiece
        elif newPiece.type == "Hands":
            oldPiece = self._allGear['Hands']
            self._allGear['Hands'] = newPiece
        elif newPiece.type == "Legs":
            oldPiece = self._allGear['Legs']
            self._allGear['Legs'] = newPiece
        elif newPiece.type == "Feet":
            oldPiece = self._allGear['Feet']
            self._allGear['Feet'] = newPiece
        elif newPiece.type == "Finger":
            if not self._allGear['Left Finger']:
                self._allGear['Left Finger'] = newPiece
            elif not self._allGear['Right Finger']:
                self._allGear['Right Finger'] = newPiece
            elif self._moreRecentFinger == "Left":
                oldPiece = self._allGear['Right Finger']
                self._allGear['Right Finger'] = newPiece
                self._moreRecentFinger = 'Right'
            else:
                oldPiece = self._allGear['Left Finger']
                self._allGear['Left Finger'] = newPiece
                self._moreRecentFinger = 'Left'
        elif newPiece.type == "Neck":
            oldPiece = self._allGear['Neck']
            self._allGear['Neck'] = newPiece
        elif newPiece.isinstance(equipment.Weapon):
            if newPiece.handsRequired == "Two-Handed":
                # Case 1: Both hands are empty
                if not self._allGear['Main Hand'] and not self._allGear['Off Hand']:
                    self._allGear['Main Hand'] = newPiece
                # Case 2: Main hand full, Off-hand empty
                if self._allGear['Main Hand'] and not self._allGear['Off Hand']:
                    oldPiece = self._allGear['Main Hand']
                    self._allGear['Main Hand'] = newPiece
                # Case 3: Main hand empty, Off-hand full
                if not self._allGear['Main Hand'] and self._allGear['Off Hand']:
                    oldPiece = self._allGear['Off Hand']
                    self._allGear['Main HAnd'] = newPiece
                # Case 4: Both hands full
                if self._allGear['Main Hand'] and self._allGear['Off Hand']:
                    oldPiece = [self._allGear['Main Hand'], self._allGear['Off Hand']]
                    self._allGear['Main Hand'] = newPiece
            elif newPiece.handsRequired == "One-Handed Exclusive":
                pass
                # TODO
            elif newPiece.handsRequired == "One-Handed":
                pass
                # TODO
        # TODO refactor into two helper methods.
        return oldPiece
                
        
            
    
    
    @property
    def equippedOffHand(self):
        return self._allGear['Off Hand']
    
    @property
    def equippedWeapon(self):
        return self._allGear['Main Hand']
        
    @property
    def equippedShield(self):
        if( self._allGear['Off Hand'].isinstance(equipment.Armor) ):
            return self._allGear['Off Hand']
        else:
            return None
    
    @property
    def equippedChestArmor(self):
        return self._allGear['Chest']
        
    @property
    def equippedHeadArmor(self):
        return self._allGear['Head']
        
    @property
    def equippedHandsArmor(self):
        return self._allGear['Hands']
        
    @property
    def equippedLegsArmor(self):
        return self._allGear['Legs']
        
    @property
    def equippedFeetArmor(self):
        return self._allGear['Feet']
        
    @property
    def equippedFingers(self):
        return [self._allGear['Left Finger'], self._allGear['Right Finger']]
        
    @property
    def equippedNeck(self):
        return self._allGear['Neck']
        
        
        
        
    
