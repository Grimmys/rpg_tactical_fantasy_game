from enum import Enum, auto


class MissionType(Enum):
    POSITION = auto()
    KILL_EVERYBODY = auto()
    MAIN_TURN_LIMIT = auto()


class Mission:
    def __init__(self, is_main, nature, positions, description, nb_players=1, turn_limit=-1):
        self.main = is_main
        self.type = nature
        self.positions = positions
        self.desc = description
        self.ended = self.type is MissionType.MAIN_TURN_LIMIT
        self.turn_limit = turn_limit
        self.restrictions = None
        if self.main:
            self.min_chars = nb_players
        self.succeeded_chars = []

    def pos_is_valid(self, pos):
        return pos in self.positions

    def update_state(self, player=None, entities=None, turns=0):
        if self.type is MissionType.POSITION and player is not None:
            self.succeeded_chars.append(player)
            self.ended = len(self.succeeded_chars) == self.min_chars
        elif self.type is MissionType.KILL_EVERYBODY:
            self.ended = len(entities['foes']) == 0
        elif self.type is MissionType.MAIN_TURN_LIMIT:
            self.ended = turns <= self.turn_limit
        return True
