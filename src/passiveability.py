#!/usr/bin/python

import sys
import listener
from combat import *

ROOT_FOLDER = "./res/images/icons/"

ARCANE_ARCHER = ROOT_FOLDER + "arcane_archer_skills/"
ASSASSIN = ROOT_FOLDER + "assassin_skills/"
BATTLEMAGE = ROOT_FOLDER + "battlemage_skills/"
BARBARIAN = ROOT_FOLDER + "barbarian_skills/"
NIGHTBLADE = ROOT_FOLDER + "nightblade_skills/"
SPELLSWORD = ROOT_FOLDER + "spellsword_skills/"

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
                target.baseMeleeAccuracy += 2
        else:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy -= 2

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
            healing = round(target.totalHP * 0.05)
            Combat.healTarget(target, healing)
            Combat.addStatus(target, "Stunning Recovery", duration=1)

    # Dragoon

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
                for buff in [x for x in target.statusList if x.name == spell.name]:
                    buff.turnsLeft += 1
        # Has no reverse.

    def applyFocalPoint(self, target, reverse=False, other=None):
        if not target.usingWeaponStyle("Two Handed"):
            return
        eStatus = None
        for s in target.statusList:
            if "Enchantment" in s.categoryList:
                eStatus = s
        if not eStatus:
            return
        else:
            holyDamage = (round(15 * (1 + target.totalDivineBonusDamage / 100) *
                                     (1 - other.totalDivineResistance / 100)))
            Combat.lowerHP(other, holyDamage)

    def applyBladesOfReduction(self, target, reverse=False, victim=None):
        if not target.usingWeapon("Sword") and not target.usingWeapon("Axe"):
            return
        doApply = Dice.rollPresetChance(target, victim, "Reliable")
        if doApply:
            duration = -1 # Never ends
            Combat.applyStatus(victim, "Blades of Reduction", duration)

    # Marksman
    def applyExcellentVision(self, target):
        target._bonusRange += 2
        target.baseAwareness += 2

    def applyLayingInWait(self, target, reverse=False):
        source = self.owner
        if not reverse:
            # If no moves last turn TODO
            mag = (source.getStatusStackCount("Laying in Wait") + 1) * 2
            Combat.addStatus(source, "Laying in Wait", duration=-1, magnitude=mag, overwrite=False)
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
                source.statusRangedAccuracy += 1
        else:
            if source.usingWeapon("Shortbow"):
                source.statusCriticalMagnitude -= 10
                source.statusRangedAccuracy -= 1

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
        if not reverse:
            #if back not against wall, TODO
            source.statusDodge += 3
        else:
            # if back not against wall
            source.statusDodge -= 3

    def applyTreasureBag(self, target):
        target.baseInventoryCapacity += 15

    def applyAnEyeForValue(self, target):
        target.goldFind += 2

    def applySlingSkills(self, target, reverse=False, other=None):
        source = self.target
        if not reverse:
            if source.usingWeapon("Sling"):
                source.statusRangedAccuracy += 5
        else:
            if source.usingWeapon("Sling"):
                source.statusRangedAccuracy -= 5

    def applyHideInPeril(self, target, reverse=False, amount=None):
        source = self.target
        if amount >= source.totalHP * 0.4 and not source.inStealth():
            Combat.addStatus(source, "Shadow Walk", -1)

    def applyBackstabUpgrade(self, target):
        toRemove = None
        for abil in target.abilities:
            if abil.name == "Backstab":
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
                source.statusMeleeAccuracy += 3
                source.statusCriticalChance += 5
        else:
            if source.usingWeaponStyle("Single"):
                source.statusMeleeAccuracy -= 3
                source.statusCriticalChance -= 5

    def applyUpCloseAndPersonal(self, target, reverse=False, spell=None):
        source = self.owner
        if not reverse:
            if spell.school == "Bane" and location.in_melee_range(source.location, target.location):
                source.statusSpellpower += 4
        else:
            if spell.school == "Bane" and location.in_melee_range(source.location, target.location):
                source.statusSpellpower -= 4

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
                target.overrideMovementAPCost = 2
        else:
            target.overrideMovementAPCost = -1

    def applyMilitaryDefensiveTraining(self, target, reverse=False, other=None):
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

    def applyMilitaryOffensiveTraining(self, target, reverse=False, spell=None):
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
        target.baseDodge += 12

    def applyGlee(self, target, reverse=False):
        source = self.owner
        source.MP += source.level * 2 + 18

    def applyInfuriatingBlows(self, target, reverse=False, other=None):
        source = self.owner
        source.MP += 2

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

    # Monsters

    def applyDeflectMissiles(self, target, reverse=False, hero=None):
        ''' Monsters with Deflect Missiles gain 10 Dodge and 5% DR against Ranged
        attacks.'''
        source = self.owner
        if not reverse:
            source.statusDR += 5
            source.statusDodge += 10
        else:
            source.statusDR -= 5
            source.statusDodge -= 10

    def applyGrowingBoldness(self, target, reverse=False, hero=None):
        ''' Monsters with Growing Boldness gain +2 Strength and 1% attack power after
        every attempt to attack in melee. '''
        source = self.owner
        source.statusStrength += 2
        source.attackPower += 1

    def applyMonsterAgility(self, target):
        ''' Monsters with 'Monster Agility' have +10-30 Dodge (based on level). '''
        target.baseDodge += target.level + 10

    def applyPanic(self, target, reverse=False, hero=None):
        ''' Monsters that Panic gain Dexterity (increasing their accuracy and
        dodge) every time they are hit with melee attacks when at half health
        or lower.  Lasts the entire battle and stacks. '''
        source = self.owner
        if source.HP <= 0.5 * source.totalHP:
            source.statusDexterity += 2

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
        'text' : "+2 Accuracy on attacks with two weapons"
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
        'text' : 'Whenever the Barbarian is stunned, he recovers 5% of his\n' + \
                'Maximum HP.  May occur once per monster turn.'
        },

        'Polearm Specialization':
        {
        'class' : 'Dragoon',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyPolearmSpecialization,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
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
                           'Incmoing Melee Attack Complete', 'Incoming Ranged Attack Complete']
        },
        'Fire-Touched':
        {
        'class' : 'Dragoon',
        'level' : 2,
        'type' : 'static',
        'action' : applyFireTouched,
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
                'a target\'s magic resist by 3 with a reliable chance.'
        },

        'Excellent Vision':
        {
        'class' : 'Marksman',
        'level' : 1,
        'type' : 'static',
        'action' : applyExcellentVision
        },
        'Laying in Wait':
        {
        'class' : 'Marksman',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyLayingInWait,
        'onStringList' : ['Player Turn Start'],
        'offStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack']
        },
        'Fire Handler':
        {
        'class' : 'Marksman',
        'level' : 2,
        'type' : 'static',
        'action' : applyFireHandler,
        },
        'Camouflage':
        {
        'class' : 'Marksman',
        'level' : 2,
        'type' : 'static',
        'action' : applyCamouflage
        },
        'Shortbow Niche':
        {
        'class' : 'Marksman',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyShortbowNiche,
        'onStringList' : ['Outgoing Ranged Attack'],
        'offStringList' : ['Outgoing Ranged Attack Complete']
        },
        'Incredible Focus':
        {
        'class' : 'Marksman',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyIncredibleFocus,
        'onStringList' : ['Status Applied'],
        'offStringList' : []
        },
        'Superior Training':
        {
        'class' : 'Marksman',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applySuperiorTraining,
        'onStringList' : ['Incoming Ranged Attack Hit'],
        'offStringList' : []
        },

        'Knowledge of Poison':
        {
        'class' : 'Druid',
        'level' : 1,
        'type' : 'static',
        'action' : applyKnowledgeOfPoison
        },
        'Potency of Poisons':
        {
        'class' : 'Druid',
        'level' : 1,
        'type' : 'static',
        'action' : applyPotencyOfPoisons
        },
        'Exposure to Poison':
        {
        'class' : 'Druid',
        'level' : 1,
        'type' : 'static',
        'action' : applyExposureToPoison
        },
        'Time with Nature':
        {
        'class' : 'Druid',
        'level' : 3,
        'type' : 'static',
        'action' : applyTimeWithNature
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
        'action' : applyAnatomy
        },
        'Slightly Sneakier':
        {
        'class' : 'Assassin',
        'level' : 3,
        'type' : 'static',
        'action' : applySlightlySneakier
        },
        'Dabbles with Poison':
        {
        'class' : 'Assassin',
        'level' : 4,
        'type' : 'static',
        'action' : applyDabblesWithPoison
        },


        # Shadow
        'A Dabbler of Sorts':
        {
        'class' : 'Shadow',
        'level' : 1,
        'type' : 'static',
        'action' : applyADabblerOfSorts
        },
        'Backflip':
        {
        'class' : 'Shadow',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyBackflip,
        'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
        'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
        },
        'Treasure Bag':
        {
        'class' : 'Shadow',
        'level' : 2,
        'type' : 'static',
        'action' : applyTreasureBag
        },
        'An Eye for Value':
        {
        'class' : 'Shadow',
        'level' : 2,
        'type' : 'static',
        'action' : applyAnEyeForValue
        },
        'Backstab Upgrade':
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
        'offStringList' : ['Outgoing Ranged Attack Complete']
        },
        'Hide in Peril':
        {
        'class' : 'Shadow',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyHideInPeril,
        'onStringList' : ['Incmoing Damage'],
        'offStringList' : []
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
        'action' : applyForbiddenStudies
        },
        'Single Blade':
        {
        'class' : 'Nightblade',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applySingleBlade,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
        },
        'Up close and Personal':
        {
        'class' : 'Nightblade',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyUpCloseAndPersonal,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete']
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
        'image' : BATTLEMAGE + 'mystical-accuracy',
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
        'text' : 'If HP is below 20% at the start of your turn, movement only costs 2 AP.'
        },
        'Military Defensive Training':
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
        'Military Spell Training':
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
        'Military Offensive Training':
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
        'offStringList' : ['Outgoing Spell Cast Complete']
        },
        'Arcane Threading Upgrade':
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
        'action' : applyWildSurvival
        },
        'Glee':
        {
        'class' : 'Trickster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyGlee,
        'onStringList' : ['Attack Dodged'],
        'offStringList' : []
        },
        'Infuriating Blows':
        {
        'class' : 'Trickster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyInfuriatingBlows,
        'onStringList' : ['Outgoing Melee Attack Hit', 'Outgoing Ranged Attack Hit'],
        'offStringList' : []
        },
        'Double Dodge':
        {
        'class' : 'Trickster',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyDoubleDodge,
        'onStringList' : ['Attack Dodged'],
        'offStringList' : [] # Removed on status removal.
        },
        'Risky Fighting':
        {
        'class' : 'Trickster',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyRiskyFighting,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
        },
        'Slightly Smugger':
        {
        'class' : 'Trickster',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applySlightlySmugger,
        'onStringList' : ['Attack Dodged'],
        'offStringList' : [] # Removed on status removal
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








