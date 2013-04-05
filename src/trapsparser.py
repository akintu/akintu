#!/usr/bin/python

################################# This file is no longer in use! ###############################

import sys
import re
from trap import TrapTemplate
from statuseffectsparser import InvalidDataFileSyntax



class TrapsParser(object):

    def __init__(self):
        """Prepares the parser.
        Possible states are:
          "Expecting Name" -- not currently parsing an object,
             may have just finished parsing an object.
          "Expecting Rating"
          "Expecting Rarity"
          "Expecting Effect A"
          "Expecting Parameters A"
          "Expecting Parameters B"
          "Expecting Parameters C"
          """
        self.state = "Expecting Name"

        self.trapTemplateList = []

    # Paths by State:
    #   Expecting Name              --> Expecting Rating   --> Expecting Rarity
    #   Expecting Rarity            --> Expecting Effect A --> Expecting Parameters A
    #   etc.
    #
    # Required Ordered Tags:
    #
    #    NAME
    #    TRAP RATING
    #    RARITY WEIGHT
    #    EFFECT A      ...
    #    EFFECT B      ...
    #    EFFECT C      ...
    #
    # Valid effect tags:
    #
    #    ELEMENT
    #    MIN
    #    MAX
    #    MAGNITUDE
    #    POISON RATING
    #    DURATION
    #    QUANTITY
    #

    def parseAll(self, fileName):
        nameTag = re.compile("(?:\[NAME: )(.*)(?:\])", re.I)
        trapRatingTag = re.compile("(?:\[TRAP RATING: )(.*)(?:\])", re.I)
        rarityTag = re.compile("(?:\[RARITY WEIGHT: )(.*)(?:\])", re.I)
        effectATag = re.compile("(?:\[EFFECT A: )(.*)(?:\])", re.I)
        effectBTag = re.compile("(?:\[EFFECT B: )(.*)(?:\])", re.I)
        effectCTag = re.compile("(?:\[EFFECT C: )(.*)(?:\])", re.I)
        elementTag = re.compile("(?:\[ELEMENT: )(.*)(?:\])", re.I)
        minTag = re.compile("(?:\[MIN: )(.*)(?:\])", re.I)
        maxTag = re.compile("(?:\[MAX: )(.*)(?:\])", re.I)
        magnitudeTag = re.compile("(?:\[MAGNITUDE: )(.*)(?:\])", re.I)
        poisonRatingTag = re.compile("(?:\[POISON RATING: )(.*)(?:\])", re.I)
        durationTag = re.compile("(?:\[DURATION: )(.*)(?:\])", re.I)
        quantityTag = re.compile("(?:\[QUANTITY: )(.*)(?:\])", re.I)
        wModHeavyTag = re.compile("(?:\[WEIGHT MOD HEAVY: )(.*)(?:\])", re.I)
        wModMediumTag = re.compile("(?:\[WEIGHT MOD MEDIUM: )(.*)(?:\])", re.I)
        wModLightTag = re.compile("(?:\[WEIGHT MOD LIGHT: )(.*)(?:\])", re.I)




        f = open(fileName, 'r')

        name = None
        tRating = None
        rarity = None
        effectList = None

        for line in f:
            line = line.strip()

            if(self.state == "Expecting Name"):
                name = "Undefined"
                tRating = -1
                rarity = -1
                effectList = [{'name': None},{'name': None},{'name': None}]
                if(TrapsParser.isEmptyText(line)):
                    continue
                name = nameTag.match(line).group(1)
                self.state = "Expecting Rating"
                continue

            if(self.state == "Expecting Rating"):
                tRating = trapRatingTag.match(line).group(1)
                self.state = "Expecting Rarity"
                continue

            if(self.state == "Expecting Rarity"):
                rarity = TrapsParser.reformatRanges(rarityTag.match(line).group(1))
                self.state = "Expecting Effect A"
                continue

            if(self.state == "Expecting Effect A"):
                effectList[0]['name'] = effectATag.match(line).group(1)
                self.state = "Expecting Parameters A"
                continue

            if(self.state == "Expecting Parameters A"):
                if( effectBTag.match(line) ):
                    effectList[1]['name'] = effectBTag.match(line).group(1)
                    self.state = "Expecting Parameters B"
                elif( elementTag.match(line) ):
                    effectList[0]['element'] = elementTag.match(line).group(1)
                elif( minTag.match(line) ):
                    effectList[0]['min'] = minTag.match(line).group(1)
                elif( maxTag.match(line) ):
                    effectList[0]['max'] = maxTag.match(line).group(1)
                elif( magnitudeTag.match(line) ):
                    effectList[0]['magnitude'] = magnitudeTag.match(line).group(1)
                elif( poisonRatingTag.match(line) ):
                    effectList[0]['pRating'] = poisonRatingTag.match(line).group(1)
                elif( durationTag.match(line) ):
                    effectList[0]['duration'] = durationTag.match(line).group(1)
                elif( quantityTag.match(line) ):
                    effectList[0]['quantity'] = quantityTag.match(line).group(1)
                elif( wModHeavyTag.match(line) ):
                    effectList[0]['wModHeavy'] = wModHeavyTag.match(line).group(1)
                elif( wModMediumTag.match(line) ):
                    effectList[0]['wModMedium'] = wModMediumTag.match(line).group(1)
                elif( wModLightTag.match(line) ):
                    effectList[0]['wModLight'] = wModLightTag.match(line).group(1)
                continue

            if(self.state == "Expecting Parameters B"):
                if( effectCTag.match(line) ):
                    effectList[2]['name'] = effectCTag.match(line).group(1)
                    self.state = "Expecting Parameters C"
                elif( elementTag.match(line) ):
                    effectList[1]['element'] = elementTag.match(line).group(1)
                elif( minTag.match(line) ):
                    effectList[1]['min'] = minTag.match(line).group(1)
                elif( maxTag.match(line) ):
                    effectList[1]['max'] = maxTag.match(line).group(1)
                elif( magnitudeTag.match(line) ):
                    effectList[1]['magnitude'] = magnitudeTag.match(line).group(1)
                elif( poisonRatingTag.match(line) ):
                    effectList[1]['pRating'] = poisonRatingTag.match(line).group(1)
                elif( durationTag.match(line) ):
                    effectList[1]['duration'] = durationTag.match(line).group(1)
                elif( quantityTag.match(line) ):
                    effectList[1]['quantity'] = quantityTag.match(line).group(1)
                elif( wModHeavyTag.match(line) ):
                    effectList[1]['wModHeavy'] = wModHeavyTag.match(line).group(1)
                elif( wModMediumTag.match(line) ):
                    effectList[1]['wModMedium'] = wModMediumTag.match(line).group(1)
                elif( wModLightTag.match(line) ):
                    effectList[1]['wModLight'] = wModLightTag.match(line).group(1)
                continue

            if(self.state == "Expecting Parameters C"):
                if( TrapsParser.isEmptyText(line) ):
                    self.state = "Expecting Name"
                    for i in range(len(effectList)):
                        for key, val in effectList[i].iteritems():
                            effectList[i][key] = TrapsParser.reformatRanges(val)
                    tTemplate = TrapTemplate(name, tRating, rarity, effectList)
                    self.trapTemplateList.append(tTemplate)
                elif( elementTag.match(line) ):
                    effectList[2]['element'] = elementTag.match(line).group(1)
                elif( minTag.match(line) ):
                    effectList[2]['min'] = minTag.match(line).group(1)
                elif( maxTag.match(line) ):
                    effectList[2]['max'] = maxTag.match(line).group(1)
                elif( magnitudeTag.match(line) ):
                    effectList[2]['magnitude'] = magnitudeTag.match(line).group(1)
                elif( poisonRatingTag.match(line) ):
                    effectList[2]['pRating'] = poisonRatingTag.match(line).group(1)
                elif( durationTag.match(line) ):
                    effectList[2]['duration'] = durationTag.match(line).group(1)
                elif( quantityTag.match(line) ):
                    effectList[2]['quantity'] = quantityTag.match(line).group(1)
                elif( wModHeavyTag.match(line) ):
                    effectList[2]['wModHeavy'] = wModHeavyTag.match(line).group(1)
                elif( wModMediumTag.match(line) ):
                    effectList[2]['wModMedium'] = wModMediumTag.match(line).group(1)
                elif( wModLightTag.match(line) ):
                    effectList[2]['wModLight'] = wModLightTag.match(line).group(1)
                continue

            raise InvalidDataFileSyntax("Unkown or misplaced Tag: " + line + " in " + fileName)

        f.close()
        return self.trapTemplateList

    @staticmethod
    def isEmptyText(text):
        return (len(text) == 0 or text[0] == "#" or TrapsParser.onlyWhitespace(text))

    @staticmethod
    def onlyWhitespace(text):
        clearedLine = text.replace(" ", "")
        return (clearedLine == "")

    @staticmethod
    def reformatRanges(stringValue):
        extractionRegex = re.compile("(\d+) \+ (\d+\.*\d*)L")
        if not extractionRegex.match(stringValue):
            return stringValue
        base = extractionRegex.match(stringValue).group(1)
        perLevel = extractionRegex.match(stringValue).group(2)
        return [base, perLevel]

if __name__ == "__main__":
    parser = TrapsParser()
    parser.parseAll("./data/Trap_Data.txt")
    for template in parser.trapTemplateList:
        print template.name
        print template.trapRating
        print template.rarity
        print template.effectA
        print template.effectB
        print template.effectC


