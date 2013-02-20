import random
from command import *

class AI():
    def __init__(self, server):
        self.server = server
        
    def run(self, pid=None, direction=None, region=None):
        newloc = self.server.person[pid].location.move(direction, 1)
        self.server.SDF.queue.put((None, Person(PersonActions.MOVE, pid, newloc)))

    def wander(self, pid=None, region=None, move_chance=0):
        if random.random() <= move_chance:
            dirs = [1, 2, 3, 4, 6, 7, 8, 9]
            direction = random.choice(dirs)
            newloc = self.server.person[pid].location.move(direction, 1)
            while not region.has(newloc) or not self.server.tile_is_open(newloc):
                dirs.remove(direction)
                if len(dirs) == 0:
                    return
                direction = random.choice(dirs)
                newloc = self.server.person[pid].location.move(direction, 1)
            
            self.server.SDF.queue.put((None, Person(PersonActions.MOVE, pid, newloc)))
