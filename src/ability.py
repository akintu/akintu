#!/usr/bin/python

import sys
from dice import *
import listener
from combat import *

ROOT_FOLDER = "./res/images/icons/skills/"

FIGHTER_SKILLS = ROOT_FOLDER + "fighter_skills/"
THIEF_SKILLS = ROOT_FOLDER + "thief_skills/"
RANGER_SKILLS = ROOT_FOLDER + "ranger_skills/"
WIZARD_SKILLS = ROOT_FOLDER + "wizard_skills/"

ANARCHIST_SKILLS = ROOT_FOLDER + "anarchist_skills/"
ARCANE_ARCHER_SKILLS = ROOT_FOLDER + "arcane_archer_skills/"
ASSASSIN_SKILLS = ROOT_FOLDER + "assassin_skills/"
BATTLEMAGE_SKILLS = ROOT_FOLDER + "battlemage_skills/"
BARBARIAN_SKILLS = ROOT_FOLDER + "barbarian_skills/"
DRAGOON_SKILLS = ROOT_FOLDER + "dragoon_skills/"
DRUID_SKILLS = ROOT_FOLDER + "druid_skills/"
MARKSMAN_SKILLS = ROOT_FOLDER + "marksman_skills/"
NIGHTBLADE_SKILLS = ROOT_FOLDER + "nightblade_skills/"
NINJA_SKILLS = ROOT_FOLDER + "ninja_skills/"
SHADOW_SKILLS = ROOT_FOLDER + "shadow_skills/"
SORCERER_SKILLS = ROOT_FOLDER + "sorcerer_skills/"
SPELLSWORD_SKILLS = ROOT_FOLDER + "spellsword_skills/"
TACTICIAN_SKILLS = ROOT_FOLDER + "tactician_skills/"
TRICKSTER_SKILLS = ROOT_FOLDER + "trickster_skills/"
WEAPONMASTER_SKILLS = ROOT_FOLDER + "weaponmaster_skills/"

class AbilityStub(object):
    def __init__(self, name):
        self.name = name
        info = Ability.allAbilities[name]
        self.text = 'TODO'
        self.image = './res/images/icons/cubeforce.png'
        rangeText = str(info['range'])
        if info['range'] == -1:
           rangeText = "Weapon Range"
        cooldownText = "0"
        if info['cooldown']:
            cooldownText = `info['cooldown']`
        if 'text' in info:
            self.text = 'AP: ' + `info['APCost']` + '  Cooldown: ' + cooldownText + '  Range: ' + rangeText + \
                        "\n" + info['text'] 
        if 'image' in info:
            self.image = info['image']
            

