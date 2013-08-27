#!/usr/bin/python

import sys
from dice import *
import broadcast
import location
import command
from region import Region

# combat.py
# Author: Devin Ekins -- G. Cube
#
# combat.py is used to handle the majority of combat logic according to game
# rules.  See ability.py, spell.py, trait.py, status.py for other facets of
# Combat specific to individual activities.

class IncompleteMethodCall(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Combat(object):
    def __init__(self):
        pass

    gameServer = None
    allStatuses = None

    @staticmethod
    def sendToAll(character, type):
        '''Send an update of a given type to all players in the
        same combat instance as the updated player.'''
        messageObj = None
        if type == "AP":
            messageObj = command.Command("PERSON", "UPDATE", id=character.id, AP=character.AP)
        elif type == "MOVE_TILES":
            messageObj = command.Command("PERSON", "UPDATE", id=character.id, \
                    remainingMovementTiles=character.remainingMovementTiles)
        elif type == "MP":
            messageObj = command.Command("PERSON", "UPDATE", id=character.id, MP=character.MP)
        elif type == "HP":
            Combat.sendToAll(character, "HP_BUFFER")
            messageObj = command.Command("PERSON", "UPDATE", id=character.id, HP=character.HP)
        elif type == "MoveAPCost":
            messageObj = command.Command("PERSON", "UPDATE", id=character.id, \
                    overrideMovementAPCost=character.overrideMovementAPCost)
        elif type == "Status":
            messageObj = command.Command("PERSON", "UPDATE", id=character.id, \
                    statuses=Combat.encodeStatuses(character))
        elif type == "HP_BUFFER":
            messageObj = command.Command("UPDATE", "HP_BUFFER", id=character.id, \
                    bufferSum=character.getHPBufferSum())
        Combat.gameServer.broadcast(messageObj, -character.id)

    @staticmethod
    def sendCombatMessage(message, character, color="white", toAll=True):
        '''Send a message to all players in combat with the provided character.'''
        messageObj = command.Command("UPDATE", "TEXT", text=message, color=color)
        Combat.gameServer.broadcast(messageObj, -character.id if toAll else character.id)

    @staticmethod
    def encodeStatuses(character):
        '''Returns a version of this character's statusList that only contains the name and turnsLeft.
        Used for sending updates to the UI and the network.'''
        encodedList = []
        for stat in character.statusList:
            encodedList.append(stat.name, stat.turnsLeft)
        return encodedList

    @staticmethod
    def modifyResource(target, type, value):
        """Modifies the given resource by the given value.
           May need to implement listeners...
        Inputs:
          target == Person
          type == "AP", "MP", "HP"
          value == int, non-zero.
        Outputs:
          None"""
        type = type.upper()
        if type == "AP":
            target.AP += value
            Combat.sendToAll(target, "AP")
        elif type == "MP":
            target.MP += value
            if target.totalMP > 0:
                Combat._shoutResourceLevel(target, type, float(target.MP) / target.totalMP)
            Combat.sendToAll(target, "MP")
        elif type == "HP":
            target.HP += value
            Combat._shoutResourceLevel(target, type, float(target.HP) / target.totalHP)
            Combat.sendToAll(target, "HP")
        else:
            raise TypeError("Type: " + type + " is not valid.  Proper values are: 'HP', 'MP', or 'AP'.")

    @staticmethod
    def applyCooldown(target, abilityName, duration):
        """Adds the ability to the target's list of current cooldowns with the given
        duration.  No behavior is guaranteed if the character already has this ability on
        cooldown.
        Inputs:
          target == Person
          abilityName == "ExampleAbility"
          duration = positive int
        Outputs:
          None"""
        if (duration <= 0):
            return
        target.cooldownList.append([abilityName, duration])
        # Should we check here if the abilityName matches any known ability?  That is, check for typos?

    @staticmethod
    def calcPhysicalHitChance(offense, defense, outrightMiss=False):
        """Uses the game rules' dodge mechanics to compute how likely a
        dodge vs. accuracy lineup would be.
        Inputs:
          offense -- int probably accuracy
          defense -- int probably dodge
        Outputs:
          [int, int]
            index[0] == chanceToHit (5 to 100)
            index[1] == any crit modification from accuracy extremes
                        (will typically be 0)"""
        accCritMod = 0
        chanceToHit = None
        delta = offense - defense
        if(20 < delta):
            chanceToHit = 100
            accCritMod = (delta - 20) * 0.25
        elif(0 <= delta <= 20):
            chanceToHit = 80 + delta
        elif(-5 <= delta < 0):
            chanceToHit = 80 - delta * 4
        elif(-15 <= delta < -5):
            chanceToHit = 60 - (delta + 5) * 3
        elif(-25 <= delta < -15):
            chanceToHit = 30 - (delta + 15) * 2
        elif(-35 <= delta < -25):
            chanceToHit = 10 - (delta + 25) * 0.5
        else:
            chanceToHit = 5
            accCritMod = (delta + 35) * (-2)
        return [chanceToHit, accCritMod]

    @staticmethod
    def calcMagicalHit(offense, defense):
        """Uses the game rules' magical resistance mechanics to compute
        which kind of hit this attack is.
        Inputs:
          offense -- int probably spellpower
          defense -- int probably magicResist
        Outputs:
          Any Hit type string"""
        offense *= Dice.rollFloat(0.0, 1.00)
        defense *= Dice.rollFloat(0.0, 1.00)
        if(offense * 2.5 <= defense):
            return "Fully Resisted"
        elif(offense < defense):
            return "Partially Resisted"
        elif(defense <= offense and offense <= defense * 2):
            return "Normal Hit"
        else:
            # Defense less than 1/2 offense
            return "Critical Hit"

    @staticmethod
    def calcPoisonHit(source, target, rating):
        """Uses the game rules' poison tolerance mechanics to compute whether
        this poison hit works or is ignored.
        Inputs:
          source -- attacker (Person)
          target -- victim (Person)
        Outputs:
          "Normal Hit" is the poison worked,
          "Miss" if the poison was tolerated."""
        offense = None
        defense = target.totalPoisonTolerance
        color = 'darkgreen'
        if source.team == "Players":
            offense = source.totalPoisonRatingBonus + rating
        else:
            offense = rating
            color = 'red'
        offenseAdj = offense * Dice.rollFloat(0.5, 1.0)
        defenseAdj = defense * Dice.rollFloat(0.5, 1.0)
        if(offenseAdj >= defenseAdj):
            result = "Normal Hit"
            Combat.sendCombatMessage(target.name + " was poisoned (" + `offense` + " vs " + `defense` + ")",
                                     source, color=color)
        else:
            result = "Miss"
            Combat.sendCombatMessage(target.name + " tolerated a poison attack (" + `offense` + " vs " + `defense` + ")",
                                     source, color=color)
        return result

    @staticmethod
    def physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty):
        '''Returns the appropriate hit/miss result based on game rules for physical hits.'''
        hitDuple = None
        if source.usingWeapon("Ranged"):
            # Ranged attack
            defense = target.totalDodge + target.totalRangedDodge
            offense = source.totalRangedAccuracy + modifier
            if source.inRange(target, 1) and not ignoreMeleeBowPenalty:
                # Ranged attack with penalty 20% miss chance
                outrightMissChance = int(round(20 * (1 - float(source.meleeRangedAttackPenaltyReduction) / 100)))
                if Dice.rollBeneath(outrightMissChance):
                    Combat.sendCombatMessage("Jammed (" + str(outrightMissChance) + "%)", source)
                    return "Miss"
            if source.usingWeapon("Longbow") and not source.baseClass == "Ranger" and not source.secondaryClass == "Ranger":
                # -25% Accuracy
                offense = int(round(offense * 0.75))
            elif source.usingWeapon("Shuriken") and not source.characterClass == "Ninja":
                offense = int(round(offense * 0.25))
            hitDuple = Combat.calcPhysicalHitChance(offense, defense)
        else:
            # Melee attack
            defense = target.totalDodge + target.totalMeleeDodge
            offense = source.totalMeleeAccuracy + modifier
            if source.usingWeapon("Katana") and not source.characterClass == "Ninja":
                offense = int(round(offense * 0.9))
            if source.usingWeapon("Polearm") and not source.baseClass == "Fighter":
                offense = int(round(offense * 0.7))
            hitDuple = Combat.calcPhysicalHitChance(offense, defense)
        chanceToHit = hitDuple[0]
        accuracyCritMod = hitDuple[1]
        if (Dice.rollBeneath(chanceToHit)):
            chanceToCritical = source.totalCriticalChance + accuracyCritMod + critMod
            if(Dice.rollBeneath(chanceToCritical)):
                return "Critical Hit"
            else:
                return "Normal Hit"
        else:
            return "Miss"

    @staticmethod
    def magicalHitMechanics(source, target):
        '''Returns the appropriate hit/miss result based on game rules for magical hits.'''
        offense = source.totalSpellpower
        defense = target.totalMagicResist
        result = Combat.calcMagicalHit(offense, defense)
        if source.team == "Monsters":
            Combat.sendCombatMessage("Roll: " + result + "(" + str(offense) + " vs " + str(defense) + ")",
                                    target)
        else:
            Combat.sendCombatMessage("Roll: " + result + "(" + str(offense) + " vs " + str(defense) + ")",
                                    source)
        return result

    @staticmethod
    def calcHit(source, target, type, rating=0, modifier=0, critMod=0, ignoreMeleeBowPenalty=False):
        """Determies if the attack performed from the source to the target is successful, and returns
        a HitType string to indicate this.
        Inputs:
          source -- Person performing attack
          target -- Person receiving attack
          type -- The type of attack in question; possible values:
            "Physical" (Dodge vs. Acuracy)
            "Magical"  (Magic Resist vs. Spellpower)
            "Magical-Poison"  (Poison Tolerance vs. Poison Rating after Magical roll)
            "Physical-Poison" (Poison Tolerance vs. Poison Rating after Physical roll)
            "Poison"   (Poison Tolerance vs. Poison Rating only)
            UNIMPLEMENTED:: "Trap"     (Trap Evade vs. Trap Rating)
          rating -- (optional) int indicating the poison or trap rating of the attack.
          modifier -- (optional) int indicating the +chance to hit this attack has beyond normal.
          critMod -- (optional) int indicating the additional % chance to critical this attack has.
          ignoreMeleeBowPenalty -- (optional) boolean indicating if the usual melee bow miss penalty is ignored.
        Outputs:
          A string representing the type of hit; possible values:
            "Miss" (Failed to have any effect)
            "Partially Resisted" (Only possible with magic)
            "Normal Hit" (Standard outcome for successful attacks)
            "Critical Hit" (Possible outcome for successful physical attacks and magical attacks
                            although most of the latter ignore whether the spell was a critical or not.)
          If the attack was physical, it will return a list of those strings containing either one or
          two strings, depending on whether the attacker is using one or two weapons."""
        type = type.strip().replace("-", " ")
        ### Caching for dual weilding weapons.
        if source.team == "Players":
            if source.usingWeaponStyle("Dual") and not source.lastUsedModifier:
                source.lastUsedRating = rating
                source.lastUsedCritMod = critMod
                source.lastUsedModifier = modifier
            else:
                source.lastUsedRating = None
                source.lastUsedCritMod = None
                source.lastUsedModifier = None

        if (type == "Physical"):
            Combat._shoutAttackStart(source, target)
            if Dice.rollBeneath(target.totalAvoidanceChance):
                Combat.sendCombatMessage("Avoided attack (" + str(target.totalAvoidanceChance) + "%)",
                                         target)
                return "Miss"
            if source.usingWeapon("Ranged") and \
            Dice.rollBeneath(target.totalRangedAvoidanceChance):
                Combat.sendCombatMessage("Avoided ranged attack (" + str(target.totalRangedAvoidanceChance) +
                                        "%)", target)
                return "Miss"
            attackOne = Combat.physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty)
            offenseMessage = str(source.totalMeleeAccuracy + modifier)
            if source.usingWeapon("Ranged"):
                offenseMessage = str(source.totalRangedAccuracy + modifier)
            Combat.sendCombatMessage("Rolled: " + attackOne + " (" + offenseMessage + " vs " +
                                     str(target.totalDodge) + ")", source)

            return attackOne

        if (type == "Magical"):
            result = Combat.magicalHitMechanics(source, target)
            return result

        if (type == "Magical Poison" or type == "Poison Magical"):
            if (Combat.calcPoisonHit(source, target, rating) == "Normal Hit"):
                return Combat.magicalHitMechanics(source, target)
            else:
                return "Miss"

        if (type == "Poison"):
            return Combat.calcPoisonHit(source, target, rating)

        if (type == "Trap"):
            raise NotImplementedError("This method does not yet support the Trap type.")

        raise TypeError("Unknown Attack Type: " + type + " .")

    @staticmethod
    def addStatus(target, status, duration, magnitude=0, chance=1,
                  overwrite=True, partial=False, critical=False,
                  hitValue="Normal Hit"):
        """Method is used to apply a Status to a target Person.  The properties
        needed to create and apply the status are mostly provided by default parameters
        and in most cases, they can be ignored.
        Inputs: (optional parameters indicated by a star)
          target -- Person; the target of the Status
          status -- string; the name of the status to apply
          duration -- int; the number of turns this status should last, if the status
                           is intended to last indefinitely, the duration should be
                           set to -1.
          magnitude -- int*; the power of the status.  It is not used by many statuses.
                            if it is not needed, it can be kept at its default value of
                            zero.
          chance -- float*; the chance this status will be applied at all.  It defaults
                            to 1, which indicates a 100% chance of application.  This
                            parameter was included to aid with the logic of the data files.
          overwrite -- boolean*; whether or not this Status should be overwritten by
                                 a Status of the same exact type.  It should typically be
                                 kept at its default value of True, but if it is a status
                                 that needs to 'stack', it should be False.
          partial -- boolean*; whether or not this Status will be ignored should the
                               hitValue be "Partially Resisted".  If True and the
                               hitValue is "Partially Resisted", this method will have
                               no effect.
          critical -- boolean*; whether or not this Status requires a hitValue of
                                "Critical Hit" in order to take effect.  Defaults to
                                False.
          hitValue -- hit type string*; defaults to "Normal Hit".  If the value is provided
                               and is "Miss", the method will have no effect.  Otherwise it
                               may only have varied behavior if either the critical or
                               partial booleans are set to True.
          min -- int*; some Statuses require a range of values to be supplied.  If this is
                       the case, this should be a non-negative value.
          max -- int*; some Statuses require a range of values to be supplied.  If this is
                       the case, this should be a non-negative value greater than 'min'.
          charges -- int*; some statuses have a number of charges until they expire instead of
                           a duration.  Is set to a default of zero if not time based.
        Outputs:
          None"""
        if(hitValue == "Miss" or (hitValue == "Partially Resisted" and partial == True)):
            return
        if(hitValue != "Critical Hit" and critical == True):
            return
        if(Dice.rollSuccess(100 * chance) == "Miss"):
            return

        Combat._shoutStatusApplied(target, status)

        dStatus = None
        for display in Combat.allStatuses:
            if display.name == status:
                dStatus = display
        dStatus = dStatus.cloneWithDetails(magnitude, duration)

        if dStatus.name not in [x.name for x in target.statusList]:
            target.statusList.append(dStatus)
            dStatus.activate(target)
        else:
            for display in target.statusList:
                if display.name == dStatus.name:
                    if not overwrite:
                        display.deactivate(target)
                        display.stacks += 1
                        display.activate(target)
                    else:
                        Combat.removeStatus(target, display.name, notifyClients=False)
                        target.statusList.append(dStatus)
                        dStatus.activate(target)

        comm = command.Command("PERSON", "ADDSTATUS", id=target.id, status=dStatus.name, \
                turns=dStatus.turnsLeft, image=dStatus.image, displayText=dStatus.text)
        Combat.gameServer.broadcast(comm, -comm.id)

    @staticmethod
    def removeStatus(target, statusName, notifyClients=True):
        """Removes a specific status effect from a given Person.
        Will simply do nothing if the status is not found.
        Inputs:
          target -- Person
          statusName -- the name of a status effect to remove
          notifyClients -- boolean; indicates whether we need to tell
            all of the clients that this status has been removed.  Should
            remain True unless this status is going to be reapplied
            immediately after being removed.
        Outputs:
          None"""
        matchingStatus = None
        for stat in target.statusList:
            if stat.name == statusName:
                matchingStatus = stat
                break
        if matchingStatus:
            matchingStatus.deactivate(target)
            target.statusList.remove(matchingStatus)

            if notifyClients:
                comm = command.Command("PERSON", "REMOVESTATUS", id=target.id, status=statusName)
                Combat.gameServer.broadcast(comm, -comm.id)

    @staticmethod
    def setStatusDuration(target, statusName, newDuration):
        """Applies a new duration to an existing status.
        Will do nothing if the status is not found.
        Inputs:
          target -- Person
          statusName -- the name of a status effect to change
            the duration of
          newDuration -- int > 0, the new number of turns
            for this status
        Outputs:
          None"""
        statusName = statusName.capitalize().strip()
        matchingStatus = None
        for stat in target.statusList:
            if stat.name == statusName:
                matchingStatus = target.statusList
                matchingStatus.turnsLeft = newDuration
                break

    @staticmethod
    def removeStealth(target):
        """Removes any form of stealth (other than invisibility) from
        the given Person.
        Inputs:
          target -- Person
        Outputs:
          None"""
        Combat.removeStatus(target, "Stealth")
        Combat.removeStatus(target, "Conceal")
        Combat.removeStatus(target, "Shadow Walk")
        Combat.removeStatus(target, "Sneaky Sneaky") # assassin ability

    @staticmethod
    def removeStatusOfType(target, category, removeAll=False):
        """Removes a random status from the given 'category' from the target.
        Alternatively, if 'removeAll' is set, it will remove all statuses that
        fit within the category given.
        Inputs:
          target -- Person; the character to remove status(es) from
          category -- string; a status category identifying a set of statuses
                      possible values: TODO
          removeAll -- boolean*; if set, will remove all statuses belonging to
                       the given category instead of a single random status
                       belonging to the category
        Output:
          None"""
        removalCandidates = []
        for dStatus in target.statusList:
            if category in dStatus.categoryList or category == dStatus.element:
                removalCandidates.append(dStatus)

        if removalCandidates:
            if removeAll:
                for dStatus in removalCandidates:
                    Combat.removeStatus(target, dStatus.name)
            else:
                choice = Dice.roll(0, len(removalCandidates) - 1)
                Combat.removeStatus(target, removalCandidates[choice].name)


    @staticmethod
    def instantMove(target, desiredCombatLocation):
        '''Moves a Person from one location to another instantly without animation.'''
        action = command.Command("PERSON", "MOVE", id=target.id, location=desiredCombatLocation, details=True)
        Combat.gameServer.broadcast(action, -action.id)
        target.cLocation = desiredCombatLocation

    @staticmethod
    def knockback(target, sourceOfImpact, distance, ignoreResistance=False):
        """Moves the target via 'knockback' a set number of tiles away from the source of
        impact.
        Inputs:
          target -- Person to move
          sourceOfImpact -- Location from which the knockback originated
          distance -- int number of tiles to move
          ignoreResistance -- (optional) if True, will not roll to see if the resistance of
                              the Person causes him to remain unaffected by the knockback
          """
        if not ignoreResistance and target.team == "Players" and Dice.rollBeneath(target.knockbackResistance):
            Combat.sendCombatMessage("Knockback resisted (" + `target.knockbackResistance` + ")", target)
            return

        newloc = target.cLocation.move(sourceOfImpact.direction_to(target.cLocation), distance)
        if newloc == target.cLocation:
            return

        line = target.cLocation.line_to(newloc)
        for i, loc in enumerate(line):
            if not Combat.gameServer.tile_is_open(loc, target.id) or loc.pane != (0, 0):
                line = line[:i]
                break
        newloc = line.pop() if len(line) > 0 else target.cLocation
        action = command.Command("PERSON", "MOVE", id=target.id, location=newloc, force=True)
        Combat.gameServer.SDF.queue.put((None, action))

    @staticmethod
    def decrementMovementTiles(target, removeAll=False):
        ''' Decrease the number of tiles a player can move without incurring an AP cost. '''
        if removeAll:
            target.remainingMovementTiles = 0
            Combat.sendToAll(target, "MOVE_TILES")
        elif target.remainingMovementTiles == 0:
            print "ERROR: Attempting to decrement Movement tiles when none remain!"
        else:
            target.remainingMovementTiles -= 1
            Combat.sendToAll(target, "MOVE_TILES")

    @staticmethod
    def resetMovementTiles(target, freeMove=False):
        ''' Reset the movement tiles to maximum minus this last move.
        (Used after an AP cost has been incurred.) '''
        if freeMove:
            target.remainingMovementTiles = target.totalMovementTiles
        else:
            target.remainingMovementTiles = target.totalMovementTiles - 1
        Combat.sendToAll(target, "MOVE_TILES")

    @staticmethod
    def addMovementTiles(target, tileAmount):
        ''' Add movement tiles to the current move. '''
        target.remainingMovementTiles += tileAmount
        Combat.sendToAll(target, "MOVE_TILES")

    @staticmethod
    def calcDamage(source, target, minimum, maximum, element, hitValue, partial=1, critical=1, scalesWith=None, scaleFactor=0):
        """Computes the amount of damage that should be dealt to the target after considering all bonuses and penalties
        to the attack that caused this method to be called such as source elemental damage bonuses or target vulnerabilities.
        Does not actually apply any damage to anything.
        Inputs:
          source -- Person; attacker
          target -- Person; victim
          min -- int; the minimum base damage to roll
          max -- int; the maximum base damage to roll; if less than min, will be set to min
          element -- string; the elemental type of the attack.  Possible values:
                     "Fire", "Cold", "Electric", "Poison", "Divine", "Shadow", "Arcane",
                     "Bludegoning", "Piercing", "Slashing"
          hitValue -- hitType string; Possible values:
                     "Miss", "Normal Hit", "Partially Resisted", "Critical Hit"
          partial -- (optional) float, non-negative; the amount to multiply the damage by if the attack
                     was partially resisted
          critical -- (optional) float, non-negative; the amount to multiply the damage by if the attack
                     was a critical hit
          scalesWith -- (optional) string attribute; the attribute to use if the attack scales with an attriute's value
                      possible values:
                      "Strength", "Cunning", "Spellpower"
          scaleFactor -- (optional) float, non-negative; the amount to multiply the base damage by per point of the
                         scaling attribute.  If the scaling attribute is not specified but this is given an non-zero
                         value, it will raise an IncompleteMethodCall Error.
        Outputs:
          non-negative int representing the damage that should be dealt to the target"""
        # Actual method:
        if hitValue == "Miss" or hitValue == "Fully Resisted":
            return 0

        dieRoll = Dice.roll(minimum, maximum)

        if scalesWith == "Strength":
            dieRoll *= 1 + (source.totalStrength * scaleFactor)
        elif scalesWith == "Cunning":
            dieRoll *= 1 + (source.totalCunning * scaleFactor)
        elif scalesWith == "Spellpower":
            dieRoll *= 1 + (source.totalSpellpower * scaleFactor)
        elif scalesWith is not None:
            raise TypeError("calcDamage cannot be called with scaling attribute: " + scalesWith + " .")

        if hitValue == "Critical Hit":
            dieRoll *= critical
        elif hitValue == "Partially Resisted":
            dieRoll *= partial

        if source:
            dieRoll = source.applyBonusDamage(dieRoll, element)
            # DoTs have no source.

        if element == "Fire":
            dieRoll *= 1 - (min(80, float(target.totalFireResistance) / 100))
        elif element == "Cold":
            dieRoll *= 1 - (min(80, float(target.totalColdResistance) / 100))
        elif element == "Electric":
            dieRoll *= 1 - (min(80, float(target.totalElectricResistance) / 100))
        elif element == "Poison":
            dieRoll *= 1 - (min(80, float(target.totalPoisonResistance) / 100))
        elif element == "Shadow":
            dieRoll *= 1 - (min(80, float(target.totalShadowResistance) / 100))
        elif element == "Divine":
            dieRoll *= 1 - (min(80, float(target.totalDivineResistance) / 100))
        elif element == "Arcane":
            dieRoll *= 1 - (min(80, float(target.totalArcaneResistance) / 100))
        elif element == "Bludgeoning":
            dieRoll *= 1 - (min(80, float(target.totalBludgeoningResistance) / 100))
        elif element == "Piercing":
            dieRoll *= 1 - (min(80, float(target.totalPiercingResistance) / 100))
        elif element == "Slashing":
            dieRoll *= 1 - (min(80, float(target.totalSlashingResistance) / 100))
        else:
            raise TypeError("Encountered an unknown element: " + element + " .")

        if dieRoll <= 0:
            print "0 damage dealt"
            return 0

        result = int(round(dieRoll))
        color = 'orange'
        receiver = source
        if (source and source.team == "Monsters") or (not source and target.team == "Players"):
            color = 'red'
            receiver = target
        if source:
            Combat.sendCombatMessage(source.name + " --> " + target.name + ": " + str(result) + " " +
                                    element + " damage", receiver, color)
        else:
            Combat.sendCombatMessage("DoT --> " + target.name + ": " + str(result) + " " + element +
                                    " damage", target, color)
        return result

    @staticmethod
    def basicAttack(source, target, hitType, **params):
        '''Performs an attack with a provided hitType.  If two weapons are equipped,
        this method will cal calcHit the second time.'''
        if 'noCounter' not in params:
            params['noCounter'] = False
        if source.team == "Players":
            if source.usingWeaponStyle("Dual"):
                originalCounterStatus = params['noCounter']
                params['noCounter'] = True
                Combat.weaponAttack(source, target, hitType, **params)
                params['noCounter'] = originalCounterStatus
                params['hand'] = "Left"
                modifier = source.lastUsedModifier
                critMod = source.lastUsedCritMod
                pRating = source.lastUsedRating
                hitType2 = Combat.calcHit(source, target, "Physical", modifier=modifier, critMod=critMod,
                                          rating=pRating)
                Combat.weaponAttack(source, target, hitType2, **params)
            else:
                Combat.weaponAttack(source, target, hitType, **params)
        else:
            Combat.monsterAttack(source, target, hitType, **params)

    @staticmethod
    def monsterAttack(source, target, hitType, **params):
        '''Performs a basic monster attack.'''
        Combat._shoutAttackHit(source, target, hitType)
        if hitType == "Miss":
            Combat._shoutAttackDodged(source, target)
            Combat._shoutAttackComplete(source, target, params['noCounter'])
            return
        baseAttackDamage = Dice.roll(source.attackMinDamage, source.attackMaxDamage)
        if source.attackElement == "Fire":
            baseAttackDamage *= 1 - (float(target.totalFireResistance) / 100)
        elif source.attackElement == "Cold":
            baseAttackDamage *= 1 - (float(target.totalColdResistance) / 100)
        elif source.attackElement == "Electric":
            baseAttackDamage *= 1 - (float(target.totalElectricResistance) / 100)
        elif source.attackElement == "Poison":
            baseAttackDamage *= 1 - (float(target.totalPoisonResistance) / 100)
        elif source.attackElement == "Shadow":
            baseAttackDamage *= 1 - (float(target.totalShadowResistance) / 100)
        elif source.attackElement == "Divine":
            baseAttackDamage *= 1 - (float(target.totalDivineResistance) / 100)
        elif source.attackElement == "Arcane":
            baseAttackDamage *= 1 - (float(target.totalArcaneResistance) / 100)
        baseAttackDamage = source.applyBonusDamage(baseAttackDamage, source.attackElement)
        Combat.sendCombatMessage("Incoming Attack From: " + source.name + " dealing " +
                                str(int(baseAttackDamage)) + " " + source.attackElement + " damage!",
                                color='red', character=target)
        Combat.lowerHP(target, round(baseAttackDamage))
        Combat._shoutAttackComplete(source, target, params['noCounter'])

    @staticmethod
    def weaponAttack(source, target, hitType, forceMod=1, criticalDamageMod=1, armorPenetrationMod=0,
                     elementOverride=None, noCounter=False, overallDamageMod=1, mightMod=0,
                     ignoreOnHitEffects=False, poisonRatingMod=0, backstab=False, hand="Right"):
        """Performs a weapon attack against the target from the source.  Calls actually apply the damage
        to the target, unlike 'calcDamage()'.
        Inputs: (optional values indicated by a *)
          source -- Person; attacker
          target -- Person; victim
          hitType -- string; possbile values: "Miss", "Normal Hit", "Critical Hit"
          forceMod -- float*; the amount to multiply the weapon's Force by for this attack
          criticalDamageMod -- float*; the amount to multiply the attack's critical damage by
          armorPenetrationMod -- int*; the amount of armor penetration added to this attack
          elementOverride -- string*; if this attack's native elemental types are to be ignored, this
                             field should be one of the elements.  All damage dealt by this attack will
                             be converted to that type before application.
          noCounter -- boolean*; if set, this will prevent any immediate counterattacks
          overallDamageMod -- float*; the amount to multiply the end result of this damage by.
          mightMod -- int*; the amount of bonus might applied to this attack
          ignoreOnHitEffects -- boolean*; if set, this attack will not trigger listeners waiting for
                                a weapon attack or apply any weapon's on-hit effects.
          poisonRatingMod -- int*; the amount to boost the poison rating of this attack by for any added
                                  'applied' poisons.
          backstab -- boolean*; was this attack a backstab?
          hand -- string*; which hand is attacking ("Right" or "Left")
        Outputs:
          None"""
        Combat._shoutAttackHit(source, target, hitType)

        if hitType == "Miss":
            # Enemy still counters
            Combat._shoutAttackComplete(source, target, noCounter)
            return
        # Barehands not allowed
        if hand == "Right":
            weapon = source.equippedItems.equippedWeapon
        else:
            weapon = source.equippedItems.equippedOffHand
        effectiveForce = (weapon.force + source.statusForce) * forceMod
        if source.usingWeapon("Ranged"):
            effectiveForce *= 1 + (float(source.totalRangedForce) / 100)
        effectiveMight = max(0, round(Dice.rollFloat(0.0, 1.0) * (source.totalMight + mightMod) * (float(effectiveForce) / 100)))
        effectiveDR = min(80, max(0, target.totalDR - (armorPenetrationMod + source.totalArmorPenetration)))
        outgoingDamage = ((Dice.roll(weapon.damageMin + weapon.damageMinBonus,
                                    weapon.damageMax + weapon.damageMaxBonus) +
                                    effectiveMight) *
                         (1 - (float(effectiveDR) / 100)))
        outgoingDamage *= overallDamageMod

        if hitType == "Critical Hit":
            outgoingDamage = int(round(outgoingDamage * criticalDamageMod *
                            float(weapon.criticalMultiplier + source.totalCriticalMagnitude) / 100))

        elementalEffects = []
        if not ignoreOnHitEffects:
            elementalEffects = Combat.applyOnHitEffects(source, target)

        if elementOverride:
            # Treat all damage thus far as elemental.
            elementalEffects.append([elementOverride, outgoingDamage])
            outgoingDamage = 0
        else:
            if weapon.damageType == "Bludgeoning":
                outgoingDamage *= (1 - (float(target.totalBludgeoningResistance) / 100))
            elif weapon.damageType == "Piercing":
                outgoingDamage *= (1 - (float(target.totalPiercingResistance) / 100))
            elif weapon.damageType == "Slashing":
                outgoingDamage *= (1 - (float(target.totalSlashingResistance) / 100))
            elif weapon.damageType == "Slashing & Piercing" or weapon.damageType == "Piercing & Slashing":
                resistance = min(target.totalSlashingResistance, target.totalPiercingResistance)
                outgoingDamage *= (1 - (float(resistance / 100)))
            elif weapon.damageType == "Bludgeoning & Piercing" or weapon.damageType == "Piercing & Bludgeoning":
                resistance = min(target.totalBludgeoningResistance, target.totalPiercingResistance)
                outgoingDamage *= (1 - (float(resistance / 100)))
            elif weapon.damageType == "Bludgeoning & Slashing" or wepaon.damageType == "Slashing & Bludgeoning":
                resistance = min(target.totalBludgeoningResistance, target.totalSlashingResistance)
                outgoingDamage *= (1 - (float(resistance / 100)))
        totalDamage = int(round(Combat.sumElementalEffects(elementalEffects, source, target,
                                elementOverride) + outgoingDamage))
        Combat.sendCombatMessage("Dealt " + str(totalDamage) + " total Damage.", source, color="yellow")

        Combat.lowerHP(target, totalDamage)
        if weapon.range > 1:
            source.record.recordRangedAttack()
        else:
            source.record.recordMeleeAttack()
        Combat._shoutAttackComplete(source, target, noCounter)

    @staticmethod
    def applyOnHitEffects(source, target):
        resultList = []
        for effect in source.onHitEffects:
            result = effect.apply(source, target)
            if result:
                resultList.append(result)
        return resultList

    @staticmethod
    def sumElementalEffects(elementalEffects, source, target, overrideElement=None):
        damSum = 0
        for duple in elementalEffects:
            if overrideElement:
                duple[0] = overrideElement
            if duple[0] == "Arcane":
                currentDamage = round(duple[1] * (1 + float(source.totalArcaneBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalArcaneResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Cold":
                currentDamage = round(duple[1] * (1 + float(source.totalColdBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalColdResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Divine":
                currentDamage = round(duple[1] * (1 + float(source.totalDivineBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalDivineResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Electric":
                currentDamage = round(duple[1] * (1 + float(source.totalElectricBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalElectricResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Fire":
                currentDamage = round(duple[1] * (1 + float(source.totalFireBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalFireResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Poison":
                currentDamage = round(duple[1] * (1 + float(source.totalPoisonBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalPoisonResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Shadow":
                currentDamage = round(duple[1] * (1 + float(source.totalShadowBonusDamage) / 100))
                currentDamage = round(currentDamage * (1 - float(target.totalShadowResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Piercing":
                currentDamage = duple[1]
                currentDamage = round(currentDamage * (1 - float(target.totalPiercingResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Bludgeoning":
                currentDamage = duple[1]
                currentDamage = round(currentDamage * (1 - float(target.totalBludgeoningResistance) / 100))
                damSum += currentDamage
            elif duple[0] == "Slashing":
                currentDamage = duple[1]
                currentDamage = round(currentDamage * (1 - float(target.totalSlashingResistance) / 100))
                damSum += currentDamage
        return damSum

    @staticmethod
    def setMovementCost(target, newCost, numberOfMoves=1, duration=-1):
        """Sets the AP cost of the next move of the target Person to the specified value.
        Inputs:
          target -- Person; the target whose movement cost we are adjusting
          newCost -- int; a non-negative value to assign the AP cost of movement to.
          numberOfMoves* -- int; the number of moves at this adjusted AP cost.  Once
                           expired, this method will reset the AP movement cost to its
                           default value.  If this is to be time based and not based
                           on the number of movements, this parameter should be set
                           to -1. TODO
          duration -- int*; the number of turns this AP cost should be assigned to the target.
                           By default, it is -1 which indicates it is not based on the
                           number of turns, but rather the number of movements. TODO

        Outputs:
          None"""
        target.overrideMovementAPCost = newCost
        Combat.sendToAll(target, "MoveAPCost")

    @staticmethod
    def endTurn(player):
        """Will end the turn of the given player-character.
        Inputs:
          player -- Person; the player whose turn will be ended
        Outputs:
          None"""
        Combat.decrementMovementTiles(player, removeAll=True)
        Combat.modifyResource(player, "AP", -player.AP)

    @staticmethod
    def disarmTraps(thief):
        """Disarm the traps within melee range.
        Inputs:
          thief -- Person; the thief disarming the traps
        Outputs:
          None"""
        nearbyTraps = [Combat.gameServer.pane[thief.cPane].tiles[loc.tile].getTrap() for loc in \
                Region("CIRCLE", thief.cLocation, 1) \
                if Combat.gameServer.pane[thief.cPane].tiles[loc.tile].getTrap() and
                   Combat.gameServer.pane[thief.cPane].tiles[loc.tile].getTrap().visible]
        numberTrapsDisarmed = 0
        for trap in nearbyTraps:
            chance = min(95, 55 + 5 * (thief.level - trap.level) + 2 * (thief.totalCunning + thief.trapDisarmBonus - trap.trapRating))
            if Dice.rollBeneath(chance):
                Combat.gameServer.pane[thief.cPane].removeTrap(trap.location)
                numberTrapsDisarmed += 1
                Combat.gameServer.broadcast(command.Command("TRAP", "REMOVE", location=trap.location), -thief.id)
                Combat.sendCombatMessage(trap.name + " disarmed.", thief, color='orange')
        if numberTrapsDisarmed == 0:
            Combat.sendCombatMessage("Failed to disarm any traps.", thief, color='orange', toAll=False)

    @staticmethod
    def inBackstabPosition(source, target):
        '''Returns True if this source is in an acceptable backstab position
        of the given target.'''
        # Make sure you are facing the enemy's back.
        direction = source.cLocation.direction_to(target.cLocation)
        directionValues = [direction]
        if direction == 7:
            directionValues = [4,8]
        elif direction == 1:
            directionValues = [2,4]
        elif direction == 9:
            directionValues = [6,8]
        elif direction == 3:
            directionValues = [2,6]
        return target.cLocation.direction in directionValues

    @staticmethod
    def lowerHP(target, amount):
        """Used to actually lower the amount of HP a Person has.  May kill that person.
        Will attempt to use any HP buffer first and may be interrupted by listeners.
        Inputs:
          target -- Person; the person taking damage
          amount -- the final amount to deal to the target
        Outputs:
          None"""
        if amount <= 0:
            return
        interruptCodes = Combat._shoutDamage(target, amount)
        if interruptCodes and "Ignore Damage" in interruptCodes:
            return

        remaining = amount
        while( target.HPBufferList ):
            current = target.HPBufferList[0]
            if remaining > current[1]:
                remaining -= current[1]
                target.HPBufferList.remove(current)
            elif remaining < current[1]:
                current[1] -= remaining
                Combat.sendToAll(target, "HP_BUFFER")
                return
            elif remaining == current[1]:
                target.HPBufferList.remove(current)
                Combat.sendToAll(target, "HP_BUFFER")
                return
        Combat.modifyResource(target, "HP", -remaining)


    @staticmethod
    def healTarget(source, target, amount):
        """Used to actually perform healing to the target from the source.
        Cannot 'overheal' or refill an HP buffer.
        Inputs:
          source -- Person; the person performing the healer
          target -- Person; the person receiving the healing, may be the same as the source.
          amount -- int; the amount of HP to restore
        Outputs:
          None"""
        if source.team == "Players":
            total = round(amount * (1 + float(source.healingBonus) / 100))
        else:
            total = amount
        # Listeners here?
        Combat.modifyResource(target, "HP", total)

    @staticmethod
    def applyElementalEffects(source):
        '''Returns all onhiteffects associated with the given source.'''
        ee = []
        for effect in source.onHitEffects:
            if "On Hit" in effect.categories:
                duple = effect.apply(source, target)
                if duple:
                    ee.append(duple)
        return ee

    @staticmethod
    def calcExperienceGain(player, monsterList):
        ''' Calculates the amount of experience this player should gain. '''
        expGain = 0
        for mon in monsterList:
            if player.level <= mon.level:
                expGain += mon.experience
            elif player.level <= mon.level - 2:
                expGain += int(round(mon.experience * 0.75))
            else:
                expGain += int(round(mon.experience * 0.15))
        return expGain

    # Shout methods are helpers to bundle and broadcast (shout) Broadcast objects
    # to appropriate targets.

    @staticmethod
    def _shoutAttackDodged(source, target):
        dodger = target
        bc = broadcast.DodgeBroadcast()
        bc.shout(dodger)

    @staticmethod
    def _shoutAttackStart(source, target):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        if source.team == "Monsters":
            direction = "Incoming"
            otherParty = source
            hearer = target
        attackType = "Ranged"
        if source.usingWeapon("Melee"):
            attackType = "Melee"
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)

        # Now for the monster
        if direction == "Outgoing":
            direction = "Incoming"
        else:
            direction = "Outgoing"
        if source.team == "Monsters":
            otherParty = target
            hearer = source
        else:
            otherParty = source
            hearer = target
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)

    @staticmethod
    def _shoutAttackHit(source, target, hitType):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        hitTypeString = hitType
        if hitType == "Normal Hit":
            hitTypeString = "Hit"
        if hitType == "Miss":
            hitTypeString = "Miss"
        if source.team == "Monsters":
            direction = "Incoming"
            otherParty = source
            hearer = target
        attackType = "Ranged"
        if source.usingWeapon("Melee"):
            attackType = "Melee"
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty, 'suffix' : hitTypeString}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)

        # Now for the monster
        if direction == "Outgoing":
            direction = "Incoming"
        else:
            direction = "Outgoing"
        if source.team == "Monsters":
            otherParty = target
            hearer = source
        else:
            otherParty = source
            hearer = target
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty, 'suffix' : hitTypeString}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)

    @staticmethod
    def _shoutAttackComplete(source, target, noCounter):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        if source.team == "Monsters":
            direction = "Incoming"
            otherParty = source
            hearer = target
        attackType = "Ranged"
        if source.usingWeapon("Melee"):
            attackType = "Melee"
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty, 'suffix' : 'Complete', 'noCounter' : noCounter}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)

        # Now for the monster
        if direction == "Outgoing":
            direction = "Incoming"
        else:
            direction = "Outgoing"
        if source.team == "Monsters":
            otherParty = target
            hearer = source
        else:
            otherParty = source
            hearer = target
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty, 'suffix' : 'Complete', 'noCounter' : noCounter}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)

    @staticmethod
    def _shoutDamage(target, amount):
        direction = "Incoming"
        if target.team == "Monsters":
            direction = "Outgoing"
        # This won't shout outgoing to players. TODO
        bundle = {'direction' : direction, 'amount' : amount}
        bc = broadcast.DamageBroadcast(bundle)
        return bc.shout(target)

    @staticmethod
    def _shoutStatusApplied(target, statusName):
        if target.team != "Players":
            return
        bc = broadcast.StatusBroadcast({'statusName' : statusName})
        bc.shout(target)

    @staticmethod
    def _shoutResourceLevel(target, resourceType, resourcePercent):
        if target.team != "Players":
            return
        bc = broadcast.ResourceLevelBroadcast({'resource' : resourceType, 'percent' : resourcePercent})
        bc.shout(target)

    @staticmethod
    def getAOETargets(cPane, center, radius, selectMonsters=True):
        """Gets all people in combat affected by an AOE field.
        Input:
            cPane: The overworld location of the monsterLeader that generated the combatPane
            center: A Location that is the center of the area effect
            radius: Integer value of the radius of the area
            selectMonsters: Boolean for whether targets are Monsters or Players
        Output:
            people: A list of Person objects who are inside the area"""

        R = Region("CIRCLE", center, radius)
        return Combat.getTargetsInRegion(cPane, R, selectMonsters)

    @staticmethod
    def getLineTargets(cPane, start, end, selectMonsters=True, width=1, selectFirstOnly=False):
        """Gets either the closest, or all people in combat affected by a projectile
        Input:
            cPane: The overworld location of the monsterLeader that generated the combatPane
            start: A Location from which to start drawing the line
            end: A Location at the other end of the line
            selectMonsters: Boolean for whether targets are Monsters or Players
            width: Width of the line
            selectFirstOnly: Boolean indicating return only closest target to start, or all
        Output:
            people: A list of Person objects inside the area.  A list is returned even if
                    selectFirstOnly is True"""

        R = Region("LINE", start, end, width)
        people = Combat.getTargetsInRegion(cPane, R, selectMonsters)

        if selectFirstOnly and len(people) > 0:
            minDist = start.distance(people[0].cLocation)
            index = 0
            for i, p in enumerate(people):
                dist = start.distance(p.cLocation)
                if dist < minDist:
                    minDist = dist
                    index = i
            people = [people[index]]

        return people

    @staticmethod
    def getConeTargets(cPane, center, distance, degrees, selectMonsters=True):
        """Gets all people in combat affected by a cone-shaped AOE field
        Input:
            cPane: The overworld locatino of the monsterLeader that generated the combatPane
            center: A Location that is the center or origin of the cone
                Note: Ensure that center.direction is the facing direction.  This is used
                to determine where the front, sides, and back are.
            distance: An Integer for how long the range of it
            degrees: Determines the shape of the cone
                90 -- Front and front-diagonals
                180 -- Front, front-diagonals, sides
                270 -- Front, front-diagonals, sides, back-diagonals
                For <90 degrees, use getLineTargets, for >270 degrees use getAOETargets
            selectMonsters: Boolean for whether targets are Monsters or Players
        Output:
            people: A list of Person objects inside the cone."""

        R = Region()
        if degrees == 90:
            R("ADD", "DIAMOND", center.move(center.direction, distance), distance)
            R("INT", "CIRCLE", center, distance)
        if degrees == 180:
            corners = {2: (4, 3), 4: (7, 2), 6: (8, 3), 8: (7, 6)}
            R("ADD", "SQUARE", center.move(corners[center.direction][0], distance), \
                    center.move(corners[center.direction][1], distance))
            R("INT", "CIRCLE", center, distance)
        if degrees == 270:
            R("ADD", "CIRCLE", center, distance)
            R("SUB", "DIAMOND", center.move(10 - center.direction, distance + 1), distance)

        return Combat.getTargetsInRegion(cPane, R, selectMonsters)

    @staticmethod
    def againstWall(cPane, location, direction):
        '''Method returns True if the given target has its back to an impassible
        surface.'''
        return not Combat.gameServer.pane[cPane].is_tile_passable(location.move(direction, 1))

    @staticmethod
    def getDiagonalTargets(cPane, location):
        '''Method returns all monster-targets on the corners of the given location.'''
        R = Region("CIRCLE", location, 1)
        R("SUB", "DIAMOND", location, 1)
        return Combat.getTargetsInRegion(cPane, R)

    @staticmethod
    def checkParryPosition(cPane, location, targetLoc):
        '''Method returns True if the given targetLocation is in a "Parryable"
        position according to the specs on the trait "parry", and False otherwise.'''
        R = Region("CIRCLE", location, 1)
        if targetLoc in R:
            facings = {2: [1, 2, 3], 4: [1, 4, 7], 6: [3, 6, 9], 8: [7, 8, 9]}
            if location.direction_to(targetLoc) in facings[location.direction]:
                return True
        return False

    @staticmethod
    def getTargetsInRegion(cPane, R, selectMonsters=True):
        '''Method returns a list of all targets in the region, either all players
        or monsters.  Returns an empty list if there are no such targets in the
        given region.'''
        return [Combat.gameServer.person[i] for i in Combat.gameServer.pane[cPane].person \
                if Combat.gameServer.person[i].cLocation in R and \
                Combat.gameServer.person[i].team == ("Monsters" if selectMonsters else "Players")]

    @staticmethod
    def getRandomAdjacentLocation(cPane, location):
        '''Method grabs a location adjacent to the given location randomly.
        If no location is passable in this region, it returns None.'''
        R = Region("CIRCLE", location, 1)
        return random.choice([x for x in R if x.pane == (0, 0) and \
                Combat.gameServer.tile_is_open(x, cPane=cPane)])