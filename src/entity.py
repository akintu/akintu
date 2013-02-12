#!/usr/bin/python

import sys

class Entity(object):
    def __init__(self, location=None, team="Neutral", image=None, passable=False):
        self.location = location
        team = team.capitalize()
        if team not in ["Monsters", "Players", "Neutral"]:
            raise TypeError("Unkown entity team specified: " + team)
        self.team = team
        self.image = image
        self.passable = passable
