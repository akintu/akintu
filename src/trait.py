#!/usr/bin/python

import sys
import listener

class Trait(object):
    
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        content = allContentByName[name]
        self.requiredClass = content['class']    
        self.type = content['type']
        self.action = content['action']
        self.rank = 1
        self.onStringList = None
        self.offStringList = None
        self.extraStaticAction = None
        if self.type == 'dynamic' or self.type == "dynamic and static":
            self.onStringList = content['onString']
            self.offStringList = content['offString']
            self.registerListener()
        else: 
            self.action(self.owner)
        if self.type == "dynamic and static":
            self.extraStaticAction = content['staticAction']
            self.extraStaticAction(self.owner)
        
        
    def advanceTier(self):
        if self.rank == 4:
            return
        if self.rank == 3 and player.level < 7:
            return
        if self.rank == 2 and player.level < 5:
            return
        if self.rank == 1 and player.level < 3:
            return
        self.rank += 1
        if self.type == "static":
            self.action(self.owner)
            
    @staticmethod
    def getTraitRank(player, traitName):
        for t in player.traits:
            if t.name == traitName:
                return t.rank
        return 0
 
    def registerListener(self):
        newListener = listener.Listener(self.owner, self.onStringList, self.action, self.offStringList)
        owner.listeners.append(newListener) 
            
    @staticmethod
    def applyParry(target, reverse=False, attacker=None):
        #if target.facingAttacker() TODO
        tRank = getTraitRank(target, "Parry")
        if not reverse:
            if tRank == 1:
                target.statusDodge += 2
            elif tRank == 2:
                target.statusDodge += 4
            elif tRank == 3:
                target.statusDodge += 6
            elif tRank == 4:
                target.statusDodge += 11
        else:
            if tRank == 1:
                target.statusDodge -= 2
            elif tRank == 2:
                target.statusDodge -= 4
            elif tRank == 3:
                target.statusDodge -= 6
            elif tRank == 4:
                target.statusDodge -= 11
                
    @staticmethod
    def applyPreparation(target, reverse=False, other=None):
        if target.attacksPerformed[0] > 0:
            return
        tRank = getTraitRank(target, "Preparation")
        if not reverse:
            if tRank == 1:
                target.statusMeleeAccuracy += 8
                target.statusRangedAccuracy += 8
            elif tRank == 2:
                target.statusMeleeAccuracy += 11
                target.statusRangedAccuracy += 11
            elif tRank == 3:
                target.statusMeleeAccuracy += 14
                target.statusRangedAccuracy += 14
            elif tRank == 4:
                target.statusMeleeAccuracy += 18
                target.statusRangedAccuracy += 18
        else:
            if tRank == 1:
                target.statusMeleeAccuracy -= 8
                target.statusRangedAccuracy -= 8
            elif tRank == 2:
                target.statusMeleeAccuracy -= 11
                target.statusRangedAccuracy -= 11
            elif tRank == 3:
                target.statusMeleeAccuracy -= 14
                target.statusRangedAccuracy -= 14
            elif tRank == 4:
                target.statusMeleeAccuracy -= 18
                target.statusRangedAccuracy -= 18        
    
    @staticmethod
    def applyTank(target, reverse=False, other=None):
        if not target.usingArmor("Heavy"):
            return
        tRank = getTraitRank(target, "Tank")
        if not reverse:
            if tRank == 1:
                target.statusDR += 1
            elif tRank == 2:
                target.statusDR += 2
            elif tRank == 3:
                target.statusDR += 4
            elif tRank == 4:
                target.statusDR += 7
        else:
            if tRank == 1:
                target.statusDR -= 1
            elif tRank == 2:
                target.statusDR -= 2
            elif tRank == 3:
                target.statusDR -= 4
            elif tRank == 4:
                target.statusDR -= 7            
            
    @staticmethod
    def applyFencer(target, reverse=False, other=None):
        if not target.usingArmor("Medium"):
            return
        tRank = getTraitRank(target, "Fencer")
        if not reverse:
            if tRank == 1:
                target.statusMeleeAccuracy += 2
            elif tRank == 2:
                target.statusMeleeAccuracy += 4
            elif tRank == 3:
                target.statusMeleeAccuracy += 6
            elif tRank == 4:
                target.statusMeleeAccuracy += 9
        else:
            if tRank == 1:
                target.statusMeleeAccuracy -= 2
            elif tRank == 2:
                target.statusMeleeAccuracy -= 4
            elif tRank == 3:
                target.statusMeleeAccuracy -= 6
            elif tRank == 4:
                target.statusMeleeAccuracy -= 9            

    @staticmethod
    def applyShieldResilience(target, reverse=False, other=None):
        if not target.usingShield("Any"):
            return
        tRank = getTraitRank(target, "Shield Resilience")
        if not reverse:
            if tRank == 1:
                target.knockbackResistance += 30
                target.statusRangedDodge += 1
            elif tRank == 2:
                target.knockbackResistance += 60
                target.statusRangedDodge += 2
            elif tRank == 3:
                target.knockbackResistance += 90
                target.statusRangedDodge += 3
            elif tRank == 4:
                target.knockbackResistance += 100
                target.statusRangedDodge += 4
        else:
            if tRank == 1:
                target.knockbackResistance -= 30
                target.statusRangedDodge -= 1
            elif tRank == 2:
                target.knockbackResistance -= 60
                target.statusRangedDodge -= 2
            elif tRank == 3:
                target.knockbackResistance -= 90
                target.statusRangedDodge -= 3
            elif tRank == 4:
                target.knockbackResistance -= 100
                target.statusRangedDodge -= 4            
         
    @staticmethod
    def applyBully(target, reverse=False, victim=None):
        if not target.usingWeaponStyle("Two-Handed") or victim.size == "Large" or victim.size == "Huge":
            return
        tRank = getTraitRank(target, "Bully")
        if not reverse:
            if tRank == 1:
                target.statusForce += 5
                target.statusMeleeAccuracy += 2
                target.statusRangedAccuracy += 2
                target.statusCriticalChance += 0.5
            elif tRank == 2:
                target.statusForce += 10
                target.statusMeleeAccuracy += 3
                target.statusRangedAccuracy += 3
                target.statusCriticalChance += 1
            elif tRank == 3:
                target.statusForce += 15
                target.statusMeleeAccuracy += 4
                target.statusRangedAccuracy += 4
                target.statusCriticalChance += 1.5
            elif tRank == 4:
                target.statusForce += 25
                target.statusMeleeAccuracy += 5
                target.statusRangedAccuracy += 5
                target.statusCriticalChance += 2
        else:
            if tRank == 1:
                target.statusForce -= 5
                target.statusMeleeAccuracy -= 2
                target.statusRangedAccuracy -= 2
                target.statusCriticalChance -= 0.5
            elif tRank == 2:
                target.statusForce -= 10
                target.statusMeleeAccuracy -= 3
                target.statusRangedAccuracy -= 3
                target.statusCriticalChance -= 1
            elif tRank == 3:
                target.statusForce -= 15
                target.statusMeleeAccuracy -= 4
                target.statusRangedAccuracy -= 4
                target.statusCriticalChance -= 1.5
            elif tRank == 4:
                target.statusForce -= 25
                target.statusMeleeAccuracy -= 5
                target.statusRangedAccuracy -= 5
                target.statusCriticalChance -= 2        
                
    @staticmethod
    def applyBoldness(target, reverse=False, victim=None):
        if victim.size == "Small" or victim.size == "Medium":
            return
        tRank = getTraitRank(target, "Boldness")
        if not reverse:
            if victim.size == "Large":
                if tRank == 1:
                    target.statusForce += 5
                if tRank == 2:
                    target.statusForce += 10
                if tRank == 3:
                    target.statusForce += 15
                if tRank == 4:
                    target.statusForce += 20
            elif victim.size == "Huge":
                if tRank == 1:
                    target.statusForce += 15
                if tRank == 2:
                    target.statusForce += 30
                if tRank == 3:
                    target.statusForce += 45
                if tRank == 4:
                    target.statusForce += 60
        else:
            if victim.size == "Large":
                if tRank == 1:
                    target.statusForce -= 5
                if tRank == 2:
                    target.statusForce -= 10
                if tRank == 3:
                    target.statusForce -= 15
                if tRank == 4:
                    target.statusForce -= 20
            elif victim.size == "Huge":
                if tRank == 1:
                    target.statusForce -= 15
                if tRank == 2:
                    target.statusForce -= 30
                if tRank == 3:
                    target.statusForce -= 45
                if tRank == 4:
                    target.statusForce -= 60        
    
    @staticmethod    
    def applyWellTraveled(target):
        tRank = getTraitRank(target, "Well-Traveled")
        if tRank == 1:
            target._baseInventoryCapacity += 15
            target.baseFireResistance += 1
            target.baseColdResistance += 1
        if tRank == 2:
            target._baseInventoryCapacity += 15
            target.baseFireResistance += 1
            target.baseColdResistance += 1
        if tRank == 3:
            target._baseInventoryCapacity += 15
            target.baseFireResistance += 1
            target.baseColdResistance += 1
        if tRank == 4:
            target._baseInventoryCapacity += 25
            target.baseFireResistance += 2
            target.baseColdResistance += 2            
        
    @staticmethod
    def applyHammerAndAnvil(target, reverse=False, victim=None):
        # TODO: if target has back against wall...
        tRank = getTraitRank(target, "Hammer and Anvil")
        if not reverse: 
            if tRank == 1:
                target.baseOverallDamageBonus += 5
            elif tRank == 2:
                target.baseOverallDamageBonus += 10
            elif tRank == 3:
                target.baseOverallDamageBonus += 15
            elif tRank == 4:
                target.baseOverallDamageBonus += 20
        else:
            if tRank == 1:
                target.baseOverallDamageBonus -= 5
            elif tRank == 2:
                target.baseOverallDamageBonus -= 10
            elif tRank == 3:
                target.baseOverallDamageBonus -= 15
            elif tRank == 4:
                target.baseOverallDamageBonus -= 20
                    
    @staticmethod
    def applyReservoir(target):
        tRank = getTraitRank(target, "Reservoir")
        if tRank == 1:
            target.baseMP += 10
        elif tRank == 2:
            target.baseMP += 5
        elif tRank == 3:
            target.baseMP += 5
        elif tRank == 4:
            target.baseMP += 5
            
    @staticmethod
    def applySurvivor(target):
        tRank = getTraitRank(target, "Survivor")
        if tRank == 1:
            target.baseHP += 4
        elif tRank == 2:
            target.baseHP += 4
        elif tRank == 3:
            target.baseHP += 4
        elif tRank == 4:
            target.baseHP += 4

    @staticmethod
    def applyIllusionSpellFocusStatic(target):
        tRank = getTraitRank(target, "Illusion Spell Focus")
        if tRank == 1:
            pass
        elif tRank == 2:
            target.illusionResist += 1
        elif tRank == 3:
            target.illusionResist += 1
        elif tRank == 4:
            target.illusionResist += 2
            
    @staticmethod
    def applyIllusionSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Illusion":
            return
        tRank = getTraitRank(target, "Illusion Spell Focus")
        if not reverse:
            if tRank == 1:
                spell.MPCost -= 1
                target.statusSpellpower += 1
            elif tRank == 2:
                spell.MPCost -= 1
                target.statusSpellpower += 2
            elif tRank == 3:
                spell.MPCost -= 2
                target.statusSpellpower += 3
            elif tRank == 4:
                spell.MPCost -= 2
                target.statusSpellpower += 5
        else:
            if tRank == 1:
                spell.MPCost += 1
                target.statusSpellpower -= 1
            elif tRank == 2:
                spell.MPCost += 1
                target.statusSpellpower -= 2
            elif tRank == 3:
                spell.MPCost += 2
                target.statusSpellpower -= 3
            elif tRank == 4:
                spell.MPCost += 2
                target.statusSpellpower -= 5        
            
    @staticmethod
    def applyPrimalSpellFocusStatic(target):
        tRank = getTraitRank(target, "Primal Spell Focus")
        if tRank == 1:
            target.baseMP += 1
        elif tRank == 2:
            target.baseMP += 1
            target.primalResist += 1
        elif tRank == 3:
            target.baseMP += 1
        elif tRank == 4:
            target.baseMP += 2
            target.primalResist += 2
            
    @staticmethod
    def applyPrimalSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Primal":
            return
        tRank = getTraitRank(target, "Primal Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 2
            if tRank == 2:
                target.statusSpellpower += 4
            if tRank == 3:
                target.statusSpellpower += 6
            if tRank == 4:
                target.statusSpellpower += 8
        else:
            if tRank == 1:
                target.statusSpellpower -= 2
            if tRank == 2:
                target.statusSpellpower -= 4
            if tRank == 3:
                target.statusSpellpower -= 6
            if tRank == 4:
                target.statusSpellpower -= 8        
            
    @staticmethod
    def applyNaturalSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Natural":
            return
        tRank = getTraitRank(target, "Natural Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 1
                target.healingBonus += 5
            elif tRank == 2:
                target.statusSpellpower += 2
                target.healingBonus += 10
            elif tRank == 3:
                target.statusSpellpower += 3
                target.healingBonus += 15
            elif tRank == 4:
                target.statusSpellpower += 4
                target.healingBonus += 20
        else:
                target.statusSpellpower -= 1
                target.healingBonus -= 5
            elif tRank == 2:
                target.statusSpellpower -= 2
                target.healingBonus -= 10
            elif tRank == 3:
                target.statusSpellpower -= 3
                target.healingBonus -= 15
            elif tRank == 4:
                target.statusSpellpower -= 4
                target.healingBonus -= 20        
            
    @staticmethod
    def applyMysticSpellFocusStatic(target):
        tRank = getTraitRank(target, "Mystic Spell Focus")
        if tRank == 1:
            target.mysticResist += 1
        elif tRank == 2:
            target.mysticResist += 1
        elif tRank == 3:
            target.mysticResist += 1
        elif tRank == 4:
            target.mysticResist += 1

    @staticmethod
    def applyMysticSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Mystic":
            return
        tRank = getTraitRank(target, "Mystic Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 2
            elif tRank == 2:
                target.statusSpellpower += 4
            elif tRank == 3:
                target.statusSpellpower += 6
            elif tRank == 4:
                target.statusSpellpower += 8
        else:
            if tRank == 1:
                target.statusSpellpower -= 2
            elif tRank == 2:
                target.statusSpellpower -= 4
            elif tRank == 3:
                target.statusSpellpower -= 6
            elif tRank == 4:
                target.statusSpellpower -= 8             
            
    @staticmethod
    def applyBaneSpellFocusStatic(target):
        tRank = getTraitRank(target, "Bane Spell Focus")
        if tRank == 1:
            target.baseShadowBonusDamage += 7
        elif tRank == 2:
            target.baseShadowBonusDamage += 7
        elif tRank == 3:
            target.baseShadowBonusDamage += 7
        for spell in target.spellList:
            if spell.school == "Bane" and spell.APCost > 5:
                spell.APCost -= 1
        elif tRank == 4:
            target.baseShadowBonusDamage += 7
            
    @staticmethod
    def applyBaneSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Bane":
            return
        tRank = getTraitRank(target, "Bane Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 1
            elif tRank == 2:
                target.statusSpellpower += 2
            elif tRank == 3:
                target.statusSpellpower += 3
            elif tRank == 4:
                target.statusSpellpower += 4
        else:
            if tRank == 1:
                target.statusSpellpower -= 1
            elif tRank == 2:
                target.statusSpellpower -= 2
            elif tRank == 3:
                target.statusSpellpower -= 3
            elif tRank == 4:
                target.statusSpellpower -= 4        
            
    @staticmethod
    def applyEnchantmentSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Enchantment":
            return
        tRank = getTraitRank(target, "Enchantment Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 1
            elif tRank == 2:
                target.statusSpellpower += 2
            elif tRank == 3:
                target.statusSpellpower += 4        
            elif tRank == 4:
                target.statusSpellpower += 5
        else:
            if tRank == 1:
                target.statusSpellpower -= 1
            elif tRank == 2:
                target.statusSpellpower -= 2
            elif tRank == 3:
                target.statusSpellpower -= 4          
            elif tRank == 4:
                target.statusSpellpower -= 5      
            
    @staticmethod
    def applyEnchantmentSpellFocusStatic(target):
        tRank = getTraitRank(target, "Enchantment Spell Focus")
        for spell in target.spellList:
            if spell.type == "Enchantment":
                if tRank == 1:
                    spell.MPCost = min(5, spell.MPCost - 1)
                elif tRank == 2:
                    spell.MPCost = min(5, spell.MPCost - 1)
                elif tRank == 3:
                    break
                elif tRank == 4:
                    spellMPCost = min(5, spell.MPCost - 1)
       
    @staticmethod
    def applyMentalSpellFocusStatic(target):
        tRank = getTraitRank(target, "Mental Spell Focus")
        if tRank == 1:
            target.baseHP += 2
        elif tRank == 2:
            target.baseHP += 2
        elif tRank == 3:
            target.baseHP += 2
        elif tRank == 4:
            target.baseHP += 2
            
    @staticmethod
    def applyMentalSpellFocus(target, reverse=False, spell=None):
        if spell.school != "Mental":
            return
        tRank = getTraitRank(target, "Mental Spell Focus")
        if not reverse:
            if tRank == 1:
                target.statusSpellpower += 2
            elif tRank == 2:
                target.statusSpellpower += 4
            elif tRank == 3:
                target.statusSpellpower += 6
            elif tRank == 4:
                target.statusSpellpower += 8
        else:
            if tRank == 1:
                target.statusSpellpower -= 2
            elif tRank == 2:
                target.statusSpellpower -= 4
            elif tRank == 3:
                target.statusSpellpower -= 6
            elif tRank == 4:
                target.statusSpellpower -= 8

        
    allContentByName = {
        'Parry': 
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyParry,
            'onStringList' : ['Incoming Melee Attack'],
            'offStringList' : ['Incoming Melee Attack Complete']
            }
        ,
        'Preparation':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyPreparation,
            'onStringList' : ['Starting Player Turn'],
            'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            }
        ,
        'Tank':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyTank,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            }
        ,
        'Fencer':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyFencer,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            }
        ,
        'Shield Resilience':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyShieldResilience,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            }
        ,
        'Bully':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyBully,
            'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            }
        ,
        'Boldness':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyBoldness,
            'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
            'offStringList' : ['Outoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            }
        ,
        'Well-Traveled':
            {
            'class' : 'Fighter',
            'type' : 'static',
            'action' : applyWellTraveled,
            }
        ,
        'Hammer and Anvil':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : applyHammerAndAnvil,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            },
            
        # Wizard Traits
        'Reservoir':
            {
            'class' : 'Wizard',
            'type' : 'static',
            'action' : applyReservoir
            },
        'Survivor':
            {
            'class' : 'Wizard',
            'type' : 'static',
            'action' : applySurvivor
            },
        'Illusion Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyIllusionSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyIllusionSpellFocusStatic
            },
        'Primal Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyPrimalSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyPrimalSpellFocusStatic
            },
        'Natural Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic',
            'action' : applyNaturalSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete']
            },
        'Mystic Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyMysticSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete']
            'staticAction' : applyMysticSpellFocusStatic
            },
        'Bane Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyBaneSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyBaneSpellFocusStatic
            },
        'Enchantment Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyEnchantmentSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyEnchantmentSpellFocusStatic
            },
        'Mental Spell Focus':
            {
            'class' : 'Wizard',
            'type' : 'dynamic and static',
            'action' : applyMentalSpellFocus,
            'onStringList' : ['Outgoing Spell Cast'],
            'offStringList' : ['Outgoing Spell Cast Complete'],
            'staticAction' : applyMentalSpellFocusStatic
            }
    }

