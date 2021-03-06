#!/usr/bin/python

import sys
import listener
from combat import *

ROOT_FOLDER = "./res/images/icons/skills/"

ANARCHIST = ROOT_FOLDER + "anarchist_skills/"
ARCANE_ARCHER = ROOT_FOLDER + "arcane_archer_skills/"
ASSASSIN = ROOT_FOLDER + "assassin_skills/"
BATTLEMAGE = ROOT_FOLDER + "battlemage_skills/"
BARBARIAN = ROOT_FOLDER + "barbarian_skills/"
DRAGOON = ROOT_FOLDER + "dragoon_skills/"
DRUID = ROOT_FOLDER + "druid_skills/"
MARKSMAN = ROOT_FOLDER + "marksman_skills/"
NIGHTBLADE = ROOT_FOLDER + "nightblade_skills/"
NINJA = ROOT_FOLDER + "ninja_skills/"
SHADOW = ROOT_FOLDER + "shadow_skills/"
SORCERER = ROOT_FOLDER + "sorcerer_skills/"
SPELLSWORD = ROOT_FOLDER + "spellsword_skills/"
TACTICIAN = ROOT_FOLDER + "tactician_skills/"
TRICKSTER = ROOT_FOLDER + "trickster_skills/"
WEAPONMASTER = ROOT_FOLDER + "weaponmaster_skills/"

# passiveability.py
# Author: Devin Ekins -- G. Cube
#
# This module contains all Passives used by players and monsters.
# Individual methods are not typically commented as they represent 
# the functionality of individual passives -- those passives already have
# documentation on their functionality as detailed in the description
# on both the wiki and the dictionary containing the parameters of these
# functions.

class PassiveAbilityStub(object):
    def __init__(self, name):
        self.name = name
        info = None
        if name in PassiveAbility.allContentByName:
            info = PassiveAbility.allContentByName[name]
        self.image = './res/images/icons/cubeforce.png'
        self.text = 'No description yet.'
        if 'image' in info:
            self.image = info['image']
        if 'text' in info:
            self.text = info['text']

