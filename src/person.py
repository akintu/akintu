#!/usr/bin/python

import sys

class Person(object):
    def __init__(self):
        self._location = None # Tile
        self._directionFacing = None
        self._team = None #TODO: Move to parent class
        self._size = None
        self._cooldownList = []
        self._statusList = []
        self._owner = None
        self._minionList = []
        
    @property
    def location(self):
        """The Tile beneath the Person"""
        return self._AP
        
    @location.setter
    def location(self, tile):
        """Tile must be unoccupied or no change will result."""
        if tile.isOccupied():
            return
        else:
            self._location = tile
        
    @property
    def directionFacing(self):
        """The direction this Person is facing."""
        return self._directionFacing
        
    @directionFacing.setter
    def directionFacing(self, direction):
        """Possible values:
             "UP"
             "DOWN"
             "LEFT"
             "RIGHT" """
        direction = direction.upper()
        possibleValues = ["UP", "DOWN", "LEFT", "RIGHT"]
        if direction in possibleValues:
            self._directionFacing = direction
    
    @property
    def size(self):
        """The size of this person.  Does not necessarily indicate how many
        tiles it fills up."""
        return self._size
        
    @size.setter
    def size(self, s):
        """Possible values:
            "Small"
            "Medium"
            "Large"
            "Huge" """
        s = capitalize(s)
        possibleValues = ["Small", "Medium", "Large", "Huge"]
        if s in possibleValues:
            self._size = s
            
    @property
    def cooldownList(self):
        """A list of cooldown tuples of form [String, int].  These are used
        to indicate which abilities cannot be used until 'int' more turns
        have passed."""
        return self._cooldownList
        
    @cooldownList.setter
    def cooldownList(self, list):
        """May be used to change the cooldown list... may not want this function."""
        #TODO
        self._cooldownList = list
        
    @property 
    def statusList(self):
        """A list of all display Statuses currently active on this target."""
        return self._statusList
        
    @statusList.setter
    def statusList(self, list):
        """May be used to change the cooldown list... may not want this function."""
        #TODO
        self._statusList = list  
    
    @property
    def owner(self):
        return self._owner
        
    @owner.setter(self, value):
        """Possible values:
             None (Usually the case)
             PlayerCharacter pc (If a summon/guardian)
             Monster m (If a minion of a monster)"""
        if (value is None) or (value.isinstance(Person):
            self._owner = value
        # TODO, if not None, set the link the other direction as well.
            
    @property
    def minionList(self):
        return self._minionList
        
    @minionList.setter
    def minionList(self, value):
        self._minionList = value
    
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
        weaponType = weaponType.capitalize().strip()
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
        
    def isClass(self, className):
        """Returns True if this person has a character class of name
        'className'.
        Inputs: 
          self
          className = The name of the class to check against.
        Outputs:
          True or False"""
        return (str(self.characterClass) == className)
    
    def hasAdjacentFreeSpace(self):
        """Returns True if this person has at least one connecting
        tile (at its location) that is not occupied.
        Inputs:
          self
        Outputs:
          True or False"""
        xCoord = self.location.x
        yCoord = self.location.y
        adjacentCoords = ([[xCoord + 1, yCoord], [xCoord + 1, yCoord + 1]
                           [xCoord + 1, yCoord - 1], [xCoord, yCoord + 1]
                           [xCoord - 1, yCoord - 1], [xCoord - 1, yCoord]
                           [xCoord, yCoord - 1], [xCoord - 1, yCoord + 1]])
                       
        for coords in adjacentCoords:
            if Terrain.getTile(coords[0], coords[1]).isWalkable:
                return True
        return False                
        # TODO Write Terrain.getLocation(x, y) method.                 
    
    def hasWeaponEnchant(self):
        """Returns True if any wepaon enchantment cast by a spellsword is
        present on the weapon(s) of this Person.
        Inputs: 
          self
        Outputs:
          True or False"""
        #TODO: Add status class and modify status classifications (external)
        for status in self.statusList:
            if "Weapon Enchantment" in status.categoryList:
                return True
        return False
        
    def hasStatus(self, statusName):
        """Returns True if this person has a status with a display name
        matching the given 'statusName'.
        Inputs:
          self
          statusName = The name of the status to look for
        Outputs:
          True or False"""
        for item in self.statusList:
            if (statusName == str(item)):
                return True
        return False
        
    # usingAnimalStyle method is identical to hasStatus but needs to
    # function out of combat as well.  TODO
    
    def isSummon(self):
        """Returns True if this Person is a Guardian summoned by a 
        Sorcerer playercharacter.
        Inputs:
          self
        Outputs:
          True or False"""
        return (self.owner is not None)

    def haveSummon(self):
        """Returns True if this Person is a Sorcerer and has a
        Guardian active.
        Inputs:
          self
        Outputs:
          True or False"""
        # "and minionList" = contains something
        if self.isClass("Sorcerer") and self.minionList:
            return True
        return False
    
    def getMeleeFacingEnemy(self):
        """Returns the enemy as a Person directly in front of 
        this Person.  If there is not an enemy in front of this
        Person, it will return None instead.
        Inputs:
          self
        Outputs:
          Person -- enemy directly in front
          None -- if no enemy is directly in front""" 
        x = self.location.x
        y = self.location.y
        direction = self.directionFacing
        location = None
        if(direction == "UP"):
            location = Location(x, y + 1)
        elif(direction == "DOWN"):
            location = Location(x, y - 1)
        elif(direction == "LEFT"):
            location = Location(x - 1, y)
        elif(direction == "RIGHT"):
            location = Location(x + 1, y)
        
        possibleEnemy = Terrain.getObjectAt(location)
        if (isinstance(possibleEnemy, Person) and
            possibleEnemy.team == "Monsters"):
            return possibleEnemy
        else:
            return None
  
    def getMostRecentStatus(self, category): #Rename?
        """Returns the most recent Status object applied to this Person
        or None if no Statuses are on this Person.
        Inputs:
          self
          category = a string representing the category of status effect
                     to look for.  Possible values include:
                     "Buff", "Debuff", "Magical", "Physical", 
                     "Weapon Enchantment", "Threading", "Stealth",
                     "DR Debuff"
        Outputs:
          Status object or None"""
        matches = []
        for status in self.statusList:
            if (status.category == category):
                matches.append(status)
        # Get the last element as it will be the last one applied.
        if matches:
            return matches[-1]
        else:
            return None
            
    
        
        
        
        
        
        