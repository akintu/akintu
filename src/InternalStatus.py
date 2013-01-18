#!/usr/bin/python

import sys

class InternalStatus(object):
    def __init__(self):
	    self._name = None
		# self._parentStatus = None ... is this needed?
		self._immunity = None		
		self.applyEffect = None
        self.unapplyEffect = None
	
	# TODO attribute getters/setters
	
	
	
	applyFunctionDict = /
        (#'AI_attack_nearby' : 
	     #'AI_flee' :
	     'Applied_poison_rating_bonus': lambda target, magnitude: target.equipmentPoisonRatingBonus += magnitude,
		 'Attack_power_bonus': lambda target, magnitude: target.attackPower *= (1 + magnitude / 100), 
		 'Attack_power_penalty': lambda target, magnitude: target.attackPower *= (1 - magnitude / 100),
		 'Arcane_archer_mana_regen_penalty': lambda target, magnitude: target.arcaneArcherManaRegenBase -= magnitude, 
		 'Armor_penetration_bonus': lambda target, magnitude: target.statusArmorPenetration += magnitude,
		 'Avoidance': lambda target, magnitude: target.avoidanceChance = magnitude,
		 'Bleeding': lambda target, magnitude: target.HP -= (target.HP * magnitude / 100), 
		 'Combo_attack_internal': None,
		 'Crane_style': None,
		 'Critical_chance_bonus': lambda target, magnitude: target.statusCriticalChance += magnitude,
		 'Critical_magnitude_bonus': lambda target, magnitude: target.statusCriticalMagnitude += magnitude,
		 'Damage_over_time': lambda target, magnitude, min, max: # TODO: Apply damage to target  ,
		 'Dodge_bonus': lambda target, magnitude: target.statusDodge += magnitude,
		 'Dodge_penalty': lambda target, magnitude: target.statusDodge -= magnitude, 
		 'Dragon_style': None,
		 'DR_bonus': lambda target, magnitude: target.statusDR += magnitude,
		 'DR_penalty': lambda target, magnitude: target.statusDR -= magnitude,
		 'Elemental_resistance_arcane': lambda target, magnitude: target.statusArcaneResistance += magnitude,
		 'Elemental_resistance_cold': lambda target, magnitude: target.statusColdResistance += magnitude,
		 'Elemental_resistance_divine': lambda target, magnitude: target.statusDivineResistance += magnitude,
		 'Elemental_resistance_electric': lambda target, magnitude: target.statusElectricResistance += magnitude,
		 'Elemental_resistance_fire': lambda target, magnitude: target.statusFireResistance += magnitude,
		 'Elemental_resistance_poison': lambda target, magnitude: target.statusPoisonResistance += magnitude,
		 'Elemental_resistance_shadow': lambda target, magnitude: target.statusShadowResistance += magnitude,
		 'Elemental_vulnerability': lambda target, magnitude, element: target.lowerElementalResistance(element, magnitude), 
		 'Hidden': None,
		 'Hidden_double_cunning': None,
		 'HP_buffer': lambda target, magnitude: target.applyHPBuffer(magnitude),
		 'Increased_movement_AP_cost': lambda target, magnitude: target.movementAPCost += magnitude, 
		 'Magic_resist_bonus': lambda target, magnitude: target.statusMagicResist += magnitude,
		 'Magic_resist_penalty': lambda target, magnitude: target.statusMagicResist -= magnitude,
		 'Melee_accuracy_bonus': lambda target, magnitude: target.statusMeleeAccuracy += magnitude,
		 'Melee_accuracy_penalty': lambda target, magnitude: target.statusMeleeAccuracy -= magnitude,
		 'Melee_dodge_bonus': lambda target, magnitude: target.statusMeleeDodge += magnitude,
		)
		
	unapplyFunctionDict = /
	    (#'AI_attack_nearby' : 
	     #'AI_flee' :
		 'Applied_poison_rating_bonus': lambda target, magnitude: target.equipmentPoisonRatingBonus -= magnitude,
		 'Attack_power_bonus': lambda target, magnitude: target.attackPower /= (1 + magnitude / 100), 
		 'Attack_power_penalty': lambda target, magnitude: target.attackPower /= (1 - magnitude / 100),
		 'Arcane_archer_mana_regen_penalty': lambda target, magnitude: target.arcaneArcherManaRegenBase += magnitude, 
		 'Armor_penetration_bonus': lambda target, magnitude: target.statusArmorPenetration -= magnitude,
		 'Avoidance': lambda target, magnitude: target.avoidanceChance = 0,
		 'Bleeding': None,
		 'Combo_attack_internal': None,
		 'Crane_style': None,
		 'Critical_chance_bonus': lambda target, magnitude: target.statusCriticalChance -= magnitude,
		 'Critical_magnitude_bonus': lambda target, magnitude: target.statusCriticalMagnitude -= magnitude,
		 'Damage_over_time': None,
		 'Dodge_bonus': lambda target, magnitude: target.statusDodge -= magnitude,
		 'Dodge_penalty': lambda target, magnitude: target.statusDodge += magnitude,
		 'Dragon_style': None,
		 'DR_bonus': lambda target, magnitude: target.statusDR -= magnitude,
		 'DR_penalty': lambda target, magnitude: target.statusDR -= magnitude,
		 'Elemental_resistance_arcane': lambda target, magnitude: target.statusArcaneResistance -= magnitude,
         'Elemental_resistance_cold': lambda target, magnitude: target.statusColdResistance -= magnitude,
         'Elemental_resistance_electric': lambda target, magnitude: target.statusElectricResistance -= magnitude,
         'Elemental_resistance_fire': lambda target, magnitude: target.statusFireResistance -= magnitude,
		 'Elemental_resistance_poison': lambda target, magnitude: target.statusPoisonResistance -= magnitude,
         'Elemental_resistance_shadow': lambda target, magnitude: target.statusShadowResistance -= magnitude,
         'Elemental_vulnerability': lambda target, magnitude, element: target.raiseElementalResistance(element, magnitude),
		 'Hidden': None,
		 'Hidden_double_cunning': None,
		 'HP_buffer': None, # Clear HP buffer??
		 'Increased_movement_AP_cost': lambda target, magnitude: target.movementAPCost -= magnitude, 
		 'Magic_resist_bonus': lambda target, magnitude: target.statusMagicResist -= magnitude,
		 'Magic_resist_penalty': lambda target, magnitude: target.statusMagicResist += magnitude,
		 'Melee_accuracy_bonus': lambda target, magnitude: target.statusMeleeAccuracy -= magnitude,
		 'Melee_accuracy_penalty': lambda target, magnitude: target.statusMeleeAccuracy += magnitude,
		 'Melee_dodge_bonus': lambda target, magnitude: target.statusMeleeDodge -= magnitude,
		 
        )
  
  
  
  # [NAME: Melee_force_bonus]
  # [TYPE: Internal]
  
