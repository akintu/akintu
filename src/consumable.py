#!/usr/bin/python

import sys
import entity
from combat import *
from dice import *

class Consumable(entity.Entity):

    AP_COST = 7
    COOLDOWN = 3

    def __init__(self, name, location=None):
        entity.Entity.__init__(self, location)
        self.name = name
        self.identifier = name
        self.weight = 1
        self.type = None # Used as cooldown name
        self.goldValue = 0
        self.level = 0
        self.effect = None
        self.cooldownLength = Consumable.COOLDOWN
        if name in Consumable.allPotions:
            self.type = "Potion"
            self.goldValue = Consumable.allPotions[name]['goldValue']
            self.level = Consumable.allPotions[name]['level']
            self.effect = Consumable.allPotions[name]['effect']
            self.ip = Consumable.allPotions[name]['ip']
        elif name in Consumable.allPoisons:
            self.type = "Applied Poison"
            self.goldValue = Consumable.allPoisons[name]['goldValue']
            self.level = Consumable.allPoisons[name]['level']
            self.effect = Consumable.allPoisons[name]['effect']
            self.ip = Consumable.allPoisons[name]['ip']

    def canUse(self, user):
        if self.type in user.cooldownList:
            return False
        if user.AP >= 7:
            return True

    def use(self, user):
        if self.canUse(user):
            self.effect(user)
            self.user.inventory.removeItem(self)
            Combat.applyCooldown(user, self.type, self.cooldownLength)
            print "Used item: " + self.name + "."
        else:
            print "Attempted to use " + self.name + " but it cannot be used at this time."


    def _basicHealingPotion(self, user):
        healing = Dice.roll(3, 10)
        healing *= (1 + float(user.totalPotionEffect) / 100)
        Combat.healTarget(user, user, round(healing))

    def _lesserHealingPotion(self, user):
        healing = Dice.roll(6, 20)
        healing *= (1 + float(user.totalPotionEffect) / 100)
        Combat.healTarget(user, user, round(healing))

    def _moderateHealingPotion(self, user):
        healing = Dice.roll(9, 30)
        healing *= (1 + float(user.totalPotionEffect) / 100)
        Combat.healTarget(user, user, round(healing))

    # Healing functions go above

    def _basicManaPotion(self, user):
        mana = Dice.roll(5, 8)
        mana *= (1 + float(user.totalPotionEffect) / 100)
        Combat.modifyResource(user, "MP", mana)

    def _lesserManaPotion(self, user):
        mana = Dice.roll(10, 17)
        mana *= (1 + float(user.totalPotionEffect) / 100)
        Combat.modifyResource(user, "MP", mana)

    def _moderateManaPotion(self, user):
        mana = Dice.roll(18, 30)
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
            Combat.addStatus(user, "Rock Potion", duration=8)
        else:
            print "Cannot stack Stone effects."

    def _prismaticPotion(self, user):
        Combat.addStatus(user, "Prismatic Potion", duration=8)

    def _vaccine(self, user):
        Combat.addStatus(user, "Vaccine", duration=99)
        damage = round(Dice.roll(1, 8) * (1 - float(user.totalPoisonResistance) / 100))
        Combat.lowerHP(user, damage)

    def _spiritPotion(self, user):
        Combat.addStatus(user, "Spirit Potion", duration = 8)

    # Buffing potions go above.

    def _basicPoison(self, user):
        bonus = 20 * (1 + float(user.totalPoisonBonusDamage) / 100)
        base = Consumable._calcWeaponAverageDamage(user.equippedItems.equippedWeapon)
        total = round(float(bonus) / 100 * base)
        duration = 8
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
            'goldValue' : 30,
            'level' : 1,
            'effect' : _basicHealingPotion,
            'ip' : 1
            },
        'Lesser Healing Potion' :
            {
            'goldValue' : 75,
            'level' : 3,
            'effect' : _lesserHealingPotion,
            'ip' : 3
            },
        'Moderate Healing Potion' :
            {
            'goldValue' : 160,
            'level' : 6,
            'effect' : _moderateHealingPotion,
            'ip' : 7
            },
        # Other healing potions here
        'Basic Mana Potion' :
            {
            'goldValue' : 60,
            'level' : 1,
            'effect' : _basicManaPotion,
            'ip' : 2
            },
        'Lesser Mana Potion' :
            {
            'goldValue' : 200,
            'level' : 3,
            'effect' : _lesserManaPotion,
            'ip' : 6
            },
        'Moderate Mana Potion' :
            {
            'goldValue' : 550,
            'level' : 6,
            'effect' : _moderateManaPotion,
            'ip' : 12
            },
        # Other mana potions here
        'Antidote' :
            {
            'goldValue' : 20,
            'level' : 1,
            'effect' : _antidote,
            'ip' : 1
            },
        'Thawing Potion' :
            {
            'goldValue' : 30,
            'level' : 1,
            'effect' : _thawingPotion,
            'ip' : 2
            },
        'Quenching Potion' :
            {
            'goldValue' : 30,
            'level' : 1,
            'effect' : _quenchingPotion,
            'ip' : 2
            },
        'Neutralizing Potion' :
            {
            'goldValue' : 25,
            'level' : 5,
            'effect' : _neutralizingPotion,
            'ip' : 5
            },
        'Clotting Potion' :
            {
            'goldValue' : 7000,
            'level' : 5,
            'effect' : _clottingPotion,
            'ip' : 10
            },
        'Rock Potion' :
            {
            'goldValue' : 120,
            'level' : 5,
            'effect' : _rockPotion,
            'ip' : 5
            },
        'Prismatic Potion' :
            {
            'goldValue' : 150,
            'level' : 5,
            'effet' : _prismaticPotion,
            'ip' : 6
            },
        'Vaccine' :
            {
            'goldValue' : 100,
            'level' : 5,
            'effect' : _vaccine,
            'ip' : 4
            },
        'Spirit Potion' :
            {
            'goldValue' : 250,
            'level' : 8,
            'effect' : _spiritPotion,
            'ip' : 10
            }
            # TODO: Other buffing potions go here.
        }
    allPoisons = {
        'Basic Poison' :
            {
            'goldValue' : 10,
            'level' : 1,
            'effect' : _basicPoison,
            'ip' : 1
            },
        'Numbing Poison' :
            {
            'goldValue' : 15,
            'level' : 1,
            'effect' : _numbingPoison,
            'ip' : 1
            },
            # Sickening Poison
        'Vile Poison' :
            {
            'goldValue' : 40,
            'level' : 1,
            'effect' : _vilePoison,
            'ip' : 2
            }

            # TODO: Fill in other poisons.
        }
        # TODO: Scrolls/Oils and Effusions






















