from location import Location
from const import *
import zlib
import os

class Region:
    def __init__(self, history=None):
        self.locations = set()
        self.history = [] if not history else zlib.decompress(history).split("\r\n")
        self.shape = {"SQUARE": self.square, "DIAMOND": self.diamond, "CIRCLE": self.circle,
                      "LINE": self.line, "CURVE": self.curve}
        if history:
            self.rehydrate()

    def __iter__(self):
        for x in self.locations:
            yield x

    def __contains__(self, item):
        return item in self.locations

    def __str__(self):
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
                        self.locations else "  "
            strrep += os.linesep
        return strrep
        
    def __repr__(self):
        return zlib.compress("\r\n".join(self.history), 9)

    def __call__(self, method, shape, *details):
        if shape.upper() in self.shape:
            if method.upper() == "ADD":
                self.locations |= self.shape[shape.upper()](*details)
            elif method.upper() == "SUB":
                self.locations -= self.shape[shape.upper()](*details)
            elif method.upper() == "INT":
                self.locations &= self.shape[shape.upper()](*details)
            elif method.upper() == "XOR":
                self.locations ^= self.shape[shape.upper()](*details)
            self.history.append(method + "|" + shape + "|" + "|".join([str(x) for x in details]))
            
    def __eq__(self, other):
        for L in self:
            if L not in other:
                return False
                
        for L in other:
            if L not in self:
                return False
        
        return True
            
    def dehydrate(self):
        return self.__repr__()
            
    def rehydrate(self):
        for line in self.history:
            parts = line.split("|")
            method = parts[0]
            shape = parts[1]
            details = parts[2:]
            for i, d in enumerate(details):
                try:
                    details[i] = int(d)
                except ValueError:
                    details[i] = Location(d)
            
            if shape.upper() in self.shape:
                if method.upper() == "ADD":
                    self.locations |= self.shape[shape.upper()](*details)
                elif method.upper() == "SUB":
                    self.locations -= self.shape[shape.upper()](*details)
                elif method.upper() == "INT":
                    self.locations &= self.shape[shape.upper()](*details)
                elif method.upper() == "XOR":
                    self.locations ^= self.shape[shape.upper()](*details)
                
    def square(self, loc1, loc2):
        locations = set()
        for y in loc1.line_to(Location(loc1.abs_x, loc2.abs_y)):
            for x in loc1.line_to(Location(loc2.abs_x, loc1.abs_y)):
                locations |= {Location(x.abs_x, y.abs_y)}
        return locations

    def diamond(self, loc, dist):
        locations = set()

        for x in loc.move(7, dist).line_to(loc.move(6, dist)):
            for y in loc.move(7, dist).line_to(loc.move(2, dist)):
                tile = Location(x.abs_x, y.abs_y)
                if loc.distance(tile) <= dist:
                    locations |= {tile}
        return locations

    def circle(self, loc, rad):
        locations = set()

        for x in loc.move(7, rad).line_to(loc.move(6, rad)):
            for y in loc.move(7, rad).line_to(loc.move(2, rad)):
                tile = Location(x.abs_x, y.abs_y)
                if round(loc.true_distance(tile)) <= rad:
                    locations |= {tile}
        return locations
        
    def line(self, loc1, loc2, width=1):
        locations = set()
        
        for x in range(-(width - 1) / 2, ((width - 1) / 2) + 1):
            if abs(loc1.abs_x - loc2.abs_x) > abs(loc1.abs_y - loc2.abs_y):
                locations |= set(Location(loc1.abs_x, loc1.abs_y + x).line_to(
                        Location(loc2.abs_x, loc2.abs_y + x)))
            else:
                locations |= set(Location(loc1.abs_x + x, loc1.abs_y).line_to(
                        Location(loc2.abs_x + x, loc2.abs_y)))
        return locations
        
    def curve(self, center, radius, width=1):
        locations = set()
        locations |= self.circle(center, radius + width / 2)
        locations -= self.circle(center, radius - width / 2)
        return locations

if __name__ == "__main__":
    R = Region()
    #This was my first test case.  I like the second one WAY better though!
    #R("ADD", "SQUARE", Location((0, 0), (5, 8)), Location((0, 0), (15, 18)))
    #R("SUB", "SQUARE", Location((0, 0), (7, 10)), Location((0, 0), (13, 16)))
    #R("ADD", "DIAMOND", Location((0, 0), (22, 10)), 5)
    #R("SUB", "DIAMOND", Location((0, 0), (22, 15)), 3)
    #R("ADD", "CIRCLE", Location((0, 0), (0, 0)), 8)
    #R("SUB", "CIRCLE", Location((0, 0), (0, 0)), 5)

    #Build region from shapes
    R("ADD", "SQUARE", Location(0, 0), Location(31, 19))
    R("SUB", "SQUARE", Location(1, 1), Location(30, 18))
    R("ADD", "CIRCLE", Location(16, 10), 7)
    R("SUB", "DIAMOND", Location(22, 10), 6)
    R("SUB", "SQUARE", Location(14, 6), Location(15, 7))
    R("ADD", "LINE", Location(20, 10), Location(22, 10), 3)
    #R("ADD", "CURVE", Location(20, 18), 5, 3)

    #Display the region
    print R

    l1 = Location(15, 10)
    assert l1 in R
    assert l1.move(6, 2) not in R
    for l2 in R:
        assert l2 in R
        
    S = Region(R.dehydrate())
    assert S == R