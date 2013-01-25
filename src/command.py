'''
Class for communicating map sync actions
'''

class Command:
	def __init__(self, target, location, action, details):
		self.target = target
		self.location = location
		self.action = action
		self.details = details