#!/usr/bin/python

import sys
import internalstatus

class Status(object):
    def __init__(self):
        # Values loaded at startup time
        self.displayName = None
        self.element = None
        self.categoryList = None
        self.internalList = None

        #self.persistent = None #boolean Not sure where to put this yet TODO
        
        # Values given to individual instances of this Status
        self.turnsLeft = None
        self.stacks = 1
        self.charges = None
        
    def populate(self, name, element, categoryList, internalList):
        """Populates the fields of this status from the information gained
        through a parser from a txt file or a previously created displaystatus."""
        self.displayName = name
        self.element = element
        self.categoryList = categoryList
        self.internalList = internalList
        
    def applyMagnitude(self, magnitude): 
        """If no magnitude is provided, use the value given from the data
        file."""
        for item in self.internalList:
            if item.magnitude == 0:
                item.magnitude = magnitude
    
    def applyMinMax(self, min, max):
        for item in self.internalList:
            if min > 0:
                item.min = min
            if max > 0:
                if max < min:
                    item.max = min
                else:
                    item.max = max
    
    def cloneWithDetails(self, magnitude, duration, min=0, max=0, charges=0):
        clone = Status()
        clone.populate(self.displayName, self.element, self.categoryList, self.internalList)
        clone.turnsLeft = duration
        clone.charges = charges
        clone.applyMagnitude(magnitude)
        clone.applyMinMax(min, max)
        return clone
        
    def activate(self, target):
        # Requires identical ordering of parameters, TODO
        for iStatus in self.internalList:
            if iStatus.recurring == "False":
                iStatus.applyEffect(target, iStatus.magnitude)
        
    def deactivate(self, target):
        # Also requires identical ordering of parameters, TODO
        for iStatus in self.internalList:
            iStatus.unapplyEffect(target, iStatus.magnitude)
            
    def upkeepActivate(self, target):
        """Only applies if this includes components that are to be
        applied on every upkeep phase."""
        for iStatus in self.internalList:
            if iStatus.recurring == "True":
                iStatus.applyEffect(target, iStatus.magnitude)
    
    
        
            

    
    
    