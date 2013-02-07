#!/usr/bin/python

import sys

class Entity(object):
    def __init__(self, location=None, team="Neutral", directionFacing=None, image=None):
        self.location = location
        self.directionFacing = directionFacing
        team = team.capitalize()
        if team not in ["Monsters", "Players", "Neutral"]:
            raise TypeError("Unkown entity team specified: " + team)
        self.team = team
        self.image = image
    
        
    