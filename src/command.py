'''
Class for communicating game state actions across the network
'''

class Command:
    '''
    This class is designed as a container for any kind of value that needs to be communicated.
    To use it, just pass in a named parameter of your choice, and the initializer will create
    an attribute with that name and assign it your value.
    The 'type' and 'action' attributes are for categorizing and handling the commands.  Again,
    these are arbitrary and up to the developer to decide on.
    '''
    def __init__(self, type, action, *args, **kwargs):
        self.type = type.upper()
        self.action = action.upper()
        if args:
            self.args = args
        self.__dict__.update(kwargs)

    def __repr__(self):
        '''
        This is how the command should be shown when printed, and basically just shows all its
        attributes and their values.
        '''
        rep = self.__class__.__name__ + "(type: " + self.type + ", action: " + self.action + ", "
        return  rep + ", ".join([attr + ": " + str(val) for attr, val in \
            self.__dict__.iteritems() if attr not in ['type', 'action'] and val != None]) + ")"