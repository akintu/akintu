#!/usr/bin/python

import sys
from Person import *

class PlayerCharacter(object):
   def __init__(self):
   
       # Resources
       self._AP = None
       self._totalAP = None
       self._HP = None
       self._totalHP = None
       self._MP = None
       self._totalMP = None
       
       # Primary Attributes
       self._baseConstitution = None
       self._equipmentConstitution = None
       self._statusConstitution = None
       
       self._baseCunning = None
       self._equipmentCunning = None
       self._statusCunning = None     

       self._baseDexterity = None
       self._equipmentDexterity = None
       self._statusDexterity = None    

       self._basePiety = None
       self._equipmentPiety = None
       self._statusPiety = None 
       
       self._baseSorcery = None
       self._equipmentSorcery = None
       self._statusSorcery = None

       self._baseStrength = None
       self._equipmentStrength = None
       self._statusStrength = None
      
       # Derived Attributes
       self._baseArmorPenetration = None
       self._equipmentArmorPenetration = None
       self._statusArmorPenetration = None
       
       self._baseAwareness = None
       self._equipmentAwareness = None
       self._statusAwareness = None
       
       self._baseCriticalChance = None
       self._equipmentCriticalChance = None
       self._statusCriticalChance = None
       
       self._baseCriticalMagnitude = None
       self._equipmentCriticalMagnitude = None
       self._statusCriticalMagnitude = None
       
       self._baseDodge = None
       self._equipmentDodge = None
       self._statusDodge = None
       
       self._baseDR = None
       self._equipmentDR = None
       self._statusDR = None
       
       #self._baseForce = N\A
       self._equipmentForce = None
       self._statusForce = None
       
       self._baseMagicResist = None
       self._equipmentMagicResist = None
       self._statusMagicResist = None
       
       self._baseMeleeAccuracy = None
       self._equipmentMeleeAccuracy = None
       self._statusMeleeAccuracy = None
       
       self._baseMeleeDodge = None
       self._equipmentMeleeDodge = None
       self._statusMeleeDodge = None
       
       self._baseMight = None
       self._equipmentMight = None
       self._statusMight = None
       
       self._baseMovementTiles = None
       self._equipmentMovementTiles = None
       self._statusMovementTiles = None
       
       self._baseOverallDamageBonus = None
       self._equipmentOverallDamageBonus = None
       self._statusOverallDamageBonus = None
       
       self._basePoisonRatingBonus = None
       self._equipmentPoisonRatingBonus = None
       self._statusPoisonRatingBonus = None
       
       self._basePoisonTolerance = None
       self._equipmentPoisonTolerance = None
       self._statusPoisonTolerance = None      
       
       self._basePotionEffect = None
       self._equipmentPotionEffect = None
       self._statusPotionEffect = None
       
       self._baseRangedAccuracy = None
       self._equipmentRangedAccuracy = None
       self._statusRangedAccuracy = None
       
       self._baseRangedCriticalMagnitude = None
       self._equipmentRangedCriticalMagnitude = None
       self._statusRangedCriticalMagnitude = None
       
       self._baseRangedDodge = None
       self._equipmentRangedDodge = None
       self._statusRangedDodge = None     

       self._baseRangedForce = None
       self._equipmentRangedForce = None
       self._statusRangedForce = None   
       
       self._baseSneak = None
       self._equipmentSneak = None
       self._statusSneak = None
       
       self._baseSpellpower = None
       self._equipmentSpellpower = None
       self._statusSpellpower = None
       
       self._baseTrapEvade = None
       self._equipmentTrapEvade = None
       self._statusTrapEvade = None
       
       # Elemental Resistances
       
       self._baseArcaneResistance = None
       self._equipmentArcaneResistance = None
       self._statusArcaneResistance = None
       
       self._baseColdResistance = None
       self._equipmentColdResistance = None
       self._statusColdResistance = None
       
       self._baseDivineResistance = None
       self._equipmentDivineResistance = None
       self._statusDivineResistance = None
       
       self._baseElectricResistance = None
       self._equipmentElectricResistance = None
       self._statusElectricResistance = None
       
       self._baseFireResistance = None
       self._equipmentFireResistance = None
       self._statusFireResistance = None
       
       self._basePoisonResistance = None
       self._equipmentPoisonResistance = None
       self._statusPoisonResistance = None
       
       self._baseShadowResistance = None
       self._equipmentShadowResistance = None
       self._statusShadowResistance = None
       
       # Elemental Bonus Damages
       
       self._baseArcaneBonusDamage = None
       self._equipmentArcaneBonusDamage = None
       self._statusArcaneBonusDamage = None
       
       self._baseColdBonusDamage = None
       self._equipmentColdBonusDamage = None
       self._statusColdBonusDamage = None
       
       self._baseDivineBonusDamage = None
       self._equipmentDivineBonusDamage = None
       self._statusDivineBonusDamage = None
       
       self._baseElectricBonusDamage = None
       self._equipmentElectricBonusDamage = None
       self._statusElectricBonusDamage = None
       
       self._baseFireBonusDamage = None
       self._equipmentFireBonusDamage = None
       self._statusFireBonusDamage = None
       
       self._basePoisonBonusDamage = None
       self._equipmentPoisonBonusDamage = None
       self._statusPoisonBonusDamage = None
       
       self._baseShadowBonusDamage = None
       self._equipmentShadowBonusDamage = None
       self._statusShadowBonusDamage = None
       
       # TODO: Write method applyOnHitMod(name, *args)
       # TODO: Write method removeOnHitMod(name)
       
       # Intrinsic properties (read-only)
       
       self._growthType = None 
       self._characterClass = None
       
       # Class specific properties and weird things:
       
       self._arcaneArcherManaRegenLow = None
       self._arcaneArcherManaRegenHigh = None
       self._arcaneArcherManaRegenBase = None
       
       self._avoidanceChance = None
       
       self._HPBufferList = None
       
       self._baseMovementAPCost = None
       self._equipmentMovementAPCost = None
       self._overrideMovementAPCost = None
       self._statusMovementAPCost = None
       
       self._baseMeleeAttackAPCost = None
       
       self._ninjaStyle = None
       
       self._baseRangedAttackAPCost = None
       
       self._statusSpellFailureChance = None
       
       # self._activeSummon
       # self._abilityAPModsList [["AbilityName", -2], [...]]
       # self._spellMPModsList [["SpellName", -1], [...]]
       # self._empathyToSummon 
       # self._stealthBreakMaxOverride Default 100
       
    # Resources (AP, MP, HP)
       
    @property
    def AP(self):
        """The current Action Points of a PlayerCharacter"""
        return self._AP
        
    @AP.setter
    def AP(self, value):
        if value > totalAP: 
            value = totalAP
        self._AP = value
    
    @property
    def totalAP(self):
        """A value for the adjusted total AP for the player.
        this value can change only by equipping magical eqiupment
        that improves the max AP of a player."""
        return self._maximumAP
        
    @totalAP.setter
    def totalAP(self, value):
        if value > 25: 
            value = 25
        if value < 0: 
            value = 0
        self._totalAP = value       
    
    @property
    def HP(self):
        """The current hit points of the player.  When it 
        reaches 0, the player dies."""
        return self._HP
    
    @HP.setter
    def HP(self, value):
        if value > totalHP:
            value = totalHP
        if value < 0:
            value = 0
        self._HP = value            
    
    @property
    def totalHP(self):
        """The maximum HP of the player.  Is determined by eqiupment,
        skills, statuses, and base attributes."""
        return self._totalHP
    
    @totalHP.setter
    def totalHP(self, value):
        """Automatically restricts the current HP to the new maximum
        if necessary."""
        if value < 1:
            value = 1
        self._totalHP = value   
        if HP > totalHP:
            HP = totalHP        
    
    @property
    def MP(self):
        """The current Mana Points of a PlayerCharacter"""
        return self._MP
    
    @MP.setter
    def MP(self, value):
        """Will not exceed totalMP"""
        if value < 0:
            value = 0
        if value > totalMP:
            value = totalMP
        self._MP = value
        
    @property
    def totalMP(self):
        """The maximum MP of the player.  Is determined by class, level,
        equipment, skills, statuses, and base attributes."""
        return self._totalMP
        
    @totalMP.setter
    def totalMP(self, value):
        """Will automatically restrict the current MP to the new maximum
        if necessary."""
        if value < 0:
            value = 0
        if self.growthType == "Non-Caster":
            totalMP = 0
            return
        
        self._totalMP = value
        if MP > totalMP:
            MP = totalMP
            
    # Intrinsic (read-only) properties
    
    @property
    def totalDexterity(self):
        """Should always equal base + equipment + status Dexterity, except
        when that equation would reduce it to a non-positive value."""
        MINIMUM = 1
        return max(MINIMUM, 
                   baseDexterity + equipmentDexterity + statusDexterity) 
    
    @property
    def equipmentDexterity(self):
        """Equals the total dexterity bonus from all pieces of equipment
        currently equipped.  Will not automatically update with equipment
        change.  That must be done elsewhere."""
        return self._equipmentDexterity
        
    @equipmentDexterity.setter
    def equipmentDexterity(self, value):
        """
        int value: should be the sum of the Dexterity mods from all equipment.
        """
        self._equipmentDexterity = value
        
    @property
    def statusDexterity(self):
        """Equals the total dexterity from all buffs and debuffs of any kind
        at the current point in time.  Will not automatically update with 
        status changes.  That must be done elsewhere."""
        return self._statusDexterity
        
    @statusDexterity.setter
    def statusDexterity(self, value):
        """
        int value: should be the sum of all Dex mods from all statuses.
        """
        self._statusDexterity = value
        
    @property
    def baseDexterity(self):
        """Equals the Dexterity from all *static* abilities and levelup stat
        gains."""
        return self._baseDexterity

    @baseDexterity.setter
    def baseDexterity(self, value):
        """
        int value: should be the total dexterity without *dynamic* mods.
        
        Will not allow non-positive values.
        """
        if value > 0:
            self_.baseDexterity = value
        
    @property
    def totalStrength(self):
        """Should always equal base + equipment + status Strength, except
        when that equation would reduce it to a non-positive value."""
        MINIMUM = 1
        return max(MINIMUM, 
                   baseStrength + equipmentStrength + statusStrength)

    @property
    def equipmentStrength(self):
        """Equals the total strength bonus from all pieces of equipment
        currently equipped.  Will not automatically update with equipment
        change.  That must be done elsewhere."""
        return self._equipmentStrength
        
    @equipmentStrength.setter
    def equipmentStrength(self, value):
        """
        int value: should be the sum of the Strength mods from all equipment.
        """
        self._equipmentStrength = value 

    @property
    def statusStrength(self):
        """Equals the total strength from all buffs and debuffs of any kind
        at the current point in time.  Will not automatically update with 
        status changes.  That must be done elsewhere."""
        return self._statusStrength
        
    @statusStrength.setter
    def statusStrength(self, value):
        """
        int value: should be the sum of all Dex mods from all statuses.
        """
        self._statusStrength = value
        
    @property
    def baseStrength(self):
        """Equals the Strength from all *static* abilities and levelup stat
        gains."""
        return self._baseStrength

    @baseStrength.setter
    def baseStrength(self, value):
        """
        int value: should be the total strength without *dynamic* mods.
        
        Will not allow non-positive values.
        """
        if value > 0:
            self_.baseStrength = value      
    
    @property
    def totalCunning(self):
        """Should always equal base + equipment + status Cunning, except
        when that equation would reduce it to a non-positive value."""
        MINIMUM = 1
        return max(MINIMUM, 
                   baseCunning + equipmentCunning + statusCunning)

    @property
    def equipmentCunning(self):
        """Equals the total cunning bonus from all pieces of equipment
        currently equipped.  Will not automatically update with equipment
        change.  That must be done elsewhere."""
        return self._equipmentCunning
        
    @equipmentCunning.setter
    def equipmentCunning(self, value):
        """
        int value: should be the sum of the Cunning mods from all equipment.
        """
        self._equipmentCunning = value  

    @property
    def statusCunning(self):
        """Equals the total cunning from all buffs and debuffs of any kind
        at the current point in time.  Will not automatically update with 
        status changes.  That must be done elsewhere."""
        return self._statusCunning
        
    @statusCunning.setter
    def statusCunning(self, value):
        """
        int value: should be the sum of all Dex mods from all statuses.
        """
        self._statusCunning = value
        
    @property
    def baseCunning(self):
        """Equals the Cunning from all *static* abilities and levelup stat
        gains."""
        return self._baseCunning

    @baseCunning.setter
    def baseCunning(self, value):
        """
        int value: should be the total cunning without *dynamic* mods.
        
        Will not allow non-positive values.
        """
        if value > 0:
            self_.baseCunning = value   
    
    @property
    def totalSorcery(self):
        """Should always equal base + equipment + status Sorcery, except
        when that equation would reduce it to a non-positive value."""
        MINIMUM = 1
        return max(MINIMUM, 
                   baseSorcery + equipmentSorcery + statusSorcery)

    @property
    def equipmentSorcery(self):
        """Equals the total sorcery bonus from all pieces of equipment
        currently equipped.  Will not automatically update with equipment
        change.  That must be done elsewhere."""
        return self._equipmentSorcery
        
    @equipmentSorcery.setter
    def equipmentSorcery(self, value):
        """
        int value: should be the sum of the Sorcery mods from all equipment.
        """
        self._equipmentSorcery = value  

    @property
    def statusSorcery(self):
        """Equals the total sorcery from all buffs and debuffs of any kind
        at the current point in time.  Will not automatically update with 
        status changes.  That must be done elsewhere."""
        return self._statusSorcery
        
    @statusSorcery.setter
    def statusSorcery(self, value):
        """
        int value: should be the sum of all Dex mods from all statuses.
        """
        self._statusSorcery = value
        
    @property
    def baseSorcery(self):
        """Equals the Sorcery from all *static* abilities and levelup stat
        gains."""
        return self._baseSorcery

    @baseSorcery.setter
    def baseSorcery(self, value):
        """
        int value: should be the total sorcery without *dynamic* mods.
        
        Will not allow non-positive values.
        """
        if value > 0:
            self_.baseSorcery = value   

    @property
    def totalPiety(self):
        """Should always equal base + equipment + status Piety, except
        when that equation would reduce it to a non-positive value."""
        MINIMUM = 1
        return max(MINIMUM, 
                   basePiety + equipmentPiety + statusPiety)

    @property
    def equipmentPiety(self):
        """Equals the total piety bonus from all pieces of equipment
        currently equipped.  Will not automatically update with equipment
        change.  That must be done elsewhere."""
        return self._equipmentPiety
        
    @equipmentPiety.setter
    def equipmentPiety(self, value):
        """
        int value: should be the sum of the Piety mods from all equipment.
        """
        self._equipmentPiety = value    

    @property
    def statusPiety(self):
        """Equals the total piety from all buffs and debuffs of any kind
        at the current point in time.  Will not automatically update with 
        status changes.  That must be done elsewhere."""
        return self._statusPiety
        
    @statusPiety.setter
    def statusPiety(self, value):
        """
        int value: should be the sum of all Dex mods from all statuses.
        """
        self._statusPiety = value
        
    @property
    def basePiety(self):
        """Equals the Piety from all *static* abilities and levelup stat
        gains."""
        return self._basePiety

    @basePiety.setter
    def basePiety(self, value):
        """
        int value: should be the total piety without *dynamic* mods.
        
        Will not allow non-positive values.
        """
        if value > 0:
            self_.basePiety = value 
            
    @property
    def totalConstitution(self):
        """Should always equal base + equipment + status Constitution, except
        when that equation would reduce it to a non-positive value."""
        MINIMUM = 1
        return max(MINIMUM, 
                   baseConstitution + equipmentConstitution + statusConstitution)

    @property
    def equipmentConstitution(self):
        """Equals the total constitution bonus from all pieces of equipment
        currently equipped.  Will not automatically update with equipment
        change.  That must be done elsewhere."""
        return self._equipmentConstitution
        
    @equipmentConstitution.setter
    def equipmentConstitution(self, value):
        """
        int value: should be the sum of the Constitution mods from all equipment.
        """
        self._equipmentConstitution = value 

    @property
    def statusConstitution(self):
        """Equals the total constitution from all buffs and debuffs of any kind
        at the current point in time.  Will not automatically update with 
        status changes.  That must be done elsewhere."""
        return self._statusConstitution
        
    @statusConstitution.setter
    def statusConstitution(self, value):
        """
        int value: should be the sum of all Dex mods from all statuses.
        """
        self._statusConstitution = value
        
    @property
    def baseConstitution(self):
        """Equals the Constitution from all *static* abilities and levelup stat
        gains."""
        return self._baseConstitution

    @baseConstitution.setter
    def baseConstitution(self, value):
        """
        int value: should be the total constitution without *dynamic* mods.
        
        Will not allow non-positive values.
        """
        if value > 0:
            self_.baseConstitution = value  
            
    # Derived Attributes
    
