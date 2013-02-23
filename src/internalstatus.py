#!/usr/bin/python

import sys
import onhiteffect

# The lifetime of a Status object:
#   1. Status is loaded into memory from the data file on game startup.
#       --STATE-- Common Fields are initialized but the Status is unusable.
#   2. A call to Combat.addStatus() is made, referencing a name: "abc" 
#         The datastructure is searched for a Status object with named "abc".
#         Such as Status (hopefully unique!) is found and a copy is made.
#   3. The addStatus() method takes this copy and fills it in with additional 
#         information needed to complete its functionality.
#       --STATE-- Only now is the Status ready to be used by anything.
#   4. The addStatus() method adds the new Status to a character who deals with it
#         over its natural lifetime unless it is dispelled early.
#   5. Either through turn upkeep, the end of battle, or through a REMOVED_ON action,
#         the Status is removed from existence.
#

# The lifetime of an InternalStatus object:
#   1. IStatus is defined via the data file and is given a name, an immunity, and 
#          a recurring boolean.
#         --STATE-- Only a husk of an IStatus exists here, it cannot be used.
#   2. IStatus is referred to by the definition of a Display Status.  The IStatus
#         is looked up by name.  The properties of this IStatus are copied over to 
#         a new IStatus and additional information now fills the new IStatus which
#         is stored with the Display Status.
#         --STATE-- This IStatus is theoretically ready to be used.  The magnitude
#            and possibly the min/max fields may be overridden later, but some IStatuses
#            will never change from here.
#   3. An addStatus() call is performed which applys a Display Status and, along with it,
#       all of its IStatuses who also get magnitude information and element.      
#         --STATE-- This IStatus has been fully instantiated and is ready to have work
#                   done by it.
#


class InternalStatus(object):

    def __init__(self, name, recurring, immunity, element=None):
        # Known only from loaded data file definition:
        self.name = name
        self.recurring = recurring
        self.immunity = immunity
        self.applyEffect = applyFunctionDict[name]
        self.unapplyEffect = unapplyFunctionDict[name]
        
        # Known only from loaded data file instantiation:
        self.parentName = None
        
        # May only be known at apply time:
        self.magnitude = None # inherit magnitude from caller if 0.      
        self.duration = None # Not typically used or kept track of here.  Only for HP Buffers
                             # thus far.
        self.element = element
            
    def cloneWithDetails(self, magnitude, element, parent):
        """Returns a Status with 'ready-to-use' values based off of a previously defined InternalStatus."""
        cloneStatus = InternalStatus(self.name, self.recurring, self.immunity, self.element)
        cloneStatus.magnitude = magnitude
        cloneStatus.parentName = parent
        return cloneStatus


def Applied_poison_rating_bonus_method(self, target, magnitude):
    target.equipmentPoisonRatingBonus += magnitude

def Attack_power_bonus_method(self, target, magnitude):
    target.attackPower += magnitude

def Attack_power_penalty_method(self, target, magnitude):
    target.attackPower -= magnitude

def Arcane_archer_mana_regen_penalty_method(self, target, magnitude):
    target.arcaneArcherManaRegenBase -= magnitude

def Armor_penetration_bonus_method(self, target, magnitude):
    target.statusArmorPenetration += magnitude

def Avoidance_method(self, target, magnitude):
    target.avoidanceChance = magnitude

def Awareness_penalty_method(self, target, magnitude):
    target.statusAwareness -= magnitude
    
def Bleeding_method(self, target, magnitude):
    target.HP -= (target.HP * magnitude / 100)

def Combo_attack_internal_method(self, target, magnitude):
    pass

def Crane_style_method(self, target, magnitude):
    pass

def Critical_chance_bonus_method(self, target, magnitude):
    target.statusCriticalChance += magnitude

def Critical_magnitude_bonus_method(self, target, magnitude):
    target.statusCriticalMagnitude += magnitude

def Damage_over_time_method(self, target, magnitude):
    dam = calcDamage(None, target, magnitude, magnitude, self.element, "Normal Hit")
    target.lowerHP(target, dam)
    
