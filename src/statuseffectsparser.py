#!/usr/bin/python

import sys
import re
import status
import internalstatus

# statuseffectsparser.py
# Author: Devin Ekins -- G. Cube
#
# This module simply parses the Stats_Effects_Data.txt file in such a fashion that
# Akintu will be able to make use of it after one execution.  It contains
# only one method that matters to the outside, parseAll() which will 
# load all data at startup time.
#
# This file is modeled after a DFA pattern and was the first of the parsers to be
# written.  As a consequence it is more flexible to handle errors in the data
# file, but has much more complex code written here.


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
          "Expecting Recurring" -- currently parsing an internal defnition.
          "Expecting Immune" -- currently parsing an internal definition.
          "Expecting Magnitude" -- currently parsing a display status'
             internal effect but haven't read the required magnitude field yet
          "Expecting Any" -- current parsing a display status' internal
             effect and have already read the magnitude.  We don't know what to
             expect from here although we know we shouldn't get a name, type, or
             element."""
        self.state = "Expecting Name"
        self.displayStatusList = []

    # Paths by State:
    #   Expecting Name        --> Expecting Type    --> Expecting Element OR Expecting Recurring
    #   Expecting Recurring   --> Expecting Immune  --> Expecting Name
    #   Expecting Element     --> Top Level         --> Expecting Magnitude OR Top Level OR Expecting Name
    #   Expecting Magnitude   --> Expecting Any OR Expecting Magnitude
    #   Expecting Any         --> Expecting Any OR Top Level OR Expecting Name
    #
    # Valid Ordered Tags:
    #    NAME*                      --> Expecting Type
    #    TYPE*                      --> Expecting Element OR Expecting Immune
    #    ELEMENT*                   --> Top Level
    #
    # Valid Top Level Tags (as of this writing anyway...):
    #    REMOVED_ON                 --> Top Level
    #    INTERNAL*                  --> Expecting Magnitude
    #    CATEGORY                   --> Top Level
    #
    # Valid Internal Tags:
    #    CHANCE                     --> Expecting Magnitude OR Expecting Any
    #    CONDITIONAL                --> Expecting Magnitude OR Expecting Any
    #    MAGNITUDE*                 --> Expecting Any
    #    MIN                        --> Expecting Magnitude OR Expecting Any
    #    MAX                        --> Expecting Magnitude OR Expecting Any
    #
    # Valid Definition Tags:
    #    IMMUNE                     --> Expecting Name
    #    RECURRING                  --> Definition Level
    #
    #

    # Note: *'d Items are required.

    def parseAll(self, fileName):
        nameTag = re.compile("(?:\[NAME: )(.*)(?:\])", re.I)
        typeTag = re.compile("(?:\[TYPE: )(.*)(?:\])", re.I)
        imageTag = re.compile("(?:\[IMAGE: )(.*)(?:\])", re.I)
        elementTag = re.compile("(?:\[ELEMENT: )(.*)(?:\])", re.I)
        internalTag = re.compile("(?:\[INTERNAL: )(.*)(?:\])", re.I)
        magnitudeTag = re.compile("(?:\[MAGNITUDE: )(.*)(?:\])", re.I)
        immuneTag = re.compile("(?:\[IMMUNE: )(.*)(?:\])", re.I)
        removedOnTag = re.compile("(?:\[REMOVED_ON: )(.*)(?:\])", re.I)
        conditionalTag = re.compile("(?:\[CONDITIONAL: )(.*)(?:\])", re.I)
        chanceTag = re.compile("(?:\[CHANCE: )(.*)(?:\])", re.I)
        minTag = re.compile("(?:\[MIN: )(.*)(?:\])", re.I)
        maxTag = re.compile("(?:\[MAX: )(.*)(?:\])", re.I)
        categoryTag = re.compile("(?:\[CATEGORY: )(.*)(?:\])", re.I)
        recurringTag = re.compile("(?:\[RECURRING: )(.*)(?:\])", re.I)

        f = open(fileName, 'r')

        # Initialize fields to undefined/default values.
        # Up to six internals are allowed.  The number of initialized values will need to be changed
        # if this is to be extended beyond six. Please excuse this magic number.
        name = None
        type = None
        image = None
        immune = None
        recurring = None
        element = None
        internalNameList = None
        internalList = None
        magnitudeList = None
        categoryList = None
        conditionalList = None
        chanceList = None
        minList = None
        maxList = None
        allInternalHusks = set()

        for line in f:
            line = line.strip()

            if(self.state == "Expecting Name"):
                name = "Undefined"
                type = "Undefined"
                image = "Undefined"
                immune = "Undefined"
                recurring = "Undefined"
                element = "Undefined"
                internalNameList = []
                internalList = []
                magnitudeList = []
                categoryList = []
                conditionalList = ["True", "True", "True", "True", "True", "True"]
                chanceList = [100, 100, 100, 100, 100, 100]
                minList = [0, 0, 0, 0, 0, 0]
                maxList = [0, 0, 0, 0, 0, 0]
                if(StatusEffectsParser.isEmptyText(line)):
                    continue
                name = nameTag.match(line).group(1)
                self.state = "Expecting Type"
                continue

            if(self.state == "Expecting Type"):
                type = typeTag.match(line).group(1)
                if(type == "Display"):
                    self.state = "Expecting Image"
                    continue
                elif(type == "Internal"):
                    self.state = "Expecting Recurring"
                    continue

            if(self.state == "Expecting Recurring"):
                recurring = recurringTag.match(line).group(1)
                self.state = "Expecting Immune"
                continue

            if(self.state == "Expecting Immune"):
                if(StatusEffectsParser.isEmptyText(line)):
                    immune = "None"
                else:
                    immune = immuneTag.match(line).group(1)
                iStatus = internalstatus.InternalStatus(name, recurring, immune)
                allInternalHusks.add(iStatus)
                self.state = "Expecting Name"
                continue

            if(self.state == "Expecting Image"):
                image = imageTag.match(line).group(1)
                self.state = "Expecting Element"
                continue

            if(self.state == "Expecting Element"):
                element = elementTag.match(line).group(1)
                self.state = "Top Level"
                continue

            if(self.state == "Top Level" or self.state == "Expecting Any"):
                # INTERNAL*
                # CATEGORY
                # REMOVED_ON
                if(StatusEffectsParser.isEmptyText(line)):
                    for i in range(len(internalNameList)):
                        iStatus = None
                        for husk in allInternalHusks:
                            if husk.name == internalNameList[i]:
                                iStatus = husk.cloneWithDetails(int(magnitudeList[i]), element, name)
                        internalList.append(iStatus)
                    displayStatus = status.Status()
                    displayStatus.populate(name, image, element, categoryList, internalList)
                    self.displayStatusList.append(displayStatus)
                    self.state = "Expecting Name"
                    continue
                if(internalTag.match(line)):
                    internalNameList.append(internalTag.match(line).group(1))
                    self.state = "Expecting Magnitude"
                    continue
                if(categoryTag.match(line)):
                    categoryList.append(categoryTag.match(line).group(1))
                    self.state = "Top Level"
                    continue
                if(removedOnTag.match(line)):
                    removedOn = removedOnTag.match(line).group(1)
                    self.state = "Top Level"
                    continue

            if(self.state == "Expecting Magnitude" or self.state == "Expecting Any"):
                # CHANCE
                # CONDITIONAL
                # MAGNITUDE*
                # MIN
                # MAX
                if((self.state != "Expecting Any") and magnitudeTag.match(line)):
                    magnitudeList.append(magnitudeTag.match(line).group(1))
                    self.state = "Expecting Any"
                    continue
                # We always want to match up the following with the appropriate internal.
                # This is accomplished by finding out what the index of the most recently
                # appended internal is and using that as the corresponding index.
                index = len(internalNameList) - 1
                if(conditionalTag.match(line)):
                    conditionalList[index] = conditionalTag.match(line).group(1)
                    continue
                if(chanceTag.match(line)):
                    chanceList[index] = chanceTag.match(line).group(1)
                    continue
                if(minTag.match(line)):
                    minList[index] = minTag.match(line).group(1)
                    continue
                if(maxTag.match(line)):
                    maxList[index] = maxTag.match(line).group(1)
                    continue
            raise InvalidDataFileSyntax("Unkown or misplaced Tag: " + line + " in " + fileName)

        return self.displayStatusList

    @staticmethod
    def isEmptyText(text):
        return (len(text) == 0 or text[0] == "#" or StatusEffectsParser.onlyWhitespace(text))

    @staticmethod
    def onlyWhitespace(text):
        clearedLine = text.replace(" ", "")
        return (clearedLine == "")

if __name__ == "__main__":
    parser = StatusEffectsParser()
    parser.parseAll("./data/Status_Effects_Data.txt")
    for s in parser.displayStatusList:
        print (s.displayName + ":")
        for i in range(len(s.internalList)):
            if s.internalList[i]:
                print ("    Internal= " + s.internalList[i].name)
    print("Number of loaded statuses: " + str(len(parser.displayStatusList)))












