'''
AI was initially designed to be used for both overworld and combat AI, but is now only for overworld.
TODO: Add 'chase' and 'evade' behaviors
'''
import random
from command import *
from network import *
from time import time
import collections
import cPickle
import zlib

class AI():
    def __init__(self, history=None):
        '''
        History is what comes out of an AI object if you cast it to a string, and can then be used
        to initialize a new AI object.
        '''
        self.server = None
        self.behavior = collections.OrderedDict()
        self.paused = False
        self.history = []
        if history:
            self.rehydrate(history)

    def startup(self, server):
        '''
        Since AI needs access to the game world state, a pointer to the server is necessary.
        This attribute assignment would go in the __init__, but AI is instantiated in pane generation
        where there is no hook to the server.  Therefore, the server calls this method on each
        monster when it has received a populated pane to bring them to life.
        '''
        self.server = server
        for name in self.behavior.keys():
            self.start(name)

    ###### AI BEHAVIORS ######
    def wander(self, pid=None, region=None, move_chance=0):
        '''
        Move person with pid randomly in the assigned region, with probability equal to move_chance
        '''
        if time() < self.behavior['wander']['time']:
            return False
        if random.random() <= move_chance:
            dirs = [2, 4, 6, 8]
            direction = random.choice(dirs)
            newloc = self.server.person[pid].location.move(direction, 1)
            while not newloc in region or not self.server.tile_is_open(newloc) or self.server.world.is_town_pane(newloc.pane):
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
        '''
        Add and activate an AI behavior to a Person object.
        Inputs:
            name: the name of the behavior method, e.g., 'wander'
            frequency: the frequency that the behavior is called in calls / second
            details: the other named parameters from the behavior method being added
        '''
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
        '''
        Serialize AI object state for storage or transmission
        '''
        return zlib.compress(cPickle.dumps(self.history), 9)

    def rehydrate(self, history, pid):
        '''
        Restore AI object state from storage or transmission
        '''
        if not isinstance(history, list):
            history = cPickle.loads(zlib.decompress(history))
        for behavior in history:
            if 'pid' in behavior['details']:
                behavior['details']['pid'] = pid
            self.add(behavior['name'], behavior['frequency'], **behavior['details'])

    def remove(self, name):
        '''
        Stop a particular AI behavior from active use and delete it
        '''
        if name in self.behavior:
            self.stop(name)
            del self.behavior[name]
        else:
            print "Server error: Attempted to stop non-existent ai function:", name

    def start(self, name):
        '''
        Activate an existing AI behavior that has been stopped
        '''
        self.behavior[name]['running'] = True
        self.behavior[name]['time'] = time()
        self.behavior[name]['task'].start(1.0 / self.behavior[name]['frequency'])

    def stop(self, name):
        '''
        Cease the looping calls that activate the named behavior
        '''
        if self.behavior[name]['running'] and not self.paused:
            self.behavior[name]['task'].stop()
            self.behavior[name]['running'] = False

    def update_frequency(self, name, frequency):
        '''
        Modify the frequency of calls to a behavior.  Used when stats that affect movement speed
        are modified
        '''
        self.behavior[name]['frequency'] = frequency
        self.stop(name)
        self.start(name)

    def pause(self):
        '''
        Stop all behavior calls for a time, but do not affect their running flag.
        '''
        if not self.paused:
            for name in self.behavior.keys():
                if self.behavior[name]['running']:
                    self.behavior[name]['task'].stop()
            self.paused = True

    def resume(self):
        '''
        Start all behaviors that have their 'running' flag set, effectively resuming an entire
        paused AI object.
        '''
        if self.paused:
            for name in self.behavior.keys():
                if self.behavior[name]['running']:
                    self.start(name)
            self.paused = False

    def shutdown(self):
        '''
        Prepare for deleting the parent Person object by stopping and deleting all AI behaviors
        '''
        for name in self.behavior.keys():
            self.remove(name)
