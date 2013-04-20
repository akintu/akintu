
from entity import*

class Portal(Entity):
    '''
    The Portal class is used for transporting the player
    to a specific location, or too provide information 
    that the server can use to trigger a specific event,
    like opening a shop.
    '''

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
        
    def trigger(self):
        '''
        Does not actually fire an event, but provides
        additional location information.  The existance
        of this method allows the server to pull the
        relevant info from this class.
        '''
        return (self.iLocation, self.new_location)
        