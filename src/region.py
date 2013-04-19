from location import Location
from const import *
import zlib
import cPickle
import os
import re

class Region:
    def __init__(self, *args):
        '''
        Initializer accepts several different possible inputs.  They are:
            * a Region object, which it copies
            * a list of Location objects, which it converts to a Region one at a time
            * a serialized Region, which it deserializes
            * a shape creation command, as per the __call__ method, with the small difference
                that for the first shape, only the "ADD" method is supported, so that argument is
                completely omitted.
        '''
        self.locations = set()
        self.history = []
        if len(args) == 1:
            if isinstance(args[0], Region):
                self.history = args[0].history[:]
                self.locations = args[0].locations.copy()
            elif isinstance(args[0], list):
                for l in args[0]:
                    self.__call__("ADD", "CIRCLE", l, 0)
            else:
                self.rehydrate(args[0])
        elif len(args) > 1:
            self.__call__("ADD", *args)

    def __iter__(self):
        for x in self.locations:
            yield x

    def __contains__(self, item):
        return item in self.locations

    def __str__(self):
        '''
        Returns a picture of the region using ascii characters.
        The edges of the printed area are determined by scanning the region for the extreme locations
            on each of the four direction boundaries.
        '''
        if len(self.locations) == 0:
            return ""
        left = right = top = bottom = self.locations.pop()
        self.locations.add(left)
        for loc in self.locations:
            if loc.pane[0] < left.pane[0] or \
                    (loc.pane[0] == left.pane[0] and loc.tile[0] < left.tile[0]):
                left = loc
            if loc.pane[0] > right.pane[0] or \
                    (loc.pane[0] == right.pane[0] and loc.tile[0] > right.tile[0]):
                right = loc
            if loc.pane[1] < top.pane[1] or \
                    (loc.pane[1] == top.pane[1] and loc.tile[1] < top.tile[1]):
                top = loc
            if loc.pane[1] > bottom.pane[1] or \
                    (loc.pane[1] == bottom.pane[1] and loc.tile[1] > bottom.tile[1]):
                bottom = loc
        strrep = ""
        for y in Location(left.abs_x, top.abs_y).line_to(Location(left.abs_x, bottom.abs_y)):
            for x in Location(left.abs_x, top.abs_y).line_to(Location(right.abs_x, top.abs_y)):
                strrep += "@ " if Location((x.pane[0], y.pane[1]), (x.tile[0], y.tile[1])) in \
                        self.locations else ". "
            strrep += os.linesep
        return strrep

    def __repr__(self):
        return zlib.compress(cPickle.dumps(self.history), 9)

    def __call__(self, method, shape, *details):
        '''
        Creates a new shape and performs a specified set operation with the locations in that shape
        against the locations currently in the Region.
        Currently supported set operation methods include:
            * ADD (Union)
            * SUB (Difference)
            * INT (Intersection)
            * XOR (Exclusive Or)
        Currently supported shapes include:
            * SQUARE
            * CIRCLE
            * DIAMOND
            * LINE
        Details are shape specific, see their individual method documentation for details.
        '''
        if method.upper() == "SHIFT":
            temp = set()
            for l in self.locations:
                temp.add(l + shape)
            self.locations = temp
        elif hasattr(self, shape.lower()):
            if method.upper() == "ADD":
                self.locations |= getattr(self, shape.lower())(*details)
            elif method.upper() == "SUB":
                self.locations -= getattr(self, shape.lower())(*details)
            elif method.upper() == "INT":
                self.locations &= getattr(self, shape.lower())(*details)
            elif method.upper() == "XOR":
                self.locations ^= getattr(self, shape.lower())(*details)

        hist = {}
        hist['method'] = method
        hist['shape'] = shape
        hist['details'] = details
        self.history.append(hist)

    def __eq__(self, other):
        return all(x in other for x in self) and all (x in self for x in other)

    #All set operators supported in Python are also supported for Regions, as Regions are just sets
    #with convenience methods for populating the set.  These include |, -, &, ^
    def __add__(self, other):
        R = Region(self)
        R("ADD", "REGION", other)
        return R

    def __or__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        R = Region(self)
        R("SUB", "REGION", other)
        return R

    def __and__(self, other):
        R = Region(self)
        R("INT", "REGION", other)
        return R

    def __xor__(self, other):
        R = Region(self)
        R("XOR", "REGION", other)
        return R

    def __lshift__(self, other):
        R = Region(self)
        R("SHIFT", other)
        return R

    #dehydrate, rehydrate, getstate, and setstate are all used in Region serialization.
    #Most regions are just used as a glorified iterator, but serialization is used in monster AI saving
    def dehydrate(self):
        return self.__repr__()

    def rehydrate(self, history):
        if not isinstance(history, list):
            history = cPickle.loads(zlib.decompress(history))
        for line in history:
            self(line['method'], line['shape'], *line['details'])

    def __getstate__(self):
        return self.__repr__()

    def __setstate__(self, state):
        self.locations = set()
        self.history = []
        self.rehydrate(state)

    def __len__(self):
        return len(self.locations)

    def __getitem__(self, key):
        if len(self.locations) == 0:
            return None
        return list(self.locations)[key]


    def square(self, loc1, loc2):
        '''
        Accepts one of two formats for construction:
            * loc1 and loc2 are both Locations corresponding to opposite corners of a quadrilateral
            * loc1 is the center Location of a square with a diagonal of length loc2 * 2
                In this method, loc2 is like a radius of sorts for the square
        '''
        locations = set()

        if not isinstance(loc2, Location):
            d = loc2
            loc2 = loc1.move(3, d)
            loc1 = loc1.move(7, d)

        for y in loc1.line_to(Location(loc1.abs_x, loc2.abs_y)):
            for x in y.line_to(Location(loc2.abs_x, y.abs_y)):
                locations |= {x}
        return locations

    def diamond(self, loc, dist):
        '''
        Creates a diamond shape centered on loc, with a total distance to each edge Location of dist
        See Location.distance() for more details on the distance calculation
        '''
        locations = set()

        for x in loc.move(7, dist).line_to(loc.move(9, dist)):
            for y in x.line_to(x.move(2, dist * 2)):
                if loc.distance(y) <= dist:
                    locations |= {y}
        return locations

    def circle(self, loc, rad):
        '''
        Creates a circle centered at loc with radius rad
        '''
        locations = set()

        for x in loc.move(7, rad).line_to(loc.move(9, rad)):
            for y in x.line_to(x.move(2, rad * 2)):
                if round(loc.true_distance(y)) <= rad:
                    locations |= {y}
        return locations

    def line(self, loc1, loc2, width=1):
        '''
        Creates a line from loc1 to loc2 that is width tiles wide
        '''
        locations = set()

        for x in range(-(width - 1) / 2, ((width - 1) / 2) + 1):
            if abs(loc1.abs_x - loc2.abs_x) > abs(loc1.abs_y - loc2.abs_y):
                locations |= set(Location(loc1.abs_x, loc1.abs_y + x).line_to(
                        Location(loc2.abs_x, loc2.abs_y + x)))
            else:
                locations |= set(Location(loc1.abs_x + x, loc1.abs_y).line_to(
                        Location(loc2.abs_x + x, loc2.abs_y)))
        return locations

