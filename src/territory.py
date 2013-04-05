'''
TERRITORY: 
    Contains a set number of panes with the size
    defined in const.py (TERRITORY_X, TERRITORY_Y)
    Each territory contains 1 Town (Pane) object
    And will have at least 1 dungeon
'''

from const import *
from region import *

class Territory(object):
    def __init__(self, territory_tuple):
