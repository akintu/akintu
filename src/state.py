'''
Save/Load State
'''

import os
import pickle

from const import *

class State(object):
    
    char_file = None
    world_file = dict()
    tmp = dict()
    
    @staticmethod
    def init_world(world_save_file):
        '''
        Member Variables:
            world_save_file:    String with the filename of the world save file
                                Looks in const.py''s WORLD_SAVE_PATH.  It is a 
                                dictionary that will contain AT A MINIMUM SEED_KEY,
                                but it can contain any of the following:
                                {   
                                    SEED_KEY    :   "seed",
                                    MONSTER_KEY :   [(dehydrated_monster, Location_Object), (...)]
                                    CHEST_KEY   :   [(type, level, tile_loc), (...)]
                                    ITEM_KEY    :   [("items"), (...)] TODO: NOT YET IMPLEMENTED (3/15/2013)
                                }
        '''
        
        State.world = State.load(WORLD_SAVE_PATH, world_save_file)
        assert State.world == None, "World should be a dictionary with SEED_KEY (min)"
    
    @staticmethod
    def save(path, filename, data, overwrite=True):
        # Create the saves directories if they don't exist
        if not os.path.exists(path):
            os.makedirs(path)
        # if not os.path.exists(CHAR_SAVE_PATH):
            # os.makedirs(CHAR_SAVE_PATH)
        # if not os.path.exists(WORLD_SAVE_PATH):
            # os.makedirs(WORLD_SAVE_PATH)

        if overwrite:
            att = "wb"  #write, byte format
        else:
            att = "ab"  #append, byte format (to keep line endings consistent)
        
        path_to_file = os.path.join(path, filename)
        # try:
        pickle.dump( data, open(path_to_file, att))
        # except:
            # print "Problem saving" + str(data) + "to " + filename
        # file = open(path_to_file, att) 
        # file.write("\n" + data)
        # file.close()
        
    @staticmethod
    def load(path, filename):
        path_to_file = os.path.join(path, filename)
        try:
            if os.path.exists(path_to_file):
                print "Attempting to open " + path_to_file
                data = pickle.load( open( path_to_file, "rb" ) )
                # file = open(path_to_file, "rb")
                # for line in file:
                    # pass
                # last = line
                # file.close()
                # print "Unpickled Data: "
                # print data
                return data
            else:
                return None#print "File doesn't exist " + path_to_file
        except:
            print "Could not open " + path_to_file
            return None
            
    
    @staticmethod
    def load_player(file_name):
        '''
        Returns the player's saved state in the form of it's dehydrated string.
        Member Variables:
            file_name:  Can be 1 of three things:
                1. The full path to a players save file
                2. The filename of thesave file (Looking in CHAR_SAVE_PATH)
                3. The 3 digit number at the beginning of the filename (Looking in CHAR_SAVE_PATH)
        
        '''
        
        if isinstance(file_name, tuple):
            State.char_file = None
            return None
        else:
            if not os.path.exists(file_name):   #Perchance they provide a custom path
                try:
                    tmp = int(file_name)    #Force try/catch
                    saved_list = os.listdir(CHAR_SAVE_PATH)
                    if saved_list:
                        for filename in saved_list:
                            if filename.split("_")[0] != file_name:  
                                continue
                            else:
                                #path_to_file = os.path.join(CHAR_SAVE_PATH, filename)
                                print "Substituting " + file_name + " with " + filename
                                file_name = filename
                                State.char_file = filename
                                break
                except:
                    print "Could not find " + str(file_name)

        player_string = State.load(CHAR_SAVE_PATH, file_name)
        return player_string
        
    @staticmethod
    def save_player(player):
        '''
        Dehydrates our current player and saves it.
        '''

        if not State.char_file:
            saved_list = os.listdir(CHAR_SAVE_PATH)
            max_save = 0
            if saved_list:
                increment_list = []
                for filename in saved_list:
                    split_list = filename.split("_")
                    tmp = split_list[0] #Get first element from list (the incremental save number)
                    try:
                        tmp = int(tmp)
                    except:
                        tmp = 0
                    increment_list.append(tmp)
                max_save = max(increment_list)
            max_save += 1
            State.char_file = str("%03d" % max_save) + "_" + str(player.name) + "_" + str(player.race) + "_" + str(player.characterClass) + CHAR_SAVE_EXT
        
        player_string = player.dehydrate()
        State.save(CHAR_SAVE_PATH, State.char_file, player_string)
        
        