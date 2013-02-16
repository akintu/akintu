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
        self.persons = dict()
        self.personsgroup = pygame.sprite.RenderUpdates()
        for i, j in [(i, j) for i in range(PANE_X) for j in range(PANE_Y)]:
            self.world[(i, j)] = None
        pygame.display.flip()

    def set_pane(self, pane):
        # Remove all persons
        for personid in list(self.persons):
            self.personsgroup.remove(self.persons[personid])
            self.persons.pop(personid)
        for key, val in pane.images.iteritems():
            mode = val.mode
            size = val.size
            data = val.tostring()
            if mode == 'RGBA':
                self.images[key] = \
                    pygame.image.fromstring(data, size, mode).convert_alpha()
            else:
                #assert mode in 'RGB', 'RGBA'
                self.images[key] = \
                    pygame.image.fromstring(data, size, mode).convert()
        self.pane = pane
        self.draw_world()

    def draw_world(self):
        for i, j in [(i, j) for i in range(PANE_X) for j in range(PANE_Y)]:
            tile = self.pane.tiles[(i, j)]

            # Draw the tile background
            if tile.image not in self.images:
                self.images[tile.image] = \
                    pygame.image.load(tile.image).convert_alpha()
            tileimage = self.images[tile.image]
            self.background.blit(tileimage, (i*TILE_SIZE, j*TILE_SIZE))

            # Draw all the entities
            for ent in tile.entities:
                if ent.image not in self.images:
                    self.images[ent.image] = \
                        pygame.image.load(ent.image).convert_alpha()
                entimage = self.images[ent.image]
                self.background.blit(entimage, (i*TILE_SIZE, j*TILE_SIZE))
        self.screen.blit(self.background, [0, 0])
        pygame.display.update()

    def update_tile(self, tile, location):
        self.pane.tiles[location.tile] = tile
        i, j = location.tile

        # Draw the tile background
        if tile.image not in self.images:
            self.images[tile.image] = \
                pygame.image.load(tile.image).convert_alpha()
        tileimage = self.images[tile.image]
        self.background.blit(tileimage, (i*TILE_SIZE, j*TILE_SIZE))

        # Draw all the entities
        for ent in tile.entities:
            if ent.image not in self.images:
                self.images[ent.image] = \
                    pygame.image.load(ent.image).convert_alpha()
            entimage = self.images[ent.image]
            self.background.blit(entimage, (i*TILE_SIZE, j*TILE_SIZE))

        # Draw the entire background (if this becomes an issue we'll refactor)
        self.screen.blit(self.background, [0, 0])
        self.personsgroup.draw(self.screen)
        pygame.display.update()

    def add_person(self, personid, statsdict):
        if 'image' not in statsdict or \
           'location' not in statsdict:
            raise Exception('Image or location not defined')
        self.persons[personid] = \
            PersonSprite(statsdict)
        self.personsgroup.add(self.persons[personid])

    def remove_person(self, personid):
        self.personsgroup.remove(self.persons[personid])
        self.persons.pop(personid)

    def update_person(self, personid, statsdict):
        if 'location' in statsdict:
            self.persons[personid].newest_coord = statsdict['location']

    def update(self):
        self.personsgroup.update()
        rectlist = self.personsgroup.draw(self.screen)
        pygame.display.update(rectlist)
        self.personsgroup.clear(self.screen, self.background)

    def set_fps(self, fps):
        if SHOW_FPS:
            pygame.display.set_caption("%s %d" % (CAPTION, fps))


class PersonSprite(pygame.sprite.DirtySprite):
    def __init__(self, statsdict):
        pygame.sprite.DirtySprite.__init__(self)
        # Store away the statsdict
        self.statsdict = statsdict
        # Get all the images required
        imagepre = self.statsdict['image']
        endings = [(2, '_fr1.png'), (4, '_lf1.png'),
                   (6, '_rt1.png'), (8, '_bk1.png')]
        self.images = {key: pygame.image.load(imagepre + end).convert_alpha()
                       for key, end in endings}
        # Location and rect info
        loc = self.statsdict['location']
        self.image = self.images[loc.direction]
        self.rect = self.image.get_rect()
        self.current_coord = None
        self.newest_coord = loc
        self.rect.topleft = [x*TILE_SIZE for x in loc.tile]

    def update(self):
        if self.current_coord != self.newest_coord:
            self.current_coord = self.newest_coord
            self.rect.topleft = [x*TILE_SIZE for x in self.newest_coord.tile]
            self.image = self.images[self.newest_coord.direction]
