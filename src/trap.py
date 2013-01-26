#!/usr/bin/python

import sys
import dice
import combat

class Trap(object):
    trapTemplates = []
    
    @staticmethod
    def loadTrapTemplates():
        trapTemplates = TrapTemplate.allTemplates
    
    # TODO Constructor for player traps.
    
    def __init__(self, trapTemplateName, level):
        """Constructor for Hostile traps (overworld traps)"""
        template = None
        for t in trapTemplates:
            if t.name == trapTemplateName:
                template = t
        if template:
            self.name = template.name
            self.level = level
            self.trapRating = round(template.trapRating[0] + template.trapRating[1] * level)
            self.rarity = template.rarity
            self.effectA = template.effectA
            self.effectB = template.effectB
            self.effectC = template.effectC
        else:
            TypeError("Template Type: " + trapTemplateName + " not found.")
        
    def triggerAllEffects(self, target):
        """Call to trigger all effects on the target.  Will attempt to
        affect the target, but the target still has its trap evade which
        will be rolled which can negate one or more effects."""
        if (self.effectA):
            self.triggerEffect(target, **self.effectA)
        if (self.effectB):
            self.triggerEffect(target, **self.effectB)
        if (self.effectC):
            self.triggerEffect(target, **self.effectC)
        
    def triggerEffect(self, target, name=None, element=None, min=0, max=0, pRating=0, duration=0,
                      quantity=1, magnitude=0, wModHeavy=0, wModMedium=0, wModLight=0):
        if(min != 0):
            min = round(min[0] + min[1] * self.level)
        if(max != 0):
            max = round(max[0] + max[1] * self.level)
        if(pRating != 0):
            pRating = round(pRating[0] + pRating[1] * self.level)
                      
        if name == "Damage":
            self.dealDamage(target, element, min, max, quantity, wModHeavy, wModMedium, wModLight)
        if name == "Toxin":
            self.applyToxin(target, duration, pRating)
        if name == "Lower Movement Tiles":
            self.slowMovement(target, duration, magnitude)
        if name == "Blindess":
            self.blind(target, duration, magnitude)
        if name == "Mana Loss":
            self.drainMana(target, magnitude)
        
    def dealDamage(self, target, element, min, max, quantity, wModHeavy, wModMedium, wModLight):
        while (quantity > 0):
            if Dice.rollTrapHit(target, self) == "Hit":
                minDam = (min[0] + min[1] * self.level).round()
                maxDam = (max[0] + max[1] * self.level).round()
                actualDam = Combat.calcDamage(self, target, minDam, maxDam, element, "Normal Hit")
                
                if(target.usingArmor("Heavy")):
                    actualDam *= (1 + wModHeavy/100)
                elif(target.usingArmor("Medium")):
                    actualDam *= (1 + wModMedium/100)
                elif(target.usingArmor("Light")):
                    actualDam *= (1 + wModLight/100)
                
                Combat.lowerHP(target, actualDam)     
            quantity -= 1
                
    def applyToxin(self, target, duration, poisonRating):
        pass
        #TODO
        
    def slowMovement(self, target, duration, magnitude):
        if Dice.rollTrapHit(target, self) == "Hit":
            Combat.addStatus(target, "Hostile Trap Slow", duration, magnitude)
        
    def blind(self, target, duration, magnitude):
        if Dice.rollTrapHit(target, self) == "Hit":
            Combat.addStatus(target, "Hostile Trap Blind", duration, magnitude)
    
    def drainMana(self, target, magnitude):
        if Dice.rollTrapHit(target, self) == "Hit":
            Combat.modifyResource(target, "MP", -target.MP)
        
class TrapTemplate(object):
    allTemplates = []
    
    def __init__(self, name, trapRating, rarity, effectList):
        self.name = name
        self.trapRating = trapRating
        self.rarity = rarity
        self.effectA = effectList[0]
        self.effectB = effectList[1]
        self.effectC = effectList[2]
        
        
        
    
        