class PassiveAbility(object):

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        content = PassiveAbility.allContentByName[name]
        self.requiredClass = content['class']
        self.level = content['level']
        self.type = content['type']
        self.action = content['action']
        self.onStringList = None
        self.offStringList = None
        if 'image' in content:
            self.image = content['image']
        else:
            self.image = './res/images/icons/cubeforce.png'
        if 'text' in content:
            self.text = content['text']
        else:
            self.text = 'No description yet.'
        if self.type == 'dynamic':
            self.onStringList = content['onStringList']
            self.offStringList = content['offStringList']
            self.registerListener()
        if self.type == 'static':
            if self.action:
                self.action(self, self.owner)

    def registerListener(self):
        newListener = listener.Listener(self, self.owner, self.onStringList, self.action, self.offStringList)
        self.owner.listeners.append(newListener)

    # Barbarian
    def applyColdEndurance(self, target):
        target.baseColdResistance += 10

    def applyMagicalVulnerability(self, target):
        target.baseMagicResist -= 3

    def applyMightyWeapon(self, target, reverse=False, other=None):
        if not reverse:
            if target.usingWeaponStyle("Two-Handed"):
                target.baseMight += 6
        else:
            if target.usingWeaponStyle("Two-Handed"):
                target.baseMight -= 6

    def applyTwoWeaponTargeting(self, target, reverse=False, other=None):
        if not reverse:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy += 3
        else:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy -= 3

    def applyBloodOnTheEdge(self, target, reverse=False, damage=0):
        # No reverse possible.
        hpThreshold = round(target.totalHP * 0.30)
        if target.HP > hpThreshold:
            return
        hpThreshold = round(target.totalHP * 0.05)
        if damage > hpThreshold:
            return
        return "Ignore Damage"

    def applyMagicalIgnorance(self, target):
        target.baseMagicResist -= 3

    def applyStunningRecovery(self, target, reverse=False, statusName=None):
        if statusName == "Stun" and not target.hasStatus("Stunning Recovery"):
            healing = round(target.totalHP * 0.10)
            Combat.healTarget(target, target, healing)
            Combat.addStatus(target, "Stunning Recovery", duration=1)

    def applyWalkItOff(self, target, reverse=False, other=None):
        source = self.owner
        if source.record._previousTurnTilesMoved > 0:
            Combat.healTarget(source, source, int(source.totalHP * 0.01))

    # Dragoon

    def applyOblivious(self, target):
        target.baseIntuition -= 12
        target.baseAwareness -= 5

    def applyPolearmSpecialization(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeapon("Polearm"):
                source.statusForce += 30
                source.statusCriticalChance += 5
        else:
            if source.usingWeapon("Polearm"):
                source.statusForce -= 30
                source.statusCriticalChance -= 5

    def applyDragonFoe(self, target, reverse=False, other=None):
        source = self.owner
        if other.team != "Monsters":
            return
        if not reverse:
            if other.type == "Dragonkin":
                source.statusMeleeAccuracy += 2
                source.statusRangedAccuracy += 2
                source.statusDodge += 2
        else:
            if other.type == "Dragonkin":
                source.statusMeleeAccuracy -= 2
                source.statusRangedAccuracy -= 2
                source.statusDodge -= 2

    def applyFireTouched(self, target):
        target.baseFireResistance += 10

    def applyJumpAttackUpgrade(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Jump Attack":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)

    def applyJumpAttackUpgrade2(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Faster Jump Attack":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)

    def applyJumpAttackUpgrade3(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Faster Jump Attack++":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)

    # Weapon Master
    def applyShieldEfficiency(self, target, reverse=False, other=None):
        source = self.owner
        if source.usingShield():
            Combat.modifyResource(source, "AP", 1)

    def applyDirectCounterattack(self, target, reverse=False, other=None):
        source = self.owner
        # TODO: STUB
        pass
        
    def applyShieldCounter(self, target, reverse=False, other=None):
        source = self.owner
        # Stack an additional 50% bludgeoning damage onto the counterattack.
        # TODO: STUB
        pass
        
    def applyTwoHandedParry(self, target, reverse=False, other=None):
        source = self.owner
        # TODO: Make this only apply to angles that you can counterattack from.
        if not source.usingWeaponStyle("Two Handed"):
            return
        if not reverse:
            source.statusDodge += 4
        else:
            source.statusDodge -= 4
            
    def applyHoldTheLine(self, target, reverse=False, percent=None):
        if not reverse:
            if not target.hasStatus("Hold the Line") and percent < 0.30:
                Combat.addStatus(target, "Hold the Line", -1)
        else:
            if target.hasStatus("Hold the Line") and percent >= 0.30:
                Combat.removeStatus(target, "Hold the Line")
            
    def applyDirectCounterattack2(self, target, reverse=False, other=None):
        source = self.owner
        # TODO: STUB
        pass
    
    def applyDirectCounterattackUpgrade(self, target):    
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Direct Counterattack":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)
            
    def applyTwoWeaponGlancing(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeaponStyle("Dual"):
                source.statusDR += 2
        else:
            if source.usingWeaponStyle("Dual"):
                source.statusDR -= 2
    
    def applyRapidBandaging(self, target, reverse=False,  statusName=None):
        # An odd mechanism to find out if the most recently applied status
        # was a bleeding status...
        status = target.getMostRecentStatus("Bleeding")
        if status.name == statusName and Dice.rollSuccess(50):
            Combat.removeStatus(target, statusName)
    
    # Spellsword
    def applySeekerOfEnchantments(self, target, reverse=False, spell=None):
        if not reverse:
            if spell.school == "Enchantment":
                target.statusSpellpower += 6
        else:
            if spell.school == "Enchantment":
                target.statusSpellpower -= 6

    def applyDuality(self, target):
        target.baseDR += 2
        target.baseMagicResist += 1

    def applyLastingEnchantment(self, target, reverse=False, spell=None):
        if spell.school == "Enchantment":
            for buff in [x for x in target.statusList if x.name == spell.name or
                         x.name == "Weapon Enhance Striking" or
                         x.name == "Weapon Enhance Punishing" or
                         x.name == "Weapon Enhance Precision"]:
                buff.turnsLeft += 1
        # Has no reverse.

    def applyKeenEnchantment(self, target, reverse=False, other=None):
        if not target.usingWeaponStyle("Two Handed") or not target.hasWeaponEnchant():
            return
        if not reverse:
            target.statusCriticalChance += 8
        else:
            target.statusCriticalChance -= 8

    def applyFocalPoint(self, target, reverse=False, other=None):
        if not target.usingWeaponStyle("Two Handed") or not target.hasWeaponEnchant():
            return
        holyDamage = (int(15 * (1 + target.totalDivineBonusDamage * 0.01) *
                                 (1 - other.totalDivineResistance * 0.01)))
        Combat.lowerHP(other, holyDamage)
        Combat.sendCombatMessage(target.name + " --> " + other.name + ": " + `holyDamage` + " " +
                                "Holy" + " damage", target, 'yellow')

    def applyBladesOfReduction(self, target, reverse=False, other=None):
        if not target.usingWeapon("Sword") and not target.usingWeapon("Axe"):
            return
        doApply = Dice.rollPresetChance(target, other, "Reliable")
        if doApply:
            duration = -1 # Never ends
            Combat.addStatus(other, "Blades of Reduction", duration)

    # Anarchist
    def applyHateCraft(self, target):
        target.bonusTrapDamage += 20

    def applyShockAndBurn(self, target):
        target.baseFireBonusDamage += 5
        target.baseElectricBonusDamage += 5
        target.baseElectricResistance += 10
        target.baseArmorPenetration += 2

    def applyRushedDelivery(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.record._currentTurnTilesMoved >= 3:
                source.bonusTrapDamage += 50
                source.bonusTrapRating += 2
        else:
            if source.record._currentTurnTilesMoved >= 3:
                source.bonusTrapDamage -= 50
                source.bonusTrapRating -= 2

    # Marksman
    def applyExcellentVision(self, target):
        target._bonusRange += 2
        target.baseAwareness += 2

    def applyLayingInWait(self, target, reverse=False, other=False):
        source = self.owner
        if not reverse:
            if source.record._previousTurnTilesMoved == 0:
                mag = 4
                Combat.addStatus(source, "Laying in Wait", duration=-1, magnitude=mag)
        else:
            Combat.removeStatus(source, "Laying in Wait")

    def applyFireHandler(self, target):
        target.baseFireResistance += 5
        target.baseFireBonusDamage += 5

    def applyCamouflage(self, target):
        target.baseSneak += 8
        target.baseDodge += 2
        target.baseRangedAccuracy += 2

    def applyShortbowNiche(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeapon("Shortbow"):
                source.statusCriticalMagnitude += 10
                source.statusCriticalChance += 5
        else:
            if source.usingWeapon("Shortbow"):
                source.statusCriticalMagnitude -= 10
                source.statusCriticalChance -= 5

    def applyIncredibleFocus(self, target, reverse=False, statusName=None):
        source = self.owner
        if statusName == "Stun" and Dice.rollBeneath(75):
            Combat.removeStatus(source, statusName)

    def applySuperiorTraining(self, target, reverse=False, other=None):
        source = self.owner
        duration = 2 # Decremented almost immediately.
        mag = 3
        Combat.addStatus(source, "Superior Training", duration, mag)

    # Druid
    def applyKnowledgeOfPoison(self, target):
        target.basePoisonBonusDamage += 30

    def applyPotencyOfPoisons(self, target):
        target.basePoisonRatingBonus += 5

    def applyExposureToPoison(self, target):
        target.basePoisonTolerance += 5
        target.basePoisonResistance += 20

    def applyTimeWithNature(self, target):
        target.basePoisonResistance += 5
        target.baseColdResistance += 5

    # Tactician
    def applySpellsOfDeception(self, target, reverse=False, spell=None):
        if not reverse:
            if spell.school == "Illusion" or spell.school == "Mental":
                target.statusSpellpower += 5
        else:
            if spell.school == "Illusion" or spell.school == "Mental":
                target.statusSpellpower -= 5

    # Assassin
    def applyAnatomy(self, target):
        target.baseCriticalChance += 10

    def applySlightlySneakier(self, target):
        target.baseSneak += 3

    def applyDabblesWithPoison(self, target):
        target.basePoisonRatingBonus += 2

    # Shadow
    def applyADabblerOfSorts(self, target):
        target.basePoisonRatingBonus += 3
        target.basePoisonBonusDamage += 5

    def applyBackflip(self, target, reverse=False, other=None):
        source = self.owner
        direction = other.cLocation.direction_to(source.cLocation)
        if not Combat.againstWall(source.cPane, source.cLocation, direction):
            if not reverse:
                source.statusDodge += 3
            else:
                source.statusDodge -= 3

    def applyTreasureBag(self, target):
        target.baseInventoryCapacity += 15

    def applyAnEyeForValue(self, target):
        target.goldFind += 2

    def applySlingSkills(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeapon("Sling"):
                source.statusRangedAccuracy += 5
        else:
            if source.usingWeapon("Sling"):
                source.statusRangedAccuracy -= 5

    def applyHideInPeril(self, target, reverse=False, damage=None):
        source = self.owner
        if damage >= source.totalHP * 0.3 and not source.inStealth():
            Combat.addStatus(source, "Shadow Walk", -1)

    def applyBackstabUpgrade(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Backstab":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)

    def applyBackstabUpgrade2(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Bleeding Backstab":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)

    # Nightblade
    def applyNightArmor(self, target):
        target.baseDR += 3
        target.baseShadowResistance += 3
        target.avoidanceChance += 3

    def applyForbiddenStudies(self, target):
        target.baseShadowBonusDamage += 5

    def applySingleBlade(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeaponStyle("Single"):
                source.statusMeleeAccuracy += 4
                source.statusCriticalChance += 6
        else:
            if source.usingWeaponStyle("Single"):
                source.statusMeleeAccuracy -= 4
                source.statusCriticalChance -= 6

    def applyMagicalDarkness(self, target, reverse=False, **kwArgs):
        source = self.owner
        if not reverse:
            if source.inStealth():
                source.statusShadowBonusDamage += 5
                source.statusSpellpower += 4
        else:
            if source.inStealth():
                source.statusShadowBonusDamage -= 5
                source.statusSpellpower -= 4

    def applyUpCloseAndPersonal(self, target, reverse=False, spell=None):
        source = self.owner
        if not reverse:
            if spell.school == "Bane" and source.cLocation.in_melee_range(target.cLocation):
                source.statusSpellpower += 4
        else:
            if spell.school == "Bane" and source.cLocation.in_melee_range(target.cLocation):
                source.statusSpellpower -= 4

    def applySingleBlade2(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeaponStyle("Single"):
                source.statusMeleeAccuracy += 4
                source.statusCriticalChance += 6
        else:
            if source.usingWeaponStyle("Single"):
                source.statusMeleeAccuracy -= 4
                source.statusCriticalChance -= 6

    # Battle Mage
    def applyCloseRangedMagic(self, target, reverse=False, spell=None):
        if not reverse:
            if spell.range < 4:
                target.baseSpellpower += 6
        else:
            if spell.range < 4:
                target.baseSpellpower -= 6

    def applyManaAttack(self, target, reverse=False, other=None):
        if not reverse:
            Combat.modifyResource(target, "MP", 8)
        else:
            pass

    def applyDireMana(self, target, reverse=False, damage=0):
        if not reverse:
            if damage >= target.totalHP * 0.15:
                Combat.modifyResource(target, "MP", int(round(target.totalMP * 0.10)))
        else:
            pass

    def applyMysticalAccuracy(self, target):
        target.baseMeleeAccuracy += 2

    def applyMysticalShieldUse(self, target, reverse=False, other=None):
        if not reverse:
            if target.usingShield("Any"):
                target.baseDR += 3
        else:
            if target.usingShield("Any"):
                target.baseDR -= 3

    def applyRapidRetreat(self, target, reverse=False, other=None):
        if not reverse:
            if target.HP < target.totalHP * 0.20:
                Combat.setMovementCost(target, 3)
        else:
            Combat.setMovementCost(target, -1)

    def applyMilitaryDefensiveTraining(self, target, reverse=False, spell=None):
        if not target.usingShield():
            return
        if not reverse:
            target.statusMagicResist += 3
        else:
            target.statusMagicResist -= 3

    def applyMilitarySpellTraining(self, target, reverse=False, spell=None):
        if target.usingShield():
            return
        if not reverse:
            target.statusSpellpower += 2
        else:
            target.statusSpellpower -= 2

    def applyMilitaryOffensiveTraining(self, target, reverse=False, other=None):
        if target.usingWeapon("Club"):
            if not reverse:
                target.statusMight += 5
            else:
                target.statusMight -= 5
        else:
            if not reverse:
                target.statusMeleeAccuracy += 2
            else:
                target.statusMeleeAccuracy -= 2

    def applyRefraction(self, target, reverse=False, spell=None):
        if spell.range > -1 and spell.range < 5:
            duration = 1
            magnitude = 5
            Combat.addStatus(self.owner, "Refraction", duration, magnitude)

    # Arcane Archer
    def applyManaArrows(self, target, reverse=False, other=None):
        source = self.owner
        if source.usingWeapon("Bow") or source.usingWeapon("Crossbow"):
            Combat.modifyResource(source, "MP", source.arcaneArcherManaRegen)

    def applyConduit(self, target):
        target.baseArcaneBonusDamage += 15
        target.baseCriticalMagnitude += 5

    def applyMysticalResearch(self, target, reverse=False, spell=None):
        source = self.owner
        if not reverse:
            if spell.school == "Mystic":
                source.statusSpellpower += 4
        else:
            if spell.school == "Mystic":
                source.statusSpellpower -= 4

    def applyArcaneThreadingUpgrade(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Arcane Threading":
                toRemove = abil
                break
        if toRemove:
            target.abilities.remove(toRemove)

    # Trickster

    def applyWildSurvival(self, target):
        target.baseDodge += 14

    def applyGlee(self, target, reverse=False):
        source = self.owner
        Combat.modifyResource(source, "MP", source.level * 2 + 10)

    def applyInfuriatingBlows(self, target, reverse=False, other=None):
        source = self.owner
        Combat.modifyResource(source, "MP", 2)

    def applyBurningPassion(self, target):
        target.baseFireBonusDamage += 15

    def applyDoubleDodge(self, target, reverse=False):
        source = self.owner
        Combat.addStatus(source, "Double Dodge", 1)
        magnitude = min(15, 5 * source.getStatusStackCount("Double Dodge"))
        source.statusDodge += magnitude

    def applyRiskyFighting(self, target, reverse=False, other=None):
        source = self.owner
        if not reverse:
            if source.usingWeaponStyle("Dual"):
                source.statusMeleeAccuracy += 4
                source.statusCriticalChance += 5
        else:
            if source.usingWeaponStyle("Dual"):
                source.statusMeleeAccuracy -= 4
                source.statusCriticalChance -= 5

    def applySlightlySmugger(self, target, reverse=False):
        source = self.owner
        duration = 2
        magnitude = 3
        Combat.addStatus(source, "Slightly Smugger", duration, magnitude)

    def applyJustPlainLucky(self, target):
        target.baseDodge += 3

    # Debug

    def applyLibertarian(self, target):
        target.baseHP += 1000

    # Monsters

    def applyDeflectMissiles(self, target, reverse=False, other=None):
        ''' Monsters with Deflect Missiles gain 10 Dodge and 5% DR against Ranged
        attacks.'''
        source = self.owner
        if not reverse:
            source.statusDR += 5
            source.statusDodge += 10
        else:
            source.statusDR -= 5
            source.statusDodge -= 10

    def applyGrowingBoldness(self, target, reverse=False, other=None):
        ''' Monsters with Growing Boldness gain +2 Strength and 1% attack power after
        every attempt to attack in melee. '''
        source = self.owner
        source.statusStrength += 2
        source.attackPower += 1
        Combat.sendCombatMessage(source.name + " Grows more bold.", other, color='red')

    def applyKnockback2(self, target, reverse=False, other=None):
        ''' Monsters with Knockback 2, will knockback targets when they successfully
        hit them with their basic attack 2 tiles. '''
        source = self.owner
        distance = 2
        #Combat.knockback(other, self.cLocation, distance)

    def applyMonsterAgility(self, target):
        ''' Monsters with 'Monster Agility' have +10-30 Dodge (based on level). '''
        target.baseDodge += target.level + 10

    def applyPanic(self, target, reverse=False, other=None):
        ''' Monsters that Panic gain Dexterity (increasing their accuracy and
        dodge) every time they are hit with melee attacks.
        Lasts the entire battle and stacks. '''
        source = self.owner
        source.statusDexterity += 2
        Combat.sendCombatMessage(source.name + " Panics; +2 Dexterity.", other, color='red')

    def applyRegeneration(self, target, reverse=False):
        ''' Monsters with regerenation recover 15% of their max HP each turn.'''
        source = self.owner
        source.HP += round(source.totalHP * 0.15)

    allContentByName = {
        'Cold Endurance':
        {
        'class' : 'Barbarian',
        'level' : 1,
        'type' : 'static',
        'action' : applyColdEndurance,
        'image' : BARBARIAN + "cold-endurance.png",
        'text' : '+10% Cold Resistance'
        },
        'Magical Vulnerability':
        {
        'class' : 'Barbarian',
        'level' : 1,
        'type' : 'static',
        'action' : applyMagicalVulnerability,
        'image' : BARBARIAN + "magical-vulnerability.png",
        'text' : '-3 Magic Resist'
        },
        'Mighty Weapon':
        {
        'class' : 'Barbarian',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyMightyWeapon,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : BARBARIAN + "mighty-weapon.png",
        'text' : '+6 Might on attacks with two-handed weapons'
        },
        'Two Weapon Targeting':
        {
        'class' : 'Barbarian',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyTwoWeaponTargeting,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : BARBARIAN + "two-weapon-targeting.png",
        'text' : "+3 Accuracy on attacks with two weapons"
        },
        'Blood on the Edge':
        {
        'class' : 'Barbarian',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyBloodOnTheEdge,
        'onStringList' : ['Incoming Damage'],
        'offStringList' : [],
        'image' : BARBARIAN + "blood-on-the-edge.png",
        'text' : "Any incoming damage dealing less than 5% of maximum HP\n" + \
                "is ignored while the Barbarian has less than 30% HP."
        },
        'Magical Ignorance':
        {
        'class' : 'Barbarian',
        'level' : 3,
        'type' : 'static',
        'action' : applyMagicalIgnorance,
        'image' : BARBARIAN + "magical-ignorance.png",
        'text' : '-3 Magic Resist'
        },
        'Stunning Recovery':
        {
        'class' : 'Barbarian',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyStunningRecovery,
        'onStringList' : ['Incoming Status Applied'],
        'offStringList' : [],
        'image' : BARBARIAN + "stunning-recovery.png",
        'text' : 'Whenever the Barbarian is stunned, he recovers 10% of his\n' + \
                'Maximum HP.  May occur once per monster turn.'
        },
        'Walk it off':
        {
        'class' : 'Barbarian',
        'level' : 5,
        'type' : 'dynamic',
        'action' : applyWalkItOff,
        'onStringList' : ['Player Turn Start'],
        'offStringList' : [],
        'image' : BARBARIAN + "walk-it-off.png",
        'text' : 'As long as the Barbarian performed at least one movement action\n' + \
                'during the previous turn, he regains 1% Max HP at the start of\n' + \
                'this turn.'
        },


        'Oblivious':
        {
        'class' : 'Dragoon',
        'level' : 1,
        'type' : 'static',
        'action' : applyOblivious,
        'image' : DRAGOON + "oblivious.png",
        'text' : 'Focusing on the sky all the time clouds your mind.\n' + \
                '-12 Intuition, -5 Awareness'
        },
        'Polearm Specialization':
        {
        'class' : 'Dragoon',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyPolearmSpecialization,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : DRAGOON + "polearm-specialization.png",
        'text' : 'Grants Force x 1.30 and Critical hit chance + 5% when using polearms.'
        },
        'Dragon Foe':
        {
        'class' : 'Dragoon',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyDragonFoe,
        'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack',
                          'Incoming Melee Attack', 'Incoming Ranged Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete',
                           'Incmoing Melee Attack Complete', 'Incoming Ranged Attack Complete'],
        'image' : DRAGOON + 'dragon-foe.png',
        'text' : '+2 Melee and Ranged Accuracy vs. dragonkin and +2 Dodge vs. their attacks.'
        },
        'Fire-Touched':
        {
        'class' : 'Dragoon',
        'level' : 2,
        'type' : 'static',
        'action' : applyFireTouched,
        'image' : DRAGOON + 'fire-touched.png',
        'text' : '+10% Fire Resistance'
        },
        '--IGNORE-- Jump Attack Upgrade':
        {
        'class' : 'Dragoon',
        'level' : 3,
        'type' : 'static',
        'action' : applyJumpAttackUpgrade
        },
        '--IGNORE-- Jump Attack Upgrade 2':
        {
        'class' : 'Dragoon',
        'level' : 4,
        'type' : 'static',
        'action' : applyJumpAttackUpgrade2
        },
        '--IGNORE-- Jump Attack Upgrade 3':
        {
        'class' : 'Dragoon',
        'level' : 5,
        'type' : 'static',
        'action' : applyJumpAttackUpgrade3
        },

        'Shield Efficiency':
        {
        'class' : 'Weapon Master',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyShieldEfficiency,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : [],
        'image' : WEAPONMASTER + 'shield-efficiency.png',
        'text' : 'Basic melee attacks refund 1 AP when using a shield.' 
        },
        'Direct Counterattack':
        {
        'class' : 'Weapon Master',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyDirectCounterattack,
        'onStringList' : ['Incoming Melee Attack'],
        'offStringList' : [],
        'image' : WEAPONMASTER + 'direct-counterattack.png',
        'text' : "Upon being attacked in melee by an enemy directly\n" +\
                 "in front of you, you will immediately counterattack with a\n" +\
                 "basic melee attack during the enemy's turn."
        },
        'Shield Counter':
        {
        'class' : 'Weapon Master',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyShieldCounter,
        'onStringList' : ['Outgoing Counterattack'],
        'offStringList' : [],
        'image' : WEAPONMASTER + 'shield-counter.png',
        'text' : 'Deal 50% extra damage as bludgeoning during counterattacks.\n' +\
                 'Must have a shield equipped.'
        },
        'Two-Handed Parry':
        {
        'class' : 'Weapon Master',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyTwoHandedParry,
        'onStringList' : ['Incoming Melee Attack'],
        'offStringList' : ['Incoming Melee Attack Complete'],
        'image' : WEAPONMASTER + 'two-handed-parry.png',
        'text' : 'When attacked from angles from which you can counterattack,\n' +\
                 '+4 Dodge if equipped with a two-handed weapon.'
        },
        'Hold the Line':
        {
        'class' : 'Weapon Master',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyHoldTheLine,
        'onStringList' : ['Player HP Level Changed'],
        'offStringList' : ['Player HP Level Changed'],
        'image' : WEAPONMASTER + 'hold-the-line.png',
        'text' :  'If your HP is reduced below 30%, you gain +5% DR until\n' +\
                  'it reaches 30% or higher. Must have a shield equipped.'
        },
        'Direct Counterattack 2':
        {
        'class' : 'Weapon Master',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyDirectCounterattack2,
        'onStringList' : ['Incoming Melee Attack'],
        'offStringList' : [],
        'image' : WEAPONMASTER + 'direct-counterattack.png',
        'text' : "Upon being attacked in melee by an enemy directly\n" +\
                 "in front of you, or front-diagonal to you, you will\n" +\
                 "immediately counterattack with a basic melee\n" +\
                 "attack during the enemy's turn."
        },
        '--IGNORE-- Direct Counterattack Upgrade':
        {
        'class' : 'Weapon Master',
        'level' : 4,
        'type' : 'static',
        'action' : applyDirectCounterattackUpgrade
        },
        'Two-Weapon Glancing':
        {
        'class' : 'Weapon Master',
        'level' : 5,
        'type' : 'dynamic',
        'action' : applyTwoWeaponGlancing,
        'onStringList' : ['Incoming Melee Attack'],
        'offStringList' : ['Incoming Melee Attack Complete'],
        'image' : WEAPONMASTER + 'two-weapon-glancing.png',
        'text' : 'Gain +2% DR against melee attacks while equipping two weapons.'
        },
        'Rapid Bandaging':
        {
        'class' : 'Weapon Master',
        'level' : 5,
        'type' : 'dynamic',
        'action' : applyRapidBandaging,
        'onStringList' : ['Incoming Status Applied'],
        'offStringList' : [],
        'image' : WEAPONMASTER + 'rapid-bandaging.png',
        'text' : 'When a bleeding effect would normally be applied to the\n' +\
                 'Weaponmaster, there is a 50% chance that it will be ignored.'
        },
        
        'Seeker of Enchantments':
        {
        'class' : 'Spellsword',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applySeekerOfEnchantments,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete'],
        'image' : SPELLSWORD + 'seeker-of-enchantments.png',
        'text' : '+6 Spellpower when casting enchantment spells'
        },
        'Duality':
        {
        'class' : 'Spellsword',
        'level' : 1,
        'type' : 'static',
        'action' : applyDuality,
        'image' : SPELLSWORD + 'duality.png',
        'text' : '+2% DR and +1 magic resist'
        },
        'Lasting Enchantment':
        {
        'class' : 'Spellsword',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyLastingEnchantment,
        'onStringList' : ['Outgoing Spell Cast Complete'],
        'offStringList' : [],
        'image' : SPELLSWORD + 'lasting-enchantment.png',
        'text' : '+1 Turn to all enchantments cast on yourself'
        },
        'Keen Enchantment':
        {
        'class' : 'Spellsword',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyKeenEnchantment,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : SPELLSWORD + 'keen-enchantment.png',
        'text' : '+8% To critical hit chance when using a two-handed weapon\n' + \
                'that is also benefiting from a Spellsword enchantment.'
        },
        'Focal Point':
        {
        'class' : 'Spellsword',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyFocalPoint,
        'onStringList' : ['Outgoing Melee Attack Critical Hit'],
        'offStringList' : [],
        'image' : SPELLSWORD + 'focal-point.png',
        'text' : '+15 divine damage on critical hits if using an enchanted,\n' + \
                'two-handed weapon'
        },
        'Blades of Reduction':
        {
        'class' : 'Spellsword',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyBladesOfReduction,
        'onStringList' : ['Outgoing Melee Attack Hit', 'Outgoing Melee Attack Critical Hit'],
        'offStringList' : [],
        'image' : SPELLSWORD + 'blades-of-reduction.png',
        'text' : 'If wielding a weapon that deals slashing damage, successful hits reduce\n' + \
                'a target\'s magic resist by 4 and fire resistance by 10% with a reliable chance.'
        },

        # Anarchist
        'Trap Chaos':
        {
        'class' : 'Anarchist',
        'level' : 1,
        'type' : 'static',
        'action' : None,
        'image' : ANARCHIST + 'trap-chaos.png',
        'text' : 'You can lay down traps on adjacent enemies.  If you do so, the trap\n' + \
                'is immediately triggered and has a trap rating bonus of  +5 + Cunning/10.\n' + \
                'Traps with multiple charges apply all charges at once.  (If the trap does\n' + \
                'not deal damage, the duration of the inflicted status is multiplied\n' + \
                'instead.'
        },
        'Hate Craft':
        {
        'class' : 'Anarchist',
        'level' : 1,
        'type' : 'static',
        'action' : applyHateCraft,
        'image' : ANARCHIST + 'hate-craft.png',
        'text' : 'Anarchist traps are particularly deadly.  +20% All Trap Damage.'
        },
        'Shock and Burn':
        {
        'class' : 'Anarchist',
        'level' : 3,
        'type' : 'static',
        'action' : applyShockAndBurn,
        'image' : ANARCHIST + 'shock-and-burn.png',
        'text' : '+5% Fire and Electric Damage, +10% Electric resistance and\n' + \
                '+2% Armor Penetration on all attacks.'
        },
        'Rushed Delivery':
        {
        'class' : 'Anarchist',
        'level' : 5,
        'type' : 'dynamic',
        'action' : applyRushedDelivery,
        'onStringList' : ['Trap Chaos'],
        'offStringList' : ['Trap Chaos Complete'],
        'image' : ANARCHIST + 'rushed-delivery.png',
        'text' : 'If you have moved three or more tiles this turn, any trap you\n' + \
                'use on an enemy will deal +50% Overall damage and have an\n' + \
                'additional +2 Trap Rating.'
        },

        'Excellent Vision':
        {
        'class' : 'Marksman',
        'level' : 1,
        'type' : 'static',
        'action' : applyExcellentVision,
        'image' : MARKSMAN + 'excellent-vision.png',
        'text' : '+2 Range with all ranged weapons and +2 Awareness'
        },
        'Laying in Wait':
        {
        'class' : 'Marksman',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyLayingInWait,
        'onStringList' : ['Player Turn Start'],
        'offStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
        'image' : MARKSMAN + 'laying-in-wait.png',
        'text' : 'If the Marksman did not move last turn, gain +4 Accuracy.'
        },
        'Fire Handler':
        {
        'class' : 'Marksman',
        'level' : 2,
        'type' : 'static',
        'action' : applyFireHandler,
        'image' : MARKSMAN + 'fire-handler.png',
        'text' : '+5% Fire Resistance, +5% Fire damage'
        },
        'Camouflage':
        {
        'class' : 'Marksman',
        'level' : 2,
        'type' : 'static',
        'action' : applyCamouflage,
        'image' : MARKSMAN + 'camouflage.png',
        'text' : 'If invisible via magical spells or potions, +8 Sneak.\n' + \
                'Also grants +2 Dodge and +2 Ranged Accuracy always.'

        },
        'Shortbow Niche':
        {
        'class' : 'Marksman',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyShortbowNiche,
        'onStringList' : ['Outgoing Ranged Attack'],
        'offStringList' : ['Outgoing Ranged Attack Complete'],
        'image' : MARKSMAN + 'shortbow-niche.png',
        'text' : '+10% Critical Magnitude and +5% Critical Chance when using a shortbow.'
        },
        'Incredible Focus':
        {
        'class' : 'Marksman',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyIncredibleFocus,
        'onStringList' : ['Status Applied'],
        'offStringList' : [],
        'image' : MARKSMAN + 'incredible-focus.png',
        'text' : 'Any successful stun attack against the Marksman has a 75% chance\n' + \
                'of failing to affect her.'
        },
        'Superior Training':
        {
        'class' : 'Marksman',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applySuperiorTraining,
        'onStringList' : ['Incoming Ranged Attack Hit'],
        'offStringList' : [],
        'image' : MARKSMAN + 'superior-training.png',
        'text' : 'If the Marksman is hit with a non-magical ranged attack, her accuracy\n' + \
                'increases by 3 for the next turn.'
        },

        # Druid
        'Knowledge of Poison':
        {
        'class' : 'Druid',
        'level' : 1,
        'type' : 'static',
        'action' : applyKnowledgeOfPoison,
        'image' : DRUID + 'knowledge-of-poison.png',
        'text' : '+30% to all poison damage dealt.'
        },
        'Potency of Poisons':
        {
        'class' : 'Druid',
        'level' : 1,
        'type' : 'static',
        'action' : applyPotencyOfPoisons,
        'image' : DRUID + 'potency-of-poisons.png',
        'text' : '+5 Poison rating to all poison skills and\n' + \
                'applications.'
        },
        'Exposure to Poison':
        {
        'class' : 'Druid',
        'level' : 1,
        'type' : 'static',
        'action' : applyExposureToPoison,
        'image' : DRUID + 'exposure-to-poison.png',
        'text' : '+5 Poison Tolerance and +20% Poison resistance.'
        },
        'Time with Nature':
        {
        'class' : 'Druid',
        'level' : 3,
        'type' : 'static',
        'action' : applyTimeWithNature,
        'image' : DRUID + 'time-with-nature.png',
        'text' : '+5% Poison Resistance; +5% Cold Resistance'
        },

        # Tactician
        'Spells of Deception':
        {
        'class' : 'Tactician',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applySpellsOfDeception,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete']
        },

        # Assassin
        'Anatomy':
        {
        'class' : 'Assassin',
        'level' : 1,
        'type' : 'static',
        'action' : applyAnatomy,
        'image' : ASSASSIN + 'anatomy.png',
        'text' : '+10% Critical chance for all melee and ranged attacks\n' + \
                'other than ranged backstabs.'
        },
        'Slightly Sneakier':
        {
        'class' : 'Assassin',
        'level' : 3,
        'type' : 'static',
        'action' : applySlightlySneakier,
        'image' : ASSASSIN + 'slightly-sneakier.png',
        'text' : '+3 Sneak'
        },
        'Dabbles with Poison':
        {
        'class' : 'Assassin',
        'level' : 4,
        'type' : 'static',
        'action' : applyDabblesWithPoison,
        'image' : ASSASSIN + 'dabbles-with-poison.png',
        'text' : '+2 Poison Rating to all applied poisons'
        },


        # Shadow
        'A Dabbler of Sorts':
        {
        'class' : 'Shadow',
        'level' : 1,
        'type' : 'static',
        'action' : applyADabblerOfSorts,
        'image' : SHADOW + 'a-dabbler-of-sorts.png',
        'text' : '+3 Poison rating to any applied poisons and +5% poison damage overall.'
        },
        'Backflip':
        {
        'class' : 'Shadow',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyBackflip,
        'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
        'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete'],
        'image' : SHADOW + 'backflip.png',
        'text' : 'If there is at least one unoccupied passable tile behind you when you are\n' + \
                'attacked by a ranged or melee attack, you gain +3 Dodge against it.'
        },
        'Treasure Bag':
        {
        'class' : 'Shadow',
        'level' : 2,
        'type' : 'static',
        'action' : applyTreasureBag,
        'image' : SHADOW + 'treasure-bag.png',
        'text' : '+15 lbs. carrying capacity'
        },
        'An Eye for Value':
        {
        'class' : 'Shadow',
        'level' : 2,
        'type' : 'static',
        'action' : applyAnEyeForValue,
        'image' : SHADOW + 'an-eye-for-value.png',
        'text' : '+2% Gold Find'
        },
        '--IGNORE-- Backstab Upgrade':
        {
        'class' : 'Shadow',
        'level' : 2,
        'type' : 'static',
        'action' : applyBackstabUpgrade
        },
        'Sling Skills':
        {
        'class' : 'Shadow',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applySlingSkills,
        'onStringList' : ['Outgoing Ranged Attack'],
        'offStringList' : ['Outgoing Ranged Attack Complete'],
        'image' : SHADOW + 'sling-skills.png',
        'text' : '+5 Accuracy with slings'
        },
        'Hide in Peril':
        {
        'class' : 'Shadow',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyHideInPeril,
        'onStringList' : ['Incoming Damage'],
        'offStringList' : [],
        'image' : SHADOW + 'hide-in-peril.png',
        'text' : 'When harmed by anything dealing at least 30% of your maximum HP,\n' + \
                'you will immediately enter stealth if you aren\'t in stealth already.'
        },
        '--IGNORE-- Backstab Upgrade 2':
        {
        'class' : 'Shadow',
        'level' : 5,
        'type' : 'static',
        'action' : applyBackstabUpgrade2
        },


        # Nightblade
        'Night Armor':
        {
        'class' : 'Nightblade',
        'level' : 1,
        'type' : 'static',
        'action' : applyNightArmor,
        'image' : NIGHTBLADE + 'night-armor.png',
        'text' : 'Grants +3% DR, +3% Avoidance, +3% Shadow Resistance'
        },
        'Forbidden Studies':
        {
        'class' : 'Nightblade',
        'level' : 1,
        'type' : 'static',
        'action' : applyForbiddenStudies,
        'image' : NIGHTBLADE + 'forbidden-studies.png',
        'text' : '+5% Shadow Damage'
        },
        'Single Blade':
        {
        'class' : 'Nightblade',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applySingleBlade,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : NIGHTBLADE + 'single-blade.png',
        'text' : '+4 Melee Accuracy and +6% Critical Chance when using only\n' + \
                'one one-handed weapon and no shield.'
        },
        'Magical Darkness':
        {
        'class' : 'Nightblade',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMagicalDarkness,
        'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack', 'Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete', 'Outgoing Spell Cast Complete'],
        'image' : NIGHTBLADE + 'magical-darkness.png',
        'text' : 'While in stealth, +5% Shadow Damage and +4 Spellpower'
        },
        'Up close and Personal':
        {
        'class' : 'Nightblade',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyUpCloseAndPersonal,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete'],
        'image' : NIGHTBLADE + 'up-close-and-personal.png',
        'text' : 'Bane spells cast in melee range have +4 Spellpower.'
        },
        'Single Blade 2':
        {
        'class' : 'Nightblade',
        'level' : 5,
        'type' : 'dynamic',
        'action' : applySingleBlade2,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : NIGHTBLADE + 'single-blade.png',
        'text' : 'Grants an additional +4 Melee Accuracy and +6% Critical Chance when\n' + \
                'using only one one-handed weapon and no shield.'
        },

        # Battle Mage
        'Close-Ranged Magic':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyCloseRangedMagic,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete'],
        'image' : BATTLEMAGE + 'close-ranged-magic.png',
        'text' : '+6 Spellpower with all spells having a range of 3 or less.'
        },
        'Mana Attack':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyManaAttack,
        'onStringList' : ['Outgoing Melee Attack Hit'],
        'offStringList' : [],
        'image' : BATTLEMAGE + 'mana-attack.png',
        'text' : '+8 mana for every sucessful melee attack'
        },
        'Dire Mana':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyDireMana,
        'onStringList' : ['Incoming Damage'],
        'offStringList' : [],
        'image' : BATTLEMAGE + 'dire-mana.png',
        'text' : 'Recover 10% of MP when receiving damage of at least 15% of max HP.'
        },
        'Mystical Accuracy':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'static',
        'action' : applyMysticalAccuracy,
        'image' : BATTLEMAGE + 'mystical-accuracy.png',
        'text' : '+2 Melee Accuracy'
        },
        'Mystical Shield Use':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyMysticalShieldUse,
        'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
        'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete'],
        'image' : BATTLEMAGE + 'mystical-shield-use.png',
        'text' : '+3% DR when using any shield'
        },
        'Rapid Retreat':
        {
        'class' : 'Battle Mage',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyRapidRetreat,
        'onStringList' : ['Player Turn Start'],
        'offStringList' : ['Monster Turn Start'],
        'image' : BATTLEMAGE + 'rapid-retreat.png',
        'text' : 'If HP is below 20% at the start of your turn, movement only costs 3 AP.'
        },
        'Military Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : None,
        'onStringList' : [],
        'offStringList' : [],
        'image' : BATTLEMAGE + 'military-training.png',
        'text' : 'If wielding a club weapon, +5 Might; otherwise, +2 Accuracy.\n' + \
                'If wielding a shield, +3 magic resist; otherwise, +2 spellpower.'
        },
        '--IGNORE-- Military Defensive Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMilitaryDefensiveTraining,
        'onStringList' : ['Incoming Spell Cast'],
        'offStringList' : ['Incoming Spell Cast Complete'],
        'image' : BATTLEMAGE + 'military-training.png',
        'text' : 'If wielding a club weapon, +5 Might; otherwise, +2 Accuracy.\n' + \
                'If wielding a shield, +3 magic resist; otherwise, +2 spellpower.'
        },
        '--IGNORE-- Military Spell Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMilitarySpellTraining,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete'],
        'image' : BATTLEMAGE + 'military-training.png',
        'text' : 'If wielding a club weapon, +5 Might; otherwise, +2 Accuracy.\n' + \
                'If wielding a shield, +3 magic resist; otherwise, +2 spellpower.'
        },
        '--IGNORE-- Military Offensive Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMilitaryOffensiveTraining,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : BATTLEMAGE + 'military-training.png',
        'text' : 'If wielding a club weapon, +5 Might; otherwise, +2 Accuracy.\n' + \
                'If wielding a shield, +3 magic resist; otherwise, +2 spellpower.'
        },
        'Refraction':
        {
        'class' : 'Battle Mage',
        'level' : 5,
        'type' : 'dynamic',
        'action' : applyRefraction,
        'onStringList' : ['Outgoing Spell Cast Complete'],
        'offStringList' : [],
        'image' : BATTLEMAGE + 'refraction.png',
        'text' : 'After casting a spell with a max range of 4 or less,\n' + \
                'gain +5% DR for the remainder of this turn.'
        },

        # Arcane Archer
        'Mana Arrows':
        {
        'class' : 'Arcane Archer',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyManaArrows,
        'onStringList' : ['Outgoing Ranged Attack Complete'],
        'offStringList' : [],
        'image' : ARCANE_ARCHER + 'mana-arrows.png',
        'text' : 'All ranged attacks with either a bow or crossbow regenerate 6 MP.\n' + \
                'This occurs even if the attack misses.'
        },
        'Conduit':
        {
        'class' : 'Arcane Archer',
        'level' : 1,
        'type' : 'static',
        'action' : applyConduit,
        'image' : ARCANE_ARCHER + 'conduit.png',
        'text' : '+15% Arcane Damage, +5% Critical Magnitude'
        },
        'Mystical Research':
        {
        'class' : 'Arcane Archer',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyMysticalResearch,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete'],
        'image' : ARCANE_ARCHER + 'mystical-research.png',
        'text' : '+4 Spellpower with all Mystic spells.'
        },
        '--IGNORE-- Arcane Threading Upgrade':
        {
        'class' : 'Arcane Archer',
        'level' : 4,
        'type' : 'static',
        'action' : applyArcaneThreadingUpgrade
        },

        # Trickster
        'Wild Survival':
        {
        'class' : 'Trickster',
        'level' : 1,
        'type' : 'static',
        'action' : applyWildSurvival,
        'image' : TRICKSTER + 'wild-survival.png',
        'text' : '+14 Dodge'
        },
        'Glee':
        {
        'class' : 'Trickster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyGlee,
        'onStringList' : ['Attack Dodged'],
        'offStringList' : [],
        'image' : TRICKSTER + 'glee.png',
        'text' : 'Regain 10 + 2 * Level MP every time you dodge an attack.'
        },
        'Infuriating Blows':
        {
        'class' : 'Trickster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyInfuriatingBlows,
        'onStringList' : ['Outgoing Melee Attack Hit', 'Outgoing Ranged Attack Hit'],
        'offStringList' : [],
        'image' : TRICKSTER + 'infuriating-blows.png',
        'text' : 'Regain 2 MP for every successful melee or ranged attack.'
        },
        'Burning Passion':
        {
        'class' : 'Trickster',
        'level' : 1,
        'type' : 'static',
        'action' : applyBurningPassion,
        'image' : TRICKSTER + 'burning-passion.png',
        'text' : '+15% Bonus Fire Damage'
        },
        'Double Dodge':
        {
        'class' : 'Trickster',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyDoubleDodge,
        'onStringList' : ['Attack Dodged'],
        'offStringList' : [], # Removed on status removal.
        'image' : TRICKSTER + 'double-dodge.png',
        'text' : 'If you dodge an attack, +5 Dodge for the rest of the turn.\n' + \
                'Stacks twice up to a total of +15 Dodge.'
        },
        'Risky Fighting':
        {
        'class' : 'Trickster',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyRiskyFighting,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete'],
        'image' : TRICKSTER + 'risky-fighting.png',
        'text' : '+4 Accuracy and +5% Critical chance with melee weapons if dual wielding.'
        },
        'Slightly Smugger':
        {
        'class' : 'Trickster',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applySlightlySmugger,
        'onStringList' : ['Attack Dodged'],
        'offStringList' : [], # Removed on status removal
        'image' : TRICKSTER + 'slightly-smugger.png',
        'text' : 'If you dodge an attack, gain +3 Spellpower for your next turn.'
        },
        'Just Plain Lucky':
        {
        'class' : 'Trickster',
        'level' : 5,
        'type' : 'static',
        'action' : applyJustPlainLucky,
        'image' : TRICKSTER + 'just-plain-lucky.png',
        'text' : '+3 Dodge'
        },

        # Debug
        'Libertarian':
        {
        'class' : 'Debug',
        'level' : 1,
        'type' : 'static',
        'action' : applyLibertarian
        },

        # Monsters
        'Deflect Missiles':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyDeflectMissiles,
        'onStringList' : ['Incoming Ranged Attack'],
        'offStringList' : ['Incoming Ranged Attack Complete']
        },
        'Growing Boldness':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyGrowingBoldness,
        'onStringList' : ['Outgoing Melee Attack Complete'],
        'offStringList' : []
        },
        'Knockback 2':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyKnockback2,
        'onStringList' : ['Outgoing Melee Attack Hit', 'Outgoing Ranged Attack Hit'],
        'offStringList' : []
        },
        'Monster Agility':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'static',
        'action' : applyMonsterAgility
        },
        'Panic':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyPanic,
        'onStringList' : ['Incoming Melee Attack Hit'],
        'offStringList' : []
        },
        'Regeneration':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyRegeneration,
        'onStringList' : ['Monster Turn Start'],
        'offStringList' : []
        }



    }








