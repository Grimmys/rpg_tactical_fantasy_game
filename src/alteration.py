class Alteration:
    def __init__(self, name, abbr, power, duration, desc, effects=None):
        if effects is None:
            effects = []
        self.name = name
        self.abbreviated_name = abbr
        self.power = power
        self.duration = duration
        self.time = 0
        self.desc = desc
        self.effects = effects

    def get_turns_left(self):
        return self.duration - self.time

    def increment(self):
        self.time += 1

    def is_finished(self):
        return self.time >= self.duration

    def __str__(self):
        return self.name.replace('_', ' ').capitalize()

    def __eq__(self, o):
        return self.name == o
