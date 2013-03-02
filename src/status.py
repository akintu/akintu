#!/usr/bin/python

import sys
import internalstatus

class Status(object):
    def __init__(self):
        # Values loaded at startup time
        self.name = None
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
        self.name = name
        self.element = element
        self.categoryList = categoryList
        self.internalList = internalList
        
    def applyMagnitude(self, magnitude): 
        """If no magnitude is provided, use the value given from the data
        file."""
        for item in self.internalList:
            if item.magnitude == 0:
                item.magnitude = magnitude
    
    def cloneWithDetails(self, magnitude, duration):
        clone = Status()
        clone.populate(self.name, self.element, self.categoryList, self.internalList)
        clone.turnsLeft = duration
        clone.applyMagnitude(magnitude)
        for iStatus in clone.internalList:
            iStatus.element = clone.element
        return clone
        
    def activate(self, target):
        for iStatus in self.internalList:
            if iStatus.recurring == "False":
                iStatus.applyEffect(iStatus, target, iStatus.magnitude)
        
    def deactivate(self, target):
        for iStatus in self.internalList:
            if iStatus.unapplyEffect:
                iStatus.unapplyEffect(iStatus, target, iStatus.magnitude)
            
    def upkeepActivate(self, target):
        """Only applies if this includes components that are to be
        applied on every upkeep phase."""
        for iStatus in self.internalList:
            if iStatus.recurring == "True":
                iStatus.applyEffect(iStatus, target, iStatus.magnitude)
    
    
        
            

    
    
    