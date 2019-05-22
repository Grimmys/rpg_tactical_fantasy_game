

class Alteration:
    def __init__(self, name, effect, power, duration):
        self.name = name
        self.effect = effect
        self.power = power
        self.duration = duration
        self.time = 0

    def get_name(self):
        return self.name

    def time(self):
        self.time += 1
        return self.time == self.duration
