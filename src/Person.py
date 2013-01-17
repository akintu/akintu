#!/usr/bin/python

import sys

class Person(object):
    def resource(self, type, quantity):
	    """Returns True if the Person has at least 'quantity' of the resource.
		Inputs:
		  self
		  type = type of resource: "HP", "MP", "AP"
		  quantity = positive integer
		Outputs:
		  True or False"""
		if type == "AP":
		    return (self.AP >= quantity)
		if type == "MP":
		    return (self.MP >= quantity)
        if type == "HP":
            return (self.HP >= quantity)
        raise TypeError("Attempted to use an invalid resource type.")
		
		
    def inRange(self, target, range):
	    """Returns True if the Person is at most range tiles away from the 
		target.
		Inputs:
		  self
		  target = may either be a Location or a Person
		  range = a positive integer
		Outputs:
		  True or False"""
		selfLoc = self.location
		otherLoc = None
		if isinstance(target, Person):
		    otherLoc = target.location
		elif isinstance(target, Location):
		    otherLoc = target
		horizontalDistance = selfLoc.x - otherLoc.x
		veritcalDistance = selfLoc.y - otherLoc.y
		totalDistance = max(horizontalDistance, verticalDistance)
		return (range >= totalDistance)
		   
		   
	def onCooldown(self, abilityName):
	    """Returns True if the ability is currently unavailable due to
		being 'on cooldown' from having been used too recently.
		Inputs:
		  self
		  abilityNAme = The name of the ability being checked
		Outputs:
		  True or False"""
		return (abilityName in self.cooldownList)
		  
		  
	def sizeCompare(self, size, smallerThan):
	    """Returns True if the size of this Person is smaller than the given
		size and 'smallerThan' is True.  Returns True if the size of this
		Person is larger than the given size and 'smallerThan' is False.
		Inputs:
		  self
		  size = "Small", "Medium", "Large", or "Huge"
		  smallerThan = boolean
		Outputs:
		  True or False"""
		otherSizeNum = None
		possibleSizes = ["Small", "Medium", "Large", "Huge"]
		selfSizeNum = possibleSizes.index(self.size)
		if (size in possibleSizes):
		    otherSizeNum = possibleSizes.index(size)
		else
            raise TypeError("Attempted to compare with an invalid size.")
		
		if (smallerThan == True):
		    return (selfSizeNum < otherSizeNum)
		elif (smallerThan == False):
		    return (selfSizeNum > otherSizeNum)
       
    def usingWeapon(self, weaponType):
        """Returns True if the passed Weapon type matches the type of
        weapon this Person is using or is a superset of that type.
        Inputs:
          self
          weaponType = "Sword", "Club", "Shortbow", "Longbow", "Bow",
                       "Crossbow", "Axe", "Polearm", "Ranged", "Melee",
                       "Shuriken", "Mage Weapon", "Sling", "Knife"
        Outputs:
          True or False"""
        acceptList = [weaponType]
		if weaponType == "Melee":
		    acceptList.extend(["Sword", "Club", "Axe", "Polearm",
			                   "Mage Weapon", "Knife"])
		elif weaponType == "Ranged":
		    acceptList.extend(["Longbow", "Shortbow", "Sling", "Crossbow",
			                   "Shuriken"])
		elif weaponType == "Bow":
		    acceptList.extend(["Longbow", "Shortbow"])
	    return (self.equipment.equippedWeapon.type in acceptList or
		        self.equipment.equippedOffHand.type in acceptList)
        
	def usingArmor(self, armorLevel):
	    """Returns True if the passed armorLevel matches the armor level
		the Person has currently equipped.
		Inputs:
		  self
		  armorLevel = "Heavy", "Medium", "Light", "Robes"
		Outputs:
		  True or False"""
		return (self.equipment.armorLevel == armorLevel)
		
	def usingShield(self, shieldType):
	    """Returns True if the passed shieldType matches the kind of 
		shield the Person has currently equipped.
		Inputs:
		  self
		  shieldType = "Heavy", "Medium", "Any", "None"
		Outputs:
		  True or False"""
		shield = self.equipment.equippedShield
		if (shieldType == "Any"):
		    return (shield is not None)
		elif (shieldType == "None"):
		    return (shield is None)
		elif (shield == None):
		    return False
		else: 
		    return (shield.type == shieldType)
		
	def usingWeaponStyle(self, style):
	    """Returns True if this Person is using (equipping) the given 
		weapon style.  Monsters are considered to be using no weapons.
		This will always return False in their case.
		Inputs: 
		  self
		  style = "Dual" (Two weapons), 
		          "Dual Same Type" (Two weapons that are also the same 
				                    weaponType)
				  "Two Handed" (One weapon that requires both hands)
				  "Single" (One weapon that requires one hand and the
				            other hand is empty)
				  "Single and Shield" (One weapon that requires one hand
				                       and a shield)
		Outputs:
		  True or False"""
		style.replace("-", " ") 
		handOne = self.equipment.equippedWeapon
		handTwo = self.equipment.equippedOffHand
		  
		if (style == "Dual Same Type" and 
		   handOne is not None and 
		   handTwo is not None):
		    return handOne.type == handTwo.type
        if (style == "Dual"):
		    return (handOne is not None and handTwo is not None)
		if (style == "Two Handed"):
		    return (handOne is not None and handTwo == "Occupied")
		if (style == "Single"):
		    return (handOne is not None and handTwo is None)
		if (style == "Single and Shield"):
		    return (handOne is not None and self.usingShield("Any"))
		# And for the monsters...
		return False
		
	def getNumberOfStackedStatus(self, statusName):
	    """Returns the integer number of the status indicated currently
		present on the player.  Will simply return 0 if no such 'stacks' of
		the status are present at all.
		Inputs:
		  self
		  statusName = the internal name of the status effect to look for
		Ouputs:
		  A non-negative integer"""
		statusObject = None
		for item in self.statusList:
		    if (statusName == str(item)):
			    statusObject = item
		if (statusObject is None):
		    return 0
		else:
		    return statusObject.stacks
		
	def canReach(self, target, tilesAllowed):
	    """Returns True if it is possible to walk from self's current location
		to the target's location within the allowed number of tiles.
		Inputs:
		  self
		  target = Location of destination
		  tilesAllowed = non-negative integer of how many tiles can be used
		                 to reach the target location.
		Outputs:
		  True or False"""
		pass #TODO: Requires path-finding
		
	def inStealth(self):
	    """Returns True if this Person has any form of stealth other than 
		invisibility.
		Inputs:
		  self
		Outputs:
		  True or False"""
		stealthList = ["Stealth", "Shadow Walk", "Conceal"]
		for item in self.statusList:
		    if (str(item) in stealthList):
			    return True
		return False	
		
	def inBackstabPosition(self, target, rangedBackstab=False):
	    """Returns True if this Person is behind the target, including behind
		diagonals.  If rangedBackstab is False, as it is by default, the player
		must also be in melee range."""
		targetFacing = target.directionFacing
		# TODO: Are we including diagnoal facing directions?
		xDifference = self.location.x - target.location.x
		yDifference = self.location.y - target.location.y
		
		if(not rangedBackstab):
		    if (abs(xDifference) > 1) or (abs(yDifference) > 1):
			    return False
		
		if(targetFacing == "DOWN"):
		    if (yDifference <= 0) or (abs(xDifference) > yDifference):
			    return False
		elif(targetFacing == "UP"):
		    if (yDifference >= 0) or (abs(xDifference) > yDifference):
			    return False
		elif(targetFacing == "LEFT"):
		    if (xDifference <= 0) or (abs(yDifference) > xDifference):
			    return False
		elif(targetFacing == "RIGHT"):
		    if (xDifference >= 0) or (abs(yDifference) > xDifference):
			    return False
		else:
		    raise TypeError("Invalid Directional Argument Given.")
			
		return True
		
	


			
		