class Ability(object):

    def __init__(self, name, owner):
        self.owner = owner
        self.name = name  
        info = Ability.allAbilities[name]
        self.level = info['level']
        self.HPCost = info['HPCost']
        self.APCost = info['APCost']
        self.range = info['range']
        rangeText = str(self.range)
        if self.range == -1:
           rangeText = "Weapon Range"
        self.targetType = info['target']
        self.action = info['action']
        self.cooldown = info['cooldown']
        cooldownText = "0"
        if self.cooldown:
            cooldownText = `self.cooldown`
        self.checkFunction = info['checkFunction']
        self.breakStealth = info['breakStealth']
        if 'text' in info:
            self.text = 'AP: ' + `self.APCost` + '  Cooldown: ' + cooldownText + '  Range: ' + rangeText + \
                        "\n" + info['text'] 
        else:
            self.text = 'No description yet.'
        if 'image' in info:
            self.image = info['image']
        else:
            self.image = './res/images/icons/cubeforce.png'
        if name == "Melee Attack":
            if owner.totalMeleeAttackAPCost <= 0:
                self.APCost = 99
            else:
                self.APCost = owner.totalMeleeAttackAPCost
            self.text = 'AP: ' + `self.APCost` + "\n" + "Basic Melee Attack"
        elif name == "Ranged Attack":
            if owner.totalRangedAttackAPCost <= 0:
                self.APCost = 99
            else:
                self.APCost = owner.totalRangedAttackAPCost
            self.text = 'AP: ' + `self.APCost` + "\n" + "Basic Ranged Attack"

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
        mod = 0 # dummy code
        source = self.owner
        
        
        if source.team == "Players" and not source.equippedItems.equippedWeapon:
            return (False, "You cannot use any abilities without a weapon!!")
        
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
                    if self.breakStealth < 100:
                        Combat.sendCombatMessage(self.owner.name + " broke stealth early!", self.owner, color='white')
                    else:
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
        Combat.basicAttack(source, target, hit, forceMod=1.6, mightMod=3)

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
        hit = Combat.calcHit(source, target, "Physical", modifier=-12)
        Combat.basicAttack(source, target, hit, forceMod=0.5, overallDamageMod=0.75)

    def _quickStrikeCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")

    def _preciseBlow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=5, critMod=6)
        Combat.basicAttack(source, target, hit)

    def _preciseBlowCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")

    def _thrust(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=1)
        Combat.basicAttack(source, target, hit, elementOverride="Piercing")
       
    def _thrustCheck(self, target):
        if self.owner.usingWeapon("Sword"):
            return (True, "")
        return (False, "Must be using a sword to use " + self.name + ".")
      
    def _clobber(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-3)
        Combat.basicAttack(source, target, hit, armorPenetrationMod=10, overallDamageMod=1.1)
        if hit != "Miss" and target.size != "Huge" and target.size != "Large":
            if Dice.rollBeneath(25):
                duration = 1
                Combat.addStatus(target, "Stun", duration) 
        
    def _clobberCheck(self, target):
        if self.owner.usingWeapon("Club"):
            return (True, "")
        return (False, "Must be using a club to use " + self.name + ".")
        
    def _backstab(self, target):
        source = self.owner
        critChance = 0
        critMag = 0
        accuracy = 0
        if source.usingWeapon("Sword"):
            critChance = 30
            critMag = 1.6
            if source.usingWeaponStyle("Single"):
                accuracy = 9
        elif source.usingWeapon("Knife"):
            critChance = 50
            critMag = 2
            if source.usingWeaponStyle("Single"):
                accuracy = 5
        hit = Combat.calcHit(source, target, "Physical", modifier=accuracy, critMod=critChance)
        if hit != "Critical Hit":
            if source.usingWeaponStyle("Single"):
                Combat.basicAttack(source, target, hit, overallDamageMod=1.5)
            else:
                Combat.basicAttack(source, target, hit, overallDamageMod=1.25)
        else:
            Combat.basicAttack(source, target, hit, criticalDamageMod=critMag)

    def _backstabCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not Combat.inBackstabPosition(source, target):
            return (False, "Must be in backstab position to perform " + self.name + " .")
        if not source.usingWeapon("Sword") and not source.usingWeapon("Knife"):
            return (False, "Must be using either swords or knives to preform " + self.name + " .")
        return (True, "")


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

    def _hitAndRun(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, noCounter=True)
        direction = target.cLocation.direction_to(source.cLocation)
        choiceBase = source.cLocation
        choiceA = choiceBase.move(direction, 2)
        choiceB = choiceBase.move(direction, 1)
        if Combat.gameServer.tile_is_open(choiceA, cPane=target.cPane):
            Combat.instantMove(source, choiceA)
        elif Combat.gameServer.tile_is_open(choiceB, cPane=target.cPane):
            Combat.instantMove(source, choiceB)
        
        
    def _feint(self, target):
        source = self.owner
        chance = min(80, (source.totalCunning - target.totalCunning) * 8)
        success = Dice.rollBeneath(chance)
        if success:
            duration = 2
            Combat.addStatus(target, "Feint", duration)
            Combat.sendCombatMessage("Success! (" + str(chance) + ")", source, color="darkorange")
        else:
            Combat.sendCombatMessage("Failed. (" + str(chance) + ")", source, color="darkorange") 

    def _farSightedFocus(self, target):
        source = self.owner
        duration = 3
        Combat.addStatus(source, "Far-Sighted Focus", duration)

    def _farSightedFocusCheck(self, target):
        return (True, "")

    def _expertNotch(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=6)
        Combat.basicAttack(source, target, hit)
    
    def _expertNotchCheck(self, target):
        source = self.owner
        if not source.usingWeapon("Bow"):
            return (False, "Must be using a bow to use " + self.name)
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
        hit = Combat.calcHit(source, target, "Physical", modifier=-8)
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
        hit = Combat.calcHit(source, target, "Physical", critMod=2)
        Combat.basicAttack(source, target, hit, forceMod=1.75, mightMod=8)

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

    # Dragoon
    def _jumpAttack(self, target):
        source = self.owner
        landingZone = Combat.getRandomAdjacentLocation(target.cPane, target.cLocation)
        Combat.instantMove(source, landingZone)
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, overallDamageMod=1.75, noCounter=True)
        if hit:
            for t in Combat.getAOETargets(source.cPane, source.cLocation, radius=1, selectMonsters=True):
                Combat.basicAttack(source, t, "Normal Hit", overallDamageMod=0.25, ignoreOnHitEffects=True,
                                elementOverride="Bludgeoning", noCounter=True)
        
    def _jumpAttackCheck(self, target):
        source = self.owner
        if not source.usingWeapon("Polearm"):
            return (False, "Must have a polearm equipped to use: " + self.name)
        if Combat.getRandomAdjacentLocation(target.cPane, target.cLocation):
            return (True, "")
        return (False, "No valid landing zones exist near target; cannot use " + self.name)
    
    def _diagonalThrusts(self, target):
        source = self.owner
        targetList = Combat.getDiagonalTargets(source.cPane, source.cLocation)
        for t in targetList:
            hit = Combat.calcHit(source, t, "Physical")
            Combat.basicAttack(source, t, hitType=hit, forceMod=1.20, criticalDamageMod=1.05)
        
    def _diagonalThrustsCheck(self, target):
        source = self.owner
        if source.usingWeapon("Polearm"):
            return (True, "")
        return (False, "Must be using a polearm to use: " + self.name)
        
    def _longReach(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, noCounter=True)
        
    def _longReachCheck(self, target):
        source = self.owner
        if source.usingWeapon("Polearm"):
            return (True, "")
        return (False, "Must be using a polearm to use: " + self.name)
        
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
            
    @staticmethod
    def _martialModeDisable(dirtyHack, target, reverse=False, percent=None):
        if percent > 0.15:
            Combat.removeStatus(target, "Martial Mode")
        toRemove = None
        for x in target.listeners:
            if x.action == Ability._martialModeDisable:
                toRemove = x
        if toRemove:
            target.listeners.remove(toRemove)

    def _splashMagic(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit)
        if hit != "Miss":
            stat = None
            for status in source.statusList:
                if status.categoryList and "Weapon Enchantment" in status.categoryList:
                    stat = status
                    break
            element = stat.element
            if not element:
                element = "Arcane"
            allTargets = Combat.getAOETargets(source.cPane, target.cLocation, radius=1)
            damage = 3 + source.totalSpellpower / 3
            for tar in allTargets:
                tarDamage = Combat.calcDamage(source, target, damage, damage, element, "Normal Hit")
                Combat.lowerHP(tar, tarDamage)
    
    def _splashMagicCheck(self, target):
        source = self.owner
        if source.hasWeaponEnchant():
            return (True, "")
        return (False, "Must have a Spellsword enchantment active to use " + self.name)
            
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
        if hit != "Critical Hit":
            Combat.basicAttack(source, target, hit, overallDamageMod=1.5)
        else:
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

    def _riskyShot(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", critMod=15)
        if hit == "Critial Hit":
            duration = 5
            Combat.addStatus(target, "Riksy Shot", duration)
        Combat.basicAttack(source, target, hit)
        
    def _riskyShotCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        if not source.usingWeapon("Ranged"):
            return (False, "Must be using a Ranged weapon to perform " + self.name + " .")
        return (True, "")
        
        
    # Shadow

    def _shadowWalk(self, target):
        source = self.owner
        duration = -1
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
        if hit != "Critical Hit":
            if source.usingWeaponStyle("Single"):
                Combat.basicAttack(source, target, hit, overallDamageMod=1.5)
            else:
                Combat.basicAttack(source, target, hit, overallDamageMod=1.25)
        else:
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
        return(True, "")
        
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
        if hit != "Critical Hit":
            if source.usingWeaponStyle("Single"):
                Combat.basicAttack(source, target, hit, overallDamageMod=1.5)
            else:
                Combat.basicAttack(source, target, hit, overallDamageMod=1.25)
        else:
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
        return(True, "")
            
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
        healing = int(round(source.totalHP * 0.04))
        Combat.healTarget(source, source, healing)

    def _stealthRecoveryCheck(self, target):
        source = self.owner
        if source.inStealth():
            return (True, "")
        return (False, "Must be in stealth to use " + self.name + ".")

    # Nightblade
    
    def _shroud(self, target):
        source = self.owner
        radius = 1
        monsters = Combat.getAOETargets(source.cPane, source.cLocation, radius=radius, selectMonsters=True)
        # Get all melee targets and deal shadow damage.
        for monster in monsters:
            shadowDamage = Combat.calcDamage(source, monster, 4, 12, element="Shadow", hitValue="Normal Hit", scalesWith="Spellpower", scaleFactor=0.03)
            Combat.lowerHP(monster, shadowDamage)
        duration = 2
        Combat.addStatus(target, "Shroud", duration)
        
    def _hex(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Magical")
        if hit != "Resisted" and hit != "Fully Resisted" and hit != "Miss":
            Combat.sendCombatMessage("Hex Successful", source, color='darkorange', toAll=False)
            duration = 3
            Combat.addStatus(target, self.name, duration)
        else:
            Combat.sendCombatMessage("Hex Failed", source, color='darkorange', toAll=False)
            
    def _vampireStrike(self, target):
        source = self.owner
        mod = 0
        if source.inStealth():
            mod = 3
        hit = Combat.calcHit(source, target, "Physical", modifier=mod)
        if hit != "Miss":
            min = 1 + 2 * source.level
            max = 16 + 2 * source.level
            if source.inStealth():
                min = int(min * 1.3)
                max = int(max * 1.3)
            dam = Combat.calcDamage(source, target, min, max, element="Shadow", hitValue="Normal Hit")
            healing = dam * 2
            Combat.lowerHP(target, dam)
            Combat.healTarget(source, source, healing)  
        
    def _vampireStrikeCheck(self, target):
        source = self.owner
        if not source.usingWeapon("Melee"):
            return (False, "Must be using a melee weapon to use " + self.name)
        return (True, "")
            
    def _shadowstep(self, target):
        source = self.owner
        Combat.addMovementTiles(target, 4)

    def _shadowstepCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to use " + self.name)
        return (True, "")

    def _darkIntent(self, target):
        source = self.owner
        duration = 1
        magnitude = 3 + source.level / 2
        Combat.addStatus(source, "Dark Intent", duration, magnitude)
        
    # Battle Mage
    def _bufferStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=3)
        Combat.basicAttack(source, target, hit)
        duration = 4
        magnitude = int(round(10 + source.totalSpellpower / 15))
        if hit != "Miss":
            Combat.addStatus(source, self.name, duration, magnitude)

    def _bufferStrikeCheck(self, target):
        source = self.owner
        if source.usingWeapon("Melee"):
            return (True, "")
        else:
            return (False, self.name + " requires a melee weapon.")

    def _innerMight(self, target):
        source = self.owner
        duration = 3
        magnitude = 3 + source.totalSpellpower / 5
        Combat.addStatus(source, "Inner Might", duration, magnitude)
        newListener = listener.Listener(self, self.owner, [], Ability._innerMightDisable, ['Player MP level changed'])
        source.listeners.append(newListener)

    def _innerMightCheck(self, target):
        source = self.owner
        if source.MP >= source.totalMP * 0.75:
            return (True, "")
        else:
            return (False, "MP level must be above 75% to use: " + self.name + " .")

    @staticmethod
    def _innerMightDisable(dirtyHack, target, reverse=False, percent=None):
        if percent < 0.75:
            Combat.removeStatus(target, "Inner Might")
        toRemove = None
        for x in target.listeners:
            if x.action == Ability._innerMightDisable:
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
        Combat.modifyResource(source, "MP", 12)

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
        hit = Combat.calcHit(source, target, "Physical", modifier=-4)
        Combat.basicAttack(source, target, hit)
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
        ''' Only used when at <35% of max HP '''
        source = self.owner
        if source.HP < source.totalHP * 0.35:
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
            duration = 4
            magnitude = 4 * self.level
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
            duration = 3
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
        if hit != "Miss" and hit != "Fully Resisted" and hit != "Resisted":
            if Dice.rollBeneath(5):
                Combat.addStatus(target, "Stun", duration=2)
            duration = 3
            magnitude = 3 + source.level # Used for both spellpower and accuracy loss
            Combat.addStatus(target, "Phantom Stare", duration)
            sMin = 8 + source.level * 2
            sMax = 16 + source.level * 2
            damage = Combat.calcDamage(source, target, sMin, sMax, "Shadow", hit, partial=0.25)
            Combat.lowerHP(target, damage)

    def _poisonFang(self, target):
        ''' Lowers target's poison tolerance, might and deals poison damage if successful. '''
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
        'breakStealth' : 100,
        'image' : ROOT_FOLDER + "melee-attack.png",
        'text' : 'overriden'
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
        'breakStealth' : 100,
        'image' : ROOT_FOLDER + "ranged-attack.png",
        'text' : 'overriden'
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
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + "mighty-blow.png",
        'text' : 'Melee attack that deals bonus damage but with a penalty to accuracy.\n' + \
                'It is more powerful with larger weapons.'
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
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + "brace.png",
        'text' : "Defensive move that ends turn but grants +5% DR."
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
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + "dash.png",
        'text' : "Allows for movement at a reduced AP cost."
        },
        'Quick Strike':
        {
        'level' : 2,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : 1,
        'target' : 'hostile',
        'action' : _quickStrike,
        'cooldown' : None,
        'checkFunction' : _quickStrikeCheck,
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + "quick-strike.png",
        'text' : "Fast melee attack with -12 Accuracy, -50% force, and -25% overall damage."
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
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + "precise-blow.png",
        'text' : "Melee attack with +5 additional Accuracy and +6% Critical Hit chance"
        },
        'Thrust':
        {
        'level' : 4,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 1,
        'target' : 'hostile',
        'action' : _thrust,
        'cooldown' : 1,
        'checkFunction' : _thrustCheck,
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + "thrust.png",
        'text' : "Melee Sword attack that deals piercing damage instead of slashing.\n" + \
                "Also has +1 Accuracy."
        },
        'Clobber':
        {
        'level' : 4,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 1,
        'target' : 'hostile',
        'action' : _clobber,
        'cooldown' : None,
        'checkFunction' : _clobberCheck,
        'breakStealth' : 100,
        'image' : FIGHTER_SKILLS + 'clobber.png',
        'text' : 'Melee Club attack at -3 Accuracy.  Deals +10% Damage, has +10%\n' + \
                'Armor Penetration, and a 25% chance to stun.  Large and huge\n' + \
                'enemies are immune to the stun.'
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
        'breakStealth' : 100,
        'image' : THIEF_SKILLS + "backstab.png",
        'text' : 'Melee attack from stealth with a high critical hit chance.\n' + \
                'Must be behind the target and wielding only sword or knife type weapons.\n' + \
                'If the attack doesn\'t critical, it still deals +50% damage. (+25%\n' + \
                'if dual-wielding.)'
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
        'breakStealth' : 100,
        'image' : THIEF_SKILLS + "chain-grasp.png",
        'text' : 'Throw a chain to tangle a target, lowering its dodge, movement speed,\n' +
                    'and spell casting success.  Dependent on Cunning and cannot be used on\n' +
                    'huge foes.'
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
        'breakStealth' : 0,
        'image' : THIEF_SKILLS + "agile-position.png",
        'text' : 'Defensive move that ends turn but grants +12 to dodge.'
        },
        'Hit and Run':
        {
        'level' : 2,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 1,
        'target' : 'hostile',
        'action' : _hitAndRun,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 100,
        'image' : THIEF_SKILLS + 'hit-and-run.png',
        'text' : 'Basic melee attack followed by moving two spaces away from\n' + \
                'your target, if possible.'
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
        'breakStealth' : 100,
        'image' : THIEF_SKILLS + 'feint.png',
        'text' : 'Melee-range debuff that lowers enemy dodge rating by 10 with a success dependent on Cunning.\n' + \
                'Maximum success chance is 80%. Lasts 2 turns.'
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
        'breakStealth' : 0,
        'image' : THIEF_SKILLS + 'far-sighted-focus.png',
        'text' : 'Focus yourself to gain +5 Ranged accuracy and +7 Dodge vs ranged attacks but lower\n' + \
                'overall dodge by 2 points. Lasts 3 Turns. Does not break stealth.'
        },

        # Ranger
        # "Ranger*" abilities are given to Druid,
        # Marksman, and Tactician classes.
        'Expert Notch':
        {
        'level' : 1,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : -1,
        'target' : 'hostile',
        'action' : _expertNotch,
        'cooldown' : 1,
        'checkFunction' : _expertNotchCheck,
        'breakStealth' : 100,
        'image' : RANGER_SKILLS + 'expert-notch.png',
        'text' : 'Ranged attack with +6 Accuracy.  Must have a shortbow or longbow equipped.'
        },
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
        'breakStealth' : 0,
        'image' : RANGER_SKILLS + 'tunnel-vision.png',
        'text' : 'Increases Ranged accuracy by 10 and Might by 3 but movement tiles drop by 1.'
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
        'breakStealth' : 100,
        'image' : RANGER_SKILLS + 'balm.png',
        'text' : 'Heal 5% of your own HP.'
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
        'breakStealth' : 100,
        'image' : RANGER_SKILLS + 'rapid-reload.png',
        'text' : 'Ranged attack with a crossbow that has -8 Accuracy but a low AP cost.'
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
        'breakStealth' : 0,
        'image' : RANGER_SKILLS + 'rangers-aim.png',
        'text' : 'Improve your Accuracy by 5 and Critical hit chance by 1% for the remainder of this turn.'
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
        'breakStealth' : 0,
        'image' : WIZARD_SKILLS + 'magic-guard.png',
        'text' : 'Defensive ability that ends your turn but grants +3 Magic resist\n' + \
            'and +10% Arcane resistance.'
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
        'breakStealth' : 100,
        'image' : WIZARD_SKILLS + 'gather.png',
        'text' : 'Gather in energy from your surroundings to gain +5 spellpower, +10% Arcane and Divine damage\n' + \
            'for the remainder of your turn.'
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
        'breakStealth' : 100,
        'image' : WIZARD_SKILLS + 'reverse-hex.png',
        'text' : 'Remove one random negative status effect from an ally\n' + \
            'or from yourself. Does not affect bleeding.'
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
        'breakStealth' : 0,
        'image' : WIZARD_SKILLS + 'spell-sight.png',
        'text' : 'Gain +3 Spellpower and +5 Ranged Accuracy until your\n' + \
            'next ranged attck or spell finishes.'
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
        'breakStealth' : 100,
        'image' : BARBARIAN_SKILLS + 'berserker-rage.png',
        'text' : 'Adds 10 Might and 50% critical magnitude for 5 turns.\n' + \
                'Health must be below 75% of maximum.'
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
        'breakStealth' : 100,
        'image' : BARBARIAN_SKILLS + 'sacrificial-strike.png',
        'text' : 'Attack harms you and your foe.\n' + \
                'Has 1.75x Force, +8 Might and +2% Critical Chance.'
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
        'breakStealth' : 100,
        'image' : BARBARIAN_SKILLS + 'desperate-strike.png',
        'text' : 'Melee attack usable when below 25% HP.\n' + \
            'Has +10 Accuracy, +20% Critical Chance, 2.5x Force and\n' + \
            '+10 Armor Penetration.  Also has an occasional chance to stun\n' + \
            'the enemy for 1 turn.'
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
        'breakStealth' : 0,
        'image' : BARBARIAN_SKILLS + 'blood-of-the-ancients.png',
        'text' : 'Recover 15% of your HP but reduce your DR by 5% for 1 turn.'
        },

        # Dragoon
        'Jump Attack':
        {
        'level' : 1,
        'class' : 'Dragoon',
        'HPCost' : 0,
        'APCost' : 15,
        'range' : 8,
        'target' : 'hostile',
        'action' : _jumpAttack,
        'cooldown' : 2,
        'checkFunction' : _jumpAttackCheck,
        'breakStealth' : 100,
        'image' : DRAGOON_SKILLS + 'jump-attack.png',
        'text' : 'Jump from your current location to immediately next to a selected enemy.\n' + \
                'You will land on a random adjacent tile to the target dealing 175% damage if you hit.\n ' + \
                'Additionally, you will deal 25% of weapon damage to all targets adjacent to\n' + \
                'your landing location (including the primary target) as bludgeoning damage.'
        },
        'Faster Jump Attack':
        {
        'level' : 3,
        'class' : 'Dragoon',
        'HPCost' : 0,
        'APCost' : 14,
        'range' : 8,
        'target' : 'hostile',
        'action' : _jumpAttack,
        'cooldown' : 2,
        'checkFunction' : _jumpAttackCheck,
        'breakStealth' : 100,
        'image' : DRAGOON_SKILLS + 'jump-attack.png',
        'text' : 'Jump from your current location to immediately next to a selected enemy.\n' + \
                'You will land on a random adjacent tile to the target dealing 175% damage if you hit.\n ' + \
                'Additionally, you will deal 25% of weapon damage to all targets adjacent to\n' + \
                'your landing location (including the primary target) as bludgeoning damage.'
        },
        'Diagonal Thrusts':
        {
        'level' : 3,
        'class' : 'Dragoon',
        'HPCost' : 0,
        'APCost' : 11,
        'range' : 0,
        'target' : 'self',
        'action' : _diagonalThrusts,
        'cooldown' : None,
        'checkFunction' : _diagonalThrustsCheck,
        'breakStealth' : 100,
        'image' : DRAGOON_SKILLS + 'diagonal-thrusts.png',
        'text' : 'Strike foes in all diagonal directions.  Attack with Force x 1.20 and +5% critical magnitude\n' + \
                'on each strike.  Must have a polearm equipped.'
        },
        'Faster Jump Attack++':
        {
        'level' : 4,
        'class' : 'Dragoon',
        'HPCost' : 0,
        'APCost' : 14,
        'range' : 8,
        'target' : 'hostile',
        'action' : _jumpAttack,
        'cooldown' : 1,
        'checkFunction' : _jumpAttackCheck,
        'breakStealth' : 100,
        'image' : DRAGOON_SKILLS + 'jump-attack.png',
        'text' : 'Jump from your current location to immediately next to a selected enemy.\n' + \
                'You will land on a random adjacent tile to the target dealing 175% damage if you hit.\n ' + \
                'Additionally, you will deal 25% of weapon damage to all targets adjacent to\n' + \
                'your landing location (including the primary target) as bludgeoning damage.\n' + \
                'Now has a reduced cooldown.'
        },
        'Long Reach':
        {
        'level' : 4,
        'class' : 'Dragoon',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 2,
        'target' : 'hostile',
        'action' : _longReach,
        'cooldown' : None,
        'checkFunction' : _longReachCheck,
        'breakStealth' : 100,
        'image' : DRAGOON_SKILLS + 'long-reach.png',
        'text' : 'Melee attack with a polearm that can strike\n' + \
                'a foe from 2 tiles away and ignores counterattacks.'
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
        'breakStealth' : 0,
        'image' : SPELLSWORD_SKILLS + 'martial-mode.png',
        'text' : 'When at less than 15% MP, your fighting style returns to that of a warrior. \n' +\
                '+5 Might, +1 Melee Accuracy and +3% DR.\n' + \
                'Lasts entire battle or until MP rises above 15%.'
        },
        'Splash Magic':
        {
        'level' : 3,
        'class' : 'Spellsword',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _splashMagic,
        'cooldown' : 2,
        'checkFunction' : _splashMagicCheck,
        'breakStealth' : 100,
        'image' : SPELLSWORD_SKILLS + 'splash-magic.png',
        'text' : 'Melee Attack that blasts targets adjacent to your primary target with\n' + \
                'elemental damage according to the most recent enchantment\'s element on\n' + \
                'your weapon.  If that enchantment has no element, the element will be\n' + \
                'arcane.  Requires an enchantment on your weapon.'
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
        'cooldown' : 1,
        'checkFunction' : _shadowWalkCheck,
        'breakStealth' : 0,
        'image' : SHADOW_SKILLS + 'shadow-walk.png',
        'text' : 'Enter stealth, making enemies lose track of you until you take an action\n' + \
                'that removes stealth.  Movement cost is raised to 6 AP for the duration.\n' + \
                'Shadow Walk benefits a time and a half from Cunning, making the Shadow\n' + \
                'very hard to detect.'
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
        'breakStealth' : 100,
        'image' : THIEF_SKILLS + 'backstab.png',
        'text' : 'Melee attack from stealth with a high critical hit chance.\n' + \
                'Must be behind the target and wielding only sword or knife type weapons.\n' + \
                'Additionally, Bleeding Backstab causes the target to bleed for 5% of thier\n' + \
                'current HP per turn for the next two turns.'
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
        'breakStealth' : 100,
        'image' : SHADOW_SKILLS + 'rear-assault.png',
        'text' : 'A backstab attack performed while NOT in stealth will all benefits of a standard\n' + \
                'backstab plus bleeding.  However, it is performed at -14 Accuracy and is thus\n' + \
                'unlikely to hit.'
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
        'breakStealth' : 100,
        'image' : SHADOW_SKILLS + 'quick-with-a-crossbow.png',
        'text' : 'Ranged attack that requires a crossbow but has a low AP cost and\n' + \
                'benefits from +1 Accuracy and +1% critical chance.'
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
        'cooldown' : 1,
        'checkFunction' : _stealthRecoveryCheck,
        'breakStealth' : 0,
        'image' : SHADOW_SKILLS + 'stealth-recovery.png',
        'text' : 'Recover 4% of max HP while in stealth.  Will not break stealth.'
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
        'breakStealth' : 0,
        'image' : THIEF_SKILLS + 'stealth.png',
        'text' : 'Enter stealth, making enemies lose track of you until you take an action\n' + \
                'that removes stealth.  Movement cost is raised to 8 AP for the duration.'  
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
        'breakStealth' : 100,
        'image' : ASSASSIN_SKILLS + 'ranged-backstab.png',
        'text' : 'Perform a backstab with a ranged weapon other than the longbow.\n' + \
                'The mechanics are identical to a melee backstab performed\n' + \
                'with a single knife, however you do not need to be immediately\n' + \
                'behind the target, but you do need to be aiming at its back.'
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
        'breakStealth' : 5,
        'image' : ASSASSIN_SKILLS + 'hidden-shot.png',
        'text' : 'Attack from within stealth with only a 5% chance to break stealth.\n' + \
                'Has a +10% bonus to critical magnitude.'
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
        'breakStealth' : 100,
        'image' : ASSASSIN_SKILLS + 'visible-attack.png',
        'text' : 'Attack while NOT in stealth with +3 Acuracy.'
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
        'breakStealth' : 0,
        'image' : ASSASSIN_SKILLS + 'sneaky-sneaky.png',
        'text' : 'Use while in stealth to temporarily add 8 to your sneak, +5% to your\n' + \
                'critical hit chance and +10% to your critical magnitude.  Ends upon exiting\n' + \
                'stealth.'
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
        'breakStealth' : 2,
        'image' : ASSASSIN_SKILLS + 'cautious-shot.png',
        'text' : 'A ranged attack from stealth that has only a 2% chance to break stealth but\n' + \
                'deals only 50% damage.'
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
        'breakStealth' : 100,
        'image' : ASSASSIN_SKILLS + 'massive-shot.png',
        'text' : 'Ranged attack that requires stealth.  Attack with +2 Accuracy, Force x 1.30,\n' + \
                '+30% Damage, and +350% critical magnitude.  Lowers your sneak by 5 for the next 8 turns.'
        },
        'Risky Shot':
        {
        'level' : 5,
        'class' : 'Assassin',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : -1,
        'target' : 'hostile',
        'action' : _riskyShot,
        'cooldown' : 2,
        'checkFunction' : _riskyShotCheck,
        'breakStealth' : 20,
        'image' : ASSASSIN_SKILLS + 'risky-shot.png',
        'text' : 'Ranged attack from within stealth that has a 20% chance to break stealth but has\n' + \
                '+15% critical chance.  It it critically hits, it causes bleeding for 5% of current\n' + \
                'HP per turn and reduces enemy attack power by 5% for 5 turns.'
        },

        # Nightblade
        'Nightblade Stealth':
        {
        'level' : 1,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 0,
        'target' : 'self',
        'action' : _stealth,
        'cooldown' : 3,
        'checkFunction' : _stealthCheck,
        'breakStealth' : 0,
        'image' : THIEF_SKILLS + 'stealth.png',
        'text' : 'Enter stealth, making enemies lose track of you until you take an action\n' + \
                'that removes stealth.  Movement cost is raised to 6 AP for the duration.'  
        },
        'Shroud':
        {
        'level' : 1,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 0,
        'target' : 'self',
        'action' : _shroud,
        'cooldown' : 5,
        'checkFunction' : None,
        'breakStealth' : 100,
        'image' : NIGHTBLADE_SKILLS + 'shroud.png',
        'text' : 'Deal 4-12 +3% Shadow damage to all foes in melee range.\n' + \
                'Also activates a protective shroud for the next 2 turns that\n' + \
                'gives +20% Avoidance chance.'
        },
        'Hex':
        {
        'level' : 2,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 4,
        'target' : 'hostile',
        'action' : _hex,
        'cooldown' : 2,
        'checkFunction' : None,
        'breakStealth' : 100,
        'image' : NIGHTBLADE_SKILLS + 'hex.png',
        'text' : 'Weaken a target foe.  On a successful magical hit roll, the foe\'s\n' + \
                'Slashing resistance is lowered 25%, DR by 10% and Shadow Resistance\n' + \
                'is dropped by 25%.'
        },
        'Vampire Strike':
        {
        'level' : 3,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 1,
        'target' : 'hostile',
        'action' : _vampireStrike,
        'cooldown' : 3,
        'checkFunction' : _vampireStrikeCheck,
        'breakStealth' : 100,
        'image' : NIGHTBLADE_SKILLS + 'vampire-strike.png',
        'text' : 'Melee Attack that deals 1-16 + 2 * level shadow damage on\n' + \
                'a successful physical attack roll.  Receive double the damage\n' + \
                'dealt as healing.  Both effects +30% if used from stealth and\n' + \
                'accuracy used to hit is raised by 3.  Breaks stealth.'
        },
        'Shadowstep':
        {
        'level' : 4,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 0,
        'target' : 'self',
        'action' : _shadowstep,
        'cooldown' : 2,
        'checkFunction' : _shadowstepCheck,
        'breakStealth' : 0,
        'image' : NIGHTBLADE_SKILLS + 'shadowstep.png',
        'text' : 'Move up to 4 tiles while in stealth.'
        },
        'Dark Intent':
        {
        'level' : 5,
        'class' : 'Nightblade',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _darkIntent,
        'cooldown' : 1,
        'checkFunction' : None,
        'breakStealth' : 0,
        'image' : NIGHTBLADE_SKILLS + 'dark-intent.png',
        'text' : 'Gain +3 + 1 per 2 levels shadow damage to each\n' + \
                'attack this turn.'
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
        'breakStealth' : 100,
        'image' : BATTLEMAGE_SKILLS + 'buffer-strike.png',
        'text' : 'Melee attack with +3 Accuracy.  If successful, grants a 10 + 0.6% HP buffer for 4 turns.'
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
        'breakStealth' : 0,
        'image' : BATTLEMAGE_SKILLS + 'inner-might.png',
        'text' : 'Grants +3 Might + 6% as long as the Battle Mage retains at least 75% of his mana.\n' + \
                'Lasts 3 Turns as long as MP doesn\'t drop below 75%.'
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
        'breakStealth' : 0,
        'image' : ARCANE_ARCHER_SKILLS + 'arcane-threading.png',
        'text' : '+4 Arcane damage to all bow and crossbow attacks.\n' + \
                'Lasts until replaced by another threading.'
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
        'breakStealth' : 100,
        'image' : ARCANE_ARCHER_SKILLS + 'triple-charged-arrow.png',
        'text' : 'Ranged attack that recovers an additional 12 points of mana.'
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
        'breakStealth' : 0,
        'image' : ARCANE_ARCHER_SKILLS + 'arcane-threading.png',
        'text' : '+7 Arcane damage to all bow and crossbow attacks.\n' + \
                'Lasts until replaced by another threading.'
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
        'breakStealth' : 0,
        'image' : ARCANE_ARCHER_SKILLS + 'electric-threading.png',
        'text' : '+8 Electric damage to all bow and crossbow attacks.\n' + \
            'Lasts until replaced by another threading.'
        },

        # Trickster
        'Sidestep':
        {
        'level' : 1,
        'class' : 'Trickster',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _sidestep,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 0,
        'image' : TRICKSTER_SKILLS + 'sidestep.png',
        'text' : 'Ends turn by preparing for attacks with +3 Dodge.'
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
        'breakStealth' : 0,
        'image' : TRICKSTER_SKILLS + 'risky-focus.png',
        'text' : 'Increase your spellpower by 6 at the cost of 5 Dodge'
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
        'breakStealth' : 100,
        'image' : TRICKSTER_SKILLS + 'weary-bolt.png',
        'text' : 'A ranged attack that requires a crossbow.  On a successful\n' + \
                'hit, your target loses 5% attack power for 3 turns.  This effect\n' + \
                'may stack up to 4 times to a total of -20% attack power.'
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
        'checkFunction' : None,
        'breakStealth' : 100,
        'image' : TRICKSTER_SKILLS + 'curious-drain.png',
        'text' : 'An attack at -4 Accuracy that lowers enemy dodge by 8 and\n' + \
                'gives +8 dodge to the Trickster for 4 turns.'
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
