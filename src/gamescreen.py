'''
Main visual engine
'''

import pygame
from pygame.locals import *
from pygame import Rect, Color

import os
import sys
from PIL import Image

from const import *
from world import *


class GameScreen(object):
    '''
    Main graphics engine for Akintu
    '''

    def __init__(self):
        '''
        Initialize Akintu graphics engine with default settings
        '''
        self.screen = pygame.display.set_mode(
                (PANE_X * TILE_SIZE + 256,
                max(PANE_Y * TILE_SIZE, 20 * TILE_SIZE)
                ))
        pygame.display.set_caption('Akintu r01')
        self.background = pygame.Surface((PANE_X * TILE_SIZE,
                                          PANE_Y * TILE_SIZE))
        self.world = dict()
        self.images = dict()
        self.persons = dict()
        self.personsgroup = pygame.sprite.RenderUpdates()
        for i, j in [(i, j) for i in range(PANE_X) for j in range(PANE_Y)]:
            self.world[(i, j)] = None
        pygame.display.flip()

    def set_pane(self, pane):
        '''
        Set the Pane for the graphics engine to display
        '''
        # Remove all persons first
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
        '''
        Draw the world (represented by a Pane)
        '''
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
        '''
        Update a specific tile in the current pane
        '''
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
        '''
        Add a Person object to the world

        Required entries in statsdict:
            - 'image'
            - 'location'

        Supported entries in statsdict:
            - 'image'
            - 'location'
            - 'xoffset' (in pixels)
            - 'xoffset' (in pixels)
            - 'foot' (0 or 1)

        To be supported in the future:
            - 'name'
            - 'HP'
            - 'MP'
            - 'AP'
            - 'buffedHP'
            - 'totalHP'
            - 'totalMP'
            - 'totalAP'
            - 'location'
            - 'statusList'
            - 'cooldownList'
            - time remaining
            - is it the players turn?
        '''
        # Check for properly-formatted statsdict, set some defaults if not
        # present
        if 'image' not in statsdict or \
           'location' not in statsdict:
            raise Exception('Image or location not defined')
        for attr in ['xoffset', 'yoffset', 'foot']:
            if attr not in statsdict:
                statsdict[attr] = 0

        self.persons[personid] = \
            PersonSprite(statsdict)
        self.personsgroup.add(self.persons[personid])

    def remove_person(self, personid):
        '''
        Remove a Person object from the world
        '''
        self.personsgroup.remove(self.persons[personid])
        self.persons.pop(personid)

    def update_person(self, personid, statsdict):
        '''
        Update statsdict for a Person object

        See documentation for add_person() to see supported entries in
        statsdict
        '''
        if 'location' in statsdict:
            self.persons[personid].current_coord = statsdict['location']
        self.persons[personid].update_dict(statsdict)

    def update(self):
        '''
        Updates and redraws necessary parts of the game world

        Should be called once per game loop cycle
        '''
        self.personsgroup.update()
        rectlist = self.personsgroup.draw(self.screen)
        pygame.display.update(rectlist)
        self.personsgroup.clear(self.screen, self.background)

    def set_fps(self, fps):
        '''
        Set the FPS in the title bar (if enabled)
        '''
        if SHOW_FPS:
            pygame.display.set_caption("%s %d" % (CAPTION, fps))


class PersonSprite(pygame.sprite.DirtySprite):
    def __init__(self, statsdict):
        '''
        Initialize the PersonSprite

        Entries required in statsdict:
            - 'image'
            - 'location'
        '''
        pygame.sprite.DirtySprite.__init__(self)
        # Store away the statsdict
        self.statsdict = statsdict
        # Get all the images required
        imagepre = self.statsdict['image']
        # Try to retrieve the different facing images
        try:
            self.images = []
            endings = [(2, '_fr1.png'), (4, '_lf1.png'),
                       (6, '_rt1.png'), (8, '_bk1.png')]
            self.images.append(
                    {key: pygame.image.load(imagepre+end).convert_alpha()
                    for key, end in endings})
            endings = [(2, '_fr2.png'), (4, '_lf2.png'),
                       (6, '_rt2.png'), (8, '_bk2.png')]
            self.images.append(
                    {key: pygame.image.load(imagepre+end).convert_alpha()
                    for key, end in endings})
        # Assume imagepre is the actual image location, add facing overlays
        except pygame.error:
            self.images = facing_overlays(imagepre)

        # Location and rect info
        loc = self.statsdict['location']
        foot = self.statsdict['foot']
        xoff= self.statsdict['xoffset']
        yoff= self.statsdict['yoffset']
        self.image = self.images[foot][loc.direction]
        self.rect = self.image.get_rect()
        self.current_coord = loc
        self.rect.topleft = (loc.tile[0] * TILE_SIZE + xoff,
                             loc.tile[1] * TILE_SIZE + yoff)

    def update(self):
        '''
        Hook for SpritesGroup update() calls

        Checks for new coordinate, updates location if necessary
        '''
        self.statsdict['foot'] = (self.statsdict['foot'] + 1) % 2
        foot = self.statsdict['foot']
        xoff = self.statsdict['xoffset']
        yoff = self.statsdict['yoffset']
        loc = self.current_coord
        self.rect.topleft = (loc.tile[0] * TILE_SIZE + xoff,
                             loc.tile[1] * TILE_SIZE + yoff)
        self.image = self.images[foot][loc.direction]

    def update_dict(self, statsdict):
        '''
        Update self.statsdict with all they keys/values in statsdict
        '''
        for key in statsdict:
            self.statsdict[key] = statsdict[key]

####### MISC Utility Functions #######


def facing_overlays(imageloc):
    '''
    Given an image location, will return a facing dictionary of images with
    facing overlays
    '''
    keys = [2, 4, 6, 8]
    rects = [(0, 29, 32, 3),
             (0, 0, 3, 32),
             (29, 0, 3, 32),
             (0, 0, 32, 3)]
    imagedict = dict()
    for key, rect in zip(keys, rects):
        imagedict[key] = pygame.image.load(imageloc).convert_alpha()
        imagedict[key].fill(Color('blue'), rect)
    return [imagedict, imagedict]
