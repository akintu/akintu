'''
Save/Load State
'''

import os
import pickle
import datetime

from const import *

class State(object):
    
    char_file = None
    world_file = None
    
    world_data = None
    tmp_world_data = dict()
    
    log_data = ""
    
    @staticmethod
    def load(path, filename, pickled=True):
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
    def save(path, filename, data, overwrite=True, pickled=True):
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
                                print "Substituting " + file_name + " with " + filename
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
                            ITEM_KEY    :   [("items"), (...)] TODO: NOT YET IMPLEMENTED (3/15/2013)
                        }
                }
        '''
        
        if isinstance(state, dict): #Option 1
            State.world_file = None
            State.world_data = state
        else:                       #Option 2
            State.world_file = state
            State.world_data = State.load(WORLD_SAVE_PATH, State.world_file)
            
        for key, value in State.world_data.iteritems():
            if isinstance(value, dict):
                # print "PANE: " + str(key)
                monsters = value[MONSTER_KEY]
                # for monster in monsters:
                    # print "\tMonster loc: " + str(monster[1])
        
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
                # print "PANE: " + str(key)
                monsters = value[MONSTER_KEY]
                # for monster in monsters:
                    # print "\tMonster loc: " + str(monster[1])
                
        State.save(WORLD_SAVE_PATH, State.world_file, data)
        
        
    @staticmethod
    def load_pane(pane_loc):
        '''
        Returns a dictionary of data for a pane given a location tuple
        for that pane (e.g. (0, 1)) or None if no saved data exists.
        '''
        
        data = None
        if pane_loc in State.tmp_world_data:
            data = State.tmp_world_data[pane_loc]
        elif pane_loc in State.world_data:
            data = State.world_data[pane_loc]
        
        #print "Loading pane " + str(pane_loc) + " with data " + str(data)
        if data:
            # print "PANE: " + str(pane_loc)
            monsters = data[MONSTER_KEY]
            # for monster in monsters:
                # print "\tMonster loc: " + str(monster[1])
        return data
        
    @staticmethod
    def save_pane(pane_loc, data):
        '''
        Saves the given pane data dictionary into our world state dictionary
        '''
        
        assert isinstance(data, dict), "Pane data should be a dictionary"
        assert isinstance(pane_loc, tuple), "Pane location should be a tuple"
        #print "Saving pane " + str(pane_loc)+ " with data " + str(data)
        State.tmp_world_data[pane_loc] = data
        
        if data:
            #print "PANE: " + str(pane_loc)
            monsters = data[MONSTER_KEY]
            # for monster in monsters:
                # print "\tMonster loc: " + str(monster[1])
        
    @staticmethod
    def log(data):
        pass

    @staticmethod
    def save_log():
        pass
        