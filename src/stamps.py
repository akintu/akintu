import sys, os
from const import *
from region import *

class Stamp(object):
    '''
    Used for parsing stamp files for later use by Township.py. Stamps files
    are categorized for finer grain placement, if desired. A stamp file is 
    saved with the convention X_Y.txt where X and Y represent the width and
    height of the stamps in that file (respectively). Each stamp is preceded
    by two lines. They will begin with # but can have other information on the
    line that will be ignored. e.g a file called 4_6.txt might look like this:
        #   4x6 Landscape Stamp
        #
        tttrrr
        ttwwrr
        twwwww
        twwwww
        #
        #
        ... (more stamps follow)
    The content of each stamp is determined by Stamp.key_dict. It contains the 
    key value pairs that the world can use to place the appropriate objects on
    the pane. The key is a single character, the value is the key that will be
    used by the Sprite class to determine the image to use, and allows for 
    specific funtionality (e.g. passability).

    The exception to this convention is the text.txt stamp file. It contains
    additional information for each stamp to allow for varied widths within
    the same file. Text stamps will always be 5 tiles tall.
    '''
    BOSS = "boss"
    DUNGEON = "dungeon"
    HOUSE = "house"
    SHOP = "shop"
    RESPEC = "respec"
    GARDEN = "garden"
    TREASURE = "treasure"
    MAZE = "maze"
    WATER = "water"
    LANDSCAPE = "landscape"
    SPAWN = "spawn"
    TEXT = "text"

    keys = [DUNGEON, HOUSE, SHOP, RESPEC, GARDEN, TREASURE, WATER, LANDSCAPE, SPAWN, BOSS]
    key_dict = {' ': None,
                '_': None,
                'p':'walk',
                'd':'dirt',
                'l':'gravel',
                'f':'flowers',
                '+':'obstacle',
                'g':'grass',
                'r':'rock',
                's':'shrub',
                't':'tree',
                'w':'water',
                'b':'bones',
                '$':CHEST_KEY,
                'm':MONSTER_KEY,
                'B':BOSS_KEY,
                'G':'garden',
                'H':'house',
                'R':'respec',
                'S':'shop',
                'D':'dungeon',
                'P':'portal'}
    obst_dict = dict((v,k) for k,v in key_dict.iteritems())
    loaded = False

    def __init__(self, size, data):
        self.size = size
        self.width = size[0]
        self.height = size[1]
        self.data = data
        self.region = Region()

    def __repr__(self):
        string = "\n"
        for i in range(self.height):
            start = i*self.width
            end = start+self.width
            string += self.data[start:end] + "\n"
        return string

    def __str__(self):
        return self.__repr__()

    def getRegion(self, location=Location((0, 0), (0, 0))):
        '''
        Returns a Region object that contains the locations of 
        entities within this stamp.
        '''
        right = location.tile[0]
        bottom = location.tile[1]
        self.region("ADD", "SQUARE", location, Location(location.pane, (right + self.width-1, bottom + self.height-1)))
        loc = location
        for i in range(self.height):
            tmp = loc.move(2, i)
            start = i*self.width
            end = start+self.width
            string = self.data[start:end]
            for j in range(self.width):
                tmp2 = tmp.move(6, j)
                if string[j] == " ":
                    self.region("SUB", "SQUARE", tmp2, tmp2)
        return self.region
        
    def getEntityLocations(self, location):
        '''
        Returns the locations and keys of all the entities 
        in this stamp as a dictionary. Used by Pane to 
        load the stamp.
        '''
        entities_dict = dict()
        for i in range(self.height):
            tmp = location.move(2, i)
            start = i*self.width
            end = start+self.width
            data_line = self.data[start:end]
            for j in range(self.width):
                tmp2 = tmp.move(6, j)
                key = data_line[j]
                entities_dict[tmp2] = self.key_dict[key]
        return entities_dict

    def join(self, direction, stamp, distance=0):
        '''
        Used to join two stamps together. Currently
        only used with text stamps, and as such, does
        not fully support other stamps or placement
        schemes. It is only to be used with stamps of
        the same height. Uses the direction scheme 
        defined in Location.py
        '''
        new_string = ""
        padding = ""
        for pad in range(distance):
            padding += " "
        if direction in [6, 4]:
            if direction == 6: 
                a = self
                b = stamp
            else:
                a = stamp
                b = self
            
            width = a.width + b.width + distance
            height = max(a.height, b.height)
            for i in range(a.height):
                start_1 = i*a.width
                start_2 = i*b.width
                end_1 = start_1+a.width
                end_2 = start_2+b.width
                new_string += a.data[start_1:end_1] + padding + b.data[start_2:end_2]
                    
        if direction == 2:
            assert False, "Currenly only suports joining stamps horizontally"

        return Stamp((width, height), new_string)


    @staticmethod
    def load():
        '''
        Parses all stamp files into memory
        '''
        if Stamp.loaded:
            return
        Stamp.loaded = True
        Stamp.allSizes = dict()
        Stamp.allTypes = dict()
        Stamp.allStamps = dict()

        for key in Stamp.keys:
            Stamp.allStamps[key] = Stamp.parseStampFiles(os.path.join(STAMP_PATH, key))

        #This is not included. Replace 'd' with the type of entity you would
        #like the text to represent. 'dirt' is passable, so that is why it is used.
        Stamp.text = Stamp.parseTextStamps(('+', 'd'))

    @staticmethod
    def getStamps(key):
        '''
        Returns the stamps of a particular key contained in Stamp.keys.
        '''
        if not Stamp.loaded:
            Stamp.load()
        if key in Stamp.allStamps:
            return Stamp.allStamps[key]
        else:
            print "Key " + str(key) + " not found"

    @staticmethod
    def getStringStamp(text):
        '''
        Used to get a stamp that represents the 'text'
        '''
        text = str(text).upper()
        if not Stamp.loaded:
            Stamp.load()
        if len(text) < 1:
            return 
        tmp_stamp = Stamp.text[text[0]]

        for i in range(1,len(text)):
            tmp_stamp = tmp_stamp.join(6, Stamp.text[text[i]], distance=1)

        return tmp_stamp

    @staticmethod
    def parseStampFiles(path, rep=("+", "+")):
        '''
        Parses the stamps in the file given by path.
        '''
        stamp_dict = dict()
        stamp_files = None
        if os.path.exists(path):
            stamp_files = os.listdir(path)

        head, tail = os.path.split(path)
        Stamp.allTypes[tail] = []

        if stamp_files:
            for filename in stamp_files:
                # print filename
                stamp_list = []
                width, ext = filename.split("_")
                width = int(width)
                height = int(ext.split(".")[0])

                Stamp.allTypes[tail].append((width, height))
                if not (width, height) in Stamp.allSizes:
                    Stamp.allSizes[(width, height)] = []
                Stamp.allSizes[(width, height)].append(tail)
                #Open File and Read in lines
                file = os.path.join(path, filename)
                lines_in = open(file, 'r').readlines()
                num_stamps = len(lines_in)/(height+2)

                for i in range(num_stamps):
                    tlines = lines_in[i*(height+2) : i*(height+2)+(height+2)]
                    char_string = ""
                    for j in range(height):
                        tmp = tlines[j+2][:-1] + " "*width    #Strip newline and pad with spaces
                        tmp = tmp.replace(rep[0], rep[1])
                        tmp = tmp.replace("\t", "    ")
                        tlines[j+2] = tmp[:width]
                        char_string += tlines[j+2]
                    stamp_list.append(Stamp(size=(width, height), data=char_string))
                stamp_dict[(width, height)] = stamp_list

        return stamp_dict

    @staticmethod
    def parseTextStamps(rep=('+', '+')):
        '''
        Parses the text.txt stamp file.
        '''
        text_dict = dict()
        path = os.path.join(STAMP_PATH, "text", "font.txt")
        if not os.path.exists(path):
            print path + " not found"
            return
        lines_in = open(path, 'r').readlines()
        num_chars = len(lines_in)/7

        for i in range(num_chars):
            tlines = lines_in[7*i : 7*i + 7]

            # get character  
            tchar = tlines[0][:-1] # remove newline

            # get width of character
            width = int(tlines[1].strip())
            # print (str(width) + ": \"" + str(tchar) + "\"")

            # remove newline and combine rows into one string
            # pad the end to make sure it fills the width
            char_string = ""
            for j in range(5):
                tmp = tlines[j+2][:-1] + " "*width
                tmp = tmp.replace(rep[0], rep[1])
                tlines[j+2] = tmp[:width]
                char_string += tlines[j+2]

            text_dict[tchar] = Stamp(size=(width, 5), data=char_string)
        return text_dict

if __name__ == "__main__":
    '''
    Test Routines
    '''
    pass
    # stamps = Stamp.getStamps(Stamp.TEXT)
    stamp = Stamp.getStringStamp("hELLO WORLD!")
    print stamp
    region = stamp.getRegion()
    print region
    
    for key in Stamp.keys:
        Stamp.getStamps(key)
