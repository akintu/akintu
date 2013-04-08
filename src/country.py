
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
        for x in range(COUNTRY_X):
            for y in range(COUNTRY_Y):
                township = Township(self.seed, country_loc=loc, township_loc=(x,y))
                self.townships[(x, y)] = township


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
                print "   Township: " + str(township.loc)
                print "\tTopLeft Pane: " + str(township.topLeft)
                print "\tCenter Pane: " + str(township.center)