def Dodge_bonus_method(self, target, magnitude):
    target.statusDodge += magnitude

def Dodge_penalty_method(self, target, magnitude):
    target.statusDodge -= magnitude

def Double_dodge_method(self, target, magnitude):
    pass
    
def Dragon_style_method(self, target, magnitude):
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

def Elemental_vulnerability_method(self, target, magnitude, element):
    target.lowerElementalResistance(self.element, magnitude)

def Hidden_method(self, target, magnitude):
    pass

def Hidden_double_cunning_method(self, target, magnitude):
    pass

def HP_buffer_method(self, target, magnitude):
    target.applyHPBuffer(self.parentName, magnitude, self.duration)

def Increased_movement_AP_cost_method(self, target, magnitude):
    target.statusMovementAPCost += magnitude

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

def Might_penalty_method(self, target, magnitude):
    target.statusMight -= magnitude
    
def Movement_speed_penalty_method(self, target, magnitude):
    target.movementTiles -= magnitude
    # TODO: Ensure monsters can always move at least one tile.

def Movement_tiles_penalty_method(self, target, magnitude):
    target.movementTiles -= magnitude
    
def Nothing_method(self, target, magnitude):
    pass
    
def No_turn_method(self, target, magnitude):
    target.AP = 0
    
def Numbing_poison_method(self, target, magnitude):
    target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyNumbingPoison))
    
def On_hit_cripple_weapon_method(target, chance, conditional, magnitude):
    target.applyOnHitMod('On_hit_cripple_weapon', conditional, chance, magnitude)
    
def On_hit_frost_weapon_method(target, chance, conditional, magnitude1, magnitude2):
    target.applyOnHitMod('On_hit_frost_weapon', conditional, chance, magnitude1, 'Movement_speed_penalty', magnitude2, 'Dodge_penalty')

def On_hit_mage_hunting_method(self, target, magnitude):
    target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyMageHunting))
    
def On_hit_stun_method(target, chance, conditional):
    target.applyOnHitMod('On_hit_stun', conditional, chance, 0, 'No_turn')

def On_hit_suppressing_weapon_method(self, target, magnitude):
    target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applySuppressed))
    target.statusCriticalChance -= 10
    
def Overall_damage_bonus_method(self, target, magnitude):
    target.statusOverallDamageBonus += magnitude

def Overall_damage_penalty_method(self, target, magnitude):
    target.statusOverallDamageBonus -= magnitude

def Panther_style_method(self, target, magnitude):
    pass

def Poison_tolerance_bonus_method(self, target, magnitude):
    target.statusPoisonTolerance += magnitude

def Poison_tolerance_penalty_method(self, target, magnitude):
    target.statusPoisonTolerance -= magnitude

def Potion_effect_bonus_method(self, target, magnitude):
    target.statusPotionEffect += magnitude

def Prepare_melee_dodge_counterattack_method(self, target, magnitude):
    pass

def Ranged_accuracy_bonus_method(self, target, magnitude):
    target.statusRangedAccuracy += magnitude

def Ranged_accuracy_penalty_method(self, target, magnitude):
    target.statusRangedAccuracy -= magnitude

def Ranged_critical_magnitude_bonus_method(self, target, magnitude):
    target.statusRangedCriticalMagnitude += magnitude

def Ranged_dodge_bonus_method(self, target, magnitude):
    target.statusRangedDodge += magnitude

def Ranged_dodge_penalty_method(self, target, mangitude):
    target.statusRangedDodge -= magnitude
    
def Ranged_force_bonus_method(self, target, magnitude):
    target.statusRangedForce += magnitude

def Recover_HP_percent_method(self, target, magnitude):
    target.HP += (target.totalHP * magnitude / 100)

def Reduced_stealth_AP_cost_method(self, target, magnitude):
    target.abilityAPModsList.extend([['Stealth', -magnitude], ['Shadow Walk', -magnitude], ['Conceal', -magnitude]])

def Reduced_missile_range_method(self, target, magnitude):
    target.missleRange -= magnitude

