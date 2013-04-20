#!/usr/bin/python

import sys
'''
entity.py
Author: Devin Ekins -- G. Cube

Entity is the base class for most objects that can be seen in Akintu.
This involves things such as Person (from which PlayerCharacter and Monster
are derived from) as well as Trap, Equipment (from which Armor and Weapon
are derived from) etc.

Only common functionalities should be present here, if possible.
'''
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
