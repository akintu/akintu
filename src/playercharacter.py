#!/usr/bin/python

import sys
from person import *

class PlayerCharacter(object):
    def __init__(self):  
         
        self._baseOverallDamageBonus = None
        self._equipmentOverallDamageBonus = None
        self._statusOverallDamageBonus = None
         
        self._basePoisonRatingBonus = None
        self._equipmentPoisonRatingBonus = None
        self._statusPoisonRatingBonus = None      
         
        self._basePotionEffect = None
        self._equipmentPotionEffect = None
        self._statusPotionEffect = None

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
         
        # Intrinsic properties
         
        self.growthType = None 
        self.characterClass = None
        self.baseClass = None
        self.secondaryClass = None
        self.armorTolerance = None
         
        # Class specific properties and weird things:
         
        self._arcaneArcherManaRegenLow = None
        self._arcaneArcherManaRegenHigh = None
        self._arcaneArcherManaRegenBase = None
         
        self._ninjaStyle = None

        self.DROutside = None
         
        # self._activeSummon
        # self._abilityAPModsList [["AbilityName", -2], [...]]
        # self._spellMPModsList [["SpellName", -1], [...]]
        # self._empathyToSummon 
        # self._stealthBreakMaxOverride Default 100
        
        # Levelup stats
        self.levelupStrength = None
        self.levelupCunning = None
        self.levelupSorcery = None
        self.levelupPiety = None
        self.levelupConstitution = None
        self.levelupHP = None
        self.levelupMP = None
        self.skillLevels = None
        self.spellLevels = None
        
        # Just includes the name
        self.spellList = []
        self.abilityList = []
        
        # Trait list of form, [["Bully", 3], ["Courage", 2]...] where the int is the rank.
        self.traitList = []
        
    # Resources (AP, MP, HP)
    
    
    
    
       
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
        return self._statusOverallDamageBonus
        
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
        return (self._basePotionEffect + self._equipmentPotionEffect +
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
        
    
        
        
        
        
                        
         