def Refund_mana_on_cast_method(self, target, magnitude):
    pass

def Send_empathy_damage_to_summon_method(self, target, magnitude):
    target.empathyToSummon = magnitude

def Set_maximum_stealth_break_chance_method(self, target, magnitude):
    target.stealthBreakMaxOverride = magnitude

def Set_movement_AP_cost_method(self, target, magnitude):
    target.overrideMovementAPCost = magnitude

def Snake_style_method(self, target, magnitude):
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
    
def Target_throat_method(self, target, magnitude):
    target.onHitEffects.appedn(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyTargetThroat))
    
def Tiger_style_method(self, target, magnitude):
    pass

def Trap_evade_bonus_method(self, target, magnitude):
    target.statusTrapEvade += magnitude

def Trap_evade_penalty_method(self, target, magnitude):
    target.statusTrapEvade -= magnitude
    
def Vile_poison_method(self, target, magnitude):
    target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyVilePoison))
    
def Weapon_damage_bonus_method(self, target, magnitude):
    target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyFlatElementalDamage, self.element))
    
def Applied_poison_rating_bonus_method_reverse(self, target, magnitude):
    target.equipmentPoisonRatingBonus -= magnitude

def Attack_power_bonus_method_reverse(self, target, magnitude):
    target.attackPower -= magnitude

def Attack_power_penalty_method_reverse(self, target, magnitude):
    target.attackPower += magnitude

def Arcane_archer_mana_regen_penalty_method_reverse(self, target, magnitude):
    target.arcaneArcherManaRegenBase += magnitude

def Armor_penetration_bonus_method_reverse(self, target, magnitude):
    target.statusArmorPenetration -= magnitude

def Avoidance_method_reverse(self, target, magnitude):
    target.avoidanceChance = 0

def Awareness_penalty_method_reverse(self, target, magnitude):
    target.statusAwareness += magnitude
    
def Bleeding_method_reverse(self, target, magnitude):
    pass

def Combo_attack_internal_method_reverse(self, target, magnitude):
    pass

def Crane_style_method_reverse(self, target, magnitude):
    pass

def Critical_chance_bonus_method_reverse(self, target, magnitude):
    target.statusCriticalChance -= magnitude

def Critical_magnitude_bonus_method_reverse(self, target, magnitude):
    target.statusCriticalMagnitude -= magnitude

def Damage_over_time_method_reverse(self, target, magnitude):
    pass

def Dodge_bonus_method_reverse(self, target, magnitude):
    target.statusDodge -= magnitude

def Dodge_penalty_method_reverse(self, target, magnitude):
    target.statusDodge += magnitude
    
def Double_dodge_method_reverse(self, target, magnitude):
    stacks = target.getStatusStackCount("Double Dodge")
    target.statusDodge -= min(15, stacks * 5)
    
def Dragon_style_method_reverse(self, target, magnitude):
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

def Elemental_resistance_divine_method_reverse(self, target, magnitude):
    target.statusDivineResistance -= magnitude
    
def Elemental_resistance_fire_method_reverse(self, target, magnitude):
    target.statusFireResistance -= magnitude

def Elemental_resistance_poison_method_reverse(self, target, magnitude):
    target.statusPoisonResistance -= magnitude

def Elemental_resistance_shadow_method_reverse(self, target, magnitude):
    target.statusShadowResistance -= magnitude

def Elemental_vulnerability_method_reverse(self, target, magnitude, element):
    target.raiseElementalResistance(element, magnitude)

def Hidden_method_reverse(self, target, magnitude):
    pass

def Hidden_double_cunning_method_reverse(self, target, magnitude):
    pass

def HP_buffer_method_reverse(self, target, magnitude, name, duration):
    target.unapplyHPBuffer(name, duration)

def Increased_movement_AP_cost_method_reverse(self, target, magnitude):
    target.statusMovementAPCost -= magnitude

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
    
def Might_penalty_method_reverse(self, target, magnitude):
    target.statusMight += magnitude

