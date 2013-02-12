#!/usr/bin/python

import sys
import entity

class Wealth(entity.Entity):
    
    wealthList = []
 
    types = {
        "Gold" : 
                {
                  'value' : 0,
                  'weight' : 0,
                  'image' : None
                },
        "Small Pouch of Gems" : 
                {
                  'value' : 100,
                  'weight' : 2,
                  'image' : None
                },
        "Coarse Gemstone" :
                {
                  'value' : 225,
                  'weight' : 1,
                  'image' : None
                }
            }     
 
    def __init__(self, name, goldAmount=0):
        entity.Entity.__init__(self, location=None)
        self.name = name
        self.goldValue = goldAmount
        self.weight = 0
        self.image = None
        if name in Wealth.types:
            if name != "Gold":
                self.goldValue = Wealth.types[name]['value']
                self.weight = Wealth.types[name]['value']
                self.image = Wealth.types[name]['image']
        self.identifier = self.name + ": " + str(self.goldValue)      
        


    
    