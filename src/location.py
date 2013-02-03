'''
Location Class
'''
from const import *

class Location(object):
    def __init__(self, pane, tile):
        self.pane = pane
        self.tile = tile
        
    def move(self, direction, distance):
        '''
        Direction is number based (with diagonals)
        See diagram:
                 UP
             7   8   9 
        LEFT 4       6 RIGHT
             1   2   3
                DOWN
        '''
        
        tile = list(self.tile)
        pane = list(self.pane)
        #LEFT
        if direction in [1, 4, 7]:
            tile[0] -= distance
        #RIGHT
        if direction in [3, 6, 9]:
            tile[0] += distance
        #UP
        if direction in [7, 8, 9]:
            tile[1] -= distance
        #DOWN
        if direction in [1, 2, 3]:    
            tile[1] += distance
        
        #LEFT PANE
        while tile[0] < 0:
            tile[0] += PANE_X
            pane[0] -= 1
        #RIGHT PANE
        while tile[0] >= PANE_X:
            tile[0] -= PANE_X
            pane[0] += 1
        #UP PANE
        while tile[1] < 0:
            tile[1] += PANE_Y
            pane[1] -= 1
        #DOWN PANE
        while tile[1] >= PANE_Y:
            tile[1] -= PANE_Y
            pane[1] += 1
        
        return Location(tuple(pane), tuple(tile))