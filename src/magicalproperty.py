#!/usr/bin/python

import sys
import equipment
from dice import *
import onhiteffect

class MagicalProperty(object):

    fullList = []

    def __init__(self, argDict, item, name, counts=1):
        self.name = name
        self.weight = argDict['weight']
        self.cost = argDict['cost']
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
        subList = MagicalProperty.adjustWeights(subList, item)
        totalWeight = MagicalProperty.getTotalWeight(subList)
        maxProperties = MagicalProperty.getMaxProperties(ip)
        
        return MagicalProperty.rollProperties(subList, maxProperties, ip, totalWeight, item)
        
    @staticmethod 
    def getMaxProperties(ip):
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
    def rollProperties(subList, maxListSize, givenIp, totalWeight, item):
        chosenList = []
        position = 0
        attempts = 0
        ip = givenIp
        while( ip > 0 ):
            if (len(chosenList) < maxListSize):
                dieRoll = Dice.roll(1, totalWeight)
                possibleProperty = MagicalProperty.selection(subList, dieRoll)
                print "Ip to match: " + str(ip) + " IP of " + possibleProperty[0] + " = " + str(possibleProperty[1]['cost'])
                
                chosenNames = [x.name for x in chosenList]
                if possibleProperty[0] in chosenNames:
                    continue
                    
                thisIp = possibleProperty[1]['cost']
                if thisIp > ip:
                    continue
                else: 
                    ip -= thisIp
                    property = MagicalProperty(possibleProperty[1], item, possibleProperty[0])
                    chosenList.append(property)
            else:
                if position >= len(chosenList):
                    if attempts > 10:
                        ip = givenIp
                        chosenList = []
                        position = 0 
                        continue
                    else: 
                        attempts += 1
                        position = Dice.roll(0, len(chosenList) - 1)
                currentProperty = chosenList[position]
                thisIp = currentProperty.cost
                if thisIp > ip or (currentProperty.max and currentProperty.counts >= currentProperty.max):
                    position += 1
                else:
                    ip -= thisIp
                    currentProperty.counts += 1
                    position = Dice.roll(0, len(chosenList) - 1)
                    print currentProperty.name + " counts " + str(currentProperty.counts)
        return chosenList
        
        
    @staticmethod
    def selection(subList, dieRoll):
        remaining = dieRoll
        for prop in subList:
            currentWeight = prop[1]['weight']
            remaining -= currentWeight
            if remaining <= 0:
                return prop
        
    @staticmethod
    def getTotalWeight(subList):
        total = 0
        for prop in subList:
            total += prop[1]['weight']
        return total
        
    @staticmethod
    def cacheList():
        for key, value in MagicalProperty.allProperties.iteritems():
            current = [key, value]
            MagicalProperty.fullList.append(current)        
        
    @staticmethod
    def getFilledList(item):
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
        for prop in subList:
            for tendency in item.bonusTendencyList:
                tName = tendency.split(",")[0]
                tAmount = int(tendency.split(",")[1])
                if tName == prop[0] or tName in prop[1]['categories']:
                    prop[1]['weight'] = round(prop[1]['weight'] * (1 + tAmount / 100))
        return subList                    
        
        
    def _AP(self, owner, reverse=False):
        APIncrease = max(self.max)
        if not reverse:
            owner.equipmentAP += APIncrease
        else:
            owner.equipmentAP -= APIncrease
        
    def _allAccuracy(self, owner, reverse=False):
        bonus = self.counts * 2
        if not reverse:
            owner.equipmentMeleeAccuracy += bonus
            owner.rangedMeleeAccuracy += bonus
        else:
            owner.equipmentMeleeAccuracy -= bonus
            owner.rangedMeleeAccuracy -= bonus        
        
    def _armorPenetration(self, owner, reverse=False):
        bonus = 0.5 * self.counts
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
            owner.equipment
        
    def _criticalHitChance(self, owner, reverse=False):
        bonus = self.counts * 0.50
        if not reverse:
            owner.equipmentCriticalChance += bonus
        else:
            owner.equipmentCriticalChance -= bonus
            
    def _criticalHitMagnitude(self, owner, reverse=False):
        bonus = self.counts
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
            raise TypeError("Cannot increase damage on item: " + str(self.item) + ".")
        if not reverse:
            item.damageMinBonus += self.counts * item.gradientMin
            item.damageMaxBonus += self.counts * item.gradientMax     
    
    def _DR(self, owner, reverse=False):
        if self.item.DRGradientPoints == 0:
            raise TypeError("Cannot increase DR on item: " + str(self.item) + ".")
        if not reverse:
            item.DR += self.counts * item.DRGradient
    
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
        bonus = self.counts
        if not reverse:
            owner.equipmentFireBonusDamage += bonus
        else:
            owner.equipmentFireBonusDamage -= bonus
            
    def _elementalEnhancementCold(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentColdBonusDamage += bonus
        else:
            owner.equipmentColdBonusDamage -= bonus    
    
    def _elementalEnhancementElectric(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentElectricBonusDamage += bonus
        else:
            owner.equipmentElectricBonusDamage -= bonus
    
    def _elementalEnhancementPoison(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentPoisonBonusDamage += bonus
        else:
            owner.equipmentPoisonBonusDamage -= bonus
    
    def _elementalEnhancementDivine(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentDivineBonusDamage += bonus
        else:
            owner.equipmentDivineBonusDamage -= bonus
    
    def _elementalEnhancementShadow(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentShadowBonusDamage += bonus
        else:
            owner.equipmentShadowBonusDamage -= bonus
    
    def _elementalEnhancementArcane(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentArcaneBonusDamage += bonus
        else:
            owner.equipmentArcaneBonusDamage -= bonus
    
    def _elementalDamageFire(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Fire")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Fire")

    def _elementalDamageCold(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Cold")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Cold")
            # TODO Write unregisterOnHitEffect method in PlayerCharacter class.
        
    def _elementalDamageElectric(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Electric")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Electric")

    def _elementalDamagePoison(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Poison")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Poison")
    
    def _elementalDamageShadow(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Shadow")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Shadow")
        
    def _elementalDamageDivine(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 3
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Divine")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Divine")

    def _elementalDamageArcane(self, owner, reverse=False):
        bonusMin = self.counts
        bonusMax = self.counts * 2
        pass
        if not reverse:
            hitEffect = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Arcane")
            owner.onHitEffects.append(hitEffect)
        else:
            owner.unregisterOnHitEffect(self.counts, onhiteffect.applyElementalDamage, "Arcane")
        
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
            
    def _identification(self, owner, reverse=False):
        bonus = self.counts
        if not reverse:
            owner.equipmentIdentification += bonus
        else:
            owner.equipmentIdentification -= bonus
            
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
            owner.eqiupmentMight += bonus
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
        bonus = self.counts / 2
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
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyAcidic)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerEvil(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyEvil)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
         
    def _registerHoly(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyHoly)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerIgnite(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyIgnite)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerSlowing(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applySlowing)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerSpellhunger(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applySpellhunger)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerStunning(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyStunning)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerMinorBleeding(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyMinorBleeding)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerModerateBleeding(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyModerateBleeding)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerSeriousBleeding(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applySeriousBleeding)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)   
         
    def _registerHealthSteal(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyHealthSteal)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerManaSteal(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyManaSteal)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerToxic(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyToxic)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerWeakeningFire(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningFire)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)

    def _registerWeakeningCold(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningCold)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)            
            
    def _registerWeakeningElectric(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningElectric)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerWeakeningPoison(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningPoison)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerWeakeningDivine(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningDivine)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerWeakeningShadow(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningShadow)
            owner.onHitEffects.append(onHit)
        else:
            owner.removeOnHitEffect(self.name, self.counts)
            
    def _registerWeakeningArcane(self, owner, reverse=False):
        if not reverse:
            onHit = onhiteffect.OnHitEffect(self.counts, onhiteffect.applyWeakeningArcane)
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
            'goldMod' : 200
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
            'goldMod' : 35
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
            'goldMod' : 30
            },
        'Awareness':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _awareness,
            'max' : None,
            'doubled' : False,
            'exclusion': 'Armor Only',
            'categories' : ['Thief', 'Ranger'],
            'goldMod' : 12
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
            'goldMod' : 30
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
            'goldMod' : 12
            },
        'Critical Hit Chance':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _criticalHitChance,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Thief', 'Critical'],
            'goldMod' : 15
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
            'goldMod' : 15
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
            'goldMod' : 35
            },
        'Damage':
            {# TODO, apply on item generation, adjust gold value and remove from list. 
            'weight' : 50,
            'cost' : 'Varies',
            'effect' : _damage,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Damage Gradient',
            'categories' : [],
            'goldMod' : 40
            },
        'DR':
            {# TODO, apply on item generation, adjust gold value and remove from list. 
            'weight' : 50,
            'cost' : 'Varies',
            'effect' : _DR,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'DR Gradient',
            'categories' : [],
            'goldMod' : 40
            },
        'Dexterity':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _dexterity,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Ranger', 'Thief'],
            'goldMod' : 35
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
            'goldMod' : 12
            },
        'Elemental Enhancement: Fire':
            {
            'weight' : 7,
            'cost' : 1,
            'effect' : _elementalEnhancementFire,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 12
            },
        'Elemental Enhancement: Cold':
            {
            'weight' : 7,
            'cost' : 1,
            'effect' : _elementalEnhancementCold,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 12
            },        
        'Elemental Enhancement: Electric':
            {
            'weight' : 7,
            'cost' : 1,
            'effect' : _elementalEnhancementElectric,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 12
            },            
        'Elemental Enhancement: Poison':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _elementalEnhancementPoison,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting', 'Thief'],
            'goldMod' : 12
            },            
        'Elemental Enhancement: Shadow':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _elementalEnhancementShadow,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting', 'Thief'],
            'goldMod' : 12
            },            
        'Elemental Enhancement: Divine':
            {
            'weight' : 4,
            'cost' : 1,
            'effect' : _elementalEnhancementDivine,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 15
            },
        'Elemental Enhancement: Arcane':
            {
            'weight' : 7,
            'cost' : 1,
            'effect' : _elementalEnhancementArcane,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard', 'Elemental_Casting'],
            'goldMod' : 10
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
            'goldMod' : 45
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
            'goldMod' : 45
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
            'goldMod' : 45
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
            'goldMod' : 45
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
            'goldMod' : 60
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
            'goldMod' : 45
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
            'goldMod' : 45
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
            'goldMod' : 12
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
            'goldMod' : 12
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
            'goldMod' : 12
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
            'goldMod' : 10
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
            'goldMod' : 12
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
            'goldMod' : 12
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
            'goldMod' : 12
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
            'goldMod' : 30
            },
        'Identification':
            {
            'weight' : 5,
            'cost' : 1,
            'effect' : _identification,
            'max' : None,
            'doubled' : False,
            'exclusion' : 'Armor Only',
            'categories' : [],
            'goldMod' : 10
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
            'goldMod' : 12
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
            'goldMod' : 50
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
            'goldMod' : 12
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
            'goldMod' : 12
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
            'goldMod' : 2000
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
            'goldMod' : 30
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
            'goldMod' : 12
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
            'goldMod' : 20
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
            'goldMod' : 12
            },
        'Regeneration: HP':
            {
            'weight' : 6,
            'cost' : 6,
            'effect' : _regenerationHP,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Defense'],
            'goldMod' : 100
            },
        'Regeneration MP':
            {
            'weight' : 5,
            'cost' : 7,
            'effect' : _regenerationMP,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Wizard'],
            'goldMod' : 135
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
            'goldMod' : 25
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
            'goldMod' : 30
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
            'goldMod' : 12
            },
        'Strength':
            {
            'weight' : 10,
            'cost' : 3,
            'effect' : _strength,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Fighter', 'Ranger'],
            'goldMod' : 30
            },
        'Trap Avoidance':
            {
            'weight' : 10,
            'cost' : 1,
            'effect' : _trapAvoidance,
            'max' : None,
            'doubled' : True,
            'exclusion' : None,
            'categories' : ['Thief', 'Ranger'],
            'goldMod' : 12
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
            'goldMod' : 12
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
            'goldMod' : 180
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
            'goldMod' : 180
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
            'goldMod' : 55
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
            'goldMod' : 35
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
            'goldMod' : 12
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
            'goldMod': 45
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
            'goldMod' : 18
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
            'goldMod' : 60
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
            'goldMod' : 200
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
            'goldMod' : 60
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
            'goldMod' : 50
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
            'goldMod' : 40
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
            'goldMod' : 10
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
            'goldMod' : 10
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
            'goldMod' : 10
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
            'goldMod' : 10
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
            'goldMod' : 10
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
            'goldMod' : 10
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
            'goldMod' : 10
            }
    }