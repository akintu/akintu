#!/usr/bin/python

import sys

class Entity(object):
    def __init__(self, location=None, team="Neutral", image=None, passable=False,
                 cLocation=None, cPane=None):
        self.location = location
        team = team.capitalize()
        if team not in ["Monsters", "Players", "Neutral"]:
            raise TypeError("Unkown entity team specified: " + team)
        self.team = team
        self.image = image
        self.passable = passable
        self.cPane = None
        self.cLocation = None

    def getAnimationImages(self):
        print "Called unimplemented method Entity.getAnimationImages()."
        print "You must override this function in child implementation."
        pass
        
    def getAnimationSpeed(self):
        print "Called unimplemented method Entity.getAnimationSpeed()."
        print "You must override this function in child implementation."
        pass