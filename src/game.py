'''
Main game control
'''

import pygame
from pygame.locals import *

import os
import sys

from command import *
from location import *
from network import *
from const import *
from gamescreen import GameScreen
from world import *

clock = pygame.time.Clock()

class Game(object):
    def __init__(self):
        self.serverip = "localhost"
        if len(sys.argv) == 1:
            self.SDF = ServerDataFactory()
            reactor.listenTCP(1337, self.SDF)
            LoopingCall(self.server_loop).start(0)
            self.players = {}  # {Port: Location} of all players
            self.allPeople = {}  # {Pane: List()} containing lists of persons
        else:
            self.serverip = sys.argv[1]

        # Always start a client, if you are the server, you serve yourself.
        self.CDF = ClientDataFactory()
        reactor.connectTCP(self.serverip, 1337, self.CDF)

        self.setup = LoopingCall(self.setup_game)
        self.setup.start(0)

        reactor.run()
        
    def server_loop(self):
        while not self.SDF.queue.empty():
            port, command = self.SDF.queue.get()
            if isinstance(command, CreatePerson):
                #Assume clients only send this when they want to create themselves
                #Send new sprite to all clients, then give calling client everything on pane
                
                #if self.passable(command.location):
                self.players[port] = command.location
                
                if command.location.pane not in self.allPeople:
                    self.allPeople[command.location.pane] = list()
                command.index = len(self.allPeople[command.location.pane])
                self.allPeople[command.location.pane].append(command.location)
                
                for p, l in self.players.iteritems():
                    if self.players[port].pane == l.pane:
                        self.SDF.send(p, command)
                
                for i, l in enumerate(self.allPeople[command.location.pane]):
                    self.SDF.send(port, CreatePerson(i, l))
            if isinstance(command, MovePerson):
                if self.passable(command.dest):
                    if command.dest.pane not in self.allPeople:
                        self.allPeople[command.dest.pane] = list()
                    self.allPeople[command.dest.pane][command.index] = command.dest
                    for p, l in self.players.iteritems():
                        if command.dest.pane == l.pane:
                            self.SDF.send(p, command)

    def setup_game(self):
        if not self.CDF.port:
            return
    
        # Set up game engine
        self.screen = GameScreen()
        self.world = World("CorrectHorseStapleBattery")
        
        location = Location((0, 0), (PANE_X/2, PANE_Y/2))
        self.switch_panes(location)
        self.people = []
        self.player = {'location': location, 'index': -1}
        self.CDF.send(CreatePerson(None, location))

        self.setup.stop()
        LoopingCall(self.game_loop).start(1.0 / DESIRED_FPS)
        
    def game_loop(self):
        clock.tick()
        fps = clock.get_fps()
        self.screen.set_fps(fps)
        self.check_queue()
        self.handle_events()
        self.screen.update()
        
    def check_queue(self):
        while not self.CDF.queue.empty():
            command = self.CDF.queue.get()
            if isinstance(command, CreatePerson):
                if self.player['index'] == -1:
                    self.player['index'] = command.index
                else:
                    self.people.append([command.location])
                    self.screen.add_person(len(self.people) - 1, None, command.location)
            if isinstance(command, MovePerson):
                self.people[command.index][0] = command.dest
                self.screen.update_person(command.index, command.dest)
            
    def handle_events(self):
        pygame.event.clear([MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        for event in pygame.event.get():
            if event.type == QUIT:
                reactor.stop()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    reactor.stop()
                elif event.key in [K_LEFT, K_KP4, K_h]:
                    self.move_person(self.player['index'], 4, 1)
                elif event.key in [K_RIGHT, K_KP6, K_l]:
                    self.move_person(self.player['index'], 6, 1)
                elif event.key in [K_UP, K_KP8, K_k]:
                    self.move_person(self.player['index'], 8, 1)
                elif event.key in [K_DOWN, K_KP2, K_j]:
                    self.move_person(self.player['index'], 2, 1)
                elif event.key in [K_KP7, K_y]:  # UP LEFT
                    self.move_person(self.player['index'], 7, 1)
                elif event.key in[K_KP9, K_u]:  # UP RIGHT
                    self.move_person(self.player['index'], 9, 1)
                elif event.key in [K_KP3, K_n]:  # DOWN RIGHT
                    self.move_person(self.player['index'], 3, 1)
                elif event.key in [K_KP1, K_b]:  # DOWN LEFT
                    self.move_person(self.player['index'], 1, 1)

    def move_person(self, index, direction, distance):
        newloc = self.people[index][0].move(direction, distance)
        if self.passable(newloc):
            self.CDF.send(MovePerson(index, newloc))
            if self.people[index][0].pane != newloc.pane:
                self.switch_panes(newloc)
                self.screen.add_person(index, None, self.people[index][0])
            self.people[index][0] = newloc
            if self.player['index'] == index:
                self.player['location'] = newloc
            self.screen.update_person(index, self.people[index][0])

    def passable(self, newloc):
        tupleloc = newloc.tile
        if not tupleloc in self.pane.tiles:
            return False
        if newloc.pane == self.player['location'].pane:
            #if not self.pane.tiles[tupleloc].passable:
            #print self.pane.is_tile_passable(newloc)
            if not self.pane.is_tile_passable(newloc):
                return False
            tile = self.pane.tiles[tupleloc]
            for ent in tile.entities:
                if not ent.passable:
                    return False
        return True

    def switch_panes(self, location):
        #TODO we can add transitions here.
        self.pane, imagedict = self.world.get_pane(location.pane)
        self.screen.set_pane(self.pane, imagedict)
