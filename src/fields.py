from region import Region

class Fields:
    def __init__(self):
        self.fields = []

    def add_field(self, name, loc, radius=0, duration=-1):
        self.fields.append([name, loc if isinstance(loc, Region) else Region("CIRCLE", loc, radius), duration])

    def remove_field(self, name, loc, all=False):
        fields = sorted([f for f in self.fields if f[0] == name and loc in f[1]], key=lambda f: f[2])
        if len(fields) > 0:
            if all:
                self.fields = [x for x in self.fields if x not in fields]
            else:
                self.fields.remove(fields[0])

    def get_fields(self, loc):
        return [f[0] for f in self.fields if loc in f[1]]

    def turn(self):
        for field in self.fields:
            field[2] -= 1

        self.fields = [f for f in self.fields if f[2] != 0]

    def get_region(self):
        R = Region()
        for f in self.fields:
            R += f[1]
        return R