from region import Region

class Fields:
    def __init__(self):
        self.fields = []

    def add_field(self, name, loc, radius, duration):
        self.fields.append([name, Region("CIRCLE", loc, radius), duration])

    def get_fields(self, loc):
        return [f[0] for f in self.fields if loc in f[1]]

    def turn(self):
        for field in self.fields:
            field[2] -= 1

        self.fields = [f for f in self.fields if f[2] > 0]

    def get_region(self):
        R = Region()
        for f in self.fields:
            R += f[1]
        return R