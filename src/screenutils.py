'''
Series of helper classes for use in GameScreen
'''
import os

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
                            'ItemDialog.move_selection')
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


class CharacterDialog(object):
    '''
    Provides a dialog for viewing character status, including acting as a
    portal to view character abilities, traits, etc
    '''
    def __init__(self,
                 player,
                 bgcolor='gray',
                 abilitykey='H',
                 spellkey='J',
                 passivekey='K',
                 traitkey='L'):
        '''
        Initialize the class
        '''
        self.player = player
        self.bgcolor = bgcolor
        self.akey = abilitykey
        self.skey = spellkey
        self.pkey = passivekey
        self.tkey = traitkey
        self.surface = pygame.Surface((1280, 640))
        self.surface.fill(Color(self.bgcolor))

        self._draw_status()

    def _draw_status(self):
        '''
        Draw the actual status screen
        '''
        p = self.player
        s = self.surface

        # Draw the player image
        ipath = os.path.join('res', 'images', 'sprites', p.image + '_fr1.png')
        psprite = pygame.image.load(ipath).convert_alpha()
        psprite = pygame.transform.scale2x(psprite)
        psprite = pygame.transform.scale2x(psprite)
        psprite = pygame.transform.scale2x(psprite)
        s.blit(psprite, (32, 40))

        hfont = pygame.font.SysFont('Arial', 20)
        pfont = pygame.font.SysFont('Arial', 16)
        nfont = pygame.font.SysFont('Arial', 32)

        x = 340
        y = 40

        l = p.name
        f = nfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Level:  ' + str(p.level)
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Experience:  ' + str(p.experience) + '/' +
             str(p.getExpForNextLevel()))
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Character Class:  ' + p.characterClass
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Race:  ' + p.race
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('HP:  ' + str(int(p.HP)) + '/' + str(int(p.totalHP)) + ' (' +
             str(p.equipmentHP) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('MP:  ' + str(int(p.MP)) + '/' + str(int(p.totalMP)) + ' (' +
             str(p.equipmentMP) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'AP:  ' + str(p.totalAP) + ' (' + str(p.equipmentAP) + ')'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height * 2

        l = 'Primary Statistics'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Strength:  ' + str(int(p.totalStrength)) + ' (' +
             str(p.equipmentStrength) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Dexterity:  ' + str(int(p.totalDexterity)) + ' (' +
             str(p.equipmentDexterity) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Cunning:  ' + str(int(p.totalCunning)) + ' (' +
             str(p.equipmentCunning) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Sorcery:  ' + str(int(p.totalSorcery)) + ' (' +
             str(p.equipmentSorcery) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Piety:  ' + str(int(p.totalPiety)) + ' (' +
             str(p.equipmentPiety) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Constitution:  ' + str(int(p.totalConstitution)) + ' (' +
             str(p.equipmentConstitution) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height * 2
        y = 40
        x += 320

        hfont = pygame.font.SysFont('Arial', 18)
        pfont = pygame.font.SysFont('Arial', 14)

        l = 'Secondary Statistics'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Melee Accuracy:  ' + str(p.totalMeleeAccuracy) + ' (' +
             str(p.equipmentMeleeAccuracy) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Ranged Accuracy:  ' + str(p.totalRangedAccuracy) + ' (' +
             str(p.equipmentRangedAccuracy) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Dodge:  ' + str(p.totalDodge) + ' (' + str(p.equipmentDodge) + ')'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Ranged Dodge:  ' + str(p.totalRangedDodge) + ' (' +
             str(p.equipmentRangedDodge) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Might:  ' + str(p.totalMight) + ' (' + str(p.equipmentMight) + ')'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Melee Dodge:  ' + str(p.totalMeleeDodge) + ' (' +
             str(p.equipmentMeleeDodge) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Spellpower:  ' + str(p.totalSpellpower) + ' (' +
             str(p.equipmentSpellpower) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Magic Resist:  ' + str(p.totalMagicResist) + ' (' +
             str(p.equipmentMagicResist) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Critical Chance:  ' + str(p.totalCriticalChance) + '% (' +
             str(int(p.equipmentCriticalChance)) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Critical Magnitude:  ' + str(p.totalCriticalMagnitude) + '% (' +
             str(p.equipmentCriticalMagnitude) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Armor Penetration:  ' + str(p.totalArmorPenetration) + '% (' +
             str(p.equipmentArmorPenetration) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Damage Resistance:  ' + str(p.totalDR) + '% (' +
             str(p.equipmentDR) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Poison Tolerance:  ' + str(p.totalPoisonTolerance) + ' (' +
             str(p.equipmentPoisonTolerance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Poison Rating Bonus:  ' + str(p.totalPoisonRatingBonus) + ' (' +
             str(p.equipmentPoisonRatingBonus) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Awareness:  ' + str(p.totalAwareness) + ' (' +
             str(p.equipmentAwareness) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Sneak:  ' + str(p.totalSneak) + ' (' + str(p.equipmentSneak) + ')'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Trap Evade:  ' + str(p.totalTrapEvade) + ' (' +
             str(p.equipmentTrapEvade) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Movement Tiles:  ' + str(p.totalMovementTiles) + ' (' +
             str(p.equipmentMovementTiles) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Intuition:  ' + str(p.totalIntuition) + ' (' +
             str(p.equipmentIntuition) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height * 2

        l = 'Tertiary Statistics'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Shop Bonus:  ' + str(p.totalShopBonus) + '% (' +
             str(p.equipmentShopBonus) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Carrying Capacity:  ' + str(p.inventoryCapacity) + ' (' +
             str(p.equipmentCarryingCapacity) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Trap Rating Bonus:  ' + str(p.bonusTrapRating)
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Trap Damage Bonus:  ' + str(p.bonusTrapDamage) + '%'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Jewlery Bonus:  +' + str(p.totalJewleryBonus)
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Potion Bonus Effect:  ' + str(p.totalPotionEffect) + '%'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Trap Damage Reduction:  ' + str(p.totalTrapDamageReduction) +
             '% (' + str(p.equipmentIntuition) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Gold Find:  +' + str(p.goldFind) + '%'
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height * 2
        y = 40
        x += 320

        l = 'Elemental Resistances'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Arcane Resistance:  ' + str(p.totalArcaneResistance) + '% (' +
             str(p.equipmentArcaneResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Cold Resistance:  ' + str(p.totalColdResistance) + '% (' +
             str(p.equipmentColdResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Divine Resistance:  ' + str(p.totalDivineResistance) + '% (' +
             str(p.equipmentDivineResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Electric Resistance:  ' + str(p.totalElectricResistance) +
             '% (' + str(p.equipmentElectricResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Fire Resistance:  ' + str(p.totalFireResistance) + '% (' +
             str(p.equipmentFireResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Poison Resistance:  ' + str(p.totalPoisonResistance) + '% (' +
             str(p.equipmentPoisonResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Shadow Resistance:  ' + str(p.totalShadowResistance) + '% (' +
             str(p.equipmentShadowResistance) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height * 2

        l = 'Elemental Power'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Arcane Damage Bonus:  ' + str(p.totalArcaneBonusDamage) + '% (' +
             str(p.equipmentArcaneBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Cold Damage Bonus:  ' + str(p.totalColdBonusDamage) + '% (' +
             str(p.equipmentColdBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Divine Damage Bonus:  ' + str(p.totalDivineBonusDamage) + '% (' +
             str(p.equipmentDivineBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Electric Damage Bonus:  ' + str(p.totalElectricBonusDamage) +
             '% (' + str(p.equipmentElectricBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Fire Damage Bonus:  ' + str(p.totalFireBonusDamage) + '% (' +
             str(p.equipmentFireBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Poison Damage Bonus:  ' + str(p.totalPoisonBonusDamage) + '% (' +
             str(p.equipmentPoisonBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = ('Shadow Damage Bonus:  ' + str(p.totalShadowBonusDamage) + '% (' +
             str(p.equipmentShadowBonusDamage) + ')')
        f = pfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height * 4

        l = 'Press ' + self.akey + ' to view Active Abilities'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Press ' + self.pkey + ' to view Passive Abilities'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Press ' + self.skey + ' to view Spells'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height
        l = 'Press ' + self.tkey + ' to view Traits'
        f = hfont.render(l, True, Color('black'))
        s.blit(f, (x, y))
        y += f.get_rect().height


class MenuDialog(object):
    '''
    Provides a generic menu dialog for text selections
    '''
    def __init__(self,
                 selections,
                 bgcolor='gray',
                 toptext='Game Paused'):
        '''
        Initialize the class
        '''
        self.bgcolor = bgcolor
        self.toptext = toptext
        self.items = selections
        self.surface = pygame.Surface((1280, 640))
        self.surface.fill(Color(self.bgcolor))
        self.selection = 0

        self._drawtoptext()
        self._drawitems()
        self._updateselection()

    def get_selection(self):
        '''
        Get the current selection
        '''
        return self.selection

    def move_selection(self, direction):
        '''
        Move the current selection (based on num pad directions, 2 4 6 8)
        '''
        selection = self.selection
        if direction == 2:
            selection += 1
        elif direction == 4 or direction == 6:
            pass
        elif direction == 8:
            selection -= 1
        else:
            raise Exception('Invalid direction passed to '
                            'MenuDialog.move_selection')
        selection = min(selection, len(self.items) - 1)
        selection = max(selection, 0)
        self.selection = selection
        self._updateselection()

        return self.selection

    def _updateselection(self):
        '''
        Draw a rectangle around current selection, removing from previous
        '''

        self._drawitems()

        font = pygame.font.SysFont('Arial', 20)
        selected = font.render(items[self.selection], True, Color('black'))

        rect = selected.get_rect()

        x = int(640 - (rect.width / 2))
        y = 100 + (self.selection * 44)

        rect = rect.move(x, y)
        rect = rect.inflate(10, 10)

        pygame.draw.rect(self.surface, Color('yellow'), rect, 3)

    def _drawitems(self):
        '''
        Draw the menu items
        '''
        self.surface.fill(Color(self.bgcolor), (0, 80, 1280, 640))
        y = 100
        font = pygame.font.SysFont('Arial', 20)
        for line in self.items:
            curfont = font.render(line, True, Color('black'))
            x = int(640 - (curfont.get_rect().width / 2))
            self.surface.blit(curfont, (x, y))
            y += 44

    def _drawtoptext(self):
        '''
        Draw the top text area
        '''
        font = pygame.font.SysFont('Arial', 32)
        textsurface = font.render(self.toptext, True, Color('black'))
        x = int(640 - (textsurface.get_rect().width / 2))
        y = 20
        self.surface.blit(textsurface, (x, y))


if __name__ == '__main__':
    import time

    pygame.init()

    items = ['Save Game', 'Load Game', 'Quit Game', 'Party']

    screen = pygame.display.set_mode((1280, 640))
    dialog = MenuDialog(items, bgcolor='gray')
    screen.blit(dialog.surface, (0, 0))
    pygame.display.flip()

    while(True):
        time.sleep(1)
        dialog.move_selection(2)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(2)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(2)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(2)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(4)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(6)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(8)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(8)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(8)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
        dialog.move_selection(8)
        screen.blit(dialog.surface, (0, 0))
        print dialog.get_selection()
        pygame.event.clear()
        time.sleep(1)
        pygame.display.flip()