@property
    def totalMeleeAccuracy(self):
        """
        MeleeAccuracy is determined by STR, DEX, equipment that boosts MeleeAccuracy,
        "static" abililties that boost MeleeAccuracy, and "dynamic"
        statuses that boost or reduce MeleeAccuracy.
        """
        return equipmentMeleeAccuracy + statusMeleeAccuracy + baseMeleeAccuracy
            
    @property
    def equipmentMeleeAccuracy(self):
        """
        The MeleeAccuracy granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentMeleeAccuracy
        
    @equipmentMeleeAccuracy.setter
    def equipmentMeleeAccuracy(self, value):
        """
        int value: should be the total meleeAccuracy given from equipment on
        """
        self._equipmentMeleeAccuracy = value
            
    @property
    def statusMeleeAccuracy(self):
        """
        The MeleeAccuracy gained or lost from the sum of statuses.
        """
        return self._statusMeleeAccuracy
        
    @statusMeleeAccuracy.setter
    def statusMeleeAccuracy(self, value):
        """
        int value: should be the total meleeAccuracy given from statuses.
        """
        self._statusMeleeAccuracy = value
        
    @property
    def baseMeleeAccuracy(self):
        """
        The MeleeAccuracy granted from STR, DEX and any "static" abilities
        """
        return self._baseMeleeAccuracy
        
    @baseMeleeAccuracy.setter
    def baseMeleeAccuracy(self, value):
        """
        int value: should be Dex/2 + Str/2 + static Ability Bonus
        """
        if value >= 0:
            self._baseMeleeAccuracy = value 
                
    @property
    def totalMeleeDodge(self):
        """
        MeleeDodge is bonus dodge granted from static abilities, magical
        equipment bonuses, and dynamic abilities/statuses.  It is normally zero
        as it is added to Dodge but is not very common.  It is not included in
        the normal totalDodge, so it will need to be added manually on the event
        of a melee incoming attack.
        """
        return equipmentMeleeDodge + statusMeleeDodge + baseMeleeDodge
    
    @property
    def equipmentMeleeDodge(self):
        """
        The MeleeDodge granted from any magical equipment bonuses.
        Will not automatically update.
        """
        return self._equipmentMeleeDodge
    
    @equipmentMeleeDodge.setter
    def equipmentMeleeDodge(self, value):
        """
        int value: should be the total meleeDodge given from equipment on
        """
        self._equipmentMeleeDodge = value
    
    @property
    def statusMeleeDodge(self):
        """
        The MeleeDodge gained or lost from the sum of statuses.
        """
        return self._statusMeleeDodge
    
    @statusMeleeDodge.setter
    def statusMeleeDodge(self, value):
        """
        int value: should be the total meleeDodge given from statuses.
        """
        self._statusMeleeDodge = value
    
    @property
    def baseMeleeDodge(self):
        """
        The MeleeDodge granted from static abilities.
        """
        return self._baseMeleeDodge
        
    @baseMeleeDodge.setter
    def baseMeleeDodge(self, value):
        """
        int value: should be whatever the static ability bonus is, or zero.
        """
        self._baseMeleeDodge = value
    
    @property
    def totalMight(self):
        """
        Might is determined by Strength, equipment that boosts Might,
        possible "static" abililties that boost Might, and "dynamic"
        statuses that boost or reduce Might.
        """
        return equipmentMight + statusMight + baseMight
            
    @property
    def equipmentMight(self):
        """
        The Might granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentMight
        
    @equipmentMight.setter
    def equipmentMight(self, value):
        """
        int value: should be the total might given from equipment on
        """
        self._equipmentMight = value
            
    @property
    def statusMight(self):
        """
        The Might gained or lost from the sum of statuses.
        """
        return self._statusMight
        
    @statusMight.setter
    def statusMight(self, value):
        """
        int value: should be the total might given from statuses.
        """
        self._statusMight = value
        
    @property
    def baseMight(self):
        """
        The Might granted from Strength and any "static" abilities
        """
        return self._baseMight
        
    @baseMight.setter
    def baseMight(self, value):
        """
        int value: should be max(0, (Strength - 10)) + static ability might
        """
        if value >= 0:
            self._baseMight = value
           
    @property
    def totalMovementTiles(self):
        """
        The number of tiles this character can move in a single movement-AP cost.
        Will almost always be 2
        Cannot be reduced below 1.
        """
        return min(self._baseMovementTiles + self._equipmentMovementTiles + 
               self._statusMovementTiles, 1)
            
    @property
    def baseMovementTiles(self):
        """
        As of Akintu tier 4, will always be exactly 2.
        """
        return self._baseMovementTiles
        
    @baseMovementTiles.setter
    def baseMovementTiles(self, value):
        """
        int Tiles
        """
        self._baseMovementTiles = value
        
    @property
    def equipmentMovementTiles(self):
        """It should be ultra-rare for an item to modify this."""
        return self._eqiupmentMovementTiles
        
    @equipmentMovementTiles.setter
    def equipmentMovementTiles(self, value):
        self._equipmentMovementTiles = value
        
    @property
    def statusMovementTiles(self):
        return self._statusMovementTiles
        
    @statusMovementTiles.setter
    def statusMovementTiles(self, value):
        self._statusMovementTiles = value
       
    @property
    def totalOverallDamageBonus(self):
        """ Should be 0 for 0% by default.
            Would be 14 for 14% (not 1.14)
        """
        return self._baseOverallDamageBonus + self._equipmentOverallDamageBonus +
               self._statusOverallDamageBonus
               
    @property
    def baseOverallDamageBonus(self):
        """ Should almost always be 0 for 0%."""
        return self._baseOverallDamageBonus
        
    @baseOverallDamageBonus.setter
    def baseOverallDamageBonus(self, value):
        """ Set to ints not floats."""
        self._baseOverallDamageBonus = value
        
    @property
    def eqiupmentOverallDamageBonus(self):
        return self._equipmentOverallDamageBonus
        
    @equipmentOverallDamageBonus.setter
    def equipmentOverallDamageBonus(self, value):
        self._equipmentOverallDamageBonus = value
        
    @property
    def statusOverallDamageBonus(self):
        return self._statusOverallDamageBonus
        
    @statusOverallDamageBonus.setter
    def statusOverallDamageBonus(self, value):
        return self._statusOverallDamageBonus
        
    @property
    def totalPoisonRatingBonus(self):
        """ The bonus applied to any applied poison, or any ability
        that has a poison effect that uses the poison rating roll 
        (which is almost all of them other than weapon elemental damage.)
        """
        return self._basePoisonRatingBonus + self.equipmentPoisonRatingBonus +
               self._statusPoisonRatingBonus
    
    @property
    def basePoisonRatingBonus(self):
        """ int """
        return self._basePoisonRatingBonus
        
    @basePoisonRatingBonus.setter
    def basePoisonRatingBonus(self, value):
       self._basePoisonRatingBonus = value
       
    @property
    def equipmentPoisonRatingBonus(self):
        return self._equipmentPoisonRatingBonus
        
    @equipmentPoisonRatingBonus.setter
    def equipmentPoisonRatingBonus(self, value):
        self._equipmentPoisonRatingBonus = value
        
    @property
    def statusPoisonRatingBonus(self):
        return self._statusPoisonRatingBonus
        
    @statusPoisonRatingBonus.setter
    def statusPoisonRatingBonus(self, value):
        self._statusPoisonRatingBonus = value
        
    @property
    def totalRangedAccuracy(self):
        """
        RangedAccuracy is determined by DEX, equipment that boosts RangedAccuracy,
        "static" abililties that boost RangedAccuracy, and "dynamic"
        statuses that boost or reduce RangedAccuracy.
        """
        return equipmentRangedAccuracy + statusRangedAccuracy + baseRangedAccuracy
            
    @property
    def equipmentRangedAccuracy(self):
        """
        The RangedAccuracy granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentRangedAccuracy
        
    @equipmentRangedAccuracy.setter
    def equipmentRangedAccuracy(self, value):
        """
        int value: should be the total rangedAccuracy given from equipment on
        """
        self._equipmentRangedAccuracy = value
            
    @property
    def statusRangedAccuracy(self):
        """
        The RangedAccuracy gained or lost from the sum of statuses.
        """
        return self._statusRangedAccuracy
        
    @statusRangedAccuracy.setter
    def statusRangedAccuracy(self, value):
        """
        int value: should be the total rangedAccuracy given from statuses.
        """
        self._statusRangedAccuracy = value
        
    @property
    def baseRangedAccuracy(self):
        """
        The RangedAccuracy granted from DEX and any "static" abilities
        """
        return self._baseRangedAccuracy
        
    @baseRangedAccuracy.setter
    def baseRangedAccuracy(self, value):
        """
        int value: should be Dex + static Ability Bonus
        """
        if value >= 0:
            self._baseRangedAccuracy = value            

    @property
    def totalRangedCriticalMagnitude(self):
        """
        Ranged critical magnitude is bonus only, that is, it is 100 by default
        and the % is MULTIPLIED with the normal critical magnitude.  
        
        This stat itself is 100 + each component bonus to RCM.
        """
        return (100 + equipmentRangedCriticalMagnitude +
                statusRangedCriticalMagnitude + baseRangedCriticalMagnitude)        
            
    @property
    def equipmentRangedCriticalMagnitude(self):
        """
        Any ranged critical magnitude granted from any magical equipment
        currently equipped.  
        Will not automatically update.
        """
        return self._equipmentRangedCriticalMagnitude
            
    @equipmentRangedCriticalMagnitude.setter:
    def equipmentRangedCriticalMagnitude(self, value):
        """
        int value: should be the total ranged critical magnitude from equipment
        on, if any.
        """
        self._equipmentRangedCriticalMagnitude = value
        
    @property
    def statusRangedCriticalMagnitude(self):
        """
        The ranged crit mag from statuses, if any.
        """
        return self._statusRangedCriticalMagnitude
    
    @statusRangedCriticalMagnitude.setter
    def statusRangedCriticalMagnitude(self, value):
        """
        int value: should be the total % ranged crit mag from statuses.
        """
        self._statusRangedCriticalMagnitude = value
        
    @property
    def baseRangedCriticalMagnitude(self):
        """
        The ranged crit mag from static abilities. 0 by default.
        """
        return self._baseRangedCriticalMagnitude
        
    @baseRangedCriticalMagnitude.setter
    def baseRangedCriticalMagnitude(self, value):
        """
        int value: should be a % bonus from static abilities only.
          will mostly be 0.
        """
        self._baseRangedCriticalMagnitude = value
            
    @property
    def totalSpellpower(self):
        """
        Spellpower is determined by SOR, equipment that boosts Spellpower,
        "static" abililties that boost Spellpower, and "dynamic"
        statuses that boost or reduce Spellpower.
        """
        return equipmentSpellpower + statusSpellpower + baseSpellpower
            
    @property
    def equipmentSpellpower(self):
        """
        The Spellpower granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentSpellpower
        
    @equipmentSpellpower.setter
    def equipmentSpellpower(self, value):
        """
        int value: should be the total spellpower given from equipment on
        """
        self._equipmentSpellpower = value
            
    @property
    def statusSpellpower(self):
        """
        The Spellpower gained or lost from the sum of statuses.
        """
        return self._statusSpellpower
        
    @statusSpellpower.setter
    def statusSpellpower(self, value):
        """
        int value: should be the total spellpower given from statuses.
        """
        self._statusSpellpower = value
        
    @property
    def baseSpellpower(self):
        """
        The Spellpower granted from SOR and any "static" abilities
        """
        return self._baseSpellpower
        
    @baseSpellpower.setter
    def baseSpellpower(self, value):
        """
        int value: should be Sorc + static Ability Bonus
        """
        if value >= 0:
            self._baseSpellpower = value    
            
    @property
    def totalCriticalChance(self):
        """
        CriticalChance is determined by CUN, equipment that boosts CriticalChance,
        "static" abililties that boost CriticalChance, and "dynamic"
        statuses that boost or reduce CriticalChance.  This does not factor in
        extra critical chance from accuracy beyond 100%
        """
        return equipmentCriticalChance + statusCriticalChance + baseCriticalChance
            
    @property
    def equipmentCriticalChance(self):
        """
        The CriticalChance granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentCriticalChance
        
    @equipmentCriticalChance.setter
    def equipmentCriticalChance(self, value):
        """
        float value: should be the total criticalChance given from equipment on
        """
        self._equipmentCriticalChance = value
            
    @property
    def statusCriticalChance(self):
        """
        The CriticalChance gained or lost from the sum of statuses.
        """
        return self._statusCriticalChance
        
    @statusCriticalChance.setter
    def statusCriticalChance(self, value):
        """
        float value: should be the total criticalChance given from statuses.
        """
        self._statusCriticalChance = value
        
    @property
    def baseCriticalChance(self):
        """
        The CriticalChance granted from CUN and any "static" abilities
        """
        return self._baseCriticalChance
        
    @baseCriticalChance.setter
    def baseCriticalChance(self, value):
        """
        float value: should be (0.5*(CUN over 10)) + static Ability Bonus
        """
        if value >= 0:
            self._baseCriticalChance = value            
            
     @property
    def totalCriticalMagnitude(self):
        """
        CriticalMagnitude is determined by weapon critical multiplier and any magical
        bonuses from equipment toward critical magnitude, 
        "static" abililties that boost CriticalMagnitude, and "dynamic"
        statuses that boost or reduce CriticalMagnitude.  Bonuses to critical magnitude
        from the different sources are multiplicative with a rating of 100 = to 
        a neutral multiplier of 100%.  The result is, the total is adjusted so it is
        the exact float/int to multiply the damage by upon a critical hit with no
        further division.
        """
        return (equipmentCriticalMagnitude/100 * baseCriticalMagnitude/100 *
                (100 + statusCriticalMagnitude/100))        
            
    @property
    def equipmentCriticalMagnitude(self):
        """
        The CriticalMagnitude granted from both the base critical multiplier of the 
        currently equipped weapon and any magical bonuses from equipment further
        boosting it.
        
        Will not automatically update.
        """
        return self._equipmentCriticalMagnitude
        
    @equipmentCriticalMagnitude.setter
    def equipmentCriticalMagnitude(self, value):
        """
        float value: should be the total criticalMagnitude given from equipment on
                     base level = the 'critical multiplier' of the weapon
        """
        self._equipmentCriticalMagnitude = value
            
    @property
    def statusCriticalMagnitude(self):
        """
        The CriticalMagnitude gained or lost from the sum of statuses.
        """
        return self._statusCriticalMagnitude
        
    @statusCriticalMagnitude.setter
    def statusCriticalMagnitude(self, value):
        """
        float value: should be the total criticalMagnitude given from statuses.
                     base level = 0
        """
        self._statusCriticalMagnitude = value
        
    @property
    def baseCriticalMagnitude(self):
        """
        The CriticalMagnitude granted from any "static" abilities
        """
        return self._baseCriticalMagnitude
        
    @baseCriticalMagnitude.setter
    def baseCriticalMagnitude(self, value):
        """
        float value: should be 100 + any static Ability Bonus
                     must be non-negative
        """
        if value >= 0:
            self._baseCriticalMagnitude = value     
            
    @property
    def totalMagicResist(self):
        """
        MagicResist is determined by PIE, equipment that boosts MagicResist,
        "static" abililties that boost MagicResist, and "dynamic"
        statuses that boost or reduce MagicResist.
        """
        return equipmentMagicResist + statusMagicResist + baseMagicResist
            
    @property
    def equipmentMagicResist(self):
        """
        The MagicResist granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentMagicResist
        
    @equipmentMagicResist.setter
    def equipmentMagicResist(self, value):
        """
        int value: should be the total magicResist given from equipment on
        """
        self._equipmentMagicResist = value
            
    @property
    def statusMagicResist(self):
        """
        The MagicResist gained or lost from the sum of statuses.
        """
        return self._statusMagicResist
        
    @statusMagicResist.setter
    def statusMagicResist(self, value):
        """
        int value: should be the total magicResist given from statuses.
        """
        self._statusMagicResist = value
        
    @property
    def baseMagicResist(self):
        """
        The MagicResist granted from PIE and any "static" abilities
        """
        return self._baseMagicResist
        
    @baseMagicResist.setter
    def baseMagicResist(self, value):
        """
        int value: should be PIE + static Ability Bonus
        """
        self._baseMagicResist = value               
            
    @property
    def totalPoisonTolerance(self):
        """
        PoisonTolerance is determined by CON, equipment that boosts PoisonTolerance,
        "static" abililties that boost PoisonTolerance, and "dynamic"
        statuses that boost or reduce PoisonTolerance.
        """
        return equipmentPoisonTolerance + statusPoisonTolerance + basePoisonTolerance
            
    @property
    def equipmentPoisonTolerance(self):
        """
        The PoisonTolerance granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentPoisonTolerance
        
    @equipmentPoisonTolerance.setter
    def equipmentPoisonTolerance(self, value):
        """
        int value: should be the total poisonTolerance given from equipment on
        """
        self._equipmentPoisonTolerance = value
            
    @property
    def statusPoisonTolerance(self):
        """
        The PoisonTolerance gained or lost from the sum of statuses.
        """
        return self._statusPoisonTolerance
        
    @statusPoisonTolerance.setter
    def statusPoisonTolerance(self, value):
        """
        int value: should be the total poisonTolerance given from statuses.
        """
        self._statusPoisonTolerance = value
        
    @property
    def basePoisonTolerance(self):
        """
        The PoisonTolerance granted from CON and any "static" abilities
        """
        return self._basePoisonTolerance
        
    @basePoisonTolerance.setter
    def basePoisonTolerance(self, value):
        """
        int value: should be CON above 10 + static Ability Bonus
        """
        if value >= 0:
            self._basePoisonTolerance = value   
            
    @property
    def totalPotionEffect(self):
        """
        An int representing how much healing and mana potions are
        augmented.  Starts at 100 but is increased by many possible
        factors, especially Sorcery."""
        return self._basePotionEffect + self._equipmentPotionEffect +
               self._statusPotionEffect
               
    @property
    def basePotionEffect(self):
        """An int starting at 100 that indicates 100%"""
        return self._basePotionEffect
        
    @basePotionEffect.setter
    def basePotionEffect(self, value):
        """The contribution from SOR should be max(0, (SOR - 10) * 5)
        or in other words, 5% per point of SOR beyond 10 but no penalty
        given for SOR less than 10."""
        self._basePotionEffect = value
        
    @property
    def equipmentPotionEffect(self):
        return self._equipmentPotionEffect
        
    @equipmentPotionEffect.setter
    def equipmentPotionEffect(self, value):
        self._equipmentPotionEffect = value
        
    @property
    def statusPotionEffect(self):
        return self._statusPotionEffect
        
    @statusPotionEffect.setter
    def statusPotionEffect(self, value):
        self._statusPotionEffect = value
            
    @property
    def totalDodge(self):
        """
        Dodge is determined by DEX, equipment that boosts Dodge,
        "static" abililties that boost Dodge, and "dynamic"
        statuses that boost or reduce Dodge.  Does not include
        rangedDodge or meleeDodge (even when relevant.)
        """
        return equipmentDodge + statusDodge + baseDodge
            
    @property
    def equipmentDodge(self):
        """
        The Dodge granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentDodge
        
    @equipmentDodge.setter
    def equipmentDodge(self, value):
        """
        int value: should be the total dodge given from equipment on
        """
        self._equipmentDodge = value
            
    @property
    def statusDodge(self):
        """
        The Dodge gained or lost from the sum of statuses.
        """
        return self._statusDodge
        
    @statusDodge.setter
    def statusDodge(self, value):
        """
        int value: should be the total dodge given from statuses.
        """
        self._statusDodge = value
        
    @property
    def baseDodge(self):
        """
        The Dodge granted from DEX and any "static" abilities
        """
        return self._baseDodge
        
    @baseDodge.setter
    def baseDodge(self, value):
        """
        int value: should be Dex + static Ability Bonus
        """
        self._baseDodge = value             

    @property
    def totalTrapEvade(self):
        """
        TrapEvade is determined by CUN, DEX, equipment that boosts TrapEvade,
        "static" abililties that boost TrapEvade, and "dynamic"
        statuses that boost or reduce TrapEvade.
        """
        return equipmentTrapEvade + statusTrapEvade + baseTrapEvade
            
    @property
    def equipmentTrapEvade(self):
        """
        The TrapEvade granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentTrapEvade
        
    @equipmentTrapEvade.setter
    def equipmentTrapEvade(self, value):
        """
        int value: should be the total trapEvade given from equipment on
        """
        self._equipmentTrapEvade = value
            
    @property
    def statusTrapEvade(self):
        """
        The TrapEvade gained or lost from the sum of statuses.
        """
        return self._statusTrapEvade
        
    @statusTrapEvade.setter
    def statusTrapEvade(self, value):
        """
        int value: should be the total trapEvade given from statuses.
        """
        self._statusTrapEvade = value
        
    @property
    def baseTrapEvade(self):
        """
        The TrapEvade granted from DEX, CUN and any "static" abilities
        """
        return self._baseTrapEvade
        
    @baseTrapEvade.setter
    def baseTrapEvade(self, value):
        """
        int value: should be DEX + CUN + static Ability Bonus
        """
        self._baseTrapEvade = value 

    @property
    def totalAwareness(self):
        """
        Awareness is determined by CUN, equipment that boosts Awareness,
        "static" abililties that boost Awareness, and "dynamic"
        statuses that boost or reduce Awareness.
        """
        return equipmentAwareness + statusAwareness + baseAwareness
            
    @property
    def equipmentAwareness(self):
        """
        The Awareness granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentAwareness
        
    @equipmentAwareness.setter
    def equipmentAwareness(self, value):
        """
        int value: should be the total awareness given from equipment on
        """
        self._equipmentAwareness = value
            
    @property
    def statusAwareness(self):
        """
        The Awareness gained or lost from the sum of statuses.
        """
        return self._statusAwareness
        
    @statusAwareness.setter
    def statusAwareness(self, value):
        """
        int value: should be the total awareness given from statuses.
        """
        self._statusAwareness = value
        
    @property
    def baseAwareness(self):
        """
        The Awareness granted from CUN and any "static" abilities
        """
        return self._baseAwareness
        
    @baseAwareness.setter
    def baseAwareness(self, value):
        """
        int value: should be CUN + static Ability Bonus
        """
        self._baseAwareness = value         
        
    @property
    def totalDR(self):
        """
        DR is determined by equipment that boosts DR,
        "static" abililties that boost DR, and "dynamic"
        statuses that boost or reduce DR.
        
        Damage Reduction will not be lowered beneath 0%
        in this variable.  
        
        Damage Reduction WILL be raised
        above 80% in this variable if asked to.  It is the
        viewer's repsonsibility to adjust downward after 
        considering any armor penetration.
        """
        return max(0, equipmentDR + statusDR + baseDR)
            
    @property
    def equipmentDR(self):
        """
        The DR granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentDR
        
    @equipmentDR.setter
    def equipmentDR(self, value):
        """
        int value: should be the total DR given from equipment on
        """
        self._equipmentDR = value
            
    @property
    def statusDR(self):
        """
        The DR gained or lost from the sum of statuses.
        """
        return self._statusDR
        
    @statusDR.setter
    def statusDR(self, value):
        """
        int value: should be the total DR given from statuses.
        """
        self._statusDR = value
        
    @property
    def baseDR(self):
        """
        The DR granted from any "static" abilities
        """
        return self._baseDR
        
    @baseDR.setter
    def baseDR(self, value):
        """
        int value: should be only static Ability Bonus
        """
        self._baseDR = value            
        
    @property
    def totalForce(self):
        """
        float -- The total Force multiplier used with Might to determine used might.
        """
        return (statusForce * equipmentForce / 100)
        
    @property
    def equipmentForce(self):
        """
        int -- The primary source for Force.
        """
        return self._equipmentForce
        
    @equipmentForce.setter
    def equipmentForce(self, value):
        """
        Should be an int.  That is, 125% Force = 125 not 1.25
        """
        self._equipmentForce = value
        
    @property
    def statusForce(self):
        """
        The amount Force is modified by an ability.
        """
        return self._statusForce
        
    @statusForce.setter
    def statusForce(self, value):
        """
        Should be an int for the percent.
        """
        self._statusForce = value
        
    @property
    def totalArmorPenetration(self):
        """
        ArmorPenetration is determined by CUN, equipment that boosts ArmorPenetration,
        "static" abililties that boost ArmorPenetration, and "dynamic"
        statuses that boost or reduce ArmorPenetration.
        """
        return equipmentArmorPenetration + statusArmorPenetration + baseArmorPenetration
            
    @property
    def equipmentArmorPenetration(self):
        """
        The ArmorPenetration granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentArmorPenetration
        
    @equipmentArmorPenetration.setter
    def equipmentArmorPenetration(self, value):
        """
        float value: should be the total armorPenetration given from equipment on
        """
        self._equipmentArmorPenetration = value
            
    @property
    def statusArmorPenetration(self):
        """
        The ArmorPenetration gained or lost from the sum of statuses.
        """
        return self._statusArmorPenetration
        
    @statusArmorPenetration.setter
    def statusArmorPenetration(self, value):
        """
        float value: should be the total armorPenetration given from statuses.
        """
        self._statusArmorPenetration = value
        
    @property
    def baseArmorPenetration(self):
        """
        The ArmorPenetration granted from CUN and any "static" abilities
        """
        return self._baseArmorPenetration
        
    @baseArmorPenetration.setter
    def baseArmorPenetration(self, value):
        """
        float value: should be 0.25 * CUN above 10 + static Ability Bonus
        """
        self._baseArmorPenetration = value      
    
    @property
    def totalRangedDodge(self):
        """ Is only the bonus dodge given against ranged attacks.  
        Needs to be manually added to the dodge total."""
        return self._baseRangedDodge + self._equipmentRangedDodge +
               self._statusRangedDodge
               
    @property
    def baseRangedDodge(self):
        return self._baseRangedDodge

    @baseRangedDodge.setter
    def baseRangedDodge(self, value):
        """Should be 0 unless some passive abilities boost it."""
        self._baseRangedDodge = value

    @property
    def equipmentRangedDodge(self):
        return self._equipmentRangedDodge
        
    @eqiupmentRangedDodge.setter
    def equipmentRangedDodge(self, value):
        self._eqiupmentRangedDodge = value
        
    @property
    def statusRangedDodge(self):
        return self._statusRangedDodge
        
    @statusRangedDodge.setter
    def statusRangedDodge(self, value):
        self._statusRangedDodge = value
    
    @property
    def totalRangedForce(self):
        """
        Ranged force is determined primarily by the weapon being used, but
        could also be affected by some special statuses and maybe even passive
        abilities.
        """
        return self._baseRangedForce * (self._equipmentRangedForce / 100) * 
               (1 + self._statusRangedForce)
               
    @property
    def equipmentRangedForce(self):
        """
        The ranged force granted from a ranged weapon equipped.  May also
        be benefitted from a magical property on it.
        """
        return self._equipmentRangedForce
        
    @equipmentRangedForce.setter
    def equipmentRangedForce(self, value):
        """
        int value: should be the percent such that 125% would be 125 etc.
        """
        self._equipmentRangedForce = value
        
    @property
    def statusRangedForce(self):
        return self._statusRangedForce
        
    @statusRangedForce.setter
    def statusRangedForce(self, value):
        self._statusRangedForce = value
        
    @property
    def baseRangedForce(self):
        return self._baseRangedForce
        
    @baseRangedForce.setter
    def baseRangedFroce(self, value):
        """ The default value here should be 100 """
        self._baseRangedForce = value
    
    @property
    def totalSneak(self):
        """
        Sneak is determined by CUN, equipment that boosts Sneak,
        "static" abililties that boost Sneak, and "dynamic"
        statuses that boost or reduce Sneak.
        """
        return equipmentSneak + statusSneak + baseSneak
            
    @property
    def equipmentSneak(self):
        """
        The Sneak granted from any magical equipment currently on.
        Will not automatically update.
        """
        return self._equipmentSneak
        
    @equipmentSneak.setter
    def equipmentSneak(self, value):
        """
        int value: should be the total sneak given from equipment on
        """
        self._equipmentSneak = value
            
    @property
    def statusSneak(self):
        """
        The Sneak gained or lost from the sum of statuses.
        """
        return self._statusSneak
        
    @statusSneak.setter
    def statusSneak(self, value):
        """
        int value: should be the total sneak given from statuses.
        """
        self._statusSneak = value
        
    @property
    def baseSneak(self):
        """
        The Sneak granted from CUN and any "static" abilities
        """
        return self._baseSneak
        
    @baseSneak.setter
    def baseSneak(self, value):
        """
        int value: should be CUN beyond 10 + static Ability Bonus
        """
        self._baseSneak = value 

    # Intrinsic Properties
    @property
    def growthType(self):
        """The skill growth type.  One of "Caster", "Hybrid", or "Non-Caster".
        """
        return self._growthType
        
        
    # Elemental Resistances
    
    @property
    def totalArcaneResistance(self):
        """The percent (as an int) of incoming Arcane damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._baseArcaneResistance + self._equipmentArcaneResistance +
               self._statusArcaneResistance
               
    @property
    def baseArcaneResistance(self):
        return self._baseArcaneResistance
        
    @baseArcaneResistance.setter
    def baseArcaneReistance(self, value):
        self._baseArcaneResistance = value
        
    @property
    def equipmentArcaneResistance(self):
        return self._equipmentArcaneResistance
        
    @equipmentArcaneResistance.setter
    def equipmentArcaneResistance(self, value):
        self._equipmentArcaneResistance = value
        
    @property
    def statusArcaneResistance(self):
        return self._statusArcaneResistance
    
    @statusArcaneResistance.setter
    def statusArcaneResistance(self, value):
        return self._statusArcaneResistance
        
    @property
    def totalColdResistance(self):
        """The percent (as an int) of incoming Cold damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._baseColdResistance + self._equipmentColdResistance +
               self._statusColdResistance
               
    @property
    def baseColdResistance(self):
        return self._baseColdResistance
        
    @baseColdResistance.setter
    def baseColdReistance(self, value):
        self._baseColdResistance = value
        
    @property
    def equipmentColdResistance(self):
        return self._equipmentColdResistance
        
    @equipmentColdResistance.setter
    def equipmentColdResistance(self, value):
        self._equipmentColdResistance = value
        
    @property
    def statusColdResistance(self):
        return self._statusColdResistance
    
    @statusColdResistance.setter
    def statusColdResistance(self, value):
        return self._statusColdResistance   
        
    @property
    def totalDivineResistance(self):
        """The percent (as an int) of incoming Divine damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._baseDivineResistance + self._equipmentDivineResistance +
               self._statusDivineResistance
               
    @property
    def baseDivineResistance(self):
        return self._baseDivineResistance
        
    @baseDivineResistance.setter
    def baseDivineReistance(self, value):
        self._baseDivineResistance = value
        
    @property
    def equipmentDivineResistance(self):
        return self._equipmentDivineResistance
        
    @equipmentDivineResistance.setter
    def equipmentDivineResistance(self, value):
        self._equipmentDivineResistance = value
        
    @property
    def statusDivineResistance(self):
        return self._statusDivineResistance
    
    @statusDivineResistance.setter
    def statusDivineResistance(self, value):
        return self._statusDivineResistance   
    
    @property
    def totalElectricResistance(self):
        """The percent (as an int) of incoming Electric damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._baseElectricResistance + self._equipmentElectricResistance +
               self._statusElectricResistance
               
    @property
    def baseElectricResistance(self):
        return self._baseElectricResistance
        
    @baseElectricResistance.setter
    def baseElectricReistance(self, value):
        self._baseElectricResistance = value
        
    @property
    def equipmentElectricResistance(self):
        return self._equipmentElectricResistance
        
    @equipmentElectricResistance.setter
    def equipmentElectricResistance(self, value):
        self._equipmentElectricResistance = value
        
    @property
    def statusElectricResistance(self):
        return self._statusElectricResistance
    
    @statusElectricResistance.setter
    def statusElectricResistance(self, value):
        return self._statusElectricResistance   
    
    @property
    def totalFireResistance(self):
        """The percent (as an int) of incoming Fire damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._baseFireResistance + self._equipmentFireResistance +
               self._statusFireResistance
               
    @property
    def baseFireResistance(self):
        return self._baseFireResistance
        
    @baseFireResistance.setter
    def baseFireReistance(self, value):
        self._baseFireResistance = value
        
    @property
    def equipmentFireResistance(self):
        return self._equipmentFireResistance
        
    @equipmentFireResistance.setter
    def equipmentFireResistance(self, value):
        self._equipmentFireResistance = value
        
    @property
    def statusFireResistance(self):
        return self._statusFireResistance
    
    @statusFireResistance.setter
    def statusFireResistance(self, value):
        return self._statusFireResistance   
    
    @property
    def totalPoisonResistance(self):
        """The percent (as an int) of incoming Poison damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._basePoisonResistance + self._equipmentPoisonResistance +
               self._statusPoisonResistance
               
    @property
    def basePoisonResistance(self):
        return self._basePoisonResistance
        
    @basePoisonResistance.setter
    def basePoisonReistance(self, value):
        self._basePoisonResistance = value
        
    @property
    def equipmentPoisonResistance(self):
        return self._equipmentPoisonResistance
        
    @equipmentPoisonResistance.setter
    def equipmentPoisonResistance(self, value):
        self._equipmentPoisonResistance = value
        
    @property
    def statusPoisonResistance(self):
        return self._statusPoisonResistance
    
    @statusPoisonResistance.setter
    def statusPoisonResistance(self, value):
        return self._statusPoisonResistance   
    
    @property
    def totalShadowResistance(self):
        """The percent (as an int) of incoming Shadow damage that will be ignored.
        May be reduced below zero by certain abilities.  Old game rules may have 
        this listed as a separate 'elemental vulnerability' but those abilities that
        mention such need to be updated/replaced as the distinction is being
        eliminated.
        
        Elemental Resistances above 80% should not have an effect beyond 80% but
        that logic is not encoded here.  Thus values greater than 80 may be 
        returned."""
        return self._baseShadowResistance + self._equipmentShadowResistance +
               self._statusShadowResistance
               
    @property
    def baseShadowResistance(self):
        return self._baseShadowResistance
        
    @baseShadowResistance.setter
    def baseShadowReistance(self, value):
        self._baseShadowResistance = value
        
    @property
    def equipmentShadowResistance(self):
        return self._equipmentShadowResistance
        
    @equipmentShadowResistance.setter
    def equipmentShadowResistance(self, value):
        self._equipmentShadowResistance = value
        
    @property
    def statusShadowResistance(self):
        return self._statusShadowResistance
    
    @statusShadowResistance.setter
    def statusShadowResistance(self, value):
        return self._statusShadowResistance   

    # Elemental Bonus Damages
    
    @property
    def totalArcaneBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Arcane attacks."""
        return self._baseArcaneBonusDamage +
               self._eqiupmentArcaneBonusDamage +
               self._statusArcaneBonusDamage
    
    @property
    def baseArcaneBonusDamage(self):
        return self._baseArcaneBonusDamage
        
    @baseArcaneBonusDamage.setter
    def baseArcaneBonusDamage(self, value):
        self._baseArcaneBonusDamage = value
        
    @property
    def equipmentArcaneBonusDamage(self):
        return self._equipmentArcaneBonusDamage
        
    @equipmentArcaneBonusDamage.setter
    def equipmentArcaneBonusDamage(self, value):
        self._equipmentArcaneBonusDamage = value
        
    @property
    def statusArcaneBonusDamage(self):
        return self._statusArcaneBonusDamage
        
    @statusArcaneBonusDamage.setter
    def statusArcaneBonusDamage(self, value):
        self._statusArcaneBonusDamage = value
        
    @property
    def totalColdBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Cold attacks."""
        return self._baseColdBonusDamage +
               self._eqiupmentColdBonusDamage +
               self._statusColdBonusDamage
    
    @property
    def baseColdBonusDamage(self):
        return self._baseColdBonusDamage
        
    @baseColdBonusDamage.setter
    def baseColdBonusDamage(self, value):
        self._baseColdBonusDamage = value
        
    @property
    def equipmentColdBonusDamage(self):
        return self._equipmentColdBonusDamage
        
    @equipmentColdBonusDamage.setter
    def equipmentColdBonusDamage(self, value):
        self._equipmentColdBonusDamage = value
        
    @property
    def statusColdBonusDamage(self):
        return self._statusColdBonusDamage
        
    @statusColdBonusDamage.setter
    def statusColdBonusDamage(self, value):
        self._statusColdBonusDamage = value
        
    @property
    def totalDivineBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Divine attacks."""
        return self._baseDivineBonusDamage +
               self._eqiupmentDivineBonusDamage +
               self._statusDivineBonusDamage
    
    @property
    def baseDivineBonusDamage(self):
        return self._baseDivineBonusDamage
        
    @baseDivineBonusDamage.setter
    def baseDivineBonusDamage(self, value):
        self._baseDivineBonusDamage = value
        
    @property
    def equipmentDivineBonusDamage(self):
        return self._equipmentDivineBonusDamage
        
    @equipmentDivineBonusDamage.setter
    def equipmentDivineBonusDamage(self, value):
        self._equipmentDivineBonusDamage = value
        
    @property
    def statusDivineBonusDamage(self):
        return self._statusDivineBonusDamage
        
    @statusDivineBonusDamage.setter
    def statusDivineBonusDamage(self, value):
        self._statusDivineBonusDamage = value

    @property
    def totalElectricBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Electric attacks."""
        return self._baseElectricBonusDamage +
               self._eqiupmentElectricBonusDamage +
               self._statusElectricBonusDamage
    
    @property
    def baseElectricBonusDamage(self):
        return self._baseElectricBonusDamage
        
    @baseElectricBonusDamage.setter
    def baseElectricBonusDamage(self, value):
        self._baseElectricBonusDamage = value
        
    @property
    def equipmentElectricBonusDamage(self):
        return self._equipmentElectricBonusDamage
        
    @equipmentElectricBonusDamage.setter
    def equipmentElectricBonusDamage(self, value):
        self._equipmentElectricBonusDamage = value
        
    @property
    def statusElectricBonusDamage(self):
        return self._statusElectricBonusDamage
        
    @statusElectricBonusDamage.setter
    def statusElectricBonusDamage(self, value):
        self._statusElectricBonusDamage = value
        
    @property
    def totalFireBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Fire attacks."""
        return self._baseFireBonusDamage +
               self._eqiupmentFireBonusDamage +
               self._statusFireBonusDamage
    
    @property
    def baseFireBonusDamage(self):
        return self._baseFireBonusDamage
        
    @baseFireBonusDamage.setter
    def baseFireBonusDamage(self, value):
        self._baseFireBonusDamage = value
        
    @property
    def equipmentFireBonusDamage(self):
        return self._equipmentFireBonusDamage
        
    @equipmentFireBonusDamage.setter
    def equipmentFireBonusDamage(self, value):
        self._equipmentFireBonusDamage = value
        
    @property
    def statusFireBonusDamage(self):
        return self._statusFireBonusDamage
        
    @statusFireBonusDamage.setter
    def statusFireBonusDamage(self, value):
        self._statusFireBonusDamage = value    
   
    @property
    def totalPoisonBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Poison attacks."""
        return self._basePoisonBonusDamage +
               self._eqiupmentPoisonBonusDamage +
               self._statusPoisonBonusDamage
    
    @property
    def basePoisonBonusDamage(self):
        return self._basePoisonBonusDamage
        
    @basePoisonBonusDamage.setter
    def basePoisonBonusDamage(self, value):
        self._basePoisonBonusDamage = value
        
    @property
    def equipmentPoisonBonusDamage(self):
        return self._equipmentPoisonBonusDamage
        
    @equipmentPoisonBonusDamage.setter
    def equipmentPoisonBonusDamage(self, value):
        self._equipmentPoisonBonusDamage = value
        
    @property
    def statusPoisonBonusDamage(self):
        return self._statusPoisonBonusDamage
        
    @statusPoisonBonusDamage.setter
    def statusPoisonBonusDamage(self, value):
        self._statusPoisonBonusDamage = value
        
    @property
    def totalShadowBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Shadow attacks."""
        return self._baseShadowBonusDamage +
               self._eqiupmentShadowBonusDamage +
               self._statusShadowBonusDamage
    
    @property
    def baseShadowBonusDamage(self):
        return self._baseShadowBonusDamage
        
    @baseShadowBonusDamage.setter
    def baseShadowBonusDamage(self, value):
        self._baseShadowBonusDamage = value
        
    @property
    def equipmentShadowBonusDamage(self):
        return self._equipmentShadowBonusDamage
        
    @equipmentShadowBonusDamage.setter
    def equipmentShadowBonusDamage(self, value):
        self._equipmentShadowBonusDamage = value
        
    @property
    def statusShadowBonusDamage(self):
        return self._statusShadowBonusDamage
        
    @statusShadowBonusDamage.setter
    def statusShadowBonusDamage(self, value):
        self._statusShadowBonusDamage = value
        
    # Class specific and miscellaneous
    
    @property
    def totalAvoidanceChance(self):
        """The chance to avoid (not dodge) an attack
        usually due to stealth/concealment."""
        return self._avoidanceChance
        
    @property
    def avoidanceChance(self):
        """The chance to avoid (not dodge) an attack
        usually due to stealth/concealment."""
        return self._avoidanceChance
        
    @avoidanceChance.setter
    def avoidanceChance(self, value):
        """Should be a non-negative int."""
        if value >= 0:
            self._avoidanceChance = value

    @property
    def arcaneArcherManaRegenBase(self):
        return self._arcaneArcherManaRegenBase
    
    @arcaneArcherManaRegenBase.setter
    def arcaneArcherManaRegenBase(self, value):
        self._arcaneArcherManaRegenBase = value
        
    @property
    def arcaneArcherManaRegenHigh(self):
        return self._arcaneArcherManaRegenHigh
    
    @arcaneArcherManaRegenHigh.setter
    def arcaneArcherManaRegenHigh(self, value):
        self._arcaneArcherManaRegenHigh = value
        
    @property
    def arcaneArcherManaRegenLow(self):
        return self._arcaneArcherManaRegenLow
    
    @arcaneArcherManaRegenLow.setter
    def arcaneArcherManaRegenLow(self, value):
        self._arcaneArcherManaRegenLow = value

    @property
    def HPBufferList(self):
        """The list of any HP buffers that should absorb damage before
        continuing on to lower the person's actual HP.
        
        The format for an HPBuffer element is: ['bufferName', '100', '4']
        Where the name of this buff is bufferName, 
        the amount of HP to absorb is 100,
        and the turns left is 4.
        """
        return self._HPBufferList
        
    @HPBufferList.setter
    def HPBufferList(self, value):
        self._HPBufferList = value
    
    @property
    def totalMovementAPCost(self):
        """The AP cost to move up to the number of tiles listed
        in the movementTiles variable.  This can never be
        reduced below 0.
        
        This variable uses the combination of the three typical
        components: base, equipment, and status, but it also
        checks to see if the override value is not -1.  When it
        is a valid value, that value will be returned instead."""
        if self._overrideMovementAPCost >= 0:
            return self._overrideMovementAPCost
        else:
            return max(self._baseMovementAPCost + 
                       self._equipmentMovementAPCost +
                       self._statusMovementAPCost, 0)
    
    @property
    def baseMovementAPCost(self):
        return self._baseMovementAPCost
        
    @baseMovementAPCost.setter
    def baseMovementAPCost(self, value):
        self._baseMovementAPCost = value
        
    @property
    def equipmentMovementAPCost(self):
        return self._eqiupmentMovementAPCost
        
    @equipmentMovementAPCost.setter
    def equipmentMovementAPCost(self, value):
        self._equipmentMovementAPCost = value
        
    @property
    def overrideMovementAPCost(self):
        return self._overrideMovementAPCost
        
    @overrideMovementAPCost.setter
    def overrideMovementAPCost(self, value):
        """A negative value is used to indicate that this value should be
        ignored. If a negative value is assigned, it will always be 
        set to exactly -1."""
        if value < 0:
            value = -1
        self._overrideMovementAPCost = value
        
    @property
    def statusMovementAPCost(self):
        return self._statusMovementAPCost
        
    @statusMovementAPCost.setter
    def statusMovementAPCost(self, value):
        self._statusMovementAPCost = value
        
    @property
    def totalMeleeAttackAPCost(self):
        """Is comprised only of the value given at character creation.
        This public access is given only to avoid inconsistency with the
        way other variables are accessed."""
        return self._totalMeleeAttackAPCost
        
    @property
    def baseMeleeAttackAPCost(self):
        """Should never be modified after character creation."""
        return self._baseMeleeAttackAPCost
        
    @baseMeleeAttackAPCost.setter
    def baseMeleeAttackAPCost(self, value):
        """Should never be modified after character creation."""
        self._baseMeleeAttackAPCost = value
        
    @property
    def ninjaStyle(self):
        """The Style this Ninja is currently using.  If this playercharacter
        is not a Ninja, it should always be None."""
        return self._ninjaStyle
        
    @ninjaStyle.setter
    def ninjaStyle(self, value):
        """The Style this Ninja is currently using.  If this playercharacter
        is not a Ninja, it should always be None."""
        if self.characterClass != "Ninja":
            return
        elif value in ["Tiger", "Panther", "Snake", "Crane", "Dragon"]:
            self._ninjaStyle = value
        
    @property
    def totalRangedAttackAPCost(self):
        """Is comprised only of the value given at character creation.
        This public access is given only to avoid inconsistency with the
        way other variables are accessed."""
        return self._baseRangedAttackAPCost
        
    @property
    def baseRangedAttackAPCost(self):
        """Should never be modified after character creation."""
        return self._baseRangedAttackAPCost
        
    @baseRangedAttackAPCost.setter
    def baseRangedAttackAPCost(self, value):
        """Should never be modified after character creation."""
        self._baseRangedAttackAPCost = value
    
    @property
    def totalSpellFailureChance(self):
       """Is comprised of only the status value, but the accessor pattern
       is preserved for consistency."""
       return self._statusSpellFailureChance
       
    @property
    def statusSpellFailureChance(self):
        """ An int that represents a percent."""
        return self._statusSpellFailureChance
        
    @statusSpellFailureChance.setter
    def statusSpellFailureChance(self, value):
        self._statusSpellFailureChance = value
    
    # Methods
    
    def lowerElementalResistance(elementName, magnitude):
        elementName = elementName.strip().capitalize()
        if elementName == "Fire":
            self.statusFireResistance -= magnitude
        elif elementName == "Cold":
            self.statusColdResistance -= magnitude
        elif elementName == "Electric":
            self.statusElectricResistance -= magnitude
        elif elementName == "Poison":
            self.statusPoisonResistance -= magnitude
        elif elementName == "Divine":
            self.statusDivineResistance -= magnitude
        elif elementName == "Shadow":
            self.statusShadowResistance -= magnitude
        elif elementName == "Arcane":
            self.statusArcaneResistance -= magnitude
        elif:
            if elementName in ['Bludgeoning', 'Piercing', 'Slashing']:
                raise TypeError("Physical type: " + elementName + " is not allowed in this method.")
            else:
                raise TypeError("Unkown Element used: " + elementName + " .")
        
    def raiseElementalResistance(elementName, magnitude):
        elementName = elementName.strip().capitalize()
        if elementName == "Fire":
            self.statusFireResistance += magnitude
        elif elementName == "Cold":
            self.statusColdResistance += magnitude
        elif elementName == "Electric":
            self.statusElectricResistance += magnitude
        elif elementName == "Poison":
            self.statusPoisonResistance += magnitude
        elif elementName == "Divine":
            self.statusDivineResistance += magnitude
        elif elementName == "Shadow":
            self.statusShadowResistance += magnitude
        elif elementName == "Arcane":
            self.statusArcaneResistance += magnitude
        elif:
            if elementName in ['Bludgeoning', 'Piercing', 'Slashing']:
                raise TypeError("Physical type: " + elementName + " is not allowed in this method.")
            else:
                raise TypeError("Unkown Element used: " + elementName + " .")        
            
    def applyHPBuffer(self, bufferName, HPMagnitude, turnsToLive):
        """Adds a new HPBuffer to the character, or refreshes an existing one with the same name.
        Inputs:
          bufferName -- string; The name of the status that granted this buffer.
          HPMagnitude -- int > 0; The amount of HP this buffer should be able to absorb.
          turnsToLive -- int > 0;The number of turns this buffer should stay active.
        Outputs:
          None"""
        if HPMagnitude <=0 or turnsToLive <=0:
            return
            
        oldBuffer = None
        for buff in self.HPBufferList:
            if buff[0] == bufferName:
                oldBuffer = buff
        if oldBuffer:
            oldBuffer[1] = HPMagnitude
            oldBuffer[2] += turnsToLive
        else:
            self.HPBuffer.append([bufferName, HPMagnitude, turnsToLive])
            
    def unapplyHPBuffer(self, bufferName, turnsToLive):
        """Removes an existing HPBuffer from the list or reduces the time left to live
        on a buffer that was placed by multiple identically named abiliites.
        Inputs:
          bufferName -- string; the name of the status that granted this buffer.
          turnsToLive -- int > 0; the number of turns the buffer originally had to live.
        Outputs:
          None"""
        if turnsToLive <= 0:
            return
        for buff in self.HPBufferList:
            if buff[0] == bufferName:
                buff[2] -= turnsToLive
                if buff[2] <= 0:
                    self.HPBufferList.remove(buff)
        
        
        
        
                        
         