def Movement_speed_penalty_method_reverse(self, target, magnitude):
    target.movementTiles += magnitude

def Movement_tiles_penalty_method_reverse(self, target, magnitude):
    target.movementTiles += magnitude
    
def Nothing_method_reverse(self, target, magnitude):
    pass
    
def No_turn_method_reverse(self, target, magnitude):
    pass

def Numbing_poison_method_reverse(self, target, magnitude):
    target.removeOnHitEffect("NumbingPoison", magnitude)
    
def On_hit_cripple_weapon_method_reverse(self, target, magnitude):
    target.removeOnHitMod('On_hit_cripple_weapon')
    
def On_hit_frost_weapon_method_reverse(self, target, magnitude):
    target.removeOnHitMod('On_hit_frost_weapon')
    
def On_hit_mage_hunting_method_reverse(self, target, magnitude):
    target.removeOnHitEffect("MageHunting", magnitude)

def On_hit_stun_method_reverse(self, target, magnitude):
    target.removeOnHitMod('On_hit_stun')

def On_hit_suppressing_weapon_method_reverse(self, target, magnitude):
    target.removeOnHitEffect('On_hit_suppressing_weapon', magnitude)
    target.statusCriticalChance += 10
    
def Overall_damage_bonus_method_reverse(self, target, magnitude):
    target.statusOverallDamageBonus -= magnitude

def Overall_damage_penalty_method_reverse(self, target, magnitude):
    target.statusOverallDamageBonus += magnitude

def Panther_style_method_reverse(self, target, magnitude):
    pass

def Poison_tolerance_bonus_method_reverse(self, target, magnitude):
    target.statusPoisonTolerance -= magnitude

def Poison_tolerance_penalty_method_reverse(self, target, magnitude):
    target.statusPoisonTolerance += magnitude

def Potion_effect_bonus_method_reverse(self, target, magnitude):
    target.statusPotionEffect -= magnitude

def Prepare_melee_dodge_counterattack_method_reverse(self, target, magnitude):
    pass

def Ranged_accuracy_bonus_method_reverse(self, target, magnitude):
    target.statusRangedAccuracy -= magnitude

def Ranged_accuracy_penalty_method_reverse(self, target, magnitude):
    target.statusRangedAccuracy += magnitude

def Ranged_critical_magnitude_bonus_method_reverse(self, target, magnitude):
    target.statusRangedCriticalMagnitude -= magnitude

def Ranged_dodge_bonus_method_reverse(self, target, mangitude):
    target.statusRangedDodge -= magnitude

def Ranged_dodge_penalty_method_reverse(self, target, mangitude):
    target.statusRangedDodge += magnitude
    
def Ranged_force_bonus_method_reverse(self, target, magnitude):
    target.statusRangedForce -= magnitude

def Recover_HP_percent_method_reverse(self, target, magnitude):
    pass

def Redirect_melee_attacks_method_reverse(self, target, magnitude):
    pass

def Reduced_stealth_AP_cost_method_reverse(self, target, magnitude):
    target.abilityAPModsList.remove(['Shadow Walk', -magnitude]).remove(['Conceal', -magnitude]).remove(['Stealth', -magnitude])

def Reduced_missile_range_method_reverse(self, target, magnitude):
    target.missleRange += magnitude

def Refund_mana_on_cast_method_reverse(self, target, magnitude):
    pass

def Send_empathy_damage_to_summon_method_reverse(self, target, magnitude):
    target.empathyToSummon = 0

def Set_maximum_stealth_break_chance_method_reverse(self, target, magnitude):
    target.stealthBreakMaxOverride = 100

def Set_movement_AP_cost_method_reverse(self, target, magnitude):
    target.overrideMovementAPCost = -1

def Snake_style_method_reverse(self, target, magnitude):
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
    
def Target_throat_method_reverse(self, target, magnitude):
    target.removeOnHitEffect("TargetThroat", magnitude)
    
def Tiger_style_method_reverse(self, target, magnitude):
    pass