if __name__ == "__main__":
    R = Region()

    #Build region from shapes
    R("ADD", "SQUARE", Location(0, 0), Location(31, 19))
    R("SUB", "SQUARE", Location(1, 1), Location(30, 18))
    R("ADD", "CIRCLE", Location(16, 10), 7)
    R("SUB", "DIAMOND", Location(22, 10), 6)
    R("SUB", "SQUARE", Location(14, 6), Location(15, 7))
    R("ADD", "LINE", Location(20, 10), Location(22, 10), 3)
    #R("ADD", "CURVE", Location(20, 18), 5, 3)

    T = Region()
    T("ADD", "DIAMOND", Location(0, 0), 4)
    T <<= (2, 3)        #Shifts all Locations in T 2 tiles to the right, and 3 tiles down
    R("XOR", "REGION", T)

    #These two lines do the exact same thing.  However, the first is preferred as it only creates
    #a shape in generating the mask, as opposed to an entire Region.  Therefore, the serialization
    #of R after the first call is smaller than the serialization of R after only running the second
    #line.
    R("INT", "SQUARE", Location(0, 0), Location(31, 19))
    R &= Region("SQUARE", Location(0, 0), Location(31, 19))

    l1 = Location(15, 10)
    assert l1 in R
    R("XOR", "SQUARE", Location(0, 0), Location(31, 19))
    assert l1 not in R
    R ^= Region("SQUARE", Location(0, 0), Location(31, 19))
    assert l1 in R
    print R

    assert l1.move(6, 2) not in R
    for l2 in R:
        assert l2 in R

    S = Region(R)
    assert S == R
    S("ADD", "LINE", Location(0, 0), Location(31, 19), 3)
    S("ADD", "LINE", Location(0, 19), Location(31, 0), 3)
    assert S != R
    S = Region(R.dehydrate())
    assert S == R
    S("ADD", "CIRCLE", Location(4, 12), 3)
    assert S != R

    assert Location(0, 0) in Region("CIRCLE", Location(0, 0), 10)