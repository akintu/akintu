'''
Container class for tracking and evaluating the presence of status effect fields at a location
'''

from region import Region

class Fields:
    def __init__(self):
        self.fields = []

    def add_field(self, name, loc, radius=0, duration=-1):
        '''
        Adds a field with name, radius, and duration at loc
        If duration == -1, the field never expires
        '''
        self.fields.append([name, loc if isinstance(loc, Region) else Region("CIRCLE", loc, radius), duration])

    def remove_field(self, loc, name=None, all=False):
        '''
        Sorts the fields affecting loc by duration, then removes the first one with a matching name
        If all==True, removes all fields rather than just the first one.
        '''
        fields = sorted([f for f in self.fields if f[0] == (name if name else f[0]) and loc in f[1]], key=lambda f: f[2])
        if len(fields) > 0:
            if all:
                self.fields = [x for x in self.fields if x not in fields]
            else:
                self.fields.remove(fields[0])

    def get_fields(self, loc):
        '''
        Returns a list of all fields currently affection location loc
        '''
        return [f[0] for f in self.fields if loc in f[1]]

    def turn(self):
        '''
        Decrements the duration counter for all fields, and removes any fields for which the duration
        counter has reached 0
        '''
        for field in self.fields:
            field[2] -= 1

        self.fields = [f for f in self.fields if f[2] != 0]

    def get_region(self):
        '''
        Converts all current fields to a Region object.  This is used in game.py for display purposes
        '''
        R = Region()
        for f in self.fields:
            R += f[1]
        return R