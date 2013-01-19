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
		    return self.AP >= quantity
		if type == "MP":
		    return self.MP >= quantity
        if type == "HP":
            return self.HP >= quantity
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
		return range >= totalDistance
		   
		   
	def onCooldown(self, abilityName):
	    """Returns True if the ability is currently unavailable due to
		being 'on cooldown' from having been used too recently.
		Inputs:
		  self
		  abilityNAme = The name of the ability being checked
		Outputs:
		  True or False"""
		return abilityName in self.cooldownList
		  
		  
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
		if size in possibleSizes:
		    otherSizeNum = possibleSizes.index(size)
		else
            raise TypeError("Attempted to compare with an invalid size.")
		
		if smallerThan == True:
		    return selfSizeNum < otherSizeNum
		elif smallerThan == False:
		    return selfSizeNum > otherSizeNum
            



			
		
