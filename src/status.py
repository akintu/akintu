#!/usr/bin/python

import sys

class Status(object):
    def __init__(self):
        self.displayName = None
        self.element = None
        self.categoryList = None
        self.turnsLeft = None
        self.internalList = None
        #self._recurring = None #boolean
        self.persistent = None #boolean
        
        self._loadedFromFile = False
        # TODO: where should we indicate persistence?
        
    @property
    def loadedFromFile(self):
        """Indicates whether this file has already had its properties loaded
        from a text file."""
        return self._loadedFromFile
        
    def populateFromFile(self, name, element, categoryList, internalList):
        """Populates the fields of this status from the information gained
        through a parser from a txt file."""
        if( self._loadedFromFile ):
            return
        self.displayName = name
        self.element = element
        self.categoryList = categoryList
        self.internalList = internalList
        self._loadedFromFile = True
    
    
    