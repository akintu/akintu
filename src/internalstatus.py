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
        self.applyEffect = applyFunctionDict[name]
        self.unapplyEffect = unapplyFunctionDict[name]
        self._loadedFromFile = True
    
        
    applyFunctionDict = {
    'Applied_poison_rating_bonus' : self.Applied_poison_rating_bonus_method,
    'Attack_power_bonus' : self.Attack_power_bonus_method,
    'Attack_power_penalty' : self.Attack_power_penalty_method,
    'Arcane_archer_mana_regen_penalty' : self.Arcane_archer_mana_regen_penalty_method,
    'Armor_penetration_bonus' : self.Armor_penetration_bonus_method,
    'Avoidance' : self.Avoidance_method,
    'Bleeding' : self.Bleeding_method,
    'Combo_attack_internal' : None,
    'Crane_style' : None,
    'Critical_chance_bonus' : self.Critical_chance_bonus_method,
    'Critical_magnitude_bonus' : self.Critical_magnitude_bonus_method,
    'Damage_over_time' : self.Damage_over_time_method,
    'Dodge_bonus' : self.Dodge_bonus_method,
    'Dodge_penalty' : self.Dodge_penalty_method,
    'Dragon_style' : None,
    'DR_bonus' : self.DR_bonus_method,
    'DR_penalty' : self.DR_penalty_method,
    'Elemental_resistance_arcane' : self.Elemental_resistance_arcane_method,
    'Elemental_resistance_cold' : self.Elemental_resistance_cold_method,
    'Elemental_resistance_divine' : self.Elemental_resistance_divine_method,
    'Elemental_resistance_electric' : self.Elemental_resistance_electric_method,
    'Elemental_resistance_fire' : self.Elemental_resistance_fire_method,
    'Elemental_resistance_poison' : self.Elemental_resistance_poison_method,
    'Elemental_resistance_shadow' : self.Elemental_resistance_shadow_method,
    'Elemental_vulnerability' : self.Elemental_vulnerability_method,
    'Hidden' : None,
    'Hidden_double_cunning' : None,
    'HP_buffer' : self.HP_buffer_method,
    'Increased_movement_AP_cost' : self.Increased_movement_AP_cost_method,
    'Magic_resist_bonus' : self.Magic_resist_bonus_method,
    'Magic_resist_penalty' : self.Magic_resist_penalty_method,
    'Melee_accuracy_bonus' : self.Melee_accuracy_bonus_method,
    'Melee_accuracy_penalty' : self.Melee_accuracy_penalty_method,
    'Melee_dodge_bonus' : self.Melee_dodge_bonus_method,
    'Melee_force_bonus' : self.Melee_force_bonus_method,
    'Might_bonus' : self.Might_bonus_method,
    'Movement_speed_penalty' : self.Movement_speed_penalty_method,
    'No_turn' : self.No_turn_method,
    'On_hit_cripple_weapon' : self.On_hit_cripple_weapon_method,
    'On_hit_frost_weapon' : self.On_hit_frost_weapon_method,
    'On_hit_stun' : self.On_hit_stun_method,
    'On_hit_suppressing_weapon' : self.On_hit_suppressing_weapon_method,
    'Overall_damage_bonus' : self.Overall_damage_bonus_method,
    'Overall_damage_penalty' : self.Overall_damage_penalty_method,
    'Panther_style' : None,
    'Poison_tolerance_bonus' : self.Poison_tolerance_bonus_method,
    'Poison_tolerance_penalty' : self.Poison_tolerance_penalty_method,
    'Potion_effect_bonus' : self.Potion_effect_bonus_method,
    'Prepare_melee_dodge_counterattack' : None,
    'Ranged_accuracy_bonus' : self.Ranged_accuracy_bonus_method,
    'Ranged_accuracy_penalty' : self.Ranged_accuracy_penalty_method,
    'Ranged_critical_magnitude_bonus' : self.Ranged_critical_magnitude_bonus_method,
    'Ranged_dodge_bonus' : self.Ranged_dodge_bonus_method,
    'Ranged_force_bonus' : self.Ranged_force_bonus_method,
    'Recover_HP_percent' : self.Recover_HP_percent_method,
    'Reduced_stealth_AP_cost' : self.Reduced_stealth_AP_cost_method,
    'Reduced_missile_range' : self.Reduced_missile_range_method,
    'Refund_mana_on_cast' : None,
    'Send_empathy_damage_to_summon' : self.Send_empathy_damage_to_summon_method,
    'Set_maximum_stealth_break_chance' : self.Set_maximum_stealth_break_chance_method,
    'Set_movement_AP_cost' : self.Set_movement_AP_cost_method,
    'Snake_style' : None,
    'Sneak_bonus' : self.Sneak_bonus_method,
    'Sneak_penalty' : self.Sneak_penalty_method,
    'Spellpower_bonus' : self.Spellpower_bonus_method,
    'Spellpower_penalty' : self.Spellpower_penalty_method,
    'Spell_failure_chance' : self.Spell_failure_chance_method,
    'Tiger_style' : None,
    'Trap_evade_bonus' : self.Trap_evade_bonus_method,
    'Trap_evade_penalty' : self.Trap_evade_penalty_method,
    }
        
        #'AI_attack_nearby' : 
        #'AI_flee' :
        # 'On_hit_spell_failure': TODO
        # 'Redirect_melee_attacks': None, # Include magnitude How?
        #'Weapon_damage_bonus': lambda target, magnitude, element: 
        # clear HP buffer?
        #'Target_ranged_accuracy_bonus':
        #'Target_ranged_dodge_bonus':
        #'Target_ranged_dodge_penalty_marksman':
        
    unapplyFunctionDict = {
    'Applied_poison_rating_bonus' : self.Applied_poison_rating_bonus_method_reverse,
    'Attack_power_bonus' : self.Attack_power_bonus_method_reverse,
    'Attack_power_penalty' : self.Attack_power_penalty_method_reverse,
    'Arcane_archer_mana_regen_penalty' : self.Arcane_archer_mana_regen_penalty_method_reverse,
    'Armor_penetration_bonus' : self.Armor_penetration_bonus_method_reverse,
    'Avoidance' : self.Avoidance_method_reverse,
    'Bleeding' : None,
    'Combo_attack_internal' : None,
    'Crane_style' : None,
    'Critical_chance_bonus' : self.Critical_chance_bonus_method_reverse,
    'Critical_magnitude_bonus' : self.Critical_magnitude_bonus_method_reverse,
    'Damage_over_time' : None,
    'Dodge_bonus' : self.Dodge_bonus_method_reverse,
    'Dodge_penalty' : self.Dodge_penalty_method_reverse,
    'Dragon_style' : None,
    'DR_bonus' : self.DR_bonus_method_reverse,
    'DR_penalty' : self.DR_penalty_method_reverse,
    'Elemental_resistance_arcane' : self.Elemental_resistance_arcane_method_reverse,
    'Elemental_resistance_cold' : self.Elemental_resistance_cold_method_reverse,
    'Elemental_resistance_electric' : self.Elemental_resistance_electric_method_reverse,
    'Elemental_resistance_fire' : self.Elemental_resistance_fire_method_reverse,
    'Elemental_resistance_poison' : self.Elemental_resistance_poison_method_reverse,
    'Elemental_resistance_shadow' : self.Elemental_resistance_shadow_method_reverse,
    'Elemental_vulnerability' : self.Elemental_vulnerability_method_reverse,
    'Hidden' : None,
    'Hidden_double_cunning' : None,
    'HP_buffer' : None,
    'Increased_movement_AP_cost' : self.Increased_movement_AP_cost_method_reverse,
    'Magic_resist_bonus' : self.Magic_resist_bonus_method_reverse,
    'Magic_resist_penalty' : self.Magic_resist_penalty_method_reverse,
    'Melee_accuracy_bonus' : self.Melee_accuracy_bonus_method_reverse,
    'Melee_accuracy_penalty' : self.Melee_accuracy_penalty_method_reverse,
    'Melee_dodge_bonus' : self.Melee_dodge_bonus_method_reverse,
    'Melee_force_bonus' : self.Melee_force_bonus_method_reverse,
    'Might_bonus' : self.Might_bonus_method_reverse,
    'Movement_speed_penalty' : self.Movement_speed_penalty_method_reverse,
    'No_turn' : None,
    'On_hit_cripple_weapon' : self.On_hit_cripple_weapon_method_reverse,
    'On_hit_frost_weapon' : self.On_hit_frost_weapon_method_reverse,
    'On_hit_stun' : self.On_hit_stun_method_reverse,
    'On_hit_suppressing_weapon' : self.On_hit_suppressing_weapon_method_reverse,
    'Overall_damage_bonus' : self.Overall_damage_bonus_method_reverse,
    'Overall_damage_penalty' : self.Overall_damage_penalty_method_reverse,
    'Panther_style' : None,
    'Poison_tolerance_bonus' : self.Poison_tolerance_bonus_method_reverse,
    'Poison_tolerance_penalty' : self.Poison_tolerance_penalty_method_reverse,
    'Potion_effect_bonus' : self.Potion_effect_bonus_method_reverse,
    'Prepare_melee_dodge_counterattack' : None,
    'Ranged_accuracy_bonus' : self.Ranged_accuracy_bonus_method_reverse,
    'Ranged_accuracy_penalty' : self.Ranged_accuracy_penalty_method_reverse,
    'Ranged_critical_magnitude_bonus' : self.Ranged_critical_magnitude_bonus_method_reverse,
    'Ranged_dodge_bonus' : self.Ranged_dodge_bonus_method_reverse,
    'Ranged_force_bonus' : self.Ranged_force_bonus_method_reverse,
    'Recover_HP_percent' : None,
    'Redirect_melee_attacks' : None,
    'Reduced_stealth_AP_cost' : self.Reduced_stealth_AP_cost_method_reverse,
    'Reduced_missile_range' : self.Reduced_missile_range_method_reverse,
    'Refund_mana_on_cast' : None,
    'Send_empathy_damage_to_summon' : self.Send_empathy_damage_to_summon_method_reverse,
    'Set_maximum_stealth_break_chance' : self.Set_maximum_stealth_break_chance_method_reverse,
    'Set_movement_AP_cost' : self.Set_movement_AP_cost_method_reverse,
    'Snake_style' : None,
    'Sneak_bonus' : self.Sneak_bonus_method_reverse,
    'Sneak_penalty' : self.Sneak_penalty_method_reverse,
    'Spellpower_bonus' : self.Spellpower_bonus_method_reverse,
    'Spellpower_penalty' : self.Spellpower_penalty_method_reverse,
    'Spell_failure_chance' : self.Spell_failure_chance_method_reverse,
    'Tiger_style' : None,
    'Trap_evade_bonus' : self.Trap_evade_bonus_method_reverse,
    'Trap_evade_penalty' : self.Trap_evade_penalty_method_reverse,
    }
    
    def Applied_poison_rating_bonus_method(self, target, magnitude):
        target.equipmentPoisonRatingBonus += magnitude)

    def Attack_power_bonus_method(self, target, magnitude):
        target.attackPower *= (1 + magnitude / 100)

    def Attack_power_penalty_method(self, target, magnitude):
        target.attackPower *= (1 - magnitude / 100)

    def Arcane_archer_mana_regen_penalty_method(self, target, magnitude):
        target.arcaneArcherManaRegenBase -= magnitude

    def Armor_penetration_bonus_method(self, target, magnitude):
        target.statusArmorPenetration += magnitude

    def Avoidance_method(self, target, magnitude):
        target.avoidanceChance = magnitude

    def Bleeding_method(self, target, magnitude):
        target.HP -= (target.HP * magnitude / 100)

    def Combo_attack_internal_method(self):
        pass

    def Crane_style_method(self):
        pass

    def Critical_chance_bonus_method(self, target, magnitude):
        target.statusCriticalChance += magnitude

    def Critical_magnitude_bonus_method(self, target, magnitude):
        target.statusCriticalMagnitude += magnitude

    def Dodge_bonus_method(self, target, magnitude):
        target.statusDodge += magnitude

    def Dodge_penalty_method(self, target, magnitude):
        target.statusDodge -= magnitude

    def Dragon_style_method(self):
        pass

    def DR_bonus_method(self, target, magnitude):
        target.statusDR += magnitude

    def DR_penalty_method(self, target, magnitude):
        target.statusDR -= magnitude

    def Elemental_resistance_arcane_method(self, target, magnitude):
        target.statusArcaneResistance += magnitude

    def Elemental_resistance_cold_method(self, target, magnitude):
        target.statusColdResistance += magnitude

    def Elemental_resistance_divine_method(self, target, magnitude):
        target.statusDivineResistance += magnitude

    def Elemental_resistance_electric_method(self, target, magnitude):
        target.statusElectricResistance += magnitude

    def Elemental_resistance_fire_method(self, target, magnitude):
        target.statusFireResistance += magnitude

    def Elemental_resistance_poison_method(self, target, magnitude):
        target.statusPoisonResistance += magnitude

    def Elemental_resistance_shadow_method(self, target, magnitude):
        target.statusShadowResistance += magnitude

    def Elemental_vulnerability_method(self, target, magnitude, minimum, maximum, element):
        target.lowerElementalResistance(element, magnitude)

    def Hidden_method(self):
        pass

    def Hidden_double_cunning_method(self):
        pass

    def HP_buffer_method(self, target, magnitude):
        target.applyHPBuffer(magnitude)

    def Increased_movement_AP_cost_method(self, target, magnitude):
        target.movementAPCost += magnitude

    def Magic_resist_bonus_method(self, target, magnitude):
        target.statusMagicResist += magnitude

    def Magic_resist_penalty_method(self, target, magnitude):
        target.statusMagicResist -= magnitude

    def Melee_accuracy_bonus_method(self, target, magnitude):
        target.statusMeleeAccuracy += magnitude

    def Melee_accuracy_penalty_method(self, target, magnitude):
        target.statusMeleeAccuracy -= magnitude

    def Melee_dodge_bonus_method(self, target, magnitude):
        target.statusMeleeDodge += magnitude

    def Melee_force_bonus_method(self, target, magnitude):
        target.statusForce += magnitude

    def Might_bonus_method(self, target, magnitude):
        target.statusMight += magnitude

    def Movement_speed_penalty_method(self, target, magnitude):
        target.movementTiles -= magnitude

    def No_turn_method(self, target, magnitude):
        target.AP = 0

    def On_hit_cripple_weapon_method(target, chance, conditional, magnitude):
        target.applyOnHitMod('On_hit_cripple_weapon', conditional, chance, magnitude)

    def On_hit_frost_weapon_method(target, chance, conditional, magnitude1, magnitude2):
        target.applyOnHitMod('On_hit_frost_weapon', conditional, chance, magnitude1, 'Movement_speed_penalty', magnitude2, 'Dodge_penalty')

    def On_hit_stun_method(target, chance, conditional):
        target.applyOnHitMod('On_hit_stun', conditional, chance, 0, 'No_turn')

    def On_hit_suppressing_weapon_method(target, chance, conditional, magnitude1, magnitude2, magnitude3):
        target.applyOnHitMod('On_hit_suppressing_weapon', conditional, chance, magnitude1, 'Melee_accuracy_penalty', magnitude2, 'Ranged_accuracy_penalty', magnitude3, 'Attack_power_penalty')

    def Overall_damage_bonus_method(self, target, magnitude):
        target.statusOverallDamageBonus += magnitude

    def Overall_damage_penalty_method(self, target, magnitude):
        target.statusOverallDamageBonus -= magnitude

    def Panther_style_method(self):
        pass

    def Poison_tolerance_bonus_method(self, target, magnitude):
        target.statusPoisonTolerance += magnitude

    def Poison_tolerance_penalty_method(self, target, magnitude):
        target.statusPoisonTolerance -= magnitude

    def Potion_effect_bonus_method(self, target, magnitude):
        target.statusPotionEffect += magnitude

    def Prepare_melee_dodge_counterattack_method(self):
        pass

    def Ranged_accuracy_bonus_method(self, target, magnitude):
        target.statusRangedAccuracy += magnitude

    def Ranged_accuracy_penalty_method(self, target, magnitude):
        target.statusRangedAccuracy -= magnitude

    def Ranged_critical_magnitude_bonus_method(self, target, magnitude):
        target.statusRangedCriticalMagnitude += magnitude

    def Ranged_dodge_bonus_method(self, target, magnitude):
        target.statusRangedDodge += magnitude

    def Ranged_force_bonus_method(self, target, magnitude):
        target.statusRangedForce += magnitude

    def Recover_HP_percent_method(self, target, magnitude):
        target.HP += (target.totalHP * magnitude / 100)

    def Reduced_stealth_AP_cost_method(self, target, magnitude):
        target.abilityAPModsList.extend([['Stealth', -magnitude], ['Shadow Walk', -magnitude], ['Conceal', -magnitude]])

    def Reduced_missile_range_method(self, target, magnitude):
        target.missleRange -= magnitude

    def Refund_mana_on_cast_method(self):
        pass

    def Send_empathy_damage_to_summon_method(self, target, magnitude):
        target.empathyToSummon = magnitude

    def Set_maximum_stealth_break_chance_method(self, target, magnitude):
        target.stealthBreakMaxOverride = magnitude

    def Set_movement_AP_cost_method(self, target, magnitude):
        target.movementAPOverride = magnitude

    def Snake_style_method(self):
        pass

    def Sneak_bonus_method(self, target, magnitude):
        target.statusSneak += magnitude

    def Sneak_penalty_method(self, target, magnitude):
        target.statusSneak -= magnitude

    def Spellpower_bonus_method(self, target, magnitude):
        target.statusSpellpower += magnitude

    def Spellpower_penalty_method(self, target, magnitude):
        target.statusSpellpower -= magnitude

    def Spell_failure_chance_method(self, target, magnitude):
        target.spellFailureChance += magnitude

    def Tiger_style_method(self):
        pass

    def Trap_evade_bonus_method(self, target, magnitude):
        target.statusTrapEvade += magnitude

    def Trap_evade_penalty_method(self, target, magnitude):
        target.statusTrapEvade -= magnitude


      
    def Applied_poison_rating_bonus_method_reverse(self, target, magnitude):
        target.equipmentPoisonRatingBonus -= magnitude

    def Attack_power_bonus_method_reverse(self, target, magnitude):
        target.attackPower /= (1 + magnitude / 100)

    def Attack_power_penalty_method_reverse(self, target, magnitude):
        target.attackPower /= (1 - magnitude / 100)

    def Arcane_archer_mana_regen_penalty_method_reverse(self, target, magnitude):
        target.arcaneArcherManaRegenBase += magnitude

    def Armor_penetration_bonus_method_reverse(self, target, magnitude):
        target.statusArmorPenetration -= magnitude

    def Avoidance_method_reverse(self, target, magnitude):
        target.avoidanceChance = 0

    def Bleeding_method_reverse(self):
        pass

    def Combo_attack_internal_method_reverse(self):
        pass

    def Crane_style_method_reverse(self):
        pass

    def Critical_chance_bonus_method_reverse(self, target, magnitude):
        target.statusCriticalChance -= magnitude

    def Critical_magnitude_bonus_method_reverse(self, target, magnitude):
        target.statusCriticalMagnitude -= magnitude

    def Damage_over_time_method_reverse(self):
        pass

    def Dodge_bonus_method_reverse(self, target, magnitude):
        target.statusDodge -= magnitude

    def Dodge_penalty_method_reverse(self, target, magnitude):
        target.statusDodge += magnitude

    def Dragon_style_method_reverse(self):
        pass

    def DR_bonus_method_reverse(self, target, magnitude):
        target.statusDR -= magnitude

    def DR_penalty_method_reverse(self, target, magnitude):
        target.statusDR -= magnitude

    def Elemental_resistance_arcane_method_reverse(self, target, magnitude):
        target.statusArcaneResistance -= magnitude

    def Elemental_resistance_cold_method_reverse(self, target, magnitude):
        target.statusColdResistance -= magnitude

    def Elemental_resistance_electric_method_reverse(self, target, magnitude):
        target.statusElectricResistance -= magnitude

    def Elemental_resistance_fire_method_reverse(self, target, magnitude):
        target.statusFireResistance -= magnitude

    def Elemental_resistance_poison_method_reverse(self, target, magnitude):
        target.statusPoisonResistance -= magnitude

    def Elemental_resistance_shadow_method_reverse(self, target, magnitude):
        target.statusShadowResistance -= magnitude

    def Elemental_vulnerability_method_reverse(self, target, magnitude, element):
        target.raiseElementalResistance(element, magnitude)

    def Hidden_method_reverse(self):
        pass

    def Hidden_double_cunning_method_reverse(self):
        pass

    def HP_buffer_method_reverse(self):
        pass

    def Increased_movement_AP_cost_method_reverse(self, target, magnitude):
        target.movementAPCost -= magnitude

    def Magic_resist_bonus_method_reverse(self, target, magnitude):
        target.statusMagicResist -= magnitude

    def Magic_resist_penalty_method_reverse(self, target, magnitude):
        target.statusMagicResist += magnitude

    def Melee_accuracy_bonus_method_reverse(self, target, magnitude):
        target.statusMeleeAccuracy -= magnitude

    def Melee_accuracy_penalty_method_reverse(self, target, magnitude):
        target.statusMeleeAccuracy += magnitude

    def Melee_dodge_bonus_method_reverse(self, target, magnitude):
        target.statusMeleeDodge -= magnitude

    def Melee_force_bonus_method_reverse(self, target, magnitude):
        target.statusForce -= magnitude

    def Might_bonus_method_reverse(self, target, magnitude):
        target.statusMight -= magnitude

    def Movement_speed_penalty_method_reverse(self, target, magnitude):
        target.movementTiles += magnitude

    def No_turn_method_reverse(self):
        pass

    def On_hit_cripple_weapon_method_reverse(self, target):
        target.removeOnHitMod('On_hit_cripple_weapon')

    def On_hit_frost_weapon_method_reverse(self, target):
        target.removeOnHitMod('On_hit_frost_weapon')

    def On_hit_stun_method_reverse(self, target):
        target.removeOnHitMod('On_hit_stun')

    def On_hit_suppressing_weapon_method_reverse(self, target):
        target.removeOnHitMod('On_hit_suppressing_weapon')

    def Overall_damage_bonus_method_reverse(self, target, magnitude):
        target.statusOverallDamageBonus -= magnitude

    def Overall_damage_penalty_method_reverse(self, target, magnitude):
        target.statusOverallDamageBonus += magnitude

    def Panther_style_method_reverse(self):
        pass

    def Poison_tolerance_bonus_method_reverse(self, target, magnitude):
        target.statusPoisonTolerance -= magnitude

    def Poison_tolerance_penalty_method_reverse(self, target, magnitude):
        target.statusPoisonTolerance += magnitude

    def Potion_effect_bonus_method_reverse(self, target, magnitude):
        target.statusPotionEffect -= magnitude

    def Prepare_melee_dodge_counterattack_method_reverse(self):
        pass

    def Ranged_accuracy_bonus_method_reverse(self, target, magnitude):
        target.statusRangedAccuracy -= magnitude

    def Ranged_accuracy_penalty_method_reverse(self, target, magnitude):
        target.statusRangedAccuracy += magnitude

    def Ranged_critical_magnitude_bonus_method_reverse(self, target, magnitude):
        target.statusRangedCriticalMagnitude -= magnitude

    def Ranged_dodge_bonus_method_reverse(self, target, mangitude):
        target.statusRangedDodge -= magnitude

    def Ranged_force_bonus_method_reverse(self, target, magnitude):
        target.statusRangedForce -= magnitude

    def Recover_HP_percent_method_reverse(self):
        pass

    def Redirect_melee_attacks_method_reverse(self):
        pass

    def Reduced_stealth_AP_cost_method_reverse(self, target, magnitude):
        target.abilityAPModsList.remove(['Shadow Walk', -magnitude]).remove(['Conceal', -magnitude]).remove(['Stealth', -magnitude])

    def Reduced_missile_range_method_reverse(self, target, magnitude):
        target.missleRange += magnitude

    def Refund_mana_on_cast_method_reverse(self):
        pass

    def Send_empathy_damage_to_summon_method_reverse(self, target, magnitude):
        target.empathyToSummon = 0

    def Set_maximum_stealth_break_chance_method_reverse(self, target, magnitude):
        target.stealthBreakMaxOverride = 100

    def Set_movement_AP_cost_method_reverse(self, target, magnitude):
        target.movementAPOverride = -1

    def Snake_style_method_reverse(self):
        pass

    def Sneak_bonus_method_reverse(self, target, magnitude):
        target.statusSneak -= magnitude

    def Sneak_penalty_method_reverse(self, target, magnitude):
        target.statusSneak += magnitude

    def Spellpower_bonus_method_reverse(self, target, magnitude):
        target.statusSpellpower -= magnitude

    def Spellpower_penalty_method_reverse(self, target, magnitude):
        target.statusSpellpower += magnitude

    def Spell_failure_chance_method_reverse(self, target, magnitude):
        target.spellFailureChance -= magnitude

    def Tiger_style_method_reverse(self):
        pass

    def Trap_evade_bonus_method_reverse(self, target, magnitude):
        target.statusTrapEvade -= magnitude

    def Trap_evade_penalty_method_reverse(self, target, magnitude):
        target.statusTrapEvade += magnitude

