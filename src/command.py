'''
Class for communicating map sync actions
'''

class Command:
    def __init__(self, type, action, *args, **kwargs):
        self.type = type.upper()
        self.action = action.upper()
        if args:
            self.args = args
        self.__dict__.update(kwargs)

    def __repr__(self):
        rep = self.__class__.__name__ + "(type: " + self.type + ", action: " + self.action + ", "
        return  rep + ", ".join([attr + ": " + str(val) for attr, val in \
            self.__dict__.iteritems() if attr not in ['type', 'action'] and val != None]) + ")"