'''
Main visual engine
'''

import pygame
from pygame.locals import *

import os
import sys

# TEST
sys.path.append("test")
from testworld import *

class GameScreen(object):

    def __init__(self):
        self.screen = pygame.display.set_mode((1024, 640))
        self.background = pygame.Surface((1024, 640))
        self.world = dict()
        self.images = dict()
        self.players = dict()
        self.playersgroup = pygame.sprite.RenderUpdates()
        for i,j in [(i, j) for i in range(32) for j in range(20)]:
            self.world[(i, j)] = None
        pygame.display.flip()

    def set_pane(self, pane):
        self.pane = pane
        self.draw_world()

    def draw_world(self):
        for i,j in [(i, j) for i in range(32) for j in range(20)]:
            tile = self.pane.tiles[(i, j)]
            if(self.images.has_key(tile.image)):
                tileimage = self.images[tile.image]
            else:
                self.images[tile.image] = pygame.image.load(tile.image)
                tileimage = self.images[tile.image]
            self.background.blit(tileimage, (i*32, j*32))
        self.screen.blit(self.background, [0, 0])
        pygame.display.update()

    def add_player(self, playerid, player):
        self.players[playerid] = PlayerSprite("test/knight.png", self.pane.startpoint)
        self.playersgroup.add(self.players[playerid])
        return self.pane.startpoint

    def remove_player(self, playerid):
        self.playersgroup.remove(self.players[playerid])
        self.players.pop(playerid)

    def update_player(self, playerid, location):
        self.players[playerid].newest_coord = location

    def update(self):
        self.playersgroup.update()
        rectlist = self.playersgroup.draw(self.screen)
        pygame.display.update(rectlist)
        self.playersgroup.clear(self.screen, self.background)


class PlayerSprite(pygame.sprite.DirtySprite):
    def __init__(self, image, startpoint):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.current_coord = None
        self.newest_coord = startpoint
        self.rect.topleft = [x*32 for x in startpoint]

    def update(self):
        if self.current_coord != self.newest_coord:
            self.current_coord = self.newest_coord
            self.rect.topleft = [x*32 for x in self.newest_coord]
