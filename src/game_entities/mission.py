"""
Defines Mission class and MissionType enum, data structures representing the different missions that could or should be
accomplished by the player during a level.
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

import pygame

from src.constants import TILE_SIZE
from src.game_entities.destroyable import Destroyable
from src.game_entities.item import Item
from src.game_entities.objective import Objective
from src.game_entities.player import Player
from src.gui.position import Position

if TYPE_CHECKING:
    from src.scenes.level_scene import LevelEntityCollections


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
    objective_tiles -- the objectives linked to the mission that should be displayed on the map
    description -- the description of the mission
    nb_players -- the number of player characters that should validate the mission
    turn_limit -- the limit of turns until the mission would be considered as failed
    gold_reward -- the quantity of gold given to the player in case of success
    items_reward -- the items given to the player in case of success
    targets -- the sequence of destroyable entities that should be eliminated

    Attributes:
    main -- whether the mission is primary or not
    type -- the kind of the mission
    objective_tiles -- the objectives linked to the mission that should be displayed on the map
    description -- the description of the mission
    ended -- whether the mission is ended or not
    turn_limit -- the limit of turns until the mission would be considered as failed
    restrictions -- the list of restrictions regarding the accomplishment of the mission
    gold -- the quantity of gold given to the player in case of success
    items -- the items given to the player in case of success
    min_players -- the minimal number of player characters that should validate the mission
    succeeded_chars -- the player characters which have validated the mission
    targets -- the sequence of destroyable entities that should be eliminated
    """

    def __init__(
        self,
        is_main: bool,
        nature: MissionType,
        objective_tiles: Sequence[Objective],
        description: str,
        nb_players: int,
        turn_limit: Optional[int] = None,
        gold_reward: int = 0,
        items_reward: Optional[Sequence[Item]] = None,
        targets: Optional[Sequence[Destroyable]] = None,
    ) -> None:
        if items_reward is None:
            items_reward = []
        self.main: bool = is_main
        self.type: MissionType = nature
        self.objective_tiles: Sequence[Objective] = objective_tiles
        self.description: str = description
        self.ended: bool = self.type is MissionType.TURN_LIMIT
        self.turn_limit: int = turn_limit
        self.restrictions: Optional[Sequence[str]] = None
        self.gold: int = gold_reward
        self.items: Sequence[Item] = items_reward
        self.min_chars: int = nb_players
        self.succeeded_chars: list[Player] = []
        self.targets = targets

    def is_position_valid(self, position: Position) -> bool:
        """
        Determine whether the mission can be accomplished from the given position or not.
        Return the result of the computation.

        Keyword Arguments:
        position -- the position that should be checked
        """
        if self.type is MissionType.POSITION:
            return position in self.objective_tiles
        if self.type is MissionType.TOUCH_POSITION:
            for objective in self.objective_tiles:
                if (
                    abs(position[0] - objective.position[0])
                    + abs(position[1] - objective.position[1])
                    == TILE_SIZE
                ):
                    return True
        return False

    def update_state(
        self,
        player: Player = None,
        entities: Optional[LevelEntityCollections] = None,
        turns: int = 0,
    ) -> None:
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
            self.type in (MissionType.POSITION, MissionType.TOUCH_POSITION)
        ) and player is not None:
            self.succeeded_chars.append(player)
            self.ended = len(self.succeeded_chars) == self.min_chars
        elif self.type is MissionType.KILL_EVERYBODY:
            self.ended = len(entities.foes) == 0
        elif self.type is MissionType.KILL_TARGETS:
            self.ended = all((target.hit_points <= 0 for target in self.targets))
        elif self.type is MissionType.TURN_LIMIT:
            self.ended = turns <= self.turn_limit

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the objective tiles on the given screen.

        Keyword arguments:
        screen -- the screen on which the tiles should be drawn
        """
        for objective in self.objective_tiles:
            objective.display(screen)
