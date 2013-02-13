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
                
    def applyBloodOnTheEdge(self, target, reverse=False, damageAmount=0):
        # No reverse possible.
        hpThreshold = round(target.totalHP * 0.30)
        if target.HP > hpThreshold:
            return
        hpThreshold = round(target.totalHP * 0.05)
        if damageAmount > hpThreshold:
            return
        return "Ignore Damage"
            
    def applyMagicalIgnorance(self, target):
        target.baseMagicResist -= 3
        
    def applyStunningRecovery(self, target, reverse=False, statusName=None):
        if statusName == "Stun" and not target.hasStatus("Stunning Recovery"):
            healing = round(target.totalHP * 0.05)
            Combat.healTarget(target, healing)
            Combat.addStatus(target, "Stunning Recovery", duration=1)
    
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
                
    def applyBladesOfReduction(self, target, reverse=False, victim=None):
        if not target.usingWeapon("Sword") and not target.usingWeapon("Axe"):
            return
        doApply = Dice.rollPresetChance(target, victim, "Reliable")
        if doApply:
            duration = -1 # Never ends
            Combat.applyStatus(victim, "Blades of Reduction", duration) 
                
                
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
            
    # Monsters
    def applyPanic(self, target, reverse=False, hero=None):
        ''' Monsters that Panic gain Dexterity (increasing their accuracy and
        dodge) every time they are hit with melee attacks when at half health
        or lower.  Lasts the entire battle and stacks. '''
        if self.HP <= 0.5 * self.totalHP:
            self.statusDexterity += 2
            
    def applyDeflectMissiles(self, target, reverse=False, hero=None):
        ''' Monsters with Deflect Missiles gain 10 Dodge and 5% DR against Ranged
        attacks.'''
        if not reverse: 
            self.statusDR += 5
            self.statusDodge += 10
        else:
            self.statusDR -= 5
            self.statusDodge -= 10
            
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
        'Two Weapon Targeting':
        {
        'class' : 'Barbarian',
        'level' : 2,
        'type' : 'dynamic',
        'action' : applyTwoWeaponTargeting,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
        },
        'Blood on the Edge':
        {
        'class' : 'Barbarian',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyBloodOnTheEdge,
        'onStringList' : ['Incoming Damage'],
        'offStringList' : []
        },
        'Magical Ignorance':
        {
        'class' : 'Barbarian',
        'level' : 3,
        'type' : 'static',
        'action' : applyMagicalIgnorance
        },
        'Stunning Recovery':
        {
        'class' : 'Barbarian',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyStunningRecovery,
        'onStringList' : ['Incoming Status Applied'],
        'offStringList' : []
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
        'onStringList' : ['Outgoing Melee Attack Critical Hit'],
        'offStringList' : []
        },
        'Blades of Reduction':
        {
        'class' : 'Spellsword',
        'level' : 4,
        'type' : 'dynamic',
        'action' : applyBladesOfReduction,
        'onStringList' : ['Outgoing Melee Attack Hit', 'Outgoing Melee Attack Critical Hit'],
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
        },
        'Military Defensive Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMilitaryDefensiveTraining,
        'onStringList' : ['Incoming Spell Cast'],
        'offStringList' : ['Incoming Spell Cast Complete']
        },
        'Military Spell Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMilitarySpellTraining,
        'onStringList' : ['Outgoing Spell Cast'],
        'offStringList' : ['Outgoing Spell Cast Complete']
        },
        'Military Offensive Training':
        {
        'class' : 'Battle Mage',
        'level' : 3,
        'type' : 'dynamic',
        'action' : applyMilitaryOffensiveTraining,
        'onStringList' : ['Outgoing Melee Attack'],
        'offStringList' : ['Outgoing Melee Attack Complete']
        },        
        
        # Monsters
        'Panic':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyPanic,
        'onStringList' : ['Incoming Melee Attack Hit'],
        'offStringList' : []
        },
        'Deflect Missiles':
        {
        'class' : 'Monster',
        'level' : 1,
        'type' : 'dynamic',
        'action' : applyDeflectMissiles,
        'onStringList' : ['Incoming Ranged Attack'],
        'offStringList' : ['Incoming Ranged Attack Complete']
        }
        
        
    }


                
    
    
        
        
        