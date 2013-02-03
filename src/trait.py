#!/usr/bin/python

import sys
import listener

class Trait(object):
    allContentByName = {
        {'Parry': 
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyParry,
            'onStringList' : ['Incoming Melee Attack'],
            'offStringList' : ['Incoming Melee Attack Complete']
            }
        },
        {'Preparation':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyPreparation,
            'onStringList' : ['Starting Player Turn'],
            'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            }
        },
        {'Tank':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyTank,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            }
        },
        {'Fencer':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyFencer,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            }
        },
        {'Shield Resilience':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyShieldResilience,
            'onStringList' : ['Incoming Melee Attack', 'Incoming Ranged Attack'],
            'offStringList' : ['Incoming Melee Attack Complete', 'Incoming Ranged Attack Complete']
            }
        },
        {'Bully':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyBully,
            'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            }
        },
        {'Boldness':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyBoldness,
            'onStringList' : ['Outgoing Melee Attack', 'Outgoing Ranged Attack'],
            'offStringList' : ['Outoing Melee Attack Complete', 'Outgoing Ranged Attack Complete']
            }
        },
        {'Well-Traveled':
            {
            'class' : 'Fighter',
            'type' : 'static',
            'action' : Trait.applyWellTraveled,
            }
        },
        {'Hammer and Anvil':
            {
            'class' : 'Fighter',
            'type' : 'dynamic',
            'action' : Trait.applyHammerAndAnvil,
            'onStringList' : ['Outgoing Melee Attack'],
            'offStringList' : ['Outgoing Melee Attack Complete']
            }
        }
    }

    def __init__(self, name, owner):
	    self.name = name
        self.owner = owner
        content = Trait.allContentByName[name]
        self.requiredClass = content['class']    
        self.type = content['type']
        self.action = content['action']
        self.rank = 1
        self.onStringList = None
        self.offStringList = None
        if self.type == 'dynamic':
            self.onStringList = content['onString']
            self.offStringList = content['offString']
            self.registerListener()
        else: 
            self.action(self.owner)

        
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
        tRank = Trait.getTraitRank(target, "Parry"):
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
        tRank = Trait.getTraitRank(target, "Preparation"):
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
        tRank = Trait.getTraitRank(target, "Tank"):
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
        tRank = Trait.getTraitRank(target, "Fencer"):
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
        tRank = Trait.getTraitRank(target, "Shield Resilience")
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
        tRank = Trait.getTraitRank(target, "Bully")
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
        tRank = Trait.getTraitRank(target, "Boldness")
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
        tRank = Trait.getTraitRank(target, "Well-Traveled")
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
        tRank = Trait.getTraitRank(target, "Hammer and Anvil")
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
                