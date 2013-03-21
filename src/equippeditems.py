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

    @property
    def allGear(self):
        return [x for x in self._allGear.values() if x]
        
    def _equipArmor(self, newPiece):
        oldPiece = []
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
        elif newPiece.type == "Neck":
            oldPiece = self._allGear['Neck']
            self._allGear['Neck'] = newPiece
        return [oldPiece]

    def _equipRing(self, newPiece, hand=None):
        oldPiece = []
        if hand == "Left":
            oldPiece = self._allGear['Left Finger']
            self._allGear['Left Finger'] = newPiece
            self._moreRecentFinger = 'Left'
        elif hand == "Right":
            oldPiece = self._allGear['Right Finger']
            self._allGear['Right Finger'] = newPiece
            self._moreRecentFinger = 'Right'
        elif not self._allGear['Left Finger']:
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
        return [oldPiece]

    def _equipWeapon(self, newPiece, hand="Right"):
        if hand == "Main" or not hand:
            hand = "Right"
        elif hand == "Off" or hand == "Off-Hand":
            hand = "Left"

        handsUsed = newPiece.handsRequired

        oldPieceOne = None
        oldPieceTwo = None
        if handsUsed == "Two-Handed" or handsUsed == "One-Handed Exclusive":
            # Case 1&2: Main hand full or empty, Off-hand empty
            if not self._allGear['Off Hand']:
                oldPieceOne = self._allGear['Main Hand']
                self._allGear['Main Hand'] = newPiece
            # Case 3: Main hand empty, Off-hand full
            elif not self._allGear['Main Hand'] and self._allGear['Off Hand']:
                oldPieceOne = self._allGear['Off Hand']
                self._allGear['Main Hand'] = newPiece
                self._allGear['Off Hand'] = None
            # Case 4: Both hands full
            elif self._allGear['Main Hand'] and self._allGear['Off Hand']:
                # Case 4a : Off-hand is using a shield and this is One-Handed Exclusive
                if self.equippedShield and handsUsed == "One-Handed Exclusive":
                    oldPieceOne = self._allGear['Main Hand']
                    self._allGear['Main Hand'] = newPiece
                # Case 4b : Off-hand is using a weapon, or this is a Two-Handed weapon
                else:
                    oldPieceOne = self._allGear['Main Hand']
                    oldPieceTwo = self._allGear['Off Hand']
                    self._allGear['Main Hand'] = newPiece
                    self._allGear['Off Hand'] = None
        elif handsUsed == "One-Handed" and hand == "Right":
            oldPieceOne = self._allGear['Main Hand']
            self._allGear['Main Hand'] = newPiece
        elif handsUsed == "One-Handed" and hand == "Left":
            oldPieceOne = self._allGear['Off Hand']
            self._allGear['Off Hand'] = newPiece
            if self._allGear['Main Hand'] and (self._allGear['Main Hand'].handsRequired == "One-Handed Exclusive" \
             or self._allGear['Main Hand'].handsRequired == "Two-Handed"):
                oldPieceTwo = self._allGear['Main Hand']
                self._allGear['Main Hand'] = None
        if oldPieceTwo:
            return [oldPieceOne, oldPieceTwo]
        else:
            return [oldPieceOne]

    def _equipShield(self, newPiece):
        oldPiece = None
        mainHand = self._allGear['Main Hand']
        if mainHand and mainHand.handsRequired == "Two-Handed":
            oldPiece = mainHand
            self._allGear['Main Hand'] = None
        else:
            oldPiece = self._allGear['Off Hand']
        self._allGear['Off Hand'] = newPiece
        return [oldPiece]

    def equip(self, newPiece, hand=None):
        """Equips the given 'newPiece' of Equipment.  If the new piece is
        either a ring or a one-handed weapon, specifying the 'hand' will
        determine which weapon/shield/ring it replaces.  Otherwise a default
        value will be used.  Returns the equipment previously equipped in a
        list.
        Inputs:
          newPiece -- Equipment; The piece of equipment to put on.
          hand -- string*; Possible values: "Right", "Left" (The primary hand
                            is considered to be "Right".)
        Outputs:
          A List of the equipment that was displaced (even if it was only one
          piece.)"""
        if not hand:
            hand = "Right"
        if isinstance(newPiece, equipment.Weapon):
            return self._equipWeapon(newPiece, hand)
        if newPiece.type == "Finger" or newPiece.type == "Fingers":
            return self._equipRing(newPiece, hand)
        if newPiece.type == "Shield":
            return self._equipShield(newPiece)
        else:
            return self._equipArmor(newPiece)

    def unequip(self, slot):
        '''Unequips an item from the given slot.  If the slot is not an armor
        slot (weapon/offhand/shield) or a ring slot it will unequip both hands 
        of equipment.
        Returns the equipment previously equipped in a list.
        Inputs:
            slot -- String; the slot of equipment to remove from.
        Outputs:
            A List of the equipment previously in that slot or None if nothing
            was there.'''
        if slot == "Head":
            old = self._allGear['Head']
            self._allGear['Head'] = None
            return [old]
        if slot == "Chest":
            old = self._allGear['Chest']
            self._allGear['Chest'] = None
            return [old]
        if slot == "Hands":
            old = self._allGear['Hands']
            self._allGear['Hands'] = None
            return [old]
        if slot == "Legs":
            old = self._allGear['Legs']
            self._allGear['Legs'] = None
            return [old]
        if slot == "Feet":
            old = self._allGear['Feet']
            self._allGear['Feet'] = None
            return [old]
        if slot == "Neck":
            old = self._allGear['Neck']
            self._allGear['Neck'] = None
            return [old]
        if slot == "Fingers" or slot == "Finger":
            old = []
            if self._allGear['Left Finger']:
                old.append(self._allGear['Left Finger'])
                self._allGear['Left Finger'] = None
            if self._allGear['Right Finger']:
                old.append(self._allGear['Right Finger'])
                self._allGear['Right Finger'] = None
            return old
        else:
            # Weapon/Shield slot
            old = []
            if self._allGear['Off Hand']:
                old.append(self._allGear['Off Hand'])
                self._allGear['Off Hand'] = None
            if self._allGear['Main Hand']:
                old.append(self._allGear['Main Hand'])
                self._allGear['Main Hand'] = None
            return old
            
            
    @property
    def equippedOffHand(self):
        return self._allGear['Off Hand']

    @property
    def equippedWeapon(self):
        return self._allGear['Main Hand']

    @property
    def equippedShield(self):
        if isinstance(self._allGear['Off Hand'], equipment.Armor) :
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

    @property
    def totalArmorGrade(self):
        ag = 0
        if self._allGear['Head']:
            ag += self._allGear['Head'].gradePoints
        if self._allGear['Chest']:
            ag += self._allGear['Chest'].gradePoints
        if self._allGear['Legs']:
            ag += self._allGear['Legs'].gradePoints
        if self._allGear['Hands']:
            ag += self._allGear['Hands'].gradePoints
        if self._allGear['Feet']:
            ag += self._allGear['Feet'].gradePoints
        return ag

    @property
    def armorLevel(self):
        grade = self.totalArmorGrade
        if grade == 0:
            return "Robes"
        if 0 < grade and grade <= 8:
            return "Light"
        if 8 < grade and grade <= 20:
            return "Medium"
        if 20 < grade:
            return "Heavy"

    @property
    def equippedWeight(self):
        totalWeight = 0
        if self._allGear['Head']:
            totalWeight += int(self._allGear['Head'].weight)
        if self._allGear['Chest']:
            totalWeight += int(self._allGear['Chest'].weight)
        if self._allGear['Legs']:
            totalWeight += int(self._allGear['Legs'].weight)
        if self._allGear['Hands']:
            totalWeight += int(self._allGear['Hands'].weight)
        if self._allGear['Feet']:
            totalWeight += int(self._allGear['Feet'].weight)
        if self._allGear['Main Hand']:
            totalWeight += int(self._allGear['Main Hand'].weight)
        if self._allGear['Off Hand']:
            totalWeight += int(self._allGear['Off Hand'].weight)
        return totalWeight



