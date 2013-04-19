
import pygame
import random

from const import*
from region import*
from township import*

class Country(object):
    '''
    A group of Township objects and their stamps.
    Also maintains a list of all the towns near where
    we have visited; e.g. when you first start the game, 
    there will be 1 town in self.towns.  As you wander 
    into different townships, the list grows.
    '''

    def __init__(self, seed, country_loc=(0,0)):
        self.seed = seed
        self.country_loc = country_loc

        self.townships = dict()
        self.towns = []
        self.stamps = dict()

    def getStamps(self, pane):
        '''
        Checks to see if we've loaded the township this pane
        belongs to.  If not, we create a new one by calling 
        self.addTownship.

        Returns the stamp(s) associated with the requested 
        pane
        '''

        if pane in self.stamps:
            return self.stamps[pane]
        country_loc, township_loc = Township.getTownshipLocation(pane)
        if not township_loc in self.townships:
            self.addTownship(township_loc)
            t = self.townships[township_loc]
            if pane in t.stamps:
                return t.stamps[pane]
        return None

    def addTownship(self, township_loc):
        '''
        Creates a new Township object and adds it to this country's
        townships dictionary.
        Pulls out the stamps and adds them to this country's stamps
        list.
        '''

        t = Township(self.seed, country_loc=self.country_loc, township_loc=township_loc)
        t.loadStamps()
        self.townships[township_loc] = t
        self.towns.append(t.town_loc)
        self.stamps = dict(self.stamps.items() + t.stamps.items())

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
