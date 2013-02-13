'''
Location Class
'''
from const import *

class Location(object):
    def __init__(self, pane, tile, direction=2):
        self.pane = pane
        self.tile = tile
        self.direction = direction

    # So it turns out __repr__ is like toString()
    def __repr__(self):
        return "(%s, %s, %d)" % (self.pane, self.tile, self.direction)

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

        if direction not in [2, 4, 6, 8]:
            dirs = None
            if self.direction in [2, 8]:
                dirs = {1: 2, 3: 2, 7: 8, 9: 8}
            if self.direction in [4, 6]:
                dirs = {1: 4, 3: 6, 7: 4, 9: 6}
            direction = dirs[direction]
            
        return Location(tuple(pane), tuple(tile), direction)
        
    def distance(self, dest):
        return  abs((self.pane[0] * PANE_X + self.tile[0]) - \
                (dest.pane[0] * PANE_X + dest.tile[0])) + \
                abs((self.pane[1] * PANE_Y + self.tile[1]) - \
                (dest.pane[1] * PANE_Y + dest.tile[1]))
                
    def in_melee_range(self, dest):
        if self.pane != dest.pane:
            return False
        if dest.tile in [(self.tile[0] + dx, self.tile[1] + dy) for dx in range(-1, 2) for dy in range(-1, 2)]:
            return True
        return False

if __name__ == "__main__":
    a = Location((3, 1), (15, 20))
    b = Location((3, 1), (5, 10))
    c = Location((3, 1), (15, 15))
    d = Location((3, 1), (0, 0))
    e = Location((0, 0), (0, 0))
    assert a.distance(b) == 20
    assert a.distance(c) == 5
    assert a.distance(d) == 35
    assert a.distance(e) == 151
    f = Location((3, 1), (15, 21))
    g = Location((3, 1), (15, 19))
    assert a.in_melee_range(b) == False
    assert a.in_melee_range(f) == True
    assert a.in_melee_range(g) == True
    h = Location((3, 1), (15, 18))
    assert a.in_melee_range(h) == False