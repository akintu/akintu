
from entity import*

class Portal(Entity):
    def __init__(self, location=None, team="Neutral", image=None, passable=True):
        super(Portal, self).__init__(location=location, team=team, image=image, passable=passable)

    def trigger(self, target):
        print "Portal.trigger(target) called"
        pass