#!/usr/bin/python

import sys
from combat import *
import dice
import command

ROOT_FOLDER = "./res/images/icons/"
TIER1 = ROOT_FOLDER + "tier1_spells/"
TIER2 = ROOT_FOLDER + "tier2_spells/"

class SpellStub(object):
    def __init__(self, name):
        self.name = name
        info = Spell.allSpells[name]
        self.text = 'Fill me in!'
        self.image = './res/images/icons/cubeforce.png'
        cooldownText = '0'
        rangeText = str(info['range'])
        self.school = info['school']
        if info['cooldown']:
            cooldownText = str(info['cooldown'])
        if name in Spell.allSpells:
            info = Spell.allSpells[name]
            if 'text' in info:
                self.text = 'AP: ' + `info['APCost']` + '  MP: ' + `info['MPCost']` + '  Cooldown: ' + cooldownText + '  Range: ' + rangeText + \
                        '  School: ' + self.school + "\n" + info['text']
            if 'image' in info:
                self.image = info['image']


class Spell(object):

    def __init__(self, name, owner):
        self.name = name
        info = None
        if name in Spell.allSpells:
            info = Spell.allSpells[name]
        elif name in Spell.monsterSpells:
            info = Spell.monsterSpells[name]

        self.tier = info['tier']
        self.school = info['school']
        self.MPCost = info['MPCost']
        self.APCost = info['APCost']
        self.range = info['range']
        self.targetType = info['target']
        self.action = info['action']
        self.cooldown = info['cooldown']
        if 'condition' in info:
            self.condition = info['condition']
        else:
            self.condition = None
        if 'image' in info:
            self.image = info['image']
        else:
            self.image = './res/images/icons/cubeforce.png'
        rangeText = str(self.range)
        cooldownText = '0'
        if self.cooldown:
            cooldownText = str(self.cooldown)
        if 'text' in info:
            self.text = 'AP: ' + `self.APCost` + '  MP: ' + `self.MPCost` + '  Cooldown: ' + cooldownText + '  Range: ' + rangeText + \
                        '  School: ' + self.school + "\n" + info['text']
        else:
            self.text = 'No description yet.'
        self.owner = owner
        if 'specialTargeting' in info:
            self.specialTargeting = info['specialTargeting']
        else:
            self.specialTargeting = "DEFAULT"
        if 'radius' in info:
            self.radius = info['radius']
        else:
            self.radius = 0
        if 'placesField' in info:
            self.placesField = info['placesField']
        else:
            self.placesField = False

    def shouldUse(self, target):
        '''
        Used by only monsters to determine if the
        spell should be used.
        '''
        if self.condition is not None:
            return self.condition(self, target)
        else:
            return True

    def canUse(self, target):
        '''
        target: Person (later, Location?)
        '''
        source = self.owner

        mod = 0 # dummy code
        if source.MP < self.MPCost - mod:
            return (False, "Insufficient Mana")
        if source.AP < self.APCost - mod:
            return (False, "Insufficient AP")
        if self.targetType == "self" and source is not target:
            return (False, "Spell is self-only, and the given target is not the caster.")
        if self.targetType == "hostile" and source.team == target.team:
            return (False, "Cannot target own team with hostile spell.")
        if self.targetType == "friendly" and source.team != target.team:
            return (False, "Cannot target hostile with beneficial spell.")
        # Do we need any check for AoE spells?
        if not self.targetType == "location" and not source.inRange(target, self.range):
            return (False, "Target is out of range.")
        if source.onCooldown(self.name) :
            return (False, self.name + " is on Cooldown.")
        return (True, "")


    def use(self, target):
        ''' Casts the given spell on or around the given target Person (or location)
        Performs a check if this is possible, but this is not where the canUse
        check should be made.  If caught here, will print a message to the console.'''
        if self.canUse(target)[0]:
            Combat.modifyResource(self.owner, "MP", -self.MPCost)
            Combat.modifyResource(self.owner, "AP", -self.APCost)
            if self.cooldown:
                Combat.applyCooldown(self.owner, self.name, self.cooldown)
            spellSuccess = Dice.rollSuccess(100 - self.owner.spellFailureChance)
            if spellSuccess:
                hitType = None
                self._shoutSpellCast(self.owner, target)
                if self.targetType == "hostile" and target.team == "Players":
                    self.applySchoolResistance(target)
                    hitType = self.action(self, target)
                    self.unapplySchoolResistance(target)
                else:
                    self.action(self, target)
                if self.owner.team == "Players":
                    self.owner.record.recordSpell()
                if hitType == "Miss" or hitType == "Fully Resisted":
                    self._shoutSpellResisted()
                self._shoutSpellCastComplete(self.owner, target)
                if self.targetType != "friendly" and self.targetType != "self":
                    Combat.removeStealth(self.owner)

            else:
                Combat.sendCombatMessage("Spell Casting Failed! (" + str(self.owner.spellFailureChance) +
                                         "%)", self.owner)
                return

        else:
            print "Caught an unusable spell late!"
            return

    def applySchoolResistance(self, target):
        if self.school == "Enchantment":
            target.statusMagicResist += target.enchantmentResist
        elif self.school == "Bane":
            target.statusMagicResist += target.baneResist
        elif self.school == "Mental":
            target.statusMagicResist += target.mentalResist
        elif self.school == "Illusion":
            target.statusMagicResist += target.illusionResist
        elif self.school == "Primal":
            target.statusMagicResist += target.primalResist
        elif self.school == "Mystic":
            target.statusMagicResist += target.mysticResist
        elif self.school == "Natural":
            target.statusMagicResist += target.naturalResist

    def unapplySchoolResistance(self, target):
        if self.school == "Enchantment":
            target.statusMagicResist -= target.enchantmentResist
        elif self.school == "Bane":
            target.statusMagicResist -= target.baneResist
        elif self.school == "Mental":
            target.statusMagicResist -= target.mentalResist
        elif self.school == "Illusion":
            target.statusMagicResist -= target.illusionResist
        elif self.school == "Primal":
            target.statusMagicResist -= target.primalResist
        elif self.school == "Mystic":
            target.statusMagicResist -= target.mysticResist
        elif self.school == "Natural":
            target.statusMagicResist -= target.naturalResist

    # Status Fields

    @staticmethod
    def _applyZoneOfSilence(target):
        ''' Applys a bonus critical chance and sneak to players only '''
        if target.team == "Players":
            duration = 2 # Immediately decremented
            Combat.addStatus(target, "Zone of Silence", duration)

    @staticmethod
    def _applyPit(target):
        ''' If a player steps on it, it should be removed.'''
        if target.team == "Players":
            Combat.gameServer.pane[target.cPane].fields.remove_field(target.cLocation, "Pit", all=True)
            action = command.Command("FIELD", "REMOVE", name="Pit", location=target.cLocation, all=True)
            Combat.gameServer.broadcast(action, -target.id)

    @staticmethod
    def _applySmokeScreen(target):
        '''Applys bonus dodge but lowers fire resistance to either team'''
        duration = 2 # Immediately decremeneted
        Combat.addStatus(target, "Smoke Screen", duration)


    # Monster Only Spells

    def _shadowField(self, target):
        '''Deals massive shadow damage to a 3x3 area centered on a player.
        Partial Resistance = 33% Damage Dealt.'''
        source = self.owner
        targets = Combat.getAOETargets(source.cPane, target.cLocation, radius=1, selectMonsters=False)
        for tar in targets:
            hitType = Combat.calcHit(source, tar, "Magical")
            damageBase = 11
            damage = Combat.calcDamage(source, tar, damageBase, damageBase * 4, "Shadow", hitValue=hitType,
                                   partial=0.33, scalesWith="Spellpower", scaleFactor=0.02)
            Combat.lowerHP(tar, damage)
        return "Normal Hit" # Return value doesn't matter for monsters.

    # Player & Monster Spells

    def _arcaneDart(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = (Combat.calcDamage(source, target, minimum=2, maximum=4, element="Arcane",
                                    hitValue=hitType, critical=1.25, scalesWith="Spellpower", scaleFactor=0.03))
        Combat.lowerHP(target, damage)
        return hitType

    def _arcaneWard(self, target):
        source = self.owner
        duration = int(Dice.scale(source.totalSpellpower, 3, 0.1, cap=6))
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.01)
        Combat.addStatus(target, self.name, duration, magnitude)
        return "Normal Hit"

    def _mysticShield(self, target):
        source = self.owner
        duration = 5
        magnitude = Dice.scale(source.totalSpellpower, 7, 0.06)
        Combat.addStatus(target, self.name, duration, magnitude)
        return "Normal Hit"

    def _flickerOfLife(self, target):
        source = self.owner
        magnitude = Dice.scale(source.totalSpellpower, Dice.roll(10,20), 0.02)
        Combat.healTarget(source, target, magnitude)
        return "Normal Hit"

    def _flickerOfLifeCheck(self, target):
        ''' Monsters should only cast this if
        HP is at or below 50%.  Should heal self
        if at or below 67%'''
        source = self.owner
        if target == source and target.HP <= target.totalHP * 0.67:
            return True
        elif target.HP <= target.totalHP * 0.50:
            return True
        return False

    def _stoneGuard(self, target):
        source = self.owner
        duration = int(Dice.scale(source.totalSpellpower, 4, 0.05, cap=6))
        magnitude = Dice.scale(source.totalSpellpower, 12, 0.008)
        Combat.addStatus(target, self.name, duration, magnitude)
        return "Normal Hit"

    def _stoneGuardCheck(self, target):
        '''Should only cast a buffing spell if the target doesn't
        already have it.'''
        source = self.owner
        if target.hasStatus("Stone Guard"):
            return False
        return True

    def _singe(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = (Combat.calcDamage(source, target, minimum=2, maximum=10, element="Fire",
                                    hitValue=hitType, critical=1.2, partial=0.5,
                                    scalesWith="Spellpower", scaleFactor=0.05))
        Combat.lowerHP(target, damage)
        return hitType

    def _chill(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, minimum=1, maximum=12, element="Cold",
                                   hitValue=hitType, scalesWith="Spellpower",
                                   scaleFactor=0.01)
        duration = 3
        chance = Dice.rollPresetChance(source, target, "Frequent")
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.012)
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType, chance=chance)
        Combat.lowerHP(target, damage)
        return hitType

    def _shock(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, minimum=15, maximum=22, element="Electric", hitValue=hitType,
                                   scalesWith="Spellpower", scaleFactor=0.014, partial=0.5)
        Combat.lowerHP(target, damage)
        return hitType

    def _suggestLaziness(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        # TODO: this status requires AI -- we don't have that yet.
        return hitType

    def _stutter(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        duration = 5
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.02)
        if hitType != "Miss" and hitType != "Fully Resisted":
            Combat.addStatus(target, self.name, duration, magnitude)
        return hitType

    def _cloudVision(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        duration = int(Dice.scale(source.totalSpellpower, 4, 0.025))
        magnitude = Dice.scale(source.totalSpellpower, 10, 0.012)
        if hitType == "Partially Resisted":
            magnitude /= 2
        if hitType != "Miss" and hitType != "Fully Resisted":
            Combat.addStatus(target, self.name, duration, magnitude)
        return hitType

    def _cloudVisionCheck(self, target):
        ''' Should only cast if target doesn't
        already have the debuff. '''
        source = self.owner
        if target.hasStatus("Cloud Vision"):
            return False
        return True

    def _haunt(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, minimum=13, maximum=20, element="Shadow", hitValue=hitType,
                                   scalesWith="Spellpower", scaleFactor=0.01)
        Combat.lowerHP(target, damage)
        if hitType not in ["Partial Resist", "Partially Resisted", "Miss", "Fully Resisted", "Resisted"]:
            duration = int(Dice.scale(source.totalSpellpower, 3, 0.02, cap=4))
            magnitude = round(Dice.roll(2,8) * (1 + source.totalSpellpower * 0.005))
            Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)
        return hitType

    def _zoneOfSilence(self, target):
        # Target is a location.
        source = self.owner
        duration = min(7, 4 + source.totalSpellpower / 30)
        radius = 1
        Combat.gameServer.pane[source.cPane].fields.add_field("Zone of Silence", target, radius, duration)
        action = command.Command("FIELD", "ADD", name="Zone of Silence", location=target, radius=radius, duration=duration)
        Combat.gameServer.broadcast(action, -source.id)


    def _blurry(self, target):
        source = self.owner
        duration = 1
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.02)
        Combat.addStatus(target, self.name, duration, magnitude)
        return "Normal Hit"

    def _weaponEnhance(self, target):
        source = self.owner
        duration = int(Dice.scale(source.totalSpellpower, 3, 0.03, cap=7))
        magnitudeA = Dice.scale(source.totalSpellpower, 3, 0.07) # Accuracy/Penetration
        magnitudeB = Dice.scale(source.totalSpellpower, 5, 0.05) # Crit mag
        magnitudeC = Dice.scale(source.totalSpellpower, 1, 0.035) # Crit chance
        Combat.addStatus(target, "Weapon Enhance Striking", duration, magnitudeA)
        Combat.addStatus(target, "Weapon Enhance Punishing", duration, magnitudeB)
        Combat.addStatus(target, "Weapon Enhance Precision", duration, magnitudeC)
        return "Normal Hit"

    def _flamingWeapon(self, target):
        source = self.owner
        duration = int(Dice.scale(source.totalSpellpower, 3, 0.03, cap=7))
        magnitude = round(Dice.roll(1,8) * (1 + source.totalSpellpower * 0.01))
        Combat.addStatus(target, self.name, duration, magnitude)
        return "Normal Hit"

    # TIER 2

    def _burst(self, target):
        source = self.owner
        # target is a Location
        centerTargetList = Combat.getAOETargets(source.cPane, target, radius=0)
        if centerTargetList:
            centerTarget = centerTargetList[0]
            hitType = Combat.calcHit(source, centerTarget, "Magical")
            if hitType != "Miss" and hitType != "Fully Resisted":
                damage = Combat.calcDamage(source, centerTarget, 10, 12, "Arcane",
                                           hitValue=hitType, scalesWith="Spellpower",
                                           scaleFactor=0.01)
                Combat.lowerHP(centerTarget, damage)
        allTargetsList = Combat.getAOETargets(source.cPane, target, radius=4)
        allTargetsSorted = sorted(allTargetsList, key=lambda x: x.cLocation.distance(target), reverse=True)
        for tar in allTargetsSorted:
            hitType = Combat.calcHit(source, tar, "Magical")
            if hitType != "Miss" and hitType != "Fully Resisted":
                damage = Combat.calcDamage(source, tar, 5, 6, "Arcane",
                                           hitValue=hitType, scalesWith="Spellpower",
                                           scaleFactor=0.01)
                Combat.lowerHP(tar, damage)
                Combat.knockback(tar, target, distance=1)

    def _identification(self, target):
        source = self.owner
        duration = 3
        Combat.addStatus(source, self.name, duration)
        return "Normal Hit"

    def _hoveringShield(self, target):
        source = self.owner
        duration = 5
        magnitude = 12 + source.totalSpellpower / 10
        Combat.addStatus(target, self.name, duration, magnitude)
        return "Normal Hit"

    def _fright(self, target):
        source = self.owner
        duration = 4
        hitType = Combat.calcHit(source, target, "Magical")
        if hitType != "Miss":
            Combat.addStatus(target, self.name, duration)
        return hitType

    def _infection(self, target):
        source = self.owner
        minDam = int(7 * (1 + source.totalSpellpower * 0.03) *
                           (1 + float(source.totalPoisonBonusDamage) / 100))
        maxDam = int(12 * (1 + source.totalSpellpower * 0.03) *
                           (1 + float(source.totalPoisonBonusDamage) / 100))
        dieRoll = Dice.roll(minDam, maxDam)
        rating = round(35 + 0.4 * source.totalSpellpower)
        duration = 4 + source.totalSpellpower / 20
        hitType = Combat.calcHit(source, target, "Poison Magical", rating=rating)
        if hitType != "Miss" and hitType != "Fully Resisted":
            Combat.addStatus(target, "Infection", duration, dieRoll)
        return hitType

    def _handsOfHealing(self, target):
        source = self.owner
        value = int(Dice.roll(20, 40) * (1 + 0.02 * source.totalSpellpower))
        Combat.healTarget(source, target, value)
        return "Normal Hit"

    def _elementalBoon(self, target):
        source = self.owner
        magnitude = 15 + source.totalSpellpower / 10
        duration = max(7, 6 + source.totalSpellpower / 50)
        Combat.addStatus(target, "Elemental Boon", duration, magnitude)
        return "Normal Hit"

    def _torrent(self, target):
        source = self.owner
        lower = 10
        upper = 35
        knockbackDistance = 5
        newTar = Combat.getLineTargets(target.cPane, source.cLocation, target.cLocation, selectMonsters=True, width=1, selectFirstOnly=True)[0]
        hitType = Combat.calcHit(source, newTar, "Magical")
        if hitType != "Miss" and hitType != "Fully Resisted":
            dam = Combat.calcDamage(source, newTar, lower, upper, "Cold", hitValue=hitType, scalesWith="Spellpower", scaleFactor=0.014)
            Combat.lowerHP(newTar, dam)
            if hitType == "Normal Hit" or hitType == "Critical Hit":
                Combat.knockback(newTar, source.cLocation, knockbackDistance)
        return hitType

    def _lightningBolt(self, target):
        source = self.owner
        lower = 5
        upper = 33
        manyTargets = Combat.getLineTargets(target.cPane, source.cLocation, target.cLocation, selectMonsters=True, width=2)
        for t in manyTargets:
            hitType = Combat.calcHit(source, t, "Magical")
            if hitType != "Miss" and hitType != "Fully Resisted":
                dam = Combat.calcDamage(source, t, lower, upper, "Electric", hitValue=hitType, critical=1.3, partial=0.5,
                                        scalesWith="Spellpower", scaleFactor=0.005)
                Combat.lowerHP(t, dam)
        return hitType

    def _smokeScreen(self, target):
        # Target is a location.
        source = self.owner
        duration = min(7, 3 + source.totalSpellpower / 15)
        radius = 4
        Combat.gameServer.pane[source.cPane].fields.add_field("Smoke Screen", target, radius, duration)
        action = command.Command("FIELD", "ADD", name="Smoke Screen", location=target, radius=radius, duration=duration)
        Combat.gameServer.broadcast(action, -source.id)

    def _pit(self, target):
        # Target is a location.
        source = self.owner
        duration = 4
        radius = 0
        Combat.gameServer.pane[source.cPane].fields.add_field("Pit", target, radius, duration)
        action = command.Command("FIELD", "ADD", name="Pit", location=target, radius=radius, duration=duration)
        Combat.gameServer.broadcast(action, -source.id)

    def _shrink(self, target):
        source = self.owner
        targetList = Combat.getAOETargets(target.cPane, target.cLocation, radius=1)
        wasResisted = False
        for tar in targetList:
            hitType = Combat.calcHit(source, tar, "Magical")
            if hitType != "Miss" and hitType != "Fully Resisted" and hitType != "Partially Resisted":
                duration = min(5, 2 + source.totalSpellpower / 20)
                Combat.addStatus(tar, "Shrink", duration)
            else:
                wasResisted = True
        if wasResisted:
            return "Fully Resisted"
        else:
            return "Normal Hit"

    def _frostWeapon(self, target):
        source = self.owner
        duration = min(7, 3 + source.totalSpellpower / 10)
        magnitude = Dice.roll(2, 5) + source.totalSpellpower / 15
        Combat.addStatus(target, "Frost Weapon", duration, magnitude)
        return "Normal Hit"



    monsterSpells = {
        'Shadow Field':
        {
        'tier' : 1,
        'school' : 'Bane',
        'MPCost' : 24,
        'APCost' : 10,
        'range' : 7,
        'target' : 'hostile',
        'action' : _shadowField,
        'cooldown' : 5
        }
    }

    allSpells = {
        # Player/Monster Spells
        'Arcane Dart':
        {
        'tier' : 1,
        'school' : 'Mystic',
        'MPCost' : 2,
        'APCost' : 6,
        'range' : 14,
        'target' : 'hostile',
        'action' : _arcaneDart,
        'cooldown' : None,
        'image' : TIER1 + "arcane-dart.png",
        'text' : 'Deals 2-4 + 3% arcane damage over a long distance.\n' + \
                'On Critical: +25% damage'
        },

        'Arcane Ward':
        {
        'tier' : 1,
        'school' : 'Mystic',
        'MPCost' : 7,
        'APCost' : 9,
        'range' : 0,
        'target' : 'self',
        'action' : _arcaneWard,
        'cooldown' : None,
        'image' : TIER1 + "arcane-ward.png",
        'text' : 'Grants a defensive warding that raises dodge chance, DR and magic resist\n' + \
                'for 3 turns + 1 per 10 spellpower up to a maximum of 6 turns. Starting\n' + \
                'values are +5% DR, +5 Dodge, +5 Magic Resist.'
        },

        'Mystic Shield':
        {
        'tier' : 1,
        'school' : 'Mystic',
        'MPCost' : 16,
        'APCost' : 12,
        'range' : 0,
        'target' : 'self',
        'action' : _mysticShield,
        'cooldown' : 4,
        'image' : TIER1 + 'mystic-shield.png',
        'text' : 'Grants an HP buffer absorbing 7 + 6% HP for up to 5 turns.'
        },

        'Flicker of Life':
        {
        'tier' : 1,
        'school' : 'Natural',
        'MPCost' : 15,
        'APCost' : 9,
        'range' : 7,
        'target' : 'friendly',
        'action' : _flickerOfLife,
        'cooldown' : None,
        'image' : TIER1 + "flicker-of-life.png",
        'text' : 'Restore 10-20 + 2% HP to yourself or an ally.',
        'condition' : _flickerOfLifeCheck
        },

        'Stone Guard':
        {
        'tier' : 1,
        'school' : 'Natural',
        'MPCost' : 15,
        'APCost' : 9,
        'range' : 5,
        'target' : 'friendly',
        'action' : _stoneGuard,
        'cooldown' : None,
        'image' : TIER1 + 'stone-guard.png',
        'text' : 'Grant a protective stone barrier increasing DR and poison tolerance.' + \
                '\nLasts between 4 and 6 turns.  Starting values are +12% DR and\n' + \
                '+12 Poison Tolerance.',
        'condition' : _stoneGuardCheck
        },

        'Singe':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 6,
        'APCost' : 7,
        'range' : 8,
        'target' : 'hostile',
        'action' : _singe,
        'cooldown' : None,
        'image' : TIER1 + 'singe.png',
        'text' : 'Deals 2-10 + 5% fire damage.\n' + \
                'On Critical +20% damage'
        },

        'Chill':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 10,
        'APCost' : 6,
        'range' : 6,
        'target' : 'hostile',
        'action' : _chill,
        'cooldown' : None,
        'image' : TIER1 + 'chill.png',
        'text' : 'Deals 1-12 + 1% cold damage and has a frequent chance to lower\n' + \
                'the dodge of the target by at least 5 points for 3 turns.'
        },

        'Shock':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 13,
        'APCost' : 7,
        'range' : 3,
        'target' : 'hostile',
        'action' : _shock,
        'cooldown' : 1,
        'image' : TIER1 + 'shock.png',
        'text' : 'Deals 15-22 + 1.4% Electric damage.\n' + \
                'On partial resist: -50% damage'
        },

        'Suggest Laziness':
        {
        'tier' : 1,
        'school' : 'Mental',
        'MPCost' : 5,
        'APCost' : 5,
        'range' : 12,
        'target' : 'hostile',
        'action' : _suggestLaziness,
        'cooldown' : None,
        'image' : TIER1 + 'suggest-laziness.png',
        'text' : 'This ability needs to be modified, please don\'t use it. TODO'
        },

        'Stutter':
        {
        'tier' : 1,
        'school' : 'Mental',
        'MPCost' : 14,
        'APCost' : 9,
        'range' : 7,
        'target' : 'hostile',
        'action' : _stutter,
        'cooldown' : None,
        'image' : TIER1 + 'stutter.png',
        'text' : 'Inflicts a 10% chance to fail to cast spells and reduces spellpower.'
        },

        'Cloud Vision':
        {
        'tier' : 1,
        'school' : 'Bane',
        'MPCost' : 9,
        'APCost' : 5,
        'range' : 7,
        'target' : 'hostile',
        'action' : _cloudVision,
        'cooldown' : None,
        'image' : TIER1 + 'cloud-vision.png',
        'text' : 'Greatly lowers enemy accuracy.\n' + \
                'Lasts 4 turns + 1 per 10 spellpower.\n' + \
                'On Partial Resist: -50% accuracy penalty',
        'condition' : _cloudVisionCheck
        },

        'Haunt':
        {
        'tier' : 1,
        'school' : 'Bane',
        'MPCost' : 20,
        'APCost' : 11,
        'range' : 5,
        'target' : 'hostile',
        'action' : _haunt,
        'cooldown' : 3,
        'image' : TIER1 + 'haunt.png',
        'text' : 'Deals 13-20 + 1% shadow damage immediately and inflicts an\n' + \
                'evil spirit upon the target, dealing 2-8 + 0.5% shadow damage each turn.\n' + \
                'Lasts 3 turns (4 if spellpower is 50 or higher.)\n' + \
                'On Partial Resist: DoT is ignored'
        },

        'Zone of Silence':
        {
        'tier' : 1,
        'school' : 'Illusion',
        'MPCost' : 10,
        'APCost' : 5,
        'range' : 6,
        'target' : 'location',
        'action' : _zoneOfSilence,
        'cooldown' : None,
        'image' : TIER1 + 'zone-of-silence.png',
        'text' : 'Creates a 3x3 area allowing Players that move through\n' + \
                'the Zone have their sneak increased by 10 and gain +10%\n' + \
                'critical hit chance for their next turn.',
        'radius' : 1,
        'placesField' : True
        },

        'Blurry':
        {
        'tier' : 1,
        'school' : 'Illusion',
        'MPCost' : 6,
        'APCost' : 3,
        'range' : 0,
        'target' : 'self',
        'action' : _blurry,
        'cooldown' : None,
        'image' : TIER1 + 'blurry.png',
        'text' : 'Cause your own image, sound and smells to become slightly\n' + \
                'distorted, leading foes to find you harder to target and detect.\n' + \
                'Lasts one turn.  Starting values are +5 Dodge and Sneak'
        },

        'Weapon Enhance':
        {
        'tier' : 1,
        'school' : 'Enchantment',
        'MPCost' : 9,
        'APCost' : 5,
        'range' : 4,
        'target' : 'friendly',
        'action' : _weaponEnhance,
        'cooldown' : None,
        'image' : TIER1 + 'weapon-enhance.png',
        'text' : 'Enhance a weapon to become more accurate, penetrate armor better,\n' + \
                'critically hit more often and deal more damage when it does.\n' + \
                'lasts between 3 and 7 turns.  Starting values are +3 Accuracy,\n' + \
                '+5% Critical Damage, +3% Armor Penetration, +1% Critical Hit Chance.'
        },

        'Flaming Weapon':
        {
        'tier' : 1,
        'school' : 'Enchantment',
        'MPCost' : 12,
        'APCost' : 8,
        'range' : 4,
        'target' : 'friendly',
        'action' : _flamingWeapon,
        'cooldown' : None,
        'image' : TIER1 + 'flaming-weapon.png',
        'text' : 'Enchant a weapon to deal an additional 1-8 + 1% fire damage.\n' + \
                'Lasts between 3 and 7 turns.'
        },

        # Tier 2
        'Burst':
        {
        'tier' : 2,
        'school' : 'Mystic',
        'MPCost' : 16,
        'APCost' : 11,
        'range' : 8,
        'target' : 'location',
        'action' : _burst,
        'cooldown' : 1,
        'image' : TIER2 + 'burst.png',
        'text' : 'Deal 10-12 + 1% arcane damage to any target at the center\n' + \
                'of your chosen location and half that damage to every hostile\n' + \
                'target within four tiles of it.  All secondary targets will\n' + \
                'be knocked 1 tile away from the center.',
        'radius' : 4
        },
        'Identification':
        {
        'tier' : 2,
        'school' : 'Mystic',
        'MPCost' : 5,
        'APCost' : 5,
        'range' : 0,
        'target' : 'self',
        'action' : _identification,
        'cooldown' : 1,
        'image' : TIER2 + 'identification.png',
        'text' : 'Grants +5 Spellpower and +15 Intuition for 3 turns.'
        },
        'Hovering Shield':
        {
        'tier' : 2,
        'school' : 'Mystic',
        'MPCost' : 8,
        'APCost' : 5,
        'range' : 0,
        'target' : 'self',
        'action' : _hoveringShield,
        'cooldown' : 5,
        'image' : TIER2 + 'hovering-shield.png',
        'text' : 'Gives the caster a 12 + 0.8% Bonus dodge vs. ranged\n' + \
                'attacks for five turns.'
        },
        'Fright':
        {
        'tier' : 2,
        'school' : 'Bane',
        'MPCost' : 6,
        'APCost' : 2,
        'range' : 6,
        'target' : 'hostile',
        'action' : _fright,
        'cooldown' : 1,
        'image' : TIER2 + 'fright.png',
        'text' : 'Lowers the target\'s shadow resistance by 30% aand\n' + \
                'it\'s attack power by 10% for four turns.'
        },
        'Infection':
        {
        'tier' : 2,
        'school' : 'Natural',
        'MPCost' : 7,
        'APCost' : 6,
        'range' : 1,
        'target' : 'hostile',
        'action' : _infection,
        'cooldown' : None,
        'image' : TIER2 + 'infection.png',
        'text' : 'Deals 7-12 + 3% poison damage against the foe and lowers\n' + \
                'poison tolerance by 8.  Lasts 4 turns + 1 per 20 spellpower.\n' + \
                'Has a poison rating of 40 + 1%.'
        },
        'Hands of Healing':
        {
        'tier' : 2,
        'school' : 'Natural',
        'MPCost' : 22,
        'APCost' : 8,
        'range' : 1,
        'target' : 'friendly',
        'action' : _handsOfHealing,
        'cooldown' : 1,
        'image' : TIER2 + 'hands-of-healing.png',
        'text' : 'Restore 20-40 + 2% health to yourself or an adjacent\n' + \
                'ally.'
        },
        'Elemental Boon':
        {
        'tier' : 2,
        'school' : 'Primal',
        'MPCost' : 8,
        'APCost' : 10,
        'range' : 6,
        'target' : 'friendly',
        'action' : _elementalBoon,
        'cooldown' : None,
        'image' : TIER2 + 'elemental-boon.png',
        'text' : 'Grant +15% Fire, Cold, and Electric Resistance to\n' + \
                'the target.  Each resistance grows 1% per 10 spellpower.\n' + \
                'Lasts 6 Turns (7 with 50+ spellpower).'
        },
        'Torrent':
        {
        'tier' : 2,
        'school' : 'Primal',
        'MPCost' : 25,
        'APCost' : 14,
        'range' : 16,
        'target' : 'hostile',
        'action' : _torrent,
        'cooldown' : 2,
        'image' : TIER2 + 'torrent.png',
        'text' : 'Blasts a target with supercooled liquid for 10-35 + 1.4% Cold damage and knocks back\n' + \
                'any non-huge target 5 tiles that does not resist (paritally or fully).  Will hit the first\n' + \
                'hostile target it encounters between itself and the intended target.'
        },
        'Lightning Bolt':
        {
        'tier' : 2,
        'school' : 'Primal',
        'MPCost' : 32,
        'APCost' : 8,
        'range' : 8,
        'target' : 'hostile',
        'action' : _lightningBolt,
        'cooldown' : 1,
        'image' : TIER2 + 'lightning-bolt.png',
        'text' : 'Zap a series of targets between you and your specified target for 5-33 + 0.5% Electric damage.\n' + \
                'On partial resist: -50% damage\n' + \
                'On critical: +30% damage'
        },
        'Pit' :
        {
        'tier' : 2,
        'school' : 'Illusion',
        'MPCost' : 5,
        'APCost' : 2,
        'range' : 5,
        'target' : 'location',
        'action' : _pit,
        'cooldown' : None,
        'image' : TIER2 + 'pit.png',
        'text' : 'Cause all enemies to believe a bottomless pit exist on a tile.\n' + \
                'Monsters will take less direct paths, trying to move around that\n' + \
                'tile and will not be able to move onto it.  If a player walks over\n' + \
                'the tile, the effect is dispelled.',
        'placesField' : True
        },
        'Smoke Screen':
        {
        'tier' : 2,
        'school' : 'Illusion',
        'MPCost' : 18,
        'APCost' : 6,
        'range' : 4,
        'target' : 'location',
        'action' : _smokeScreen,
        'cooldown' : 3,
        'image' : TIER2 + 'smoke-screen.png',
        'text' : 'Cover an area with smoke, causing players and monsters that enter it\n' + \
                'to have +10 dodge but -35% fire resistance for a turn.',
        'radius' : 4,
        'placesField' : True
        },
        'Shrink':
        {
        'tier' : 2,
        'school' : 'Enchantment',
        'MPCost' : 10,
        'APCost' : 9,
        'range' : 4,
        'target' : 'hostile',
        'action' : _shrink,
        'cooldown' : 2,
        'image' : TIER2 + 'shrink.png',
        'text' : 'Shrinks a target and its adjacent allies such that their attack power and\n' + \
                'DR are both reduced by 12% for 2 turns (up to 5 turns with 60 spellpower).\n' + \
                'Monsters that partially resist ignore all effects; small creatures are immune.',
        'radius' : 1
        },
        'Frost Weapon':
        {
        'tier' : 2,
        'school' : 'Enchantment',
        'MPCost' : 12,
        'APCost' : 8,
        'range' : 3,
        'target' : 'friendly',
        'action' : _frostWeapon,
        'cooldown' : 0,
        'image' : TIER2 + 'frost-weapon.png',
        'text' : 'Enhance the effect of your, or your ally\'s, weapon to deal 2-5 + 2% Cold damage and\n' + \
                'have an unlikely chance on hit to reduce movement speed by 1 tile/move and lower\n' + \
                'Dodge by 4 points for 3 turns.  The enchantment itself lasts 3 Turns + 1 per 10 spellpower\n' + \
                'up to a maximum of 7 turns.'
        }
    }

    def _shoutSpellCast(self, source, target):
        s = self
        direction = None
        double = None
        hearer = None
        if self.targetType == 'location' or (source.team == "Players" and target.team != "Players"):
            direction = "Outgoing"
            hearer = source
        elif source.team == "Monsters":
            direction = "Incoming"
            hearer = target
        elif source.team == "Players" and target.team == "Players":
            direction = "Outgoing"
            double = "Incoming"
            hearer = source
        bundle = {'direction' : direction, 'suffix' : None, 'spell' : s}
        bc = broadcast.SpellBroadcast(bundle)
        bc.shout(hearer)
        if double:
            bundle = {'direction' : double, 'suffix' : None, 'spell' : s}
            bc = broadcast.SpellBroadcast(bundle)
            hearer = source
            bc.shout(hearer)

    def _shoutSpellCastComplete(self, source, target):
        s = self
        direction = None
        double = None
        hearer = None
        if self.targetType == 'location' or (source.team == "Players" and target.team != "Players"):
            direction = "Outgoing"
            hearer = source
        elif source.team == "Monsters":
            direction = "Incoming"
            hearer = target
        elif source.team == "Players" and target.team == "Players":
            direction = "Outgoing"
            double = "Incoming"
            hearer = source
        bundle = {'direction' : direction, 'suffix' : 'Complete', 'spell' : s}
        bc = broadcast.SpellBroadcast(bundle)
        bc.shout(hearer)
        if double:
            bundle = {'direction' : double, 'suffix' : 'Complete', 'spell' : s}
            bc = broadcast.SpellBroadcast(bundle)
            hearer = source
            bc.shout(hearer)

    def _shoutSpellResisted(self):
        if not self.owner.team == "Players":
            return
        bc = broadcast.SpellResistBroadcast({spell : self})
        bc.shout(self.owner)

fieldEffects = {
    'Pit' : Spell._applyPit,
    'Smoke Screen' : Spell._applySmokeScreen,
    'Zone of Silence' : Spell._applyZoneOfSilence
}
