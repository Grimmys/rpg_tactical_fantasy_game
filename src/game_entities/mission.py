from enum import Enum, auto
from typing import Sequence, Union, List

from src.constants import TILE_SIZE
from src.game_entities.entity import Entity
from src.game_entities.item import Item
from src.game_entities.player import Player


class MissionType(Enum):
    POSITION = auto()
    TOUCH_POSITION = auto()
    KILL_EVERYBODY = auto()
    KILL_TARGETS = auto()
    TURN_LIMIT = auto()


class Mission:
    """

    """
    def __init__(self, is_main: bool, nature: MissionType, positions: Sequence[tuple[int, int]],
                 description: str, nb_players: int, turn_limit: int = None, gold_reward: int = 0,
                 items_reward: Sequence[Item] = None) -> None:
        if items_reward is None:
            items_reward = []
        self.main: bool = is_main
        self.type: MissionType = nature
        self.positions: Sequence[tuple[int, int]] = positions
        self.description: str = description
        self.ended: bool = self.type is MissionType.TURN_LIMIT
        self.turn_limit: int = turn_limit
        self.restrictions: Union[Sequence[str], None] = None
        self.gold: int = gold_reward
        self.items: Sequence[Item] = items_reward
        self.min_chars: int = nb_players
        self.succeeded_chars: List[Player] = []

    def position_is_valid(self, position: tuple[int, int]) -> bool:
        """

        :param position:
        :return:
        """
        if self.type is MissionType.POSITION:
            return position in self.positions
        if self.type is MissionType.TOUCH_POSITION:
            for mission_pos in self.positions:
                if abs(position[0] - mission_pos[0]) + abs(position[1] - mission_pos[1])\
                        == TILE_SIZE:
                    return True
        return False

    def update_state(self, player: Player = None, entities: dict[str, Sequence[Entity]] = None,
                     turns: int = 0) -> bool:
        """

        :param player:
        :param entities:
        :param turns:
        :return:
        """
        if (self.type is MissionType.POSITION or self.type is MissionType.TOUCH_POSITION) \
                and player is not None:
            self.succeeded_chars.append(player)
            self.ended = len(self.succeeded_chars) == self.min_chars
        elif self.type is MissionType.KILL_EVERYBODY:
            self.ended = len(entities['foes']) == 0
        elif self.type is MissionType.TURN_LIMIT:
            self.ended = turns <= self.turn_limit
        return True