def Trap_evade_bonus_method_reverse(self, target, magnitude):
    target.statusTrapEvade -= magnitude

def Trap_evade_penalty_method_reverse(self, target, magnitude):
    target.statusTrapEvade += magnitude

def Vile_poison_method_reverse(self, target, magnitude):
    target.removeOnHitEffect("VilePoison", magnitude)
    
def Weapon_damage_bonus_method_reverse(self, target, magnitude):
    target.removeOnHitEffect("FlatElementalDamage " + self.element, magnitude)
    
applyFunctionDict = {
    'Applied_poison_rating_bonus' : Applied_poison_rating_bonus_method,
    'Attack_power_bonus' : Attack_power_bonus_method,
    'Attack_power_penalty' : Attack_power_penalty_method,
    'Arcane_archer_mana_regen_penalty' : Arcane_archer_mana_regen_penalty_method,
    'Armor_penetration_bonus' : Armor_penetration_bonus_method,
    'Avoidance' : Avoidance_method,
    'Awareness_penalty' : Awareness_penalty_method,
    'Bleeding' : Bleeding_method,
    'Combo_attack_internal' : None,
    'Crane_style' : None,
    'Critical_chance_bonus' : Critical_chance_bonus_method,
    'Critical_magnitude_bonus' : Critical_magnitude_bonus_method,
    'Damage_over_time' : Damage_over_time_method,
    'Dodge_bonus' : Dodge_bonus_method,
    'Dodge_penalty' : Dodge_penalty_method,
    'Double_dodge_internal' : None,
    'Dragon_style' : None,
    'DR_bonus' : DR_bonus_method,
    'DR_penalty' : DR_penalty_method,
    'Elemental_resistance_arcane' : Elemental_resistance_arcane_method,
    'Elemental_resistance_cold' : Elemental_resistance_cold_method,
    'Elemental_resistance_divine' : Elemental_resistance_divine_method,
    'Elemental_resistance_electric' : Elemental_resistance_electric_method,
    'Elemental_resistance_fire' : Elemental_resistance_fire_method,
    'Elemental_resistance_poison' : Elemental_resistance_poison_method,
    'Elemental_resistance_shadow' : Elemental_resistance_shadow_method,
    'Elemental_vulnerability' : Elemental_vulnerability_method,
    'Hidden' : None,
    'Hidden_double_cunning' : None,
    'HP_buffer' : HP_buffer_method,
    'Increased_movement_AP_cost' : Increased_movement_AP_cost_method,
    'Magic_resist_bonus' : Magic_resist_bonus_method,
    'Magic_resist_penalty' : Magic_resist_penalty_method,
    'Melee_accuracy_bonus' : Melee_accuracy_bonus_method,
    'Melee_accuracy_penalty' : Melee_accuracy_penalty_method,
    'Melee_dodge_bonus' : Melee_dodge_bonus_method,
    'Melee_force_bonus' : Melee_force_bonus_method,
    'Might_bonus' : Might_bonus_method,
    'Might_penalty' : Might_penalty_method,
    'Movement_speed_penalty' : Movement_speed_penalty_method,
    'Movement_tiles_penalty' : Movement_tiles_penalty_method,
    'No_turn' : No_turn_method,
    'Numbing_poison_internal' : Numbing_poison_method,
    'On_hit_cripple_weapon' : On_hit_cripple_weapon_method,
    'On_hit_frost_weapon' : On_hit_frost_weapon_method,
    'On_hit_mage_hunting' : On_hit_mage_hunting_method,
    'On_hit_stun' : On_hit_stun_method,
    'On_hit_suppressing_weapon' : On_hit_suppressing_weapon_method,
    'Overall_damage_bonus' : Overall_damage_bonus_method,
    'Overall_damage_penalty' : Overall_damage_penalty_method,
    'Panther_style' : None,
    'Poison_tolerance_bonus' : Poison_tolerance_bonus_method,
    'Poison_tolerance_penalty' : Poison_tolerance_penalty_method,
    'Potion_effect_bonus' : Potion_effect_bonus_method,
    'Prepare_melee_dodge_counterattack' : None,
    'Ranged_accuracy_bonus' : Ranged_accuracy_bonus_method,
    'Ranged_accuracy_penalty' : Ranged_accuracy_penalty_method,
    'Ranged_critical_magnitude_bonus' : Ranged_critical_magnitude_bonus_method,
    'Ranged_dodge_bonus' : Ranged_dodge_bonus_method,
    'Ranged_dodge_penalty' : Ranged_dodge_penalty_method,
    'Ranged_force_bonus' : Ranged_force_bonus_method,
    'Recover_HP_percent' : Recover_HP_percent_method,
    'Reduced_stealth_AP_cost' : Reduced_stealth_AP_cost_method,
    'Reduced_missile_range' : Reduced_missile_range_method,
    'Refund_mana_on_cast' : None,
    'Send_empathy_damage_to_summon' : Send_empathy_damage_to_summon_method,
    'Set_maximum_stealth_break_chance' : Set_maximum_stealth_break_chance_method,
    'Set_movement_AP_cost' : Set_movement_AP_cost_method,
    'Snake_style' : None,
    'Sneak_bonus' : Sneak_bonus_method,
    'Sneak_penalty' : Sneak_penalty_method,
    'Spellpower_bonus' : Spellpower_bonus_method,
    'Spellpower_penalty' : Spellpower_penalty_method,
    'Spell_failure_chance' : Spell_failure_chance_method,
    'Stunning_recovery_internal' : None,
    'Target_throat_internal' : Target_throat_method,
    'Tiger_style' : None,
    'Trap_evade_bonus' : Trap_evade_bonus_method,
    'Trap_evade_penalty' : Trap_evade_penalty_method,
    'Vile_poison_internal' : Vile_poison_method,
    'Weapon_damage_bonus' : Weapon_damage_bonus_method
}
        
        #'AI_attack_nearby' : 
        #'AI_flee' : # Need decent AI to implement these...
        # 'Redirect_melee_attacks': None, # Save this one for last?
        
