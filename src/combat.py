#!/usr/bin/python

import sys
import dice

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
        elif type == "MP":
            target.MP += value
        elif type == "HP":
            target.HP += value
        else
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
        offense *= random.uniform(0.75, 1.00)
        defense *= random.uniform(0.75, 1.00)
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
        offense *= random.uniform(0.5, 1.0)
        defense *= random.uniform(0.5, 1.0)
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
                #Ranged attack with penalty TODO
                #Passives alter how this functions? TODO
            #Ranged attack not in melee, or it doesn't matter.
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
        type = type.capitalize().strip().replace(" ", "-")
        if (type == "Physical"):
            return Combat.physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty)
        
        if (type == "Magical"):
            return Combat.magicalHitMechanics(source, target)
            
        if (type == "Magical-Poison" or type == "Poison-Magical"):
            if (Combat.poisonHitMechanics(source, target, rating) == "Normal Hit"):
                return Combat.magicalHitMechanics(source, target)
            else:
                return "Miss"
        
        if (type == "Physical-Poison" or type == "Poison-Physical"):
            if (Combat.poisonHitMechanics(source, target, rating) == "Normal Hit"):
                return Combat.physicalHitMechanics(source, target, modifier, critMod, ignoreMeleeBowPenalty)
            else:
                return "Miss"
            
        if (type == "Poison"):
            return Combat.poisonHitMechanics(source, target, rating)
            
        if (type == "Trap"):
            raise NotImplementedError("This method does not yet support the Trap type.")
            
        raise TypeError("Unknown Attack Type: " + type + " .")            
          
          
          