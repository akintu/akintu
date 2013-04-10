
import pygame
import random

from const import*
from region import*
from township import*

class Country(object):
    '''
    COUNTRY:
        A set number of Township objects with it's size 
        COUNTRY_X, COUNTRY_Y defined in const.py
    '''

    def __init__(self, seed, loc=(0,0)):
        self.seed = seed
        self.loc = loc

        self.townships = dict()
        self.towns = []
        self.stamps = dict()
        for x in range(COUNTRY_X):
            for y in range(COUNTRY_Y):
                t = Township(self.seed, country_loc=loc, township_loc=(x,y))
                # t.addTown()
                # t.addDungeons(5)
                t.loadStamps(5)
                self.townships[(x, y)] = t
                self.towns.append(t.town_loc)
                self.stamps = dict(self.stamps.items() + t.stamps.items())

    def getStamps(self, pane):
        if pane in self.stamps:
            # print self.stamps[pane]
            return self.stamps[pane]
        # print str(pane) + " not found in country stamp dictionary"
        # print self.stamps.keys()
        country_loc, township_loc = Township.getTownshipLocation(pane)
        if township_loc in self.townships:
            t = self.townships[township_loc]
            if pane in t.stamps:
                return t.stamps[pane]
        return None


if __name__ == "__main__":
    '''
    Run some Tests
    '''

    for x in range(2):
        for y in range(1):
            c = Country("SOME NEW SEED", (x,y))
            print "_"*40
            print "COUNTRY: " + str((x, y))
            for loc, township in c.townships.iteritems():
                
                print "   Township: " + str(township.loc[1])
                print "\tTopLeft Pane: " + str(township.topLeft)
                print "\tCenter Pane: " + str(township.center)
                print township.stamps
