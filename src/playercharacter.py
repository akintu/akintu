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
       
       self._baseForce = None # Default is 100 (no percent modified)
       self._equipmentForce = None # Will be a percent as an int
       self._statusForce = None # Also an int "percent"
       
       # TODO: Force g/s
       
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
       
       # TODO: getter/setter movementTiles
       
       self._baseOverallDamageBonus = None # default 0%
       self._equipmentOverallDamageBonus = None # Typically/always 0?
       self._statusOverallDamageBonus = None
       
       # TODO: getter/setter overallDamageBonus
       
       self._basePoisonRatingBonus = None
       self._equipmentPoisonRatingBonus = None
       self._statusPoisonRatingBonus = None
       
       # TODO: Getters/setters for poisonratingbonus
       
       self._basePoisonTolerance = None
       self._equipmentPoisonTolerance = None
       self._statusPoisonTolerance = None      
       
       self._basePotionEffect = None # default = 100% before Sorc.
       self._equipmentPotionEffect = None
       self._statusPotionEffect = None
       
       # TODO: getter/setter for potionEffect
       
       self._baseRangedAccuracy = None
       self._equipmentRangedAccuracy = None
       self._statusRangedAccuracy = None
       
       self._baseRangedCriticalMagnitude = None
       self._equipmentRangedCriticalMagnitude = None
       self._statusRangedCriticalMagnitude = None
       
       self._baseRangedDodge = None
       self._equipmentRangedDodge = None
       self._statusRangedDodge = None     

       self._baseRangedForce = None # Default is 100 (no percent modified)
       self._equipmentRangedForce = None # Will be a percent as an int
       self._statusRangedForce = None # Also an int "percent"      
       
       # TODO; G/s for ranged force
       # TODO: Getters/setters for ranged dodge
       
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
       
       # TODO: All elemental resistance setters/getters
       # TODO: Write method lowerElementalResistance(element, magnitude)
       # TODO: Write method raiseElementalResistance(element, magnitude)
       
       # TODO: Write method applyHPBuffer(magnitude)
       # TODO: Movement AP cost, melee attack AP cost, ranged attack AP cost, movementAPOverride default -1
       # TODO: spellFailureChance default = 0
       # TODO: Write method applyOnHitMod(name, *args)
       # TODO: Write method removeOnHitMod(name)
       
       # Intrinsic properties (read-only)
       self._growthType = None 
       self._characterClass = None
       
       # Class specific properties and weird things:
       # self._ninjaStyle
       # self._activeSummon
       # self._arcaneArcherManaRegenBase
       # self._arcaneArcherManaRegenHigh
       # self._arcaneArcherManaRegenLow
       # self._avoidanceChance
       # self._abilityAPModsList [["AbilityName", -2], [...]]
       # self._spellMPModsList [["SpellName", -1], [...]]
       # self._empathyToSummon 
       # self._stealthBreakMaxOverride Default 100
       # self._HPBufferList format: [['name', 50 ], ...] ?
       
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
        
    
        
        
        
    
        
    
