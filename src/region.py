from location import Location
from const import *

RAct = enum(ADD = 1, SUBTRACT = 2)
RShape = enum(SQUARE = 1, DIAMOND = 2, CIRCLE = 3, LINE = 4)

class Region:
    def __init__(self):
        self.locations = set()
        
    def __iter__(self):
        temp = self.locations
        while len(temp):
            yield temp.pop()

    def build(self, method, shape, *details):
        if shape == RShape.SQUARE:
            if method == RAct.ADD:
                self.locations |= self.square(*details)
            else:
                self.locations -= self.square(*details)
        if shape == RShape.DIAMOND:
            if method == RAct.ADD:
                self.locations |= self.diamond(*details)
            else:
                self.locations -= self.diamond(*details)
        if shape == RShape.CIRCLE:
            if method == RAct.ADD:
                self.locations |= self.circle(*details)
            else:
                self.locations -= self.circle(*details)

    def square(self, loc1, loc2):
        locations = set()

        pane_x = min(loc1.pane[0], loc2.pane[0])
        pane_y = min(loc2.pane[1], loc2.pane[1])
        tile_x = loc1.tile[0] if loc1.pane[0] < loc2.pane[0] or (loc1.pane[0] == loc2.pane[0] and \
            loc1.tile[0] <= loc2.tile[0]) else loc2.tile[0]
        tile_y = loc1.tile[1] if loc1.pane[1] < loc2.pane[1] or (loc1.pane[1] == loc2.pane[1] and \
            loc1.tile[1] <= loc2.tile[1]) else loc2.tile[1]
        top_left = Location((pane_x, pane_y), (tile_x, tile_y))

        pane_x = max(loc1.pane[0], loc2.pane[0])
        pane_y = max(loc2.pane[1], loc2.pane[1])
        tile_x = loc1.tile[0] if loc1.pane[0] > loc2.pane[0] or (loc1.pane[0] == loc2.pane[0] and \
            loc1.tile[0] >= loc2.tile[0]) else loc2.tile[0]
        tile_y = loc1.tile[1] if loc1.pane[1] > loc2.pane[1] or (loc1.pane[1] == loc2.pane[1] and \
            loc1.tile[1] >= loc2.tile[1]) else loc2.tile[1]
        bottom_right = Location((pane_x, pane_y), (tile_x, tile_y))

        col = top_left
        for y in range(top_left.pane[1] * PANE_Y + top_left.tile[1], \
                        bottom_right.pane[1] * PANE_Y + bottom_right.tile[1] + 1):
            tile = col
            for x in range(top_left.pane[0] * PANE_X + top_left.tile[0], \
                            bottom_right.pane[0] * PANE_X + bottom_right.tile[0] + 1):
                locations |= {Location(tile.pane, tile.tile)}
                tile = tile.move(6, 1)
            col = col.move(2, 1)

        return locations

    def diamond(self, loc, dist):
        locations = set()
        top_left = loc.move(7, dist)
        bottom_right = loc.move(3, dist)

        col = top_left
        for x in range(top_left.pane[0] * PANE_X + top_left.tile[0], \
                        bottom_right.pane[0] * PANE_X + bottom_right.tile[0] + 1):
            tile = col
            for y in range(top_left.pane[1] * PANE_Y + top_left.tile[1], \
                            bottom_right.pane[1] * PANE_Y + bottom_right.tile[1] + 1):
                if loc.distance(tile) <= dist:
                    locations |= {Location(tile.pane, tile.tile)}
                tile = tile.move(6, 1)
            col = col.move(2, 1)

        return locations

    def circle(self, loc, rad):
        locations = set()
        top_left = loc.move(7, rad)
        bottom_right = loc.move(3, rad)

        col = top_left
        for x in range(top_left.pane[0] * PANE_X + top_left.tile[0], \
                        bottom_right.pane[0] * PANE_X + bottom_right.tile[0] + 1):
            tile = col
            for y in range(top_left.pane[1] * PANE_Y + top_left.tile[1], \
                            bottom_right.pane[1] * PANE_Y + bottom_right.tile[1] + 1):
                if loc.radius(tile) <= rad:
                    locations |= {Location(tile.pane, tile.tile)}
                tile = tile.move(6, 1)
            col = col.move(2, 1)

        return locations

    def has(self, location):
        return location in self.locations

if __name__ == "__main__":
    R = Region()
    #This was my first test case.  I like the second one WAY better though!
    #R.build(RAct.ADD, RShape.SQUARE, Location((0, 0), (5, 8)), Location((0, 0), (15, 18)))
    #R.build(RAct.SUBTRACT, RShape.SQUARE, Location((0, 0), (7, 10)), Location((0, 0), (13, 16)))
    #R.build(RAct.ADD, RShape.DIAMOND, Location((0, 0), (22, 10)), 5)
    #R.build(RAct.SUBTRACT, RShape.DIAMOND, Location((0, 0), (22, 15)), 3)
    #R.build(RAct.ADD, RShape.CIRCLE, Location((0, 0), (0, 0)), 8)
    #R.build(RAct.SUBTRACT, RShape.CIRCLE, Location((0, 0), (0, 0)), 5)

    #Build region from shapes
    R.build(RAct.ADD, RShape.SQUARE, Location((0, 0), (0, 0)), Location((0, 0), (31, 19)))
    R.build(RAct.SUBTRACT, RShape.SQUARE, Location((0, 0), (1, 1)), Location((0, 0), (30, 18)))
    R.build(RAct.ADD, RShape.CIRCLE, Location((0, 0), (16, 10)), 7)
    R.build(RAct.SUBTRACT, RShape.DIAMOND, Location((0, 0), (22, 10)), 6)
    R.build(RAct.SUBTRACT, RShape.SQUARE, Location((0, 0), (14, 6)), Location((0, 0), (15, 7)))

    #Display the region
    for y in range(PANE_Y):
        line = ""
        for x in range(PANE_X):
            line += "@ " if R.has(Location((0, 0), (x, y))) else ". "
        print line

    l1 = Location((0, 0), (15, 10))
    assert R.has(l1)
    assert not R.has(l1.move(6, 2))