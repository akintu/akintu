'''
Series of helper classes for use in GameScreen
'''

import pygame
from pygame.locals import *
from pygame import Rect, Color

DEF_RECT = pygame.Rect(0, 0, 80, 133)


class TilingDialog(object):
    '''
    Reusable class which provides tiling-selection functionality
    '''

    def __init__(self, toptext, itemlist, selection=0):
        '''
        Initialize the class
        '''
        self.selection = selection
        self.toptext = toptext
        self.items = itemlist
        self.surface = pygame.Surface((1280, 640))
        self.surface.fill(Color('gray'))
        self.images = {}
        self.prev_selection = selection
        self.cur_selection = selection

        self._processitems()
        self._drawtoptext()
        self._drawitems()
        self._updateselection()

    def select_index(self, index):
        '''
        Select a specific index
        '''
        self.prev_selection = self.cur_selection
        self.cur_selection = index
        self._updateselection()

    def get_selection(self):
        '''
        Get the current selection
        '''
        return self.cur_selection

    def move_selection(self, direction):
        '''
        Move the current selection (based on num pad directions, 2 4 6 8)
        '''
        selection = self.cur_selection
        if direction == 2:
            selection += 16
        elif direction == 4:
            selection -= 1
        elif direction == 6:
            selection += 1
        elif direction == 8:
            selection -= 16
        else:
            raise Exception('Invalid direction passed to '
                            'TilingDialog.move_selection')
        if selection >= len(self.items):
            selection = len(self.items) - 1
        elif selection < 0:
            selection = 0
        self.prev_selection = self.cur_selection
        self.cur_selection = selection
        self._updateselection()

    def _processitems(self):
        '''
        Processes the item list, loading the necessary images
        '''
        for item in self.items:
            if item.image not in self.images:
                self.images[item.image] = \
                    pygame.image.load(item.image).convert_alpha()

    def _updateselection(self):
        '''
        Draw a rectangle around current selection, removing from previous
        '''
        x = 0
        y = 57
        y += (self.prev_selection // 16) * 133
        x += (self.prev_selection % 16) * 80
        pygame.draw.rect(self.surface,
                         Color('gray'),
                         DEF_RECT.move(x, y),
                         3)
        x = 0
        y = 57
        y += (self.cur_selection // 16) * 133
        x += (self.cur_selection % 16) * 80
        pygame.draw.rect(self.surface,
                         Color('yellow'),
                         DEF_RECT.move(x, y),
                         3)
        text = self.items[self.cur_selection].text
        self._drawbottomtext(text)

    def _drawtoptext(self):
        '''
        Draw the top text area
        '''
        textsurface = self._generatetext(self.toptext, 42)
        self.surface.blit(textsurface, (5, 10))

    def _drawbottomtext(self, text):
        '''
        Draw the bottom text area with the given text
        '''
        textsurface = self._generatetext(text, 174)
        self.surface.blit(textsurface, (5, 466))

    def _drawitems(self):
        '''
        Draw the possible selections in a 16x3 grid
        '''
        font = pygame.font.SysFont("Arial", 12)
        # Generate surfaces for each item
        surfaces = []
        for item in self.items:
            surface = pygame.Surface((80, 133))
            surface.fill(Color('gray'))
            image = self.images[item.image]
            surface.blit(image, (16, 5))
            names = item.name.split(' ')
            y = 58
            for name in names:
                namefont = font.render(name, True, Color('black'))
                x = 40 - (namefont.get_rect().width // 2)
                surface.blit(namefont, (x, y))
                y += namefont.get_rect().height
            surfaces.append(surface)
        y = 57
        x = 0
        for surf in surfaces:
            self.surface.blit(surf, (x, y))
            x += 80
            if x >= 1280:
                x = 0
                y += 133

    def _generatetext(self, text, height, width=1200, color='black'):
        '''
        Generate a text surface of given height and width with the given text

        Splits on newlines, does not wrap otherwise
        '''
        surface = pygame.Surface((width, height))
        surface.fill(Color('gray'))
        lines = text.split('\n')
        y = 0
        font = pygame.font.SysFont('Arial', 12)
        for line in lines:
            curfont = font.render(line, True, Color(color))
            surface.blit(curfont, (0, y))
            y += curfont.get_rect().height
        return surface
