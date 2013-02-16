#!/usr/bin/python

import sys
import monstersparser
import monster
import cctemplatesparser
import armorparser
import weaponsparser
import statuseffectsparser
import copy
import playercharacter
import location
from dice import *
from const import *

class TheoryCraft(object):
    
    GROUP_GP = 10 # TODO: Move to const.py
    
    hasLoaded = False
    
    classes = []
    statuses = []
    armors = []
    weapons = []
    monsters = []
    
    @staticmethod
    def loadAll():
        if TheoryCraft.hasLoaded:
            print "Warning: The parsers have already loaded their data."
            
        parser = monstersparser.MonstersParser()
        TheoryCraft.monsters = parser.parseAll("./data/Monster_Data.txt")
        parser = cctemplatesparser.CCTemplatesParser()
        TheoryCraft.classes = parser.parseAll("./data/Character_Class_Data.txt", "./data/Race_Data.txt")
        parser = armorparser.ArmorParser()
        TheoryCraft.armors = parser.parseAll("./data/Armor_Data.txt")
        parser = weaponsparser.WeaponsParser()
        TheoryCraft.weapons = parser.parseAll("./data/Weapon_Data.txt")
        parser = statuseffectsparser.StatusEffectsParser()
        TheoryCraft.statuses = parser.parseAll("./data/Status_Effects_Data.txt")
        TheoryCraft.hasLoaded = True
        
    @staticmethod
    def getMonster(index=None, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2)), level=1, region=None, name=None):
        theMonster = None
        if name:
            for mon in TheoryCraft.monsters:
                if mon['name'] == name:
                    theMonster = monster.Monster(mon)
                    break
        # TODO: search by region
        # TODO: This is a stub...
        else:
            inLevelList = [x for x in TheoryCraft.monsters if x['level'] = level]
            if inLevelList:
                choice = Dice.roll(0, len(inLevelList) - 1)
                theMonster = monster.Monster(inLevelList[choice])
            else:
                # No monster of this level exists, just give a default monster for testing.
                theMonster = monster.Monster(TheoryCraft.monsters[0])
        theMonster.index = index
        theMonster.location = loc
        return theMonster
        
    @staticmethod
    def getNewPlayerCharacter(race, characterClass, index=None, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2))):
        race = race.capitalize()
        characterClass = characterClass.capitalize()
        for char in TheoryCraft.classes:
            if char['name'] == race + " " + characterClass:
                pc = playercharacter.PlayerCharacter(char)
                pc.index = index
                pc.location = loc
                return pc
        print "Bad character name/race, returning nothing; you're so stupid."
        
    @staticmethod
    def generateMonsterGroup(initialMonster, levelTolerance=1):
        ''' Generates a 'random' grouping of monsters
        based on the Monster this method is called on.
        The initialMonster supplied will be in the group,
        and this method will attempt to fill up the GP.
        This method will not scale the HP of the monsters.
        Inputs:
          initialMonster -- the Monster that was on the overworld
             representing this group.
          levelTolerance -- int*; defaults to 1.  Indicates the
                      number of levels +/- allowed to deviate
                      from the initial monster's level.
        Outputs:
          list of Monsters '''
        # TODO: Add in region logic when we have regions.
        listOfMonsters = [initialMonster]
        subList = [x for x in TheoryCraft.monsters if
                   x['level'] <= initialMonster.level + levelTolerance and
                   x['level'] >= initialMonster.level - levelTolerance]
        minGP = initialMonster.GP
        for m in subList:
            if m['GP'] < minGP:
                minGP = m['GP']
        currentGP = initialMonster.GP
        while(minGP <= TheoryCraft.GROUP_GP - currentGP):
            selection = Dice.roll(0, len(subList) - 1)
            if subList[selection]['GP'] <= TheoryCraft.GROUP_GP - currentGP:
                listOfMonsters.append(monster.Monster(subList[selection]))
                currentGP += subList[selection]['GP']
        return listOfMonsters
        