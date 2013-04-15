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
        self.overlays = {}

        overlay_colors = ['blue', 'green', 'red', 'cyan', 'orange', 'black']
        for c in overlay_colors:
            color = Color(c)
            color.a = 50
            self.overlays[c] = generate_overlay(TILE_SIZE, TILE_SIZE, color)

        pygame.display.flip()
        self.turntime = 0
        self.tile_updated = False

        # Draw the sidebar text area and make sure it has at least one item
        # in it (even though it's a blank item)
        self.show_text('')

    def show_tiling_dialog(self, text, items, selection=0, bgcolor='gray'):
        '''
        Show a tiling dialog with the given text, items, and selection
        '''
        self.dialog = screenutils.TilingDialog(text, items, selection, bgcolor)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return self.dialog.get_selection()

    def show_item_dialog(self,
                         text,
                         leftitems,
                         rightitems,
                         equipment=False,
                         bgcolor='gray',
                         capacity='',
                         gold='',
                         discount='',
                         valuemod=(1.0, 1.0)):
        '''
        Show an item dialog with the given parameters
        '''
        self.dialog = screenutils.ItemDialog(text,
                                             leftitems,
                                             rightitems,
                                             equipment,
                                             bgcolor,
                                             capacity,
                                             gold,
                                             discount,
                                             valuemod)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return self.dialog.get_selection()

    def show_character_dialog(self,
                              player,
                              bgcolor='gray',
                              abilitykey='H',
                              spellkey='J',
                              passivekey='K',
                              traitkey='L'):
        '''
        Show the character status dialog
        '''
        self.dialog = screenutils.CharacterDialog(player,
                                                  bgcolor,
                                                  abilitykey,
                                                  spellkey,
                                                  passivekey,
                                                  traitkey)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return None

    def show_menu_dialog(self,
                         items,
                         bgcolor='gray',
                         toptext='Save your progress?'):
        '''
        Show the menu dialog
        '''
        self.dialog = screenutils.MenuDialog(items, bgcolor, toptext)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return self.dialog.get_selection()

    def show_text_dialog(self,
                         text,
                         title,
                         bgcolor='lightblue',
                         nextkey='N',
                         backkey='B',
                         exitkey='Q',
                         topkey='T'):
        '''
        Show a text dialog
        '''
        self.dialog = screenutils.TextDialog(text,
                                             title,
                                             bgcolor,
                                             nextkey,
                                             backkey,
                                             exitkey,
                                             topkey)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return None

    def show_dual_pane_dialog(self,
                              text,
                              leftitems,
                              rightitems,
                              bgcolor='gray'):
        '''
        Show a dual pane dialog with the given parameters
        '''
        self.dialog = screenutils.DualPaneDialog(text,
                                                 leftitems,
                                                 rightitems,
                                                 bgcolor)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return self.dialog.get_selection()

    def update_dual_pane_dialog_text(self, text):
        '''
        Update the top text of a dual pane dialog
        '''
        if not self.dialog:
            return None
        self.dialog.update_toptext(text)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()

    def update_dual_pane_dialog_items(self, leftitems, rightitems):
        '''
        Update the item lists in the item dialog
        '''
        if not self.dialog:
            return None
        ret = self.dialog.set_items(leftitems, rightitems)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return ret

    def update_item_dialog_text(self, text, capacity=None, gold=None):
        '''
        Update the top text (and optionally capacity) of an item dialog
        '''
        if not self.dialog:
            return None
        self.dialog.update_toptext(text, capacity, gold)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()

    def update_item_dialog_items(self, leftitems, rightitems):
        '''
        Update the item lists in the item dialog
        '''
        if not self.dialog:
            return None
        ret = self.dialog.set_items(leftitems, rightitems)
        self.screen.blit(self.dialog.surface, (0, 0))
        pygame.display.update()
        return ret

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

        for k, v in self.pane.tiles.iteritems():
            v.overlay = []

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

            for o in tile.overlay:
                self.background.blit(self.overlays[o],
                                     (i*TILE_SIZE, j*TILE_SIZE))

        self.screen.blit(self.background, [0, 0])
        pygame.display.update()

    def update_tile(self, tile, location):
        '''
        Update a specific tile in the current pane
        '''
        tile.overlay = self.pane.tiles[location.tile].overlay
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

        for o in tile.overlay:
            self.background.blit(self.overlays[o],
                                 (i*TILE_SIZE, j*TILE_SIZE))

        self.tile_updated = True

    def set_overlay(self, location, overlay=None):
        '''
        Set the overlay for a specific tile in the current pane

        If overlay is an empty list, remove all overlays
        '''
        tile = self.pane.tiles[location.tile]
        if overlay is None:
            tile.overlay = []
        else:
            tile.overlay = overlay
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

        for o in tile.overlay:
            self.background.blit(self.overlays[o],
                                 (i*TILE_SIZE, j*TILE_SIZE))

        self.tile_updated = True

    def get_overlay(self, location):
        '''
        Get the overlay status for a specific tile in the current pane
        '''
        return self.pane.tiles[location.tile].overlay

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
            - 'statusList'

        To be supported in the future:
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
        for attr in ['xoffset', 'yoffset', 'foot']:
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
                       'totalMP', 'totalAP', 'restrictedAP', 'level',
                       'statusList']:
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
            if self.tile_updated:
                self.screen.blit(self.background, [0, 0])
                self.personsgroup.update()
                self.personsgroup.draw(self.screen)
                pygame.display.update()
                self.personsgroup.clear(self.screen, self.background)
            else:
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

    def set_turntime(self, turntime):
        '''
        Sets the turntime, which should be between 0.0 and 1.0 (percent of turn
        remaining
        '''
        self.turntime = turntime
        self._drawturntime()

    def _drawturntime(self):
        '''
        Draw the turn timer
        '''
        timerrect = (PANE_X * TILE_SIZE + 251, 0, 5, 296)
        diff = (1-self.turntime)*296
        ctimerrect = (PANE_X * TILE_SIZE + 251, diff, 5, 296-diff)
        self.screen.fill(Color('black'), timerrect)
        self.screen.fill(Color('green'), ctimerrect)
        pygame.display.update([timerrect])

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

        hstring = str(int(HP))
        mstring = str(int(MP))
        astring = str(int(AP)) + ' / ' + (str(int(reducedAP))
                                          if totalAP else '0')

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

        if 'statusList' not in statsdict:
            statsdict['statusList'] = []
            # Test code -- 'unstring' to see statuses in action
            '''
            class Status(object):
                def __init__(self):
                    self.image = 'res/images/icons/monster_status/bleeding.png'
                    self.turnsLeft = 5
            statsdict['statusList'] = [Status(), Status(), Status(), Status(),
                                       Status(), Status(), Status(), Status()]
            '''

        y = abary + 12
        x = barx
        font = pygame.font.SysFont('Arial', 10)
        for status in statsdict['statusList']:
            image = pygame.image.load(
                    statsdict['statusList'][status]['image']).convert_alpha()
            image = pygame.transform.smoothscale(image, (16, 16))
            turns_to_display = statsdict['statusList'][status]['turnsLeft']
            if turns_to_display == -1:
                turns_to_display = ""
            turns = font.render(str(turns_to_display), True, Color('black'))
            frame.blit(image, (x, y))
            x += image.get_rect().width + 1
            frame.blit(turns, (x, y))
            x += turns.get_rect().width + 2

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

        if 'statusList' not in statsdict:
            statsdict['statusList'] = []
            # Test code -- 'unstring' to see statuses in action
            '''
            class Status(object):
                def __init__(self):
                    self.image = 'res/images/icons/monster_status/bleeding.png'
                    self.turnsLeft = 5
            statsdict['statusList'] = [Status(), Status(), Status(), Status(),
                                       Status(), Status(), Status(), Status()]
            '''

        y = mbary + 6
        x = barx
        font = pygame.font.SysFont('Arial', 10)
        for status in statsdict['statusList']:
            image = pygame.image.load(
                    statsdict['statusList'][status]['image']).convert_alpha()
            image = pygame.transform.smoothscale(image, (10, 10))
            turns = font.render(
                    str(statsdict['statusList'][status]['turnsLeft']),
                    True,
                    Color('black'))
            frame.blit(image, (x, y))
            x += image.get_rect().width + 1
            frame.blit(turns, (x, y-1))
            x += turns.get_rect().width + 1

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
        self._drawturntime()
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
            # Normal images
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
            endings = [(2, '_fr1.png'), (4, '_lf1.png'),
                       (6, '_rt1.png'), (8, '_bk1.png')]
            self.images.append(
                {key:
                    set_alpha(pygame.image.load(imagepre+end).convert_alpha())
                 for key, end in endings})
            endings = [(2, '_fr2.png'), (4, '_lf2.png'),
                       (6, '_rt2.png'), (8, '_bk2.png')]
            self.images.append(
                {key:
                    set_alpha(pygame.image.load(imagepre+end).convert_alpha())
                 for key, end in endings})
            # Stealthed images
        except pygame.error:
            # Assume imagepre is the actual image location, add facing overlays
            self.images = facing_overlays(imagepre)

        # Location and rect info
        loc = self.statsdict['location']
        foot = self.statsdict['foot']
        xoff = self.statsdict['xoffset']
        yoff = self.statsdict['yoffset']
        stealth = 0
        for status in ['Stealth', 'Shadow Walk', 'Conceal']:
            if status in self.statsdict.get('statusList', []):
                stealth = 1
        self.image = self.images[foot + (2 * stealth)][loc.direction]
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
        stealth = 0
        for status in ['Stealth', 'Shadow Walk', 'Conceal']:
            if status in self.statsdict.get('statusList', []):
                stealth = 1
        loc = self.current_coord
        self.rect.topleft = (loc.tile[0] * TILE_SIZE + xoff,
                             loc.tile[1] * TILE_SIZE + yoff)
        self.image = self.images[foot + (2 * stealth)][loc.direction]
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
    # Normal images
    imagedict = dict()
    for key, rect in zip(keys, rects):
        imagedict[key] = pygame.image.load(imageloc).convert_alpha()
        imagedict[key].fill(Color('blue'), rect)
    # Stealthed images
    simagedict = dict()
    for key, rect in zip(keys, rects):
        simagedict[key] = \
            set_alpha(pygame.image.load(imageloc).convert_alpha())
        simagedict[key].fill(Color('blue'), rect)
    return [imagedict, imagedict, simagedict, simagedict]


def set_alpha(image, alpha=100):
    '''
    Given a surface, return a surface with the given alpha applied to every
    pixel
    '''
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            c = image.get_at((x, y))
            if c[3] != 0:
                c = (c[0], c[1], c[2], alpha)
                image.set_at((x, y), c)
    return image


def generate_overlay(width, height, rgba):
    '''
    Given a width and height and an RGBA tuple, generate a transparent surface
    with that RGBA and return it
    '''
    surface = pygame.Surface((width, height)).convert_alpha()
    for x in range(width):
        for y in range(height):
            surface.set_at((x, y), rgba)
    return surface


class Item(object):
    '''
    Generic item, for use in the DualPaneDialog
    '''
    def __init__(self, name, details, color='black'):
        '''
        Initialize the item
        '''
        self.displayName = name
        self.color = color
        self.details = details
