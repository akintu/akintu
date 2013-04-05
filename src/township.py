'''
TOWNSHIP: 
    Contains a set number of panes with the size
    defined in const.py (TOWNSHIP_X, TOWNSHIP_Y)
    Each territory contains 1 Town (Pane) object
    and will have at least 1 dungeon
'''

from const import *
from region import *

class Township(object):
    def __init__(self, pane, seed):
        self.stampsLoaded = False
        if isinstance(pane, Location):
            pane = pane.pane
        if not isinstance(pane, tuple):
            pane = None
        
        self.x, self.y = Township.getTownshipLocation(pane)
        self.topLeft = Township.getTownshipTopLeft(None, pane_loc=pane)
        self.tile_width = PANE_X * TOWNSHIP_X
        self.tile_height = PANE_Y * TOWNSHIP_Y

        self.tile_region = Region()
        self.tile_region("ADD", "SQUARE", Location((0,0), (0, 0)), Location((TOWNSHIP_X-1, TOWNSHIP_Y-1), (PANE_X-1,PANE_Y-1)))

    def loadStamps(self):
        if self.stampsLoaded:
            print "Township.loadStamps has already been called"
            return
        self.stampsLoaded = True
        for pane, region in self.paneRegions:
            pass

    def getPaneRegion(self, pane):
        pass

    @staticmethod
    def getTownshipLocation(pane):
        '''
        The x,y coordinate of this township. i.e. if a township is
        a 5x5 group of panes, pane (0, 0) is in the center.

        For Example:

            TOWNSHIP (0,0)          TOWNSHIP (1,0)          TOWNSHIP (2,0)
            #   # (0,-2)#   #    (3,-2) #   #   #   #    (8,-2) #   #   #   #
            #   #   #   #   #       #   #   #   #   #       #   #   #   #   #
            #   # (0,0) #   #       #   # (5,0) #   #       #   #(10,0) #   #
            #   #   #   #   #       #   #   #   #   #       #   #   #   #   #
            #   #   #   #   #       #   #   #   #   #       #   #   #   #   #

        '''

        loc_x = ((pane[0] + TOWNSHIP_X/2)/TOWNSHIP_X)
        loc_y = ((pane[1] + TOWNSHIP_Y/2)/TOWNSHIP_Y)
        return (loc_x, loc_y)

    @staticmethod
    def getTownshipTopLeft(township_loc, pane_loc):
        '''
        Given a township location tuple or a pane location tuple
        returns the top left pane of that township
        
        For Example:
            township_loc((0,0))
        '''
        if pane_loc:
            tmp = Township.getTownshipLocation(pane_loc)
            if township_loc:
                assert township_loc == tmp,\
                    "You supplied both a township_loc and pane_loc and they do not\n\
                    correspond to the same township. Supply one or the other."
            else:
                township_loc = tmp
        loc_x = TOWNSHIP_X*township_loc[0] - TOWNSHIP_X/2
        loc_y = TOWNSHIP_Y*township_loc[1] - TOWNSHIP_Y/2
        return (loc_x, loc_y)

def test_parameters(pane, town, topLeft):
    # topLeft = (TOWNSHIP_X*town[0]-TOWNSHIP_X/2, town[1]-TOWNSHIP_Y/2)
    print "Testing pane " + str(pane) + " is in township " + str(town)
    print "\tAnd top left is " + str(topLeft) + " from center"
    t = Township(pane, "TEST SEED")
    assert len(set(t.tile_region)) == PANE_X * PANE_Y * TOWNSHIP_X * TOWNSHIP_Y
    assert t.x == town[0] and t.y == town[1], "township.x: " + str(t.x) + ", township.y: " + str(t.y)
    assert t.topLeft == topLeft, "township.topLeft: " + str(t.topLeft) + " Supplied: " + str(topLeft)

if __name__=="__main__":
    r = Region()
    print r
    test_parameters((0,0), (0, 0), (-2,-2))
    test_parameters((TOWNSHIP_X,0), (1, 0), (3, -2))
    test_parameters((0,-TOWNSHIP_Y), (0, -1), (-2, -7))
    test_parameters((-3,3), (-1, 1), (-7,3))
    test_parameters((3,-3), (1, -1), (3,-7))
    test_parameters((-2,2), (0, 0), (-2,-2))
    test_parameters((TOWNSHIP_X*5,2), (5, 0), (23,-2))
    test_parameters((-2,TOWNSHIP_Y*5), (0, 5), (-2,23))
    test_parameters((TOWNSHIP_X*20,TOWNSHIP_Y*(-10)), (20, -10), (98,-52))
    test_parameters((9,0), (2, 0), (8,-2))
