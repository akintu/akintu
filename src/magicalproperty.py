#!/usr/bin/python

import sys
import equipment
from dice import *
import onhiteffect

# magicalproperty.py
# Author: Devin Ekins -- G. Cube
#
# magicalproperty houses the logic and game logic behind all of the interesting
# facets of item creation, namely, the distribution of magical properties.
# The dictionary and individual helper methods are set up to apply very specific
# modifications to an equipping player and are not called explicitly.  These
# methods are more data than code, as they will be assigned into individual
# pieces of equipment which will have a bound variable used to call them.
#
# Magical Property generation is a complex heuristic task that involves
# thinning out the possible magical properties into a smaller subset of 
# available properties based on game rules followed by a guess-and-check
# pattern of trying to match randomly selected properties into an item
# until they fit perfectly with no IP (item points) remaining.
# This is not guaranteed to complete execution within a specific amount
# of time, but actual experienced runtimes have never caused more than
# a negligible delay.  I suspect the algorithm could fail to find an item
# within 20 seconds or so with about the same probability that a meteor will
# extinguish all life on the planet Earth, rendering the execution delay 
# of this process less noticable.
#

class MagicalProperty(object):

    fullList = []

    def __init__(self, argDict, item, name, counts=1):
        self.name = name
        self.prefix = argDict['prefix']
        self.suffix = argDict['suffix']
        self.weight = argDict['weight']
        self.cost = argDict['cost']
        if self.cost == 'Varies':
            if self.name == "Damage":
                self.cost = item.gradientPoints
            elif self.name == "DR":
                self.DR = item.DRGradientPoints
        self.effect = argDict['effect']
        self.max = argDict['max']
        self.doubled = argDict['doubled']
        self.exclusion = argDict['exclusion']
        self.categories = argDict['categories']
        self.goldMod = argDict['goldMod']
        self._counts = counts
        self.item = item

        self.itemIsTwoHanded = False
        if (isinstance(item, equipment.Weapon) and item.type == "Two Handed" or
           item.type == "Two-Handed"):
            self.itemIsTwoHanded = True


    @property
    def counts(self):
        ''' The public view of the counts of a property.  Some propreties
        are doubled on two-handed weapons; that is handled here.'''
        if self.doubled and self.itemIsTwoHanded:
            return min(self._counts * 2, self.max)
        return self._counts

    @counts.setter
    def counts(self, value):
        self._counts = value
        
    @staticmethod
    def generateProperties(item, ipScore):
        ''' Rolls a list of properties for a normal treasure chest,
        not a class specific one.
        Inputs:
          item -- the equipment to be given properties
          ipScore -- the ipScore rolled for this item (before bonusMod)
        Outputs:
          A list of property objects in no particular order.'''
        if not MagicalProperty.fullList:
            MagicalProperty.cacheList()
        ip = ipScore + int(item.bonusMod)
        if item.type == "Finger":
            ip *= 2
        elif item.type == "Neck":
            ip *= 3
        if ip <= 0:
            return []
        subList = MagicalProperty.getFilledList(item)
        #subList = MagicalProperty.adjustWeights(subList, item)
        totalWeight = MagicalProperty.getTotalWeight(subList)
        maxProperties = MagicalProperty.getMaxProperties(ip)
        #rounded = MagicalProperty.roundIp(ip)
        
        return MagicalProperty.rollProperties(subList, maxProperties, ip, totalWeight, item)

    @staticmethod
    def roundIp(ip):
        ''' Deprecated method for unecessary optimization in item creation.'''
        rounded = ip
        factor = 1
        if 9 <= rounded <= 29:
            factor = 2
            if rounded % 2 == 1:
                rounded -= 1
        elif 30 <= rounded <= 89:
            factor = 3
            if rounded % 3 == 1:
                rounded -= 1
            elif rounded % 3 == 2:
                rounded += 1
        elif 90 <= rounded:
            factor = 5
            if rounded % 5 == 1:
                rounded -= 1
            elif rounded % 5 == 2:
                rounded -= 2
            elif rounded % 5 == 3:
                rounded += 2
            elif rounded % 5 == 4:
                rounded += 1
        return (rounded, factor)
        
    @staticmethod
    def getMaxProperties(ip):
        ''' Method uses game rules to determine how many properties
        a weapon or armor should have on it according to its overall IP
        value. '''
        if ip <= 4:
            return 1
        elif ip <= 9:
            return 2
        elif ip <= 16:
            return 3
        elif ip <= 25:
            return 4
        elif ip > 25:
            return 5
            
    @staticmethod
    def setErrorThreshold(ip):
        ''' Deprecated method for unnecessary optimization. '''
        if ip < 30:
            return 3
        elif ip < 70:
            return 4
        else:
            return 5
            
    @staticmethod
    def rollProperties(subList, maxListSize, givenIp, totalWeight, item):
        ''' Beast of a method that takes an item and its potential, as 
        represented by its parameters (described below) and pseudo-randomly
        selects which properties are assigned to the item.
        INPUTS:
          subList -- A list of magical properties that are valid for this item.
          maxListSize -- An int representing how many properties should exist on this item.
          givenIp -- An int representing the potential power of this item based on game
                     rules and item/treasure chest level.
          totalWeight -- An int representing the total weighting of all magical properties
                         int the sublist of the total list
                         defined elsewhere in this module.
          item -- The actual piece of Equipment (Weapon, Armor) that will have
                  its properties determined here.
        OUTPUTS:
          A list of chosen magical properties to be assigned to this Equipment.'''
        errorThreshold = MagicalProperty.setErrorThreshold(givenIp)
        chosenList = []
        position = 0
        attempts = 0
        ip = givenIp
        #ip = givenIpTuple[0]
        #factor = givenIpTuple[1]
        while( ip > 0 ):
            if attempts > 20:
                # if givenIp - ip <= errorThreshold:
                    # print ">>>>>>>> Giving up on exact item creation; difference = " + str(givenIp - ip) + " <<<<<<<<<<<<<<<"
                    # break
                ip = givenIp
                chosenList = []
                position = 0
                attempts = 0 
            if (len(chosenList) < maxListSize):
                dieRoll = Dice.roll(1, totalWeight)
                possibleProperty = MagicalProperty.selection(subList, dieRoll)
                #print "Ip to match: " + str(ip) + " IP of " + possibleProperty[0] + " = " + str(possibleProperty[1]['cost'])

                chosenNames = [x.name for x in chosenList]
                if possibleProperty[0] in chosenNames:
                    continue

                thisIp = possibleProperty[1]['cost']
                if possibleProperty[0] == "DR":
                    thisIp = item.DRGradientPoints
                    #print "DR Gradient points = " + str(thisIp)
                    if item.DRGradientPoints == 0:
                        continue
                elif possibleProperty[0] == "Damage":
                    thisIp = int(item.gradientPoints)
                    #print "Damage Gradient points = " + str(thisIp)
                if thisIp > ip:
                    continue
                else:
                    ip -= thisIp
                    property = MagicalProperty(possibleProperty[1], item, possibleProperty[0])
                    chosenList.append(property)
            else:
                if position >= len(chosenList):
                    attempts += 1
                    position = Dice.roll(0, len(chosenList) - 1)
                currentProperty = chosenList[position]
                thisIp = currentProperty.cost
                if thisIp == "Varies":
                    if currentProperty.name == "DR":
                        thisIp = item.DRGradientPoints
                    elif currentProperty.name == "Damage":
                        thisIp = item.gradientPoints
                if thisIp > ip or (currentProperty.max and currentProperty.counts >= currentProperty.max):
                    position += 1
                    attempts += 1
                else:
                    ip -= thisIp
                    currentProperty.counts += 1
                    position = Dice.roll(0, len(chosenList) - 1)
                    #print currentProperty.name + " counts " + str(currentProperty.counts)
        #print ">>>>>>>>>>>> ip = " + `givenIp` + " <<<<<<<<<<<<<<<<<<<"
        return chosenList


    @staticmethod
    def selection(subList, dieRoll):
        ''' Select an individual property from all properties supplied in
        its subset list (sublist).'''
        remaining = dieRoll
        for prop in subList:
            currentWeight = prop[1]['weight']
            remaining -= currentWeight
            if remaining <= 0:
                return prop

    @staticmethod
    def getTotalWeight(subList):
        ''' Calculates the total weight of all defined magical properties in
        this subset list.'''
        total = 0
        for prop in subList:
            total += prop[1]['weight']
        return total

    @staticmethod
    def cacheList():
        ''' Store a master list of all magical property objects from this
            modules master dictionary.  Should only be performed once
            per execution of Akintu.'''
        for key, value in MagicalProperty.allProperties.iteritems():
            current = [key, value]
            MagicalProperty.fullList.append(current)

    @staticmethod
    def getFilledList(item):
        ''' Generates a sublist of properties appropriate for the equipment
        type supplied.  For instance, Armor should not increase damage, and
        weapons should not increase DR.'''
        subList = []
        if isinstance(item, equipment.Armor):
            subList.extend([prop for prop in MagicalProperty.fullList
                            if prop[1]['exclusion'] != "Weapon Only" and
                               prop[1]['exclusion'] != "Melee Weapon Only" and
                               prop[1]['exclusion'] != "Ranged Weapon Only"])
        elif isinstance(item, equipment.Weapon):
            if item.range == 1:
                subList.extend([prop for prop in MagicalProperty.fullList if
                                prop[1]['exclusion'] != "Armor Only" and
                                prop[1]['exclusion'] != "Ranged Weapon Only"])
            else:
                subList.extend([prop for prop in MagicalProperty.fullList if
                                prop[1]['exclusion'] != "Armor Only" and
                                prop[1]['exclusion'] != "Melee Weapon Only"])
        return subList

    @staticmethod
    def adjustWeights(subList, item):
        ''' Deprecated method assigning particular properties to certain kinds
        of weapons/armor according to preset values in the data file.  Was moved
        to a Tier 4 feature when the algorithmic complexity made it impractical
        to delve into before Tier 3 release. '''
        print item.name
        for prop in subList:
            for tendency in item.bonusTendencyList:
                tName = tendency.split(",")[0]
                tAmount = int(tendency.split(",")[1])
                #print "tName " + tName + " tAmount " + str(tAmount)
                if tName == prop[0] or tName in prop[1]['categories']:
                    print prop[0] + " " + str(prop[1]['weight']) + " " + str(1 + float(tAmount) / 100)
                    prop[1]['weight'] = round(prop[1]['weight'] * (1 + float(tAmount) / 100))
        return subList
        
    def _doNothing(self, *args, **kwargs):
        '''The best method ever; it knows exactly what you are thinking
        at the moment of execution and then performs that action.  It 
        instantaneously reverses the action afterward, leaving nothing but
        awe in its wake.'''
        pass
        
    def _AP(self, owner, reverse=False):
        APIncrease = min(self.max, self.counts)
        if not reverse:
            owner.equipmentAP += APIncrease
        else:
            owner.equipmentAP -= APIncrease

    def _allAccuracy(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentMeleeAccuracy += bonus
            owner.equipmentRangedAccuracy += bonus
        else:
            owner.equipmentMeleeAccuracy -= bonus
            owner.equipmentRangedAccuracy -= bonus

    def _armorPenetration(self, owner, reverse=False):
        bonus = 0.75 * self.counts
        if not reverse:
            owner.equipmentArmorPenetration += bonus
        else:
            owner.equipmentArmorPenetration -= bonus

    def _awareness(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentAwareness += bonus
        else:
            owner.equipmentAwareness -= bonus

    def _constitution(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentConstitution += bonus
        else:
            owner.equipmentConstitution -= bonus

    def _carryingCapacity(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentCarryingCapacity += bonus
        else:
            owner.equipmentCarryingCapacity -= bonus

    def _criticalHitChance(self, owner, reverse=False):
        bonus = self.counts * 0.50
        if not reverse:
            owner.equipmentCriticalChance += bonus
        else:
            owner.equipmentCriticalChance -= bonus

    def _criticalHitMagnitude(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentCriticalMagnitude += bonus
        else:
            owner.equipmentCriticalMagnitude -= bonus

    def _cunning(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentCunning += bonus
        else:
            owner.equipmentCunning -= bonus

    def _damage(self, owner, reverse=False):
        if self.item.gradientPoints == 0:
            raise TypeError("Cannot increase damage on item: " + str(self.item.name) + ".")
        if not reverse:
            self.item.damageMinBonus += self.counts * int(self.item.gradientMin)
            self.item.damageMaxBonus += self.counts * int(self.item.gradientMax)

    def _DR(self, owner, reverse=False):
        if self.item.DRGradientPoints == 0:
            raise TypeError("Cannot increase DR on item: " + str(self.item.name) + ".")
        if not reverse:
            self.item.DR += self.counts * self.item.DRGradient

    def _dexterity(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentDexterity += bonus
        else:
            owner.equipmentDexterity -= bonus

    def _dodge(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentDodge += bonus
        else:
            owner.equipmentDodge -= bonus

    def _elementalEnhancementFire(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentFireBonusDamage += bonus
        else:
            owner.equipmentFireBonusDamage -= bonus

    def _elementalEnhancementCold(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentColdBonusDamage += bonus
        else:
            owner.equipmentColdBonusDamage -= bonus

    def _elementalEnhancementElectric(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentElectricBonusDamage += bonus
        else:
            owner.equipmentElectricBonusDamage -= bonus

    def _elementalEnhancementPoison(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentPoisonBonusDamage += bonus
        else:
            owner.equipmentPoisonBonusDamage -= bonus

    def _elementalEnhancementDivine(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentDivineBonusDamage += bonus
        else:
            owner.equipmentDivineBonusDamage -= bonus

    def _elementalEnhancementShadow(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentShadowBonusDamage += bonus
        else:
            owner.equipmentShadowBonusDamage -= bonus

    def _elementalEnhancementArcane(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentArcaneBonusDamage += bonus
        else:
            owner.equipmentArcaneBonusDamage -= bonus

    def _elementalDamageFire(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Fire")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Fire", self.counts)

    def _elementalDamageCold(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Cold")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Cold", self.counts)

    def _elementalDamageElectric(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Electric")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Electric",self.counts)

    def _elementalDamagePoison(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Poison")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Poison", self.counts)

    def _elementalDamageShadow(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Shadow")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Shadow", self.counts)

    def _elementalDamageDivine(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 3
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Divine")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Divine", self.counts)

    def _elementalDamageArcane(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyElementalDamage, "Arcane")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.removeOnHitEffect("ElementalDamage Arcane", self.counts)

    def _elementalResistanceFire(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentFireResistance += bonus
        else:
            owner.equipmentFireResistance -= bonus

    def _elementalResistanceCold(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentColdResistance += bonus
        else:
            owner.equipmentColdResistance -= bonus

    def _elementalResistanceElectric(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentElectricResistance += bonus
        else:
            owner.equipmentElectricResistance -= bonus

    def _elementalResistancePoison(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentPoisonResistance += bonus
        else:
            owner.equipmentPoisonResistance -= bonus

    def _elementalResistanceDivine(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentDivineResistance += bonus
        else:
            owner.equipmentDivineResistance -= bonus

    def _elementalResistanceShadow(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentShadowResistance += bonus
        else:
            owner.equipmentShadowResistance -= bonus

    def _elementalResistanceArcane(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentArcaneResistance += bonus
        else:
            owner.equipmentArcaneResistance -= bonus

    def _HP(self, owner, reverse=False):
        bonus = self.counts * 3
        if not reverse:
            owner.equipmentHP += bonus
        else:
            owner.equipmentHP -= bonus

    def _intuition(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentIntuition += bonus
        else:
            owner.equipmentIntuition -= bonus

    def _magicResist(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentMagicResist += bonus
        else:
            owner.equipmentMagicResist -= bonus

    def _MP(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentMP += bonus
        else:
            owner.equipmentMP -= bonus

    def _manaOnImpact(self, owner, reverse=False):
        pass
        # TODO

    def _meleeAccuracy(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentMeleeAccuracy += bonus
        else:
            owner.equipmentMeleeAccuracy -= bonus

    def _might(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentMight += bonus
        else:
            owner.equipmentMight -= bonus

    def _movementBonus(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentMovementTiles += bonus
        else:
            owner.equipmentMovementTiles -= bonus

    def _piety(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentPiety += bonus
        else:
            owner.equipmentPiety -= bonus

    def _poisonTolerance(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentPoisonTolerance += bonus
        else:
            owner.equipmentPoisonTolerance -= bonus

    def _potionEffectiveness(self, owner, reverse=False):
        bonus = self.counts * 4
        if not reverse:
            owner.equipmentPotionEffect += bonus
        else:
            owner.equipmentPotionEffect -= bonus

    def _rangedAccuracy(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentRangedAccuracy += bonus
        else:
            owner.equipmentRangedAccuracy -= bonus

    def _regenerationHP(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.HPRegen += bonus
        else:
            owner.HPRegen -= bonus

    def _regenerationMP(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.MPRegen += bonus
        else:
            owner.MPRegen -= bonus

    def _shopkeeperBonus(self, owner, reverse=False):
        bonus = self.counts * 0.5
        if not reverse:
            owner.equipmentShopBonus += bonus
        else:
            owner.equipmentShopBonus -= bonus

    def _sorcery(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentSorcery += bonus
        else:
            owner.equipmentSorcery -= bonus

    def _spellpower(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentSpellpower += bonus
        else:
            owner.equipmentSpellpower -= bonus

    def _strength(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentStrength += bonus
        else:
            owner.equipmentStrength -= bonus

    def _trapAvoidance(self, owner, reverse=False):
        if not reverse:
            owner.equipmentTrapEvade += self.counts
        else:
            owner.equipmentTrapEvade -= self.counts

    def _registerAcidic(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyAcidic)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerEvil(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyEvil)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerHoly(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyHoly)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerIgnite(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyIgnite)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerSlowing(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applySlowing)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerSpellhunger(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applySpellhunger)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerStunning(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyStunning)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerMinorBleeding(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyMinorBleeding)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerModerateBleeding(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyModerateBleeding)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerSeriousBleeding(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applySeriousBleeding)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerHealthSteal(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyHealthSteal)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerManaSteal(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyManaSteal)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerToxic(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyToxic)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningFire(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningFire)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningCold(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningCold)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningElectric(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningElectric)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningPoison(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningPoison)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningDivine(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningDivine)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningShadow(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningShadow)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningArcane(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.OnHitEffect.applyWeakeningArcane)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)



    allProperties = {
        'AP':
            {
            'weight' : 4,
            'cost' : 9,
            'effect' : _AP,
            'max' : 5,
            'doubled' : False,
            'exclusion' : None,
            'categories' : [],
            'goldMod' : 200,
            'prefix' : 'Active',
            'suffix' : 'of Action'
            },
        'All Accuracy':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _allAccuracy,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Accuracy'],
            'goldMod' : 35,
            'prefix' : 'Precise',
            'suffix' : 'of Precision'
            },
        'Armor Penetration':
            {
            'weight' : 10,
            'cost' : 2,
            'effect' : _armorPenetration,
            'max' : None,
            'doubled' : True,
            'exclusion' : 'Weapon Only',
            'categories' : [],
            'goldMod' : 30,
            'prefix' : 'Carving',
            'suffix' : 'of Perforation'
            },
        'Awareness':
            {
            'weight' : 8,
            'cost' : 1,
            'effect' : _awareness,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Armor Only',
            'categories' : ['Thief', 'Ranger'],
            'goldMod' : 12,
            'prefix' : 'Alert',
            'suffix' : 'of Perception'
            },
        'Constitution':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _constitution,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Fighter'],
            'goldMod' : 30,
            'prefix' : 'Hearty',
            'suffix' : 'of Constitution'
            },
        'Carrying Capacity':
            {
            'weight' : 2,
            'cost': 1,
            'effect' : _carryingCapacity,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Wizard'],
            'goldMod' : 12,
            'prefix' : 'Uplifting',
            'suffix' : 'of Packing'
            },
        'Critical Hit Chance':
            {
            'weight' : 8,
            'cost' : 1,
            'effect' : _criticalHitChance,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Thief', 'Critical'],
            'goldMod' : 16,
            'prefix' : 'Exact',
            'suffix' : 'of Eviscerating'
            },
        'Critical Hit Magnitude':
            {
            'weight' : 7,
            'cost' : 1,
            'effect' : _criticalHitMagnitude,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Critical'],
            'goldMod' : 14,
            'prefix' : 'Deadly',
            'suffix' : 'of Death'
            },
        'Cunning':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _cunning,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Thief'],
            'goldMod' : 35,
            'prefix' : 'Clever',
            'suffix' : 'of Cunning'
            },
        'Damage':
            {
            'weight' : 110,
            'cost' : 'Varies',
            'effect' : _damage,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : [],
            'goldMod' : 40,
            'prefix' : 'Masterpiece',
            'suffix' : 'of Mastery'
            },
        'DR':
            {
            'weight' : 110,
            'cost' : 'Varies',
            'effect' : _DR,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : [],
            'goldMod' : 40,
            'prefix' : 'Masterpiece',
            'suffix' : 'of Mastery'
            },
        'Dexterity':
            {
            'weight' : 8,
            'cost' : 3,
            'effect' : _dexterity,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Ranger', 'Thief'],
            'goldMod' : 35,
            'prefix' : 'Adroit',
            'suffix' : ' of Dexterity'
            },
        'Dodge':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _dodge,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Thief'],
            'goldMod' : 12,
            'prefix' : 'Evasive',
            'suffix' : 'of Agility'
            },
        'Elemental Enhancement: Fire':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _elementalEnhancementFire,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 12,
            'prefix' : 'Warm',
            'suffix' : 'of Warmth'
            },
        'Elemental Enhancement: Cold':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _elementalEnhancementCold,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 12,
            'prefix' : 'Chilled',
            'suffix' : 'of Frost'
            },
        'Elemental Enhancement: Electric':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _elementalEnhancementElectric,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 12,
            'prefix' : 'Static',
            'suffix' : 'of Sparks'
            },
        'Elemental Enhancement: Poison':
            {
            'weight' : 3,
            'cost' : 1,
            'effect' : _elementalEnhancementPoison,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting', 'Thief'],
            'goldMod' : 12,
            'prefix' : 'Natural',
            'suffix' : 'of Nature'
            },
        'Elemental Enhancement: Shadow':
            {
            'weight' : 3,
            'cost' : 1,
            'effect' : _elementalEnhancementShadow,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting', 'Thief'],
            'goldMod' : 12,
            'prefix' : 'Dark',
            'suffix' : 'of the Deep'
            },
        'Elemental Enhancement: Divine':
            {
            'weight' : 3,
            'cost' : 1,
            'effect' : _elementalEnhancementDivine,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 15,
            'prefix' : 'Blessed',
            'suffix' : 'of Blessings'
            },
        'Elemental Enhancement: Arcane':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _elementalEnhancementArcane,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 10,
            'prefix' : 'Mystical',
            'suffix' : 'of Thought'
            },
        'Elemental Damage: Fire':
            {
            'weight' : 10,
            'cost' : 2,
            'effect' : _elementalDamageFire,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage'],
            'goldMod' : 45,
            'prefix' : 'Burning',
            'suffix' : 'of Fire'
            },
        'Elemental Damage: Cold':
            {
            'weight' : 10,
            'cost' : 2,
            'effect' : _elementalDamageCold,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage'],
            'goldMod' : 45,
            'prefix' : 'Frigid',
            'suffix' : 'of the North'
            },
        'Elemental Damage: Electric':
            {
            'weight' : 10,
            'cost' : 2,
            'effect' : _elementalDamageElectric,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage'],
            'goldMod' : 45,
            'prefix' : 'Electric',
            'suffix' : 'of Voltage'
            },
        'Elemental Damage: Poison':
            {
            'weight' : 10,
            'cost' : 2,
            'effect' : _elementalDamagePoison,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage'],
            'goldMod' : 45,
            'prefix' : 'Venom',
            'suffix' : 'of Poison'
            },
        'Elemental Damage: Divine':
            {
            'weight' : 5,
            'cost' : 4,
            'effect' : _elementalDamageFire,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage'],
            'goldMod' : 60,
            'prefix' : 'Divine',
            'suffix' : 'of the Priest'
            },
        'Elemental Damage: Shadow':
            {
            'weight' : 10,
            'cost' : 2,
            'effect' : _elementalDamageShadow,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage'],
            'goldMod' : 45,
            'prefix' : 'Unholy',
            'suffix' : 'of Shadow'
            },
        'Elemental Damage: Arcane':
            {
            'weight' : 8,
            'cost' : 2,
            'effect' : _elementalDamageArcane,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['Elemental_Damage', 'Wizard'],
            'goldMod' : 45,
            'prefix' : "Mage's",
            'suffix' : 'of the Arcane'
            },
        'Elemental Resistance : Fire':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _elementalResistanceFire,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 12,
            'prefix' : 'Dragonscale',
            'suffix' : 'of Fire Warding'
            },
        'Elemental Resistance : Cold':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _elementalResistanceCold,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 12,
            'prefix' : 'Drakescale',
            'suffix' : 'of Cold Warding'
            },
        'Elemental Resistance : Electric':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _elementalResistanceElectric,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 12,
            'prefix' : 'Wyrmscale',
            'suffix' : 'of Electric Warding'
            },
        'Elemental Resistance : Poison':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _elementalResistancePoison,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 10,
            'prefix' : 'Snakeskin',
            'suffix' : 'of Poison Warding'
            },
        'Elemental Resistance : Divine':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _elementalResistanceDivine,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 12,
            'prefix' : 'Prayer',
            'suffix' : 'of Divine Warding'
            },
        'Elemental Resistance : Shadow':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _elementalResistanceShadow,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 12,
            'prefix' : 'Demonhide',
            'suffix' : 'of Shadow Warding'
            },
        'Elemental Resistance : Arcane':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _elementalResistanceArcane,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : ['Elemental_Resist', 'Defense'],
            'goldMod' : 12,
            'prefix' : 'Ethereal',
            'suffix' : 'of Arcane Warding'
            },
        'HP':
            {
            'weight' : 20,
            'cost' : 2,
            'effect' : _HP,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Fighter', 'Defense'],
            'goldMod' : 30,
            'prefix' : 'Stout',
            'suffix' : 'of the Tortoise'
            },
        'Intuition':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _intuition,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : [],
            'goldMod' : 10,
            'prefix' : 'Intuitive',
            'suffix' : 'of Elucidation'
            },
        'Magic Resist':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _magicResist,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Defense'],
            'goldMod' : 12,
            'prefix' : "Sage's",
            'suffix' : 'of the Council'
            },
        'MP':
            {
            'weight' : 12,
            'cost' : 3,
            'effect' : _MP,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard'],
            'goldMod' : 50,
            'prefix' : 'Wellspring',
            'suffix' : 'of Deep Thought'
            },
        'Melee Accuracy':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _meleeAccuracy,
            'max' : None,
            'doubled' : True,
            'exclusion' : "Melee Weapon Only",
            'categories' : ['Fighter', 'Thief', 'Accuracy'],
            'goldMod' : 12,
            'prefix' : 'Fine',
            'suffix' : 'of Striking'
            },
        'Might':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _might,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Fighter', 'Ranger'],
            'goldMod' : 12,
            'prefix' : 'Mighty',
            'suffix' : 'of Might'
            },
        'Movement Bonus':
            {
            'weight' : 2,
            'cost' : 20,
            'effect' : _movementBonus,
            'max' : None,
            'doubled' : False,
            'exclusion' : "Armor Only",
            'categories' : ['Movement'],
            'goldMod' : 2000,
            'prefix' : 'Swift',
            'suffix' : 'of Alacrity'
            },
        'Piety':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _piety,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard'],
            'goldMod' : 30,
            'prefix' : 'Pious',
            'suffix' : 'of the Devout'
            },
        'Poison Tolerance':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _poisonTolerance,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : [],
            'goldMod' : 12,
            'prefix' : 'Tolerant',
            'suffix' : 'of Immunity'
            },
        'Potion Effectiveness':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _potionEffectiveness,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : [],
            'goldMod' : 20,
            'prefix' : 'Strange',
            'suffix' : 'of Metabolism'
            },
        'Ranged Accuracy':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _rangedAccuracy,
            'max' : None,
            'doubled' : True,
            'exclusion' : "Ranged Weapon Only",
            'categories' : ['Ranger', 'Accuracy'],
            'goldMod' : 12,
            'prefix' : 'Ornate',
            'suffix' : 'of Elegance'
            },
        'Regeneration: HP':
            {
            'weight' : 5,
            'cost' : 6,
            'effect' : _regenerationHP,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Defense'],
            'goldMod' : 100,
            'prefix' : 'Regenerating',
            'suffix' : 'of the Lizard'
            },
        'Regeneration MP':
            {
            'weight' : 4,
            'cost' : 7,
            'effect' : _regenerationMP,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard'],
            'goldMod' : 135,
            'prefix' : 'Rejuvinating',
            'suffix' : 'of the Owl'
            },
        'Shopkeeper Bonus':
            {
            'weight' : 3,
            'cost' : 2,
            'effect' : _shopkeeperBonus,
            'max' : 40, # Total +40%
            'doubled' : True,
            'exclusion' : None,
            'categories': [],
            'goldMod' : 25,
            'prefix' : 'Thrifty',
            'suffix' : 'of Thrift'
            },
        'Sorcery':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _sorcery,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard'],
            'goldMod' : 30,
            'prefix' : "Magister's",
            'suffix' : 'of Sorcery'
            },
        'Spellpower':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _spellpower,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard'],
            'goldMod' : 12,
            'prefix' : 'Spellbound',
            'suffix' : 'of Power'
            },
        'Strength':
            {
            'weight' : 8,
            'cost' : 3,
            'effect' : _strength,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Fighter', 'Ranger'],
            'goldMod' : 30,
            'prefix' : 'Brave',
            'suffix' : 'of Strength'
            },
        'Trap Avoidance':
            {
            'weight' : 8,
            'cost' : 1,
            'effect' : _trapAvoidance,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Thief', 'Ranger'],
            'goldMod' : 12,
            'prefix' : 'Cautious',
            'suffix' : 'of Reflexes'
            },
        'Acidic':
            {
            'weight' : 5,
            'cost' : 2,
            'effect' : _registerAcidic,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 12,
            'prefix' : 'Acidic',
            'suffix' : 'of Acid'
            },
        'Evil':
            {
            'weight' : 2,
            'cost' : 10,
            'effect' : _registerEvil,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 180,
            'prefix' : 'Evil',
            'suffix' : 'of the Devil'
            },
        'Holy':
            {
            'weight' : 2,
            'cost' : 10,
            'effect' : _registerHoly,
            'max' : 30,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 180,
            'prefix' : 'Holy',
            'suffix' : 'of Angels'
            },
        'Ignite':
            {
            'weight' : 5,
            'cost' : 7,
            'effect' : _registerIgnite,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 55,
            'prefix' : 'Igniting',
            'suffix' : 'of Flames'
            },
        'Slowing':
            {
            'weight' : 5,
            'cost' : 2,
            'effect' : _registerSlowing,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 35,
            'prefix' : 'Slowing',
            'suffix' : 'of Fatigue'
            },
        'Spellhunger':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _registerSpellhunger,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 12,
            'prefix' : 'Spellhunger',
            'suffix' : 'of the Void'
            },
        'Stunning':
            {
            'weight' : 5,
            'cost' : 5,
            'effect' : _registerStunning,
            'max' : 20,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod': 45,
            'prefix' : 'Stunning',
            'suffix' : 'of Concussion'
            },
        'Minor Bleeding':
            {
            'weight' : 5,
            'cost' : 2,
            'effect' : _registerMinorBleeding,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 18,
            'prefix' : 'Thorny',
            'suffix' : 'of Bleeding'
            },
        'Moderate Bleeding':
            {
            'weight' : 4,
            'cost' : 5,
            'effect' : _registerModerateBleeding,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 60,
            'prefix' : 'Barbed',
            'suffix' : 'of Wounding'
            },
        'Serious Bleeding':
            {
            'weight' : 3,
            'cost' : 11,
            'effect' : _registerSeriousBleeding,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 200,
            'prefix' : 'Jagged',
            'suffix' : 'of Gutting'
            },
        'Health Steal':
            {
            'weight' : 5,
            'cost' : 2,
            'effect' : _registerHealthSteal,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 60,
            'prefix' : 'Vampiric',
            'suffix' : 'of Draining'
            },
        'Mana Steal':
            {
            'weight' : 5,
            'cost' : 3,
            'effect' : _registerManaSteal,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 50,
            'prefix' : 'Mysterious',
            'suffix' : 'of the Vortex'
            },
        'Toxic':
            {
            'weight' : 5,
            'cost' : 3,
            'effect' : _registerToxic,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 40,
            'prefix' : 'Toxic',
            'suffix' : 'of Illness'
            },
        'Weakening: Fire':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningFire,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Kindling',
            'suffix' : 'of Dehydration'
            },
        'Weakening: Cold':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningCold,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Frosty',
            'suffix' : 'of Frostbite'
            },
        'Weakening: Electric':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningElectric,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Magnetic',
            'suffix' : 'of Magnetism'
            },
        'Weakening: Poison':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningPoison,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Ancient',
            'suffix' : 'of Weakening'
            },
        'Weakening: Divine':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningDivine,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Judicious',
            'suffix' : 'of Judgement'
            },
        'Weakening: Shadow':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningShadow,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Tempting',
            'suffix' : 'of the Liar'
            },
        'Weakening: Arcane':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _registerWeakeningArcane,
            'max' : 100,
            'doubled' : False,
            'exclusion' : 'Weapon Only',
            'categories' : ['On Hit'],
            'goldMod' : 10,
            'prefix' : 'Confounding',
            'suffix' : 'of Confusion'
            }
    }
