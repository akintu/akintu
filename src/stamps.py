import sys, os
from const import *
from region import *

class Stamp(object):
    DUNGEON = "dungeon"
    HOUSE = "house"
    SHOP = "shop"
    GARDEN = "garden"
    TREASURE = "treasure"
    MAZE = "maze"
    WATER = "water"
    LANDSCAPE = "landscape"
    TEXT = "text"
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
        self.region("ADD", "SQUARE", location, Location(location.pane, (self.width-1, self.height-1)))
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
                j = 0
        return self.region

    def join(self, arg, stamp, distance=0):
        new_string = ""
        padding = ""
        for pad in range(distance):
            padding += " "
        if arg == "HORIZONTAL":
            width = self.width + stamp.width + distance
            height = max(self.height, stamp.height)
            # print(width, height)
            #TODO: This will break when self.height is less than stamp.height
            for i in range(self.height):
                start_1 = i*self.width
                start_2 = i*stamp.width
                end_1 = start_1+self.width
                end_2 = start_2+stamp.width
                new_string += self.data[start_1:end_1] + padding + stamp.data[start_2:end_2]
                    
        if arg == "VERTICAL":
            pass

        return Stamp((width, height), new_string)


    @staticmethod
    def load():
        if Stamp.loaded:
            return
        Stamp.loaded = True

        #Open the stamp files and parse the information
        Stamp.dungeon = dict()
        Stamp.house = dict()
        Stamp.shop = dict()
        Stamp.garden = dict()
        Stamp.treasure = dict()
        Stamp.water = dict()
        Stamp.landscape = dict()
        Stamp.text = Stamp.parseTextStamps()

    @staticmethod
    def getStamps(key):
        if not Stamp.loaded:
            Stamp.load()
        if key == Stamp.DUNGEON:
            return Stamp.dungeon
        if key == Stamp.HOUSE:
            return Stamp.house
        if key == Stamp.SHOP:
            return Stamp.shop
        if key == Stamp.GARDEN:
            return Stamp.garden
        if key == Stamp.TREASURE:
            return Stamp.treasure
        if key == Stamp.WATER:
            return Stamp.water
        if key == Stamp.LANDSCAPE:
            return Stamp.landscape
        if key == Stamp.TEXT:
            return Stamp.text
    
    @staticmethod
    def getStringStamp(text):
        text = str(text).upper()
        if not Stamp.loaded:
            Stamp.load()
        if len(text) < 1:
            return 
        tmp_stamp = Stamp.text[text[0]]

        for i in range(1,len(text)):
            tmp_stamp = tmp_stamp.join("HORIZONTAL", Stamp.text[text[i]], distance=1)

        return tmp_stamp

    @staticmethod
    def parseTextStamps():
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
            tchar = tlines[0][:-1] # remove NL

            # get width of character
            width = int(tlines[1].strip())
            # print (str(width) + ": \"" + str(tchar) + "\"")

            # remove newline and combine rows into one string
            # pad the end to make sure it fills the width
            char_string = ""
            for j in range(5):
                tmp = tlines[j+2][:-1] + "     "
                tlines[j+2] = tmp[:width]
                char_string += tlines[j+2]

            text_dict[tchar] = Stamp(size=(width, 5), data=char_string)
            #text_dict[tchar] = [(width, 5), char_string]
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
    
        
#4x2 house
HOUSE_STAMPS = {(8, 5):["\
 TTTTTTT\
 TfHHHH \
 TfHPHH \
 Tffpppp\
    pTTT"],\
(7, 6):["\
T    TT\
T HHHHT\
T HPHHT\
T  pTTT\
ppppppp\
SSSS   "]}


#3x4 dungeon opening
DUNGEON_STAMPS = {(6, 6):["\
 RRRRR\
 RDDDR\
 mDDD \
  DDD \
  DPDm\
pppppp"],\
(8, 5):["\
R RDDDRT\
R mDDD T\
R  DDD T\
R  DPDm \
Rpppppp"]}
