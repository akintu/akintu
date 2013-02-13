#!/usr/bin/python

import sys
import monstersparser
import monster
import cctemplatesparser
import armorparser
import weaponsparser
import trapsparser
import statuseffectsparser
import copy
import playercharacter
import location
from const import *

class TheoryCraft(object):
    
    hasLoaded = False
    
    classes = []
    statuses = []
    armors = []
    weapons = []
    traps = []
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
        parser = trapsparser.TrapsParser()
        TheoryCraft.traps = parser.parseAll("./data/Trap_Data.txt")
        parser = statuseffectsparser.StatusEffectsParser()
        TheoryCraft.statuses = parser.parseAll("./data/Status_Effects_Data.txt")
        TheoryCraft.hasLoaded = True
        
    @staticmethod
    def getMonster(index=None, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2)), level=1, region=None, name=None):
        theMonster = None
        if name:
            for mon in TheoryCraft.monsters:
                if mon.name == name:
                    theMonster = monster.Monster(mon)
                    break
        # TODO: search by level
        # TODO: search by region
        # TODO: This is a stub...
        else:
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
        
        
        