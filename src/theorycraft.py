#!/usr/bin/python

import sys
import monstersparser
import monster
import cctemplatesparser
import equipment
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
    def getWeaponByName(name, ip=0):
        '''Gets a weapon with the given name and the
        specified base item points.'''
        for wep in TheoryCraft.weapons:
            if wep['name'] == name:
                return equipment.Weapon(**wep).cloneWithMagicalProperties(ip)
        print "Weapon name: '" + name + "' not found in master list."
        
    @staticmethod
    def getArmorByName(name, ip=0):
        '''Gets a piece of armor with the given name and the
        specified base item points.'''
        for arm in TheoryCraft.armors:
            if arm['name'] == name:
                return equipment.Armor(arm).cloneWithMagicalProperties(ip)
        print "Armor name: '" + name + "' not found in master list."    
        
    @staticmethod
    def getMonster(index=None, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2)), level=None, name=None, tolerance=1, ignoreMaxLevel=False):
        if not level:
            level = Dice.roll(1,3)
        theMonster = None
        levelChoice = Dice.roll(max(1, level - tolerance), min(20, level + tolerance))
        if name:
            for mon in TheoryCraft.monsters:
                if mon['name'] == name:
                    theMonster = monster.Monster(mon)
                    break
        else:
            inLevelList = None
            if ignoreMaxLevel: 
                inLevelList = [x for x in TheoryCraft.monsters if x['minLevel'] <= levelChoice]
            else:
                inLevelList = [x for x in TheoryCraft.monsters if x['minLevel'] <= levelChoice and x['maxLevel'] >= levelChoice]
            if inLevelList:
                choice = Dice.roll(0, len(inLevelList) - 1)
                theMonster = monster.Monster(inLevelList[choice])
            else:
                # No monster of this level exists, just give a default monster for testing.
                theMonster = monster.Monster(TheoryCraft.monsters[0])
        theMonster.location = loc
        theMonster.setLevel(levelChoice)
        return theMonster
        
    @staticmethod
    def getNewPlayerCharacter(race, characterClass, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2))):
        race = race.lower()
        characterClass = characterClass.lower()
        selection = race + " " + characterClass
        print selection
        for char in TheoryCraft.classes:
            if char['name'].lower() == race + " " + characterClass:
                pc = playercharacter.PlayerCharacter(char)
                pc.location = loc
                return pc
        print "Bad character name/race, returning nothing; you're so stupid."
        
    @staticmethod
    def generateMonsterGroup(initialMonster, levelTolerance=1, numberOfPlayers=1, ignoreMaxLevel=False):
        ''' Generates a 'random' grouping of monsters
        based on the Monster this method is called on.
        The initialMonster supplied will be in the group,
        and this method will attempt to fill up the GP (Group points).
        This method WILL scale the HP of the monsters.
        Inputs:
          initialMonster -- the Monster that was on the overworld
             representing this group.
          levelTolerance -- int*; defaults to 1.  Indicates the
                      number of levels +/- allowed to deviate
                      from the initial monster's level.
          numberOfPlayers -- int*; used to determine how much to scale
                      maximum HP by.
          ignoreMaxLevel -- bool*; if set to True, will allow monsters
                      to be generated beyond their recommended maximum
                      level.
        Outputs:
          list of Monsters '''
        # Add in category logic when we have regions?  Do we want this ever?
        listOfMonsters = [initialMonster]
        if ignoreMaxLevel:
            subList = [x for x in TheoryCraft.monsters if
                       x['minLevel'] <= initialMonster.level + levelTolerance]
        else:
            subList = [x for x in TheoryCraft.monsters if
                       x['minLevel'] <= initialMonster.level + levelTolerance and
                       x['maxLevel'] >= initialMonster.level - levelTolerance]
        minGP = initialMonster.GP
        for m in subList:
            if m['GP'] < minGP:
                minGP = m['GP']
        currentGP = initialMonster.GP
        while(minGP <= TheoryCraft.GROUP_GP - currentGP):
            selection = Dice.roll(0, len(subList) - 1)
            if subList[selection]['GP'] <= TheoryCraft.GROUP_GP - currentGP:
                addingMonster = monster.Monster(subList[selection])
                if initialMonster.level >= addingMonster.minLevel:
                    addingMonster.setLevel(initialMonster.level)
                listOfMonsters.append(monster.Monster(subList[selection]))
                currentGP += subList[selection]['GP']
                
        for mon in listOfMonsters:
            mon.adjustMaxHP(numberOfPlayers)
        return listOfMonsters
        
        
        