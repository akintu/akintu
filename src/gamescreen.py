'''
Main visual engine
'''

import pygame
from pygame.locals import *

import os
import sys
from PIL import Image

from const import *
from world import *


class GameScreen(object):

    def __init__(self):
        self.screen = pygame.display.set_mode((1024, 640))
        pygame.display.set_caption('Akintu r01')
        self.background = pygame.Surface((1024, 640))
        self.world = dict()
        self.images = dict()
        self.players = dict()
        self.playersgroup = pygame.sprite.RenderUpdates()
        for i,j in [(i, j) for i in range(PANE_X) for j in range(PANE_Y)]:
            self.world[(i, j)] = None
        pygame.display.flip()


    def update_images(self, imagedict):
        for key, val in imagedict.iteritems():
            mode = val.mode
            size = val.size
            data = val.tostring()
            assert mode in 'RGB', 'RGBA'
            self.images[key] = pygame.image.fromstring(data, size, mode).convert()


    def set_pane(self, pane):
        self.pane = pane
        self.draw_world()


    def draw_world(self):
        for i,j in [(i, j) for i in range(PANE_X) for j in range(PANE_Y)]:
            tile = self.pane.tiles[(i, j)]

            # Draw the tile background
            if not self.images.has_key(tile.image):
                self.images[tile.image] = \
                    pygame.image.load(tile.image).convert_alpha()
            tileimage = self.images[tile.image]
            self.background.blit(tileimage, (i*TILE_SIZE, j*TILE_SIZE))

            # Draw all the entities
            for ent in tile.entities:
                if not self.images.has_key(ent.image):
                    self.images[ent.image] = \
                        pygame.image.load(ent.image).convert_alpha()
                entimage = self.images[ent.image]
                self.background.blit(entimage, (i*TILE_SIZE, j*TILE_SIZE))
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


    def set_fps(self, fps):
        if SHOW_FPS:
            pygame.display.set_caption("%s %d" % (CAPTION, fps))



class PlayerSprite(pygame.sprite.DirtySprite):
    def __init__(self, image, startpoint):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect()
        self.current_coord = None
        self.newest_coord = startpoint
        self.rect.topleft = [x*TILE_SIZE for x in startpoint]


    def update(self):
        if self.current_coord != self.newest_coord:
            self.current_coord = self.newest_coord
            self.rect.topleft = [x*TILE_SIZE for x in self.newest_coord]
