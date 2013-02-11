#!/usr/bin/python

import sys
import combat
import dice
import listener

class Ability(object):
    
    def __init__(self, name, owner):
        self.name = name
        info = Ability.allAbilities[name]
        self.level = info['level']
        self.HPCost = info['HPCost']
        self.APCost = info['APCost']
        self.range = info['range']
        self.targetType = info['target']
        self.action = info['action']
        self.cooldown = info['cooldown']
        self.checkFunction = info['checkFunction']
        self.breakStealth = info['breakStealth']
        self.owner = owner
        
        
    def canUse(self, target):
        '''
        target: Person (later, Location?)
        '''
        
        # Check for modifications to ability costs here from listeners TODO
        mod = 0 # dummy code
        if self.owner.AP < self.APCost - mod:
            return (False, "Insufficient AP")
            
        messageCode = (True, "")
        if self.checkFunction:
            messageCode = self.checkFunction(self.owner, target)
        if not messageCode[0]:
            return messageCode
            
        if self.targetType == "self" and owner is not target:
            return (False, "Ability is self-only, and the given target is not the user.")
        if self.targetType == "hostile" and self.owner.team == target.team:
            return (False, "Cannot target own team with hostile ability.")
        if self.targetType == "friendly" and self.owner.team != target.team:
            return (False, "Cannot target hostile with beneficial ability.")
        # Do we need any check for AoE spells?
        if not self.owner.inRange(target):
            return (False, "Target is out of range.")
        if self.name in self.owner.cooldownList:
            return (False, "Ability is on Cooldown.")
        return (True, "")
        
        
    def use(self, target):
        ''' Uses the given ability on or around the given target Person (Location?)
        Performs a check if this is possible, but this is not where the canUse
        check should be made.  If caught here, it will raise an exception!'''
        if self.canUse(target)[0]:
            hpLoss = self.HPCost
            if "Percent" in str(self.HPCost):
                hpLoss = round(int(self.HPCost.split(" ")[0]) / 100 * self.owner.totalHP)
            Combat.modifyResource(self.owner, "HP", -hpLoss)
            Combat.modifyResource(self.owner, "AP", -self.APCost)
            if self.cooldown:
                Combat.applyCooldown(self.owner, self.name, self.cooldown)
            self.action(self, target)
            if Dice.rollBeneath(self.breakStealth):
                Combat.removeStealth(self.owner)
        else:
            return 
            # TODO! Make this raise an exception rather than silently return.
        
    
    def _mightyBlow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-5)
        Combat.basicAttack(source, target, hit, forceMod=1.5)
        
    def _mightyBlowCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")
        
    def _brace(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)
        Combat.endTurn(source)
        
    def _dash(self, target):
        newCost = 0
        numberOfMoves = 1
        Combat.setMovementCost(target, newCost, numberOfMoves)
        
    def _quickStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=-10)
        Combat.basicAttack(source, target, hit, forceMod=0.5)
        
    def _quickStrikeCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")
        
    def _preciseBlow(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=4)
        Combat.basicAttack(source, target, hit)
        
    def _preciseBlowCheck(self, target):
        if self.owner.usingWeapon("Melee"):
            return (True, "")
        return (False, self.name + " requires a Melee weapon.")
        
    def _backstab(self, target):
        source = self.owner
        critChance = 0
        critMag = 0
        accuracy = 0
        if source.usingWeapon("Sword"):
            critChance = 25
            critMag = 1.5
            if source.usingWeaponStyle("Single"):
                accuracy = 9
        elif source.usingWeapon("Knife"):
            critChance = 50
            critMag = 2
            if source.usingWeaponStyle("Single"):
                accuracy = 5
        hit = Combat.calcHit(source, target, "Physical", modifier=accuracy, critMod=critChance)
        Combat.basicAttack(source, target, hit, criticalDamageMod=critMag)
        
    def _backstabCheck(self, target):
        source = self.owner
        if not source.inStealth():
            return (False, "Must be in stealth to perform " + self.name + " .")
        # If not in backstab position : TODO
        if not source.usingWeapon("Sword") and not source.usingWeapon("Knife"):
            return (False, "Must be using either swords or knives to preform " + self.name + " .")
        
        
    def _chainGrasp(self, target):
        source = self.owner
        success = Dice.rollBeneath(min(90, (source.totalCunning - target.totalCunning) * 9))
        if success:
            duration = 3
            Combat.addStatus(target, "Chain Grasp", duration)
        
    def _chainGraspCheck(self, target):
        if target.size == "Huge":
            return (False, self.name + " cannot be used on Huge targets.")
        return (True, "")
        
    def _agilePosition(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, "Agile Position", duration)
        Combat.endTurn(source)
        
    def _agilePositionCheck(self, target):
        return (True, "")
        
    def _feint(self, target):
        source = self.owner
        success = Dice.rollBeneath(min(72, (source.totalCunning - target.totalCunning) * 8))
        if success:
            duration = 2
            Combat.addStatus(target, "Feint", duration)
            
    def _feintCheck(self, target):
        return (True, "")
        
    def _farSightedFocus(self, target):
        source = self.owner
        duration = 3
        Combat.addStatus(source, "Far-Sighted Focus", duration)
        
    def _farSightedFocusCheck(self, target):
        return (True, "")
        
    def _tunnelVision(self, target):
        source = self.owner
        duration = 4
        Combat.addStatus(source, "Tunnel Vision", duration)
        
    def _tunnelVisionCheck(self, target):
        return (True, "")
        
    def _balm(self, target):
        source = self.owner
        Combat.healTarget(source, round(source.totalHP * 0.05))
        
    def _balmCheck(self, target):
        return (True, "")
        
    def _rapidReload(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, modifier=-8)
        Combat.basicAttack(source, target, hit)
        
    def _rapidReloadCheck(self, target):
        source = self.owner
        if source.usingWeapon("Crossbow"):
            return (True, "")
        return (False, "Must be using a Crossbow to use " + self.name + ".")
        
    def _rangersAim(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, "Ranger's Aim", duration)
        
    def _rangersAimCheck(self, target):
        return (True, "")
        
    def _magicGuard(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)
        Combat.endTurn(source)
        
    def _gather(self, target):
        source = self.owner
        duration = 1
        Combat.addStatus(source, self.name, duration)
        
    def _reverseHex(self, target):
        Combat.removeStatusOfType(target, "debuff")
        
    def _berserkerRage(self, target):
        duration = 6
        Combat.addStatus(self.owner, self.name, duration)
        
    def _berserkerRageCheck(self, target):
        source = self.owner
        if source.HP <= source.totalHP * 0.75:
            return (True, "")
        return (False, "Too much HP to use " + self.name)
        
    def _sacrificialStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", critMod=1)
        Combat.basicAttack(source, target, hit, forceMod=1.5)
    
    def _sacrificialStrikeCheck(self, target):
        source = self.owner
        if source.HP < source.totalHP * 0.05 + 1:
            return (False, "Insufficient HP to use " + self.name)
        if source.usingWeapon("Melee"):
            return (True, "")
        else: 
            return (False, self.name + " requires a melee weapon.")
        
    def _desperateStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical", modifier=10, critMod=20)
        Combat.basicAttack(source, target, hit, forceMod=2.5, armorPenetrationMod=10)
        doStun = Dice.rollPresetChance(source, target, "Occasional")
        Combat.addStatus(target, "Stun", duration=1, hitValue=hit, chance=doStun)    
        
    def _desperateStrikeCheck(self, target):
        source = self.owner
        if source.HP > source.totalHP * 0.25:
            return (False, "Excess HP; cannot use " + self.name)
        if source.usingWeapon("Melee"):
            return (True, "")
        else:
            return (False, self.name + " requires a melee weapon.")
        
    def _bloodOfTheAncients(self, target):
        source = self.owner
        Combat.healTarget(source, round(source.totalHP * 0.15))
        duration = 1
        Combat.addStatus(source, "Blood of the Ancients", duration)
        
    def _bloodOfTheAncientsCheck(self, target):
        source = self.owner
        if source.HP < source.totalHP:
            return (True, "")
        return (False, "HP already at maximum; cannot use: " + self.name + " .")
        
    # Spellsword
    def _martialMode(self, target):
        source = self.owner
        duration = -1
        Combat.addStatus(target, "Martial Mode", duration) 
        newListener = listener.Listener(self, self.owner, [], self._martialModeDisable, ['Player MP level changed'])
        source.listeners.append(newListener)
    
    def _martialModeCheck(self, target):
        source = self.owner
        if source.MP > source.totalMP * 0.15:
            return (False, "Too much MP remaining to use " + self.name)
        else:
            return (True, "")
        
    def _martialModeDisable(self, target, reverse=False, percent=None):
        if percent > 0.15:
            Combat.removeStatus(target, "Martial Mode")
        toRemove = None
        for x in target.listeners:
            if x.action == self._martialModeDisable:
                toRemove = x
        if toRemove:
            target.listeners.remove(toRemove)        
        
    # Druid
    def _deepWound(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, poisonRatingMod=5)
        if hit != "Miss":
            duration = 5
            Combat.addStatus(target, "Deep Wound", duration)
        # TODO: Applied Poison ratings fix
        
    def _deepWoundCheck(self, target):
        return (True, "")
        
    def _painfulShot(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical")
        Combat.basicAttack(source, target, hit, criticalDamageMod=1.1)
        if hit != "Miss" and Dice.rollPresetChance(source, target, "Occasional"):
            duration = 5
            Combat.addStatus(target, "Painful Shot", duration)            
        
    def _painfulShotCheck(self, target):
        return (True, "")
        
    def _poisonousTouch(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Physical Poison", modifier=5, rating=12)
        if hit != "Miss":
            duration = 4
            damage = round(Dice.roll(5, 15) * (1 + source.totalCunning * 0.07))
            Combat.addStatus(target, "Poisonous Toch", duration, damage) 
        
    def _poisonousTocuhCheck(self, target):
        return (True, "")
    
    # Battle Mage
    def _bufferStrike(self, target):
        source = self.owner
        hit = Combat.calcHit(source, target, "Phsyical", modifier=3)
        Combat.basicAttack(source, target, hit)
        duration = 4
        magnitude = round(10 + source.totalSpellpower / 15)
        Combat.addStatus(source, self.name, magnitude, hitValue=hit)
    
    def _bufferStrikeCheck(self, target):
        source = self.owner
        if source.usingWeapon("Melee"):
            return (True, "")
        else:
            return (False, self.name + " requires a melee weapon.")
        
    def _innerMight(self, target):
        source = self.owner
        duration = 2
        magnitude = 3 + source.totalSpellpower // 5
        Combat.addStatus(source, "Inner Might", duration, magnitude)
        newListener = listener.Listener(self, self.owner, [], self._innerMightDisable, ['Player MP level changed'])
        source.listeners.append(newListener)
    
    def _innerMightCheck(self, target):
        source = self.owner
        if source.MP >= source.totalMP * 0.75:
            return (True, "")
        else:
            return (False, "MP level must be above 75% to use: " + self.name + " .")
            
    def _innerMightDisable(self, target, reverse=False, percent=None):
        if percent < 0.75:
            Combat.removeStatus(target, "Inner Might")
        toRemove = None
        for x in target.listeners:
            if x.action == self._innerMightDisable:
                toRemove = x
        if toRemove:
            target.listeners.remove(toRemove)    
    
    allAbilities = {
        # Fighter
        'Mighty Blow':
        {
        'level' : 1,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 9,
        'range' : 1,
        'target' : 'hostile',
        'action' : _mightyBlow,
        'cooldown' : None,
        'checkFunction' : _mightyBlowCheck,
        'breakStealth' : 100
        },
        'Brace':
        {
        'level' : 1,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _brace,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Dash':
        {
        'level' : 1,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _dash,
        'cooldown' : None,  
        'checkFunction' : None,
        'breakStealth' : 100            
        },
        'Quick Strike':
        {
        'level' : 2,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : 1,
        'target' : 'hostile',
        'action' : _quickStrike,
        'cooldown' : None,
        'checkFunction' : _quickStrikeCheck,
        'breakStealth' : 100
        },
        'Precise Blow':
        {
        'level' : 2,
        'class' : 'Fighter',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 1,
        'target' : 'hostile',
        'action' : _preciseBlow,
        'cooldown' : None,
        'checkFunction' : _preciseBlowCheck,
        'breakStealth' : 100
        },
        
        # Thief
        'Backstab':
        {
        'level' : 1,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _backstab,
        'cooldown' : 2,
        'checkFunction' : _backstabCheck,
        'breakStealth' : 100
        },
        'Chain Grasp':
        {
        'level' : 1,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 4,
        'target' : 'hostile', 
        'action' : _chainGrasp,
        'cooldown' : 7,
        'checkFunction' : _chainGraspCheck,
        'breakStealth' : 100
        },
        'Agile Position':
        {
        'level' : 2,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost': 5,
        'range' : 0,
        'target' : 'self',
        'action' : _agilePosition,
        'cooldown' : 5,
        'checkFunction' : _agilePositionCheck,
        'breakStealth' : 0
        },
        'Feint':
        {
        'level' : 4,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : 1,
        'target' : 'hostile',
        'action' : _feint,
        'cooldown' : None,
        'checkFunction' : _feintCheck,
        'breakStealth' : 100
        },
        'Far-Sighted Focus':
        {
        'level' : 4,
        'class' : 'Thief',
        'HPCost' : 0,
        'APCost' : 8,
        'range' : 0,
        'target' : 'self',
        'action' : _farSightedFocus,
        'cooldown' : 1,
        'checkFunction' : _farSightedFocusCheck,
        'breakStealth' : 0
        },
        
        # Ranger
        'Tunnel Vision':
        {
        'level' : 2,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 0,
        'target' : 'self',
        'action' : _tunnelVision,
        'cooldown' : 5,
        'checkFunction' : _tunnelVisionCheck,
        'breakStealth' : 0
        },
        'Balm':
        {
        'level' : 2,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 6,
        'range' : 0,
        'target' : 'self',
        'action' : _balm,
        'cooldown' : 2,
        'checkFunction' : _balmCheck,
        'breakStealth' : 100
        },
        'Rapid Reload':
        {
        'level' : 2,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : -1,
        'target' : 'hostile',
        'action' : _rapidReload,
        'cooldown' : None,
        'checkFunction' : _rapidReloadCheck,
        'breakStealth' : 100
        },
        "Ranger's Aim":
        {
        'level' : 4,
        'class' : 'Ranger',
        'HPCost' : 0,
        'APCost' : 2,
        'range' : 0,
        'target' : 'self',
        'action' : _rangersAim,
        'cooldown' : 1,
        'checkFunction' : _rangersAimCheck,
        'breakStealth' : 0
        },
        
        # Wizard
        'Magic Guard':
        {
        'level' : 1,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 3,
        'range' : 0,
        'target' : 'self',
        'action' : _magicGuard,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 0
        },
        'Gather':
        {
        'level' : 2,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : 0,
        'target' : 'self',
        'action' : _gather,
        'cooldown' : None,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        'Reverse Hex':
        {
        'level' : 2,
        'class' : 'Wizard',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'friendly',
        'action' : _reverseHex,
        'cooldown' : 5,
        'checkFunction' : None,
        'breakStealth' : 100
        },
        
        
        
        
        
        'Berserker Rage':
        {
        'level' : 1,
        'class' : 'Barbarian',
        'HPCost': 0,
        'APCost' : 8,
        'range' : 0,
        'target' : 'self',
        'action' : _berserkerRage,
        'cooldown' : 5,
        'checkFunction': _berserkerRageCheck,
        'breakStealth' : 100
        },
        'Sacrificial Strike':
        {
        'level' : 2,
        'class' : 'Barbarian',
        'HPCost' : '5 Percent',
        'APCost' : 5,
        'range' : 1,
        'target' : 'hostile',
        'action' : _sacrificialStrike,
        'cooldown' : None,
        'checkFunction' : _sacrificialStrikeCheck,
        'breakStealth' : 100
        },
        'Desperate Strike':
        {
        'level' : 3,
        'class' : 'Barbarian',
        'HPCost' : 0,
        'APCost' : 12,
        'range' : 1,
        'target' : 'hostile',
        'action' : _desperateStrike,
        'cooldown' : None,
        'checkFunction' : _desperateStrikeCheck,
        'breakStealth' : 100
        },
        'Blood of the Ancients':
        {
        'level' : 4,
        'class' : 'Barbarian',
        'HPCost' : 0,
        'APCost' : 11,
        'range' : 0,
        'target' : 'self',
        'action' : _bloodOfTheAncients,
        'cooldown' : 4,
        'checkFunction' : _bloodOfTheAncientsCheck,
        'breakStealth' : 0
        },
        
        'Martial Mode':
        {
        'level' : 2,
        'class' : 'Spellsword',
        'HPCost' : 0,
        'APCost' : 1,
        'range' : 0,
        'target' : 'self',
        'action' : _martialMode,
        'cooldown' : None,
        'checkFunction' : _martialModeCheck,
        'breakStealth' : 0
        },
        
        'Deep Wound':
        {
        'level' : 1,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : -1,
        'target' : 'hostile',
        'action' : _deepWound,
        'cooldown' : 1,
        'checkFunction' : _deepWoundCheck,
        'breakStealth' : 100
        },
        'Painful Shot':
        {
        'level' : 1,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 7,
        'range' : -1,
        'target' : 'hostile',
        'action' : _painfulShot,
        'cooldown' : None,
        'checkFunction' : _painfulShotCheck,
        'breakStealth' : 100
        },
        'Poisonous Touch':
        {
        'level' : 2,
        'class' : 'Druid',
        'HPCost' : 0,
        'APCost' : 5,
        'range' : 1,
        'target' : 'hostile',
        'action' : _poisonousTouch,
        'cooldown' : 3,
        'checkFunction' : _poisonousTouchCheck,
        'breakStealth' : 100
        },
        
        # Battle Mage
        'Buffer Strike':
        {
        'level' : 2,
        'class' : 'Battle Mage',
        'HPCost' : 0,
        'APCost' : 10,
        'range' : 1,
        'target' : 'hostile',
        'action' : _bufferStrike,
        'cooldown' : 3,
        'checkFunction' : _bufferStrikeCheck,
        'breakStealth' : 100
        },
        'Inner Might':
        {
        'level' : 4,
        'class' : 'Battle Mage',
        'HPCost' : 0,
        'APCost' : 4,
        'range' : 0,
        'target' : 'self',
        'action' : _innerMight,
        'cooldown' : 4,
        'checkFunction' : _innerMightCheck,
        'breakStealth' : 0
        }
        
            
            

    }