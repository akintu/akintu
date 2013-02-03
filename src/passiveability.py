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
            'onString' : 'Outgoing Melee Attack',
            'offString' : 'Outgoing Melee Attack Complete'
            }
        },
        {'Mighty Weapon':
            {
            'class' : 'Barbarian',
            'level' : 2,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyTwoWeaponTargeting,
            'onString' : 'Outgoing Melee Attack',
            'offString' : 'Outgoing Melee Attack Complete'
            }
        },
        
        
        
        
        {'Close-Ranged Magic':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyCloseRangedMagic,
            'onString' : 'Outgoing Spell Cast',
            'offString' : 'Outgoing Spell Cast Complete'
            }
        },
        {'Mana Attack':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyManaAttack,
            'onString' : 'Outgoing Melee Attack Hit',
            'offString' : None
            }
        },
        {'Dire Mana':
            {
            'class' : 'Battle Mage',
            'level' : 1,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyDireMana,
            'onString' : Incoming Damage,
            'offString' : None
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
            'onString' : 'Incoming Physical Attack',
            'offString' : 'Incoming Physical Attack Complete'
            }
        },
        {'Rapid Retreat':
            {
            'class' : 'Battle Mage',
            'level' : 2,
            'type' : 'dynamic',
            'action' : PassiveAbility.applyRapidRetreat,
            'onString' : 'Starting Player Turn',
            'offString' : 'Ending Player Turn'
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
        self.onString = None
        self.offString = None
        if self.type == 'dynamic':
            self.onString = content['onString']
            self.offString = content['offString']
            self.registerListener()
        if self.type == 'static':
            self.action(self.owner)
        
    def registerListener(self):
        newListener = listener.Listener(self.owner, self.onString, self.action, self.offString)
        owner.listeners.append(newListener)
        
    @staticmethod
    def applyColdEndurance(target):
        target.baseColdResistance += 10
        
    @staticmethod
    def applyMagicalVulnerability(target):
        target.baseMagicResist -= 3
        
    @staticmethod
    def applyMightyWeapon(target, reverse=False):
        if not reverse:
            if target.usingWeaponStyle("Two-Handed"):
                target.baseMight += 6
        else:
            if target.usingWeaponStyle("Two-Handed"):
                target.baseMight -= 6
    
    @staticmethod
    def applyTwoWeaponTargeting(target, reverse=False):
        if not reverse:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy += 2
        else:
            if target.usingWeaponStyle("Dual"):
                target.baseMeleeAccuracy -= 2
                
    @staticmethod
    def applyCloseRangedMagic(target, spell, reverse=False):
        if not reverse:
            if spell.range < 4:
                target.baseSpellpower += 7
        else:
            if spell.range < 4:
                target.baseSpellpower -= 7
                
    @staticmethod
    def applyManaAttack(target, reverse=False):
        if not reverse:
            target.MP += 9
        else:
            pass
            
    #TODO: DamageBroadcast
    @staticmethod
    def applyDireMana(target, damageAmount, reverse=False):
        if not reverse:
            if damageAmount >= target.maxHP * 0.15:
                target.MP += target.totalMP * 0.10
        else:
            pass
            
    @staticmethod
    def applyMysticalAccuracy(target):
        target.baseMeleeAccuracy += 3
            
    @staticmethod
    def applyMysticalShieldUse(target, reverse=False):
        if not reverse:
            if target.usingShield("Any"):
                target.baseDR += 3
        else:
            if target.usingShield("Any"):
                target.baseDR -= 3
                
    @staticmethod
    def applyRapidRetreat(target, reverse=False):
        if not reverse:
            if target.HP < target.totalHP * 0.20:
                target.overrideMovementAPCost = 2
        else:
            target.overrideMovementAPCost = -1
            



                
    
    
        
		
		