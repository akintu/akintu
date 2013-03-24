
from entity import*

class Portal(Entity):
    def __init__(self, new_location, location=None, team="Neutral", image=None, passable=True):
        super(Portal, self).__init__(location=location, team=team, image=image, passable=passable)
        self.new_location = new_location
        
    def trigger(self, target):
        print "Portal.trigger() called"
        return self.new_location
        