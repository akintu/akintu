#!/usr/bin/python

import sys
import equippeditems

class Inventory(object):
    MAX_SLOTS = 20
    
    def __init__(self):
	    self.allItems = []
		
    @property
    def totalWeight(self):
        tWeight = 0
        for item in self.allItems:
            tWeight += item.weight
        return tWeight