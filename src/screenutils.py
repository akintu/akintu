'''
Series of helper classes for use in GameScreen
'''

import pygame
from pygame.locals import *
from pygame import Rect, Color


class TilingDialog(object):
    '''
    Reusable class which provides tiling-selection functionality
    '''

    def __init__(self, toptext, itemlist, selection=0, bgcolor='gray'):
        '''
        Initialize the class
        '''
        self.DEF_RECT = pygame.Rect(0, 0, 80, 133)
        self.bgcolor = bgcolor
        self.selection = selection
        self.toptext = toptext
        self.items = itemlist
        self.surface = pygame.Surface((1280, 640))
        self.surface.fill(Color(self.bgcolor))
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
                         Color(self.bgcolor),
                         self.DEF_RECT.move(x, y),
                         3)
        x = 0
        y = 57
        y += (self.cur_selection // 16) * 133
        x += (self.cur_selection % 16) * 80
        pygame.draw.rect(self.surface,
                         Color('yellow'),
                         self.DEF_RECT.move(x, y),
                         3)
        text = self.items[self.cur_selection].text
        self._drawbottomtext(text)

    def _drawtoptext(self):
        '''
        Draw the top text area
        '''
        textsurface = self._generatetext(self.toptext, 42)
        self.surface.blit(textsurface, (20, 10))

    def _drawbottomtext(self, text):
        '''
        Draw the bottom text area with the given text
        '''
        textsurface = self._generatetext(text, 174)
        self.surface.blit(textsurface, (20, 466))

    def _drawitems(self):
        '''
        Draw the possible selections in a 16x3 grid
        '''
        font = pygame.font.SysFont('Arial', 12)
        # Generate surfaces for each item
        surfaces = []
        for item in self.items:
            surface = pygame.Surface((80, 133))
            surface.fill(Color(self.bgcolor))
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
        surface.fill(Color(self.bgcolor))
        lines = text.split('\n')
        y = 0
        font = pygame.font.SysFont('Arial', 18)
        for line in lines:
            curfont = font.render(line, True, Color(color))
            surface.blit(curfont, (0, y))
            y += curfont.get_rect().height
        return surface


class ItemDialog(object):
    '''
    Provides a two-paned, text-based dialog for use with inventory and shops
    '''
    def __init__(self,
                 toptext,
                 leftlist,
                 rightlist,
                 equipment=False,
                 bgcolor='gray',
                 capacity=''):
        '''
        Initialize the class
        '''
        self.DEF_RECT = pygame.Rect(1, 1, 468, 28)
        self.bgcolor = bgcolor
        self.toptext = toptext
        self.equipment = equipment
        self.items = [leftlist, rightlist]
        self.surface = pygame.Surface((1280, 640))
        self.surface.fill(Color(self.bgcolor))
        self.selection = (0, 0)
        self.tops = [0, 0]
        self.capacity = capacity

        self.leftitems = self._generateitems(self.items[0])
        self.rightitems = self._generateitems(self.items[1], self.equipment)

        self._drawtoptext()
        self._drawitems()
        self._updateselection()
        self._drawborders()

    def get_selection(self):
        '''
        Get the current selection
        '''
        pane, item = self.selection
        return (pane, item, self.items[pane][item].type)

    def update_toptext(self, toptext, capacity=None):
        '''
        Update the top text
        '''
        self.toptext = toptext
        if capacity:
            self.capacity = capacity
        self._drawtoptext()

    def set_items(self, leftlist, rightlist, toptext=None):
        '''
        Set the items lists (and optionally the top text), redraw the dialog
        '''
        self.surface.fill(Color(self.bgcolor), (10, 60, 470, 590))
        self.surface.fill(Color(self.bgcolor), (800, 60, 470, 590))
        self.items = [leftlist, rightlist]
        self.leftitems = self._generateitems(self.items[0])
        self.rightitems = self._generateitems(self.items[1], self.equipment)
        if len(self.leftitems) < 19:
            self.tops[0] = 0
        if len(self.rightitems) < 19:
            self.tops[1] = 0
        if toptext:
            self.toptext = toptext
            _drawtoptext()
        self._drawitems()
        # Recalculate the current position
        self.move_selection(-1)
        self._updateselection()

        pane, item = self.selection
        return (pane, item, self.items[pane][item].type)

    def move_selection(self, direction):
        '''
        Move the current selection (based on num pad directions, 2 4 6 8)
        '''
        selection = list(self.selection)
        if direction == 2:
            selection[1] += 1
        elif direction == 4 or direction == 6:
            selection[0] = (selection[0] + 1) % 2
        elif direction == 8:
            selection[1] -= 1
        elif direction == -1:
            pass
        else:
            raise Exception('Invalid direction passed to '
                            'TilingDialog.move_selection')
        selection[1] = min(selection[1], len(self.items[selection[0]]) - 1)
        selection[1] = max(selection[1], 0)
        if self.selection != selection:
            self.selection = tuple(selection)
        self._updateselection()

        pane, item = self.selection
        return (pane, item, self.items[pane][item].type)

    def _updateselection(self):
        '''
        Draw a rectangle around current selection, removing from previous

        Also error-checks the current selection (in case of out of bounds or
        empty lists)
        '''
        if not self.selection:
            return

        # Error-checking
        if len(self.items[self.selection[0]]) == 0:
            self.selection = ((self.selection[0] + 1) % 2, 0)
        if len(self.items[self.selection[0]]) == 0:
            self.selection = None
            return

        # Calculate new tops
        pane, item = self.selection
        top = self.tops[pane]
        if item < top:
            top = item
        elif item >= top + 19:
            top = item - 18
        self.tops[pane] = top

        self._drawitems()

        drawindex = item - top

        x = 10 + pane * 790
        y = 60 + 30 * drawindex
        pygame.draw.rect(self.surface,
                         Color('yellow'),
                         self.DEF_RECT.move(x, y),
                         3)
        text = self.items[pane][item].details
        self._drawsidetext(text)

    def _drawitems(self):
        '''
        Draw the two lists
        '''
        y = 60
        x = 10
        for i in range(self.tops[0],
                       min(self.tops[0] + 19, len(self.leftitems))):
            self.surface.blit(self.leftitems[i], (x, y))
            y += 30
        y = 60
        x = 800
        for i in range(self.tops[1],
                       min(self.tops[1] + 19, len(self.rightitems))):
            self.surface.blit(self.rightitems[i], (x, y))
            y += 30

    def _drawtoptext(self):
        '''
        Draw the top text area
        '''
        textsurface = self._generatetext(self.toptext, height=30, width=1280)
        righttextsurface = self._generatetext(self.capacity,
                                              height=30,
                                              width=100)
        self.surface.blit(textsurface, (20, 10))
        self.surface.blit(righttextsurface, (1180, 10))

    def _drawsidetext(self, text):
        '''
        Draw the side text area with the given text
        '''
        textsurface = self._generatetext(text, width=290, height=580, size=16)
        self.surface.blit(textsurface, (495, 60))

    def _drawborders(self):
        '''
        Draw the borders around the panes
        '''
        surface = self.surface
        pygame.draw.line(surface, Color('black'), (0, 45), (1280, 45), 3)
        pygame.draw.line(surface, Color('black'), (485, 45), (485, 640), 3)
        pygame.draw.line(surface, Color('black'), (795, 45), (795, 640), 3)

    def _generateitems(self, items, equipment=False):
        surfaces = []

        # Handle the equipment pane (if specified)
        if equipment:
            for item in items:
                surfaces.append(self._generateitempane(item.displayName,
                                                       item.type,
                                                       item.weight,
                                                       item.value))
            for slot in ['Head', 'Legs', 'Feet', 'Chest', 'Hands', 'Neck']:
                found = False
                for item in items:
                    if item.type == slot:
                        found = True
                        break
                if found:
                    continue
                surfaces.append(self._generateemptyitempane(slot))
            fingercount = 2
            for item in items:
                if item.type == 'Finger':
                    fingercount -= 1
            for i in range(fingercount):
                surfaces.append(self._generateemptyitempane('Finger'))
            return surfaces

        # Handle the normal pane
        for item in items:
            surfaces.append(self._generateitempane(item.displayName,
                                                   item.type,
                                                   item.weight,
                                                   item.value))
        if len(surfaces) == 0:
            surfaces.append(self._generateemptyitempane())

        return surfaces

    def _generateitempane(self, name, itemtype, weight, value):
        '''
        Generate a given item pane
        '''
        surface = pygame.Surface((470, 30))
        surface.fill(Color(self.bgcolor))
        font = pygame.font.SysFont('Arial', 18)
        sfont = pygame.font.SysFont('Arial', 14)
        bgcolor = Color(self.bgcolor)

        weightstr = str(weight) + 'lbs'
        valuestr = str(value) + 'g'

        namefont = font.render(name, True, Color('black'), bgcolor)
        typefont = sfont.render(itemtype, True, Color('black'), bgcolor)
        weightfont = sfont.render(weightstr, True, Color('black'), bgcolor)
        valuefont = sfont.render(valuestr, True, Color('black'), bgcolor)

        surface.blit(namefont, (5, 4))
        surface.blit(typefont, (295, 4))
        surface.blit(weightfont, (365, 4))
        surface.blit(valuefont, (425, 4))

        return surface

    def _generateemptyitempane(self, slot=''):
        '''
        Generate en empty item, including the slot text if provided
        '''
        surface = pygame.Surface((470, 30))
        surface.fill(Color(self.bgcolor))
        font = pygame.font.SysFont('Arial', 18)
        curfont = font.render('Empty ' + slot, True, Color('black'))
        surface.blit(curfont, (5, 4))
        return surface

    def _generatetext(self,
                      text,
                      height=590,
                      width=360,
                      color='black',
                      size=18):
        '''
        Generate a text surface of given height and width with the given text

        Splits on newlines, does not wrap otherwise
        '''
        surface = pygame.Surface((width, height))
        surface.fill(Color(self.bgcolor))
        lines = text.split('\n')
        y = 0
        font = pygame.font.SysFont('Arial', size)
        for line in lines:
            curfont = font.render(line, True, Color(color))
            surface.blit(curfont, (0, y))
            y += curfont.get_rect().height
        return surface


if __name__ == '__main__':
    import time
    pygame.init()

    class TestItem(object):
        def __init__(self, name, itemtype, weight, value, details):
            self.displayName = name
            self.type = itemtype
            self.weight = weight
            self.value = value
            self.details = details

    screen = pygame.display.set_mode((1280, 640))
    litems = []
    for i in range(25):
        litems.append(TestItem('Item Number ' + str(i),
                               'Shuriken',
                               10,
                               25,
                               'Some text\nSome more\n\nSomething else'))
    ritems = []
    ritems.append(TestItem('Item Number 0',
                           'Head',
                           10,
                           25,
                           'Some text\nSome more\n\nSomething else'))
    ritems.append(TestItem('Item Number 1',
                           'Shuriken',
                           10,
                           25,
                           'Some text\nSome more\n\nSomething else'))
    dialog = ItemDialog('Inventory',
                        litems,
                        ritems,
                        equipment=True,
                        bgcolor='lightblue')
    screen.blit(dialog.surface, (0, 0))
    while True:
        for i in range(26):
            time.sleep(.5)
            dialog.move_selection(2)
            print dialog.get_selection()
            screen.blit(dialog.surface, (0, 0))
            pygame.event.clear()
            pygame.display.flip()
        for i in range(22):
            time.sleep(.5)
            dialog.move_selection(8)
            print dialog.get_selection()
            screen.blit(dialog.surface, (0, 0))
            pygame.event.clear()
            pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(6)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(2)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(2)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(8)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(8)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(6)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(4)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(4)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        for i in range(22):
            time.sleep(.5)
            dialog.move_selection(2)
            print dialog.get_selection()
            screen.blit(dialog.surface, (0, 0))
            pygame.event.clear()
            pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(4)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
        time.sleep(1)
        dialog.move_selection(4)
        print dialog.get_selection()
        screen.blit(dialog.surface, (0, 0))
        pygame.event.clear()
        pygame.display.flip()
