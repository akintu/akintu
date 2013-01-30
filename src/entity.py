#!/usr/bin/python

import sys

class Entity(object):
    def __init__(self, team="Neutral", location=None, directionFacing=None):
        self.location = location
        self.directionFacing = directionFacing
        if team.capitalize() not in ["Monsters", "Players", "Neutral"]:
            raise TypeError("Unkown entity team specified: " + team)
        self.team = team
        
    
        
    