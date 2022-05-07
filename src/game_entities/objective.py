from typing import Union

import pygame

from src.game_entities.entity import Entity
from src.gui.position import Position


class Objective(Entity):
    def __init__(
        self, position: Position, sprite: Union[str, pygame.Surface], walkable: bool
    ):
        super().__init__("Objective", position, sprite)
        self.walkable = walkable

    def __eq__(self, other: Position):
        return self.position == other
