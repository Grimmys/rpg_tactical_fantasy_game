"""
Defines Objective class, a class representing a single marker related to a given mission that should be
displayed on the map.
"""

from typing import Union

import pygame

from src.game_entities.entity import Entity
from src.gui.position import Position


class Objective(Entity):
    """
    An Objective is an entity displayed on the map and related to one or multiple missions that should be accessed by
    one or more players in able to finish the given mission(s).

    Keyword Arguments:
    name -- the name of the objective
    position -- the current position of the objective on screen
    sprite -- the pygame Surface corresponding to the appearance of the objective on screen or
    the relative path to the visual representation of the objective
    walkable -- whether the objective should be considered as an obstacle or not for the movable entities

    Attributes:
    is_walkable -- whether the objective should be considered as an obstacle or not for the movable entities
    """

    def __init__(
        self,
        name: str,
        position: Position,
        sprite: Union[str, pygame.Surface],
        walkable: bool,
    ):
        super().__init__(name, position, sprite)
        self.is_walkable = walkable

    def __eq__(self, other: Position):
        return self.position == other
