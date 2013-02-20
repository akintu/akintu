import random
from command import *
from network import *

class AI():
    def __init__(self):
        self.server = None
        self.behavior = {}
        
    def startai(self, server):
        self.server = server
        for name in self.behavior.keys():
            self.start(name)
        
    ###### AI BEHAVIORS ######
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

    ###### AI MANAGEMENT ######
    def add(self, name, ai_func, frequency, **details):
        self.behavior[name] = {}
        self.behavior[name]['frequency'] = frequency
        self.behavior[name]['task'] = LoopingCall(ai_func, **details)
        
    def remove(self, name):
        if name in self.behavior:
            self.stop(name)
            del self.behavior[name]
        else:
            print "Server error: Attempted to stop non-existent ai function", name

    def start(self, name):
        self.behavior[name]['running'] = True
        self.behavior[name]['task'].start(1.0 / self.behavior[name]['frequency'])
        
    def stop(self, name):
        if self.behavior[name]['running']:
            self.ai[name]['task'].stop()
        
    def update_frequency(self, name, frequency):
        self.behavior[name]['frequency'] = frequency
        self.stop(name)
        self.start(name)
