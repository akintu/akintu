#!/usr/bin/python

import sys
import listener
import location
from combat import *


ROOT_FOLDER = "./res/images/icons/"

FIGHTER = ROOT_FOLDER + "traits/fighter_traits/"
RANGER = ROOT_FOLDER + "traits/ranger_traits/"
THIEF = ROOT_FOLDER + "traits/thief_traits/"
WIZARD = ROOT_FOLDER + "traits/wizard_traits/"


class TraitStub(object):
    def __init__(self, name):
        self.name = name
        self.text = 'TODO'
        self.image = './res/images/icons/cubeforce.png'
        info = Trait.allContentByName[name]
        if 'text' in info:
            self.text = info['text']
        if 'image' in info:
            self.image = info['image']

class Trait(object):

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        content = Trait.allContentByName[name]
        self.requiredClass = content['class']
        self.type = content['type']
        self.action = content['action']
        self.rank = 1
        self.onStringList = None
        self.offStringList = None
        self.extraStaticAction = None
        if self.type == 'dynamic' or self.type == "dynamic and static":
            self.onStringList = content['onStringList']
            self.offStringList = content['offStringList']
            self.registerListener()
        else:
            self.action(self, self.owner)
        if self.type == "dynamic and static":
            self.extraStaticAction = content['staticAction']
            self.extraStaticAction(self, self.owner)


    def advanceTier(self):
        if self.rank == 4:
            return
        if self.rank == 3 and player.level < 7:
            return
        if self.rank == 2 and player.level < 5:
            return
        if self.rank == 1 and player.level < 3:
            return
        self.rank += 1
        if self.type == "static":
            self.action(self, self.owner)

    @staticmethod
    def getTraitRank(player, traitName):
        for t in player.traits:
            if t.name == traitName:
                return t.rank
        return 0

    def registerListener(self):
        newListener = listener.Listener(self.owner, self.onStringList, self.action, self.offStringList)
        self.owner.listeners.append(newListener)

    
    def applyParry(self, target, reverse=False, attacker=None):
        #if target.facingAttacker() TODO
        tRank = Trait.getTraitRank(target, "Parry")
        if not reverse:
            if tRank == 1:
                target.statusDodge += 2
            elif tRank == 2:
                target.statusDodge += 4
            elif tRank == 3:
                target.statusDodge += 6
            elif tRank == 4:
                target.statusDodge += 11
        else:
            if tRank == 1:
                target.statusDodge -= 2
            elif tRank == 2:
                target.statusDodge -= 4
            elif tRank == 3:
                target.statusDodge -= 6
            elif tRank == 4:
                target.statusDodge -= 11

    
    def applyPreparation(self, target, reverse=False, other=None):
        if target.attacksPerformed[0] > 0:
            return
        tRank = Trait.getTraitRank(target, "Preparation")
        if not reverse:
            if tRank == 1:
                target.statusMeleeAccuracy += 8
                target.statusRangedAccuracy += 8
            elif tRank == 2:
                target.statusMeleeAccuracy += 11
                target.statusRangedAccuracy += 11
            elif tRank == 3:
                target.statusMeleeAccuracy += 14
                target.statusRangedAccuracy += 14
            elif tRank == 4:
                target.statusMeleeAccuracy += 18
                target.statusRangedAccuracy += 18
        else:
            if tRank == 1:
                target.statusMeleeAccuracy -= 8
                target.statusRangedAccuracy -= 8
            elif tRank == 2:
                target.statusMeleeAccuracy -= 11
                target.statusRangedAccuracy -= 11
            elif tRank == 3:
                target.statusMeleeAccuracy -= 14
                target.statusRangedAccuracy -= 14
            elif tRank == 4:
                target.statusMeleeAccuracy -= 18
                target.statusRangedAccuracy -= 18

    
    def applyTank(self, target, reverse=False, other=None):
        if not target.usingArmor("Heavy"):
            return
        tRank = Trait.getTraitRank(target, "Tank")
        if not reverse:
            if tRank == 1:
                target.statusDR += 1
            elif tRank == 2:
                target.statusDR += 2
            elif tRank == 3:
                target.statusDR += 4
            elif tRank == 4:
                target.statusDR += 7
        else:
            if tRank == 1:
                target.statusDR -= 1
            elif tRank == 2:
                target.statusDR -= 2
            elif tRank == 3:
                target.statusDR -= 4
            elif tRank == 4:
                target.statusDR -= 7

    
    def applyFencer(self, target, reverse=False, other=None):
        if not target.usingArmor("Medium"):
            return
        tRank = Trait.getTraitRank(target, "Fencer")
        if not reverse:
            if tRank == 1:
                target.statusMeleeAccuracy += 2
            elif tRank == 2:
                target.statusMeleeAccuracy += 4
            elif tRank == 3:
                target.statusMeleeAccuracy += 6
            elif tRank == 4:
                target.statusMeleeAccuracy += 9
        else:
            if tRank == 1:
                target.statusMeleeAccuracy -= 2
            elif tRank == 2:
                target.statusMeleeAccuracy -= 4
            elif tRank == 3:
                target.statusMeleeAccuracy -= 6
            elif tRank == 4:
                target.statusMeleeAccuracy -= 9

    
    def applyShieldResilience(self, target, reverse=False, other=None):
        if not target.usingShield("Any"):
            return
        tRank = Trait.getTraitRank(target, "Shield Resilience")
        if not reverse:
            if tRank == 1:
                target.knockbackResistance += 30
                target.statusRangedDodge += 1
            elif tRank == 2:
                target.knockbackResistance += 60
                target.statusRangedDodge += 2
            elif tRank == 3:
                target.knockbackResistance += 90
                target.statusRangedDodge += 3
            elif tRank == 4:
                target.knockbackResistance += 100
                target.statusRangedDodge += 4
        else:
            if tRank == 1:
                target.knockbackResistance -= 30
                target.statusRangedDodge -= 1
            elif tRank == 2:
                target.knockbackResistance -= 60
                target.statusRangedDodge -= 2
            elif tRank == 3:
                target.knockbackResistance -= 90
                target.statusRangedDodge -= 3
            elif tRank == 4:
                target.knockbackResistance -= 100
                target.statusRangedDodge -= 4

    
    def applyBully(self, target, reverse=False, victim=None):
        if not target.usingWeaponStyle("Two-Handed") or victim.size == "Large" or victim.size == "Huge":
            return
        tRank = Trait.getTraitRank(target, "Bully")
        if not reverse:
            if tRank == 1:
                target.statusForce += 5
                target.statusMeleeAccuracy += 2
                target.statusRangedAccuracy += 2
                target.statusCriticalChance += 0.5
            elif tRank == 2:
                target.statusForce += 10
                target.statusMeleeAccuracy += 3
                target.statusRangedAccuracy += 3
                target.statusCriticalChance += 1
            elif tRank == 3:
                target.statusForce += 15
                target.statusMeleeAccuracy += 4
                target.statusRangedAccuracy += 4
                target.statusCriticalChance += 1.5
            elif tRank == 4:
                target.statusForce += 25
                target.statusMeleeAccuracy += 5
                target.statusRangedAccuracy += 5
                target.statusCriticalChance += 2
        else:
            if tRank == 1:
                target.statusForce -= 5
                target.statusMeleeAccuracy -= 2
                target.statusRangedAccuracy -= 2
                target.statusCriticalChance -= 0.5
            elif tRank == 2:
                target.statusForce -= 10
                target.statusMeleeAccuracy -= 3
                target.statusRangedAccuracy -= 3
                target.statusCriticalChance -= 1
            elif tRank == 3:
                target.statusForce -= 15
                target.statusMeleeAccuracy -= 4
                target.statusRangedAccuracy -= 4
                target.statusCriticalChance -= 1.5
            elif tRank == 4:
                target.statusForce -= 25
                target.statusMeleeAccuracy -= 5
                target.statusRangedAccuracy -= 5
                target.statusCriticalChance -= 2

    
    def applyBoldness(self, target, reverse=False, victim=None):
        if victim.size == "Small" or victim.size == "Medium":
            return
        tRank = Trait.getTraitRank(target, "Boldness")
        if not reverse:
            if victim.size == "Large":
                if tRank == 1:
                    target.statusForce += 5
                if tRank == 2:
                    target.statusForce += 10
                if tRank == 3:
                    target.statusForce += 15
                if tRank == 4:
                    target.statusForce += 20
            elif victim.size == "Huge":
                if tRank == 1:
                    target.statusForce += 15
                if tRank == 2:
                    target.statusForce += 30
                if tRank == 3:
                    target.statusForce += 45
                if tRank == 4:
                    target.statusForce += 60
        else:
            if victim.size == "Large":
                if tRank == 1:
                    target.statusForce -= 5
                if tRank == 2:
                    target.statusForce -= 10
                if tRank == 3:
                    target.statusForce -= 15
                if tRank == 4:
                    target.statusForce -= 20
            elif victim.size == "Huge":
                if tRank == 1:
                    target.statusForce -= 15
                if tRank == 2:
                    target.statusForce -= 30
                if tRank == 3:
                    target.statusForce -= 45
                if tRank == 4:
                    target.statusForce -= 60

    
    def applyWellTraveled(self, target):
        tRank = Trait.getTraitRank(target, "Well-Traveled")
        if tRank == 1:
            target._baseInventoryCapacity += 15
            target.baseFireResistance += 1
            target.baseColdResistance += 1
        if tRank == 2:
            target._baseInventoryCapacity += 15
            target.baseFireResistance += 1
            target.baseColdResistance += 1
        if tRank == 3:
            target._baseInventoryCapacity += 15
            target.baseFireResistance += 1
            target.baseColdResistance += 1
        if tRank == 4:
            target._baseInventoryCapacity += 25
            target.baseFireResistance += 2
            target.baseColdResistance += 2

    
    def applyHammerAndAnvil(self, target, reverse=False, victim=None):
        # TODO: if target has back against wall...
        tRank = Trait.getTraitRank(target, "Hammer and Anvil")
        if not reverse:
            if tRank == 1:
                target.baseOverallDamageBonus += 5
            elif tRank == 2:
                target.baseOverallDamageBonus += 10
            elif tRank == 3:
                target.baseOverallDamageBonus += 15
            elif tRank == 4:
                target.baseOverallDamageBonus += 20
        else:
            if tRank == 1:
                target.baseOverallDamageBonus -= 5
            elif tRank == 2:
                target.baseOverallDamageBonus -= 10
            elif tRank == 3:
                target.baseOverallDamageBonus -= 15
            elif tRank == 4:
                target.baseOverallDamageBonus -= 20

    # Ranger
    
    def applyWoundingProjectiles(self, target, reverse=False, victim=None):
        tRank = Trait.getTraitRank(target, "Wounding Projectiles")
        chance = None
        magnitude = None
        duration = 2
        if tRank == 1:
            chance = 10
            magnitude = 5
        elif tRank == 2:
            chance = 12
            magnitude = 6
        elif tRank == 3:
            chance = 15
            magnitude = 7
        elif tRank == 4:
            chance = 18
            magnitude = 8
        if Dice.rollBeneath(chance):
            Combat.addStatus(victim, "Wounding Projectiles", duration, magnitude)

    
    def applyMeleeArcheryStatic(self, target):
        tRank = Trait.getTraitRank(target, "Melee Archery")
        if tRank == 1:
            target.meleeRangedAttackPenaltyReduction = 50
        elif tRank == 2 or tRank == 3 or tRank == 4:
            target.meleeRangedAttackPenaltyReduction = 100

    
    def applyMeleeArchery(self, target, reverse=False, victim=None):
        if not location.in_melee_range(target.location, victim.location):
            return
        tRank = Trait.getTraitRank(target, "Melee Archery")
        if not reverse:
            if tRank == 1:
                pass
            elif tRank == 2:
                pass
            elif tRank == 3:
                target.statusRangedAccuracy += 4
            elif tRank == 4:
                target.statusRangedAccuracy += 4
                target.statusOverallDamageBonus += 10
        else:
            if tRank == 1:
                pass
            elif tRank == 2:
                pass
            elif tRank == 3:
                target.statusRangedAccuracy -= 4
            elif tRank == 4:
                target.statusRangedAccuracy -= 4
                target.statusOverallDamageBonus -= 10

    
    def applyNatureTraining(self, target):
        tRank = Trait.getTraitRank(target, "Nature Training")
        if tRank == 1:
            target.basePoisonTolerance += 2
            target.basePoisonResistance += 2
        elif tRank == 2:
            target.basePoisonTolerance += 1
            target.basePoisonResistance += 2
        elif tRank == 3:
            target.basePoisonTolerance += 1
            target.basePoisonResistance += 2
        elif tRank == 4:
            target.basePoisonTolerance += 2
            target.basePoisonResistance += 3

    
    def applyExplorer(self, target):
        tRank = Trait.getTraitRank(target, "Explorer")
        if tRank == 1:
            target.baseTrapEvade += 2
            target.baseAwareness += 2
            target.goldFind += 1
        elif tRank == 2:
            target.baseTrapEvade += 1
            target.baseAwareness += 1
            target.goldFind += 1
        elif tRank == 3:
            target.baseTrapEvade += 1
            target.baseAwareness += 1
            target.goldFind += 1
        elif tRank == 4:
            target.baseTrapEvade += 1
            target.baseAwareness += 1
            target.goldFind += 1

    
    def applyTrapsmith(self, target):
        tRank = Trait.getTraitRank(target, "Trapsmith")
        if tRank == 1:
            target.bonusTrapDamage += 5
            target.bonusTrapRating -= 1
        elif tRank == 2:
            target.bonusTrapDamage += 5
            target.bonusTrapRating -= 1
        elif tRank == 3:
            target.bonusTrapDamage += 5
            target.bonusTrapRating -= 1
        elif tRank == 4:
            target.bonusTrapDamage += 5
            # No penalty at this rank

    
    def applyMastermind(self, target, reverse=False, trap=None):
        pass
        # TODO: We need to be able to track the total number of player
        # traps on the combat arena in order to implement this trait.

    
    def applyFollowupExpert(self, target, reverse=False, victim=None):
        duration = 2
        magnitudeAccuracy = None
        magnitudeForce = None
        tRank = Trait.getTraitRank(target, "Follow-up Expert")
        if tRank == 1:
            magnitudeAccuracy = 2
            magnitudeForce = 15
        elif tRank == 2:
            magnitudeAccuracy = 4
            magnitudeForce = 25
        elif tRank == 3:
            magnitudeAccuracy = 6
            magnitudeForce = 35
        elif tRank == 4:
            magnitudeAccuracy = 8
            magnitudeForce = 50
        Combat.addStatus(target, "Follow-up Expert Accuracy", duration, magnitudeAccuracy)
        Combat.addStatus(target, "Follow-up Expert Force", duration, magnitudeForce)

    
    def applyTrapSadism(self, target, reverse=False, trap=None):
        duration = 2
        magnitude = None
        tRank = Trait.getTraitRank(target, "Trap Sadism")
        if tRank == 1:
            magnitude = 15
        elif tRank == 2:
            magnitude = 30
        elif tRank == 3:
            magnitude = 45
        elif tRank == 4:
            magnitude = 65
        Combat.addStatus(target, "Trap Sadism", duration, magnitude)

    # Thief
    
    def applyUncannyEvasion(self, target):
        tRank = Trait.getTraitRank(target, "Uncanny Evasion")
        if tRank == 1:
            target.statusRangedDodge += 3
        elif tRank == 2:
            target.statusRangedDodge += 3
        elif tRank == 3:
            target.statusRangedDodge += 3
        elif tRank == 4:
            target.statusRangedDodge += 3

    
    def applyStealthyDaggers(self, target, reverse=False, victim=None):
        if not target.usingWeapon("Knife"):
            return
        tRank = Trait.getTraitRank(target, "Stealthy Daggers")
        if not reverse:
            if tRank == 1:
                if target.inStealth():
                    target.statusMeleeAccuracy += 3
                else:
                    target.statusMeleeAccuracy += 1
                target.statusOverallDamageBonus += 2
            elif tRank == 2:
                if target.inStealth():
                    target.statusMeleeAccuracy += 6
                else:
                    target.statusMeleeAccuracy += 2
                target.statusOverallDamageBonus += 3
            elif tRank == 3:
                if target.inStealth():
                    target.statusMeleeAccuracy += 9
                else:
                    target.statusMeleeAccuracy += 3
                target.statusOverallDamageBonus += 4
            elif tRank == 4:
                if target.inStealth():
                    target.statusMeleeAccuracy += 12
                else:
                    target.statusMeleeAccuracy += 4
                target.statusOverallDamageBonus += 5
        else:
            if tRank == 1:
                if target.inStealth():
                    target.statusMeleeAccuracy -= 3
                else:
                    target.statusMeleeAccuracy -= 1
                target.statusOverallDamageBonus -= 2
            elif tRank == 2:
                if target.inStealth():
                    target.statusMeleeAccuracy -= 6
                else:
                    target.statusMeleeAccuracy -= 2
                target.statusOverallDamageBonus -= 3
            elif tRank == 3:
                if target.inStealth():
                    target.statusMeleeAccuracy -= 9
                else:
                    target.statusMeleeAccuracy -= 3
                target.statusOverallDamageBonus -= 4
            elif tRank == 4:
                if target.inStealth():
                    target.statusMeleeAccuracy -= 12
                else:
                    target.statusMeleeAccuracy -= 4
                target.statusOverallDamageBonus -= 5

    
    def applyDueling(self, target, reverse=False, other=None):
        if not target.usingWeaponStyle("Single"):
            return
        tRank = Trait.getTraitRank(target, "Dueling")
        if not reverse:
            if tRank == 1:
                target.statusDodge += 1
                target.statusMeleeAccuracy += 1
                target.statusRangedAccuracy += 1
                target.statusCriticalChance += 2
            elif tRank == 2:
                target.statusDodge += 2
                target.statusMeleeAccuracy += 2
                target.statusRangedAccuracy += 2
                target.statusCriticalChance += 4
            elif tRank == 3:
                target.statusDodge += 3
                target.statusMeleeAccuracy += 3
                target.statusRangedAccuracy += 3
                target.statusCriticalChance += 6
            elif tRank == 4:
                target.statusDodge += 5
                target.statusMeleeAccuracy += 5
                target.statusRangedAccuracy += 5
                target.statusCriticalChance += 8
        else:
            if tRank == 1:
                target.statusDodge -= 1
                target.statusMeleeAccuracy -= 1
                target.statusRangedAccuracy -= 1
                target.statusCriticalChance -= 2
            elif tRank == 2:
                target.statusDodge -= 2
                target.statusMeleeAccuracy -= 2
                target.statusRangedAccuracy -= 2
                target.statusCriticalChance -= 4
            elif tRank == 3:
                target.statusDodge -= 3
                target.statusMeleeAccuracy -= 3
                target.statusRangedAccuracy -= 3
                target.statusCriticalChance -= 6
            elif tRank == 4:
                target.statusDodge -= 5
                target.statusMeleeAccuracy -= 5
                target.statusRangedAccuracy -= 5
                target.statusCriticalChance -= 8

    
    def applyTwoWeaponFighting(self, target, reverse=False, other=None):
        if not target.usingWeaponStyle("Dual"):
            return
        tRank = Trait.getTraitRank(target, "Two-Weapon Fighting")
        if not reverse:
            if tRank == 1:
                target.statusCriticalMagnitude += 5
            elif tRank == 2:
                target.statusCriticalMagnitude += 8
            elif tRank == 3:
                target.statusCriticalMagnitude += 10
            elif tRank == 4:
                target.statusCriticalMagnitude += 13
        else:
            if tRank == 1:
                target.statusCriticalMagnitude -= 5
            elif tRank == 2:
                target.statusCriticalMagnitude -= 8
            elif tRank == 3:
                target.statusCriticalMagnitude -= 10
            elif tRank == 4:
                target.statusCriticalMagnitude -= 13

    
    def applyClever(self, target):
        tRank = Trait.getTraitRank(target, "Clever")
        if tRank == 1:
            target.baseMagicResist += 2
        elif tRank == 2:
            target.baseMagicResist += 2
        elif tRank == 3:
            target.baseMagicResist += 2
        elif tRank == 4:
            target.baseMagicResist += 2

    
    def applyLucky(self, target):
        tRank = Trait.getTraitRank(target, "Lucky")
        if tRank == 1:
            target.baseTrapEvade += 5
            target.baseCriticalChance += 0.5
        elif tRank == 2:
            target.baseTrapEvace += 2
            target.baseCriticalChance += 0.5
        elif tRank == 3:
            target.baseTrapEvace += 2
            target.baseCriticalChance += 0.5
        elif tRank == 4:
            target.baseTrapEvace += 2
            target.baseCriticalChance += 0.5

    
    def applyDiscerningEyes(self, target):
        tRank = Trait.getTraitRank(target, "Discerning Eyes")
        if tRank == 1:
            target.baseAwareness += 5
            target.trapDisarmBonus += 1
        elif tRank == 2:
            target.baseAwareness += 2
            target.trapDisarmBonus += 1
        elif tRank == 3:
            target.baseAwareness += 2
            target.trapDisarmBonus += 1
        elif tRank == 4:
            target.baseAwareness += 2
            target.trapDisarmBonus += 1

    
    def applyTreasureHunter(self, target):
        tRank = Trait.getTraitRank(target, "Treasure Hunter")
        if tRank == 1:
            target.goldFind += 2
        elif tRank == 2:
            target.goldFind += 1
        elif tRank == 3:
            target.goldFind += 2
        elif tRank == 4:
            target.goldFind += 3

    
    def applyDilatant(self, target):
        tRank = Trait.getTraitRank(target, "Dilatant")
        if tRank == 1:
            target.baseHP += 3
            target.baseCarryingCapacity += 5
            target.baseAwareness += 1
            target.baseShadowResistance += 1
        elif tRank == 2:
            target.baseHP += 3
            target.baseCarryingCapacity += 5
            target.baseAwareness += 2
            target.baseShadowResistance += 1
        elif tRank == 3:
            target.baseHP += 3
            target.baseCarryingCapacity += 5
            target.baseShadowResistance += 1
        elif tRank == 4:
            target.baseHP += 5
            target.baseCarryingCapacity += 10
            target.baseAwareness += 2
            target.baseShadowResistance += 2

    # Wizard
    
    def applyReservoir(self, target):
        tRank = Trait.getTraitRank(target, "Reservoir")
        if tRank == 1:
            target.baseMP += 10
        elif tRank == 2:
            target.baseMP += 5
        elif tRank == 3:
            target.baseMP += 5
        elif tRank == 4:
            target.baseMP += 5

    
    def applySurvivor(self, target):
        tRank = Trait.getTraitRank(target, "Survivor")
        if tRank == 1:
            target.baseHP += 4
        elif tRank == 2:
            target.baseHP += 4
        elif tRank == 3:
            target.baseHP += 4
        elif tRank == 4:
            target.baseHP += 4

    
    def applyIllusionSpellFocusStatic(self, target):
        tRank = Trait.getTraitRank(target, "Illusion Spell Focus")
        if tRank == 1:
            pass
        elif tRank == 2:
            target.illusionResist += 1
        elif tRank == 3:
            target.illusionResist += 1
        elif tRank == 4:
            target.illusionResist += 2

    
    def applyIllusionSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Illusion":
            return
        tRank = Trait.getTraitRank(target, "Illusion Spell Focus")
        if not reverse:
            if tRank == 1:
                Combat.modifyResource(target, "MP", 1)
                target.statusSpellpower += 1
            elif tRank == 2:
                Combat.modifyResource(target, "MP", 1)
                target.statusSpellpower += 2
            elif tRank == 3:
                Combat.modifyResource(target, "MP", 2)
                target.statusSpellpower += 3
            elif tRank == 4:
                Combat.modifyResource(target, "MP", 2)
                target.statusSpellpower += 5
        else:
            if tRank == 1:
                target.statusSpellpower -= 1
            elif tRank == 2:
                target.statusSpellpower -= 2
            elif tRank == 3:
                target.statusSpellpower -= 3
            elif tRank == 4:
                target.statusSpellpower -= 5

    
    def applyPrimalSpellFocusStatic(self, target):
        tRank = Trait.getTraitRank(target, "Primal Spell Focus")
        if tRank == 1:
            target.baseMP += 1
        elif tRank == 2:
            target.baseMP += 1
            target.primalResist += 1
        elif tRank == 3:
            target.baseMP += 1
        elif tRank == 4:
            target.baseMP += 2
            target.primalResist += 2

    
    def applyPrimalSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Primal":
            return
        tRank = Trait.getTraitRank(target, "Primal Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 2
            if tRank == 2:
                target.statusSpellpower += 4
            if tRank == 3:
                target.statusSpellpower += 6
            if tRank == 4:
                target.statusSpellpower += 8
        else:
            if tRank == 1:
                target.statusSpellpower -= 2
            if tRank == 2:
                target.statusSpellpower -= 4
            if tRank == 3:
                target.statusSpellpower -= 6
            if tRank == 4:
                target.statusSpellpower -= 8

    
    def applyNaturalSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Natural":
            return
        tRank = Trait.getTraitRank(target, "Natural Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 1
                target.healingBonus += 5
            elif tRank == 2:
                target.statusSpellpower += 2
                target.healingBonus += 10
            elif tRank == 3:
                target.statusSpellpower += 3
                target.healingBonus += 15
            elif tRank == 4:
                target.statusSpellpower += 4
                target.healingBonus += 20
        else:
            if tRank == 1:
                target.statusSpellpower -= 1
                target.healingBonus -= 5
            elif tRank == 2:
                target.statusSpellpower -= 2
                target.healingBonus -= 10
            elif tRank == 3:
                target.statusSpellpower -= 3
                target.healingBonus -= 15
            elif tRank == 4:
                target.statusSpellpower -= 4
                target.healingBonus -= 20

    
    def applyMysticSpellFocusStatic(self, target):
        tRank = Trait.getTraitRank(target, "Mystic Spell Focus")
        if tRank == 1:
            target.mysticResist += 1
        elif tRank == 2:
            target.mysticResist += 1
        elif tRank == 3:
            target.mysticResist += 1
        elif tRank == 4:
            target.mysticResist += 1

    
    def applyMysticSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Mystic":
            return
        tRank = Trait.getTraitRank(target, "Mystic Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 2
            elif tRank == 2:
                target.statusSpellpower += 4
            elif tRank == 3:
                target.statusSpellpower += 6
            elif tRank == 4:
                target.statusSpellpower += 8
        else:
            if tRank == 1:
                target.statusSpellpower -= 2
            elif tRank == 2:
                target.statusSpellpower -= 4
            elif tRank == 3:
                target.statusSpellpower -= 6
            elif tRank == 4:
                target.statusSpellpower -= 8

    
    def applyBaneSpellFocusStatic(self, target):
        tRank = Trait.getTraitRank(target, "Bane Spell Focus")
        if tRank == 1:
            target.baseShadowBonusDamage += 7
        elif tRank == 2:
            target.baseShadowBonusDamage += 7
        elif tRank == 3:
            target.baseShadowBonusDamage += 7
        elif tRank == 4:
            target.baseShadowBonusDamage += 7

    
    def applyBaneSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Bane":
            return
        tRank = Trait.getTraitRank(target, "Bane Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 1
            elif tRank == 2:
                target.statusSpellpower += 2
            elif tRank == 3:
                target.statusSpellpower += 3
            elif tRank == 4:
                target.statusSpellpower += 4
        else:
            if tRank == 1:
                target.statusSpellpower -= 1
            elif tRank == 2:
                target.statusSpellpower -= 2
            elif tRank == 3:
                target.statusSpellpower -= 3
            elif tRank == 4:
                target.statusSpellpower -= 4

    
    def applyEnchantmentSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Enchantment":
            return
        tRank = Trait.getTraitRank(target, "Enchantment Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 1
                Combat.modifyResource(target, "MP", 1)
            elif tRank == 2:
                target.statusSpellpower += 2
                Combat.modifyResource(target, "MP", 2)
            elif tRank == 3:
                target.statusSpellpower += 4
                Combat.modifyResource(target, "MP", 2)
            elif tRank == 4:
                target.statusSpellpower += 5
                Combat.modifyResource(target, "MP", 3)
        else:
            if tRank == 1:
                target.statusSpellpower -= 1
            elif tRank == 2:
                target.statusSpellpower -= 2
            elif tRank == 3:
                target.statusSpellpower -= 4
            elif tRank == 4:
                target.statusSpellpower -= 5

    def applyMentalSpellFocusStatic(self, target):
        tRank = Trait.getTraitRank(target, "Mental Spell Focus")
        if tRank == 1:
            target.baseHP += 2
        elif tRank == 2:
            target.baseHP += 2
        elif tRank == 3:
            target.baseHP += 2
        elif tRank == 4:
            target.baseHP += 2

    
    def applyMentalSpellFocus(self, target, reverse=False, spell=None):
        if spell.school != "Mental":
            return
        tRank = Trait.getTraitRank(target, "Mental Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 2
            elif tRank == 2:
                target.statusSpellpower += 4
            elif tRank == 3:
                target.statusSpellpower += 6
            elif tRank == 4:
                target.statusSpellpower += 8
        else:
            if tRank == 1:
                target.statusSpellpower -= 2
            elif tRank == 2:
                target.statusSpellpower -= 4
            elif tRank == 3:
                target.statusSpellpower -= 6
            elif tRank == 4:
                target.statusSpellpower -= 8



    allContentByName = {
        # Fighter Traits
        'Parry':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyParry,
            'onStringList' : ['Incoming Melee Attack'],
            'offStringList' : ['Incoming Melee Attack Complete']
            },
        'Preparation':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyPreparation,
            'onStringList' : ['Starting Player Turn'],
            'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            },
        'Tank':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyTank,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            },
        'Fencer':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyFencer,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            },
        'Shield Resilience':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyShieldResilience,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            },
        'Bully':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyBully,
            'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            },
        'Boldness':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyBoldness,
            'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
            'offStringList' : ['Outoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            },
        'Well-Traveled':
            {
            'class' : 'Fighter',
            'type' : 'static',
            'action' : applyWellTraveled,
            },
        'Hammer and Anvil':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyHammerAndAnvil,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            },

        # Ranger Traits
        'Wounding Projectiles':
            {
            'class' : 'Ranger',
            'type' : 'dynamic',
            'action' : applyWoundingProjectiles,
            'onStringList' : ['Outgoing Ranged Attack Normal Hit', 'Outgoing Ranged Attack Critical Hit'],
            'offStringList' : []
            },
        'Melee Archery':
            {
            'class' : 'Ranger',
            'type' : 'dynamic and static',
            'action' : applyMeleeArchery,
            'onStringList' : ['Outgoing Ranged Attack'],
            'offStringList' : ['Outgoing Ranged Attack Complete'],
            'staticAction' : applyMeleeArcheryStatic
            },
        'Nature Training':
            {
            'class' : 'Ranger',
            'type' : 'static',
            'action' : applyNatureTraining,
            },
        'Explorer':
            {
            'class' : 'Ranger',
            'type' : 'static',
            'action' : applyExplorer
            },
        'Trapsmith':
            {
            'class' : 'Ranger',
            'type' : 'static',
            'action' : applyTrapsmith
            },
        'Mastermind':
            {
            'class' : 'Ranger',
            'type' : 'dynamic',
            'action' : applyMastermind,
            'onStringList' : ['Monster Triggered Trap Complete'],
            'offStringList' : ['Player Trap Removed']
            },
        'Follow-up Expert':
            {
            'class' : 'Ranger',
            'type' : 'dynamic',
            'action' : applyFollowupExpert,
            'onStringList' : ['Outgoing Melee Attack Hit', 'Outgoing Melee Attack Critical Hit'],
            'offStringList' : []
            },
        'Trap Sadism':
            {
            'class' : 'Ranger',
            'type' : 'dynamic',
            'action' : applyTrapSadism,
            'onStringList' : ['Monster Hit By Trap Complete'],
            'offStringList' : []
            },

        # Thief Traits
        'Uncanny Evasion':
            {
            'class' : 'Thief',
            'type' : 'static',
            'action' : applyUncannyEvasion
            },
        'Stealthy Daggers':
            {
            'class' : 'Thief',
            'type' : 'dynamic',
            'action' : applyStealthyDaggers,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            },
        'Dueling':
            {
            'class' : 'Thief',
            'type' : 'dynamic',
            'action' : applyDueling,
            'onStringList' : ['Outgoing Ranged Attack', 'Outgoing Melee Attack', 'Incoming Ranged Attack', 'Incoming Melee Attack'],
            'offStringList' : ['Outgoing Ranged Attack Complete', 'Outgoing Melee Attack Complete', 'Incoming Ranged Attack Complete', 'Incoming Melee Attack Complete']
            },
        'Two-Weapon Fighting':
            {
            'class' : 'Thief',
            'type' : 'dynamic',
            'action' : applyTwoWeaponFighting,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            },
        'Clever':
            {
            'class' : 'Thief',
            'type' : 'static',
            'action' : applyClever
            },
        'Lucky':
            {
            'class' : 'Thief',
            'type' : 'static',
            'action' : applyLucky
            },
        'Discerning Eyes':
            {
            'class' : 'Thief',
            'type' : 'static',
            'action' : applyDiscerningEyes
            },
        'Treasure Hunter':
            {
            'class' : 'Thief',
            'type' : 'static',
            'action' : applyTreasureHunter
            },
        'Dilatant':
            {
            'class' : 'Thief',
            'type' : 'static',
            'action' : applyDilatant
            },

        # Wizard Traits
        'Reservoir':
            {
            'class' : 'Wizard',
            'type' : 'static',
            'action' : applyReservoir,
            'image' : WIZARD + 'reservoir.png',
            'text' : 'Gain a permanent bonus to your maximum mana.\n' + \
                    'Rank I:   +10 Max MP\n' + \
                    'Rank II:  +15 Max MP\n' + \
                    'Rank III: +20 Max MP\n' + \
                    'Rank IV:  +25 Max MP\n'
            },
        'Survivor':
            {
            'class' : 'Wizard',
            'type' : 'static',
            'action' : applySurvivor,
            'image' : WIZARD + 'survivor.png',
            'text' : 'Gain a permanent bonus to your maximum health.\n' + \
                    'Rank I:   +4 Max HP\n' + \
                    'Rank II:  +8 Max HP\n' + \
                    'Rank III: +12 Max HP\n' + \
                    'Rank IV:  +16 Max HP\n' 
            },
        'Illusion Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyIllusionSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyIllusionSpellFocusStatic,
            'image' : WIZARD + 'illusion-spell-focus.png',
            'text' : 'Gain various benefits to casting Illusion spells.\n' + \
                    'Rank I:   Illusion spells refund 1 MP, +1 Spellpower\n' + \
                    'Rank II:  Illusion spells refund 1 MP, +2 Spellpower; +1 Magic resist vs. Illusion\n' + \
                    'Rank III: Illusion spells refund 2 MP, +3 Spellpower; +2 Magic resist vs. Illusion\n' + \
                    'Rank IV:  Illusion spells refund 2 MP, +5 Spellpower; +4 Magic resist vs. Illusion'
            },
        'Primal Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyPrimalSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyPrimalSpellFocusStatic,
            'image' : WIZARD + 'primal-spell-focus.png',
            'text' : 'Gain various benefits to casting Primal spells.\n' + \
                    'Rank I:   +2 Spellpower; +1 Max MP\n' + \
                    'Rank II:  +4 Spellpower; +2 Max MP, +1 Magic resist vs. Primal\n' + \
                    'Rank III: +6 Spellpower; +3 Max MP, +2 Magic resist vs. Primal\n' + \
                    'Rank IV:  +8 Spellpower; +5 Max MP, +4 Magic resist vs. Primal'
            },
        'Natural Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic',
            'action' : applyNaturalSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'image' : WIZARD + 'natural-spell-focus.png',
            'text' : 'Gain various benefits to casting Natural spells.\n' + 
                    'Rank I:   +1 Spellpower, +5% healing\n' + \
                    'Rank II:  +2 Spellpower, +10% healing\n' + \
                    'Rank III: +3 Spellpower, +15% healing\n' + \
                    'Rank IV:  +4 Spellpower, +20% healing'
            },
        'Mystic Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyMysticSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyMysticSpellFocusStatic,
            'image' : WIZARD + 'mystic-spell-focus.png',
            'text' : 'Gain various benefits to casting Mystic spells.\n' + \
                    'Rank I:   +2 Spellpower; +1 Magic resist vs. Mystic\n' + \
                    'Rank II:  +4 Spellpower; +2 Magic resist vs. Mystic\n' + \
                    'Rank III: +6 Spellpower; +3 Magic resist vs. Mystic\n' + \
                    'Rank IV:  +8 Spellpower; +4 Magic resist vs. Mystic'
            },
        'Bane Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyBaneSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyBaneSpellFocusStatic,
            'image' : WIZARD + 'bane-spell-focus.png',
            'text' : 'Gain various benefits to casting Bane spells.\n' + \
                    'Rank I:   +1 Spellpower; +7% Shadow Damage\n' + \
                    'Rank II:  +2 Spellpower; +14% Shadow Damage\n' + \
                    'Rank III: +3 Spellpower; +21% Shadow Damage\n' + \
                    'Rank IV:  +4 Spellpower; +28% Shadow Damage'
            },
        'Enchantment Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic',
            'action' : applyEnchantmentSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'image' : WIZARD + 'enchantment-spell-focus.png',
            'text' : 'Gain various benefits to casting enchantment spells\n' + \
                    'Rank I:   +1 Spellpower, Enchantment spells refund 1 MP\n' + \
                    'Rank II:  +2 Spellpower, Enchantment spells refund 2 MP\n' + \
                    'Rank III: +4 Spellpower, Enchantment spells refund 2 MP\n' + \
                    'Rank IV:  +5 Spellpower, Enchantment spells refund 3 MP'
            },
        'Mental Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyMentalSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyMentalSpellFocusStatic,
            'image' : WIZARD + 'mental-spell-focus.png',
            'text' : 'Gain spellpower when casting mental spells and bonus HP.\n' + \
                    'Rank I:   +2 Spellpower, +2 HP\n' + \
                    'Rank II:  +4 Spellpower, +4 HP\n' + \
                    'Rank III: +6 Spellpower, +6 HP\n' + \
                    'Rank IV:  +8 Spellpower, +8 HP'     
            }
    }

