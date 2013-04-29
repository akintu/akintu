#!/usr/bin/python

import sys
import entity
from combat import *
from dice import *

# consumable.py
# Author: Devin Ekins -- G. Cube
#
# Consumable module consists of a couple of control methods and individual
# methods specific to their individual use.  They are not commented as the 
# description of their function is defined in their dict.

class Consumable(entity.Entity):

    AP_COST = 7
    COOLDOWN = 3

    def __init__(self, name, location=None):
        entity.Entity.__init__(self, location)
        self.name = name
        self.displayName = name
        self.identifier = name
        self.weight = 1
        self.type = None # Used as cooldown name
        self.value = 0
        self.level = 0
        self.effect = None
        self.cooldownLength = Consumable.COOLDOWN
        if name in Consumable.allPotions:
            self.type = "Potion"
            self.value = Consumable.allPotions[name]['value']
            self.level = Consumable.allPotions[name]['level']
            self.effect = Consumable.allPotions[name]['effect']
            self.ip = Consumable.allPotions[name]['ip']
            self.details = Consumable.allPotions[name]['details']
        elif name in Consumable.allPoisons:
            self.type = "Poison"
            self.value = Consumable.allPoisons[name]['value']
            self.level = Consumable.allPoisons[name]['level']
            self.effect = Consumable.allPoisons[name]['effect']
            self.ip = Consumable.allPoisons[name]['ip']
            self.details = Consumable.allPoisons[name]['details']
        self.color = "black" # Never changes
            
    def canUse(self, user):
        '''Return True if the user can use this consumable.'''
        if self.type in [x[0] for x in user.cooldownList]:
            durationLeft = [x[1] for x in user.cooldownList][0]
            return (False, "Item type: " + self.type + " is on cooldown (" + str(durationLeft) + ")")
        if user.AP >= Consumable.AP_COST:
            return (True, "")
        else:
            return (False, "Not enough AP to use " + self.name + " (" + 
                        str(Consumable.AP_COST) + " needed)")

    def use(self, user):
        '''Have the user use this consumable'''
        self.effect(self, user)
        user.inventory.removeItem(self)
        Combat.applyCooldown(user, self.type, self.cooldownLength)
        Combat.modifyResource(user, "AP", -Consumable.AP_COST)
        return "Used item: " + self.name + "."


    def _basicHealingPotion(self, user):
        healing = Dice.roll(6, 20)
        healing *= (1 + float(user.totalPotionEffect) / 100)
        Combat.healTarget(user, user, round(healing))

    def _lesserHealingPotion(self, user):
        healing = Dice.roll(9, 30)
        healing *= (1 + float(user.totalPotionEffect) / 100)
        Combat.healTarget(user, user, round(healing))

    def _moderateHealingPotion(self, user):
        healing = Dice.roll(12, 40)
        healing *= (1 + float(user.totalPotionEffect) / 100)
        Combat.healTarget(user, user, round(healing))

    # Healing functions go above

    def _basicManaPotion(self, user):
        mana = Dice.roll(10, 17)
        mana *= (1 + float(user.totalPotionEffect) / 100)
        Combat.modifyResource(user, "MP", mana)

    def _lesserManaPotion(self, user):
        mana = Dice.roll(18, 30)
        mana *= (1 + float(user.totalPotionEffect) / 100)
        Combat.modifyResource(user, "MP", mana)

    def _moderateManaPotion(self, user):
        mana = Dice.roll(30, 45)
        mana *= (1 + float(user.totalPotionEffect) / 100)
        Combat.modifyResource(user, "MP", mana)

    # Mana functions go above

    def _antidote(self, user):
        Combat.removeStatusOfType(user, "Poison")

    def _thawingPotion(self, user):
        Combat.removeStatusOfType(user, "Cold")

    def _quenchingPotion(self, user):
        Combat.removeStatusOfType(user, "Fire")

    def _neutralizingPotion(self, user):
        Combat.removeStatusOfType(user, "Electric")

    def _clottingPotion(self, user):
        Combat.removeStatusOfType(user, "Bleeding", True) # removeAll

    def _rockPotion(self, user):
        if user.hasStatus(statusCategory="Stone") and not user.hasStatus("Rock Potion"):
            print "Cannot stack Stone effects."
        else:
            duration = 8
            if user.hasExtraLengthBuffs:
                duration += 1
            Combat.addStatus(user, "Rock Potion", duration)

    def _prismaticPotion(self, user):
        duration = 8
        if user.hasExtraLengthBuffs:
            duration += 1
        Combat.addStatus(user, "Prismatic Potion", duration)

    def _vaccine(self, user):
        Combat.addStatus(user, "Vaccine", duration=99)
        damage = round(Dice.roll(1, 8) * (1 - float(user.totalPoisonResistance) / 100))
        if damage > user.HP:
            damage = max(0, user.HP - 1)
        Combat.lowerHP(user, damage)

    def _spiritPotion(self, user):
        duration = 8
        if user.hasExtraLengthBuffs:
            duration += 1
        Combat.addStatus(user, "Spirit Potion", duration)

    # Buffing potions go above.

    def _basicPoison(self, user):
        bonus = 20 * (1 + float(user.totalPoisonBonusDamage) / 100)
        base = Consumable._calcWeaponAverageDamage(user.equippedItems.equippedWeapon)
        total = int((float(bonus) / 100 * base))
        duration = 8
        if user.hasExtraLengthBuffs:
            duration += 1
        Combat.addStatus(user, "Applied Basic Poison", duration, total)

    def _vilePoison(self, user):
        duration = 8 # Duration of poison on weapon, not on affected monster.
        Combat.addStatus(user, "Applied Vile Poison", duration)

    def _numbingPoison(self, user):
        duration = 8 # Duration of poison on weapon, not on affected monster.
        Combat.addStatus(user, "Applied Numbing Poison", duration)

    # Poisons go above
    # Scrolls, effusions, oils go here...

    @staticmethod
    def _calcWeaponAverageDamage(weapon):
        if not weapon:
            return 0
        minDam = weapon.damageMin + weapon.damageMinBonus
        maxDam = weapon.damageMax + weapon.damageMaxBonus
        return round((minDam + maxDam) / 2)

    allPotions = {
        'Basic Healing Potion' :
            {
            'value' : 30,
            'level' : 1,
            'effect' : _basicHealingPotion,
            'ip' : 1,
            'details' : 'Restores 6-20 points of HP'
            },
        'Lesser Healing Potion' :
            {
            'value' : 75,
            'level' : 3,
            'effect' : _lesserHealingPotion,
            'ip' : 3,
            'details' : 'Restores 9-30 points of HP'
            },
        'Moderate Healing Potion' :
            {
            'value' : 160,
            'level' : 6,
            'effect' : _moderateHealingPotion,
            'ip' : 7,
            'details' : 'Restores 12-40 points of HP'
            },
        # Other healing potions here
        'Basic Mana Potion' :
            {
            'value' : 60,
            'level' : 1,
            'effect' : _basicManaPotion,
            'ip' : 2,
            'details' : 'Restores 10-17 points of MP'
            },
        'Lesser Mana Potion' :
            {
            'value' : 200,
            'level' : 3,
            'effect' : _lesserManaPotion,
            'ip' : 6,
            'details' : 'Restores 18-30 points of MP'
            },
        'Moderate Mana Potion' :
            {
            'value' : 550,
            'level' : 6,
            'effect' : _moderateManaPotion,
            'ip' : 12,
            'details' : 'Restores 30-45 points of MP'
            },
        # Other mana potions here
        'Antidote' :
            {
            'value' : 20,
            'level' : 1,
            'effect' : _antidote,
            'ip' : 1,
            'details' : 'Removes one Poison-based ailment'
            },
        'Thawing Potion' :
            {
            'value' : 30,
            'level' : 1,
            'effect' : _thawingPotion,
            'ip' : 2,
            'details' : 'Removes one Ice-based aliment'
            },
        'Quenching Potion' :
            {
            'value' : 30,
            'level' : 1,
            'effect' : _quenchingPotion,
            'ip' : 2,
            'details' : 'Removes one Fire-based ailment'
            },
        'Neutralizing Potion' :
            {
            'value' : 25,
            'level' : 5,
            'effect' : _neutralizingPotion,
            'ip' : 5,
            'details' : 'Removes one Lightning-based ailment'
            },
        'Clotting Potion' :
            {
            'value' : 7000,
            'level' : 5,
            'effect' : _clottingPotion,
            'ip' : 10,
            'details' : 'Removes all bleeding effects'
            },
        'Rock Potion' :
            {
            'value' : 140,
            'level' : 5,
            'effect' : _rockPotion,
            'ip' : 6,
            'details' : 'Grants +20% DR for 8 \n' + \
                        'Turns (stone-based)'
            },
        'Prismatic Potion' :
            {
            'value' : 150,
            'level' : 5,
            'effect' : _prismaticPotion,
            'ip' : 6,
            'details' : 'Grants +15% Fire, Cold,\n' + \
                        'and Electric Resistance'
            },
        'Vaccine' :
            {
            'value' : 100,
            'level' : 5,
            'effect' : _vaccine,
            'ip' : 4,
            'details' : 'Grants +18 Poison tolerance,\n' + \
                        'but deals 1-8 Poison damage to\n' + \
                        'yourself'
            },
        'Spirit Potion' :
            {
            'value' : 250,
            'level' : 8,
            'effect' : _spiritPotion,
            'ip' : 10,
            'details' : 'Grants +22% Shadow Resistance\n' + \
                        'and +7% Arcane Resistance'
            }
            # TODO: Other buffing potions go here.
        }
    allPoisons = {
        'Basic Poison' :
            {
            'value' : 50,
            'level' : 1,
            'effect' : _basicPoison,
            'ip' : 1,
            'details' : 'Applies +20% Weapon damage \n' + \
                        'as Poison (Rating = User level\n' + \
                        ' * 3 + 7)'
                
            },
        'Numbing Poison' :
            {
            'value' : 45,
            'level' : 1,
            'effect' : _numbingPoison,
            'ip' : 1,
            'details' : 'Applies a chance to slow\n ' + \
                        'enemies\' movement speed.\n' + \
                        '(Rating = 13)'
            },
            # Sickening Poison
        'Vile Poison' :
            {
            'value' : 65,
            'level' : 1,
            'effect' : _vilePoison,
            'ip' : 2,
            'details' : 'Applies a chance to lower \n' + \
                        'attack power by 10% \n' + \
                        'and inflict a 3% chance\n' + \
                        'to fail to cast spells.\n' + \
                        '(Rating = 24)'
            }

            # TODO: Fill in other poisons.
        }
        # TODO: Scrolls/Oils and Effusions






















