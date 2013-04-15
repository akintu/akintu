'''
Location Class
'''
from const import *
import math
import re

class Location(object):
    def __init__(self, pane, tile=None, z=0, direction=2):
        if isinstance(pane, basestring):
            r = re.match(r'\((?P<p>\(.*\)|None), (?P<t>\(.*\)), (?P<z>.*), (?P<d>.*)\)', pane)
            if r.group('p') == "None":
                self.pane = None
            else:
                xy = r.group('p')[1:-1].split(', ')
                self.pane = (int(xy[0]), int(xy[1]))

            xy = r.group('t')[1:-1].split(', ')
            self.tile = (int(xy[0]), int(xy[1]))

            self.z = int(r.group('z'))
            self.direction = int(r.group('d'))
        else:
            if isinstance(pane, tuple) or pane is None:
                self.pane = pane
            else:
                self.pane = (pane // PANE_X, tile // PANE_Y)

            if isinstance(tile, tuple) or tile is None:
                self.tile = tile
            else:
                self.tile = (pane % PANE_X, tile % PANE_Y)

            self.z = z
            self.direction = direction

    # So it turns out __repr__ is like toString()
    def __repr__(self):
        return "(%s, %s, %d, %d)" % (self.pane, self.tile, self.z, self.direction)

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.pane == other.pane and self.tile == other.tile and self.z == other.z

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if self.abs_y == other.abs_y:
            return self.abs_x < other.abs_x
        else:
            return self.abs_y < other.abs_y

    def __le__(self, other):
        return self < other or self == other

    def __add__(self, other):
        return Location(self.abs_x + other[0], self.abs_y + other[1])

    def __hash__(self):
        x = self.abs_x
        y = self.abs_y
        strrep = ("9" if x < 0 else "") + str(abs(x)) + "0" + \
                ("9" if y < 0 else "") + str(abs(y)) + "0" + \
                ("9" if self.z < 0 else "") + str(abs(self.z))
        return int(strrep)
#        str = "%d0%d0%d" % (self.abs_x, self.abs_y, self.z)
#        return int(str.replace("-", "9"))

    @property
    def abs_x(self):
        if self.pane:
            return self.pane[0] * PANE_X + self.tile[0]
        else:
            return self.tile[0]

    @property
    def abs_y(self):
        if self.pane:
            return self.pane[1] * PANE_Y + self.tile[1]
        else:
            return self.tile[1]

    @property
    def abs_pos(self):
        return (self.abs_x, self.abs_y)

    def move(self, direction, distance=1):
        '''
        Direction is number based (with diagonals)
        See diagram:
                 UP
             7   8   9
        LEFT 4   5   6 RIGHT
             1   2   3
                DOWN
        '''

        if direction == 5:
            return self

        tile = list(self.tile)
        pane = list(self.pane)

        tile[0] += distance * (((direction - 1) % 3) - 1)  # Second operand works out to -1, 0, or 1
        tile[1] -= distance * (((direction - 1) // 3) - 1) # depending on what column or row it is in

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

        return Location(tuple(pane), tuple(tile), self.z, direction)

    def get_opposite_tile(self, edge):
        x = self.tile[0]
        y = self.tile[1]
        # if x in [0, PANE_X-1]:
            # x = math.fabs(self.tile[0] - (PANE_X - 1))
        # if y in [0, PANE_Y-1]:
            # y = math.fabs(self.tile[1] - (PANE_Y - 1))
        if edge in [4, 6, 1, 3, 7, 9]:
            x = int(math.fabs(x - (PANE_X - 1)))
        if edge in [2, 8, 1, 3, 7, 9]:
            y = int(math.fabs(y - (PANE_Y - 1)))
        return Location(self.pane, tuple((x, y)), self.z)

    def get_surrounding_panes(self):
        '''
        Gets the locations of surrounding panes

        Suppose self.pane = (0, 0)
        This will return a dictionary of locations with
        the following keys and values:
            1: BOTTOM_LEFT  (-1, 1)
            2: DOWN         ( 0, 1)
            3: BOTTOM_RIGHT ( 1, 1)
            4: LEFT         (-1, 0)
            5: CURRENT PANE ( 0, 0)
            6: RIGHT        ( 1, 0)
            7: TOP_LEFT     (-1,-1)
            8: UP           ( 0,-1)
            9: TOP_RIGHT    ( 1,-1)
        '''

        return {((-dy + 1) * 3) + dx + 2: \
            (self.pane[0] + dx, self.pane[1] + dy) for dx in range(-1, 2) for dy in range(1, -2, -1)}

    def get_surrounding_tiles(self):
        '''
        Gets the locations of the surrounding tiles
        Only returns locations on the current pane, so edge cases will
        contain invalid tile locations.
        Returns a dictionary with the facing direction as the key
        '''

        return {((-dy + 1) * 3) + dx + 2: \
            (self.tile[0] + dx, self.tile[1] + dy) for dx in range(-1, 2) for dy in range(1, -2, -1)}

    def line_to(self, dest, diags=True):
        if self == dest:
            return [self]

        locs = []
        distx = dest.abs_x - self.abs_x
        disty = dest.abs_y - self.abs_y
        dist = max(abs(distx), abs(disty))
        for x in range(dist + 1):
            locs.append(Location(self.abs_x + int(round(float(x) / dist * distx)),
                    self.abs_y + int(round(float(x) / dist * disty)), self.z))

        if not diags:
            for i, l in enumerate(locs):
                if i < len(locs) - 1:
                    if l.direction_to(locs[i+1]) % 2:
                        locs.insert(i + 1, Location(locs[i+1].abs_x, l.abs_y))

        return locs

    def direction_to(self, dest):
        if self == dest:
            return 5
        distx = dest.abs_x - self.abs_x
        #disty is negated because our y axis in game is flipped from the cartesian plane
        disty = -(dest.abs_y - self.abs_y)
        mag = self.true_distance(dest)

        x = distx / mag
        y = disty / mag

        x = 1 if abs(x) < 0.38268343236508984 else cmp(x, 0) + 1
        y = 1 if abs(y) < 0.38268343236508984 else cmp(y, 0) + 1
        return int((y * 3) + x + 1)

    def distance(self, dest):
        return  abs(self.abs_x - dest.abs_x) + abs(self.abs_y - dest.abs_y)

    def true_distance(self, dest):
        return math.sqrt((self.abs_x - dest.abs_x)**2 + (self.abs_y - dest.abs_y)**2)

    def in_melee_range(self, dest):
        if self.pane != dest.pane or self.z != dest.z:
            return False
        if dest.tile in [(self.tile[0] + dx, self.tile[1] + dy) for dx in range(-1, 2) \
                for dy in range(-1, 2)]:
            return True
        return False

if __name__ == "__main__":
    a = Location((3, 1), (15, 20))
    b = Location((3, 1), (5, 10))
    c = Location((3, 1), (15, 15))
    d = Location((3, 1), (0, 0))
    e = Location((0, 0), (0, 0))
    assert a.distance(b) == 20
    assert a.distance(b) == b.distance(a)
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
    assert a.true_distance(b) == math.sqrt(200)

    #TEST get_surrounding_panes()
    i = Location((0, 0), None)
    panes = i.get_surrounding_panes()
    assert panes[1] == (-1, 1)  # 1: BOTTOM_LEFT  (-1, 1)
    assert panes[2] == (0, 1)   # 2: DOWN         ( 0, 1)
    assert panes[3] == (1, 1)   # 3: BOTTOM_RIGHT ( 1, 1)
    assert panes[4] == (-1, 0)  # 4: LEFT         (-1, 0)
    assert panes[5] == i.pane   # 5: CURRENT PANE ( 0, 0)
    assert panes[6] == (1, 0)   # 6: RIGHT        ( 1, 0)
    assert panes[7] == (-1,-1)  # 7: TOP_LEFT     (-1,-1)
    assert panes[8] == (0,-1)   # 8: UP           ( 0,-1)
    assert panes[9] == (1,-1)   # 9: TOP_RIGHT    ( 1,-1)

    #TEST get_opposite_tile()
    j = Location(None, (0, 0))
    k = Location(None, (0, 1))
    l = Location(None, (1, 0))
    m = Location(None, (4, PANE_Y-1))

    assert j.get_opposite_tile(7).tile == (PANE_X-1, PANE_Y-1)
    assert j.get_opposite_tile(4).tile == (PANE_X-1, 0)
    assert j.get_opposite_tile(8).tile == (0, PANE_Y-1)
    assert k.get_opposite_tile(4).tile == (PANE_X-1, 1)
    assert l.get_opposite_tile(8).tile == (1, PANE_Y-1)
    assert m.get_opposite_tile(2).tile == (4, 0)

    assert j < k
    assert k > j
    assert j <= k
    assert k >= j
    assert j != k
    assert j == j

    assert Location(5, 5).direction_to(Location(3, 7)) == 1
    assert Location(5, 5).direction_to(Location(5, 7)) == 2
    assert Location(5, 5).direction_to(Location(7, 7)) == 3
    assert Location(5, 5).direction_to(Location(3, 5)) == 4
    assert Location(5, 5).direction_to(Location(5, 5)) == 5
    assert Location(5, 5).direction_to(Location(7, 5)) == 6
    assert Location(5, 5).direction_to(Location(3, 3)) == 7
    assert Location(5, 5).direction_to(Location(5, 3)) == 8
    assert Location(5, 5).direction_to(Location(7, 3)) == 9

    radius = 15
    for y in range(0, 2 * radius + 1):
        strrep = ""
        for x in range(0, 2 * radius + 1):
            strrep += str(Location(radius, radius).direction_to(Location(x, y))) + " "
        print strrep

    n = Location(b.__str__())
    assert n == b