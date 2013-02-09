#!/usr/bin/python

import sys
import dice
import status as displaystatus
import playercharacter as pc
import broadcast
import theorycraft

class IncompleteMethodCall(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Combat(object):
    def __init__(self):
        pass
       
    @staticmethod
    def modifyResource(target, type, value):
        """Modifies the given resource by the given value.
           May need to implement listeners...TODO
        Inputs:
          target == Person
          type == "AP", "MP", "HP"
          value == int, non-zero.
        Outputs: 
          None"""
        type = type.upper()
        if type == "AP":
            target.AP += value
            Combat._shoutResourceLevel(target, type, target.AP / target.totalAP)
        elif type == "MP":
            target.MP += value
            if target.totalMP > 0:
                Combat._shoutResourceLevel(target, type, target.MP / target.totalMP)
        elif type == "HP":
            target.HP += value
            Combat._shoutResourceLevel(target, type, target.HP / target.totalHP)
        else:
            raise TypeError("Type: " + type + " is not valid.  Proper values are: 'HP', 'MP', or 'AP'.")
    
    @staticmethod
    def applyCooldown(target, abilityName, duration):
        """Adds the ability to the target's list of current cooldowns with the given
        duration.  No behavior is guaranteed if the character already has this ability on
        cooldown.
        Inputs: 
          target == Person
          abilityName == "ExampleAbility"
          duration = positive int
        Outputs:
          None"""
        if (duration <= 0):
            return
        target.cooldownList.append([abilityName, duration])
        # Should we check here if the abilityName matches any known ability?  That is, check for typos?
        
    @staticmethod
    def calcPhysicalHitChance(offense, defense):
        """Uses the game rules' dodge mechanics to compute how likely a
        dodge vs. accuracy lineup would be.
        Inputs:
          offense -- int probably accuracy
          defense -- int probably dodge   
        Outputs:
          [int, int]
            index[0] == chanceToHit (5 to 100)
            index[1] == any crit modification from accuracy extremes
                        (will typically be 0)"""
        accCritMod = 0
        chanceToHit = None
        delta = offense - defense
        if(10 < delta):
            chanceToHit = 100
            accCritMod = (delta - 10) * 0.25
        elif(0 <= delta <= 10):
            chanceToHit = 90 + delta
        elif(-6 <= delta < 0):
            chanceToHit = 90 - delta * 3
        elif(-27 <= delta < -6):
            chanceToHit = 72 - (delta + 6) * 2
        elif(-47 <= delta < -27):
            chanceToHit = 30 - (delta + 27) * 1                    
        elif(-57 <= delta < -47):
            chanceToHit = 10 - (delta + 47) * 0.5
        else:
            chanceToHit = 5
            accCritMod = (delta + 57) * (-2)
        return [chanceToHit, accCritMod]
        
    @staticmethod 
    def calcMagicalHit(offense, defense):
        """Uses the game rules' magical resistance mechanics to compute
        which kind of hit this attack is.
        Inputs:
          offense -- int probably spellpower
          defense -- int probably magicResist
        Outputs:
          Any Hit type string"""
        offense *= Dice.rollFloat(0.75, 1.00)
        defense *= Dice.rollFloat(0.75, 1.00)
        if(offense <= 3 * defense):
            # Spell fails Listener TODO
            return "Miss"
        elif(offense < defense):
            return "Partially Resisted"
        elif(defense <= offense and offense <= defense * 2):
            return "Normal Hit"
        else: 
            # Defense less than 1/2 offense
            return "Critical Hit" 
        
    @staticmethod
    def calcPoisonHit(offense, defense):
        """Uses the game rules' poison tolerance mechanics to compute whether
        this poison hit works or is ignored.
        Inputs: 
          offense -- int probably poison rating
          defense -- int probably poison tolerance
        Outputs:
          "Normal Hit" or "Miss" """
        offense *= Dice.rollFloat(0.5, 1.0)
        defense *= Dice.rollFloat(0.5, 1.0)
        if(offense >= defense):
            return "Normal Hit"
        else:
            return "Miss"
        
    @staticmethod
    def physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty):
        hitDuple = None
        if (source.usingWeapon("Ranged")):
            #Ranged attack
            if(source.inRange(target, 1) and not ignoreMeleeBowPenalty):
                #Ranged attack with penalty 20% miss chance TODO
                #Passives alter how this functions? TODO
                #Ranged attack not in melee, or it doesn't matter.
                pass
            defense = target.totalDodge + target.totalRangedDodge
            offense = source.totalRangedAccuracy + modifier
            hitDuple = Combat.calcPhysicalHitChance(offense, defense)    
        else:
            #Melee attack
            defense = target.totalDodge + target.totalMeleeDodge
            offense = source.totalMeleeAccuracy + modifier
            hitDuple = Combat.calcPhysicalHitChance(offense, defense)
        chanceToHit = hitDuple[0]
        accuracyCritMod = hitDuple[1]
        if (Dice.rollBeneath(chanceToHit)):
            # We hit! Listener? TODO
            chanceToCritical = source.totalCriticalChance + accuracyCritMod + critMod
            if(Dice.rollBeneath(chanceToCritical)):
                # Critical hit! Listener TODO
                return "Critical Hit"
            else:
                return "Normal Hit"
        else:
            return "Miss"
        
    @staticmethod
    def magicalHitMechanics(source, target):
        offense = source.totalSpellpower
        defense = target.totalMagicResist
        return Combat.calcMagicalHit(offense, defense)
        
    @staticmethod
    def poisonHitMechanics(source, target, rating):
        offensePoison = source.totalPoisonRatingBonus + rating
        defensePoison = target.totalPoisonTolerance
        poisonHit = Combat.calcPoisonHit(offensePoison, defensePoison)
        
    @staticmethod
    def calcHit(source, target, type, rating=0, modifier=0, critMod=0, ignoreMeleeBowPenalty=False):
        """Determies if the attack performed from the source to the target is successful, and returns 
        a HitType string to indicate this.  Nees listeners TODO
        Inputs:        
          source -- Person performing attack
          target -- Person receiving attack
          type -- The type of attack in question; possible values:
            "Physical" (Dodge vs. Acuracy)
            "Magical"  (Magic Resist vs. Spellpower)
            "Magical-Poison"  (Poison Tolerance vs. Poison Rating after Magical roll)
            "Physical-Poison" (Poison Tolerance vs. Poison Rating after Physical roll)
            "Poison"   (Poison Tolerance vs. Poison Rating only)
            UNIMPLEMENTED:: "Trap"     (Trap Evade vs. Trap Rating)
          rating -- (optional) int indicating the poison or trap rating of the attack.
          modifier -- (optional) int indicating the +chance to hit this attack has beyond normal.
          critMod -- (optional) int indicating the additional % chance to critical this attack has.
          ignoreMeleeBowPenalty -- (optional) boolean indicating if the usual melee bow miss penalty is ignored.
        Outputs:
          A string representing the type of hit; possible values:
            "Miss" (Failed to have any effect)
            "Partially Resisted" (Only possible with magic)
            "Normal Hit" (Standard outcome for successful attacks)
            "Critical Hit" (Possible outcome for successful physical attacks and magical attacks
                            although most of the latter ignore whether the spell was a critical or not.)"""
        type = type.capitalize().strip().replace("-", " ")
        if (type == "Physical"):
            Combat._shoutAttackStart(source, target)
            return Combat.physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty)
        
        if (type == "Magical"):
            return Combat.magicalHitMechanics(source, target)
            
        if (type == "Magical Poison" or type == "Poison Magical"):
            if (Combat.poisonHitMechanics(source, target, rating) == "Normal Hit"):
                return Combat.magicalHitMechanics(source, target)
            else:
                return "Miss"
        
        if (type == "Physical Poison" or type == "Poison Physical"):
            Combat._shoutAttackStart(source, target)
            if (Combat.poisonHitMechanics(source, target, rating) == "Normal Hit"):
                return Combat.physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty)
            else:
                return "Miss"
            
        if (type == "Poison"):
            return Combat.poisonHitMechanics(source, target, rating)
            
        if (type == "Trap"):
            raise NotImplementedError("This method does not yet support the Trap type.")
            
        raise TypeError("Unknown Attack Type: " + type + " .")            
        
    @staticmethod
    def addStatus(target, status, duration, magnitude=0, chance=1, 
                  overwrite=True, partial=False, critical=False,
                  hitValue="Normal Hit", min=0, max=0, relativeTarget=None,
                  applier=None, scalesWith=None, scaleFactor=0, charges=0):
        """Method is used to apply a Status to a target Person.  The properties
        needed to create and apply the status are mostly provided by default parameters
        and in most cases, they can be ignored.
        Inputs: (optional parameters indicated by a star)
          target -- Person; the target of the Status
          status -- string; the name of the status to apply
          duration -- int; the number of turns this status should last, if the status
                           is intended to last indefinitely, the duration should be
                           set to -1.
          magnitude -- int*; the power of the status.  It is not used by many statuses.
                            if it is not needed, it can be kept at its default value of
                            zero.
          chance -- float*; the chance this status will be applied at all.  It defaults
                            to 1, which indicates a 100% chance of application.  This 
                            parameter was included to aid with the logic of the data files.
          overwrite -- boolean*; whether or not this Status should be overwritten by 
                                 a Status of the same exact type.  It should typically be
                                 kept at its default value of True, but if it is a status
                                 that needs to 'stack', it should be False.
          partial -- boolean*; whether or not this Status will be ignored should the 
                               hitValue be "Partially Resisted".  If True and the 
                               hitValue is "Partially Resisted", this method will have
                               no effect.
          critical -- boolean*; whether or not this Status requires a hitValue of
                                "Critical Hit" in order to take effect.  Defaults to 
                                False.
          hitValue -- hit type string*; defaults to "Normal Hit".  If the value is provided
                               and is "Miss", the method will have no effect.  Otherwise it
                               may only have varied behavior if either the critical or 
                               partial booleans are set to True.
          min -- int*; some Statuses require a range of values to be supplied.  If this is
                       the case, this should be a non-negative value.
          max -- int*; some Statuses require a range of values to be supplied.  If this is
                       the case, this should be a non-negative value greater than 'min'.
          relativeTarget -- Person*; a few Statuses reference another Person as a relative
                            target that also has some linked behavior applied.  Should almost
                            always be left as None however.
          applier -- Person*; some Statuses require information from the person that applied
                              the status, such as bonusElementalDamage modifying the exact
                              damage of a DoT.  Otherwise this should be left as None.
          scalesWith -- string attribute*; if an applier is specified, this should be the
                              attribute type that should be read from the applier to determine
                              some scaling property.  Possible values are:
                              "Strength", "Cunning", "Spellpower"
          scaleFactor -- float*; a non-negative value that indicates how much the scaling attribute
                              should influence the values of this Status. Should only be used in
                              conjunction with 'applier' and 'scalesWith'.
          charges -- int*; some statuses have a number of charges until they expire instead of 
                           a duration.  Is set to a default of zero if not time based.
        Outputs:
          None"""
        if(hitValue == "Miss" or (hitValue == "Partially Resisted" and partial == True)):
            return
        if(hitValue != "Critical Hit" and critical == True):
            return
        if(Dice.rollSuccess(100 * chance) == "Miss"):
            return
        
        Combat._shoutStatusApplied(target, status)
        
        dStatus = None
        for display in theorycraft.TheoryCraft.statuses:
            if display.displayName == status:
                dStatus = display
        dStatus = dStatus.cloneWithDetails(magnitude, duration, min, max, charges)
        
        for display in target.statusList:
            if display.displayName == dStatus.displayName:
                if overwrite:
                    display.stacks += 1
                else:
                    removeStatus(target, display.displayName)
                    target.statusList.append(dStatus)
                    dStatus.activate(target)
        
        # Haven't figured out what to do with these yet, TODO
        # relativeTarget,
        # applier, scalesWith, scaleFactor
        
        # Haven't figured out what to do with immunity either! TODO
    
        
    @staticmethod
    def removeStatus(target, statusName):
        """Removes a specific status effect from a given Person.
        Will simply do nothing if the status is not found.
        Inputs: 
          target -- Person
          statusName -- the name of a status effect to remove
        Outputs:
          None"""
        statusName = statusName.capitalize().strip()
        matchingStatus = None
        for stat in target.statusList:
            if stat.displayName == statusName:
                matchingStatus = target.statusList
                break
        if matchingStatus:
            target.statusList.remove(matchingStatus)
            
    @staticmethod
    def removeStealth(target):
        """Removes any form of stealth (other than invisibility) from
        the given Person.
        Inputs: 
          target -- Person
        Outputs:
          None"""
        Combat.removeStatus(target, "Stealth")
        Combat.removeStatus(target, "Conceal")
        Combat.removeStatus(target, "Shadow Walk")
    
    @staticmethod
    def removeStatusOfType(target, category, removeAll=False):
        """Removes a random status from the given 'category' from the target.
        Alternatively, if 'removeAll' is set, it will remove all statuses that
        fit within the category given.
        Inputs:
          target -- Person; the character to remove status(es) from
          category -- string; a status category identifying a set of statuses
                      possible values: TODO
          removeAll -- boolean*; if set, will remove all statuses belonging to
                       the given category instead of a single random status 
                       belonging to the category
        Output:
          None"""
        removalCandidates = []
        for dStatus in target.statusList:
            if category in dStatus.caterogyList or category == dStatus.element:
                removalCandidates.add(dStatus)
        
        if removalCandidates:
            if removeAll:
                for dStatus in removalCandidates:
                    Combat.removeStatus(target, dStatus.displayName)
            else:
                # Does this work for roll(0,0) ? TODO
                choice = Dice.roll(0, len(removalCandidates) - 1)
                Combat.removeStatus(target, removalCandidates[choice].displayName)
        
    
    @staticmethod
    def knockback(target, sourceOfImpact, distance, ignoreResistance=False, didHit=True):
        """Moves the target via 'knockback' a set number of tiles away from the source of 
        impact.
        Inputs: 
          target -- Person to move
          sourceOfImpact -- Tile from which the knockback originated
          distance -- int number of tiles to move
          ignoreResistance -- (optional) if True, will not roll to see if the resistance of
                              the Person causes him to remain unaffected by the knockback
          didHit -- (optional) boolean; used to determine if this method should do anything.
                    was included to allow simpler logic in the data files."""
        if not didHit:
            return
        pass
        # TODO
        
    @staticmethod
    def calcDamage(source, target, min, max, element, hitValue, partial=1, critical=1, scalesWith=None, scaleFactor=0):
        """Computes the amount of damage that should be dealt to the target after considering all bonuses and penalties
        to the attack that caused this method to be called such as source elemental damage bonuses or target vulnerabilities.
        Does not actually apply any damage to anything.
        Inputs:
          source -- Person; attacker
          target -- Person; victim
          min -- int; the minimum base damage to roll
          max -- int; the maximum base damage to roll; if less than min, will be set to min
          element -- string; the elemental type of the attack.  Possible values:
                     "Fire", "Cold", "Electric", "Poison", "Divine", "Shadow", "Arcane",
                     "Bludegoning", "Piercing", "Slashing"
          hitValue -- hitType string; Possible values:
                     "Miss", "Normal Hit", "Partially Resisted", "Critical Hit"
          partial -- (optional) float, non-negative; the amount to multiply the damage by if the attack 
                     was partially resisted
          critical -- (optional) float, non-negative; the amount to multiply the damage by if the attack
                     was a critical hit
          scalesWith -- (optional) string attribute; the attribute to use if the attack scales with an attriute's value
                      possible values:
                      "Strength", "Cunning", "Spellpower"
          scaleFactor -- (optional) float, non-negative; the amount to multiply the base damage by per point of the
                         scaling attribute.  If the scaling attribute is not specified but this is given an non-zero
                         value, it will raise an IncompleteMethodCall Error.
        Outputs:
          non-negative int representing the damage that should be dealt to the target"""
        # Massage input.
        element = element.strip().capitalize()
        hitValue = hitValue.strip().capitalize()
        if scalesWith:
            scalesWith = scalesWith.strip().capitalize()
        
        # Actual method:
        if hitValue == "Miss":
            return 0
       
        if max < min:
            max = min
        dieRoll = Dice.roll(min, max)
        
        if scalesWith == "Strength":
            dieRoll *= 1 + (source.totalStrength * scaleFactor)
        elif scalesWith == "Cunning":
            dieRoll *= 1 + (source.totalCunning * scaleFactor)
        elif scalesWith == "Spellpower":
            dieRoll *= 1 + (source.totalSpellpower * scaleFactor)
        elif scalesWith is not None:
            raise TypeError("calcDamage cannot be called with scaling attribute: " + scalesWith + " .")
        
        if hitValue == "Critical Hit":
            dieRoll *= critical
        elif hitValue == "Partially Resisted":
            dieRoll *= partial
            
        # TODO Worry about resistances above 80% that are reduced by any amount by some ability...
        if source.isinstance(Person):
            if element == "Fire":
                dieRoll *= 1 + (source.totalFireBonusDamage / 100)
            elif element == "Cold":
                dieRoll *= 1 + (source.totalColdBonusDamage / 100)         
            elif element == "Electric":
                dieRoll *= 1 + (source.totalElectricBonusDamage / 100)
            elif element == "Poison":
                dieRoll *= 1 + (source.totalPoisonBonusDamage / 100)    
            elif element == "Shadow":
                dieRoll *= 1 + (source.totalShadowBonusDamage / 100)
            elif element == "Divine":
                dieRoll *= 1 + (source.totalDivineBonusDamage / 100)
            elif element == "Arcane":
                dieRoll *= 1 + (source.totalArcaneBonusDamage / 100)

        if element == "Fire":
            dieRoll *= 1 - (target.totalFireResistance / 100)
        elif element == "Cold":
            dieRoll *= 1 - (target.totalColdResistance / 100)           
        elif element == "Electric":
            dieRoll *= 1 - (target.totalElectricResistance / 100)
        elif element == "Poison":
            dieRoll *= 1 - (target.totalPoisonResistance / 100)    
        elif element == "Shadow":
            dieRoll *= 1 - (target.totalShadowResistance / 100)
        elif element == "Divine":
            dieRoll *= 1 - (target.totalDivineResistance / 100)
        elif element == "Arcane":
            dieRoll *= 1 - (target.totalArcaneResistance / 100)
        elif element == "Bludgeoning":
            dieRoll *= 1 - (target.totalBludgeoningResistance / 100)
        elif element == "Piercing":
            dieRoll *= 1 - (target.totalPiercingResistance / 100)
        elif element == "Slashing":
            dieRoll *= 1 - (target.totalSlashingResistance / 100)
        else:
            raise TypeError("Encountered an unknown element: " + element + " .")
            
        if dieRoll < 0:
            dieRoll = 0
        return dieRoll.round()
        
    @staticmethod
    def basicAttack(source, target, hitType, **params):
        if source.isinstance(pc.PlayerCharacter):
            if source.usingWeaponStyle("Dual"):
                originalCounterStatus = params['noCounter']
                params['noCounter'] = True
                weaponAttack(source, target, hitType[0], **params)
                params['noCounter'] = originalCounterStatus
                weaponAttack(source, target, hitType[1], **params)
            else:
                weaponAttack(source, target, hitType[0], **params)
        else:
            pass
            # Monster Attack: TODO
        
    
    @staticmethod
    def weaponAttack(source, target, hitType, forceMod=1, criticalDamageMod=1, armorPenetrationMod=0,
                     elementOverride=None, noCounter=False, overallDamageMod=1, mightMod=0, 
                     ignoreOnHitEffects=False, poisonRatingMod=0, backstab=False, hand="Right"):
        """Performs a weapon attack against the target from the source.  Calls actually apply the damage
        to the target, unlike 'calcDamage()'.
        Inputs: (optional values indicated by a *)
          source -- Person; attacker
          target -- Person; victim
          hitType -- string; possbile values: "Miss", "Normal Hit", "Critical Hit"
          forceMod -- float*; the amount to multiply the weapon's Force by for this attack
          criticalDamageMod -- float*; the amount to multiply the attack's critical damage by
          armorPenetrationMod -- int*; the amount of armor penetration added to this attack
          elementOverride -- string*; if this attack's native elemental types are to be ignored, this
                             field should be one of the elements.  All damage dealt by this attack will
                             be converted to that type before application.
          noCounter -- boolean*; if set, this will prevent any immediate counterattacks
          overallDamageMod -- float*; the amount to multiply the end result of this damage by.
          mightMod -- int*; the amount of bonus might applied to this attack
          ignoreOnHitEffects -- boolean*; if set, this attack will not trigger listeners waiting for
                                a weapon attack or apply any weapon's on-hit effects.
          poisonRatingMod -- int*; the amount to boost the poison rating of this attack by for any added
                                  'applied' poisons.
          backstab -- boolean*; was this attack a backstab?
          hand -- string*; which hand is attacking ("Right" or "Left")
        Outputs:
          None"""
        Combat._shoutAttackHit(source, target, hitType)
        
        if hitType == "Miss":
            # Enemy still counters
            Combat._shoutAttackComplete(source, target, noCounter) 
            return
        # TODO: Barehands...
        weapon = source.equippedItem.equippedWeapon
        effectiveForce = source.totalForce * forceMod
        if( source.usingWeapon(ranged) ):
            effectiveForce *= 1 + (source.totalRangedForce / 100)
        effectiveMight = round(Dice.rollFloat(0.5, 1.0) * (source.totalMight + mightMod) * (effectiveForce / 100))       
        effectiveDR = min(80, max(0, target.totalDR - (armorPenetrationMod + source.totalArmorPenetration)))
        outgoingDamage = (Dice.roll(weapon.damageMin + weapon.damageMinBonus, 
                                    weapon.damageMax + weapon.damageMaxBonus) * 
                         (1 - (effectiveDR / 100)))
        outgoingDamage *= overallDamageMod
        
        if hitType == "Critical Hit":
            outgoingDamage += outgoingDamage * criticalDamageMod * weapon.criticalMultiplier / 100

        elementalEffects = Combat.applyOnHitEffects(source, target)
        if elementOverride:
            # Treat all damage thus far as elemental.
            elementalEffects.append([elementOverride, outgoingDamage])
            outgoingDamage = 0
        else:
            if weapon.damageType == "Bludgeoning":
                outgoingDamage *= (1 - (target.totalBludgeoningResistance / 100))
            elif weapon.damageType == "Piercing":
                outgoingDamage *= (1 - (target.totalPiercingResistance / 100))
            elif weapon.damageType == "Slashing":
                outgoingDamage *= (1 - (target.totalSlashingResistance / 100))
        # TODO: Deal with dual-type weapons    
        totalDamage = Combat.sumElementalEffects(elementalEffects, elementOverride) + outgoingDamage     
     
        target.lowerHP(totalDamage)
        Combat._shoutAttackComplete(source, target, noCounter) 
        
    @staticmethod
    def sumElementalEffects(elementalEffects, overrideElement=None):
        damSum = 0
        for duple in elementalEffects:
            if overrideElement:
                duple[0] = overrideElement
            if duple[0] == "Arcane":
                currentDamage = round(duple[1] * (1 + source.totalArcaneBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalArcaneResistance / 100))
                damSum += currentDamage
            elif duple[0] == "Cold":
                currentDamage = round(duple[1] * (1 + source.totalColdBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalColdResistance / 100))
                damSum += currentDamage                
            elif duple[0] == "Divine":
                currentDamage = round(duple[1] * (1 + source.totalDivineBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalDivineResistance / 100))
                damSum += currentDamage
            elif duple[0] == "Electric":
                currentDamage = round(duple[1] * (1 + source.totalElectricBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalElectricResistance / 100))
                damSum += currentDamage
            elif duple[0] == "Fire":
                currentDamage = round(duple[1] * (1 + source.totalFireBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalFireResistance / 100))
                damSum += currentDamage
            elif duple[0] == "Poison":
                currentDamage = round(duple[1] * (1 + source.totalPoisonBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalPoisonResistance / 100))
                damSum += currentDamage
            elif duple[0] == "Shadow":
                currentDamage = round(duple[1] * (1 + source.totalShadowBonusDamage / 100))
                currentDamage = round(currentDamage * (1 - target.totalShadowResistance / 100))
                damSum += currentDamage
        return damSum
        
    @staticmethod
    def setMovementCost(target, newCost, numberOfMoves=1, duration=-1, inStealth=False):
        """Sets the AP cost of the next move of the target Person to the specified value.
        By default, this will only apply to the next movement.
        Inputs:
          target -- Person; the target whose movement cost we are adjusting
          newCost -- int; a non-negative value to assign the AP cost of movement to.
          numberOfMoves* -- int; the number of moves at this adjusted AP cost.  Once 
                           expired, this method will reset the AP movement cost to its
                           default value.  If this is to be time based and not based
                           on the number of movements, this parameter should be set
                           to -1.
          duration -- int*; the number of turns this AP cost should be assigned to the target.
                           By default, it is -1 which indicates it is not based on the 
                           number of turns, but rather the number of movements.
          inStealth -- boolean*; If set, will cause the AP cost to reset to its default value
                                 upon exiting stealth.
        Outputs:
          None"""
        if newCost < 0:
            return
        target.overrideMovementAPCost = newCost
        target.overrideMovements = numberOfMoves
        target.overrideMovementTurns = duration
        #TODO -- trigger duration/number of moves/break on stealth??
        
    @staticmethod
    def movePlayer(target, destination, instant=False):
        """Will move the player character from its current location to the given
        destination tile.  By default, will show the moving animation.
        Inputs:
          target -- Person; the Person to move
          destination -- Tile; the location to move the target to
          instant -- boolean*; if set, the moving animation will not be displayed
                               and the player will immediately be sent to the Tile.
        Outputs:
          None"""
        pass #TODO
        
    @staticmethod
    def endTurn(player):
        """Will end the turn of the given player-character.
        Inputs:
          player -- Person; the player whose turn will be ended
        Outputs:
          None"""
        pass #TODO
        
    @staticmethod
    def modifyThreat(source, target, threatAdjustment):
        """Alters the threat of the given source toward the target specified by 
        multiplying the existing level by threatAdjustment.
        Inputs:
          source -- Person; the monster whose threat level will be modified
          target -- Person; the player to which the monster will have an adjusted
                    threat level
          threadAdjustment -- float; the amount to mulitply the threat level by
        Outputs:
          None"""
        pass #TODO
        
    @staticmethod
    def unsummonGuardian(target):
        """Removes the current guardian of the player from the battlefield.
        The player will not incur an HP loss.
        Inputs:
          target -- Person; owner of the guardian
        Outputs:
          None"""
        pass #TODO

    @staticmethod
    def summonGuardian(owner, name):
        """Create a Sorcerer-type Guardian on a nearby tile with the given
        name.
        Inputs:
          owner -- Person; the Sorcerer performing the summon
          name -- string; the name of the particular summon, must match an 
                  actual summon's name
        Outputs:
          None"""
        pass #TODO
    
    @staticmethod
    def disarmTrap(thief, trap, wasSuccessful):
        """Disarm the trap specified with the thief and his allies gaining
        experience.  If wasSuccessful is False, simply return with no effect.
        Inputs:
          thief -- Person; the thief disarming the trap
          trap -- Trap; the trap being disarmed
          wasSuccessful -- boolean*; If False, will cause this method to do 
                           nothing.  It was included to simplify data file
                           logic and possibly for extension later with 
                           'critical failure' type penalties etc.
        Outputs:
          None"""
        if not wasSuccessful:
            return
        pass 
        #TODO
    
    @staticmethod
    def lowerHP(target, amount):
        """Used to actually lower the amount of HP a Person has.  May kill that person.
        Will attempt to use any HP buffer first and may be interrupted by listeners.
        Inputs:
          target -- Person; the person taking damage
          amount -- the final amount to deal to the target
        Outputs: 
          None"""
        if amount <= 0:
            return
        interruptCodes = Combat._shoutDamage(target, amount)
        if interruptCodes and "Ignore Damage" in interruptCodes:
            return
            
        remaining = amount
        while( target.HPBufferList ):
            current = target.HPBufferList[0]
            if remaining > current[1]:
                remaining -= current[1]
                target.HPBufferList.remove(current)
            elif remaining < current[1]:
                current[1] -= remaining
                return
            elif remaining == current[1]:
                target.HPBufferList.remove(current)
                return
        Combat.modifyResource(target, "HP", remaining)
        # Plenty of listeners here TODO
        
    @staticmethod
    def healTarget(source, target, amount):
        """Used to actually perform healing to the target from the source.
        Cannot 'overheal' or refill an HP buffer.
        Inputs:
          source -- Person; the person performing the healer
          target -- Person; the person receiving the healing, may be the same as the source.
          amount -- int; the amount of HP to restore
        Outputs:
          None"""
        total = round(amount * (1 + source.healingBonus/100))
        # Listeners here? TODO
        Combat.modifyResource(target, "HP", total)
     
    @staticmethod
    def applyElementalEffects(source):
        ee = []
        for effect in source.onHitEffects:
            if "On Hit" in effect.categories:
                duple = effect.apply(source, target)
                if duple:
                    ee.append(duple)
        return ee
     
    @staticmethod
    def _shoutAttackStart(source, target):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        if source.team == "Monsters":
            direction = "Incoming"
            otherParty = source
            hearer = target
        attackType = "Ranged"
        if source.usingWeapon("Melee"):
            attackType = "Melee"
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)
    
    @staticmethod
    def _shoutAttackHit(source, target, hitType):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        if hitType != "Critical Hit":
            hitType = ""
        if source.team == "Monsters":
            direction = "Incoming"
            otherParty = source
            hearer = target
        attackType = "Ranged"
        if source.usingWeapon("Melee"):
            attackType = "Melee"
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty, 'suffix' : hitType}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)
        
    @staticmethod
    def _shoutAttackComplete(source, target, noCounter):
        direction = "Outgoing"
        hearer = source
        otherParty = target
        if source.team == "Monsters":
            direction = "Incoming"
            otherParty = source
            hearer = target
        attackType = "Ranged"
        if source.usingWeapon("Melee"):
            attackType = "Melee"
        bundle = {'direction' : direction, 'type' : attackType, 'otherPerson' : otherParty, 'suffix' : 'Complete', 'noCounter' : noCounter}
        bc = broadcast.AttackBroadcast(bundle)
        bc.shout(hearer)
        
    @staticmethod
    def _shoutDamage(target, amount):
        direction = "Incoming"
        if target.team == "Monsters":
            direction = "Outgoing"
        bundle = {'direction' : direction, 'amount' : amount}
        bc = broadcast.DamageBroadcast(bundle)
        return bc.shout(target)
        
    @staticmethod
    def _shoutStatusApplied(target, statusName):
        if target.team != "Players":
            return
        bc = broadcast.StatusBroadcast({'statusName' : statusName})
        bc.shout(target)
        
    @staticmethod
    def _shoutResourceLevel(target, resourceType, resourcePercent):
        if target.team != "Players":
            return
        bc = broadcast.ResourceLevelBroadcast({'resource' : resourceType, 'percent' : resourcePercent})
        bc.shout(target)
        
    