#!/usr/bin/python

from pygame.locals import *

import sys
import equippeditems
import equipment
import person as p
import spell
import passiveability
import ability
import inventory
import trait
import math
import consumable

class PlayerCharacter(p.Person):

    expRequiredForLevel = {1 : 100, 2 : 250, 3 : 500, 4 : 900, 5 : 1700}
    demoExpRequiredForLevel = {1 : 10, 2 : 25, 3 : 50, 4 : 90, 5 : 170}
    LEVEL_MAX = 5

    def __init__(self, argDict, name="Guy Threepwood", new=True, ironman=False, hardcore=False):
        p.Person.__init__(self, argDict)

        self.team = "Players"
        self.name = name
        if name in ["Kyle Rich", "Devin Ekins", "Joshua Belcher", "Colton Myers"]:
            self.name = "Awesome Dude"
        elif name == "jabelch":
            self.name = "Flagrant Noob"
        elif name == "yourself":
            self.name = "Ugly Grue"
            
        self.level = 1
        self._experience = 0
        self.ironman=ironman
        self.hardcore=hardcore
        
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
        self._arcaneArcherManaRegenBase = None
        if (self.characterClass == "Arcane Archer"):
            self._arcaneArcherManaRegenBase = 6

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

        # Levelup stats
        self.levelupStrength = float(p.Person.setFrom(argDict, 'levelupStrength', p.Person.ERROR))
        self.levelupDexterity = float(p.Person.setFrom(argDict, 'levelupDexterity', p.Person.ERROR))
        self.levelupCunning = float(p.Person.setFrom(argDict, 'levelupCunning', p.Person.ERROR))
        self.levelupSorcery = float(p.Person.setFrom(argDict, 'levelupSorcery', p.Person.ERROR))
        self.levelupPiety = float(p.Person.setFrom(argDict, 'levelupPiety', p.Person.ERROR))
        self.levelupConstitution = float(p.Person.setFrom(argDict, 'levelupConstitution', p.Person.ERROR))
        self.levelupHP = float(p.Person.setFrom(argDict, 'levelupHP', p.Person.ERROR))
        self.levelupMP = float(p.Person.setFrom(argDict, 'levelupMP', p.Person.ERROR))

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

        if new:
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
        if new:
            self.registerBasicAttacks()
            for abil in ability.Ability.allAbilities:
                current = ability.Ability.allAbilities[abil]
                if current['class'] == self.baseClass or current['class'] == self.secondaryClass or current['class'] == self.characterClass or \
                (current['class'] == "Thief*" and self.baseClass == "Thief"):
                    if current['level'] == 1:
                        newAbil = ability.Ability(abil, self)
                        self.abilities.append(newAbil)

        self.passiveAbilities = []
        if new:
            for pAbil in passiveability.PassiveAbility.allContentByName:
                current = passiveability.PassiveAbility.allContentByName[pAbil]
                if current['class'] == self.baseClass or current['class'] == self.secondaryClass or current['class'] == self.characterClass or \
                (current['class'] == "Thief*" and self.baseClass == "Thief"):
                    if current['level'] == 1:
                        newPAbil = passiveability.PassiveAbility(pAbil, self)
                        self.passiveAbilities.append(newPAbil)

        self.traits = []

        # Items
        self.equippedItems = equippeditems.EquippedItems(None)
        self._baseInventoryCapacity = p.Person.setFrom(argDict, 'startingInventoryCapacity', 0)
        self._equipmentCarryingCapacity = 0
        if new:
            self.inventory = inventory.Inventory(ccName=self.characterClass)
            # Actually equip starting weapon/shield.  Won't work for two one-handed weapons.
            for item in self.inventory.allItems:
                if isinstance(item, equipment.Weapon):
                    self.equip(item)
                    break
            for item in self.inventory.allItems:
                if isinstance(item, equipment.Armor) and item.type == "Shield":
                    self.equip(item)
                    break
        else:
            self.inventory = inventory.Inventory()
        
        self.movesPerformed = [0,0]
        self.attacksPerformed = [0,0]
        # TODO: Need to update attacksPerformed each turn.  The previous turn's number of attacks is in position 0, this turn's
        # in position 1.  Need to also shift those at the end of each turn...
        
        self.remainingMovementTiles = 0
        
        #### Used for dual wielding mechanics ####
        self.lastUsedRating = None
        self.lastUsedCritMod = None
        self.lastUsedModifier = None

    def registerBasicAttacks(self):
        self.abilities.append(ability.Ability("Melee Attack", self))
        self.abilities.append(ability.Ability("Ranged Attack", self))

    def selectBasicAttack(self):
        if self.usingWeapon("Ranged"):
            for abil in self.abilities:
                if abil.name == "Ranged Attack":
                    return abil
        elif self.usingWeapon("Melee"):
            for abil in self.abilities:
                if abil.name == "Melee Attack":
                    return abil
        print "selectBasicAttack: Cannot find basic attack!!!"
        return None


    def getDetailTuple(self):
        '''Should be overriden by PlayerCharacters and other
        children.  Returns a tuple of information needed to reconstitute
        this Person object.
        First argument should represent which type of object this is.'''
        return ("Player", self.name, self.race, self.characterClass)

    def dehydrate(self):
        '''Will return a dehydration string for the abilities of this
        player character.'''
        longText = []
        longText.append(self.name)
        longText.append("&" + self.race)
        longText.append("&" + self.characterClass)
        longText.append("&" + `self.level`)
        longText.append("&" + `self.inventory.gold`)
        longText.append("&" + `self.experience`)
        longText.append("&" + `self.hardcore`)
        longText.append("&" + `self.ironman`)
        longText.append("@")
        for abil in self.abilities:
            longText.append("&" + abil.name)
        longText.append("@")
        for sp in self.spellList:
            longText.append("&" + sp.name)
        longText.append("@")
        for pas in self.passiveAbilities:
            longText.append("&" + pas.name)
        longText.append("@")
        for itm in self.inventory.allItems:
            longText.append("&" + itm.identifier)
        longText.append("@")
        for eq in self.equippedItems._allGear.values():
            if eq:
                longText.append("&" + eq.identifier)
        longText.append("@")
        for tr in self.traits:
            longText.append("&" + tr.name + `tr.rank`) 
        return ''.join(longText)
        
        
    def applyBonusDamage(self, dieRoll, element):
        if element == "Fire":
            dieRoll *= 1 + (float(self.totalFireBonusDamage) / 100)
        elif element == "Cold":
            dieRoll *= 1 + (float(self.totalColdBonusDamage) / 100)
        elif element == "Electric":
            dieRoll *= 1 + (float(self.totalElectricBonusDamage) / 100)
        elif element == "Poison":
            dieRoll *= 1 + (float(self.totalPoisonBonusDamage) / 100)
        elif element == "Shadow":
            dieRoll *= 1 + (float(self.totalShadowBonusDamage) / 100)
        elif element == "Divine":
            dieRoll *= 1 + (float(self.totalDivineBonusDamage) / 100)
        elif element == "Arcane":
            dieRoll *= 1 + (float(self.totalArcaneBonusDamage) / 100)
        return int(round(dieRoll))


    def getLevelupStats(self):
        '''Used to perform a levelup on a characters stats and return the 
        summary TileObject to be used in a tile display.'''
        roundUpStrength = sumRollsOver(self._baseStrength, self.levelupStrength)
        self._baseStrength += self.levelupStrength
        displayStrengthGain = int(math.floor(self.levelupStrength))
        if roundUpStrength:
            displayStrengthGain += 1
        
        roundUpDexterity = sumRollsOver(self._baseDexterity, self.levelupDexterity)
        self._baseDexterity += self.levelupDexterity
        displayDexterityGain = int(math.floor(self.levelupDexterity))
        if roundUpDexterity:
            displayDexterityGain += 1
        
        roundUpCunning = sumRollsOver(self._baseCunning, self.levelupCunning)
        self._baseCunning += self.levelupCunning
        displayCunningGain = int(math.floor(self.levelupCunning))
        if roundUpCunning:
            displayCunningGain += 1
        
        roundUpSorcery = sumRollsOver(self._baseSorcery, self.levelupSorcery)
        self._baseSorcery += self.levelupSorcery
        displaySorceryGain = int(math.floor(self.levelupSorcery))
        if roundUpSorcery:
            displaySorceryGain += 1
        
        roundUpPiety = sumRollsOver(self._basePiety, self.levelupPiety)
        self._basePiety += self.levelupPiety
        displayPietyGain = int(math.floor(self.levelupPiety))
        if roundUpPiety:
            displayPietyGain += 1
        
        roundUpConstitution = sumRollsOver(self._baseConstitution, self.levelupConstitution)
        self._baseConstitution += self.levelupConstitution
        displayConstitutionGain = int(math.floor(self.levelupConstitution))
        if roundUpConstitution:
            displayConstitutionGain += 1
        
        self._baseHP += self.levelupHP
        self._baseMP += self.levelupMP
        
        statsName = "Gained Statistics"
        statsImage = "./res/images/icons/stats.png"
        statsText = "Gained the following statistics:\n" + \
                    "Strength + " + `displayStrengthGain` + "\n" + \
                    "Dexterity + " + `displayDexterityGain` + "\n" + \
                    "Cunning + " + `displayCunningGain` + "\n" + \
                    "Sorcery + " + `displaySorceryGain` + "\n" + \
                    "Piety + " + `displayPietyGain` + "\n" + \
                    "Constitution + " + `displayConstitutionGain` + "\n" + \
                    "HP + " + `int(self.levelupHP)` + "    MP + " + `int(self.levelupMP)`
        statsTile = TileObject(statsName, statsImage, statsText)
        
        self.HP = self.totalHP
        self.MP = self.totalMP
        return statsTile
        
        
    def gainLevelUp(self, statsOnly=True):
        """Start the levelup process for acquiring a new level.  Only used 
        for automatic levelups.
        Inputs:
            None
        Outputs:
            None"""
        # Gain stats
        roundUpStrength = sumRollsOver(self._baseStrength, self.levelupStrength)
        self._baseStrength += self.levelupStrength
        displayStrengthGain = int(math.floor(self.levelupStrength))
        if roundUpStrength:
            displayStrengthGain += 1
        
        roundUpDexterity = sumRollsOver(self._baseDexterity, self.levelupDexterity)
        self._baseDexterity += self.levelupDexterity
        displayDexterityGain = int(math.floor(self.levelupDexterity))
        if roundUpDexterity:
            displayDexterityGain += 1
        
        roundUpCunning = sumRollsOver(self._baseCunning, self.levelupCunning)
        self._baseCunning += self.levelupCunning
        displayCunningGain = int(math.floor(self.levelupCunning))
        if roundUpCunning:
            displayCunningGain += 1
        
        roundUpSorcery = sumRollsOver(self._baseSorcery, self.levelupSorcery)
        self._baseSorcery += self.levelupSorcery
        displaySorceryGain = int(math.floor(self.levelupSorcery))
        if roundUpSorcery:
            displaySorceryGain += 1
        
        roundUpPiety = sumRollsOver(self._basePiety, self.levelupPiety)
        self._basePiety += self.levelupPiety
        displayPietyGain = int(math.floor(self.levelupPiety))
        if roundUpPiety:
            displayPietyGain += 1
        
        roundUpConstitution = sumRollsOver(self._baseConstitution, self.levelupConstitution)
        self._baseConstitution += self.levelupConstitution
        displayConstitutionGain = int(math.floor(self.levelupConstitution))
        if roundUpConstitution:
            displayConstitutionGain += 1
        
        self._baseHP += self.levelupHP
        self._baseMP += self.levelupMP
        
        self.HP = self.totalHP
        self.MP = self.totalMP
        
    def getLevelupSkillOptions(self):
        '''Returns a list of all of the skills this character
        may choose from upon earning its current level. Will return
        an empty list if no such abilities are available to be chosen.'''
        if self.level not in self.skillLevels:
            return []

        activeNames = [x for x in ability.Ability.allAbilities.keys()]
        actives = [x for x in activeNames if (ability.Ability.allAbilities[x]['class'] == self.baseClass or
                    ability.Ability.allAbilities[x]['class'] == self.secondaryClass or
                    (ability.Ability.allAbilities[x]['class'] == 'Ranger*' and self.baseClass == 'Ranger' and self.characterClass != 'Anarchist') or
                    (ability.Ability.allAbilities[x]['class'] == 'Thief*' and self.baseClass == 'Thief')) and
                    ability.Ability.allAbilities[x]['level'] <= self.level and 
                    ability.Ability.allAbilities[x]['level'] != 1 and
                    x not in [y.name for y in self.abilities]]
                    
        activeStubs = []
        for active in actives:
            activeStubs.append(ability.AbilityStub(active))          
                        
        return activeStubs
        
    def getLevelupTraitOptions(self):
        '''Returns a list of all the traits this character may
        either upgrade or select for the first time.'''
        if self.level == 1:
            return []
        # Get list of traits he/she doesn't already have.
        newTraitNames = [x for x in trait.Trait.allContentByName.keys()
                        if x not in [y.name for y in self.traits] and
                        (trait.Trait.allContentByName[x]['class'] == self.baseClass or 
                        trait.Trait.allContentByName[x]['class'] == self.secondaryClass)]
        rankAllowed = 0
        if self.level < 3:
            pass
        elif self.level < 5:
            rankAllowed = 1
        elif self.level < 7:
            rankAllowed = 2
        elif self.level >= 7:
            rankAllowed = 3
        upgradeTraitNames = [x.name for x in self.traits if x.rank <= rankAllowed]
        
        allTraitNames = upgradeTraitNames
        if len(self.traits) < 5:
            allTraitNames.extend(newTraitNames)
        
        traitStubs = []
        for tName in allTraitNames:
            traitStubs.append(trait.TraitStub(tName))    
        return traitStubs

                
    def getLevelupCombos(self):
        '''Returns a list of all the passive Abilities and combination abilities
        that this character gets upon this levelup.'''
        
        passiveNames = [x for x in passiveability.PassiveAbility.allContentByName.keys()]
        passives = [x for x in passiveNames 
                    if passiveability.PassiveAbility.allContentByName[x]['class'] == self.characterClass and
                    passiveability.PassiveAbility.allContentByName[x]['level'] == self.level]
                    
        passiveStubs = []
        for passive in passives:
            passiveStubs.append(passiveability.PassiveAbilityStub(passive))
                    
        activeNames = [x for x in ability.Ability.allAbilities.keys()]
        actives = [x for x in activeNames if ability.Ability.allAbilities[x]['class'] == self.characterClass and
                    ability.Ability.allAbilities[x]['level'] == self.level]
                    
        activeStubs = []
        for active in actives:
            activeStubs.append(ability.AbilityStub(active))
                    
        passiveStubs.extend(activeStubs)
        return passiveStubs
        
    def getLevelupSpellOptions(self):
        '''Returns a list of available spells to learn during this levelup.  Returns
        an empty list if this character does not learn spells.'''
        if self.level not in self.spellLevels:
            return []
        allowedSchools = ['Primal', 'Illusion', 'Mystic', 'Natural']
        if self.characterClass == 'Nightblade':
            allowedSchools.append('Bane')
        elif self.characterClass == 'Tactician':
            allowedSchools.append('Mental')
        elif self.characterClass == 'Spellsword':
            allowedSchools.append('Enchantment')
            
        allowedTier = 1
        if 5 <= self.level and self.level <= 8:
            allowedTier = 2
        elif 9 <= self.level and self.level <= 12:
            allowedTier = 3
        elif 13 <= self.level and self.level <= 16:
            allowedTier = 4
        elif 17 <= self.level and self.level <= 20:
            allowedTier = 5
            
        spellNames = [x for x in spell.Spell.allSpells.keys()
                    if spell.Spell.allSpells[x]['tier'] == allowedTier and 
                    spell.Spell.allSpells[x]['school'] in allowedSchools and
                    x not in [y.name for y in self.spellList]]
                
        spellsToSelect = []
        for spellName in spellNames:
            spellsToSelect.append(spell.SpellStub(spellName))
        
        return spellsToSelect
                
    @property
    def experience(self):
        return self._experience

    def getExpForNextLevel(self):
        if self.level == PlayerCharacter.LEVEL_MAX:
            return 0
        else:
            return PlayerCharacter.expRequiredForLevel[self.level]
        
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
            expForNext = self.getExpForNextLevel()
            self._experience += amount
            if self._experience >= expForNext:
                self._experience = expForNext
                #self.level += 1
            return self.level
        else:
            expForNext = PlayerCharacter.expRequiredForLevel[self.level]
            expForSecondNext = PlayerCharacter.expRequiredForLevel[self.level + 1]
            self._experience += amount
            if self._experience >= expForSecondNext:
                self._experience = expForSecondNext - 1
            if self._experience >= expForNext:
                pass
                #self.level += 1
            return self.level
        #TODO: Demo mode
        
    @property
    def totalOverallDamageBonus(self):
        """ Should be 0 for 0% by default.
            Would be 14 for 14% (not 1.14)
        """
        return int(self._baseOverallDamageBonus + self._equipmentOverallDamageBonus +
               self._statusOverallDamageBonus)

    @property
    def baseOverallDamageBonus(self):
        """ Should almost always be 0 for 0%."""
        return int(self._baseOverallDamageBonus)

    @baseOverallDamageBonus.setter
    def baseOverallDamageBonus(self, value):
        """ Set to ints not floats."""
        self._baseOverallDamageBonus = value

    @property
    def equipmentOverallDamageBonus(self):
        return int(self._equipmentOverallDamageBonus)

    @equipmentOverallDamageBonus.setter
    def equipmentOverallDamageBonus(self, value):
        self._equipmentOverallDamageBonus = value

    @property
    def statusOverallDamageBonus(self):
        return int(self._statusOverallDamageBonus)

    @statusOverallDamageBonus.setter
    def statusOverallDamageBonus(self, value):
        self._statusOverallDamageBonus = value

    @property
    def totalPoisonRatingBonus(self):
        """ The bonus applied to any applied poison, or any ability
        that has a poison effect that uses the poison rating roll
        (which is almost all of them other than weapon elemental damage.)
        """
        return int(self._basePoisonRatingBonus + self.equipmentPoisonRatingBonus +
               self._statusPoisonRatingBonus)

    @property
    def basePoisonRatingBonus(self):
        """ int """
        return int(self._basePoisonRatingBonus)

    @basePoisonRatingBonus.setter
    def basePoisonRatingBonus(self, value):
       self._basePoisonRatingBonus = value

    @property
    def equipmentPoisonRatingBonus(self):
        return int(self._equipmentPoisonRatingBonus)

    @equipmentPoisonRatingBonus.setter
    def equipmentPoisonRatingBonus(self, value):
        self._equipmentPoisonRatingBonus = value

    @property
    def statusPoisonRatingBonus(self):
        return int(self._statusPoisonRatingBonus)

    @statusPoisonRatingBonus.setter
    def statusPoisonRatingBonus(self, value):
        self._statusPoisonRatingBonus = value

    @property
    def totalPotionEffect(self):
        """
        An int representing how much healing and mana potions are
        augmented.  Starts at 100 but is increased by many possible
        factors, especially Sorcery."""
        return int(max(0, (self.totalSorcery - 10) * 4) +
                self._basePotionEffect +
                self._equipmentPotionEffect +
                self._statusPotionEffect)

    @property
    def basePotionEffect(self):
        """An int starting at 100 that indicates 100%"""
        return int(self._basePotionEffect)

    @basePotionEffect.setter
    def basePotionEffect(self, value):
        """The contribution from SOR should be max(0, (SOR - 10) * 5)
        or in other words, 5% per point of SOR beyond 10 but no penalty
        given for SOR less than 10."""
        self._basePotionEffect = value

    @property
    def equipmentPotionEffect(self):
        return int(self._equipmentPotionEffect)

    @equipmentPotionEffect.setter
    def equipmentPotionEffect(self, value):
        self._equipmentPotionEffect = value

    @property
    def statusPotionEffect(self):
        return int(self._statusPotionEffect)

    @statusPotionEffect.setter
    def statusPotionEffect(self, value):
        self._statusPotionEffect = value

    @property
    def totalJewleryEffect(self):
        return int(100 +
                max(0, (self.totalSorcery - 10) * 4) +
                self._baseJewleryEffect)

    @property
    def baseJewleryEffect(self):
        return int(self._baseJewleryEffect)

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
        return int(self._baseArcaneBonusDamage +
               self._equipmentArcaneBonusDamage +
               self._statusArcaneBonusDamage)

    @property
    def baseArcaneBonusDamage(self):
        return int(self._baseArcaneBonusDamage)

    @baseArcaneBonusDamage.setter
    def baseArcaneBonusDamage(self, value):
        self._baseArcaneBonusDamage = value

    @property
    def equipmentArcaneBonusDamage(self):
        return int(self._equipmentArcaneBonusDamage)

    @equipmentArcaneBonusDamage.setter
    def equipmentArcaneBonusDamage(self, value):
        self._equipmentArcaneBonusDamage = value

    @property
    def statusArcaneBonusDamage(self):
        return int(self._statusArcaneBonusDamage)

    @statusArcaneBonusDamage.setter
    def statusArcaneBonusDamage(self, value):
        self._statusArcaneBonusDamage = value

    @property
    def totalColdBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Cold attacks."""
        return int(self._baseColdBonusDamage +
               self._equipmentColdBonusDamage +
               self._statusColdBonusDamage)

    @property
    def baseColdBonusDamage(self):
        return int(self._baseColdBonusDamage)

    @baseColdBonusDamage.setter
    def baseColdBonusDamage(self, value):
        self._baseColdBonusDamage = value

    @property
    def equipmentColdBonusDamage(self):
        return int(self._equipmentColdBonusDamage)

    @equipmentColdBonusDamage.setter
    def equipmentColdBonusDamage(self, value):
        self._equipmentColdBonusDamage = value

    @property
    def statusColdBonusDamage(self):
        return int(self._statusColdBonusDamage)

    @statusColdBonusDamage.setter
    def statusColdBonusDamage(self, value):
        self._statusColdBonusDamage = value

    @property
    def totalDivineBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Divine attacks."""
        return int(self._baseDivineBonusDamage +
               self._equipmentDivineBonusDamage +
               self._statusDivineBonusDamage)

    @property
    def baseDivineBonusDamage(self):
        return int(self._baseDivineBonusDamage)

    @baseDivineBonusDamage.setter
    def baseDivineBonusDamage(self, value):
        self._baseDivineBonusDamage = value

    @property
    def equipmentDivineBonusDamage(self):
        return int(self._equipmentDivineBonusDamage)

    @equipmentDivineBonusDamage.setter
    def equipmentDivineBonusDamage(self, value):
        self._equipmentDivineBonusDamage = value

    @property
    def statusDivineBonusDamage(self):
        return int(self._statusDivineBonusDamage)

    @statusDivineBonusDamage.setter
    def statusDivineBonusDamage(self, value):
        self._statusDivineBonusDamage = value

    @property
    def totalElectricBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Electric attacks."""
        return int(self._baseElectricBonusDamage +
               self._equipmentElectricBonusDamage +
               self._statusElectricBonusDamage)

    @property
    def baseElectricBonusDamage(self):
        return int(self._baseElectricBonusDamage)

    @baseElectricBonusDamage.setter
    def baseElectricBonusDamage(self, value):
        self._baseElectricBonusDamage = value

    @property
    def equipmentElectricBonusDamage(self):
        return int(self._equipmentElectricBonusDamage)

    @equipmentElectricBonusDamage.setter
    def equipmentElectricBonusDamage(self, value):
        self._equipmentElectricBonusDamage = value

    @property
    def statusElectricBonusDamage(self):
        return int(self._statusElectricBonusDamage)

    @statusElectricBonusDamage.setter
    def statusElectricBonusDamage(self, value):
        self._statusElectricBonusDamage = value

    @property
    def totalFireBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Fire attacks."""
        return int(self._baseFireBonusDamage +
               self._equipmentFireBonusDamage +
               self._statusFireBonusDamage)

    @property
    def baseFireBonusDamage(self):
        return int(self._baseFireBonusDamage)

    @baseFireBonusDamage.setter
    def baseFireBonusDamage(self, value):
        self._baseFireBonusDamage = value

    @property
    def equipmentFireBonusDamage(self):
        return int(self._equipmentFireBonusDamage)

    @equipmentFireBonusDamage.setter
    def equipmentFireBonusDamage(self, value):
        self._equipmentFireBonusDamage = value

    @property
    def statusFireBonusDamage(self):
        return int(self._statusFireBonusDamage)

    @statusFireBonusDamage.setter
    def statusFireBonusDamage(self, value):
        self._statusFireBonusDamage = value

    @property
    def totalPoisonBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Poison attacks."""
        return int(self._basePoisonBonusDamage +
               self._equipmentPoisonBonusDamage +
               self._statusPoisonBonusDamage)

    @property
    def basePoisonBonusDamage(self):
        return int(self._basePoisonBonusDamage)

    @basePoisonBonusDamage.setter
    def basePoisonBonusDamage(self, value):
        self._basePoisonBonusDamage = value

    @property
    def equipmentPoisonBonusDamage(self):
        return int(self._equipmentPoisonBonusDamage)

    @equipmentPoisonBonusDamage.setter
    def equipmentPoisonBonusDamage(self, value):
        self._equipmentPoisonBonusDamage = value

    @property
    def statusPoisonBonusDamage(self):
        return int(self._statusPoisonBonusDamage)

    @statusPoisonBonusDamage.setter
    def statusPoisonBonusDamage(self, value):
        self._statusPoisonBonusDamage = value

    @property
    def totalShadowBonusDamage(self):
        """int, a value of 45 would indicate +45% damage dealt via Shadow attacks."""
        return int(self._baseShadowBonusDamage +
               self._equipmentShadowBonusDamage +
               self._statusShadowBonusDamage)

    @property
    def baseShadowBonusDamage(self):
        return int(self._baseShadowBonusDamage)

    @baseShadowBonusDamage.setter
    def baseShadowBonusDamage(self, value):
        self._baseShadowBonusDamage = value

    @property
    def equipmentShadowBonusDamage(self):
        return int(self._equipmentShadowBonusDamage)

    @equipmentShadowBonusDamage.setter
    def equipmentShadowBonusDamage(self, value):
        self._equipmentShadowBonusDamage = value

    @property
    def statusShadowBonusDamage(self):
        return int(self._statusShadowBonusDamage)

    @statusShadowBonusDamage.setter
    def statusShadowBonusDamage(self, value):
        self._statusShadowBonusDamage = value

    # Class specific and miscellaneous

    @property
    def arcaneArcherManaRegen(self):
        return int(self._arcaneArcherManaRegenBase)

    @arcaneArcherManaRegen.setter
    def arcaneArcherManaRegen(self, value):
        self._arcaneArcherManaRegenBase = value

    @property
    def totalIdentification(self):
        return int(self.totalSorcery + self.equipmentIdentification + self.statusIdentification)

    @property
    def equipmentIdentification(self):
        return int(self._equipmentIdentification)

    @equipmentIdentification.setter
    def equipmentIdentification(self, value):
        self._equipmentIdentification = value

    @property
    def statusIdentification(self):
        return int(self._statusIdentification)

    @statusIdentification.setter
    def statusIdentification(self, value):
        self._statusIdentification = value

    @property
    def lockpicking(self):
        if self.baseClass == "Thief":
            return int(self.totalCunning)
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
        return int(self._bonusRange)

    @bonusRange.setter
    def bonusRange(self, value):
        self._bonusRange = value

    @property
    def bonusTrapDamage(self):
        return int(self._bonusTrapDamage)

    @bonusTrapDamage.setter
    def bonusTrapDamage(self, value):
        self._bonusTrapDamage = value

    @property
    def bonusTrapRating(self):
        return int(self._bonusTrapRating)

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
        return int(self._ninjaStyle)

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
        totalWeight = self.inventory.totalWeight
        totalWeight += self.equippedItems.equippedWeight
        return int(totalWeight)

    @property
    def inventoryCapacity(self):
        """How much the player can fit in his inventory."""
        # TODO: Worry about how +Strength and +Capacity gear could allow you to carry more than your capacity.
        if self.totalStrength <= 15:
            return int(8 * self.totalStrength + self._baseInventoryCapacity + self._equipmentCarryingCapacity)
        else:
            return int(120 + (self.totalStrength - 15) * 12 + self._baseInventoryCapacity + self._equipmentCarryingCapacity)

    @property
    def baseInventoryCapacity(self):
        return int(self._baseInventoryCapacity)
        
    @baseInventoryCapacity.setter
    def baseInventoryCapacity(self, value):
        self._baseInventoryCapacity = value
            
    @property
    def equipmentCarryingCapacity(self):
        return self._equipmentCarryingCapacity

    @equipmentCarryingCapacity.setter
    def equipmentCarryingCapacity(self, value):
        self._equipmentCarryingCapacity = value

    @property
    def totalShopBonus(self):
        return int(min(40, max(0, (self.totalCunning - 10) * 0.5 + self.equipmentShopBonus)))

    @property
    def equipmentShopBonus(self):
        return int(self._equipmentShopBonus)

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

    @p.Person.restrictionAP.getter
    def restrictionAP(self):
        toleranceGrade = 0
        if self.armorTolerance == "Light":
            toleranceGrade = 8
        elif self.armorTolerance == "Medium":
            toleranceGrade = 20
        elif self.armorTolerance == "Heavy":
            toleranceGrade = 30
        aGrade = self.equippedItems.totalArmorGrade
        return max(0, round(aGrade / 2.0) - toleranceGrade)


    @p.Person.movementSpeed.getter
    def movementSpeed(self):
        '''The overworld movement speed.  Overrides from Person.'''
        if(True):
            return 5.0
            #float(self.totalMovementTiles) / float(self.totalMovementAPCost)
        else:
            pass
            # TODO: Should check for encumberment.

    def removeOnHitEffect(self, name, count):
        for fx in self.onHitEffects:
            if fx.name.lower() == name.lower() and fx.count == count:
                self.onHitEffects.remove(fx)
                return
                # Need to return immediately to remove exactly one fx.

    # TODO: Change the amount Rings/Amulets affect you based on Sorcery.
    def equip(self, newPiece):
        """Equips a piece of gear, and places any replaced gear in the inventory."""
        if newPiece not in self.inventory.allItems:
            print "Attempted to equip item not in inventory!"
            return
        oldPieces = self.equippedItems.equip(newPiece)
        oldPiece = oldPieces[0]
        oldPiece2 = None
        if oldPiece and len(oldPieces) > 1:
            oldPiece2 = oldPieces[1]

        for prop in newPiece.propertyList:
            prop.effect(prop, self)
        if isinstance(newPiece, equipment.Armor):
            self.equipmentDR += newPiece.DR
            self.equipmentSneak += newPiece.stealthMod
            self.equipmentDodge += newPiece.dodgeMod
        elif isinstance(newPiece, equipment.Weapon):
            pass
            # Weapon stats are viewed on the weapon itself.
        self.inventory.removeItem(newPiece)

        if oldPiece:
            for prop in oldPiece.propertyList:
                prop.effect(prop, self, reverse=True)
            if isinstance(oldPiece, equipment.Armor):
                self.equipmentDR -= oldPiece.DR
                self.equipmentSneak -= oldPiece.stealthMod
                self.equipmentDodge -= oldPiece.dodgeMod
            elif isinstance(oldPiece, equipment.Weapon):
                pass
            self.inventory.allItems.append(oldPiece)
        if oldPiece2:
            for prop in oldPiece2.propertyList:
                prop.effect(prop, self, reverse=True)
            if isinstance(oldPiece2, equipment.Armor):
                self.equipmentDR -= oldPiece2.DR
                self.equipmentSneak -= oldPiece2.stealthMod
                self.equipmentDodge -= oldPiece2.dodgeMod
            elif isinstance(oldPiece2, equipment.Weapon):
                pass
            self.inventory.allItems.append(oldPiece2)
        # TODO: Check to see if weight capacity has changed?

    def shouldAutoEquip(self, armor):
        ''' Determines if a piece of equipment should be 
        auto-equipped upon acquisition. '''
        if not isinstance(armor, equipment.Armor):
            return False
        if armor.type == "Finger" and None in self.equippedItems.equippedFingers:
            return True
        if armor.type == "Neck" and not self.equippedItems.equippedNeck:
            return True
        if armor.grade == self.armorTolerance:
            if armor.type == "Hands" and not self.equippedItems.equippedHandsArmor:
                return True
            elif armor.type == "Head" and not self.equippedItems.equippedHeadArmor:
                return True
            elif armor.type == "Legs" and not self.equippedItems.equippedLegsArmor:
                return True
            elif armor.type == "Chest" and not self.equippedItems.equippedChestArmor:
                return True
            elif armor.type == "Feet" and not self.equippedItems.equippedFeetArmor:
                return True
        return False
        
    def calcBurden(self):
        if self.inventoryCapacity >= self.inventoryWeight:
            return 0
        if self.inventoryCapacity < self.inventoryWeight and self.inventoryWeight <= self.inventoryCapacity * 1.2:
            return 2
        if self.inventoryCapacity * 1.2 <= self.inventoryWeight and self.inventoryWeight <= self.inventoryCapacity * 1.4:
            return 5
        if self.inventoryCapacity * 1.4 <= self.inventoryWeight and self.inventoryWeight <= self.inventoryCapacity * 1.6:
            return 10
        if self.inventoryCapacity * 1.6 <= self.inventoryWeight and self.inventoryWeight <= self.inventoryCapacity * 1.8:
            return 15
        if self.inventoryCapacity * 1.8 <= self.inventoryWeight and self.inventoryWeight <= self.inventoryCapacity * 2.0:
            return 20
        else:
            return 25
            
    def navigateInventory(self, screen, key):
        if key == K_RIGHT or key == K_KP6 or key == K_l:
            screen.move_dialog(6)
            return None
        elif key == K_LEFT or key == K_KP4 or key == K_h:
            screen.move_dialog(4)
            return None
        elif key == K_UP or key == K_KP8 or key == K_k:
            screen.move_dialog(8)
            return None
        elif key == K_DOWN or key == K_KP2 or key == K_j:
            screen.move_dialog(2)
            return None
        elif key == K_SPACE or key == K_i:
            screen.hide_dialog()
            return True
        elif key == K_e:
            selectionTuple = screen.get_dialog_selection()
            if selectionTuple[0] == 0:
                # This is the inventory side.
                item = self.inventory.allItems[selectionTuple[1]]
                if isinstance(item, consumable.Consumable):
                    return None
                else:
                    self.equip(item)
                    self.inventory.removeItem(item)
                    text = "Equipped: " + item.displayName                                                            
                    inv = self.inventory.allItems
                    eq = self.equippedItems.allGear
                    capacity = `self.inventoryWeight` + "/" + `self.inventoryCapacity`
                    screen.update_item_dialog_text(text, capacity)
                    screen.update_item_dialog_items(inv, eq)
                    return None
        elif key == K_d:
            selectionTuple = screen.get_dialog_selection()
            if selectionTuple[0] == 0:
                # This is the inventory side.
                item = self.inventory.allItems[selectionTuple[1]]
                self.inventory.removeItem(item)
                text = "Destroyed: " + item.displayName
                inv = self.inventory.allItems
                eq = self.equippedItems.allGear
                capacity = `self.inventoryWeight` + "/" + `self.inventoryCapacity`
                screen.update_item_dialog_text(text, capacity)
                screen.update_item_dialog_items(inv, eq)
                return None
        return None
        
    def printCharacterSheet(self):
        '''Method prints a mock-up of a character sheet to the console as
        a placeholder until a real UI character sheet exists.'''
        cs = []
        cs.append("/-------------------------------------------------------\n")
        cs.append("| Character Name: " + self.name + "\n")
        cs.append("| Level: " + `self.level` + "  Experience: " + `self.experience` + "/" + `self.getExpForNextLevel()` + "\n")
        cs.append("| Character Class: " + self.characterClass + "  Race: " + self.race + "\n")
        cs.append("| HP: " + `int(self.HP)` + "/" + `int(self.totalHP)` + "  MP: " + `int(self.MP)` + "/" + `int(self.totalMP)` + "  AP: " + `self.AP` + "/" + `self.totalAP` + "\n" )
        cs.append("| ----------->>> Primary Statistics <<<-----------------\n")
        cs.append("| Strength: " + `int(self.totalStrength)` + " (" + `self.equipmentStrength` + ")  Dexterity: " + `int(self.totalDexterity)` + " (" + `self.equipmentDexterity` + ")\n")
        cs.append("| Cunning:  " + `int(self.totalCunning)` + " (" + `self.equipmentCunning` + ")  Sorcery: " + `int(self.totalSorcery)` + " (" + `self.equipmentSorcery` + ")\n")
        cs.append("| Piety:    " + `int(self.totalPiety)` + " (" + `self.equipmentPiety` + ")  Constitution: " + `int(self.totalConstitution)` + " (" + `self.equipmentConstitution` + ")\n")
        cs.append("| ----------->>> Secondary Statistics <<<---------------\n")
        cs.append("| Melee Accuracy:    " + `self.totalMeleeAccuracy` + " (" + `self.equipmentMeleeAccuracy` + ")  Ranged Accuracy: " + `self.totalRangedAccuracy` + " (" + `self.equipmentRangedAccuracy` + ")\n")
        cs.append("| Dodge:             " + `self.totalDodge` + " (" + `self.equipmentDodge` + ")  Ranged Dodge: " + `self.totalRangedDodge` + " (" + `self.equipmentRangedDodge` + ")\n")
        cs.append("| Might:             " + `self.totalMight` + " (" + `self.equipmentMight` + ")  Melee Dodge: " + `self.totalMeleeDodge` + " (" + `self.equipmentMeleeDodge` + ")\n")
        cs.append("| Spellpower:        " + `self.totalSpellpower` + " (" + `self.equipmentSpellpower` + ")  Magic Resist: " + `self.totalMagicResist` + " (" + `self.equipmentMagicResist` + ")\n")
        cs.append("| Critical Chance:   " + `self.totalCriticalChance` + "% (" + `self.equipmentCriticalChance` + ")  Critical Magnitude: " + `self.totalCriticalMagnitude` + "% (" + `self.equipmentCriticalMagnitude` + ")\n")
        cs.append("| Armor Penetration: " + `self.totalArmorPenetration` + "% (" + `self.equipmentArmorPenetration` + ")  Damage Resistance: " + `self.totalDR` + "% (" + `self.equipmentDR` + ")\n")
        cs.append("| Poison Tolerance:  " + `self.totalPoisonTolerance` + " (" + `self.equipmentPoisonTolerance` + ")  Poison Rating Bonus: " + `self.totalPoisonRatingBonus` + " (" + `self.equipmentPoisonRatingBonus` + ")\n")  
        cs.append("| Awareness:         " + `self.totalAwareness` + " (" + `self.equipmentAwareness` + ")  Sneak: " + `self.totalSneak` + " (" + `self.equipmentSneak` + ")\n")
        cs.append("| Trap Evade:        " + `self.totalTrapEvade` + " (" + `self.equipmentTrapEvade` + ")  Movement Tiles: " + `self.totalMovementTiles` + " (" + `self.equipmentMovementTiles` + ")\n")
        cs.append("| ----------->>> Tertiary Statistics <<<----------------\n")
        cs.append("| Shop Bonus:           " + `self.totalShopBonus` + "% (" + `self.equipmentShopBonus` + "%)  Carrying Capacity: " + `self.inventoryCapacity` + " (" + `self.equipmentCarryingCapacity` + ")\n")
        cs.append("| Trap Rating Bonus:    " + `self.bonusTrapRating` + "      Trap Damage Bonus: " + `self.bonusTrapDamage` + "%\n")
        cs.append("| Jewlery Effect:       " + `self.totalJewleryEffect` + "%     Potion Bonus Effect: " + `self.totalPotionEffect` + "%\n") 
        cs.append("| Identification:       " + `self.totalIdentification` + " (" + `self.equipmentIdentification` + ")  Gold Find: +" + `self.goldFind` + "%\n")
        cs.append("| ----------->>> Elemental Resistances <<<--------------\n")
        cs.append("| Arcane Resistance:   " + `self.totalArcaneResistance` + "% (" + `self.equipmentArcaneResistance` + ")\n")
        cs.append("| Cold Resistance:     " + `self.totalColdResistance` + "% (" + `self.equipmentColdResistance` + ")\n")
        cs.append("| Divine Resistance:   " + `self.totalDivineResistance` + "% (" + `self.equipmentDivineResistance` + ")\n")
        cs.append("| Electric Resistance: " + `self.totalElectricResistance` + "% (" + `self.equipmentElectricResistance` + ")\n")
        cs.append("| Fire Resistance:     " + `self.totalFireResistance` + "% (" + `self.equipmentFireResistance` + ")\n")
        cs.append("| Poison Resistance:   " + `self.totalPoisonResistance` + "% (" + `self.equipmentPoisonResistance` + ")\n")
        cs.append("| Shadow Resistance:   " + `self.totalShadowResistance` + "% (" + `self.equipmentShadowResistance` + ")\n")
        cs.append("| ----------->>> Elemental Power <<<--------------------\n")
        cs.append("| Arcane Damage Bonus:   " + `self.totalArcaneBonusDamage` + "% (" + `self.equipmentArcaneBonusDamage` + ")\n")
        cs.append("| Cold Damage Bonus:     " + `self.totalColdBonusDamage` + "% (" + `self.equipmentColdBonusDamage` + ")\n")
        cs.append("| Divine Damage Bonus:   " + `self.totalDivineBonusDamage` + "% (" + `self.equipmentDivineBonusDamage` + ")\n")
        cs.append("| Electric Damage Bonus: " + `self.totalElectricBonusDamage` + "% (" + `self.equipmentElectricBonusDamage` + ")\n")
        cs.append("| Fire Damage Bonus:     " + `self.totalFireBonusDamage` + "% (" + `self.equipmentFireBonusDamage` + ")\n")
        cs.append("| Poison Damage Bonus:   " + `self.totalPoisonBonusDamage` + "% (" + `self.equipmentPoisonBonusDamage` + ")\n")
        cs.append("| Shadow Damage Bonus:   " + `self.totalShadowBonusDamage` + "% (" + `self.equipmentShadowBonusDamage` + ")\n")
        cs.append("| ----------->>> Active Abilities <<<-------------------\n")
        for abil in self.abilities:
            cd = abil.cooldown
            if cd is None:
                cd = 0
            cs.append("| Level " + `abil.level` + ": " + abil.name + " AP: " + `abil.APCost` + " Cooldown: " + `cd` + "\n")
        cs.append("| ----------->>> Magic Spells <<<-----------------------\n")
        for spell in self.spellList:
            cd = spell.cooldown
            if cd is None:
                cd = 0
            cs.append("| " + spell.name + " MP: " + `spell.MPCost` + " AP: " + `spell.APCost` + " Cooldown: " + `cd` + "\n")
        cs.append("| ----------->>> Passive Abilities <<<------------------\n")
        for passive in self.passiveAbilities:
            if "--IGNORE--" not in passive.name:
                cs.append("| Level " + `passive.level` + ": " + passive.name + "\n")
        cs.append("| ----------->>> Traits <<<-----------------------------\n")
        for t in self.traits:
            cs.append("| Rank " + `t.rank` + " " + t.name + "\n")
        cs.append("\\-------------------------------------------------------\n")
        cs = ''.join(cs)
        print cs

    
def sumRollsOver(a, b):
    '''Determines if the sum of two numbers' remainders cause 
    overflow into a whole number.  Works for two floats, a and b.
    Not particularly accurate; do not use when accuracy is needed.
    
    Returns True if the two numbers' remainders sum to at least 1.
    '''
    a_int = int(a)
    b_int = int(b)
    a_remainder = a - a_int
    b_remainder = b - b_int
    if a_remainder + b_remainder >= 1:
        return True
    return False

class TileObject(object):
    def __init__(self, name, image, text):
        self.name = name
        self.image = image
        self.text = text

