"""
Defines Mission class and MissionType enum, data structures representing the different missions that could or should be
accomplished by the player during a level.
"""

from enum import Enum, auto
from typing import Sequence, Union, List, Optional, Tuple, Dict

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
    A Mission is an objective that can be accomplished by the player during a level.
    It can be a primary objective (i.e. mandatory) or only a secondary objective.

    Keyword Arguments:
    is_main -- whether the mission is primary or not
    nature -- the kind of the mission
    positions -- the positions of the key elements of the mission
    description -- the description of the mission
    nb_players -- the number of player characters that should validate the mission
    turn_limit -- the limit of turns until the mission would be considered as failed
    gold_reward -- the quantity of gold given to the player in case of success
    items_reward -- the items given to the player in case of success

    Attributes:
    main -- whether the mission is primary or not
    type -- the kind of the mission
    positions -- the positions of the key elements of the mission
    description -- the description of the mission
    ended -- whether the mission is ended or not
    turn_limit -- the limit of turns until the mission would be considered as failed
    restrictions -- the list of restrictions regarding the accomplishment of the mission
    gold -- the quantity of gold given to the player in case of success
    items -- the items given to the player in case of success
    min_players -- the minimal number of player characters that should validate the mission
    succeeded_chars -- the player characters which have validated the mission
    """

    def __init__(
        self,
        is_main: bool,
        nature: MissionType,
        positions: Sequence[Tuple[int, int]],
        description: str,
        nb_players: int,
        turn_limit: int = None,
        gold_reward: int = 0,
        items_reward: Sequence[Item] = None,
    ) -> None:
        if items_reward is None:
            items_reward = []
        self.main: bool = is_main
        self.type: MissionType = nature
        self.positions: Sequence[Tuple[int, int]] = positions
        self.description: str = description
        self.ended: bool = self.type is MissionType.TURN_LIMIT
        self.turn_limit: int = turn_limit
        self.restrictions: Optional[Sequence[str]] = None
        self.gold: int = gold_reward
        self.items: Sequence[Item] = items_reward
        self.min_chars: int = nb_players
        self.succeeded_chars: List[Player] = []

    def is_position_valid(self, position: Tuple[int, int]) -> bool:
        """
        Determine whether the mission can be accomplished from the given position or not.
        Return the result of the computation.

        Keyword Arguments:
        position -- the position that should be checked
        """
        if self.type is MissionType.POSITION:
            return position in self.positions
        if self.type is MissionType.TOUCH_POSITION:
            for mission_pos in self.positions:
                if (
                    abs(position[0] - mission_pos[0])
                    + abs(position[1] - mission_pos[1])
                    == TILE_SIZE
                ):
                    return True
        return False

    def update_state(
        self,
        player: Player = None,
        entities: Dict[str, Sequence[Entity]] = None,
        turns: int = 0,
    ) -> bool:
        """
        Update the state of the mission.
        Verify whether it's ended or not.
        Return always True.

        Keyword Arguments:
        player -- the player character who have validated the mission if any
        entities -- the list of entities related to the mission
        turns -- the number of turns elapsed since the beginning of the current level
        """
        if (
            self.type is MissionType.POSITION or self.type is MissionType.TOUCH_POSITION
        ) and player is not None:
            self.succeeded_chars.append(player)
            self.ended = len(self.succeeded_chars) == self.min_chars
        elif self.type is MissionType.KILL_EVERYBODY:
            self.ended = len(entities["foes"]) == 0
        elif self.type is MissionType.TURN_LIMIT:
            self.ended = turns <= self.turn_limit
        return True
