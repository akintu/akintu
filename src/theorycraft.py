#!/usr/bin/python

import sys
import monstersparser
import monster
import cctemplatesparser
import equipment
import armorparser
import weaponsparser
import statuseffectsparser
import playercharacter
import location
import consumable
import wealth
import magicalproperty
from combat import Combat
from random import randint, choice
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

        Combat.allStatuses = TheoryCraft.statuses

        TheoryCraft.hasLoaded = True

    @staticmethod
    def getWeaponByName(name, ip=0):
        '''Gets a weapon with the given name and the
        specified base item points.'''
        for wep in TheoryCraft.weapons:
            if wep['name'] == name:
                return equipment.Weapon(wep).cloneWithMagicalProperties(ip)
        return

    @staticmethod
    def getArmorByName(name, ip=0):
        '''Gets a piece of armor with the given name and the
        specified base item points.'''
        for arm in TheoryCraft.armors:
            if arm['name'] == name:
                return equipment.Armor(arm).cloneWithMagicalProperties(ip)
        return

    @staticmethod
    def rehydrateTreasure(id):
        print "DEBUG: " + id
        if id in consumable.Consumable.allPotions or id in consumable.Consumable.allPoisons:
            # TODO: Check for other consumable types!!
            return consumable.Consumable(id)
        if "Gold" in id:
            # Lousy hack, make better TODO.
            amount = int(id.partition(": ")[2])
            return wealth.Wealth("Gold", amount)
        return TheoryCraft.rehydrateEquipment(id)
        
    @staticmethod
    def rehydrateEquipment(id):
        nameAndProps = id.partition("$")
        name = nameAndProps[0]
        
        # Create temporary husk of an item, with no ip.
        weapon = TheoryCraft.getWeaponByName(name, -500)
        armor = TheoryCraft.getArmorByName(name, -500)
        item = weapon
        if not weapon:
            item = armor
            
        propertyList = []
        if nameAndProps[2]:
            propSplits = nameAndProps[2].split("$")
            for piece in propSplits:
                propName = piece.partition("#")[0]
                propCount = piece.partition("#")[2]
                propertyList.append(magicalproperty.MagicalProperty(
                    magicalproperty.MagicalProperty.allProperties[propName], item, propName, int(propCount)))
        
        rValue = item.cloneWithMagicalProperties(0, propertyList)
        return rValue
        
    @staticmethod
    def convertFromDetails(tuple):
        '''Converts a 'detail tuple' representing the intermediate state of
        a Person to an actual instance of a Person.'''
        if tuple[0] == "Monster":
            return TheoryCraft.getMonster(name=tuple[1], level=tuple[2])
        elif tuple[0] == "Player":
            return TheoryCraft.getNewPlayerCharacter(name=tuple[1], race=tuple[2], characterClass=tuple[3])
        else:
            print "Warning: Attempted to convert from invalid tuple: " + str(tuple[0]) + " ."

    @staticmethod
    def getMonster(index=None, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2)), level=None, name=None, tolerance=1, ignoreMaxLevel=False):
        ''' Generates a monster for the overworld.
        If name is specified:
            Create the exact monster specified with the exact level specified.
        If name is not specified and level is specified:
            Default behavior, generate a random monster of the given level + or - the tolerance (default=1)
        If neither name nor level are specified:
            Testing mode; generate a non-deterministic random monster within levels 1-4.'''
        if not level:
            level = Dice.roll(1,3)
        theMonster = None
        levelChoice = level
        if name:
            for mon in TheoryCraft.monsters:
                if mon['name'] == name:
                    theMonster = monster.Monster(mon)
                    break
        else:
            inLevelList = None
            lower = max(1, level - tolerance)
            upper = min(20, level + tolerance)
            levelChoice = None
            if lower == upper:
                levelChoice = lower
            else:
                levelChoice = randint(lower, upper)

            if ignoreMaxLevel:
                inLevelList = [x for x in TheoryCraft.monsters if x['minLevel'] <= levelChoice]
            else:
                inLevelList = [x for x in TheoryCraft.monsters if x['minLevel'] <= levelChoice and x['maxLevel'] >= levelChoice]
            if inLevelList:
                theMonster = monster.Monster(choice(inLevelList))
            else:
                # No monster of this level exists, just give a default monster for testing.
                theMonster = monster.Monster(TheoryCraft.monsters[0])
        theMonster.location = loc
        theMonster.setLevel(levelChoice)
        return theMonster

    @staticmethod
    def getNewPlayerCharacter(race, characterClass, loc=location.Location((0, 0), (PANE_X/2, PANE_Y/2)),
                              name="Milton Filbert"):
        race = race.lower()
        characterClass = characterClass.lower()
        selection = race + " " + characterClass
        for char_dict in TheoryCraft.classes:
            if char_dict['name'].lower() == race + " " + characterClass:
                pc = playercharacter.PlayerCharacter(char_dict, name=name)
                pc.location = loc
                return pc
        print "Bad character name/race, returning nothing; you're so stupid."

    @staticmethod
    def generateMonsterGroup(initialMonster, numberOfPlayers=1, ignoreMaxLevel=False):
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
        firstMonster = TheoryCraft.getMonster(loc=initialMonster.location, level=initialMonster.level,
                                              name=initialMonster.name)
        listOfMonsters = [firstMonster]
        if ignoreMaxLevel:
            subList = [x for x in TheoryCraft.monsters if
                       x['minLevel'] <= initialMonster.level]
        else:
            subList = [x for x in TheoryCraft.monsters if
                       x['minLevel'] <= initialMonster.level and
                       x['maxLevel'] >= initialMonster.level]
        minGP = initialMonster.GP
        for m in subList:
            if m['GP'] < minGP:
                minGP = m['GP']
        currentGP = initialMonster.GP
        numMonsters = 0
        while(minGP <= TheoryCraft.GROUP_GP - currentGP and numMonsters < 6):
            selection = None
            if len(subList) == 1:
                selection = 0
            else:
                selection = randint(0, len(subList) - 1)
            if subList[selection]['GP'] <= TheoryCraft.GROUP_GP - currentGP:
                addingMonster = monster.Monster(subList[selection])
                if initialMonster.level >= addingMonster.minLevel:
                    addingMonster.setLevel(initialMonster.level)
                listOfMonsters.append(monster.Monster(subList[selection]))
                currentGP += subList[selection]['GP']
                numMonsters += 1

        for mon in listOfMonsters:
            mon.adjustMaxHP(numberOfPlayers)
        return listOfMonsters



