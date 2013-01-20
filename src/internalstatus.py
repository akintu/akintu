#!/usr/bin/python

import sys

class InternalStatus(object):
    def __init__(self):
        self.name = None
        # self._parentStatus = None ... is this needed?
        self.immunity = None
        self.magnitude = None # inherit from caller if 0.      
        self.applyEffect = None
        self.unapplyEffect = None
        self.minList = 0
        self.maxList = 0
        self.conditional = None
        self.chance = 100
        self.upkeepApply = None
        # Element??
        self._loadedFromFile = False
       
    @property
    def loadedFromFile(self):
        """ """
        return self._loadedFromFile
    
    def assignImmunity(self, immunity):
        """ Assigns the immunity to this internal as is listed at the bottom of the data file."""
        self.immunity = immunity
    
    def populateFromFile(self, name, magnitude, conditional, chance, min, max):
        """Populates the fields of this status from the information gained
        through a parser from a txt file."""
        if( self._loadedFromFile ):
            return
        self.name = name
        self.magnitude = magnitude
        self.conditional = conditional
        self.chance = chance
        #self.applyEffect = applyFunctionDict[name]
        #self.unapplyEffect = unapplyFunctionDict[name]
        self._loadedFromFile = True
    
    
    # applyFunctionDict = \
        # {#'AI_attack_nearby' : 
         #'AI_flee' :
         # 'Applied_poison_rating_bonus' : (lambda target, magnitude: target.equipmentPoisonRatingBonus += magnitude),
         # 'Attack_power_bonus': lambda target, magnitude: target.attackPower *= (1 + magnitude / 100), 
         # 'Attack_power_penalty': lambda target, magnitude: target.attackPower *= (1 - magnitude / 100),
         # 'Arcane_archer_mana_regen_penalty': lambda target, magnitude: target.arcaneArcherManaRegenBase -= magnitude, 
         # 'Armor_penetration_bonus': lambda target, magnitude: target.statusArmorPenetration += magnitude,
         # 'Avoidance': lambda target, magnitude: target.avoidanceChance = magnitude,
         # 'Bleeding': lambda target, magnitude: target.HP -= (target.HP * magnitude / 100), 
         # 'Combo_attack_internal': None,
         # 'Crane_style': None,
         # 'Critical_chance_bonus': lambda target, magnitude: target.statusCriticalChance += magnitude,
         # 'Critical_magnitude_bonus': lambda target, magnitude: target.statusCriticalMagnitude += magnitude,
         # 'Damage_over_time': lambda target, magnitude, min, max: # TODO: Apply damage to target  ,
         # 'Dodge_bonus': lambda target, magnitude: target.statusDodge += magnitude,
         # 'Dodge_penalty': lambda target, magnitude: target.statusDodge -= magnitude, 
         # 'Dragon_style': None,
         # 'DR_bonus': lambda target, magnitude: target.statusDR += magnitude,
         # 'DR_penalty': lambda target, magnitude: target.statusDR -= magnitude,
         # 'Elemental_resistance_arcane': lambda target, magnitude: target.statusArcaneResistance += magnitude,
         # 'Elemental_resistance_cold': lambda target, magnitude: target.statusColdResistance += magnitude,
         # 'Elemental_resistance_divine': lambda target, magnitude: target.statusDivineResistance += magnitude,
         # 'Elemental_resistance_electric': lambda target, magnitude: target.statusElectricResistance += magnitude,
         # 'Elemental_resistance_fire': lambda target, magnitude: target.statusFireResistance += magnitude,
         # 'Elemental_resistance_poison': lambda target, magnitude: target.statusPoisonResistance += magnitude,
         # 'Elemental_resistance_shadow': lambda target, magnitude: target.statusShadowResistance += magnitude,
         # 'Elemental_vulnerability': lambda target, magnitude, element: target.lowerElementalResistance(element, magnitude), 
         # 'Hidden': None,
         # 'Hidden_double_cunning': None,
         # 'HP_buffer': lambda target, magnitude: target.applyHPBuffer(magnitude),
         # 'Increased_movement_AP_cost': lambda target, magnitude: target.movementAPCost += magnitude, 
         # 'Magic_resist_bonus': lambda target, magnitude: target.statusMagicResist += magnitude,
         # 'Magic_resist_penalty': lambda target, magnitude: target.statusMagicResist -= magnitude,
         # 'Melee_accuracy_bonus': lambda target, magnitude: target.statusMeleeAccuracy += magnitude,
         # 'Melee_accuracy_penalty': lambda target, magnitude: target.statusMeleeAccuracy -= magnitude,
         # 'Melee_dodge_bonus': lambda target, magnitude: target.statusMeleeDodge += magnitude,
         # 'Melee_force_bonus': lambda target, magnitude: target.statusForce += magnitude,
         # 'Might_bonus': lambda target, magnitude: target.statusMight += magnitude,
         # 'Movement_speed_penalty': lambda target, magnitude: target.movementTiles -= magnitude, # Monsters
         # 'No_turn': lambda target, magnitude: target.AP = 0, 
         # 'On_hit_cripple_weapon': lambda target, chance, conditional, magnitude: /
                                  # target.applyOnHitMod('On_hit_cripple_weapon', conditional, chance, magnitude, 'Movement_speed_penalty'),
         # 'On_hit_frost_weapon': lambda target, chance, conditional, magnitude1, magnitude2: /
                                  # target.applyOnHitMod('On_hit_frost_weapon', conditional, chance, magnitude1, 'Movement_speed_penalty',  
                                                        # magnitude2, 'Dodge_penalty'),
         # 'On_hit_stun': lambda target, chance, conditional: /
                          # target.applyOnHitMod('On_hit_stun', conditional, chance, 0, 'No_turn'),
        # 'On_hit_spell_failure': TODO
         # 'On_hit_suppressing_weapon': lambda target, chance, conditional, magnitude1, magnitude2, magnitude3: /
                                       # target.applyOnHitMod('On_hit_suppressing_weapon', conditional, chance, magnitude1, 'Melee_accuracy_penalty',
                                                             # magnitude2, 'Ranged_accuracy_penalty', magnitude3, 'Attack_power_penalty'),
         # 'Overall_damage_bonus': lambda target, magnitude: target.statusOverallDamageBonus += magnitude,                                                     
         # 'Overall_damage_penalty': lambda target, magnitude: target.statusOverallDamageBonus -= magnitude,
         # 'Panther_style': None, 
         # 'Poison_tolerance_bonus': lambda target, magnitude: target.statusPoisonTolerance += magnitude,                         
         # 'Poison_tolerance_penalty': lambda target, magnitude: target.statusPoisonTolerance -= magnitude, 
         # 'Potion_effect_bonus': lambda target, magnitude: target.statusPotionEffect += magnitude,
         # 'Prepare_melee_dodge_counterattack': None,
         # 'Ranged_accuracy_bonus': lambda target, magnitude: target.statusRangedAccuracy += magnitude,
         # 'Ranged_accuracy_penalty': lambda target, magnitude: target.statusRangedAccuracy -= magnitude,
         # 'Ranged_critical_magnitude_bonus': lambda target, magnitude: target.statusRangedCriticalMagnitude += magnitude,
         # 'Ranged_dodge_bonus': lambda target, magnitude: target.statusRangedDodge += magnitude, 
         # 'Ranged_force_bonus': lambda target, magnitude: target.statusRangedForce += magnitude,
         # 'Recover_HP_percent': lambda target, magnitude: target.HP += (target.totalHP * magnitude / 100),
         # 'Redirect_melee_attacks': None, # Include magnitude How?
         # 'Reduced_stealth_AP_cost': lambda target, magnitude: target.abilityAPModsList.extend([['Stealth', -magnitude], 
                                                                                              # ['Shadow Walk', -magnitude],
                                                                                              # ['Conceal', -magnitude]])
         # 'Reduced_missile_range': lambda target, magnitude: target.missleRange -= magnitude, #Monster only
         # 'Refund_mana_on_cast' : None,
         # 'Send_empathy_damage_to_summon' : lambda target, magnitude: target.empathyToSummon = magnitude,
         # 'Set_maximum_stealth_break_chance': lambda target, magnitude: target.stealthBreakMaxOverride = magnitude, 
         # 'Set_movement_AP_cost': lambda target, magnitude: target.movementAPOverride = magnitude,
         # 'Snake_style': None,
         # 'Sneak_bonus': lambda target, magnitude: target.statusSneak += magnitude,
         # 'Sneak_penalty': lambda target, magnitude: target.statusSneak -= magnitude,
         # 'Spellpower_bonus': lambda target, magnitude: target.statusSpellpower += magnitude,
         # 'Spellpower_penalty': lambda target, magnitude: target.statusSpellpower -= magnitude,
         # 'Spell_failure_chance': lambda target, magnitude: target.spellFailureChance += magnitude,
         #'Target_ranged_accuracy_bonus':
         #'Target_ranged_dodge_bonus':
         #'Target_ranged_dodge_penalty_marksman':
         # 'Tiger_style': None,
         # 'Trap_evade_bonus': lambda target, magnitude: target.statusTrapEvade += magnitude,
         # 'Trap_evade_penalty': lambda target, magnitude: target.statusTrapEvade -= magnitude
         #'Weapon_damage_bonus': lambda target, magnitude, element: 
        # }
        
        
        
    # unapplyFunctionDict = \
        # {#'AI_attack_nearby' : 
         #'AI_flee' :
         # 'Applied_poison_rating_bonus': lambda target, magnitude: target.equipmentPoisonRatingBonus -= magnitude,
         # 'Attack_power_bonus': lambda target, magnitude: target.attackPower /= (1 + magnitude / 100), 
         # 'Attack_power_penalty': lambda target, magnitude: target.attackPower /= (1 - magnitude / 100),
         # 'Arcane_archer_mana_regen_penalty': lambda target, magnitude: target.arcaneArcherManaRegenBase += magnitude, 
         # 'Armor_penetration_bonus': lambda target, magnitude: target.statusArmorPenetration -= magnitude,
         # 'Avoidance': lambda target, magnitude: target.avoidanceChance = 0,
         # 'Bleeding': None,
         # 'Combo_attack_internal': None,
         # 'Crane_style': None,
         # 'Critical_chance_bonus': lambda target, magnitude: target.statusCriticalChance -= magnitude,
         # 'Critical_magnitude_bonus': lambda target, magnitude: target.statusCriticalMagnitude -= magnitude,
         # 'Damage_over_time': None,
         # 'Dodge_bonus': lambda target, magnitude: target.statusDodge -= magnitude,
         # 'Dodge_penalty': lambda target, magnitude: target.statusDodge += magnitude,
         # 'Dragon_style': None,
         # 'DR_bonus': lambda target, magnitude: target.statusDR -= magnitude,
         # 'DR_penalty': lambda target, magnitude: target.statusDR -= magnitude,
         # 'Elemental_resistance_arcane': lambda target, magnitude: target.statusArcaneResistance -= magnitude,
         # 'Elemental_resistance_cold': lambda target, magnitude: target.statusColdResistance -= magnitude,
         # 'Elemental_resistance_electric': lambda target, magnitude: target.statusElectricResistance -= magnitude,
         # 'Elemental_resistance_fire': lambda target, magnitude: target.statusFireResistance -= magnitude,
         # 'Elemental_resistance_poison': lambda target, magnitude: target.statusPoisonResistance -= magnitude,
         # 'Elemental_resistance_shadow': lambda target, magnitude: target.statusShadowResistance -= magnitude,
         # 'Elemental_vulnerability': lambda target, magnitude, element: target.raiseElementalResistance(element, magnitude),
         # 'Hidden': None,
         # 'Hidden_double_cunning': None,
         # 'HP_buffer': None, # Clear HP buffer??
         # 'Increased_movement_AP_cost': lambda target, magnitude: target.movementAPCost -= magnitude, 
         # 'Magic_resist_bonus': lambda target, magnitude: target.statusMagicResist -= magnitude,
         # 'Magic_resist_penalty': lambda target, magnitude: target.statusMagicResist += magnitude,
         # 'Melee_accuracy_bonus': lambda target, magnitude: target.statusMeleeAccuracy -= magnitude,
         # 'Melee_accuracy_penalty': lambda target, magnitude: target.statusMeleeAccuracy += magnitude,
         # 'Melee_dodge_bonus': lambda target, magnitude: target.statusMeleeDodge -= magnitude,
         # 'Melee_force_bonus': lambda target, magnitude: target.statusForce -= magnitude,
         # 'Might_bonus': lambda target, magnitude: target.statusMight -= magnitude,
         # 'Movement_speed_penalty': lambda target, magnitude: target.movementTiles += magnitude, # Monsters
         # 'No_turn': None,
         # 'On_hit_cripple_weapon': lambda target: target.removeOnHitMod('On_hit_cripple_weapon'),
         # 'On_hit_frost_weapon': lambda target: target.removeOnHitMod('On_hit_frost_weapon'),
         # 'On_hit_stun': lambda target: target.removeOnHitMod('On_hit_stun'),
         #'On_hit_spell_failure':
         # 'On_hit_suppressing_weapon': lambda target: target.removeOnHitMod('On_hit_suppressing_weapon'),
         # 'Overall_damage_bonus': lambda target, magnitude: target.statusOverallDamageBonus -= magnitude,    
         # 'Overall_damage_penalty': lambda target, magnitude: target.statusOverallDamageBonus += magnitude,
         # 'Panther_style': None,
         # 'Poison_tolerance_bonus': lambda target, magnitude: target.statusPoisonTolerance -= magnitude,
         # 'Poison_tolerance_penalty': lambda target, magnitude: target.statusPoisonTolerance += magnitude,
         # 'Potion_effect_bonus': lambda target, magnitude: target.statusPotionEffect -= magnitude,
         # 'Prepare_melee_dodge_counterattack': None,
         # 'Ranged_accuracy_bonus': lambda target, magnitude: target.statusRangedAccuracy -= magnitude,
         # 'Ranged_accuracy_penalty': lambda target, magnitude: target.statusRangedAccuracy += magnitude,
         # 'Ranged_critical_magnitude_bonus': lambda target, magnitude: target.statusRangedCriticalMagnitude -= magnitude,
         # 'Ranged_dodge_bonus': lambda target, mangitude: target.statusRangedDodge -= magnitude,
         # 'Ranged_force_bonus': lambda target, magnitude: target.statusRangedForce -= magnitude,
         # 'Recover_HP_percent': None, 
         # 'Redirect_melee_attacks': None,
         #'Reduced_stealth_AP_cost': lambda target, magnitude: /
         #                            target.abilityAPModsList.remove(['Shadow Walk', -magnitude]).remove(['Conceal', -magnitude]).remove(['Stealth', -magnitude])
         # 'Reduced_missile_range': lambda target, magnitude: target.missleRange += magnitude,
         # 'Refund_mana_on_cast': None,
         # 'Send_empathy_damage_to_summon' : lambda target, magnitude: target.empathyToSummon = 0,
         # 'Set_maximum_stealth_break_chance': lambda target, magnitude: target.stealthBreakMaxOverride = 100,
         # 'Set_movement_AP_cost': lambda target, magnitude: target.movementAPOverride = -1,
         # 'Snake_style': None,
         # 'Sneak_bonus': lambda target, magnitude: target.statusSneak -= magnitude,
         # 'Sneak_penalty': lambda target, magnitude: target.statusSneak += magnitude,
         # 'Spellpower_bonus': lambda target, magnitude: target.statusSpellpower -= magnitude,
         # 'Spellpower_penalty': lambda target, magnitude: target.statusSpellpower += magnitude,
         # 'Spell_failure_chance': lambda target, magnitude: target.spellFailureChance -= magnitude,
         #'Target_ranged_accuracy_bonus':
         #'Target_ranged_dodge_bonus':
         #'Target_ranged_dodge_penalty_marksman':
         # 'Tiger_style': None,
         # 'Trap_evade_bonus': lambda target, magnitude: target.statusTrapEvade -= magnitude,
         # 'Trap_evade_penalty': lambda target, magnitude: target.statusTrapEvade += magnitude
         #'Weapon_damage_bonus': lambda target, magnitude, element: 
        # }
  
  


    
