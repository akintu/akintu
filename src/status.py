#!/usr/bin/python

import sys
import internalstatus

ROOT = "./res/images/icons/"
    
class Status(object):

    DEFAULT_IMAGE = "./res/icons/cubeforce.svg"
    
    
    def __init__(self):
        # Values loaded at startup time
        self.name = None
        self.element = None
        self.categoryList = None
        self.internalList = None
        self.image = None
        self.text = ""
        
        # Values given to individual instances of this Status
        self.turnsLeft = None
        self.stacks = 1
        self.charges = None

    def populate(self, name, image, element, categoryList, internalList):
        """Populates the fields of this status from the information gained
        through a parser from a txt file or a previously created displaystatus."""
        self.name = name
        if image.startswith(ROOT):
            self.image = image
        else:
            self.image = ROOT + image
        if image == ROOT + "None":
            self.image = Status.DEFAULT_IMAGE
        self.element = element
        self.categoryList = categoryList
        self.internalList = internalList
        for internal in internalList:
            if internal:
                self.text += internal.staticText.format(ELE=self.element) + "\n"

    def applyMagnitude(self, magnitude):
        """If no magnitude is provided, use the value given from the data
        file."""
        for item in self.internalList:
            if item.magnitude < 0:
                item.magnitude = magnitude * abs(item.magnitude)
            if item.magnitude == 0:
                item.magnitude = magnitude

    def cloneWithDetails(self, magnitude, duration):
        clone = Status()
        clone.populate(self.name, self.image, self.element, self.categoryList, self.internalList)
        clone.turnsLeft = duration
        clone.applyMagnitude(magnitude)
        clone.text = ""
        for iStatus in clone.internalList:
            iStatus.element = clone.element
            iStatus.duration = duration
            iStatus.updateText()
            clone.text += iStatus.text + "\n"
        return clone

    def activate(self, target):
        for iStatus in self.internalList:
            if iStatus.recurring == "False" and iStatus.applyEffect:
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







