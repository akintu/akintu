#!/usr/bin/python

import sys
import entity as en
from network import *
from ai import AI

class IncompleteDataInitialization(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Person(en.Entity):

    ERROR = "INITIALIZATION_FAILURE"
    
    @staticmethod
    def setFrom(argDict, variableName, defaultValue):
        if( (variableName not in argDict) or (argDict[variableName] == "None") ):
            if defaultValue == Person.ERROR:
                raise IncompleteDataInitialization( "The parameter: " + variableName + " must be specified, but isn't.")
            else:
                return defaultValue
        else:
            return argDict[variableName]
            
    def __init__(self, argDict):
        loc = Person.setFrom(argDict, 'location', None)
        img = Person.setFrom(argDict, 'image', None)
        
        en.Entity.__init__(self, location=loc, image=img, passable=False)
        
        self.id = None
        self.ai = AI()
        self.anim = None
        self.anim_start = 0

        self._cooldownList = []
        self._statusList = []
        self._minionList = []
        self._owner = None # Move to parent class?
        
        self._title = Person.setFrom(argDict, 'name', Person.ERROR)
        self._size = Person.setFrom(argDict, 'size', 'Medium')

        # Primary Attributes
        self._baseConstitution = Person.setFrom(argDict, 'startingConstitution', 0)
        self._equipmentConstitution = 0
        self._statusConstitution = 0
        
        self._baseCunning = Person.setFrom(argDict, 'startignCunning', 0)
        self._equipmentCunning = 0
        self._statusCunning = 0      
        
        self._baseDexterity = Person.setFrom(argDict, 'startingDexterity', 0)
        self._equipmentDexterity = 0
        self._statusDexterity = 0     

        self._basePiety = Person.setFrom(argDict, 'startingPiety', 0)
        self._equipmentPiety = 0
        self._statusPiety = 0 
         
        self._baseSorcery = Person.setFrom(argDict, 'startingSorcery', 0)
        self._equipmentSorcery = 0
        self._statusSorcery = 0

        self._baseStrength = Person.setFrom(argDict, 'startingStrength', 0)
        self._equipmentStrength = 0
        self._statusStrength = 0
        
        # Resources
        self._AP = Person.setFrom(argDict, 'AP', 20)
        self._baseAP = 20
        self._equipmentAP = 0
        
        self._baseHP = Person.setFrom(argDict, 'startingHP', Person.ERROR)
        self._equipmentHP = 0
        self._HP = self.totalHP
        self.HPRegen = Person.setFrom(argDict, 'HPRegen', 0)
        # TODO: Implement both kinds of regen.
        
        self._baseMP = Person.setFrom(argDict, 'startingMP', 0)
        self._equipmentMP = 0
        self._MP = self.totalMP
        self.MPRegen = Person.setFrom(argDict, 'MPRegen', 0)
        
        self._baseArmorPenetration = Person.setFrom(argDict, 'startingArmorPenetration', 0)
        self._equipmentArmorPenetration = 0
        self._statusArmorPenetration = 0
        
        self._baseAwareness = Person.setFrom(argDict, 'startingAwareness', 0)
        self._equipmentAwareness = 0
        self._statusAwareness = 0
        
        self._baseCriticalChance = Person.setFrom(argDict, 'startingCriticalChance', 0)
        self._equipmentCriticalChance = 0
        self._statusCriticalChance = 0
        
        self._baseCriticalMagnitude = Person.setFrom(argDict, 'startingCriticalMagnitude', 0)
        self._equipmentCriticalMagnitude = 0
        self._statusCriticalMagnitude = 0
        
        self._baseDodge = Person.setFrom(argDict, 'startingDexterity', 0)
        self._equipmentDodge = 0
        self._statusDodge = 0
        
        self._baseDR = Person.setFrom(argDict, 'startingDR', 0)
        self._equipmentDR = 0
        self._statusDR = 0
        
        # No such thing as 'base' force.
        # TODO: Consider moving these two to the Weapon class.
        self._equipmentForce = 0
        self._statusForce = 0
        
        self._baseMagicResist = Person.setFrom(argDict, 'startingPiety', 0)
        self._equipmentMagicResist = 0
        self._statusMagicResist = 0
        
        self._baseMeleeAccuracy = Person.setFrom(argDict, 'startingMeleeAccuracy', 0)
        self._equipmentMeleeAccuracy = 0
        self._statusMeleeAccuracy = 0
         
        self._baseMeleeDodge = Person.setFrom(argDict, 'startingMeleeDodge', 0)
        self._equipmentMeleeDodge = 0
        self._statusMeleeDodge = 0
         
        self._baseMight = Person.setFrom(argDict, 'startingMight', 0)
        self._equipmentMight = 0
        self._statusMight = 0
        
        self._baseMovementTiles = Person.setFrom(argDict, 'movementTiles', 2)
        self._equipmentMovementTiles = 0
        self._statusMovementTiles = 0
        
        self._basePoisonTolerance = Person.setFrom(argDict, 'startingPoisonTolerance', 0)
        self._equipmentPoisonTolerance = 0
        self._statusPoisonTolerance = 0  
        
        self._baseRangedAccuracy = Person.setFrom(argDict, 'startingRangedAccuracy', 0)
        self._equipmentRangedAccuracy = 0
        self._statusRangedAccuracy = 0
        
        self._baseRangedCriticalMagnitude = Person.setFrom(argDict, 'startingRangedCriticalMagnitude', 0)
        self._equipmentRangedCriticalMagnitude = 0
        self._statusRangedCriticalMagnitude = 0
        
        self._baseRangedDodge = Person.setFrom(argDict, 'startingRangedDodge', 0)
        self._equipmentRangedDodge = 0
        self._statusRangedDodge = 0      
        
        self._baseRangedForce = Person.setFrom(argDict, 'startingRangedForce', 0)
        self._equipmentRangedForce = 0
        self._statusRangedForce = 0    
        
        self._baseSneak = Person.setFrom(argDict, 'startingSneak', 0)
        self._equipmentSneak = 0
        self._statusSneak = 0
        
        self._baseSpellpower = Person.setFrom(argDict, 'startingSpellpower', 0)
        self._equipmentSpellpower = 0
        self._statusSpellpower = 0
        
        self._baseTrapEvade = Person.setFrom(argDict, 'startingTrapEvade', 0)
        self._equipmentTrapEvade = 0
        self._statusTrapEvade = 0
        
        self._baseArcaneResistance = Person.setFrom(argDict, 'startingArcaneResistance', 0)
        self._equipmentArcaneResistance = 0
        self._statusArcaneResistance = 0
        
        self._baseColdResistance = Person.setFrom(argDict, 'startingColdResistance', 0)
        self._equipmentColdResistance = 0
        self._statusColdResistance = 0
        
        self._baseDivineResistance = Person.setFrom(argDict, 'startingDivineResistance', 0)
        self._equipmentDivineResistance = 0
        self._statusDivineResistance = 0
        
        self._baseElectricResistance = Person.setFrom(argDict, 'startingElectricResistance', 0)
        self._equipmentElectricResistance = 0
        self._statusElectricResistance = 0
        
        self._baseFireResistance = Person.setFrom(argDict, 'startingFireResistance', 0)
        self._equipmentFireResistance = 0
        self._statusFireResistance = 0
        
        self._basePoisonResistance = Person.setFrom(argDict, 'startingPoisonResistance', 0)
        self._equipmentPoisonResistance = 0
        self._statusPoisonResistance = 0
        
        self._baseShadowResistance = Person.setFrom(argDict, 'startingShadowResistance', 0)
        self._equipmentShadowResistance = 0
        self._statusShadowResistance = 0
        
        # Physical Damage Resistances
         
        self._baseBludgeoningResistance = Person.setFrom(argDict, 'startingBludgeoningResistance', 0)
        self._equipmentBludegoningResistance = 0
        self._statusBludegoningResistance = 0
        
        self._basePiercingResistance = Person.setFrom(argDict, 'startingPiercingResistance', 0)
        self._equipmentPiercingResistance = 0
        self._statusPiercingResistance = 0
        
        self._baseSlashingResistance = Person.setFrom(argDict, 'startingSlashingResistance', 0)
        self._equipmentSlashingResistance = 0
        self._statusSlashingResistance = 0
        
        self._avoidanceChance = 0
        
        self._HPBufferList = []
        
        self._baseMovementAPCost = Person.setFrom(argDict, 'moveAP', Person.ERROR)
        self._equipmentMovementAPCost = 0
        self._overrideMovementAPCost = -1
        self._overrideMovementTurns = -1
        self._overrideMovements = -1
        self._statusMovementAPCost = 0
        
        self._baseMeleeAttackAPCost = Person.setFrom(argDict, 'meleeAP', Person.ERROR)
        self._baseRangedAttackAPCost = Person.setFrom(argDict, 'rangedAP', Person.ERROR)
        
        self._statusSpellFailureChance = 0
        
        self.listeners = []
    
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
    def overrideMovementTurns(self):
        return self._overrideMovementTurns
        
    @overrideMovementTurns.setter
    def overrideMovementTurns(self, value):
        if value < 0:
            value = -1
        self._overrideMovementTurns = value
        
    @property
    def overrideMovements(self):
        return self._overrideMovements
        
    @overrideMovements.setter
    def overrideMovements(self, value):
        if value < 0:
            value = -1
        self.overrideMovements = value
        
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
        return (self._baseArcaneResistance + self._equipmentArcaneResistance +
               self._statusArcaneResistance)
               
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
        return (self._baseColdResistance + self._equipmentColdResistance +
               self._statusColdResistance)
               
    @property
    def baseColdResistance(self):
        return self._baseColdResistance
        
    @baseColdResistance.setter
    def baseColdResistance(self, value):
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
        return (self._baseDivineResistance + self._equipmentDivineResistance +
               self._statusDivineResistance)
               
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
        return (self._baseElectricResistance + self._equipmentElectricResistance +
               self._statusElectricResistance)
               
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
        return (self._baseFireResistance + self._equipmentFireResistance +
               self._statusFireResistance)
               
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
        return (self._basePoisonResistance + self._equipmentPoisonResistance +
               self._statusPoisonResistance)
               
    @property
    def basePoisonResistance(self):
        return self._basePoisonResistance
        
    @basePoisonResistance.setter
    def basePoisonResistance(self, value):
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
        return (self._baseShadowResistance + self._equipmentShadowResistance +
               self._statusShadowResistance)
               
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

    # Physical "Element" Resistance:
    
    @property
    def totalBludgeoningResistance(self):
        return (self._baseBludgeoningResistance +
                self._equipmentBludgeoningResistance +
                self._statusBludgeoningResistance)
    
    @property
    def baseBludgeoningResistance(self):
        return self._baseBludgeoningResistance
        
    @baseBludgeoningResistance.setter
    def baseBludgeoningResistance(self, value):
        self._baseBludgeoningResistance = value
        
    @property
    def eqiupmentBludgeoningResistance(self):
        return self._equipmentBludgeoningResistance
    
    @eqiupmentBludgeoningResistance.setter
    def equipmentBludgeoningResistance(self, value):     
        self._equipmentBludgeoningResistance = value
        
    @property
    def statusBludgeoningResistance(self):
        return self._statusBludgeoningResistance
        
    @statusBludgeoningResistance.setter
    def statusBludgeoningResistance(self, value):
        self._statusBludgeoningResistance = value

    @property
    def totalPiercingResistance(self):
        return (self._basePiercingResistance +
                self._equipmentPiercingResistance +
                self._statusPiercingResistance)
    
    @property
    def basePiercingResistance(self):
        return self._basePiercingResistance
        
    @basePiercingResistance.setter
    def basePiercingResistance(self, value):
        self._basePiercingResistance = value
        
    @property
    def eqiupmentPiercingResistance(self):
        return self._equipmentPiercingResistance
    
    @eqiupmentPiercingResistance.setter
    def equipmentPiercingResistance(self, value):     
        self._equipmentPiercingResistance = value
        
    @property
    def statusPiercingResistance(self):
        return self._statusPiercingResistance
        
    @statusPiercingResistance.setter
    def statusPiercingResistance(self, value):
        self._statusPiercingResistance = value

    @property
    def totalSlashingResistance(self):
        return (self._baseSlashingResistance +
                self._equipmentSlashingResistance +
                self._statusSlashingResistance)
    
    @property
    def baseSlashingResistance(self):
        return self._baseSlashingResistance
        
    @baseSlashingResistance.setter
    def baseSlashingResistance(self, value):
        self._baseSlashingResistance = value
        
    @property
    def eqiupmentSlashingResistance(self):
        return self._equipmentSlashingResistance
    
    @eqiupmentSlashingResistance.setter
    def equipmentSlashingResistance(self, value):     
        self._equipmentSlashingResistance = value
        
    @property
    def statusSlashingResistance(self):
        return self._statusSlashingResistance
        
    @statusSlashingResistance.setter
    def statusSlashingResistance(self, value):
        self._statusSlashingResistance = value

    
    @property
    def totalDodge(self):
        """
        Dodge is determined by DEX, equipment that boosts Dodge,
        "static" abililties that boost Dodge, and "dynamic"
        statuses that boost or reduce Dodge.  Does not include
        rangedDodge or meleeDodge (even when relevant.)
        """
        return (self.totalDexterity + 
                self._equipmentDodge + 
                self._statusDodge + 
                self._baseDodge)
            
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
        return (self.totalCunning +
                self.totalDexterity +
                self._equipmentTrapEvade + 
                self._statusTrapEvade + 
                self._baseTrapEvade)
            
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
        return (self.totalCunning +
                self._equipmentAwareness + 
                self._statusAwareness + 
                self._baseAwareness)
            
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
        return max(0, self._equipmentDR + 
                      self._statusDR + 
                      self._baseDR)
            
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
        return (float(self._statusForce)/100 + float(self._equipmentForce) / 100)
        
    # TODO: Verify that force is not being treated as a float...
        
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
        return (max(0, (self.totalCunning - 10) * 0.25) +
                self._equipmentArmorPenetration + 
                self._statusArmorPenetration + 
                self._baseArmorPenetration)
            
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
        return (self._baseRangedDodge + self._equipmentRangedDodge +
               self._statusRangedDodge)
               
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
        
    @equipmentRangedDodge.setter
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
        return (self._baseRangedForce * (float(self._equipmentRangedForce) / 100) * 
               (1 + self._statusRangedForce))
               
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
        
        Note: The Shadow Walk double cunning effect is hardcoded
        into this formulation and thus does not need to be encoded
        anywhere else.
        """
        cunningBonus = max(0, self.totalCunning - 10)
        if isinstance(self, playercharacter) and self.characterClass == "Shadow":
            cunningBonus *= 2
        return (cunningBonus +
                self._equipmentSneak + 
                self._statusSneak + 
                self._baseSneak)
            
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
        
        
    @property
    def totalMagicResist(self):
        """
        MagicResist is determined by PIE, equipment that boosts MagicResist,
        "static" abililties that boost MagicResist, and "dynamic"
        statuses that boost or reduce MagicResist.
        """
        return (self.totalCunning + 
                self._equipmentMagicResist + 
                self._statusMagicResist + 
                self._baseMagicResist)
            
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
        return (max(0, self.totalConstitution - 10) +
                self._equipmentPoisonTolerance + 
                self._statusPoisonTolerance + 
                self._basePoisonTolerance)
            
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
    def totalRangedAccuracy(self):
        """
        RangedAccuracy is determined by DEX, equipment that boosts RangedAccuracy,
        "static" abililties that boost RangedAccuracy, and "dynamic"
        statuses that boost or reduce RangedAccuracy.
        """
        return (self.totalDexterity + 
                self._equipmentRangedAccuracy + 
                self._statusRangedAccuracy + 
                self._baseRangedAccuracy)
            
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
        return (100 + 
                self._equipmentRangedCriticalMagnitude +
                self._statusRangedCriticalMagnitude + 
                self._baseRangedCriticalMagnitude)        
            
    @property
    def equipmentRangedCriticalMagnitude(self):
        """
        Any ranged critical magnitude granted from any magical equipment
        currently equipped.  
        Will not automatically update.
        """
        return self._equipmentRangedCriticalMagnitude
            
    @equipmentRangedCriticalMagnitude.setter
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
        return (self.totalSorcery + 
                self._equipmentSpellpower + 
                self._statusSpellpower + 
                self._baseSpellpower)
            
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
        return (max(0, (self.totalCunning - 10) * 0.5) +
                self._equipmentCriticalChance + 
                self._statusCriticalChance + 
                self._baseCriticalChance)
            
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
        return (self._equipmentCriticalMagnitude/100 * 
                self._baseCriticalMagnitude/100 *
                (100 + self._statusCriticalMagnitude/100))        
            
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
    def totalMeleeAccuracy(self):
        """
        MeleeAccuracy is determined by STR, DEX, equipment that boosts MeleeAccuracy,
        "static" abililties that boost MeleeAccuracy, and "dynamic"
        statuses that boost or reduce MeleeAccuracy.
        """
        return (self.totalDexterity * 0.5 +
                self.totalStrength * 0.5 +
                self._equipmentMeleeAccuracy + 
                self._statusMeleeAccuracy + 
                self._baseMeleeAccuracy)
            
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
        return (self._equipmentMeleeDodge + 
                self._statusMeleeDodge + 
                self._baseMeleeDodge)
    
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
        return (max(0, self.totalStrength - 10) +
                self._equipmentMight + 
                self._statusMight + 
                self._baseMight)
            
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
        return max(self._baseMovementTiles + self._equipmentMovementTiles + 
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
        
    # Primary Attributes
    @property
    def totalDexterity(self):
        """Should always equal base + equipment + status Dexterity, except
        when that equation would reduce it to a non-positive value."""
        return max(self._baseDexterity + 
                   self._equipmentDexterity + 
                   self._statusDexterity) 
    
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
            self._baseDexterity = value
        
    @property
    def totalStrength(self):
        """Should always equal base + equipment + status Strength, except
        when that equation would reduce it to a non-positive value."""
        return (self._baseStrength + 
                self._equipmentStrength + 
                self._statusStrength)

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
            self._baseStrength = value      
    
    @property
    def totalCunning(self):
        """Should always equal base + equipment + status Cunning, except
        when that equation would reduce it to a non-positive value."""
        return (self._baseCunning + 
                self._equipmentCunning + 
                self._statusCunning)

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
            self._baseCunning = value   
    
    @property
    def totalSorcery(self):
        """Should always equal base + equipment + status Sorcery, except
        when that equation would reduce it to a non-positive value."""
        if self._baseSorcery == 0:
            return 0
        else:
            return (self._baseSorcery + 
                    self._equipmentSorcery + 
                    self._statusSorcery)

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
        return (self._basePiety + 
                self._equipmentPiety + 
                self._statusPiety)

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
        return (self._baseConstitution + 
                self._equipmentConstitution + 
                self._statusConstitution)

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
    def AP(self):
        """The current Action Points of a PlayerCharacter"""
        return self._AP
        
    @AP.setter
    def AP(self, value):
        if value > self._totalAP: 
            value = self._totalAP
        self._AP = value
    
    @property
    def restrictionAP(self):
        '''The amount of AP lost due to armor beyond maximum.
        Always 0 for monsters.'''
        return 0
    
    @property
    def totalAP(self):
        return self._baseAP + min(5, self._equipmentAP) - self.restrictionAP
        
    @property
    def equipmentAP(self):
        return self._equipmentAP
        
    @equipmentAP.setter
    def equipmentAP(self, value):
        ''' Value should not exceed +5 per item
        but it doesn't really matter if it does.'''
        self._equipmentAP += value
    
    @property
    def baseAP(self):
        """A value for the adjusted total AP for the player.
        this value can change only by equipping magical eqiupment
        that improves the max AP of a player."""
        return self._baseAP
        
    @baseAP.setter
    def baseAP(self, value):
        if value > 25: 
            value = 25
        if value < 0: 
            value = 0
        self._baseAP = value       
    
    
    
    @property
    def HP(self):
        """The current hit points of the player.  When it 
        reaches 0, the player dies."""
        return self._HP
    
    @HP.setter
    def HP(self, value):
        if value > self.totalHP:
            value = self.totalHP
        if value < 0:
            value = 0
        self._HP = value            
    
    @property
    def totalHP(self):
        """The maximum HP of the player.  Is determined by eqiupment,
        skills, statuses, and base attributes."""
        if self.totalConstitution == 0:
            return self.baseHP
        else:
            return self.baseHP + (self.totalConstitution - 10) * 4 + self.equipmentHP
    
    @property
    def equipmentHP(self):
        return self._equipmentHP
        
    @equipmentHP.setter
    def equipmentHP(self, value):
        self._equipmentHP = value
    
    @property
    def baseHP(self):
        return self._baseHP
        
    @baseHP.setter
    def baseHP(self, value):
        self._baseHP = value
    
    @property
    def MP(self):
        """The current Mana Points of a PlayerCharacter"""
        return self._MP
    
    @MP.setter
    def MP(self, value):
        """Will not exceed totalMP"""
        if value < 0:
            value = 0
        if value > self.totalMP:
            value = self.totalMP
        self._MP = value
        
    @property
    def totalMP(self):
        """The maximum MP of the player.  Is determined by class, level,
        equipment, skills, statuses, and base attributes."""
        if( self.totalPiety == 0 ):
            return self._baseMP
        else:
            return max(0, self._baseMP + (self.totalPiety - 10) * 4 + self.equipmentMP)
        # TODO Fix non-casters showing mana.
        
    @property
    def baseMP(self):
        return self._baseMP
        
    @baseMP.setter
    def baseMP(self, value):
        self._baseMP = value
        
    @property
    def equipmentMP(self):
        return self._equipmentMP
        
    @equipmentMP.setter
    def equipmentMP(self, value):
        self._equipmentMP = value

    @property
    def directionFacing(self):
        """The direction this Person is facing."""
        return self._directionFacing
        
    @directionFacing.setter
    def directionFacing(self, direction):
        """Possible values:
             "UP"
             "DOWN"
             "LEFT"
             "RIGHT" """
        if not direction:
            return
        direction = direction.upper()
        possibleValues = ["UP", "DOWN", "LEFT", "RIGHT"]
        if direction in possibleValues:
            self._directionFacing = direction
    
    @property
    def size(self):
        """The size of this person.  Does not necessarily indicate how many
        tiles it fills up."""
        return self._size
            
    @property
    def cooldownList(self):
        """A list of cooldown tuples of form [String, int].  These are used
        to indicate which abilities cannot be used until 'int' more turns
        have passed."""
        return self._cooldownList
        
    @cooldownList.setter
    def cooldownList(self, list):
        """May be used to change the cooldown list."""
        self._cooldownList = list
        
    @property 
    def statusList(self):
        """A list of all display Statuses currently active on this target."""
        return self._statusList
        
    @statusList.setter
    def statusList(self, list):
        """May be used to change the cooldown list."""
        self._statusList = list  
    
    @property
    def owner(self):
        return self._owner
        
    @owner.setter
    def owner(self, value):
        """Possible values:
             None (Usually the case)
             PlayerCharacter pc (If a summon/guardian)
             Monster m (If a minion of a monster)"""
        if ((value is None) or (value.isinstance(Person))):
            self._owner = value
        # TODO, if not None, set the link the other direction as well.
            
    @property
    def minionList(self):
        return self._minionList
        
    @minionList.setter
    def minionList(self, value):
        self._minionList = value
    
    @property
    def movementSpeed(self):
        '''The overworld movement speed.'''
        return 5 * float(self.totalMovementTiles) / float(self.totalMovementAPCost)
    
    def resource(self, type, quantity):
        """Returns True if the Person has at least 'quantity' of the resource.
        Inputs:
          self
          type = type of resource: "HP", "MP", "AP"
          quantity = positive integer
        Outputs:
          True or False"""
        if type == "AP":
            return (self.AP >= quantity)
        if type == "MP":
            return (self.MP >= quantity)
        if type == "HP":
            return (self.HP >= quantity)
        raise TypeError("Attempted to use an invalid resource type.")
        
        
    def inRange(self, target, range):
        """Returns True if the Person is at most range tiles away from the 
        target.
        Inputs:
          self
          target = may either be a Location or a Person
          range = a positive integer
        Outputs:
          True or False"""
        if range == -1:
            range = self.attackRange
        selfLoc = self.location
        otherLoc = target.location
        if range == 1:
            return location.in_melee_range(selfLoc, otherLoc)
        return location.distance(selfLoc, otherLoc) <= range
           
    def onCooldown(self, abilityName):
        """Returns True if the ability is currently unavailable due to
        being 'on cooldown' from having been used too recently.
        Inputs:
          self
          abilityNAme = The name of the ability being checked
        Outputs:
          True or False"""
        return (abilityName in self.cooldownList)
          
          
    def sizeCompare(self, size, smallerThan):
        """Returns True if the size of this Person is smaller than the given
        size and 'smallerThan' is True.  Returns True if the size of this
        Person is larger than the given size and 'smallerThan' is False.
        Inputs:
          self
          size = "Small", "Medium", "Large", or "Huge"
          smallerThan = boolean
        Outputs:
          True or False"""
        otherSizeNum = None
        possibleSizes = ["Small", "Medium", "Large", "Huge"]
        selfSizeNum = possibleSizes.index(self.size)
        if (size in possibleSizes):
            otherSizeNum = possibleSizes.index(size)
        else:
            raise TypeError("Attempted to compare with an invalid size.")
        
        if (smallerThan == True):
            return (selfSizeNum < otherSizeNum)
        elif (smallerThan == False):
            return (selfSizeNum > otherSizeNum)
       
    def usingWeapon(self, weaponType):
        """Returns True if the passed Weapon type matches the type of
        weapon this Person is using or is a superset of that type. 
        Also will return true if the exact name of the weapon being 
        weilded in either hand is specified.
        Inputs:
          self
          weaponType = "Sword", "Club", "Shortbow", "Longbow", "Bow",
                       "Crossbow", "Axe", "Polearm", "Ranged", "Melee",
                       "Shuriken", "Mage Weapon", "Sling", "Knife"
        Outputs:
          True or False"""
        weaponType = weaponType.capitalize().strip()
        acceptList = [weaponType]
        if weaponType == "Melee":
            acceptList.extend(["Sword", "Club", "Axe", "Polearm",
                               "Mage Weapon", "Knife"])
        elif weaponType == "Ranged":
            acceptList.extend(["Longbow", "Shortbow", "Sling", "Crossbow",
                               "Shuriken"])
        elif weaponType == "Bow":
            acceptList.extend(["Longbow", "Shortbow"])
        
        if self.team != "Players":
            wep = None
            if self.attackRange == 1:
                wep = "Sword"
            else:
                wep = "Bow"
            return wep in acceptList
        elif (self.equippedItems.equippedWeapon.name == weaponType or 
             self.equippedItems.equippedOffHand.name == weaponType):
            return True        
        else:
            return (self.equippedItems.equippedWeapon.type in acceptList or
                    self.equippedItems.equippedOffHand.type in acceptList)
        
    def usingArmor(self, armorLevel):
        """Returns True if the passed armorLevel matches the armor level
        the Person has currently equipped.
        Inputs:
          self
          armorLevel = "Heavy", "Medium", "Light", "Robes"
        Outputs:
          True or False"""
        return (self.equippedItems.armorLevel == armorLevel)
        
    def usingShield(self, shieldType):
        """Returns True if the passed shieldType matches the kind of 
        shield the Person has currently equipped.
        Inputs:
          self
          shieldType = "Heavy", "Medium", "Any", "None"
        Outputs:
          True or False"""
        shield = self.equippedItems.equippedShield
        if (shieldType == "Any"):
            return (shield is not None)
        elif (shieldType == "None"):
            return (shield is None)
        elif (shield == None):
            return False
        else: 
            return (shield.type == shieldType)
        
    def usingWeaponStyle(self, style):
        """Returns True if this Person is using (equipping) the given 
        weapon style.  Monsters are considered to be using no weapons.
        This will always return False in their case.
        Inputs: 
          self
          style = "Dual" (Two weapons), 
                  "Dual Same Type" (Two weapons that are also the same 
                                    weaponType)
                  "Two Handed" (One weapon that requires both hands)
                  "Single" (One weapon that requires one hand and the
                            other hand is empty)
                  "Single and Shield" (One weapon that requires one hand
                                       and a shield)
        Outputs:
          True or False"""
        style.replace("-", " ") 
        handOne = self.equippedItems.equippedWeapon
        handTwo = self.equippedItems.equippedOffHand
          
        if (style == "Dual Same Type" and 
           handOne is not None and 
           handTwo is not None):
            return handOne.type == handTwo.type
        if (style == "Dual"):
            return (handOne is not None and handTwo is not None)
        if (style == "Two Handed"):
            return (handOne is not None and handTwo == "Occupied")
        if (style == "Single"):
            return (handOne is not None and handTwo is None)
        if (style == "Single and Shield"):
            return (handOne is not None and self.usingShield("Any"))
        if (style == "Bare"):
            return (handOne is None and (handTwo is None or handTwo.type == "Shield"))
        # And for the monsters...
        return False
        
    def getNumberOfStackedStatus(self, statusName):
        """Returns the integer number of the status indicated currently
        present on the player.  Will simply return 0 if no such 'stacks' of
        the status are present at all.
        Inputs:
          self
          statusName = the internal name of the status effect to look for
        Ouputs:
          A non-negative integer"""
        statusObject = None
        for item in self.statusList:
            if (statusName == item.displayName):
                statusObject = item
        if (statusObject is None):
            return 0
        else:
            return statusObject.stacks
        
    def canReach(self, target, tilesAllowed):
        """Returns True if it is possible to walk from self's current location
        to the target's location within the allowed number of tiles.
        Inputs:
          self
          target = Location of destination
          tilesAllowed = non-negative integer of how many tiles can be used
                         to reach the target location.
        Outputs:
          True or False"""
        pass #TODO: Requires path-finding
        
    def inStealth(self):
        """Returns True if this Person has any form of stealth other than 
        invisibility.
        Inputs:
          self
        Outputs:
          True or False"""
        stealthList = ["Stealth", "Shadow Walk", "Conceal"]
        for item in self.statusList:
            if (item.name in stealthList):
                return True
        return False    
        
    def inBackstabPosition(self, target, rangedBackstab=False):
        """Returns True if this Person is behind the target, including behind
        diagonals.  If rangedBackstab is False, as it is by default, the player
        must also be in melee range."""
        targetFacing = target.directionFacing
        xDifference = self.location.x - target.location.x
        yDifference = self.location.y - target.location.y
        
        if(not rangedBackstab):
            if (abs(xDifference) > 1) or (abs(yDifference) > 1):
                return False
        
        if(targetFacing == "UP"):
            if (yDifference <= 0) or (abs(xDifference) > yDifference):
                return False
        elif(targetFacing == "DOWN"):
            if (yDifference >= 0) or (abs(xDifference) > yDifference):
                return False
        elif(targetFacing == "LEFT"):
            if (xDifference <= 0) or (abs(yDifference) > xDifference):
                return False
        elif(targetFacing == "RIGHT"):
            if (xDifference >= 0) or (abs(yDifference) > xDifference):
                return False
        else:
            raise TypeError("Invalid Directional Argument Given.")
            
        return True
        
    def isClass(self, className):
        """Returns True if this person has a character class of name
        'className'.
        Inputs: 
          self
          className = The name of the class to check against.
        Outputs:
          True or False"""
        return self.characterClass == className
    
    def hasAdjacentFreeSpace(self):
        """Returns True if this person has at least one connecting
        tile (at its location) that is not occupied.
        Inputs:
          self
        Outputs:
          True or False"""
        pass
        #xCoord = self.location.x
        #yCoord = self.location.y
        #adjacentCoords = ([[xCoord + 1, yCoord], [xCoord + 1, yCoord + 1]
        #                   [xCoord + 1, yCoord - 1], [xCoord, yCoord + 1]
        #                   [xCoord - 1, yCoord - 1], [xCoord - 1, yCoord]
        #                   [xCoord, yCoord - 1], [xCoord - 1, yCoord + 1]])
        #               
        #for coords in adjacentCoords:
        #    if Terrain.getTile(coords[0], coords[1]).isWalkable:
        #        return True
        #return False                
        # TODO Ask for such a method...          
    
    def hasWeaponEnchant(self):
        """Returns True if any wepaon enchantment cast by a spellsword is
        present on the weapon(s) of this Person.
        Inputs: 
          self
        Outputs:
          True or False"""
        for status in self.statusList:
            if "Weapon Enchantment" in status.categoryList:
                return True
        return False
        
    def hasStatus(self, statusName=None, statusCategory=None):
        """Returns True if this person has a status with a display name
        matching the given 'statusName' OR a status that belongs to a 
        category supplied.
        Inputs:
          self
          statusName = The name of the status to look for
          statusCategory = The name of the status cateogry to look for
        Outputs:
          True or False"""
        if statusName:
            for item in self.statusList:
                if statusName == item.name:
                    return True
        if statusCategory:
            for item in self.statusList:
                if statusCategory in item.categoryList:
                    return True
        return False
        
    def getStatusStackCount(self, statusName):
        """Returns the number of stacks of a particular status.
        If the status is not present on this Person, returns 0.
        Inputs:
          self,
          statusName = The name of the status to look for
        Outputs:
          A non-negative integer."""
        for item in self.statusList:
            if statusName == item.name:
                return item.stacks
        return 0
        
    # usingAnimalStyle method is identical to hasStatus but needs to
    # function out of combat as well.  TODO
    
    def isSummon(self):
        """Returns True if this Person is a Guardian summoned by a 
        Sorcerer playercharacter.
        Inputs:
          self
        Outputs:
          True or False"""
        return (self.owner is not None)
    
    def getMeleeFacingEnemy(self):
        """Returns the enemy as a Person directly in front of 
        this Person.  If there is not an enemy in front of this
        Person, it will return None instead.
        Inputs:
          self
        Outputs:
          Person -- enemy directly in front
          None -- if no enemy is directly in front""" 
        x = self.location.x
        y = self.location.y
        direction = self.directionFacing
        location = None
        if(direction == "DOWN"):
            location = Location(x, y + 1)
        elif(direction == "UP"):
            location = Location(x, y - 1)
        elif(direction == "LEFT"):
            location = Location(x - 1, y)
        elif(direction == "RIGHT"):
            location = Location(x + 1, y)
        
        possibleEnemy = Terrain.getObjectAt(location)
        if (isinstance(possibleEnemy, Person) and
            possibleEnemy.team == "Monsters"):
            return possibleEnemy
        else:
            return None
  
    def getMostRecentStatus(self, category): #Rename?
        """Returns the most recent Status object applied to this Person
        or None if no Statuses are on this Person.
        Inputs:
          self
          category = a string representing the category of status effect
                     to look for.  Possible values include:
                     "Buff", "Debuff", "Magical", "Physical", 
                     "Weapon Enchantment", "Threading", "Stealth",
                     "DR Debuff"
        Outputs:
          Status object or None"""
        matches = []
        for status in self.statusList:
            if (status.category == category):
                matches.append(status)
        # Get the last element as it will be the last one applied.
        if matches:
            return matches[-1]
        else:
            return None
            
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
        else:
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
        else:
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
        
    def detectStealth(self, stealthedTarget):
        ''' Rolls to see if this Person can detect the stealthed
        target.  Currently does not factor in "boss" monsters etc.
        Returns True if this Person has detected the stealthedTarget. '''
        if not stealthedTarget.inStealth():
            print "Target is not in stealth."
            return True
        chance = max(1, 15 - stealthedTarget.totalSneak + self.totalAwareness)
        if Dice.rollBeneath(chance):
            return True
        else:
            return False
        # Include Noise later? TODO (Out of combat considerations.)
        
    # Non theorycrafted methods go here:
