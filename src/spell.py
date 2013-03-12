#!/usr/bin/python

import sys
from combat import *
import dice

ROOT_FOLDER = "./res/images/icons/"
TIER1 = ROOT_FOLDER + "tier1_spells/"

class SpellStub(object):
    def __init__(self, name):
        self.name = name
        info = None
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

    def canUse(self, target):
        '''
        target: Person (later, Location?)
        '''
        source = self.owner

        # Check for modifications to spells costs here from listeners TODO
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
        if not source.inRange(target, self.range):
            return (False, "Target is out of range.")
        if source.onCooldown(self.name) :
            return (False, self.name + " is on Cooldown.")
        return (True, "")


    def use(self, target):
        ''' Casts the given spell on or around the given target Person (Location?)
        Performs a check if this is possible, but this is not where the canUse
        check should be made.  If caught here, it will raise an exception!'''
        if self.canUse(target)[0]:
            Combat.modifyResource(self.owner, "MP", -self.MPCost)
            Combat.modifyResource(self.owner, "AP", -self.APCost)
            if self.cooldown:
                Combat.applyCooldown(self.owner, self.name, self.cooldown)
            spellSuccess = Dice.rollSuccess(100 - self.owner.spellFailureChance)
            if spellSuccess:
                self._shoutSpellCast(self.owner, target)
                if self.targetType == "hostile" and target.team == "Players":
                    self.applySchoolResistance(target)
                    self.action(self, target)
                    self.unapplySchoolResistance(target)
                else:
                    self.action(self, target)
                self._shoutSpellCastComplete(self.owner, target)
                if self.targetType != "friendly" and self.targetType != "self":
                    Combat.removeStealth(self.owner)

            else:
                Combat.sendCombatMessage("Spell Casting Failed! (" + str(self.owner.spellFailureChance) +
                                         "%)", self.owner)
                return
                
        else:
            return
            # TODO! Make this raise an exception rather than silently return.

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

    # Monster Only Spells

    def _shadowField(self, target):
        '''Deals massive shadow damage to a 3x3 area centered on a player.
        Partial Resistance = 33% Damage Dealt.'''
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damageBase = 11
        damage = Combat.calcDamage(source, target, damageBase, damageBase * 4, "Shadow", hitValue=hitType,
                                   partial=0.33, scalesWith="Spellpower", scaleFactor=0.02)
        #TODO: This hits a 3x3 area.  Include all targets!
        Combat.lowerHP(target, damage)


    # Player & Monster Spells

    def _arcaneDart(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = (Combat.calcDamage(source, target, minimum=2, maximum=4, element="Arcane",
                                    hitValue=hitType, critical=1.2, scalesWith="Spellpower", scaleFactor=0.03))
        Combat.lowerHP(target, damage)

    def _arcaneWard(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 3, 0.1, cap=6)
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.01)
        Combat.addStatus(target, self.name, duration, magnitude)

    def _mysticShield(self, target):
        source = self.owner
        duration = 5
        magnitude = Dice.scale(source.totalSpellpower, 8, 0.06)
        Combat.addStatus(target, self.name, duration, magnitude)

    def _flickerOfLife(self, target):
        source = self.owner
        magnitude = Dice.scale(source.totalSpellpower, Dice.roll(10,20), 0.02)
        Combat.healTarget(source, target, magnitude)

    def _stoneGuard(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 4, 0.05, cap=6)
        magnitude = Dice.scale(source.totalSpellpower, 10, 0.008)
        Combat.addStatus(target, self.name, duration, magnitude)

    def _singe(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = (Combat.calcDamage(source, target, minimum=2, maximum=9, element="Fire",
                                    hitValue=hitType, critical=1.2, partial=0.5,
                                    scalesWith="Spellpower", scaleFactor=0.05))
        Combat.lowerHP(target, damage)

    def _chill(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, minimum=1, maximum=12, element="Cold",
                                   hitValue=hitType, scalesWith="Spellpower",
                                   scaleFactor=0.01)
        duration = 2
        chance = Dice.rollPresetChance(source, target, "Frequent")
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.012)
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType, chance=chance)

    def _shock(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, minimum=15, maximum=22, element="Electric", hitValue=hitType,
                                   scalesWith="Spellpower", scaleFactor=0.014)
        Combat.lowerHP(target, damage)

    def _suggestLaziness(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        pass
        # TODO: this status requires AI -- we don't have that yet.

    def _stutter(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        duration = 5
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.02)
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)

    def _cloudVision(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        duration = Dice.scale(source.totalSpellpower, 4, 0.025)
        magnitude = Dice.scale(source.totalSpellpower, 10, 0.012)
        if hitType == "Partially Resisted":
            magnitude /= 2
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)

    def _haunt(self, target):
        source = self.owner
        hitType = Combat.calcHit(source, target, "Magical")
        damage = Combat.calcDamage(source, target, minimum=13, maximum=20, element="Shadow", hitValue=hitType,
                                   scalesWith="Spellpower", scaleFactor=0.01)
        Combat.lowerHP(target, damage)

        duration = Dice.scale(source.totalSpellpower, 3, 0.02, cap=4)
        magnitude = round(Dice.roll(2,8) * (1 + source.totalSpellpower * 0.005))
        Combat.addStatus(target, self.name, duration, magnitude, hitValue=hitType)

    def _zoneOfSilence(self, target):
        pass
        # TODO!!

    def _blurry(self, target):
        source = self.owner
        duration = 1
        magnitude = Dice.scale(source.totalSpellpower, 5, 0.02)
        Combat.addStatus(target, self.name, duration, magnitude)

    def _weaponEnhance(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 3, 0.03, cap=7)
        magnitudeA = Dice.scale(source.totalSpellpower, 3, 0.07) # Accuracy/Penetration
        magnitudeB = Dice.scale(source.totalSpellpower, 5, 0.05) # Crit mag
        magnitudeC = Dice.scale(source.totalSpellpower, 1, 0.035) # Crit chance
        Combat.addStatus(target, "Weapon Enhance Striking", duration, magnitudeA)
        Combat.addStatus(target, "Weapon Enhance Punishing", duration, magnitudeB)
        Combat.addStatus(target, "Weapon Enhance Precision", duration, magnitudeC)

    def _flamingWeapon(self, target):
        source = self.owner
        duration = Dice.scale(source.totalSpellpower, 3, 0.03, cap=7)
        magnitude = round(Dice.roll(1,8) * (1 + source.totalSpellpower * 0.01))
        Combat.addStatus(target, self.name, duration, magnitude)

    def _hoveringShield(self, target):
        source = self.owner
        duration = 5
        magnitude = 12 + source.totalSpellpower / 10
        Combat.addStatus(target, self.name, duration, magnitude)

    def _fright(self, target):
        source = self.owner
        duration = 4
        Combat.addStatus(target, self.name, duration)

    def _infection(self, target):
        source = self.owner
        minDam = round(7 * (1 + source.totalSpellpower * 0.03) *
                           (1 + float(source.totalPoisonBonusDamage) / 100))
        maxDam = round(10 * (1 + source.totalSpellpower * 0.03) *
                           (1 + float(source.totalPoisonBonusDamage) / 100))
        dieRoll = Dice.roll(minDam, maxDam)
        rating = round(35 + 0.4 * source.totalSpellpower)
        duration = 4 + source.totalSpellpower / 20
        if Combat.calcPoisonHit(source, target, rating):
            Combat.addStatus(target, "Infection", duration, dieRoll)

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
        'APCost' : 5,
        'range' : 11,
        'target' : 'hostile',
        'action' : _arcaneDart,
        'cooldown' : None,
        'image' : TIER1 + "arcane-dart.png",
        'text' : 'Deals 2-4 + 3% arcane damage.\n' + \
                'On Critical: +20% damage'
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
                'for 3 turns + 1 per 10 spellpower up to a maximum of 6 turns.'
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
        'text' : 'Grants an HP buffer absorbing 8 + 6% HP for up to 5 turns.'
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
        'text' : 'Restore 10-20 + 2% HP to yourself or an ally.'
        },

        'Stone Guard':
        {
        'tier' : 1,
        'school' : 'Natural',
        'MPCost' : 15,
        'APCost' : 9,
        'range' : 4,
        'target' : 'friendly',
        'action' : _stoneGuard,
        'cooldown' : None,
        'image' : TIER1 + 'stone-guard.png',
        'text' : 'Grant a protective stone barrier increasing DR and poison tolerance.' + \
                '\nLasts between 4 and 6 turns.'
        },

        'Singe':
        {
        'tier' : 1,
        'school' : 'Primal',
        'MPCost' : 6,
        'APCost' : 7,
        'range' : 7,
        'target' : 'hostile',
        'action' : _singe,
        'cooldown' : None,
        'image' : TIER1 + 'singe.png',
        'text' : 'Deals 2-9 + 5% fire damage.\n' + \
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
                'the dodge of the target for 2 turns.'
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
                'On Partial Resist: -50% accuracy penalty'
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
        'MPCost' : 20,
        'APCost' : 6,
        'range' : 4,
        'target' : 'terrain',
        'action' : _zoneOfSilence,
        'cooldown' : None,
        'image' : TIER1 + 'zone-of-silence.png',
        'text' : 'Creates a 3x3 area within which Stealth requires\n' + \
                'less AP to activate and sneak is increaesd by 10.\n' + \
                'Lasts between 3 and 6 turns'
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
                'Lasts one turn.'
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
                'lasts between 3 and 7 turns.'
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
        # Burst
        # Identification
        'Hovering Shield':
        {
        'tier' : 2,
        'school' : 'Mystic',
        'MPCost' : 8,
        'APCost' : 5,
        'range' : 0,
        'target' : 'self',
        'action' : _hoveringShield,
        'cooldown' : 5
        },
        'Fright':
        {
        'tier' : 2,
        'school' : 'Bane',
        'MPCost' : 6,
        'APCost' : 3,
        'range' : 6,
        'target' : 'hostile',
        'action' : _fright,
        'cooldown' : 1
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
        'cooldown' : None
        }
    }

    def _shoutSpellCast(self, source, target):
        s = self
        direction = None
        double = None
        hearer = None
        if source.team == "Players" and target.team != "Players":
            direction = "Outgoing"
            hearer = source
        elif source.team == "Monsters" and target.team == "Players":
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
        if source.team == "Players" and target.team != "Players":
            direction = "Outgoing"
            hearer = source
        elif source.team == "Monsters" and target.team == "Players":
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