# [NAME: Might_bonus]
  # [TYPE: Internal]
  
# [NAME: Movement_speed_penalty]
  # [TYPE: Internal]
  # [IMMUNE: Boss]
  
# [NAME: No_turn]
  # [TYPE: Internal]
  # [IMMUNE: Boss]
  
# [NAME: On_hit_cripple_weapon]
  # [TYPE: Internal]
  
# [NAME: On_hit_frost_weapon]
  # [TYPE: Internal]
  
# [NAME: On_hit_stun]
  # [TYPE: Internal]
  
# [NAME: On_hit_spell_failure]
  # [TYPE: Internal]
  
# [NAME: On_hit_suppressing_weapon]
  # [TYPE: Internal]
  
# [NAME: Overall_damage_bonus]
  # [TYPE: Internal]
  
# [NAME: Overall_damage_penalty]
  # [TYPE: Internal]
  
# [NAME: Panther_style]
  # [TYPE: Internal]
  
# [NAME: Poison_tolerance_bonus]
  # [TYPE: Internal]

# [NAME: Poison_tolerance_penalty]
  # [TYPE: Internal]
  
# [NAME: Potion_effect_bonus]
  # [TYPE: Internal]
  
# [NAME: Prepare_melee_dodge_counterattack]
  # [TYPE: Internal]
  
# [NAME: Ranged_accuracy_bonus]
  # [TYPE: Internal]
  
# [NAME: Ranged_accuracy_penalty]
  # [TYPE: Internal]
  # [IMMUNE: None]

# [NAME: Ranged_critical_magnitude_bonus]
  # [TYPE: Internal]
  
# [NAME: Ranged_dodge_bonus]
  # [TYPE: Internal]
  
# [NAME: Ranged_force_bonus]
  # [TYPE: Internal]
  
# [NAME: Recover_HP_percent]
  # [TYPE: Internal]
  
# [NAME: Redirect_melee_attacks]
  # [TYPE: Internal]
  
# [NAME: Reduced_stealth_AP_cost]
  # [TYPE: Internal]
  
# [NAME: Reduced_missile_range]
  # [TYPE: Internal]
  
# [NAME: Refund_mana_on_cast]
  # [TYPE: Internal]
  
# [NAME: Send_empathy_damage_to_summon]
  # [TYPE: Internal]
  
# [NAME: Set_maximum_stealth_break_chance]
  # [TYPE: Internal]
  
# [NAME: Set_movement_AP_cost]
  # [TYPE: Internal]
  
# [NAME: Snake_style]
  # [TYPE: Internal]
  
# [NAME: Sneak_bonus]
  # [TYPE: Internal]
  
# [NAME: Sneak_penalty]
  # [TYPE: Internal]
  
# [NAME: Spellpower_bonus]
  # [TYPE: Internal]
  
# [NAME: Spellpower_penalty]
  # [TYPE: Internal]
  # [IMMUNE: None]

# [NAME: Spell_failure_chance]
  # [TYPE: Internal]
  # [IMMUNE: Boss]  
	
# [NAME: Target_ranged_accuracy_bonus]
  # [TYPE: Internal]
  
# [NAME: Target_ranged_dodge_bonus]
  # [TYPE: Internal]

# [NAME: Target_ranged_dodge_penalty_marksman]
  # [TYPE: Internal]
  
# [NAME: Tiger_style]
  # [TYPE: Internal]
  
# [NAME: Trap_evade_bonus]
  # [TYPE: Internal]
  
# [NAME: Trap_evade_penalty]
  # [TYPE: Internal]
  # [IMMUNE: Boss]
	
# [NAME: Weapon_damage_bonus]
  # [TYPE: Internal]
