#!/usr/bin/python

import sys
import person
import ability
import passiveability
import spell
import region
import servercombat
import command
from dice import *
from const import *
from combat import *

# monster.py
# Author: Devin Ekins -- G. Cube
#
# This module contains the basic Monster object used for all "Monsters", or
# hostile Person objects, in Akintu.  These monsters are populated with
# properties according to the Monster_Data.txt data file which is parsed
# elsewhere.  
#
# This module also controls a large portion of the combat AI for the monsters.
# As such, it is more tightly coupled with the combatserver.py module than I 
# would like.  This is evidenced by the globalServer variable which caches a
# reference to the game's server.
#
# Some expiramentation with a particular unadvised but functional pattern is
# used here to assign data values from a passed in kwargs dict.  If this pattern
# is ever revoked, the compensatory code to replace that pattern has been
# included but is presently commented out.

class Monster(person.Person):

    ERROR = "INITIALIZATION_FAILURE"
    globalServer = None

    @staticmethod
    def setFrom(argDict, variableName, defaultValue=ERROR):
        if( (variableName not in argDict) or (argDict[variableName] == "None") ):
            if defaultValue == Monster.ERROR:
                raise person.IncompleteDataInitialization( "The parameter: " + variableName + " must be specified, but isn't.")
            else:
                return defaultValue
        else:
            return argDict[variableName]


    def __init__(self, argDict, playerNum=1):
        person.Person.__init__(self, argDict)
        self.attackPower = 100
        self.team = "Monsters"
        # TODO: Find a way to distinguish between summons and monsters for the 'team'. Perhaps inherit from Person seperately?
        self.playerNum = playerNum
        self.level = Monster.setFrom(argDict, 'minLevel')
        self.minLevel = self.level
        self.maxLevel = Monster.setFrom(argDict, 'maxLevel')
        self.name = Monster.setFrom(argDict, 'name')
        self.GP = Monster.setFrom(argDict, 'GP')
        self.experience = self.GP * self.level
        self.type = Monster.setFrom(argDict, 'type')

        self.abilityList = []
        self.spellList = []
        self.passiveAbility = None

        self.specialAttackOneName = Monster.setFrom(argDict, 'specialAttackOne', None)
        if self.specialAttackOneName:
            if "Spell: " in self.specialAttackOneName:
                spellName = self.specialAttackOneName[7:]
                self.spellList.append(spell.Spell(spellName, self))
            else:
                self.abilityList.append(ability.Ability(self.specialAttackOneName, self))

        self.specialAttackTwoName = Monster.setFrom(argDict, 'specialAttackTwo', None)
        if self.specialAttackTwoName:
            if "Spell: " in self.specialAttackTwoName:
                spellName = self.specialAttackTwoName[7:]
                self.spellList.append(spell.Spell(spellName, self))
            else:
                self.abilityList.append(ability.Ability(self.specialAttackTwoName, self))

        self.specialAttackThreeName = Monster.setFrom(argDict, 'specialAttackThree', None)
        if self.specialAttackThreeName:
            if "Spell: " in self.specialAttackThreeName:
                spellName = self.specialAttackThreeName[7:]
                self.spellList.append(spell.Spell(spellName, self))
            else:
                self.abilityList.append(ability.Ability(self.specialAttackThreeName, self))

        self.specialPropertyName = Monster.setFrom(argDict, 'specialProperty', None)
        if self.specialPropertyName:
            self.passiveAbility = passiveability.PassiveAbility(self.specialPropertyName, self)

        self.attackElement = Monster.setFrom(argDict, 'attackElement')
        self.attackMinDamage = Monster.setFrom(argDict, 'attackMin')
        self.attackMaxDamage = Monster.setFrom(argDict, 'attackMax')
        self.attackRange = Monster.setFrom(argDict, 'attackRange')
        self.baseMagicResist = Monster.setFrom(argDict, 'magicResist')
        
        self.__dict__.update(argDict)
        # ~~~ Expiramental python pattern ahead! You've been warned! ~~~
        #
        # self.levelupArmorPenetration = Monster.setFrom(argDict, 'levelupArmorPenetration')
        # self.levelupCunning = Monster.setFrom(argDict, 'levelupCunning')
        # self.levelupDexterity = Monster.setFrom(argDict, 'levelupDexterity')
        # self.levelupMinDamage = Monster.setFrom(argDict, 'levelupMinDamage')
        # self.levelupMaxDamage = Monster.setFrom(argDict, 'levelupMaxDamage')
        # self.levelupDR = Monster.setFrom(argDict, 'levelupDR')
        # self.levelupHP = Monster.setFrom(argDict, 'levelupHP')
        # self.levelupMP = Monster.setFrom(argDict, 'levelupMP')
        # self.levelupArcaneResistance = Monster.setFrom(argDict, 'levelupArcaneResistance')
        # self.levelupBludgeoningResistance = Monster.setFrom(argDict, 'levelupBludgeoningResistance')
        # self.levelupColdResistance = Monster.setFrom(argDict, 'levelupColdResistance')
        # self.levelupDivineResistance = Monster.setFrom(argDict, 'levelupDivineResistance')
        # self.levelupElectricResistance = Monster.setFrom(argDict, 'levelupElectricResistance')
        # self.levelupFireResistance = Monster.setFrom(argDict, 'levelupFireResistance')
        # self.levelupPiercingResistance = Monster.setFrom(argDict, 'levelupPiercingResistance')
        # self.levelupPoisonResistance = Monster.setFrom(argDict, 'levelupPoisonResistance')
        # self.levelupShadowResistance = Monster.setFrom(argDict, 'levelupShadowResistance')
        # self.levelupSlashingResistance = Monster.setFrom(argDict, 'levelupSlashingResistance')
        # self.levelupMagicResist = Monster.setFrom(argDict, 'levelupMagicResist')
        # self.levelupPoisonTolerance = Monster.setFrom(argDict, 'levelupPoisonTolerance')
        # self.levelupSpellpower = Monster.setFrom(argDict, 'levelupSpellpower')
        # self.levelupStrength = Monster.setFrom(argDict, 'levelupStrength')
        self.remainingMovementTiles = 0
                
        self.registerBasicAttacks()

        self.levelSet = False
        self.currentCombatPane = None
        self.detectedPlayers = []

    def registerBasicAttacks(self):
        self.abilityList.append(ability.Ability("Melee Attack", self))
        rangedAttack = ability.Ability("Ranged Attack", self)
        rangedAttack.range = self.attackRange
        self.abilityList.append(rangedAttack)

    def applyBonusDamage(self, dieRoll, ignoreVar):
        ''' Python doesn't support the ability to overload methods... thus the ignoreVar.'''
        dieRoll *= self.attackPower / 100.0
        return int(round(dieRoll))

    def setLevel(self, level):
        '''Method should only be called once after creation to set the level of a
        monster.  Will print a warning message if this is called more than once.'''
        if self.levelSet:
            print "WARNING: Level for this monster has been set previously.  Statistics will be incorrect."
        if level < self.minLevel:
            print "Level specified is below this monster's minimum level of " + str(self.minLevel) + "."
            return
        self.levelSet = True
        diff = level - self.minLevel
        self.baseArmorPenetration += self.levelupArmorPenetration * diff
        self.baseCunning += self.levelupCunning * diff
        self.baseDexterity += self.levelupDexterity * diff
        self.attackMinDamage += self.levelupMinDamage * diff
        self.attackMaxDamage += self.levelupMaxDamage * diff
        self.baseDR += self.levelupDR * diff
        self.baseHP += self.levelupHP * diff
        self.HP = self.totalHP
        self.baseMP += self.levelupMP * diff
        self.MP = self.totalMP
        self._baseArcaneResistance += self.levelupArcaneResistance * diff
        self._baseBludgeoningResistance += self.levelupBludgeoningResistance * diff
        self._baseColdResistance += self.levelupColdResistance * diff
        self._baseDivineResistance += self.levelupDivineResistance * diff
        self._baseElectricResistance += self.levelupElectricResistance * diff
        self._baseFireResistance += self.levelupFireResistance * diff
        self._basePiercingResistance += self.levelupPiercingResistance * diff
        self._basePoisonResistance += self.levelupPoisonResistance * diff
        self._baseShadowResistance += self.levelupShadowResistance * diff
        self._baseSlashingResistance += self.levelupSlashingResistance * diff
        self.baseMagicResist += self.levelupMagicResist * diff
        self.basePoisonTolerance += self.levelupPoisonTolerance * diff
        self.baseSpellpower += self.levelupSpellpower * diff
        self.baseStrength += self.levelupStrength * diff
        self.level = level
        self.experience = self.GP * self.level

    def adjustMaxHP(self):
        if self.playerNum == 2:
            self.baseHP = int(self.baseHP * 1.5)
        elif self.playerNum == 3:
            self.baseHP = int(self.baseHP * 2)
        elif self.playerNum == 4:
            self.baseHP = int(self.baseHP * 2.5)
        self.HP = self.baseHP
            
    def getDetailTuple(self):
        '''DEPRECATED'''
        return ("Monster", self.name, self.level)

    def dehydrate(self, save=False):
        if not save:
            return "@" + self.name + "@" + `self.level` + "@" + `self.playerNum`
        _monst = {"NAME": self.name, "LEVEL": self.level, "PLAYERNUM": self.playerNum, "AI": self.ai.dehydrate()}
        return _monst

    def getSufficientAbilities(self):
        sufficient = []
        for abil in self.abilityList:
            if self.AP >= abil.APCost and abil.name not in self.cooldownList:
                sufficient.append(abil)
        for spell in self.spellList:
            if self.AP >= spell.APCost and not self.onCooldown(spell.name) and self.MP >= spell.MPCost:
                sufficient.append(spell)
        return sufficient

    def getUsableAbilities(self, server=None, combatPane=None, visiblePlayers="All"):
        if not server:
            server = Monster.globalServer
        else:
            Monster.globalServer = server
        if not combatPane:
            combatPane = self.currentCombatPane
        else:
            self.currentCombatPane = combatPane

        if self.hasStatus("Stun"):
            return []
        sufficient = self.getSufficientAbilities()
        # We now have a list of abilities that can be used according to
        # AP/MP costs and cooldowns.
        usable = []
        for abil in sufficient:
            if abil.targetType == "self":
                if abil.canUse(self)[0]: # Target is self
                    usable.append((abil, self))
            if abil.targetType == "hostile":
                players = self.getPlayersInRange(abil.range, server, combatPane, visiblePlayers)
                for player in players:
                    if abil.canUse(player)[0] and (not isinstance(abil, spell.Spell) or abil.shouldUse(player)):
                        usable.append((abil, player))
            if abil.targetType == "friendly":
                monsters = self.getMonstersInRange(abil.range, server, combatPane)
                for mon in monsters:
                    if abil.canUse(mon)[0] and abil.shouldUse(mon):
                        usable.append((abil, mon))
        return usable

    def selectAction(self, server, combatPane):
        """Returns a duple of an ability/spell and its target."""
        choicesList = self.getUsableAbilities(server, combatPane)
        choice = None
        if not choicesList:
            return None
        else:
            return Dice.choose(choicesList)

    def performAction(self, server=None, combatPane=None):
        """Select a usable ability, and perform it.
        Returns the name of the ability used if an action was possible and thus completed,
        Returns "Failure" if no action was possible."""
        # Initialize and update server and combatPane
        if not server:
            server = Monster.globalServer
        else:
            Monster.globalServer = server
        if not combatPane:
            combatPane = self.currentCombatPane
        else:
            self.currentCombatPane = combatPane

        # Select targets and perform actions, if possible.
        actionDuple = self.selectAction(server, combatPane)
        if actionDuple:
            Combat.sendCombatMessage(self.name + " is using ability: " + actionDuple[0].name + " on " + 
                                     actionDuple[1].name, actionDuple[1], color='red')
            abil = actionDuple[0]
            target = actionDuple[1]
            abil.use(target)
            if self != target:
                self.faceTarget(target)
            return abil.name
        return "Failure"

    def faceTarget(self, target):
        self.cLocation = self.cLocation.move(self.cLocation.direction_to(target.cLocation), 0)
        messageObj = command.Command("PERSON", "MOVE", id=self.id, location=self.cLocation)
        self.globalServer.SDF.queue.put((None, messageObj))
       
    def getMonstersInRange(self, range, server=None, combatPane=None):
        '''Returns a list of monsters within a set range of this monster.  Will NOT
        perform any form of sorting.'''
        if not server:
            server = Monster.globalServer
        if not combatPane:
            combatPane = self.currentCombatPane
        
        reg = region.Region()
        if range == 1:
            reg("ADD", "SQUARE", self.cLocation.move(7, 1), self.cLocation.move(3, 1))
        else:
            reg("ADD", "CIRCLE", self.cLocation, range)        
        allMonsters = [server.person[x] for x in server.pane[combatPane].person if
                        server.person[x].team == "Monsters"]
        monsters = []
        for mon in allMonsters:
            if mon.cLocation in reg:
                monsters.append(mon)
        return monsters
       
    def getPlayersInRange(self, range, server=None, combatPane=None, visiblePlayers="All"):
        """Returns a list of players within a set range of this monster.  Will sort them according
        to distance from this monster."""
        if not server:
            server = Monster.globalServer
        if not combatPane:
            combatPane = self.currentCombatPane

        reg = region.Region()
        if range == 1:
            reg("ADD", "SQUARE", self.cLocation.move(7, 1), self.cLocation.move(3, 1))
        else:
            reg("ADD", "CIRCLE", self.cLocation, range)
        players = []
        if visiblePlayers == "All":
            allPlayers = [server.person[x] for x in server.pane[combatPane].person if
                        server.person[x].team == "Players"]
        else:
            allPlayers = visiblePlayers
        
        for player in allPlayers:
            if player.cLocation in reg and player.team == "Players":
                players.append(player)

        distanceTuples = []
        for p in players:
            distanceTuples.append((p, self.cLocation.distance(p.cLocation)))
        
        sortedTuples = sorted(distanceTuples, key=lambda x: x[1])
        sortedPlayers = [x[0] for x in sortedTuples]
        return sortedPlayers

    def getNearestPlayer(self, visiblePlayers):
        '''Returns the nearest player to this monster.'''
        #allPlayers = [Monster.globalServer.person[x] for x in
        #              Monster.globalServer.pane[self.currentCombatPane].person if
        #              Monster.globalServer.person[x].team == "Players"]
        if not visiblePlayers:
            return None
        closestDistance = 999
        closestPlayer = None
        for player in visiblePlayers:
            if player.cPane != self.cPane:
                try:
                    self.detectedPlayers.remove(player)
                except:
                    pass
                continue
            thisDistance = self.cLocation.distance(player.cLocation)
            if thisDistance < closestDistance:
                closestDistance = thisDistance
                closestPlayer = player
        return closestPlayer




