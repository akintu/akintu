
from entity import*

class Portal(Entity):

    DUNGEON = "dungeon"
    OVERWORLD = "overworld"
    HOUSE = "house"
    SHOP = "shop"
    RESPEC = "respec"

    def __init__(self, iLocation, portal_type, new_location=None, team="Neutral", image=None, passable=True):
        super(Portal, self).__init__(location=iLocation.tile, team=team, image=image, passable=passable)
        self.new_location = new_location
        self.iLocation = iLocation
        self.portal_type = portal_type
        
    def trigger(self, target):
        #print "Portal.trigger() called"
        return (self.iLocation, self.new_location)
        