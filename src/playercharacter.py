#!/usr/bin/python

import sys
import equippeditems
import equipment
import person as p
import spell
import passiveability
import ability
import inventory

class PlayerCharacter(p.Person):

    expRequiredForLevel = {1 : 100, 2 : 250, 3 : 500, 4 : 900, 5 : 1700}
    demoExpRequiredForLevel = {1 : 10, 2 : 25, 3 : 50, 4 : 90, 5 : 170}
    LEVEL_MAX = 5
    
    def __init__(self, argDict):  
        p.Person.__init__(self, argDict)
        
        self.team = "Players"
        
        self.level = 1
        self._experience = 0
        
        self.goldFind = p.Person.setFrom(argDict, 'startingGoldFind', 0)
        
        self._baseOverallDamageBonus = p.Person.setFrom(argDict, 'startingOverallDamageBonus', 0)
        self._equipmentOverallDamageBonus = 0
        self._statusOverallDamageBonus = 0
         
        self._basePoisonRatingBonus = p.Person.setFrom(argDict, 'startingPoisonRatingBonus', 0)
        self._equipmentPoisonRatingBonus = 0
        self._statusPoisonRatingBonus = 0    
         
        self._basePotionEffect = p.Person.setFrom(argDict, 'startingPotionEffect', 0)
        self._equipmentPotionEffect = 0
        self._statusPotionEffect = 0

        self._baseJewleryEffect = p.Person.setFrom(argDict, 'startingJewleryEffect', 0)
        
        # Elemental Bonus Damages
        
        self._baseArcaneBonusDamage = p.Person.setFrom(argDict, 'startingArcaneBonusDamage', 0)
        self._equipmentArcaneBonusDamage = 0
        self._statusArcaneBonusDamage = 0
        
        self._baseColdBonusDamage = p.Person.setFrom(argDict, 'startingColdBonusDamage', 0)
        self._equipmentColdBonusDamage = 0
        self._statusColdBonusDamage = 0
        
        self._baseDivineBonusDamage = p.Person.setFrom(argDict, 'startingDivineBonusDamage', 0)
        self._equipmentDivineBonusDamage = 0
        self._statusDivineBonusDamage = 0
        
        self._baseElectricBonusDamage = p.Person.setFrom(argDict, 'startingElectricBonusDamage', 0)
        self._equipmentElectricBonusDamage = 0
        self._statusElectricBonusDamage = 0
        
        self._baseFireBonusDamage = p.Person.setFrom(argDict, 'startingFireBonusDamage', 0)
        self._equipmentFireBonusDamage = 0
        self._statusFireBonusDamage = 0
        
        self._basePoisonBonusDamage = p.Person.setFrom(argDict, 'startingPoisonBonusDamage', 0)
        self._equipmentPoisonBonusDamage = 0
        self._statusPoisonBonusDamage = 0
        
        self._baseShadowBonusDamage = p.Person.setFrom(argDict, 'startingShadowBonusDamage', 0)
        self._equipmentShadowBonusDamage = 0
        self._statusShadowBonusDamage = 0
         
        # Spell School Resists
        self.baneResist = p.Person.setFrom(argDict, 'startingBaneResist', 0)
        self.enchantmentResist = p.Person.setFrom(argDict, 'startingEnchantmentResist', 0)
        self.mentalResist = p.Person.setFrom(argDict, 'startingMentalResist', 0)
        self.mysticResist = p.Person.setFrom(argDict, 'startingMysticResist', 0)
        self.naturalResist = p.Person.setFrom(argDict, 'startingNaturalResist', 0)
        self.primalResist = p.Person.setFrom(argDict, 'startingPrimalResist', 0)
        self.illusionResist = p.Person.setFrom(argDict, 'startingIllusionResist', 0)
                       
        self.onHitEffects = []
         
        # Intrinsic properties
         
        self._growthType = p.Person.setFrom(argDict, 'skillGrowth', p.Person.ERROR) 
        
        title = p.Person.setFrom(argDict, 'name', p.Person.ERROR)
        self.race = title.split(' ', 1)[0]
        self.characterClass = title.split(' ', 1)[1]
        
        self.baseClass = p.Person.setFrom(argDict, 'baseCC', p.Person.ERROR)
        self.secondaryClass = p.Person.setFrom(argDict, 'secondaryCC', p.Person.ERROR)
        self.armorTolerance = p.Person.setFrom(argDict, 'armorTolerance', p.Person.ERROR)
        
        # Class specific properties and weird things:
        
        # --- Arcane Archer ---
        self._arcaneArcherManaRegenLow = None
        self._arcaneArcherManaRegenHigh = None
        self._arcaneArcherManaRegenBase = None
        if (self.characterClass == "Arcane Archer"):
            self._arcaneArcherManaRegenLow = 4
            self._arcaneArcherManaRegenBase = 6
            self._arcaneArcherManaRegenHigh = 7
        self.arcaneArcherManaRegenFactor = 1
        
        # --- Marksman ---
        self._bonusRange = 0
        self.longbowAccuracyPenaltyReduction = 0
        
        # --- Ninja ---
        # The starting (default?) style for Ninjas is the 'Tiger' style.
        self._ninjaStyle = None
        if (self.characterClass == "Ninja"):
            self._ninjaStyle = "Tiger" # TODO: Apply Tiger passives on startup.
        
        # --- Kahajit Race ---
        # Worry about whether we are 'outside' or not in the Combat class, perhaps? TODO
        self.DROutside = None
        
        # --- Ranger classes ---
        self._bonusTrapDamage = 0
        self._bonusTrapRating = 0
        self.bonusPoisonRating = 0
        self.meleeRangedAttackPenaltyReduction = 0
        
        # --- Sorceror ---
        # self._activeSummon
        # self._empathyToSummon 
        
        # --- Other ---
        # self._abilityAPModsList [["AbilityName", -2], [...]] I don't think we need these...
        # self._spellMPModsList [["SpellName", -1], [...]]
        self.knockbackResistance = 0 # Amount above 100 is treated as 100.
        self._equipmentIdentification = 0
        self._statusIdentification = 0
        self._equipmentShopBonus = 0
        
        # --- Thief classes ---
        # self._stealthBreakMaxOverride Default 100
        self.trapDisarmBonus = 0
        
        # --- Weaponmaster ---
        self.weaponAttackArc = 0
          # Possible Values = 30, 90, 180, 270, 360
        
        # --- Wizard classes ---
        self.healingBonus = 0
        
        # include starting equipment in this initializer. TODO
        self.equippedItems = equippeditems.EquippedItems(None)
        self._baseInventoryCapacity = p.Person.setFrom(argDict, 'startingInventoryCapacity', 0)
        self._equipmentCarryingCapacity = 0
        self.inventory = inventory.Inventory()
        
        # Levelup stats
        self.levelupStrength = p.Person.setFrom(argDict, 'levelupStrength', p.Person.ERROR)
        self.levelupCunning = p.Person.setFrom(argDict, 'levelupCunning', p.Person.ERROR)
        self.levelupSorcery = p.Person.setFrom(argDict, 'levelupSorcery', p.Person.ERROR)
        self.levelupPiety = p.Person.setFrom(argDict, 'levelupPiety', p.Person.ERROR)
        self.levelupConstitution = p.Person.setFrom(argDict, 'levelupConstitution', p.Person.ERROR)
        self.levelupHP = p.Person.setFrom(argDict, 'levelupHP', p.Person.ERROR)
        self.levelupMP = p.Person.setFrom(argDict, 'levelupMP', p.Person.ERROR)
       
        self.skillLevels = None
        self.spellLevels = None
        if self.growthType == "Caster":
            self.skillLevels = [1, 4, 8, 12, 16, 20]
            self.spellLevels = {1 : 3, 2 : 1,
                                3 : 2, 4 : 1,
                                5 : 2, 6 : 1,
                                7 : 2, 8 : 1, 
                                9 : 2, 10 : 1,
                                11 : 2, 12 : 1,
                                13 : 2, 14 : 1,
                                15 : 2, 16 : 1,
                                17 : 2, 18 : 1,
                                19 : 2, 20 :1}
        elif self.growthType == "Hybrid":
            self.skillLevels = [1, 3, 6, 9, 12, 15, 18, 20]
            self.spellLevels = {1 : 1, 2 : 1, 3 : 1, 4 : 1, 5 : 1,
                                6 : 1, 7 : 1, 8 : 1, 9 : 1, 10 : 1,
                                11 : 1, 12 : 1, 13 : 1, 14 : 1, 
                                15 : 1, 16 : 1, 17 : 1, 18 : 1,
                                19 : 1, 20 : 1}
        elif self.growthType == "Non-Caster":
            self.skillLevels = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
            self.spellLevels = {}
        
        self.spellList = []
        
        spellOneName = p.Person.setFrom(argDict, 'spellOne', None)
        if spellOneName:
            spellOne = spell.Spell(spellOneName, self)
            self.spellList.append(spellOne)
            
        spellTwoName = p.Person.setFrom(argDict, 'spellTwo', None)
        if spellTwoName:
            spellTwo = spell.Spell(spellTwoName, self)
            self.spellList.append(spellTwo)
            
        spellThreeName = p.Person.setFrom(argDict, 'spellThree', None)
        if spellThreeName:
            spellThree = spell.Spell(spellThreeName, self)
            self.spellList.append(spellThree)
        
        self.abilities = []
        for abil in ability.Ability.allAbilities:
            current = ability.Ability.allAbilities[abil]
            if current['class'] == self.baseClass or current['class'] == self.secondaryClass or current['class'] == self.characterClass:
                if current['level'] == 1:
                    newAbil = ability.Ability(abil, self)
                    self.abilities.append(newAbil)
                
        self.passiveAbilities = []
        for pAbil in passiveability.PassiveAbility.allContentByName:
            current = passiveability.PassiveAbility.allContentByName[pAbil]
            if current['class'] == self.baseClass or current['class'] == self.secondaryClass or current['class'] == self.characterClass:       
                if current['level'] == 1:
                    newPAbil = passiveability.PassiveAbility(pAbil, self)
                    self.passiveAbilities.append(newPAbil)
        
        self.traits = []
        
        self.listeners = []
        
        self.attacksPerformed = [0,0] 
        # TODO: Need to update attacksPerformed each turn.  The previous turn's number of attacks is in position 0, this turn's
        # in position 1.  Need to also shift those at the end of each turn...        
    
    def gainLevelUp(self):
        """Start the levelup process for acquiring a new level.  May need to
        be integrated with another UI class to make decisions later TODO.
        Inputs:
            None
        Outputs:
            None"""
        # Gain stats
        self._baseStrength += self.levelupStrength 
        self._baseCunning += self.levelupCunning
        self._baseSorcery += self.levelupSorcery
        self._basePiety += self.levelupPiety
        self._baseConstitution += self.levelupConstitution
        self._baseHP += self.levelupHP
        self._baseMP += self.levelupMP
        
        # Select/Gain Trait: TODO
        
        self.abilities = []
        for abil in ability.Ability.allAbilities:
            current = ability.Ability.allAbilities[abil]
            if current['class'] == self.characterClass:
                if current['level'] == self.level:
                    newAbil = ability.Ability(abil, self)
                    self.abilities.append(newAbil)
                    
        # Select/Gain Skill: TODO
        # Select/Gain Spell(s): TODO
        # TODO: Check to see if we need to alter the MP/AP cost of learned spells based on traits!
    
    @property
    def experience(self):
        return self._experience
        
    def addExperience(self, amount):
        """" Adds the given amount of experience to the character.
        If the character is at the max level, this will not increase the 
        experience of the character.
        This method will return the new current level of the player. 
        The experience added will never be enough to cause more than one level up.
        In the event that enough experience is given to cause multiple levelups, the
        experience gain will be capped at one point shy of the *next* level.
        Inputs:
            amount -- int > 0; how much exp is gained.
        Outputs:
            int; new current level of playercharacter"""
        if amount <= 0 or self.level == PlayerCharacter.LEVEL_MAX:
            return self.level
        if self.level == PlayerCharacter.LEVEL_MAX - 1:
            expForNext = PlayerCharacter.expRequiredForLevel[self.level + 1]
            self._experience += amount
            if self._experience >= expForNext:
                self._experience = expForNext
                self.level += 1
            return self.level
        else:
            expForNext = PlayerCharacter.expRequiredForLevel[self.level + 1]
            expForSecondNext = PlayerCharacter.expRequiredForLevel[self.level + 2]
            self._experience += amount
            if self._experience >= expForSecondNext:
                self._experience = expForSecondNext - 1
            if self._experience >= expForNext:
                self.level += 1
            return self.level                
        #TODO: Demo mode
    
    @property
    def totalOverallDamageBonus(self):
        """ Should be 0 for 0% by default.
            Would be 14 for 14% (not 1.14)
        """
        return (self._baseOverallDamageBonus + self._equipmentOverallDamageBonus +
               self._statusOverallDamageBonus)
               
    @property
    def baseOverallDamageBonus(self):
        """ Should almost always be 0 for 0%."""
        return self._baseOverallDamageBonus
        
    @baseOverallDamageBonus.setter
    def baseOverallDamageBonus(self, value):
        """ Set to ints not floats."""
        self._baseOverallDamageBonus = value
        
    @property
    def equipmentOverallDamageBonus(self):
        return self._equipmentOverallDamageBonus
        
    @equipmentOverallDamageBonus.setter
    def equipmentOverallDamageBonus(self, value):
        self._equipmentOverallDamageBonus = value
        
    @property
    def statusOverallDamageBonus(self):
        return self._statusOverallDamageBonus
        
    @statusOverallDamageBonus.setter
    def statusOverallDamageBonus(self, value):
        self._statusOverallDamageBonus = value
        
    @property
    def totalPoisonRatingBonus(self):
        """ The bonus applied to any applied poison, or any ability
        that has a poison effect that uses the poison rating roll 
        (which is almost all of them other than weapon elemental damage.)
        """
        return (self._basePoisonRatingBonus + self.equipmentPoisonRatingBonus +
               self._statusPoisonRatingBonus)
    
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
    def totalPotionEffect(self):
        """
        An int representing how much healing and mana potions are
        augmented.  Starts at 100 but is increased by many possible
        factors, especially Sorcery."""
        return (max(0, (self.totalSorcery - 10) * 5) +
                self._basePotionEffect + 
                self._equipmentPotionEffect +
                self._statusPotionEffect)
    
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
    def totalJewleryEffect(self):
        return (100 +
                max(0, (self.totalSorcery - 10)) * 5 +
                self._baseJewleryEffect)

    @property
    def baseJewleryEffect(self):
        return self._baseJewleryEffect

    @baseJewleryEffect.setter
    def baseJewleryEffect(self, value):
        self._baseJewleryEffect = value    
        
    # Intrinsic Properties
    @property
    def growthType(self):
        """The skill growth type.  One of "Caster", "Hybrid", or "Non-Caster".
        """
        return self._growthType
        
    # Elemental Bonus Damages
    
    @property
    def totalArcaneBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Arcane attacks."""
        return (self._baseArcaneBonusDamage +
               self._eqiupmentArcaneBonusDamage +
               self._statusArcaneBonusDamage)
    
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
        return (self._baseColdBonusDamage +
               self._eqiupmentColdBonusDamage +
               self._statusColdBonusDamage)
    
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
        return (self._baseDivineBonusDamage +
               self._eqiupmentDivineBonusDamage +
               self._statusDivineBonusDamage)
    
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
        return (self._baseElectricBonusDamage +
               self._eqiupmentElectricBonusDamage +
               self._statusElectricBonusDamage)
    
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
        return (self._baseFireBonusDamage +
               self._eqiupmentFireBonusDamage +
               self._statusFireBonusDamage)
    
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
        return (self._basePoisonBonusDamage +
               self._eqiupmentPoisonBonusDamage +
               self._statusPoisonBonusDamage)
    
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
        return (self._baseShadowBonusDamage +
               self._eqiupmentShadowBonusDamage +
               self._statusShadowBonusDamage)
    
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
    def totalIdentification(self):
        return self.totalSorcery + self.equipmentIdentification + self.statusIdentification
        
    @property
    def equipmentIdentification(self):
        return self._equipmentIdentification
        
    @equipmentIdentification.setter
    def equipmentIdentification(self, value):
        self._equipmentIdentification = value
        
    @property
    def statusIdentification(self):
        return self._statusIdentification
        
    @statusIdentification.setter
    def statusIdentification(self, value):
        self._statusIdentification = value
    
    @property
    def lockpicking(self):
        if self.baseClass == "Thief":
            return self.totalCunning
        else:
            return 0
    
    @property
    def tricksterAttackManaRegen(self):
        if self.characterClass == "Trickster":
            if self.usingWeaponStyle("Dual"):
                return 3
            else:
                return 2
        else:
            return 0
    
    @property
    def tricksterDodgeManaRegen(self):
        return self.level * 2 + 18
        
    @property
    def bonusRange(self):
        return self._bonusRange
        
    @bonusRange.setter
    def bonusRange(self, value):
        self._bonusRange = value
        
    @property
    def bonusTrapDamage(self):
        return self._bonusTrapDamage
        
    @bonusTrapDamage.setter
    def bonusTrapDamage(self, value):
        self._bonusTrapDamage = value
    
    @property
    def bonusTrapRating(self):
        return self._bonusTrapRating
        
    @bonusTrapRating.setter
    def bonusTrapRating(self, value):
        self._bonusTrapRating = value
        
    def isClass(self, className):
        """Returns True if this character is the characterClass provided
        or has the base class provided as its primary base class."""
        return self.characterClass == className or self.baseClass == className
        
    def hasSummon(self):
        """Returns True if this Person is a Sorcerer and has a
        Guardian active.
        Inputs:
          self
        Outputs:
          True or False"""
        if self.isClass("Sorcerer") and self.minionList:
            return True
        return False

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
    def inventoryWeight(self):
        """How much all of the inventory items weigh, in pounds."""
        pass
        # TODO
        
    @property
    def inventoryCapacity(self):
        """How much the player can fit in his inventory."""
        # TODO: Worry about how +Strength and +Capacity gear could allow you to carry more than your capacity.
        if self.totalStrength <= 15:
            return 8 * self.totalStrength + self._baseInventoryCapacity + self._equipmentCarryingCapacity
        else:
            return 120 + (self.totalStrength - 15) * 12 + self._baseInventoryCapacity + self._equipmentCarryingCapacity
    
    @property
    def equipmentCarryingCapacity(self):
        return self._equipmentCarryingCapacity
        
    @equipmentCarryingCapacity.setter
    def equipmentCarryingCapacity(self, value):
        self._equipmentCarryingCapacity = value
    
    @property
    def totalShopBonus(self):
        return min(40, max(0, (self.totalCunning - 10) * 0.5 + self.equipmentShopBonus))
        
    @property
    def equipmentShopBonus(self):
        return self._equipmentShopBonus
    
    @equipmentShopBonus.setter
    def equipmentShopBonus(self, value):
        self._equipmentShopBonus = value
    
    @property
    def attackRange(self):
        weapon = self.equippedItems.equippedWeapon
        if not weapon:
            return 1
        if weapon.range > 1:
            return self._bonusRange + weapon.range
        else:
            return weapon.range
            
    @property
    def hasExtraLengthBuffs(self):
        if self.totalSorcery >= 50:
            return True
        return False
    
    def removeOnHitEffect(self, name, count):
        for fx in self.onHitEffects:
            if fx.name.lower() == name.lower() and fx.count == count:
                self.onHitEffects.remove(fx)
                return 
                # Need to return immediately to remove exactly one fx.
    
    def equip(self, newPiece):
        """Equips a piece of gear, and places any replaced gear in the inventory."""
        oldPieces = self.equippedItems.equip(newPiece)
        oldPiece = oldPieces[0]
        oldPiece2 = None
        if len(oldPiece) > 1:
            oldPiece2 = oldPieces[1]
            
        for prop in newPiece.propertyList:
            prop.effect(self)   
        if newPiece.isinstance(equipment.Armor):
            self.equipmentDR += newPiece.DR
            self.equipmentStealth += newPiece.stealthMod
            self.equipmentDodge += newPiece.dodgeMod
        elif newPiece.isisntance(equipment.Weapon):
            pass
            # Weapon stats are viewed on the weapon itself.
            
        if oldPiece:
            for prop in oldPiece.propertyList:
                prop.effect(self, reverse=True)   
            if oldPiece.isinstance(equipment.Armor):
                self.equipmentDR -= oldPiece.DR
                self.equipmentStealth -= oldPiece.stealthMod
                self.equipmentDodge -= oldPiece.dodgeMod
            elif oldPiece.isinstance(equipment.Weapon):
                pass
            self.inventory.allItems.append(oldPiece)
        if oldPiece2:
            for prop in oldPiece2.propertyList:
                prop.effect(self, reverse=True)         
            if oldPiece2.isinstance(equipment.Armor):
                self.equipmentDR -= oldPiece2.DR
                self.equipmentStealth -= oldPiece2.stealthMod
                self.equipmentDodge -= oldPiece2.dodgeMod
            elif oldPiece2.isinstance(equipment.Weapon):
                pass
            self.inventory.allItems.append(oldPiece2)        
        # TODO: Check to see if weight capacity has changed?

    
    
    
    
         