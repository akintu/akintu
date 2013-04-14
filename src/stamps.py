import sys, os
from const import *
from region import *

class Stamp(object):
    DUNGEON = "dungeon"
    HOUSE = "house"
    SHOP = "shop"
    RESPEC = "respec"
    GARDEN = "garden"
    TREASURE = "treasure"
    MAZE = "maze"
    WATER = "water"
    LANDSCAPE = "landscape"
    TEXT = "text"
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
                'B':'building',
                'G':'garden',
                'H':'house',
                'R':'respec',
                'S':'shop',
                'D':'dungeon',
                'P':'portal'}
    loaded = False

    def __init__(self, size, data):
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
            # print(width, height)
            #TODO: This will break when a.height is less than b.height
            #Need to add padding to the string that has no more data to give
            for i in range(a.height):
                start_1 = i*a.width
                start_2 = i*b.width
                end_1 = start_1+a.width
                end_2 = start_2+b.width
                new_string += a.data[start_1:end_1] + padding + b.data[start_2:end_2]
                    
        if direction == 2:
            pass

        return Stamp((width, height), new_string)


    @staticmethod
    def load():
        if Stamp.loaded:
            return
        Stamp.loaded = True
        Stamp.allSizes = dict()
        Stamp.allTypes = dict()
        Stamp.allStamps = dict()

        Stamp.keys = [Stamp.DUNGEON, Stamp.HOUSE, Stamp.SHOP, Stamp.RESPEC, Stamp.GARDEN, Stamp.TREASURE, Stamp.WATER, Stamp.LANDSCAPE]
        for key in Stamp.keys:
            Stamp.allStamps[key] = Stamp.parseStampFiles(os.path.join(STAMP_PATH, key))

        #This is not included in Stamp.allSizes, Stamp.allTypes, or 
        Stamp.text = Stamp.parseTextStamps(('+', 'd'))

    @staticmethod
    def getStamp(size):
        if size in Stamp.allSizes:
            pass

    @staticmethod
    def getStamps(key):
        if not Stamp.loaded:
            Stamp.load()
        if key in Stamp.allStamps:
            return Stamp.allStamps[key]
        else:
            print "Key " + str(key) + " not found"

    @staticmethod
    def getStringStamp(text):
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
