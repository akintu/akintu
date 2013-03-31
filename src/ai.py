import random
from command import *
from network import *
from time import time
import collections
import cPickle
import zlib

class AI():
    def __init__(self, history=None):
        self.server = None
        self.behavior = collections.OrderedDict()
        self.paused = False
        self.history = []
        if history:
            self.rehydrate(history)

    def startup(self, server):
        self.server = server
        for name in self.behavior.keys():
            self.start(name)

    ###### AI BEHAVIORS ######
    def run(self, pid=None, direction=None):
        newloc = self.server.person[pid].location.move(direction, 1)
        self.server.SDF.queue.put((None, Command("PERSON", "MOVE", id=pid, location=newloc)))
        return True

    def wander(self, pid=None, region=None, move_chance=0):
        if time() < self.behavior['wander']['time']:
            return False
        if random.random() <= move_chance:
            dirs = [2, 4, 6, 8]
            direction = random.choice(dirs)
            newloc = self.server.person[pid].location.move(direction, 1)
            while not newloc in region or not self.server.tile_is_open(newloc):
                dirs.remove(direction)
                if len(dirs) == 0:
                    return False
                direction = random.choice(dirs)
                newloc = self.server.person[pid].location.move(direction, 1)

            self.server.SDF.queue.put((None, Command("PERSON", "MOVE", id=pid, location=newloc)))
            self.behavior['wander']['time'] = time() + (1.0 / self.behavior['wander']['frequency'])
            return True

    ###### AI MANAGEMENT ######
    def add(self, name, frequency, **details):
        if hasattr(self, name):
            behavior = {}
            behavior['frequency'] = frequency
            behavior['running'] = False
            behavior['task'] = LoopingCall(getattr(self, name), **details)
            self.behavior[name] = behavior

            hist = {}
            hist['name'] = name
            hist['frequency'] = frequency
            hist['details'] = details
            self.history.append(hist)

    def dehydrate(self):
        return self.__repr__()

    def __repr__(self):
        return zlib.compress(cPickle.dumps(self.history), 9)

    def rehydrate(self, history):
        if not isinstance(history, list):
            history = cPickle.loads(zlib.decompress(history))
        for behavior in history:
            self.add(behavior['name'], behavior['frequency'], **behavior['details'])

    def remove(self, name):
        if name in self.behavior:
            self.stop(name)
            del self.behavior[name]
        else:
            print "Server error: Attempted to stop non-existent ai function:", name

    def start(self, name):
        self.behavior[name]['running'] = True
        self.behavior[name]['time'] = time()
        self.behavior[name]['task'].start(1.0 / self.behavior[name]['frequency'])

    def stop(self, name):
        if self.behavior[name]['running'] and not self.paused:
            self.behavior[name]['task'].stop()
            self.behavior[name]['running'] = False

    def update_frequency(self, name, frequency):
        self.behavior[name]['frequency'] = frequency
        self.stop(name)
        self.start(name)

    def pause(self):
        if not self.paused:
            for name in self.behavior.keys():
                if self.behavior[name]['running']:
                    self.behavior[name]['task'].stop()
            self.paused = True

    def resume(self):
        if self.paused:
            for name in self.behavior.keys():
                if self.behavior[name]['running']:
                    self.start(name)
            self.paused = False

    def shutdown(self):
        for name in self.behavior.keys():
            self.remove(name)
