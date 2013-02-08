#!/usr/bin/python

import sys
import entity
from combat import *
from dice import *

class Consumable(entity.Entity):

    AP_COST = 7

    def __init__(self, name, location=None):
	    entity.Entity.__init__(self, location)
        self.name = name
        self.identifier = name
        self.weight = 1
        self.type = None # Used as cooldown name
        self.goldValue = 0
        self.level = 0
        self.effect = None
        self.cooldownLength = 3
        if name in allPotions:
            self.type = "Potion"
            self.goldValue = allPotions[name]['goldValue']
            self.level = allPotions[name]['level']
            self.effect = allPotions[name]['effect']
        elif name in allPoisons:
            self.type = "Applied Poison"
            self.goldValue = allPoisons[name]['goldValue']
            self.level = allPoisons[name]['level']
            self.effect = allPoisons[name]['effect']
        
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
        healing *= (1 + user.totalPotionEffect / 100)
        Combat.healTarget(user, user, round(healing))
        
    def _lesserHealingPotion(self, user):
        healing = Dice.roll(6, 20)
        healing *= (1 + user.totalPotionEffect / 100)
        Combat.healTarget(user, user, round(healing))
        
    def _moderateHealingPotion(self, user):
        healing = Dice.roll(9, 30)
        healing *= (1 + user.totalPotionEffect / 100)
        Combat.healTarget(user, user, round(healing))
        
    # Healing functions go above
    
    def _basicManaPotion(self, user):
        mana = Dice.roll(5, 8)
        mana *= (1 + user.totalPotionEffect / 100)
        Combat.modifyResource(user, "MP", mana)
        
    def _lesserManaPotion(self, user):
        mana = Dice.roll(10, 17)
        mana *= (1 + user.totalPotionEffect / 100)
        Combat.modifyResource(user, "MP", mana)
        
    def _moderateManaPotion(self, user):
        mana = Dice.roll(18, 30)
        mana *= (1 + user.totalPotionEffect / 100)
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
        pass
        # TODO: Add DR buff from rock potion.
        
    def _prismaticPotion(self, user):
        pass
        # TODO: Add Cold, Fire, Electric resistance buff from this potion.
        
    # Buffing potions go above.
    
    def _basicPoison(self, user):
        bonus = 20 * (1 + user.totalPoisonBonusDamage/100)
        base = Consumable._calcWeaponAverageDamage(user.equippedItems.equippedWeapon)
        total = round(bonus/100 * base)
        duration = 8
        Combat.addStatus(user, "Applied Basic Poison", duration, total)
        
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
            'effect' : _basicHealingPotion
            },
        'Lesser Healing Potion' :
            {
            'goldValue' : 75,
            'level' : 3,
            'effect' : _lesserHealingPotion
            },
        'Moderate Healing Potion' :
            {
            'goldValue' : 160,
            'level' : 6,
            'effect' : _moderateHealingPotion
            {,
        # Other healing potions here
        'Basic Mana Potion' :
            {
            'goldValue' : 60,
            'level' : 1,
            'effect' : _basicManaPotion
            },
        'Lesser Mana Potion' :
            {
            'goldValue' : 200,
            'level' : 3,
            'effect' : _lesserManaPotion
            },
        'Moderate Mana Potion' :
            {
            'goldValue' : 550,
            'level' : 6,
            'effect' : _moderateManaPotion
            },
        # Other mana potions here
        'Antidote' :
            {
            'goldValue' : 20,
            'level' : 1,
            'effect' : _antidote
            },
        'Thawing Potion' :
            {
            'goldValue' : 30,
            'level' : 1,
            'effect' : _thawingPotion
            },
        'Quenching Potion' :
            {
            'goldValue' : 30,
            'level' : 1,
            'effect' : _quenchingPotion
            },
        'Neutralizing Potion' :
            {
            'goldValue' : 25,
            'level' : 5,
            'effect' : _neutralizingPotion
            },
        'Clotting Potion' :
            {
            'goldValue' : 7000,
            'level' : 5,
            'effect' : _clottingPotion
            },
        'Rock Potion' :
            {
            'goldValue' : 120,
            'level' : 5,
            'effect' : _rockPotion
            },
        'Prismatic Potion' :
            {
            'goldValue' : 150,
            'level' : 5,
            'effet' : _prismaticPotion
            },
            # TODO: Other buffing potions go here.
        }
    allPoisons = {
        'Basic Poison' : 
            {
            'goldValue' : 10,
            'level' : 1,
            'effect' : _basicPoison,
            }
            # TODO: Other poisons go here.
        }   
        # TODO: Scrolls/Oils and Effusions
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
		
		