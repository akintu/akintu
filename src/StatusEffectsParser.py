#!/usr/bin/python

import sys
import re

class InvalidDataFileSyntax(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
       return repr(self.value)

class StatusEffectsParser(object):

    def __init__(self):
	    """Prepares the parser.  
		Possible states are:
		  "Expecting Name" -- not currently parsing an object, 
		     may have just finished parsing an object.
		  "Expecting Type" -- not sure which kind of status we are inside.
		  "Expecting Element" -- currently parsing a display status on the top
		     level, expecting an element.
		  "Top Level" -- Just read element, expecting any top level tags.
		  "Expecting Immune" -- currently parsing an internal 
		     definition.
		  "Expecting Magnitude" -- currently parsing a display status' 
		     internal effect but haven't read the required magnitude field yet
		  "Expecting Any" -- current parsing a display status' internal
		     effect and have already read the magnitude.  We don't know what to
			 expect from here although we know we shouldn't get a name, type, or
			 element."""
	    self.state = "Expecting Name"
	
    # Paths by State:  
	#   Expecting Name        --> Expecting Type    --> Expecting Element OR Expecting Immune
    #   Expecting Immune      --> Expecting Name
    #   Expecting Element     --> Top Level Display --> Expecting Magnitude OR Top Level Display
	#   Expecting Magnitude   --> Expecting Any OR Expecting Magnitude
	#   Expecting Any         --> Expecting Any OR Top Level Display OR Expecting Name
    #
	# Valid Ordered Tags:
	#    NAME*                      --> Expecting Type
	#    TYPE*                      --> Expecting Element OR Expecting Immune
	#    ELEMENT*                   --> Top Level Display
	#
	# Valid Top Level Tags (as of this writing anyway...):
	#    REMOVED_ON                 --> Top Level Display
	#    INTERNAL*                  --> Expecting Magnitude
	#
	# Valid Internal Tags:
	#    CHANCE                     --> Expecting Magnitude OR Expecting Any
	#    CONDITIONAL                --> Expecting Magnitude OR Expecting Any
	#    MAGNITUDE*                 --> Expecting Any
	#    MIN                        --> Expecting Magnitude OR Expecting Any
	#    MAX                        --> Expecting Magnitude OR Expecting Any
	#
	# Note: *'d Items are required.
	
	def parseAll(self, fileName):
	    nameTag = re.compile("(?:\[NAME:).*(?:\])", re.I)
		typeTag = re.compile("(?:\[TYPE:).*(?:\])", re.I)
		elementTag = re.compile("(?:\[ELEMENT:).*(?:\])", re.I)
		internalTag = re.compile("(?:\[INTERNAL:).*(?:\])", re.I)
		magnitudeTag = re.compile("(?:\[MAGNITUDE:).*(?:\])", re.I)
		immuneTag = re.compile("(?:\[IMMUNE:).*(?:\])", re.I)
		removedOnTag = re.compile("(?:\[REMOVED_ON:).*(?:\])", re.I)
		conditionalTag = re.compile("(?:\[CONDITIONAL:).*(?:\])", re.I)
		chanceTag = re.compile("(?:\[CHANCE:).*(?:\])", re.I)
		minTag = re.compile("(?:\[MIN:).*(?:\])", re.I)
		maxTag = re.compile("(?:\[MAX:).*(?:\])", re.I)
		
		f = open('./data/Status_Effects_Data.txt', 'r')
		
		# Initialize fields to undefined/default values.
		# Up to six internals are allowed.  The number of initialized values will need to be changed
		# if this is to be extended beyond six. Please excuse this magic number.
		name, type, immune, element = "Undefined"
		internalList, magnitudeList = [] # 1 to 1 correspondance with internal list (no default)
		conditionalList = ["True", "True", "True", "True", "True", "True"]
		chanceList = [100, 100, 100, 100, 100, 100]
		minList, maxList = [0, 0, 0, 0, 0, 0]
		
		for line in f:
		    line = line.strip()
			
		    if(self.state == "Expecting Name"):
				if(len(line) == 0 or line[0] == "#"):
					continue
				# We are expecting a name tag.
				name = nameTag.match(line)
				self.state = "Expecting Type"
				continue
				
			if(self.state == "Expecting Type"):
				type = typeTag.match(line)
				if(type == "Display"):
				    self.state = "Expecting Element"
					continue
				elif(type == "Internal"):
				    self.state = "Expecting Immune"
					continue
				else:
				    raise InvalidDataFileSyntax("Unkown Status Type: " + line + " in " + filename)
					
			if(self.state == "Expecting Immune"):
				if(len(line) == 0):
				    immune = "None"
				else:
				    immune = immuneTag.match(line)
				# TODO: Make internal object here!
				self.state = "Expecting Name"
				continue
				
			if(self.state == "Expecting Element"):
				element = elementTag.match(line)
				self.state = "Top Level"
				continue
			
			if(self.state == "Expecting Any"):
			    if(len(line) == 0):
				    # TODO: Create/Finalize objects here!
					self.state = "Expecting Name"
					continue
					
			if(self.state == "Top Level" || self.state == "Expecting Any"):
			    # Either removedOn tag or Internal Tag allowed
			    if(internalTag.match(line)):
				    internalList.append(internalTag.match(line))
					self.state = "Expecting Magnitude"
					continue
				if(removedOnTag.match(line)):
				    removedOn = removedOnTag.match(line)
					self.state = "Top Level"
					continue
				raise InvalidDataFileSyntax("Unkown Top Level Tag: " + line + " in " + filename)
			
			if(self.state == "Expecting Magnitude" || self.state == "Expecting Any"):
				# CHANCE
				# CONDITIONAL
				# MAGNITUDE*
				# MIN
				# MAX
                if((self.state != "Expecting Any") and magnitudeTag.match(line)):
                    magnitudeList.append(magnitudeTag.match(line))
                    self.state = "Expecting Any"
                    continue
				# We always want to match up the following with the appropriate internal.
			    # This is accomplished by finding out what the index of the most recently 
				# appended internal is and using that as the corresponding index.	
				index = len(internalList) - 1
				if(conditionalTag.match(line)):
					conditionalList[index] = conditionalTag.match(line)
					continue
				if(chanceTag.match(line)):
				    chanceList[index] = chanceTag.match(line)
					continue
				if(minTag.match(line)):
				    minList[index] = minTag.match(line)
					continue
				if(maxTag.match(line)):
				    maxList[index] = maxTag.match(line)
					continue
				raise InvalidDataFileSyntax("Unkown Internal Tag: " + line + " in " + filename)
			
			
					
                		
						
				    
			
			
				
				
			
			
			
		