unapplyFunctionDict = {
    'Applied_poison_rating_bonus' : Applied_poison_rating_bonus_method_reverse,
    'Attack_power_bonus' : Attack_power_bonus_method_reverse,
    'Attack_power_penalty' : Attack_power_penalty_method_reverse,
    'Arcane_archer_mana_regen_penalty' : Arcane_archer_mana_regen_penalty_method_reverse,
    'Armor_penetration_bonus' : Armor_penetration_bonus_method_reverse,
    'Avoidance' : Avoidance_method_reverse,
    'Awareness_penalty' : Awareness_penalty_method_reverse,
    'Bleeding' : None,
    'Combo_attack_internal' : None,
    'Crane_style' : None,
    'Critical_chance_bonus' : Critical_chance_bonus_method_reverse,
    'Critical_magnitude_bonus' : Critical_magnitude_bonus_method_reverse,
    'Damage_over_time' : None,
    'Dodge_bonus' : Dodge_bonus_method_reverse,
    'Dodge_penalty' : Dodge_penalty_method_reverse,
    'Double_dodge_internal' : Double_dodge_method_reverse,
    'Dragon_style' : None,
    'DR_bonus' : DR_bonus_method_reverse,
    'DR_penalty' : DR_penalty_method_reverse,
    'Elemental_resistance_arcane' : Elemental_resistance_arcane_method_reverse,
    'Elemental_resistance_cold' : Elemental_resistance_cold_method_reverse,
    'Elemental_resistance_electric' : Elemental_resistance_electric_method_reverse,
    'Elemental_resistance_divine' : Elemental_resistance_divine_method_reverse,
    'Elemental_resistance_fire' : Elemental_resistance_fire_method_reverse,
    'Elemental_resistance_poison' : Elemental_resistance_poison_method_reverse,
    'Elemental_resistance_shadow' : Elemental_resistance_shadow_method_reverse,
    'Elemental_vulnerability' : Elemental_vulnerability_method_reverse,
    'Hidden' : None,
    'Hidden_double_cunning' : None,
    'HP_buffer' : HP_buffer_method_reverse,
    'Increased_movement_AP_cost' : Increased_movement_AP_cost_method_reverse,
    'Magic_resist_bonus' : Magic_resist_bonus_method_reverse,
    'Magic_resist_penalty' : Magic_resist_penalty_method_reverse,
    'Melee_accuracy_bonus' : Melee_accuracy_bonus_method_reverse,
    'Melee_accuracy_penalty' : Melee_accuracy_penalty_method_reverse,
    'Melee_dodge_bonus' : Melee_dodge_bonus_method_reverse,
    'Melee_force_bonus' : Melee_force_bonus_method_reverse,
    'Might_bonus' : Might_bonus_method_reverse,
    'Might_penalty' : Might_penalty_method_reverse,
    'Numbing_poison_internal' : Numbing_poison_method_reverse,
    'Movement_speed_penalty' : Movement_speed_penalty_method_reverse,
    'Movement_tiles_penalty' : Movement_tiles_penalty_method_reverse,
    'No_turn' : None,
    'On_hit_cripple_weapon' : On_hit_cripple_weapon_method_reverse,
    'On_hit_frost_weapon' : On_hit_frost_weapon_method_reverse,
    'On_hit_mage_hunting' : On_hit_mage_hunting_method_reverse,
    'On_hit_stun' : On_hit_stun_method_reverse,
    'On_hit_suppressing_weapon' : On_hit_suppressing_weapon_method_reverse,
    'Overall_damage_bonus' : Overall_damage_bonus_method_reverse,
    'Overall_damage_penalty' : Overall_damage_penalty_method_reverse,
    'Panther_style' : None,
    'Poison_tolerance_bonus' : Poison_tolerance_bonus_method_reverse,
    'Poison_tolerance_penalty' : Poison_tolerance_penalty_method_reverse,
    'Potion_effect_bonus' : Potion_effect_bonus_method_reverse,
    'Prepare_melee_dodge_counterattack' : None,
    'Ranged_accuracy_bonus' : Ranged_accuracy_bonus_method_reverse,
    'Ranged_accuracy_penalty' : Ranged_accuracy_penalty_method_reverse,
    'Ranged_critical_magnitude_bonus' : Ranged_critical_magnitude_bonus_method_reverse,
    'Ranged_dodge_bonus' : Ranged_dodge_bonus_method_reverse,
    'Ranged_dodge_penalty' : Ranged_dodge_penalty_method_reverse,
    'Ranged_force_bonus' : Ranged_force_bonus_method_reverse,
    'Recover_HP_percent' : None,
    'Redirect_melee_attacks' : None,
    'Reduced_stealth_AP_cost' : Reduced_stealth_AP_cost_method_reverse,
    'Reduced_missile_range' : Reduced_missile_range_method_reverse,
    'Refund_mana_on_cast' : None,
    'Send_empathy_damage_to_summon' : Send_empathy_damage_to_summon_method_reverse,
    'Set_maximum_stealth_break_chance' : Set_maximum_stealth_break_chance_method_reverse,
    'Set_movement_AP_cost' : Set_movement_AP_cost_method_reverse,
    'Snake_style' : None,
    'Sneak_bonus' : Sneak_bonus_method_reverse,
    'Sneak_penalty' : Sneak_penalty_method_reverse,
    'Spellpower_bonus' : Spellpower_bonus_method_reverse,
    'Spellpower_penalty' : Spellpower_penalty_method_reverse,
    'Spell_failure_chance' : Spell_failure_chance_method_reverse,
    'Stunning_recovery_internal' : None,
    'Target_throat_internal' : Target_throat_method_reverse,
    'Tiger_style' : None,
    'Trap_evade_bonus' : Trap_evade_bonus_method_reverse,
    'Trap_evade_penalty' : Trap_evade_penalty_method_reverse,
    'Vile_poison_internal' : Vile_poison_method_reverse,
    'Weapon_damage_bonus' : Weapon_damage_bonus_method_reverse
}
    
    
    
