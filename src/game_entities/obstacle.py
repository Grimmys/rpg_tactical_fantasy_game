"""
Defines Obstacle class, a class representing a non-movable entity that cannot be crossed by movable entities.
"""

from typing import Union

import pygame

from src.game_entities.entity import Entity
from src.gui.position import Position


class Obstacle(Entity):
    """
    An Obstacle is a static entity that acts like a wall for movable entities.

    Keyword Arguments:
    position -- the current position of the obstacle on screen
    sprite -- the pygame Surface corresponding to the appearance of the obstacle on screen or
    the relative path to the visual representation of the obstacles
    """

    def __init__(self, position: Position, sprite: Union[str, pygame.Surface]):
        super().__init__("Obstacle", position, sprite)

    def __hash__(self):
        return hash(self.position)

    def __eq__(self, other: Position):
        return self.position == other
