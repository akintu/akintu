'''
Main visual engine
'''

import pygame
from pygame.locals import *
from pygame import Color

from collections import OrderedDict

import screenutils
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
        self.screen = pygame.display.set_mode((
            PANE_X * TILE_SIZE + 256,
            max(PANE_Y * TILE_SIZE, 20 * TILE_SIZE)))
        pygame.display.set_caption('Akintu r01')
        self.background = pygame.Surface((PANE_X * TILE_SIZE,
                                          PANE_Y * TILE_SIZE))
        self.images = dict()
        self.persons = OrderedDict()
        self.personsgroup = pygame.sprite.RenderUpdates()
        self.playerframes = OrderedDict()
        self.monsterframes = OrderedDict()
        self.scrollcount = 0
        self.textsize = 12
        self.sidetext = []
        self.dialog = None
        pygame.display.flip()

        # Draw the sidebar text area and make sure it has at least one item
        # in it (even though it's a blank item)
        self.show_text('')

    def show_dialog(self, text, items, selection=0, bgcolor='gray'):
        '''
        Show a tiling dialog with the given text, items, and selection
        '''
        self.dialog = screenutils.TilingDialog(text, items, selection, bgcolor)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return selection

    def hide_dialog(self):
        '''
        Hide the dialog, returns the last-selected item
        '''
        if not self.dialog:
            return None
        selection = self.dialog.get_selection()
        self.dialog = None

        self.draw_world()
        self._drawmonsterframes()
        self._drawplayerframes()
        self._draw_text()
        self.personsgroup.update()
        self.personsgroup.draw(self.screen)
        pygame.display.update()
        self.personsgroup.clear(self.screen, self.background)

        return selection

    def get_dialog_selection(self):
        '''
        Get the current selection in the dialog (if it exists)
        '''
        if not self.dialog:
            return None
        return self.dialog.get_selection()

    def move_dialog(self, direction):
        '''
        Move the dialog selection based on the 4 movement directions (2 4 6 8)

        Returns the new selection
        '''
        if not self.dialog:
            return None
        self.dialog.move_selection(direction)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return self.dialog.get_selection()

    def set_pane(self, pane):
        '''
        Set the Pane for the graphics engine to display
        '''
        # Remove all persons first
        for personid in list(self.persons):
            self.personsgroup.remove(self.persons[personid])
            self.persons.pop(personid)
        self.playerframes = OrderedDict()
        self.monsterframes = OrderedDict()
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

        # Make sure we're not in a dialog
        if not self.dialog:
            self.draw_world()
            # Redraw the text area
            self._draw_text()

    def draw_world(self):
        '''
        Draw the world (represented by a Pane)
        '''
        self.screen.fill(Color('black'))
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

        if not self.dialog:
            # Blit the entire background (if this becomes an issue we'll refactor)
            self.screen.blit(self.background, [0, 0])
            self.personsgroup.update()
            self.personsgroup.draw(self.screen)
            pygame.display.update()
            self.personsgroup.clear(self.screen, self.background)

    def add_person(self, personid, statsdict):
        '''
        Add a Person object to the world

        Required entries in statsdict:
            - 'image'
            - 'location'
            - 'team'

        Supported entries in statsdict:
            - 'image'
            - 'location'
            - 'xoffset' (in pixels)
            - 'xoffset' (in pixels)
            - 'foot' (0 or 1)
            - 'name'
            - 'HP'
            - 'MP'
            - 'AP'
            - 'buffedHP'
            - 'totalHP'
            - 'totalMP'
            - 'totalAP'
            - 'restrictedAP'
            - 'level'
            - 'size'
            - 'stealth' (0 or 1)

        To be supported in the future:
            - 'statusList'
            - 'cooldownList'
            - time remaining
            - is it the players turn?
        '''
        # Check for properly-formatted statsdict, set some defaults if not
        # present
        if 'image' not in statsdict or \
           'location' not in statsdict or \
           'team' not in statsdict:
            raise Exception('Image, location, or team not defined')
        for attr in ['xoffset', 'yoffset', 'foot', 'stealth']:
            if attr not in statsdict:
                statsdict[attr] = 0

        self.persons[personid] = PersonSprite(statsdict)
        self.personsgroup.add(self.persons[personid])

        if statsdict['team'] == "Players":
            self.playerframes[personid] = \
                self._generateplayerframe(personid)
            if not self.dialog:
                self._drawplayerframes()
        elif statsdict['team'] == "Monsters":
            self.monsterframes[personid] = \
                self._generatemonsterframe(personid)
            if not self.dialog:
                self._drawmonsterframes()

    def remove_person(self, personid):
        '''
        Remove a Person object from the world
        '''
        self.personsgroup.remove(self.persons[personid])
        self.persons.pop(personid)
        if personid in self.playerframes:
            self.playerframes.pop(personid)
            if not self.dialog:
                self._drawplayerframes()
        elif personid in self.monsterframes:
            self.monsterframes.pop(personid)
            if not self.dialog:
                self._drawmonsterframes()

    def update_person(self, personid, statsdict):
        '''
        Update statsdict for a Person object

        See documentation for add_person() to see supported entries in
        statsdict
        '''
        if 'location' in statsdict:
            self.persons[personid].current_coord = statsdict['location']
        self.persons[personid].update_dict(statsdict)

        for key in statsdict:
            if key in ['name', 'HP', 'MP', 'AP', 'buffedHP', 'totalHP', 'size',
                       'totalMP', 'totalAP', 'restrictedAP', 'level']:
                if statsdict['team'] == "Players":
                    self.playerframes[personid] = \
                        self._generateplayerframe(personid)
                    if not self.dialog:
                        self._drawplayerframes()
                elif statsdict['team'] == "Monsters":
                    self.monsterframes[personid] = \
                        self._generatemonsterframe(personid)
                    if not self.dialog:
                        self._drawmonsterframes()

    def update(self):
        '''
        Updates and redraws necessary parts of the game world

        Should be called once per game loop cycle
        '''
        if not self.dialog:
            self.personsgroup.update()
            rectlist = self.personsgroup.draw(self.screen)
            pygame.display.update(rectlist)
            self.personsgroup.clear(self.screen, self.background)

    def set_fps(self, fps):
        '''
        Set the FPS in the title bar (if enabled)
        '''
        if SHOW_FPS:
            pygame.display.set_caption("%s %d" % (CAPTION, int(fps)))

    def scroll_down(self, scrollamount=1):
        '''
        Scroll the text box down by scrollamount (default 1)
        '''
        self.scrollcount += scrollamount
        if self.scrollcount >= len(self.sidetext):
            self.scrollcount = len(self.sidetext) - 1
        if not self.dialog:
            self._draw_text()

    def scroll_up(self, scrollamount=1):
        '''
        Scroll the text box up by scrollamount (default 1)
        '''
        self.scrollcount -= scrollamount
        if self.scrollcount < 0:
            self.scrollcount = 0
        if not self.dialog:
            self._draw_text()

    def show_text(self, text, color='white', size=None):
        '''
        Add a text string to the scrolling sidebar text area

        Pass in size argument to set the text size for the whole box
        '''
        if size:
            self.textsize = size
        self.sidetext.insert(0, (text, color))
        if self.scrollcount > 0:
            self.scrollcount += 1
        if len(self.sidetext) > 100:
            self.sidetext = self.sidetext[:100]
        if self.scrollcount >= len(self.sidetext):
            self.scrollcount = len(self.sidetext) - 1
        if not self.dialog:
            self._draw_text()

    def _draw_text(self):
        '''
        Draw up to 10 lines of text in the sidebar text box

        Starts from self.scrollcount
        '''
        lines = []
        count = self.scrollcount

        for text, color in self.sidetext[count:count+10]:
            words = text.split(' ')
            beg = 0
            end = 1

            font = pygame.font.SysFont("Arial", self.textsize)

            txt = ' '.join(words[beg:end])
            prev = font.render(txt, True, Color(color))
            cur = None

            while beg < len(words) and end <= len(words):
                txt = ' '.join(words[beg:end])
                cur = font.render(txt, True, Color(color))
                rect = cur.get_rect()
                if rect.width > 246:
                    lines.append(prev)
                    beg = end - 1
                    txt = ' '.join(words[beg:end])
                    prev = font.render(txt, True, Color(color))
                    continue
                end += 1
                prev = cur
            lines.append(prev)

        height = lines[0].get_rect().height
        textarea = pygame.Surface((246, 100))
        y = 0

        for line in lines:
            textarea.blit(line, (0, y))
            y += height

        # Draw a 2 px border 1 px outside of text rect
        borderouter = (PANE_X * TILE_SIZE + 2, 297, 252, 106)
        borderinner = (PANE_X * TILE_SIZE + 4, 299, 248, 102)
        if self.scrollcount == 0:
            self.screen.fill(Color('gray'), borderouter)
        else:
            self.screen.fill(Color('blue'), borderouter)
        self.screen.fill(Color('black'), borderinner)

        top = 300
        left = PANE_X * TILE_SIZE + 5
        rect = (left, top, 246, 100)
        self.screen.fill(Color('black'), rect)
        self.screen.blit(textarea, (left, top))

        pygame.display.update([borderouter])

    def _generateplayerframe(self, personid):
        '''
        Generate unit frame for a given player personid

        Grabs the relevant data out of the PersonSprite object for that
        personID, and returns the surface for the unit frame, which can be
        blitted onto any other surface.
        '''
        frame = pygame.Surface((246, 70))
        frame.fill(Color('gray'))
        image = self.persons[personid].images[0][2]
        statsdict = self.persons[personid].statsdict

        if 'name' not in statsdict:
            name = 'Mysterious Adventurer'
        else:
            name = statsdict['name']

        # Retrieve stats (error-checking as we go)
        if 'totalHP' not in statsdict or statsdict['totalHP'] <= 0:
            totalHP = None
        else:
            totalHP = statsdict['totalHP']
        if 'HP' not in statsdict or not totalHP:
            HP = 0
        else:
            HP = statsdict['HP']
        if 'buffedHP' not in statsdict or not totalHP:
            buffedHP = 0
        else:
            buffedHP = statsdict['buffedHP']
        if 'totalMP' not in statsdict or statsdict['totalMP'] <= 0:
            totalMP = None
        else:
            totalMP = statsdict['totalMP']
        if 'MP' not in statsdict or not totalMP:
            MP = 0
        else:
            MP = statsdict['MP']
        if 'totalAP' not in statsdict or statsdict['totalAP'] <= 0:
            totalAP = None
        else:
            totalAP = statsdict['totalAP']
        if 'AP' not in statsdict or not totalAP:
            AP = 0
        else:
            AP = statsdict['AP']
        if 'restrictedAP' not in statsdict or not totalAP:
            restrictedAP = 0
            reducedAP = totalAP
        else:
            restrictedAP = statsdict['restrictedAP']
            reducedAP = totalAP
            totalAP = restrictedAP + totalAP
        if 'level' not in statsdict:
            level = '0'
        else:
            level = str(statsdict['level'])

        hstring = str(HP)
        mstring = str(MP) + ' / ' + (str(totalMP) if totalMP else '0')
        astring = str(AP) + ' / ' + (str(reducedAP) if totalAP else '0')

        barx = 32 + 4 + 40
        barlabelx = 32 + 4 + 4
        barxsize = 166
        barysize = 10
        hbary = 16
        if totalHP:
            hbar1 = barxsize
            hbar2 = int(float(HP) / totalHP * barxsize)
            hbar3 = int(float(buffedHP) / totalHP * barxsize)
        else:
            hbar1 = barxsize
            hbar2 = 0
            hbar3 = 0
        mbary = hbary + 12
        if totalMP:
            mbar1 = barxsize
            mbar2 = int(float(MP) / totalMP * barxsize)
        else:
            mbar1 = barxsize
            mbar2 = 0
        abary = mbary + 12
        if totalAP:
            abar1 = barxsize
            abar2 = int(float(AP) / totalAP * barxsize)
            abarredx = int(float(reducedAP) / totalAP * barxsize)
            abarredwidth = barxsize - abarredx
            abarredx += barx
        else:
            abar1 = barxsize
            abar2 = 0

        frame.blit(image, (4, 4))
        frame.fill(Color('black'), (barx, hbary, hbar1, barysize))
        frame.fill(Color('red'), (barx, hbary, hbar2, barysize))
        frame.fill(Color('darkred'), (barx, hbary, hbar3, barysize))
        frame.fill(Color('black'), (barx, mbary, mbar1, barysize))
        frame.fill(Color('blue'), (barx, mbary, mbar2, barysize))
        frame.fill(Color('black'), (barx, abary, abar1, barysize))
        frame.fill(Color('purple'), (barx, abary, abar2, barysize))
        frame.fill(Color('yellow'), (abarredx, abary, abarredwidth, barysize))

        font = pygame.font.SysFont("Arial", 10)
        hfont = font.render(hstring, True, Color('black'))
        mfont = font.render(mstring, True, Color('black'))
        afont = font.render(astring, True, Color('black'))
        frame.blit(hfont, (barlabelx, hbary))
        frame.blit(mfont, (barlabelx, mbary))
        frame.blit(afont, (barlabelx, abary))

        font = pygame.font.SysFont("Arial", 12, bold=True)
        namefont = font.render(name, True, Color('black'))
        frame.blit(namefont, (barx, 2))

        font = pygame.font.SysFont("Arial", 16, bold=True)
        levelfont = font.render(level, True, Color('black'))
        left = 4 + 16 - (levelfont.get_rect().width // 2)
        frame.blit(levelfont, (left, 40))

        return frame

    def _generatemonsterframe(self, personid):
        '''
        Generate unit frame for a given monster personid

        Grabs the relevant data out of the PersonSprite object for that
        personID, and returns the surface for the unit frame, which can be
        blitted onto any other surface.
        '''
        frame = pygame.Surface((121, 40))
        frame.fill(Color('gray'))
        image = self.persons[personid].images[0][2]
        statsdict = self.persons[personid].statsdict

        if 'name' not in statsdict:
            name = 'Grue'
        else:
            name = statsdict['name']

        # Retrieve stats (error-checking as we go)
        if 'totalHP' not in statsdict or statsdict['totalHP'] <= 0:
            totalHP = None
        else:
            totalHP = statsdict['totalHP']
        if 'HP' not in statsdict or not totalHP:
            HP = 0
        else:
            HP = statsdict['HP']
        if 'totalMP' not in statsdict or statsdict['totalMP'] <= 0:
            totalMP = None
        else:
            totalMP = statsdict['totalMP']
        if 'MP' not in statsdict or not totalMP:
            MP = 0
        else:
            MP = statsdict['MP']
        if 'level' not in statsdict:
            level = 'L0'
        else:
            level = 'L' + str(statsdict['level'])
        if 'size' not in statsdict:
            size = ''
        else:
            size = statsdict['size']

        hstring = str(HP)

        barx = 32 + 4 + 35
        barlabelx = 32 + 4 + 4
        barxsize = 46
        barysize = 5
        hbary = 16
        if totalHP:
            hbar1 = barxsize
            hbar2 = int(float(HP) / totalHP * barxsize)
        else:
            hbar1 = barxsize
            hbar2 = 0
        mbary = hbary + 7
        if totalMP:
            mbar1 = barxsize
            mbar2 = int(float(MP) / totalMP * barxsize)
        else:
            mbar1 = barxsize
            mbar2 = 0

        frame.blit(image, (4, 4))
        frame.fill(Color('black'), (barx, hbary, hbar1, barysize))
        frame.fill(Color('red'), (barx, hbary, hbar2, barysize))
        frame.fill(Color('black'), (barx, mbary, mbar1, barysize))
        frame.fill(Color('blue'), (barx, mbary, mbar2, barysize))

        font = pygame.font.SysFont("Arial", 9)
        hfont = font.render(hstring, True, Color('black'))
        frame.blit(hfont, (barlabelx, hbary))

        font = pygame.font.SysFont("Arial", 12, bold=True)
        namefont = font.render(name, True, Color('black'))
        frame.blit(namefont, (barlabelx, 2))

        font = pygame.font.SysFont("Arial", 9, bold=True)
        levelfont = font.render(size + ' ' + level, True, Color('black'))
        frame.blit(levelfont, (barlabelx, hbary + 12))

        return frame

    def _drawplayerframes(self):
        '''
        Draw the unitframes inside of self.playerframes
        '''
        top = 4
        left = PANE_X * TILE_SIZE + 5
        rect = (left, top, 246, 292)
        self.screen.fill(Color('black'), rect)

        for personid in self.playerframes:
            self.screen.blit(self.playerframes[personid], (left, top))
            top += 74
        pygame.display.update([rect])

    def _drawmonsterframes(self):
        '''
        Draw the unitframes inside of self.monsterframes
        '''
        top = 507
        left = PANE_X * TILE_SIZE + 5
        rect = (left, top, 246, 132)
        self.screen.fill(Color('black'), rect)

        for personid in self.monsterframes:
            self.screen.blit(self.monsterframes[personid], (left, top))
            top += 44
            if (top - 507) / 132 >= 1:
                top = 507
                left = left + 121 + 4
        pygame.display.update([rect])


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
        xoff = self.statsdict['xoffset']
        yoff = self.statsdict['yoffset']
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
        foot = self.statsdict['foot']
        xoff = self.statsdict['xoffset']
        yoff = self.statsdict['yoffset']
        loc = self.current_coord
        self.rect.topleft = (loc.tile[0] * TILE_SIZE + xoff,
                             loc.tile[1] * TILE_SIZE + yoff)
        self.image = self.images[foot][loc.direction]
        self.dirty = 1

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


def set_alpha(image, alpha):
    '''
    Given a surface, return a surface with the given alpha applied to every
    pixel
    '''
    newimage = pygame.Surface((image.get_width(), image.get_height()))
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            c = image.get_at((x, y))
            if c[3] != 0:
                c = (c[0], c[1], c[2], alpha)
                newimage.set_at((x, y), c)
    return newimage
