#!/usr/bin/python

import sys
import monstersparser
import cctemplatesparser
import armorparser
import weaponsparser
import trapsparser
import statuseffectsparser
import copy

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
        TheoryCraft.armorList = parser.parseAll("./data/Armor_Data.txt")
        parser = weaponsparser.WeaponsParser()
        TheoryCraft.weapons = parser.parseAll("./data/Weapon_Data.txt")
        parser = trapsparser.TrapsParser()
        TheoryCraft.traps = parser.parseAll("./data/Trap_Data.txt")
        parser = statuseffectsparser.StatusEffectsParser()
        TheoryCraft.statuses = parser.parseAll("./data/Status_Effects_Data.txt")
        TheoryCraft.hasLoaded = True
        
    @staticmethod
    def getMonster(level=1, region=None, name=None):
        if name:
            for mon in TheoryCraft.monsters:
                if mon.name == name:
                    return copy.deepcopy(mon)
        # TODO: search by level
        # TODO: search by region
        # TODO: This is a stub...
        return copy.deepcopy(TheoryCraft.monsters[0])
        
    @staticmethod
    def getNewPlayerCharacter(race, characterClass):
        race = race.capitalize
        characterClass = characterClass.capitalize()
        for char in TheoryCraft.classes:
            if race == char.race and characterClass == char.characterClass:
                return copy.deepcopy(char)
        print "Bad character name/race, returning nothing; you're so stupid."
        
        
        