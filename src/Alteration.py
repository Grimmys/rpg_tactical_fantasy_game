

class Alteration:
    def __init__(self, name, power, duration, desc):
        self.name = name
        self.power = power
        self.duration = duration
        self.time = 0
        self.desc = desc

    def get_formatted_name(self):
        return self.name.replace('_', ' ').capitalize()

    def get_turns_left(self):
        return self.duration - self.time

    def increment(self):
        self.time += 1
        return self.time > self.duration
