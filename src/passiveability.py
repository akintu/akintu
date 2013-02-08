#!/usr/bin/python

import sys
import listener

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
        if self.type == 'dynamic':
            self.onStringList = content['onStringList']
            self.offStringList = content['offStringList']
            self.registerListener()
        if self.type == 'static':
            self.action(self, self.owner)
        
    def registerListener(self):
        newListener = listener.Listener(self, self.owner, self.onStringList, self.action, self.offStringList)
        self.owner.listeners.append(newListener)
        
        
    
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
    
    # Spellsword    
    def applySeekerOfEnchantments(self, targer, reverse=False, spell=None):
        if not reverse:
            if spell.school == "Enchantment":
                target.statusSpellpower += 6
        else:
            if spell.school == "Enchantment":
                target.statusSepllpower -= 6
                
    def applyDuality(self, target):
        target.baseDR += 1
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
                
    # Battle Mage
    def applyCloseRangedMagic(self, target, reverse=False, spell=None):
        if not reverse:
            if spell.range < 4:
                target.baseSpellpower += 7
        else:
            if spell.range < 4:
                target.baseSpellpower -= 7
                
    def applyManaAttack(self, target, reverse=False, other=None):
        if not reverse:
            target.MP += 9
        else:
            pass
            
    def applyDireMana(self, target, reverse=False, damageAmount=0):
        if not reverse:
            if damageAmount >= target.maxHP * 0.15:
                target.MP += target.totalMP * 0.10
        else:
            pass
            
    def applyMysticalAccuracy(self, target):
        target.baseMeleeAccuracy += 3
            
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
            
    allContentByName = {
        'Cold Endurance': 
        {
        'class' : 'Barbarian',
        'level' : 1,
        'type' : 'static',
        'action' : applyColdEndurance
        },
                 
        'Magical Vulnerability':
        {
        'class' : 'Barbarian',
        'level' : 1,
        'type' : 'static',
        'action' : applyMagicalVulnerability
        },
        
        'Mighty Weapon':
        {
        'class' : 'Barbarian',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyMightyWeapon,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
        },
        
        'Mighty Weapon':
        {
        'class' : 'Barbarian',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyTwoWeaponTargeting,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
        },
        
        
        'Seeker of Enchantments':
        {
        'class' : 'Spellsword',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applySeekerOfEnchantments,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete']
        },
        'Duality':
        {
        'class' : 'Spellsword',
        'level' : 1,
        'type' : 'static',
        'action' : applyDuality
        },
        'Lasting Enchantment':
        {
        'class' : 'Spellsword',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyLastingEnchantment,
        'onStringList' : ['Outgoing Spell Cast Complete'],
        'offStringList' : []
        },
        'Focal Point':
        {
        'class' : 'Spellsword',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyFocalPoint,
        'onStringList' : ['Outgoing Physical Attack Critical Hit'],
        'offStringList' : []
        }
        
        
        'Close-Ranged Magic':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyCloseRangedMagic,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete']
        },
        
        'Mana Attack':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyManaAttack,
        'onStringList' : ['Outgoing Melee Attack Hit'],
        'offStringList' : []
        },
        
        'Dire Mana':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyDireMana,
        'onStringList' : ['Incoming Damage'],
        'offStringList' : []
        },
        
        'Mystical Accuracy':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'static',
        'action' : applyMysticalAccuracy
        },
        
        'Mystical Shield Use':
        {
        'class' : 'Battle Mage',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyMysticalShieldUse,
        'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
        'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
        },
        
        'Rapid Retreat':
        {
        'class' : 'Battle Mage',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyRapidRetreat,
        'onStringList' : ['Starting Player Turn'],
        'offStringList' : ['Ending Player Turn']
        }
        
        
    }


                
    
    
        
        
        