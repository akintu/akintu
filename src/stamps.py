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
    
    def __init__(self):
        pass

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
        Stamp.text = Stamp.parseText()
        
    @staticmethod
    def joinStamps(arg, region, **stamps):
        if arg == "HORIZONTAL":
            pass
        if arg == "VERTICAL":
            pass
        if arg == "RANDOM":
            pass

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
        text = str(text)
        if not Stamp.loaded:
            Stamp.load()
        for c in text:
            if c in Stamp.text:
                Stamp.text[c]


    @staticmethod
    def parseText():
        text_dict = dict()
        path = os.path.join(STAMP_PATH, "text", "font.txt")
        if not os.path.exists(path):
            print path + " not found"
            return
        lines_in = open(path, 'r').readlines()
        num_chars = len(lines_in)/7

        print str(num_chars) + " characters in font.txt"
        for i in range(num_chars):
            tlines = lines_in[7*i : 7*i + 7]

            # get character  
            tchar = tlines[0][:-1] # remove NL

            # get width of character
            width = int(tlines[1].strip())
            # print (str(width) + ": \"" + str(tchar) + "\"")

            # remove newline and combine rows into one string
            char_string = ""
            for j in range(5):
                tmp = tlines[j+2][:-1] + "     "
                tlines[j+2] = tmp[:width]
                char_string += tlines[j+2]
          
            text_dict[tchar] = [(width, 5), char_string]
        return text_dict

if __name__ == "__main__":
    '''
    Test Routines
    '''
    print Stamp.getStamps(Stamp.TEXT)
        
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
