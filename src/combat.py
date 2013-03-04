#!/usr/bin/python

import sys
from dice import *
import broadcast
import location
import consumable
import command

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
    def getAllPorts():
        ports = []
        if not Combat.gameServer:
            print "Combat has not had its view of gameServer initialized."
        else:
            for key in Combat.gameServer.player.keys():
                ports.append(key)
        return ports

    @staticmethod
    def getAllCombatPorts(character):
        '''Get all ports in the same combat instance as this playerCharacter.'''
        return [port for port, id in Combat.gameServer.player.iteritems() \
                if Combat.gameServer.person[id].cPane == character.cPane]

    @staticmethod
    def getPlayerPort(character):
        ''' Assumes "character" is a PlayerCharacter '''
        for port in Combat.gameServer.player:
            if Combat.gameServer.player[port] == character.id:
                return port
        return None
        
    @staticmethod
    def sendToAll(character, type):
        '''Send an update of a given type to all players in the
        same combat instance as the updated player.'''
        messageObj = None
        if type == "AP":
            messageObj = command.Update(character.id, command.UpdateProperties.AP, character.AP)
        elif type == "MP":
            messageObj = command.Update(character.id, command.UpdateProperties.MP, character.MP)
        elif type == "HP":
            messageObj = command.Update(character.id, command.UpdateProperties.HP, character.HP)
        elif type == "Status":
            messageObj = command.Update(character.id, command.UpdateProperties.STATUS,
                                        Combat.encodeStatuses(character))
        for port in Combat.getAllCombatPorts(character):
            Combat.gameServer.SDF.send(port, messageObj)

    @staticmethod
    def sendCombatMessage(message, character, color="white", toAll=True):
        '''Send a message to all players in combat with the provided character.'''
        portList = []
        if not toAll:
            portList.append(Combat.getPlayerPort(character))
        else:
            portList = Combat.getAllCombatPorts(character)
        messageObj = command.Update(id=None, property=command.UpdateProperties.TEXT, 
                                    value=message, details=color)
        for port in portList:
            Combat.gameServer.SDF.send(port, messageObj)
            
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
        if(10 < delta):
            chanceToHit = 100
            accCritMod = (delta - 10) * 0.25
        elif(0 <= delta <= 10):
            chanceToHit = 90 + delta
        elif(-6 <= delta < 0):
            chanceToHit = 90 - delta * 3
        elif(-27 <= delta < -6):
            chanceToHit = 72 - (delta + 6) * 2
        elif(-47 <= delta < -27):
            chanceToHit = 30 - (delta + 27) * 1
        elif(-57 <= delta < -47):
            chanceToHit = 10 - (delta + 47) * 0.5
        else:
            chanceToHit = 5
            accCritMod = (delta + 57) * (-2)
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
        offense *= Dice.rollFloat(0.75, 1.00)
        defense *= Dice.rollFloat(0.75, 1.00)
        if(offense <= 3 * defense):
            # Spell fails Listener TODO
            return "Miss"
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
          True or False """
        offense = None
        defense = source.totalPoisonTolerance
        if source.team == "Players":
            offense = source.totalPoisonRatingBous + rating
        else:
            offense = rating
        offense *= Dice.rollFloat(0.5, 1.0)
        defense *= Dice.rollFloat(0.5, 1.0)
        if(offense >= defense):
            return True
        else:
            return False

    @staticmethod
    def physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty):
        hitDuple = None
        if source.usingWeapon("Ranged"):
            # Ranged attack
            defense = target.totalDodge + target.totalRangedDodge
            offense = source.totalRangedAccuracy + modifier
            if source.inRange(target, 1) and not ignoreMeleeBowPenalty:
                # Ranged attack with penalty 20% miss chance
                outrightMissChance = int(round(20 * (1 - float(source.meleeRangedAttackPenaltyReduction) / 100)))
                if not Dice.rollBeneath(outrightMissChance):
                    Combat.sendCombatMessage("Jammed (" + str(outrightMissChance) + "\%)", source) 
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
                Combat.sendCombatMessage("Avoided attack (" + str(target.totalAvoidanceChance) + "\%)",
                                         target)
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
            if (Combat.poisonHitMechanics(source, target, rating) == "Normal Hit"):
                return Combat.magicalHitMechanics(source, target)
            else:
                return "Miss"

        if (type == "Poison"):
            result = Combat.calcPoisonHit(source, target, rating)
            if result == "Miss":
                print "Tolerated"
            else:
                print "Poisoned"
            return result

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
                        display.deactivate(target)
                        Combat.removeStatus(target, display.name)
                        target.statusList.append(dStatus)
                        dStatus.activate(target)

        # Haven't figured out what to do with immunity: TODO

    @staticmethod
    def removeStatus(target, statusName):
        """Removes a specific status effect from a given Person.
        Will simply do nothing if the status is not found.
        Inputs:
          target -- Person
          statusName -- the name of a status effect to remove
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
            if category in dStatus.caterogyList or category == dStatus.element:
                removalCandidates.add(dStatus)

        if removalCandidates:
            if removeAll:
                for dStatus in removalCandidates:
                    Combat.removeStatus(target, dStatus.name)
            else:
                choice = Dice.roll(0, len(removalCandidates) - 1)
                Combat.removeStatus(target, removalCandidates[choice].name)


    @staticmethod
    def knockback(target, sourceOfImpact, distance, ignoreResistance=False, didHit=True):
        """Moves the target via 'knockback' a set number of tiles away from the source of
        impact.
        Inputs:
          target -- Person to move
          sourceOfImpact -- Tile from which the knockback originated
          distance -- int number of tiles to move
          ignoreResistance -- (optional) if True, will not roll to see if the resistance of
                              the Person causes him to remain unaffected by the knockback
          didHit -- (optional) boolean; used to determine if this method should do anything.
                    was included to allow simpler logic in the data files."""
        if not didHit:
            return
        pass
        # TODO

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
        if hitValue == "Miss":
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

        dieRoll = source.applyBonusDamage(dieRoll)


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

        if dieRoll < 0:
            dieRoll = 0
        return int(round(dieRoll))

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
        baseAttackDamage = source.applyBonusDamage(baseAttackDamage)
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
        # TODO: Barehands...
        if hand == "Right":
            weapon = source.equippedItems.equippedWeapon
        else:
            weapon = source.equippedItems.equippedOffHand
        effectiveForce = source.totalForce * forceMod
        if source.usingWeapon("Ranged"):
            effectiveForce *= 1 + (float(source.totalRangedForce) / 100)
        effectiveMight = round(Dice.rollFloat(0.5, 1.0) * (source.totalMight + mightMod) * (float(effectiveForce) / 100))
        effectiveDR = min(80, max(0, target.totalDR - (armorPenetrationMod + source.totalArmorPenetration)))
        outgoingDamage = (Dice.roll(weapon.damageMin + weapon.damageMinBonus,
                                    weapon.damageMax + weapon.damageMaxBonus) *
                         (1 - (float(effectiveDR) / 100)))
        outgoingDamage *= overallDamageMod

        if hitType == "Critical Hit":
            outgoingDamage += outgoingDamage * criticalDamageMod * float(weapon.criticalMultiplier) / 100

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
        totalDamage = Combat.sumElementalEffects(elementalEffects, elementOverride) + outgoingDamage

        Combat.lowerHP(target, totalDamage)
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
    def sumElementalEffects(elementalEffects, overrideElement=None):
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
        return damSum

    @staticmethod
    def setMovementCost(target, newCost, numberOfMoves=1, duration=-1, inStealth=False):
        """Sets the AP cost of the next move of the target Person to the specified value.
        By default, this will only apply to the next movement.
        Inputs:
          target -- Person; the target whose movement cost we are adjusting
          newCost -- int; a non-negative value to assign the AP cost of movement to.
          numberOfMoves* -- int; the number of moves at this adjusted AP cost.  Once
                           expired, this method will reset the AP movement cost to its
                           default value.  If this is to be time based and not based
                           on the number of movements, this parameter should be set
                           to -1.
          duration -- int*; the number of turns this AP cost should be assigned to the target.
                           By default, it is -1 which indicates it is not based on the
                           number of turns, but rather the number of movements.
          inStealth -- boolean*; If set, will cause the AP cost to reset to its default value
                                 upon exiting stealth.
        Outputs:
          None"""
        if newCost < 0:
            return
        target.overrideMovementAPCost = newCost
        target.overrideMovements = numberOfMoves
        target.overrideMovementTurns = duration
        #TODO -- trigger duration/number of moves/break on stealth??

    @staticmethod
    def movePerson(target, destination, instant=False):
        """Will move the player character from its current location to the given
        destination tile.  By default, will show the moving animation.
        Inputs:
          target -- Person; the Person to move
          destination -- Tile; the location to move the target to
          instant -- boolean*; if set, the moving animation will not be displayed
                               and the player will immediately be sent to the Tile.
        Outputs:
          None"""
        pass #TODO

    @staticmethod
    def endTurn(player):
        """Will end the turn of the given player-character.
        Inputs:
          player -- Person; the player whose turn will be ended
        Outputs:
          None"""
        pass #TODO

    @staticmethod
    def modifyThreat(source, target, threatAdjustment):
        """Alters the threat of the given source toward the target specified by
        multiplying the existing level by threatAdjustment.
        Inputs:
          source -- Person; the monster whose threat level will be modified
          target -- Person; the player to which the monster will have an adjusted
                    threat level
          threadAdjustment -- float; the amount to mulitply the threat level by
        Outputs:
          None"""
        pass #TODO

    @staticmethod
    def unsummonGuardian(target):
        """Removes the current guardian of the player from the battlefield.
        The player will not incur an HP loss.
        Inputs:
          target -- Person; owner of the guardian
        Outputs:
          None"""
        pass #TODO

    @staticmethod
    def summonGuardian(owner, name):
        """Create a Sorcerer-type Guardian on a nearby tile with the given
        name.
        Inputs:
          owner -- Person; the Sorcerer performing the summon
          name -- string; the name of the particular summon, must match an
                  actual summon's name
        Outputs:
          None"""
        pass #TODO

    @staticmethod
    def disarmTrap(thief, trap, wasSuccessful):
        """Disarm the trap specified with the thief and his allies gaining
        experience.  If wasSuccessful is False, simply return with no effect.
        Inputs:
          thief -- Person; the thief disarming the trap
          trap -- Trap; the trap being disarmed
          wasSuccessful -- boolean*; If False, will cause this method to do
                           nothing.  It was included to simplify data file
                           logic and possibly for extension later with
                           'critical failure' type penalties etc.
        Outputs:
          None"""
        if not wasSuccessful:
            return
        pass
        #TODO

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
                return
            elif remaining == current[1]:
                target.HPBufferList.remove(current)
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
        ee = []
        for effect in source.onHitEffects:
            if "On Hit" in effect.categories:
                duple = effect.apply(source, target)
                if duple:
                    ee.append(duple)
        return ee

    @staticmethod
    def useConsumable(playerChar, item):
        ''' Attempts to use a consumable.  If successful, returns True.
        If unsucessful, returns False and does nothing.'''
        if item.canUse(playerChar):
            Combat.modifyResource(playerChar, "AP", -consumable.Consumable.AP_COST)
            item.use(playerChar)
            return True
        return False

    @staticmethod
    def calcExperienceGain(player, monsterList):
        ''' Calculates the amount of experience this player should gain. '''
        expGain = 0
        for mon in monsterList:
            if player.level <= mon.level:
                expGain += mon.experienceGiven
            elif player.level <= mon.level - 2:
                expGain += round(mon.experienceGiven * 0.75)
            else:
                expGain += round(mon.experienceGiven * 0.15)
        return expGain

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

    @staticmethod
    def _shoutAttackHit(source, target, hitType):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        hitTypeString = hitType
        if hitType == "Miss":
            hitTypeString = ""
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

    @staticmethod
    def _shoutDamage(target, amount):
        direction = "Incoming"
        if target.team == "Monsters":
            direction = "Outgoing"
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


