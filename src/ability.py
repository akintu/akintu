#!/usr/bin/python

import sys
from dice import *
import listener
from combat import *


class Ability(object):

    def __init__(self, name, owner):
        self.owner = owner
        self.name = name
        info = Ability.allAbilities[name]
        self.level = info['level']
        self.HPCost = info['HPCost']
        self.APCost = info['APCost']
        self.range = info['range']
        self.targetType = info['target']
        self.action = info['action']
        self.cooldown = info['cooldown']
        self.checkFunction = info['checkFunction']
        self.breakStealth = info['breakStealth']
        if name == "Melee Attack":
            if owner.totalMeleeAttackAPCost <= 0:
                self.APCost = 99
            else:
                self.APCost = owner.totalMeleeAttackAPCost
        elif name == "Ranged Attack":
            if owner.totalRangedAttackAPCost <= 0:
                self.APCost = 99
            else:
                self.APCost = owner.totalRangedAttackAPCost

    @staticmethod
    def convertAbilityName(aName):
        firstChar = aName[0].lower()
        aName = "_" + firstChar + aName[1:]
        aName = aName.replace(" ", "")
        return aName

    def canUse(self, target):
        '''
        target: Person (later, Location?)
        '''
        # Check for modifications to ability costs here from listeners TODO
        mod = 0 # dummy code
        source = self.owner
        if source.AP < self.APCost - mod:
            return (False, "Insufficient AP")

        if self.targetType == "self" and self.owner is not target:
            target = self.owner
            
        messageCode = (True, "")
        if self.checkFunction:
            messageCode = self.checkFunction(self, target)
        if not messageCode[0]:
            return messageCode

        if self.targetType == "self" and self.owner is not target:
            return (False, "Ability is self-only, and the given target is not the user.")
        if self.targetType == "hostile" and source.team == target.team:
            return (False, "Cannot target own team with hostile ability.")
        if self.targetType == "friendly" and source.team != target.team:
            return (False, "Cannot target hostile with beneficial ability.")
        # Do we need any check for AoE spells?
        if not source.inRange(target, self.range):
            return (False, "Target is out of range.")
        if source.onCooldown(self.name):
            return (False, self.name + " is on Cooldown " + source.getCooldownTurns(self.name) +
                                       " turns left.")
        return (True, "")


    def use(self, target):
        ''' Uses the given ability on or around the given target Person (Location?)
        Performs a check if this is possible, but this is not where the canUse
        check should be made.  If caught here, it will raise an exception!'''
        if self.canUse(target)[0]:
            hpLoss = self.HPCost
            if "Percent" in str(self.HPCost):
                hpLoss = round(int(self.HPCost.split(" ")[0]) / 100.0 * self.owner.totalHP)
            Combat.modifyResource(self.owner, "HP", -hpLoss)
            Combat.modifyResource(self.owner, "AP", -self.APCost)
            if self.cooldown:
                Combat.applyCooldown(self.owner, self.name, self.cooldown)
            self.action(self, target)
            if self.owner.inStealth():
                if Dice.rollBeneath(self.breakStealth):
                    Combat.removeStealth(self.owner)
                    Combat.sendCombatMessage(self.owner.name + " exited stealth.", self.owner, color='white')
        else:
            print "WARNING: Ability failed late!"

    def _basicAttack(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit)

    def _basicMeleeAttackCheck(self, target):
        source = self.owner
        if source.usingWeapon("Melee"):
            return (True, "")
        return (False, "Must be using a melee weapon to perform: " + self.name)

    def _basicRangedAttackCheck(self, target):
        source = self.owner
        if source.usingWeapon("Ranged"):
            return (True, "")
        return (False, "Must be using a ranged weapon to perform: " + self.name)

    def _mightyBlow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-5)
        Combat.basicAttack(source, target, hit, forceMod=1.6, mightMod=2)

    def _mightyBlowCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")

    def _brace(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)
        Combat.endTurn(source)

    def _dash(self, target):
        source = self.owner
        Combat.resetMovementTiles(source, freeMove=True)

    def _quickStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-10)
        Combat.basicAttack(source, target, hit, forceMod=0.5)

    def _quickStrikeCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")

    def _preciseBlow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=4)
        Combat.basicAttack(source, target, hit)

    def _preciseBlowCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")

    def _backstab(self, target):
        source = self.owner
        critChance = 0
        critMag = 0
        accuracy = 0
        if source.usingWeapon("Sword"):
            critChance = 25
            critMag = 1.5
            if source.usingWeaponStyle("Single"):
                accuracy = 9
        elif source.usingWeapon("Knife"):
            critChance = 50
            critMag = 2
            if source.usingWeaponStyle("Single"):
                accuracy = 5
        hit = Combat.calcHit(source, target, "Physical", modifier=accuracy, critMod=critChance)
        Combat.basicAttack(source, target, hit, criticalDamageMod=critMag)

    def _backstabCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not Combat.inBackstabPosition(source, target):
            return (False, "Must be in backstab position to perform " + self.name + " .")
        if not source.usingWeapon("Sword") and not source.usingWeapon("Knife"):
            return (False, "Must be using either swords or knives to preform " + self.name + " .")


    def _chainGrasp(self, target):
        source = self.owner
        chance = min(90, (source.totalCunning - target.totalCunning) * 9)
        success = Dice.rollBeneath(chance)
        
        if success:
            Combat.sendCombatMessage("Success! (" + str(chance) + ")", source, color="darkorange")  
            duration = 3
            Combat.addStatus(target, "Chain Grasp", duration)
        else:
            Combat.sendCombatMessage("Failed. (" + str(chance) + ")", source, color="darkorange")  
            
    def _chainGraspCheck(self, target):
        if target.size == "Huge":
            return (False, self.name + " cannot be used on Huge targets.")
        return (True, "")

    def _agilePosition(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, "Agile Position", duration)
        Combat.endTurn(source)

    def _agilePositionCheck(self, target):
        return (True, "")

    def _feint(self, target):
        source = self.owner
        success = Dice.rollBeneath(min(72, (source.totalCunning - target.totalCunning) * 8))
        if success:
            duration = 2
            Combat.addStatus(target, "Feint", duration)

    def _farSightedFocus(self, target):
        source = self.owner
        duration = 3
        Combat.addStatus(source, "Far-Sighted Focus", duration)

    def _farSightedFocusCheck(self, target):
        return (True, "")

    def _tunnelVision(self, target):
        source = self.owner
        duration = 4
        Combat.addStatus(source, "Tunnel Vision", duration)

    def _tunnelVisionCheck(self, target):
        return (True, "")

    def _balm(self, target):
        source = self.owner
        Combat.healTarget(source, source, round(source.totalHP * 0.05))

    def _rapidReload(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, modifier=-8)
        Combat.basicAttack(source, target, hit)

    def _rapidReloadCheck(self, target):
        source = self.owner
        if source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a Crossbow to use " + self.name + ".")

    def _rangersAim(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, "Ranger's Aim", duration)

    def _rangersAimCheck(self, target):
        return (True, "")

    def _shrapnelTrap(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Shrapnel Trap", self.owner, target.location)

    def _stickyTrap(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Sticky Trap", self.owner, target.location)

    def _boulderPitTrap(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Boulder Pit Trap", self.owner, target.location)

    def _magicGuard(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)
        Combat.endTurn(source)

    def _gather(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)

    def _reverseHex(self, target):
        Combat.removeStatusOfType(target, "debuff")

    def _spellSight(self, target):
        source = self.owner
        duration = -1
        Combat.addStatus(source, "Spell Sight", duration)
        newListener = listener.Listener(self, self.owner, [], self._spellSightDisable, ['Outgoing Spell Cast Complete', 'Outgoing Ranged Attack Complete'])
        source.listeners.append(newListener)

    def _spellSightDisable(self, target, reverse=False, percent=None):
        Combat.removeStatus("Spell Sight")
        toRemove = None
        for x in target.listeners:
            if x.action == self._spellSightDisable:
                toRemove = x
        if toRemove:
            target.listeners.remove(toRemove)

    def _berserkerRage(self, target):
        duration = 6
        Combat.addStatus(self.owner, self.name, duration)

    def _berserkerRageCheck(self, target):
        source = self.owner
        if source.HP <= source.totalHP * 0.75:
            return (True, "")
        return (False, "Too much HP to use " + self.name)

    def _sacrificialStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", critMod=1)
        Combat.basicAttack(source, target, hit, forceMod=1.5)

    def _sacrificialStrikeCheck(self, target):
        source = self.owner
        if source.HP < source.totalHP * 0.05 + 1:
            return (False, "Insufficient HP to use " + self.name)
        if source.usingWeapon("Melee"):
            return (True, "")
        else:
            return (False, self.name + " requires a melee weapon.")

    def _desperateStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=10, critMod=20)
        Combat.basicAttack(source, target, hit, forceMod=2.5, armorPenetrationMod=10)
        doStun = Dice.rollPresetChance(source, target, "Occasional")
        Combat.addStatus(target, "Stun", duration=1, hitValue=hit, chance=doStun)

    def _desperateStrikeCheck(self, target):
        source = self.owner
        if source.HP > source.totalHP * 0.25:
            return (False, "Excess HP; cannot use " + self.name)
        if source.usingWeapon("Melee"):
            return (True, "")
        else:
            return (False, self.name + " requires a melee weapon.")

    def _bloodOfTheAncients(self, target):
        source = self.owner
        Combat.healTarget(source, source, round(source.totalHP * 0.15))
        duration = 1
        Combat.addStatus(source, "Blood of the Ancients", duration)

    def _bloodOfTheAncientsCheck(self, target):
        source = self.owner
        if source.HP < source.totalHP:
            return (True, "")
        return (False, "HP already at maximum; cannot use: " + self.name + " .")

    # Spellsword
    def _martialMode(self, target):
        source = self.owner
        duration = -1
        Combat.addStatus(target, "Martial Mode", duration)
        newListener = listener.Listener(self, self.owner, [], self._martialModeDisable, ['Player MP level changed'])
        source.listeners.append(newListener)

    def _martialModeCheck(self, target):
        source = self.owner
        if source.MP > source.totalMP * 0.15:
            return (False, "Too much MP remaining to use " + self.name)
        else:
            return (True, "")

    def _martialModeDisable(self, target, reverse=False, percent=None):
        if percent > 0.15:
            Combat.removeStatus(target, "Martial Mode")
        toRemove = None
        for x in target.listeners:
            if x.action == self._martialModeDisable:
                toRemove = x
        if toRemove:
            target.listeners.remove(toRemove)

    # Marksman
    def _cuspOfEscape(self, target):
        hitType = Combat.calcHit(source, target, "Physical", modifier=10, critMod=5)
        Combat.basicAttack(source, target, hitType)

    def _cuspOfEscapeCheck(self, target):
        source = self.owner
        if source.usingWeapon("Melee"):
            return (False, "Must be using a ranged weapon for: " + self.name)
        if source.location.distance(target.location) != source.attackRange:
            return (False, "Target must be exactly " + source.attackRange + " tiles away.")
        return (True, "")

    def _hotArrow(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Physical", modifier=-1)
        Combat.basicAttack(source, target, hitType)
        fireBase = 3
        fireDamage = Combat.calcDamage(source, target, fireBase, fireBase, "Fire", hitType)
        Combat.lowerHP(target, fireDamage)

    def _hotArrowCheck(self, target):
        source = self.owner
        if not source.usingWeapon("Bow") and not source.usingWeapon("Crossbow"):
            return (False, "Must be using a bow or crossbow to use " + self.name)
        return (True, "")

    def _hotBullet(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(sourcd, target, hitType, criticalDamageMod=1.1)
        fireBase = 8
        fireDamage = Combat.calcDamage(source, target, fireBase, fireBase, "Fire", hitType)
        Combat.lowerHP(target, fireDamage)

    def _hotBulletCheck(self, target):
        source = self.owner
        if source.usingWeapon("Sling"):
            return (True, "")
        return (False, "Must be using a sling to use " + self.name)

    def _suppressingFire(self, target):
        source = self.owner
        duration = 4
        Combat.addStatus(self, "Suppressing Fire", duration)

    # Thief

    def _stealth(self, target):
        source = self.owner
        newAPCost = 6
        if source.characterClass == "Assassin":
            newAPCost = 8
        Combat.addStatus(source, "Stealth", magnitude=newAPCost, duration=-1)

    def _stealthCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (False, "Already in Stealth")
        return (True, "")

    # Druid

    def _deepWound(self, target):
        source = self.owner
        source.statusPoisonRatingBonus += 5
        newListener = listener.Listener(self, self.owner, [], self._deepWoundDisable,
                                       ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete'])
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit)
        if hit != "Miss":
            duration = 5
            Combat.addStatus(target, "Deep Wound", duration)

    def _deepWoundDisable(self, target, reverse=False, other=None):
        self.owner.statusPoisonRatingBonus -= 5

    def _painfulShot(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, criticalDamageMod=1.1)
        if hit != "Miss" and Dice.rollPresetChance(source, target, "Occasional"):
            duration = 5
            Combat.addStatus(target, "Painful Shot", duration)

    def _painfulShotCheck(self, target):
        return (True, "")

    def _poisonousTouch(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical Poison", modifier=5, rating=12)
        if hit != "Miss":
            duration = 4
            damage = round(Dice.roll(5, 15) * (1 + source.totalCunning * 0.07))
            Combat.addStatus(target, "Poisonous Toch", duration, damage)

    def _targetThroat(self, target):
        source = self.owner
        duration = 4
        Combat.addStatus(source, "Target Throat", duration)

    def _poisonThornTrap(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Poison Thorn Trap", self.owner, target.location)

    # Tactician

    def _accuracyFavor(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Accuracy Favor", self.owner, target.location)

    def _manaFavor(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Mana Favor", self.owner, target.location)

    def _magicalDampeningTrap(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Magical Dampening Trap", self.owner, target.location)

    def _nearsightedTrap(self, target):
        pass
        # Remove Trap
        # Add trap.Trap("Nearsighted Trap", self.owner, target.location)

    # Assassin

    def _rangedBackstab(self, target):
        source = self.owner
        critChance = 40 # Incorporates -10% due to the bonus from "Anatomy"
        critMag = 2
        accuracy = 5
        hit = Combat.calcHit(source, target, "Physical", modifier=accuracy, critMod=critChance)
        Combat.basicAttack(source, target, hit, criticalDamageMod=critMag)

    def _rangedBackstabCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not Combat.inBackstabPosition(source, target):
            return (False, "Must be behind target to perform " + self.name + " .")
        if not source.usingWeapon("Ranged"):
            return (False, "Must be using a ranged weapon to perform " + self.name + " .")
        if source.usingWeapon("Longbow"):
            return (False, "Cannot use a Longbow to perform " + self.name + " .")
        return (True, "")

    def _hiddenShot(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, criticalDamageMod=1.1)

    def _hiddenShotCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not source.usingWeapon("Ranged"):
            return (False, "Must be using a ranged weapon to perform " + self.name + " .")
        return (True, "")

    def _visibleAttack(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=3)
        Combat.basicAttack(source, target, hit)

    def _visibleAttackCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (False, "Cannot be in stealth to perform " + self.name + " .")
        return (True, "")

    def _sneakySneaky(self, target):
        source = self.owner
        duration = 4
        Combat.addStatus(source, "Sneaky Sneaky", duration)

    def _sneakySneakyCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (True, "")
        return (False, "Must be in stealth to perform " + self.name + " .")

    def _cautiousShot(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, overallDamageMod=0.5)

    def _cautiousShotCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not source.usingWeapon("Ranged"):
            return (False, "Must be using a Ranged weapon to perform " + self.name + " .")
        return (True, "")

    def _massiveShot(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=2)
        Combat.basicAttack(source, target, hit, forceMod=1.3, criticalDamageMod=4.5, overallDamageMod=1.3)
        Combat.addStatus(source, "Massive Shot", duration=8)

    def _massiveShotCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not source.usingWeapon("Ranged"):
            return (False, "Must be using a Ranged weapon to perform " + self.name + " .")
        return (True, "")

    # Shadow

    def _shadowWalk(self, target):
        source = self.owner
        duration = -2
        Combat.addStatus(source, "Shadow Walk", duration)

    def _shadowWalkCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (False, "Cannot enter stealth when already in stealth.")
        return (True, "")

    def _bleedingBackstab(self, target):
        source = self.owner
        critChance = 0
        critMag = 0
        accuracy = 0
        if source.usingWeapon("Sword"):
            critChance = 25
            critMag = 1.5
            if source.usingWeaponStyle("Single"):
                accuracy = 9
        elif source.usingWeapon("Knife"):
            critChance = 50
            critMag = 2
            if source.usingWeaponStyle("Single"):
                accuracy = 5
        hit = Combat.calcHit(source, target, "Physical", modifier=accuracy, critMod=critChance)
        Combat.basicAttack(source, target, hit, criticalDamageMod=critMag)
        if hit != "Miss":
            duration = 2
            magnitude = 3
            Combat.addStatus(target, "Bleeding", duration, magnitude)

    def _bleedingBackstabCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not Combat.inBackstabPosition(source, target):
            return (False, "Must be in backstab position to perform " + self.name + " .")
        if not source.usingWeapon("Sword") and not source.usingWeapon("Knife"):
            return (False, "Must be using either swords or knives to preform " + self.name + " .")

    def _rearAssault(self, target):
        source = self.owner
        critChance = 0
        critMag = 0
        accuracy = 0
        if source.usingWeapon("Sword"):
            critChance = 25
            critMag = 1.5
            if source.usingWeaponStyle("Single"):
                accuracy = 9
        elif source.usingWeapon("Knife"):
            critChance = 50
            critMag = 2
            if source.usingWeaponStyle("Single"):
                accuracy = 5
        accuracy -= 14
        hit = Combat.calcHit(source, target, "Physical", modifier=accuracy, critMod=critChance)
        Combat.basicAttack(source, target, hit, criticalDamageMod=critMag)
        if hit != "Miss":
            duration = 2
            magnitude = 3
            Combat.addStatus(target, "Bleeding", duration, magnitude)

    def _rearAssaultCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (False, "Must not be in stealth to perform " + self.name + " .")
        if not Combat.inBackstabPosition(source, target):
            return (False, "Must be in backstab position to perform " + self.name + " .")
        if not source.usingWeapon("Sword") and not source.usingWeapon("Knife"):
            return (False, "Must be using either swords or knives to preform " + self.name + " .")

    def _quickWithACrossbow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=1, critMod=1)
        Combat.basicAttack(source, target, hit)

    def _quickWithACrossbowCheck(self, target):
        source = self.owner
        if source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a crossbow to use " + self.name)

    def _stealthRecovery(self, target):
        source = self.owner
        healing = round(source.totalHP * 0.03)
        Combat.healTarget(source, source, healing)

    def _stealthRecoveryCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (True, "")
        return (False, "Must be in stealth to use " + self.name + ".")

    # Nightblade
    def _shadowstep(self, target):
        source = self.owner
        Combat.movePerson(source, target.location, instant=True)
        # TODO: Consider replacing the ability to set AP costs?

    def _shadowstepCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to use " + self.name)
        # TODO: Check to see if the destination tile is passable.

    # Battle Mage
    def _bufferStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Phsyical", modifier=3)
        Combat.basicAttack(source, target, hit)
        duration = 4
        magnitude = round(10 + source.totalSpellpower / 15)
        Combat.addStatus(source, self.name, magnitude, hitValue=hit)

    def _bufferStrikeCheck(self, target):
        source = self.owner
        if source.usingWeapon("Melee"):
            return (True, "")
        else:
            return (False, self.name + " requires a melee weapon.")

    def _innerMight(self, target):
        source = self.owner
        duration = 2
        magnitude = 3 + source.totalSpellpower // 5
        Combat.addStatus(source, "Inner Might", duration, magnitude)
        newListener = listener.Listener(self, self.owner, [], self._innerMightDisable, ['Player MP level changed'])
        source.listeners.append(newListener)

    def _innerMightCheck(self, target):
        source = self.owner
        if source.MP >= source.totalMP * 0.75:
            return (True, "")
        else:
            return (False, "MP level must be above 75% to use: " + self.name + " .")

    def _innerMightDisable(self, target, reverse=False, percent=None):
        if percent < 0.75:
            Combat.removeStatus(target, "Inner Might")
        toRemove = None
        for x in target.listeners:
            if x.action == self._innerMightDisable:
                toRemove = x
        if toRemove:
            target.listeners.remove(toRemove)

    # Arcane Archer
    def _arcaneThreading(self, target):
        source = self.owner
        Combat.removeStatusOfType(source, "Threading")
        duration = -1
        magnitude = 4
        Combat.addStatus(source, "Arcane Threading", duration, magnitude)

    def _arcaneThreadingCheck(self, target):
        source = self.owner
        if source.usingWeapon("Bow") or source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a bow or crossbow to use: " + self.name)

    def _tripleChargedArrow(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hitType)
        source.MP += 12

    def _tripleChargedArrowCheck(self, target):
        source = self.owner
        if source.usingWeapon("Bow") or source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a bow or crossbow to use: " + self.name)

    def _improvedArcaneThreading(self, target):
        source = self.owner
        Combat.removeStatusOfType(source, "Threading")
        duration = -1
        magnitude = 7
        Combat.addStatus(source, "Arcane Threading", duration, magnitude)

    def _improvedArcaneThreadingCheck(self, target):
        source = self.owner
        if source.usingWeapon("Bow") or source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a bow or crossbow to use: " + self.name)

    def _electricThreading(self, target):
        source = self.owner
        Combat.removeStatusOfType(source, "Threading")
        duration = -1
        magnitude = 8
        Combat.addStatus(source, "Electric Threading", duration, magnitude)

    def _electricThreadingCheck(self, target):
        source = self.owner
        if source.usingWeapon("Bow") or source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a bow or crossbow to use: " + self.name)

    # Trickster

    def _sidestep(self, target):
        source = self.owner
        Combat.addStatus(source, "Sidestep", duration=1)
        Combat.endTurn(source)

    def _riskyFocus(self, target):
        source = self.owner
        Combat.addStatus(source, "Risky Focus", duration=1)

    def _wearyBolt(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit)
        if hit != "Miss":
            count = target.getStatusStackCount("Weary Bolt") + 1
            duration = 3
            magnitude = min(20, count * 5)
            Combat.addStatus(target, "Weary Bolt", duration, magnitude, overwrite=False)
            Combat.setStatusDuration(target, "Weary Bolt", duration)

    def _wearyBoltCheck(self, target):
        source = self.owner
        if source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a crossbow to perform " + self.name)

    def _curiousDrain(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, modifier=-4)
        if hit != "Miss":
            duration = 4
            Combat.addStatus(source, "Curious Drain", duration)
            Combat.addStatus(target, "Curiously Sluggish", duration)


    # Monsters

    def _draconicGuard(self, target):
        ''' Heal 10% of max HP, raise magic resist and fire resist briefly. '''
        source = self.owner
        healing = round(source.totalHP * 0.1)
        Combat.healTarget(source, source, healing)
        duration = 3
        # Fire resist magnitude set at +15%, this magnitude is for spell resist.
        magnitude = 2 * self.level
        Combat.addStatus(source, "Draconic Guard", duration, magnitude)

    def _draconicGuardCheck(self, target):
        ''' Only used when at <25% of max HP '''
        source = self.owner
        if source.HP < source.totalHP * 0.25:
            return (True, "")
        return (False, "")

    def _drawBlood(self, target):
        ''' Deal Bleeding of 9% damage per turn for 4 Turns '''
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit)
        if hit != "Miss":
            duration = 4
            percentPerTurn = 9
            Combat.addStatus(target, "Bleeding", duration, percentPerTurn)

    def _endureBeating(self, target):
        ''' Gain +20% DR for 4 turns. '''
        source = self.owner
        duration = 5 # One turn expires immediately.
        Combat.addStatus(source, "Endure Beating", duration)

    def _endureBeatingCheck(self, target):
        ''' Should only use if above 20% HP and no targets are in melee range. '''
        source = self.owner
        if source.HP < source.totalHP * 0.2:
            return (False, "")
        # if in melee range of enemies, return False TODO
        return (True, "")

    def _flamingRend(self, target):
        ''' Deal fire damage and lower target's DR. Lower accuracy than normal.'''
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-5)
        if hit != "Miss":
            dam = Combat.calcDamage(source, target, self.level * 4, self.level * 6, "Fire", "Normal Hit")
            Combat.lowerHP(target, dam)
            duration = 3
            magnitude = 3 * self.level
            Combat.addStatus(target, "Flaming Rend", duration, magnitude)

    def _frigidSlash(self, target):
        ''' Deal slashing and cold damage and lower target's movement tiles. Lower accuracy than normal.'''
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-6)
        if hit != "Miss":
            damSlash = Combat.calcDamage(source, target, 5 + self.level * 2, 5 + self.level * 3, "Slashing", "Normal Hit")
            damCold = Combat.calcDamage(source, target, self.level * 2, self.level * 3, "Cold", "Normal Hit")
            Combat.lowerHP(target, damSlash)
            Combat.lowerHP(target, damCold)
            duration = 2
            Combat.addStatus(target, "Frigid Slash", duration)

    def _howl(self, target):
        '''Lowers Might by 15 and causes 3% of spells to fail. in an area of effect,
         and deals a small amount of shadow damage.'''
        source = self.owner
        targetsList = source.getPlayersInRange(4)
        duration = 5
        baseShadowDamage = source.level * 3
        for t in targetsList:
            Combat.addStatus(t, "Howl", duration)
            dam = Combat.calcDamage(source, t, baseShadowDamage, baseShadowDamage + 4, "Shadow", "Normal Hit")
            Combat.lowerHP(t, dam)

    def _howlCheck(self, target):
        ''' Only used if there is at least one player in range without the Howl debuff.'''
        source = self.owner
        targetsList = source.getPlayersInRange(4)
        for player in targetsList:
            if not player.hasStatus("Howl"):
                return (True, "")
        return (False, "")

    def _militaryValor(self, target):
        '''Grants bonus accuracy, +15% overall damage, but lowers shadow resistance 25%'''
        source = self.owner
        duration = 5
        magnitude = self.level + 4 # Used for accuracy bonus only
        Combat.addStatus(source, "Military Valor", duration, magnitude)

    def _militaryValorCheck(self, target):
        ''' Will only be used if HP is at least 80% of maximum. '''
        source = self.owner
        if source.HP >= source.totalHP * 0.8:
            return (True, "")
        return (False, "")

    def _phantomStare(self, target):
        '''Considered a magical attack.  Deals moderate shadow damage, has a 5% chance to stun,
        and lowers spellpower and melee accuracy.'''
        source = self.owner
        hit = Combat.calcHit(source, target, "Magical")
        if hit != "Miss":
            if Dice.rollBeneath(5):
                Combat.addStatus(target, "Stun", duration=1)
            duration = 3
            magnitude = 3 + source.level # Used for both spellpower and accuracy loss
            Combat.addStatus(target, "Phantom Stare", duration)
            sMin = 8 + source.level * 2
            sMax = 16 + source.level * 2
            damage = Combat.calcDamage(source, target, sMin, sMax, "Shadow", hit, partial=0.25)
            Combat.lowerHP(target, damage)

    def _poisonFang(self, target):
        ''' Lowers target's poison tolerance and deals poison damage if successful. '''
        source = self.owner
        if Combat.calcHit(source, target, "Physical") != "Miss":
            pRating = 6 + source.level * 2
            if Combat.calcHit(source, target, "Poison", rating=pRating) != "Miss":
                tolerancePenalty = 5 + source.level
                duration = 2
                Combat.addStatus(target, "Poison Fang", duration, tolerancePenalty)
                pDamMin = 6 + source.level * 2
                pDamMax = 9 + source.level * 2
                damage = Combat.calcDamage(source, target, pDamMin, pDamMax, "Poison", "Normal Hit")
                Combat.lowerHP(target, damage)

    def _shadowBurst(self, target):
        ''' Deals a heavy amount of shadow damage to all targets in melee range (magical) '''
        source = self.owner
        # Get all AOE targets within melee range -- TODO
        # Deal heavy shadow damage to each if they fail a magical resistance check

    def _shadowBurstCheck(self, target):
        ''' Should only be used if HP < 30% of maximum OR 3+ players are in melee range '''
        source = self.owner
        return (False, "") # TODO

    def _smash(self, target):
        ''' Deal +20% damage with +15 armor penetration '''
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, armorPenetrationMod=15, overallDamageMod=1.2)

    def _stunningCut(self, target):
        ''' Deal normal damage with +2 accuracy and 10% chance to stun. '''
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=2)
        Combat.basicAttack(source, target, hit)
        if hit != "Miss" and Dice.rollBeneath(10):
            duration = 2 # 1 turn expires immediately...
            Combat.addStatus(target, "Stun", duration)

    def _toxicSpit(self, target):
        '''If a poison check is failed, target suffers reduced accuracy, 9% spell failure,
        and -20% poison resistance (elemental.) Also deals a small amount of poison damage.'''
        source = self.owner
        rating = 6 + self.level * 3
        hit = Combat.calcPoisonHit(source, target, rating)
        if hit:
            duration = 3 + source.level / 4
            magnitude = 5 + source.level # Used for accuracy debuff
            Combat.applyStatus(target, "Toxic Spit", duration, magnitude)
            pDamMin = 2 + source.level
            pDamMax = 5 + source.level
            damage = Combat.calcDamage(source, target, pDamMin, pDamMax, "Poison", "Normal Hit")
            Combat.lowerHP(target, damage)

    def _toxicSpitCheck(self, target):
        ''' Should not be used if the target already has the toxic spit debuff '''
        if target.hasStatus("Toxic Spit"):
            return (False, "")
        return (True, "")

    def _quaffPotion(self, target):
        ''' Consume a potion, healing 15-30% of all damage taken. '''
        source = self.owner
        percentToHeal = Dice.roll(15, 30)
        amountToHeal = float(percentToHeal) / 100 * source.totalHP
        Combat.healTarget(source, source, amountToHeal)

    def _quaffPotionCheck(self, target):
        ''' Monsters should only use this if they are below 65% HP '''
        source = self.owner
        if source.HP >= source.totalHP * 0.65:
            return (False, "")
        return (True, "")


    allAbilities = {

        # All
        'Melee Attack':
        {
        'level' : 1,
        'class' : 'Any',
        'HPCost' : 0,
        'APCost' : -1,
        'range' : 1,
        'target' : 'hostile',
        'action' : _basicAttack,
        'cooldown' : None,
        'checkFunction' : _basicMeleeAttackCheck,
        'breakStealth' : 100
        },
        'Ranged Attack':
        {
        'level' : 1,
        'class' : 'Any',
        'HPCost' : 0,
        'APCost' : -1,
        'range' : -1,
        'target' : 'hostile',
        'action' : _basicAttack,
        'cooldown' : None,
        'checkFunction' : _basicRangedAttackCheck,
        'breakStealth' : 100
        },

        # Fighter
        'Mighty Blow':
        {
        'level' : 1,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 1,
        'target' : 'hostile',
        'action' : _mightyBlow,
        'cooldown' : None,
        'checkFunction' : _mightyBlowCheck,
        'breakStealth' : 100
        },
        'Brace':
        {
        'level' : 1,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _brace,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Dash':
        {
        'level' : 1,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _dash,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Quick Strike':
        {
        'level' : 2,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : 1,
        'target' : 'hostile',
        'action' : _quickStrike,
        'cooldown' : None,
        'checkFunction' : _quickStrikeCheck,
        'breakStealth' : 100
        },
        'Precise Blow':
        {
        'level' : 2,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 1,
        'target' : 'hostile',
        'action' : _preciseBlow,
        'cooldown' : None,
        'checkFunction' : _preciseBlowCheck,
        'breakStealth' : 100
        },

        # Thief
        'Backstab':
        {
        'level' : 1,
        'class' : 'Thief*',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _backstab,
        'cooldown' : 2,
        'checkFunction' : _backstabCheck,
        'breakStealth' : 100
        },
        'Chain Grasp':
        {
        'level' : 1,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 6,
        'target' : 'hostile',
        'action' : _chainGrasp,
        'cooldown' : 7,
        'checkFunction' : _chainGraspCheck,
        'breakStealth' : 100
        },
        'Agile Position':
        {
        'level' : 2,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost': 5,
        'range' : 0,
        'target' : 'self',
        'action' : _agilePosition,
        'cooldown' : 5,
        'checkFunction' : _agilePositionCheck,
        'breakStealth' : 0
        },
        'Feint':
        {
        'level' : 4,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : 1,
        'target' : 'hostile',
        'action' : _feint,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Far-Sighted Focus':
        {
        'level' : 4,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 0,
        'target' : 'self',
        'action' : _farSightedFocus,
        'cooldown' : 1,
        'checkFunction' : _farSightedFocusCheck,
        'breakStealth' : 0
        },

        # Ranger
        # "Ranger*" abilities are given to Druid,
        # Marksman, and Tactician classes.
        'Shrapnel Trap':
        {
        'level' : 1,
        'class' : 'Ranger*',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'location',
        'action' : _shrapnelTrap,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Sticky Trap':
        {
        'level' : 2,
        'class' : 'Ranger*',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : 0,
        'target' : 'location',
        'action' : _stickyTrap,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Tunnel Vision':
        {
        'level' : 2,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 0,
        'target' : 'self',
        'action' : _tunnelVision,
        'cooldown' : 5,
        'checkFunction' : _tunnelVisionCheck,
        'breakStealth' : 0
        },
        'Balm':
        {
        'level' : 2,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 0,
        'target' : 'self',
        'action' : _balm,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Rapid Reload':
        {
        'level' : 2,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : -1,
        'target' : 'hostile',
        'action' : _rapidReload,
        'cooldown' : None,
        'checkFunction' : _rapidReloadCheck,
        'breakStealth' : 100
        },
        "Ranger's Aim":
        {
        'level' : 4,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _rangersAim,
        'cooldown' : 1,
        'checkFunction' : _rangersAimCheck,
        'breakStealth' : 0
        },
        'Boulder Pit Trap':
        {
        'level' : 4,
        'class' : 'Ranger*',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'self',
        'action' : _boulderPitTrap,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0
        },

        # Wizard
        'Magic Guard':
        {
        'level' : 1,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : 0,
        'target' : 'self',
        'action' : _magicGuard,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Gather':
        {
        'level' : 2,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 0,
        'target' : 'self',
        'action' : _gather,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Reverse Hex':
        {
        'level' : 2,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'friendly',
        'action' : _reverseHex,
        'cooldown' : 5,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Spell Sight':
        {
        'level' : 4,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : 0,
        'target' : 'self',
        'action' : _spellSight,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 0
        },




        # Barbarian
        'Berserker Rage':
        {
        'level' : 1,
        'class' : 'Barbarian',
        'HPCost': 0,
        'APCost' : 8,
        'range' : 0,
        'target' : 'self',
        'action' : _berserkerRage,
        'cooldown' : 5,
        'checkFunction': _berserkerRageCheck,
        'breakStealth' : 100
        },
        'Sacrificial Strike':
        {
        'level' : 2,
        'class' : 'Barbarian',
        'HPCost' : '5 Percent',
        'APCost' : 5,
        'range' : 1,
        'target' : 'hostile',
        'action' : _sacrificialStrike,
        'cooldown' : None,
        'checkFunction' : _sacrificialStrikeCheck,
        'breakStealth' : 100
        },
        'Desperate Strike':
        {
        'level' : 3,
        'class' : 'Barbarian',
        'HPCost' : 0,
        'APCost' : 12,
        'range' : 1,
        'target' : 'hostile',
        'action' : _desperateStrike,
        'cooldown' : None,
        'checkFunction' : _desperateStrikeCheck,
        'breakStealth' : 100
        },
        'Blood of the Ancients':
        {
        'level' : 4,
        'class' : 'Barbarian',
        'HPCost' : 0,
        'APCost' : 11,
        'range' : 0,
        'target' : 'self',
        'action' : _bloodOfTheAncients,
        'cooldown' : 4,
        'checkFunction' : _bloodOfTheAncientsCheck,
        'breakStealth' : 0
        },

        #Spellsword
        'Martial Mode':
        {
        'level' : 2,
        'class' : 'Spellsword',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _martialMode,
        'cooldown' : None,
        'checkFunction' : _martialModeCheck,
        'breakStealth' : 0
        },

        #Marksman
        'Cusp of Escape':
        {
        'level' : 1,
        'class' : 'Marksman',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : -1,
        'target' : 'hostile',
        'action' : _cuspOfEscape,
        'cooldown' : 1,
        'checkFunction' : _cuspOfEscapeCheck,
        'breakStealth' : 100
        },
        'Hot Arrow':
        {
        'level' : 2,
        'class' : 'Marksman',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : -1,
        'target' : 'hostile',
        'action' : _hotArrow,
        'cooldown' : 1,
        'checkFunction' : _hotArrowCheck,
        'breakStealth' : 100
        },
        'Hot Bullet':
        {
        'level' : 3,
        'class' : 'Marksman',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : -1,
        'target' : 'hostile',
        'action' : _hotBullet,
        'cooldown' : 1,
        'checkFunction' : _hotBulletCheck,
        'breakStealth' : 100
        },
        'Suppressing Fire':
        {
        'level' : 4,
        'class' : 'Marksman',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'self',
        'action' : _suppressingFire,
        'cooldown' : 4,
        'checkFunction' : None,
        'breakStealth' : 0
        },

        #Druid
        'Deep Wound':
        {
        'level' : 1,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : -1,
        'target' : 'hostile',
        'action' : _deepWound,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Painful Shot':
        {
        'level' : 1,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : -1,
        'target' : 'hostile',
        'action' : _painfulShot,
        'cooldown' : None,
        'checkFunction' : _painfulShotCheck,
        'breakStealth' : 100
        },
        'Poisonous Touch':
        {
        'level' : 2,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 1,
        'target' : 'hostile',
        'action' : _poisonousTouch,
        'cooldown' : 3,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Target Throat':
        {
        'level' : 3,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 0,
        'target' : 'self',
        'action' : _targetThroat,
        'cooldown' : 6,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Poison Thorn Trap':
        {
        'level' : 4,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'location',
        'action' : _poisonThornTrap,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0
        },

        # Tactician
        'Accuracy Favor':
        {
        'level' : 1,
        'class' : 'Tactician',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 1,
        'target' : 'location',
        'action' : _accuracyFavor,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Mana Favor':
        {
        'level' : 1,
        'class' : 'Tactician',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 1,
        'target' : 'location',
        'action' : _manaFavor,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Magical Dampening Trap':
        {
        'level' : 2,
        'class' : 'Tactician',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'location',
        'action' : _magicalDampeningTrap,
        'cooldown' : 0,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Nearsighted Trap':
        {
        'level' : 3,
        'class' : 'Tactician',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'location',
        'action' : _nearsightedTrap,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 0
        },

        # Shadow
        'Shadow Walk':
        {
        'level' : 1,
        'class' : 'Shadow',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 0,
        'target' : 'self',
        'action' : _shadowWalk,
        'cooldown' : 2,
        'checkFunction' : _shadowWalkCheck,
        'breakStealth' : 0
        },
        'Bleeding Backstab':
        {
        'level' : 2,
        'class' : 'Shadow',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _bleedingBackstab,
        'cooldown' : 2,
        'checkFunction' : _bleedingBackstabCheck,
        'breakStealth' : 100
        },
        'Rear Assault':
        {
        'level' : 3,
        'class' : 'Shadow',
        'HPCost' : 0,
        'APCost' : 9,
        'range' : 1,
        'target' : 'hostile',
        'action' : _rearAssault,
        'cooldown' : 1,
        'checkFunction' : _rearAssaultCheck,
        'breakStealth' : 100
        },
        'Quick with a Crossbow':
        {
        'level' : 3,
        'class' : 'Shadow',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : -1,
        'target' : 'hostile',
        'action' : _quickWithACrossbow,
        'cooldown' : 1,
        'checkFunction' : _quickWithACrossbowCheck,
        'breakStealth' : 100
        },
        'Stealth Recovery':
        {
        'level' : 4,
        'class' : 'Shadow',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _stealthRecovery,
        'cooldown' : 2,
        'checkFunction' : _stealthRecoveryCheck,
        'breakStealth' : 0
        },

        # Assassin
        'Assassin Stealth':
        {
        'level' : 1,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 0,
        'target' : 'self',
        'action' : _stealth,
        'cooldown' : 3,
        'checkFunction' : _stealthCheck,
        'breakStealth' : 0
        },
        'Ranged Backstab':
        {
        'level' : 1,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : -1,
        'target' : 'hostile',
        'action' : _rangedBackstab,
        'cooldown' : 2,
        'checkFunction' : _rangedBackstabCheck,
        'breakStealth' : 100
        },
        'Hidden Shot':
        {
        'level' : 1,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : -1,
        'target' : 'hostile',
        'action' : _hiddenShot,
        'cooldown' : 2,
        'checkFunction' : _hiddenShotCheck,
        'breakStealth' : 5
        },
        'Visible Attack':
        {
        'level' : 2,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : -1,
        'target' : 'hostile',
        'action' : _visibleAttack,
        'cooldown' : 2,
        'checkFunction' : _visibleAttackCheck,
        'breakStealth' : 100
        },
        'Sneaky Sneaky':
        {
        'level' : 2,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 0,
        'target' : 'self',
        'action' : _sneakySneaky,
        'cooldown' : 3,
        'checkFunction' : _sneakySneakyCheck,
        'breakStealth' : 0
        },
        'Cautious Shot' :
        {
        'level' : 2,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : -1,
        'target' : 'hostile',
        'action' : _cautiousShot,
        'cooldown' : 1,
        'checkFunction' : _cautiousShotCheck,
        'breakStealth' : 2
        },
        'Massive Shot':
        {
        'level' : 3,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 20,
        'range' : -1,
        'target' : 'hostile',
        'action' : _massiveShot,
        'cooldown' : 4,
        'checkFunction' : _massiveShotCheck,
        'breakStealth' : 100
        },

        # Nightblade
        'Shadowstep':
        {
        'level' : 4,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 4,
        'target' : 'location',
        'action' : _shadowstep,
        'cooldown' : 2,
        'checkFunction' : _shadowstepCheck,
        'breakStealth' : 0
        },

        # Battle Mage
        'Buffer Strike':
        {
        'level' : 2,
        'class' : 'Battle Mage',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _bufferStrike,
        'cooldown' : 3,
        'checkFunction' : _bufferStrikeCheck,
        'breakStealth' : 100
        },
        'Inner Might':
        {
        'level' : 4,
        'class' : 'Battle Mage',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : 0,
        'target' : 'self',
        'action' : _innerMight,
        'cooldown' : 4,
        'checkFunction' : _innerMightCheck,
        'breakStealth' : 0
        },

        # Arcane Archer
        'Arcane Threading':
        {
        'level' : 1,
        'class' : 'Arcane Archer',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _arcaneThreading,
        'cooldown' : 1,
        'checkFunction' : _arcaneThreadingCheck,
        'breakStealth' : 0
        },
        'Triple-Charged Arrow':
        {
        'level' : 3,
        'class' : 'Arcane Archer',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : -1,
        'target' : 'hostile',
        'action' : _tripleChargedArrow,
        'cooldown' : 3,
        'checkFunction' : _tripleChargedArrowCheck,
        'breakStealth' : 100
        },
        'Improved Arcane Threading':
        {
        'level' : 4,
        'class' : 'Arcane Archer',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _improvedArcaneThreading,
        'cooldown' : 1,
        'checkFunction' : _improvedArcaneThreadingCheck,
        'breakStealth' : 0
        },
        'Electric Threading':
        {
        'level' : 4,
        'class' : 'Arcane Archer',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _electricThreading,
        'cooldown' : 1,
        'checkFunction' : _electricThreadingCheck,
        'breakStealth' : 0
        },

        # Trickster
        'Sidestep':
        {
        'level' : 1,
        'class' : 'Trickster',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : 0,
        'target' : 'self',
        'action' : _sidestep,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Risky Focus':
        {
        'level' : 2,
        'class' : 'Trickster',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _riskyFocus,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Weary Bolt':
        {
        'level' : 3,
        'class' : 'Trickster',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : -1,
        'target' : 'hostile',
        'action' : _wearyBolt,
        'cooldown' : None,
        'checkFunction' : _wearyBoltCheck,
        'breakStealth' : 100
        },
        'Curious Drain':
        {
        'level' : 4,
        'class' : 'Trickster',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : -1,
        'target' : 'hostile',
        'action' : _curiousDrain,
        'cooldown' : 1,
        'checkFunction' : _curiousDrain,
        'breakStealth' : 100
        },

        # Monsters
        'Draconic Guard':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 0,
        'target' : 'self',
        'action' : _draconicGuard,
        'cooldown' : 4,
        'checkFunction' : _draconicGuardCheck,
        'breakStealth' : 100
        },
        'Draw Blood':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _drawBlood,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Endure Beating':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 12,
        'range' : 0,
        'target' : 'self',
        'action' : _endureBeating,
        'cooldown' : 5,
        'checkFunction' : _endureBeatingCheck,
        'breakStealth' : 0
        },
        'Flaming Rend' :
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 11,
        'range' : 1,
        'target' : 'hostile',
        'action' : _flamingRend,
        'cooldown' : 3,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Frigid Slash' :
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 1,
        'target' : 'hostile',
        'action' : _frigidSlash,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Howl':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 0,
        'target' : 'self',
        'action' : _howl,
        'cooldown' : 4,
        'checkFunction' : _howlCheck,
        'breakStealth' : 100
        },
        'Military Valor':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 9,
        'range' : 0,
        'target' : 'self',
        'action' : _militaryValor,
        'cooldown' : 5,
        'checkFunction' : _militaryValorCheck,
        'breakStealth' : 100
        },
        'Phantom Stare':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 2,
        'target' : 'hostile',
        'action' : _phantomStare,
        'cooldown' : 0,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Poison Fang':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 1,
        'target' : 'hostile',
        'action' : _poisonFang,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Shadow Burst':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 15,
        'range' : 0,
        'target' : 'location',
        'action' : _shadowBurst,
        'cooldown' : 3,
        'checkFunction' : _shadowBurstCheck,
        'breakStealth' : 100
        },
        'Smash':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 14,
        'range' : 1,
        'target' : 'hostile',
        'action' : _smash,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Stunning Cut':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _stunningCut,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Toxic Spit':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 3,
        'target' : 'hostile',
        'action' : _toxicSpit,
        'cooldown' : 1,
        'checkFunction' : _toxicSpitCheck,
        'breakStealth' : 100
        },
        'Quaff Potion':
        {
        'level' : 1,
        'class' : 'Monster',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 0,
        'target' : 'self',
        'action' : _quaffPotion,
        'cooldown' : 3,
        'checkFunction' : _quaffPotionCheck,
        'breakStealth' : 0
        }


    }
