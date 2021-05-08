from enum import Enum, auto

from src.constants import TILE_SIZE


class MissionType(Enum):
    POSITION = auto()
    TOUCH_POSITION = auto()
    KILL_EVERYBODY = auto()
    KILL_TARGETS = auto()
    TURN_LIMIT = auto()


class Mission:
    def __init__(self, is_main, nature, positions, description, nb_players,
                 turn_limit=None, gold_reward=0, items_reward=None):
        if items_reward is None:
            items_reward = []
        self.main = is_main
        self.type = nature
        self.positions = positions
        self.desc = description
        self.ended = self.type is MissionType.TURN_LIMIT
        self.turn_limit = turn_limit
        self.restrictions = None
        self.gold = gold_reward
        self.items = items_reward
        self.min_chars = nb_players
        self.succeeded_chars = []

    def pos_is_valid(self, pos):
        if self.type is MissionType.POSITION:
            return pos in self.positions
        if self.type is MissionType.TOUCH_POSITION:
            for mission_pos in self.positions:
                if abs(pos[0] - mission_pos[0]) + abs(pos[1] - mission_pos[1]) == TILE_SIZE:
                    return True
        return False

    def update_state(self, player=None, entities=None, turns=0):
        if (self.type is MissionType.POSITION or self.type is MissionType.TOUCH_POSITION) \
                and player is not None:
            self.succeeded_chars.append(player)
            self.ended = len(self.succeeded_chars) == self.min_chars
        elif self.type is MissionType.KILL_EVERYBODY:
            self.ended = len(entities['foes']) == 0
        elif self.type is MissionType.TURN_LIMIT:
            self.ended = turns <= self.turn_limit
        return True
