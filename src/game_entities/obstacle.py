from typing import Union

import pygame

from src.game_entities.entity import Entity
from src.gui.position import Position


class Obstacle(Entity):

    def __init__(self, position: Position, sprite: Union[str, pygame.Surface]):
        super().__init__("Obstacle", position, sprite)

    def __hash__(self):
        return hash(self.position)

    def __eq__(self, other: Position):
        return self.position == other
