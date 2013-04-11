from region import Region

class Fields:
    def __init__(self):
        self.fields = []

    def add(self, name, loc, r, duration):
        self.fields.append([name, Region("CIRCLE", loc, r), duration])

    def get_fields(self, loc):
        return [field[0] for field in self.fields if loc in field[1]]

    def decrement_duration(self):
        for field in self.fields:
            field[2] -= 1

        self.fields = [f for f in self.fields if f[2] > 0]

    def get_region(self):
        R = Region()
        for f in self.fields:
            R += f[1]
        return R