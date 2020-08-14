from enum import Enum, auto


class SkillNature(Enum):
    MULTIPLE_ATTACKS = auto()
    ACTIVE = auto()
    ALLY_BOOST = auto()
    ALTERATION_CHANCE_BOOST = auto()


class Skill:
    def __init__(self, name, formatted_name, nature, desc, power=0, stats=[], alterations=[]):
        self.name = name
        self.formatted_name = formatted_name
        self.nature = SkillNature[nature]
        self.desc = desc
        self.power = power
        self.stats = stats
        self.alterations = alterations

    def __eq__(self, o):
        return self.name == o

    def __str__(self):
        return self.name
