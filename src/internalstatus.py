#!/usr/bin/python

import sys
import onhiteffect
from combat import Combat

# internalstatus.py
# Author: Devin Ekins -- G. Cube
#
# This module contains all internal status effects in Akintu.
# Individual methods are not typically commented as they represent 
# the functionality of individual iStatuses -- those iStatuses already have
# documentation on their functionality as detailed in the description
# in the dictionary containing the text of these functions.

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
        self.applyEffect = InternalStatus.applyFunctionDict[name]
        self.unapplyEffect = InternalStatus.unapplyFunctionDict[name]
        
        
        # Known only from loaded data file instantiation:
        self.parentName = None

        # May only be known at apply time:
        self.magnitude = None # inherit magnitude from caller if 0.
        self.duration = None
        self.element = element
        self.staticText = InternalStatus.textDict[name].format(magnitude="x", element="{ELE}")
        self.text = InternalStatus.textDict[name]
        
    def cloneWithDetails(self, magnitude, element, parent):
        """Returns a Status with 'ready-to-use' values based off of a previously defined InternalStatus."""
        cloneStatus = InternalStatus(self.name, self.recurring, self.immunity, self.element)
        cloneStatus.magnitude = magnitude
        cloneStatus.parentName = parent
        cloneStatus.text = InternalStatus.textDict[cloneStatus.name].format(
                                magnitude=str(cloneStatus.magnitude), element=cloneStatus.element)
        return cloneStatus

    def updateText(self):
        self.text = InternalStatus.textDict[self.name].format(
                                magnitude=str(self.magnitude), element=self.element)
    
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
        target.avoidanceChance += magnitude

    def Awareness_penalty_method(self, target, magnitude):
        target.statusAwareness -= magnitude

    def Bleeding_method(self, target, magnitude):
        Combat.modifyResource(target, "HP", float(target.HP) * magnitude / -100)

    def Combo_attack_internal_method(self, target, magnitude):
        pass

    def Crane_style_method(self, target, magnitude):
        pass

    def Critical_chance_bonus_method(self, target, magnitude):
        target.statusCriticalChance += magnitude

    def Critical_magnitude_bonus_method(self, target, magnitude):
        target.statusCriticalMagnitude += magnitude

    def Damage_over_time_method(self, target, magnitude):
        dam = Combat.calcDamage(None, target, magnitude, magnitude, self.element, "Normal Hit")
        Combat.lowerHP(target, dam)

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

    def Elemental_offense_arcane_method(self, target, magnitude):
        target.statusArcaneBonusDamage += magnitude
        
    def Elemental_offense_divine_method(self, target, magnitude):
        target.statusDivineBonusDamage += magnitude
        
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

    def Elemental_vulnerability_method(self, target, magnitude):
        target.lowerElementalResistance(self.element, magnitude)

    def Hidden_method(self, target, magnitude):
        pass

    def Hidden_double_cunning_method(self, target, magnitude):
        pass

    def HP_buffer_method(self, target, magnitude):
        target.applyHPBuffer(self.parentName, magnitude, self.duration)

    def Increased_movement_AP_cost_method(self, target, magnitude):
        target.statusMovementAPCost += magnitude
        
    def Intuition_bonus_method(self, target, magnitude):
        target.statusIntuition += magnitude
        
    def Knockback_resistance_bonus_method(self, target, magnitude):
        target.knockbackResistance += magnitude

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
        target.statusMovementTiles -= magnitude

    def Movement_tiles_penalty_method(self, target, magnitude):
        target.statusMovementTiles -= magnitude

    def Nothing_method(self, target, magnitude):
        pass

    def No_turn_method(self, target, magnitude):
        target.AP = 0

    def Numbing_poison_method(self, target, magnitude):
        target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyNumbingPoison))

    def On_hit_cripple_weapon_method(target, chance, conditional, magnitude):
        target.applyOnHitMod('On_hit_cripple_weapon', conditional, chance, magnitude)

    def On_hit_frost_weapon_method(self, target, magnitude):
        target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyFrostWeapon))

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

    def Ranged_dodge_penalty_method(self, target, magnitude):
        target.statusRangedDodge -= magnitude

    def Ranged_force_bonus_method(self, target, magnitude):
        target.statusRangedForce += magnitude

    def Recover_HP_percent_method(self, target, magnitude):
        target.HP += (target.totalHP * magnitude / 100)

    def Reduced_stealth_AP_cost_method(self, target, magnitude):
        target.abilityAPModsList.extend([['Stealth', -magnitude], ['Shadow Walk', -magnitude], ['Conceal', -magnitude]])

    def Reduced_missile_range_method(self, target, magnitude):
        target.missleRange -= magnitude

    def Send_empathy_damage_to_summon_method(self, target, magnitude):
        target.empathyToSummon = magnitude

    def Set_maximum_stealth_break_chance_method(self, target, magnitude):
        target.stealthBreakMaxOverride = magnitude

    def Set_movement_AP_cost_method(self, target, magnitude):
        Combat.setMovementCost(target, magnitude)

    def Slashing_resist_penalty_method(self, target, magnitude):
        target.statusSlashingResistance -= 25
        
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
        target.onHitEffects.append(onhiteffect.OnHitEffect(magnitude, onhiteffect.OnHitEffect.applyTargetThroat))

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
        target.avoidanceChance -= magnitude

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

    def Elemental_offense_arcane_method_reverse(self, target, magnitude):
        target.statusArcaneBonusDamage -= magnitude
        
    def Elemental_offense_divine_method_reverse(self, target, magnitude):
        target.statusDivineBonusDamage -= magnitude
        
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

    def Elemental_vulnerability_method_reverse(self, target, magnitude):
        target.raiseElementalResistance(self.element, magnitude)

    def Hidden_method_reverse(self, target, magnitude):
        pass

    def Hidden_double_cunning_method_reverse(self, target, magnitude):
        pass

    def HP_buffer_method_reverse(self, target, magnitude):
        target.unapplyHPBuffer(self.parentName, self.duration)

    def Increased_movement_AP_cost_method_reverse(self, target, magnitude):
        target.statusMovementAPCost -= magnitude
        
    def Intuition_bonus_method_reverse(self, target, magnitude):
        target.statusIntuition -= magnitude
        
    def Knockback_resistance_bonus_method_reverse(self, target, magnitude):
        target.knockbackResistance -= magnitude

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
        target.statusMovementTiles += magnitude

    def Movement_tiles_penalty_method_reverse(self, target, magnitude):
        target.statusMovementTiles += magnitude

    def Nothing_method_reverse(self, target, magnitude):
        pass

    def No_turn_method_reverse(self, target, magnitude):
        pass

    def Numbing_poison_method_reverse(self, target, magnitude):
        target.removeOnHitEffect("NumbingPoison", magnitude)

    def On_hit_cripple_weapon_method_reverse(self, target, magnitude):
        target.removeOnHitMod('On_hit_cripple_weapon')

    def On_hit_frost_weapon_method_reverse(self, target, magnitude):
        target.removeOnHitEffect("FrostWeapon", magnitude)

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

    def Ranged_dodge_bonus_method_reverse(self, target, magnitude):
        target.statusRangedDodge -= magnitude

    def Ranged_dodge_penalty_method_reverse(self, target, magnitude):
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

    def Send_empathy_damage_to_summon_method_reverse(self, target, magnitude):
        target.empathyToSummon = 0

    def Set_maximum_stealth_break_chance_method_reverse(self, target, magnitude):
        target.stealthBreakMaxOverride = 100

    def Set_movement_AP_cost_method_reverse(self, target, magnitude):
        Combat.setMovementCost(target, -1)

    def Slashing_resist_penalty_method_reverse(self, target, magnitude):
        target.statusSlashingResistance += 25
        
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
        'Elemental_offense_arcane' : Elemental_offense_arcane_method,
        'Elemental_offense_divine' : Elemental_offense_divine_method,
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
        'Intuition_bonus' : Intuition_bonus_method,
        'Knockback_resistance_bonus' : Knockback_resistance_bonus_method,
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
        'Refund_mana_on_resist' : None,
        'Send_empathy_damage_to_summon' : Send_empathy_damage_to_summon_method,
        'Set_maximum_stealth_break_chance' : Set_maximum_stealth_break_chance_method,
        'Set_movement_AP_cost' : Set_movement_AP_cost_method,
        'Slashing_resist_penalty' : Slashing_resist_penalty_method,
        'Snake_style' : None,
        'Sneak_bonus' : Sneak_bonus_method,
        'Sneak_penalty' : Sneak_penalty_method,
        'Spellpower_bonus' : Spellpower_bonus_method,
        'Spellpower_penalty' : Spellpower_penalty_method,
        'Spell_failure_chance' : Spell_failure_chance_method,
        'Stun_internal' : None,
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
        'Elemental_offense_arcane' : Elemental_offense_arcane_method_reverse,
        'Elemental_offense_divine' : Elemental_offense_divine_method_reverse,
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
        'Intuition_bonus' : Intuition_bonus_method_reverse,
        'Knockback_resistance_bonus' : Knockback_resistance_bonus_method_reverse,
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
        'Refund_mana_on_resist' : None,
        'Send_empathy_damage_to_summon' : Send_empathy_damage_to_summon_method_reverse,
        'Set_maximum_stealth_break_chance' : Set_maximum_stealth_break_chance_method_reverse,
        'Set_movement_AP_cost' : Set_movement_AP_cost_method_reverse,
        'Slashing_resist_penalty' : Slashing_resist_penalty_method_reverse,
        'Snake_style' : None,
        'Sneak_bonus' : Sneak_bonus_method_reverse,
        'Sneak_penalty' : Sneak_penalty_method_reverse,
        'Spellpower_bonus' : Spellpower_bonus_method_reverse,
        'Spellpower_penalty' : Spellpower_penalty_method_reverse,
        'Spell_failure_chance' : Spell_failure_chance_method_reverse,
        'Stun_internal' : None,
        'Stunning_recovery_internal' : None,
        'Target_throat_internal' : Target_throat_method_reverse,
        'Tiger_style' : None,
        'Trap_evade_bonus' : Trap_evade_bonus_method_reverse,
        'Trap_evade_penalty' : Trap_evade_penalty_method_reverse,
        'Vile_poison_internal' : Vile_poison_method_reverse,
        'Weapon_damage_bonus' : Weapon_damage_bonus_method_reverse
    }
    
    textDict = {
        'Applied_poison_rating_bonus' : 
            "Poison-based attacks will have a greater chance to overcome Poison tolerance. (Rating + {magnitude})",
        'Attack_power_bonus' : 
            "Monster attack damage is increased by {magnitude}%.",
        'Attack_power_penalty' : 
            "Monster attack damage is reduced by {magnitude}%.",
        'Arcane_archer_mana_regen_penalty' : 
            "Mana recovered from ranged attacks is reduced by {magnitude}.",
        'Armor_penetration_bonus' : 
            "Attacks will ignore an additional {magnitude}% of Damage Reduction (DR).",
        'Avoidance' : 
            "Physical attacks have at least a {magnitude}% chance of missing completely.",
        'Awareness_penalty' : 
            "Awareness is reduced by {magnitude} points, lowering the chance of detecting traps or stealthed targets.",
        'Bleeding' : 
            "Current HP is lowered by {magnitude}% each turn.",
        'Combo_attack_internal' : 
            "A combo attack has been performed.",
        'Crane_style' : 
            "The Crane style is enabled lending ranged attack bonuses and access to Crane abilities.",
        'Critical_chance_bonus' :
            "Chance to critically hit on physical attacks is {magnitude}% higher.",
        'Critical_magnitude_bonus' :
            "Bonus damage dealt on a critical hit is {magnitude}% greater than usual.",
        'Damage_over_time' : 
            "Each turn, {magnitude} {element} damage will be received.", 
        'Dodge_bonus' :
            "Chance to dodge attacks is higher than usual. (Dodge +{magnitude})",
        'Dodge_penalty' :
            "Chance to dodge attacks is lower then usual. (Dodge -{magnitude})",
        'Double_dodge_internal' :
            "Chance to dodge attacks is higher than usual. (Dodge +{magnitude} x # of stacks)", 
        'Dragon_style' : 
            "The Dragon style is enabled, lending a balanced approach to combat and Dragon abilities.",
        'DR_bonus' :
            "Armor is stronger than normal, increasing Damage Reduction (DR) by {magnitude} points.",
        'DR_penalty' :
            "Armor is weaker than normal, lowering Damage Reduction (DR) by {magnitude} points.",
        'Elemental_offense_arcane' :
            "The power of Arcane damage dealt has been increased {magnitude}%.",
        'Elemental_offense_divine' :
            "The power of Divine damage dealt has been increased {magnitude}%.",
        'Elemental_resistance_arcane' :
            "Damage received from Arcane sources is reduced by {magnitude}%.",
        'Elemental_resistance_cold' :
            "Damage received from Cold sources is reduced by {magnitude}%.",
        'Elemental_resistance_electric' :
            "Damage received from Electric sources is reduced by {magnitude}%.",
        'Elemental_resistance_divine' :
            "Damage received from Divine sources is reduced by {magnitude}%.",
        'Elemental_resistance_fire' :
            "Damage received from Fire sources is reduced by {magnitude}%.",
        'Elemental_resistance_poison' :
            "Damage received from Poison sources is reduced by {magnitude}%.",
        'Elemental_resistance_shadow' :
            "Damage received from Shadow sources is reduced by {magnitude}%.",
        'Elemental_vulnerability' :
            "Incoming elemental damage of the {element} type is increased by {magnitude}%.",
        'Hidden' :
            "Hidden from creatures that fail their Awareness check.",
        'Hidden_double_cunning' :
            "Hidden from creatures that fail their Awareness check.",
        'HP_buffer' :
            "Temporary HP will prevent most incoming damage until depleted.",
        'Increased_movement_AP_cost' :
            "Movement is more difficult and costs more AP per movement action.",
        'Intuition_bonus' :
            "Intuition is {magnitude} higher, making it easier to detect traps and receive less harm from them.",
        'Knockback_resistance_bonus' :
            "Chance to be knocked back from attacks and spells is {magnitude}% lower than usual.",
        'Magic_resist_bonus' :
            "Magic resist has been raised {magnitude} points, increasing the chance that incoming hostile spells will have no effect.",
        'Magic_resist_penalty' :
            "Magic resist has been lowered {magnitude} points, decreasing the chance that incoming hostile spells will have no effect.",
        'Melee_accuracy_bonus' :
            "Melee accuracy has been raised {magnitude} points.  Melee attacks will hit their targets more frequently.",
        'Melee_accuracy_penalty' :
            "Melee accuracy has been lowered {magnitude} points.  Melee attacks will miss their targets more frequently.",
        'Melee_dodge_bonus' :
            "Dodge against melee attacks has been raised {magnitude} points.  Melee attacks will be easier to dodge.",
        'Melee_force_bonus' :
            "Melee Force has been raised {magnitude}%.  Outgoing Melee attacks will deal additional damage dependent on Might.",
        'Might_bonus' :
            "Might has been raised {magnitude} points.  Outgoing Melee attacks will deal additional damage dependent on Force.",
        'Might_penalty' :
            "Might has been reduced {magnitude} points.  Outgoing Melee attacks will deal less damage dependent on Force.",
        'Numbing_poison_internal' :
            "Numbing poison has been applied to weapons.  Targets hit may move fewer tiles next turn.",
        'Movement_speed_penalty' :
            "Movement speed has been decreased; {magnitude} fewer tiles may be moved per movement action.",
        'Movement_tiles_penalty' :
            "Movement speed has been decreased; {magnitude} fewer tiles may be moved per movement action.",
        'No_turn' :
            "Stunned for this turn.",
        'On_hit_cripple_weapon' :
            "This weapon will cripple targets some of the time, lowering movement speed and attack power.",
        'On_hit_frost_weapon' :
            "This weapon will coat targets in frost some of the time, lowering Dodge.",
        'On_hit_mage_hunting' :
            "This weapon is more likely to hit and will deal more damage to casters.",
        'On_hit_stun' :
            "This weapon has a chance to stun targets.",
        'On_hit_suppressing_weapon' :
            "This weapon has a chance to suppress targets, lowering accuracy and attack power.",
        'Overall_damage_bonus' :
            "This weapon will deal {magnitude}% bonus damage.",
        'Overall_damage_penalty' :
            "This weapon will deal {magnitude}% less damage.",
        'Panther_style' :
            "The Panther style has been enabled, granting offensive bonuses and giving access to Panther abilities.",
        'Poison_tolerance_bonus' :
            "Poison Tolerance has been increased {magnitude} points, increasing the chance to ignore poison effects.",
        'Poison_tolerance_penalty' :
            "Poison Tolerance has been decreased {magnitude} points, lowering the chance to ignore poison effects.",
        'Potion_effect_bonus' :
            "Potions will recover HP/MP an additional {magnitude}%.",
        'Prepare_melee_dodge_counterattack' :
            "The next melee attack dodged will be counter-attacked.",
        'Ranged_accuracy_bonus' :
            "Ranged accuracy has been raised {magnitude} points, increasing the chance of hitting with Ranged attacks.",
        'Ranged_accuracy_penalty' :
            "Ranged accuracy has been lowered {magnitude} points, decreasing the chance of hitting with Ranged attacks.",
        'Ranged_critical_magnitude_bonus' :
            "Bonus damage from ranged critical hits has been raised by {magnitude}%.",
        'Ranged_dodge_bonus' :
            "Dodge versus Ranged attacks has been increased by {magnitude} points, increasing the chance of Dodging Ranged attacks.",
        'Ranged_dodge_penalty' :
            "Dodge versus Ranged attacks has been decreased by {magnitude} points, decreasing the chance of Dodging Ranged attacks.",
        'Ranged_force_bonus' :
            "The Force of ranged attacks has been increased; Damage dealt with ranged attacks will be higher dependent on Might.",
        'Recover_HP_percent' :
            "{magnitude}% of HP will be recovered each turn.",
        'Redirect_melee_attacks' :
            "TODO",
        'Reduced_stealth_AP_cost' :
            "The AP Cost of entering stealth has been decreased.",
        'Reduced_missile_range' :
            "Ranged attacks have reduced range.",
        'Refund_mana_on_resist' :
            "If an outgoing spell is resisted, some MP will be refunded.",
        'Send_empathy_damage_to_summon' :
            "TODO",
        'Set_maximum_stealth_break_chance' :
            "Chance to break stealth of most attacks has been limited to at most {magnitude}%.",
        'Set_movement_AP_cost' :
            "The AP movement cost has been altered for your next move action.",
        'Slashing_resist_penalty' :
            "Incoming slashing physical damage will deal an additional {magnitude}% damage.",
        'Snake_style' :
            "The Snake style has been enabled, granting bonus melee accuracy, Piety, and giving access to Snake skills.",
        'Sneak_bonus' :
            "Sneak has been increased by {magnitude} points.  Chance to avoid detection while stealthed is higher.",
        'Sneak_penalty' :
            "Sneak has been decreased by {magnitude} points.  Chance to avoid detection wihle stealthed is lower.",
        'Spellpower_bonus' :
            "Spellpower has been increased by {magnitude} points.  Spells will be more effective overall.",
        'Spellpower_penalty' :
            "Spellpower has been decreased by {magnitude} points.  Spells will be less effective overall.",
        'Spell_failure_chance' :
            "Spells have a {magnitude}% chance to fail while being cast.",
        'Stun_internal' :
            "Character is stunned and will not be able to perform any actions.",
        'Stunning_recovery_internal' :
            "Character is recovering from a stun and will regain some HP.",
        'Target_throat_internal' :
            "Character is targeting the vitals of its targets.  Various offensive bonuses have been granted.",
        'Tiger_style' :
            "The Tiger style has been enabled granting bonus defenses as well as access to Tiger abilities.",
        'Trap_evade_bonus' :
            "Trap Evade has been increased by {magnitude} points.  The chance of evading a sprung trap is greater than usual.",
        'Trap_evade_penalty' :
            "Trap Evade has been decreased by {magnitude} points.  The chance of evading a sprung trap is lower than usual.",
        'Vile_poison_internal' :
            "A vile poison is coating this weapon.  Targets hit may suffer reduced attack power and a chance to fail when casting spells.",
        'Weapon_damage_bonus' :
            "Weapon damage has been augmented with the element of {element}.  Attacks will deal additional damage."
    }



