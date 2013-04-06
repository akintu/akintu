import entity
class Obstacle(entity.Entity):
	def __init__(self, location=None, image=None, cLocation=None, cPane=None):
		super(Obstacle, self).__init__(location=location, team="Neutral", image=image, passable=False, cLocation=cLocation, cPane=cPane)
        pass
