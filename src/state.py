'''
Save/Load State
'''

import os
import pickle

from const import *

class State(object):
    
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
                pass#print "File doesn't exist " + path_to_file
        except:
            print "Could not open " + path_to_file
            return None
            
    
    @staticmethod
    def remove_temp_dir():
        pass