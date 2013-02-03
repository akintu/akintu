#!/usr/bin/python

import sys
import listener

class PassiveAbility(object):
    
    allContentByName = {
        {'Cold Endurance': 
            {
            'class' : 'Barbarian',
            'level' : 1,
            'type' : 'static',
            'action' : PassiveAbility.applyColdEndurance
            }
        },            
        {'Magical Vulnerability':
            {
            'class' : 'Barbarian',
            'level' : 1,
            'type' : 'static',
            'action' : PassiveAbility.applyMagicalVulnerability
            }
        },
        {'Mighty Weapon':
            {
            'class' : 'Barbarian',
            'level' : 2,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyMightyWeapon,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            }
        },
        {'Mighty Weapon':
            {
            'class' : 'Barbarian',
            'level' : 2,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyTwoWeaponTargeting,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            }
        },
        
        
        
        
        {'Close-Ranged Magic':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyCloseRangedMagic,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete']
            }
        },
        {'Mana Attack':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyManaAttack,
            'onStringList' : ['Outgoing Melee Attack Hit'],
            'offStringList' : []
            }
        },
        {'Dire Mana':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyDireMana,
            'onStringList' : ['Incoming Damage'],
            'offStringList' : []
            }
        },
        {'Mystical Accuracy':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'static',
            'action' : PassiveAbility.applyMysticalAccuracy
            }
        },
        {'Mystical Shield Use':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyMysticalShieldUse,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            }
        },
        {'Rapid Retreat':
            {
            'class' : 'Battle Mage',
            'level' : 2,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyRapidRetreat,
            'onStringList' : ['Starting Player Turn'],
            'offStringList' : ['Ending Player Turn']
            }
        }
        
    }
    
    
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
        if self.type == 'dynamic':
            self.onStringList = content['onStringList']
            self.offStringList = content['offStringList']
            self.registerListener()
        if self.type == 'static':
            self.action(self.owner)
        
    def registerListener(self):
        newListener = listener.Listener(self.owner, self.onStringList, self.action, self.offStringList)
        owner.listeners.append(newListener)
        
    @staticmethod
    def applyColdEndurance(target):
        target.baseColdResistance += 10
        
    @staticmethod
    def applyMagicalVulnerability(target):
        target.baseMagicResist -= 3
        
    @staticmethod
    def applyMightyWeapon(target, reverse=False, other=None):
        if not reverse:
            if target.usingWeaponStyle("Two-Handed"):
                target.baseMight += 6
        else:
            if target.usingWeaponStyle("Two-Handed"):
                target.baseMight -= 6
    
    @staticmethod
    def applyTwoWeaponTargeting(target, reverse=False, other=None):
        if not reverse:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy += 2
        else:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy -= 2
                
    @staticmethod
    def applyCloseRangedMagic(target, reverse=False, spell):
        if not reverse:
            if spell.range < 4:
                target.baseSpellpower += 7
        else:
            if spell.range < 4:
                target.baseSpellpower -= 7
                
    @staticmethod
    def applyManaAttack(target, reverse=False, other=None):
        if not reverse:
            target.MP += 9
        else:
            pass
            
    #TODO: DamageBroadcast
    @staticmethod
    def applyDireMana(target, reverse=False, damageAmount=0):
        if not reverse:
            if damageAmount >= target.maxHP * 0.15:
                target.MP += target.totalMP * 0.10
        else:
            pass
            
    @staticmethod
    def applyMysticalAccuracy(target):
        target.baseMeleeAccuracy += 3
            
    @staticmethod
    def applyMysticalShieldUse(target, reverse=False, other=None):
        if not reverse:
            if target.usingShield("Any"):
                target.baseDR += 3
        else:
            if target.usingShield("Any"):
                target.baseDR -= 3
                
    @staticmethod
    def applyRapidRetreat(target, reverse=False, other=None):
        if not reverse:
            if target.HP < target.totalHP * 0.20:
                target.overrideMovementAPCost = 2
        else:
            target.overrideMovementAPCost = -1
            



                
    
    
        
		
		