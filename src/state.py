'''
Save/Load State
'''

import os
import pickle
import datetime

from const import *
from location import Location

class State(object):
    '''
    Static methods to maintain the state of the world. Server must explicitly
    call these methods, or handled from the server's Pane object. As each pane
    is unloaded, it must explicitly call save_pane and pass in the data dict()
    it wants to save. Every pane we visit will have an entry in a master dict()
    that keeps track of the world.
    Additionally, clients use this class to save and load their characters. If 
    a new character is created, this will generate the save file automatically, 
    based on their name and class. It prepends the filename with an incremental
    number (000-999).
    '''
    char_file = None
    world_file = None
    world_data = None
    tmp_world_data = dict()

    @staticmethod
    def load(path, filename):
        '''
        Should not be called directly outside of this class.
        Handles loading a pickled file. Pickle then unpackages
        it and returns the data object from that file, None if 
        there was a problem.
        '''
        path_to_file = os.path.join(path, filename)
        try:
            if os.path.exists(path_to_file):
                data = pickle.load( open( path_to_file, "rb" ) )
                return data
            else:
                return None
        except:
            print "Could not open " + path_to_file
            return None


    @staticmethod
    def save(path, filename, data, overwrite=True, pickled=True):
        '''
        Should not be called from outside of this class. Given a set of
        data, this method saves it to file with the given filename and 
        path. If you want to save the file without pickle, use the 
        pickled flag.  NOTE: load does not currently support loading
        non-pickled files. This option should only be used for non-game
        items, or files that will be accessed with other tools.
        '''
        # Create the saves directories if they don't exist
        if not os.path.exists(path):
            os.makedirs(path)

        if overwrite:
            att = "wb"  #write, byte format
        else:
            att = "ab"  #append, byte format (to keep line endings consistent)
        
        path_to_file = os.path.join(path, filename)
        if pickled:
            pickle.dump( data, open(path_to_file, att))
        else:
            try:
                file = open(path_to_file, att)
                file.write("\n" + data)
                file.close()
            except:
                print "Problem saving unpickled data to " + filename


    @staticmethod
    def load_player(file_name):
        '''
        Returns the player's saved state in the form of it's dehydrated string.
        Member Variables:
            file_name:  Can be 1 of three things:
                1. The full path to a players save file
                2. The filename of the save file (Looking in CHAR_SAVE_PATH)
                3. The 3 digit number at the beginning of the filename (Looking in CHAR_SAVE_PATH)
        
        '''

        if isinstance(file_name, tuple):
            State.char_file = None
            return None
        else:
            if not os.path.exists(file_name):   #Perchance they provide a custom path
                #Used to get filename with just the number
                try:
                    tmp = int(file_name)    #Force try/catch
                    saved_list = os.listdir(CHAR_SAVE_PATH)
                    if saved_list:
                        for filename in saved_list:
                            if filename.split("_")[0] != file_name:  
                                continue
                            else:
                                #path_to_file = os.path.join(CHAR_SAVE_PATH, filename)
                                # print "Substituting " + file_name + " with " + filename
                                file_name = filename
                                break
                except:
                    pass

            State.char_file = file_name
            player_string = State.load(CHAR_SAVE_PATH, State.char_file)
            return player_string


    @staticmethod
    def save_player(player):
        '''
        Dehydrates our current player and saves it.
        '''
        if not player:
            return

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
        if os.path.exists(State.char_file):
            path = ""
        else:
            path = CHAR_SAVE_PATH

        State.save(path, State.char_file, player_string)


    @staticmethod
    def delete_player():
        '''
        Used for Hardcore Death to delete the player's save file
        '''
        file = State.char_file
        #If we haven't saved our character yet we can do nothing
        if file == None:    
            return

        if not os.path.exists(file):
            file = os.path.join(CHAR_SAVE_PATH, file)
        if os.path.exists(file):
            os.remove(file)


    @staticmethod
    def load_world(state):
        '''
        Returns a dictionary with the state of this world.
        Member Variables:
            state:  Can be one of the following:
                    1.  A dictionary with a single key and value:
                        {SEED_KEY   :   "seed"}
                        This means we are creating a new world and we return
                        state.
                    2.  A String with the filename of the world save file
                        Looks in const.py's WORLD_SAVE_PATH.  
                        
                The file is a dictionary that will contain a SEED_KEY with seed
                and any pane data dictionaries with the pane_tuple as
                the key.  e.g.:
                {   
                    SEED_KEY    :   "seed"
                    pane_tuple  :   
                        {
                            MONSTER_KEY :   [(dehydrated_monster, Location_Object), (...)]
                            CHEST_KEY   :   [(type, level, tile_loc), (...)]
                            ITEM_KEY    :   [("items"), (...)] NOT YET IMPLEMENTED
                        }
                }
        '''
        if isinstance(state, dict): #Option 1
            State.world_file = None
            State.world_data = state
        else:                       #Option 2
            State.world_file = state
            State.world_data = State.load(WORLD_SAVE_PATH, State.world_file)

        assert State.world_data != None, "World should be a dictionary with at least a SEED_KEY"
        return State.world_data


    @staticmethod
    def save_world():
        '''
        Automatically overwrites the save file (located in State.world_file)
        or creates a new one in WORLD_SAVE_PATH
        '''
        #print "State.save_world called"
        if not State.world_file:
            #Loop through the WORLD_SAVE_PATH and get incremental save
            max_save = 0
            saved_list = os.listdir(WORLD_SAVE_PATH)
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
            now = datetime.datetime.now()
            State.world_file = str("%03d" % max_save) + "_" + str(now.strftime("%Y-%m-%d_%H%M")) + WORLD_SAVE_EXT

        #Reconcile tmp_world_data with world_data
        #tmp_world_data takes precidence.
        data = dict(State.world_data.items() + State.tmp_world_data.items())
        for key, value in data.iteritems():
            if isinstance(value, dict):
                monsters = value[MONSTER_KEY]
        State.save(WORLD_SAVE_PATH, State.world_file, data)


    @staticmethod
    def load_pane(pane_loc):
        '''
        Returns a dictionary of data for a pane given a location tuple
        for that pane (e.g. (0, 1)) or None if no saved data exists.
        '''

        data = None
        if pane_loc in State.tmp_world_data.keys():
            data = State.tmp_world_data[pane_loc]
        elif pane_loc in State.world_data.keys():
            data = State.world_data[pane_loc]

        return data


    @staticmethod
    def save_pane(pane_loc, data):
        '''
        Saves the given pane data dictionary into our world state dictionary
        '''

        assert isinstance(data, dict), "Pane data should be a dictionary"
        assert isinstance(pane_loc, tuple) or isinstance(pane_loc, Location), "Pane location should be a tuple"
        State.tmp_world_data[pane_loc] = data

