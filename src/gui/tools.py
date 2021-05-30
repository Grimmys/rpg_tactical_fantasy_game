"""
Defines utilitary functions for stuff related to GUI.
"""

from math import sqrt

import pygame

from src.constants import TILE_SIZE
from src.gui.position import Position


def blit_alpha(
    target: pygame.Surface, source: pygame.Surface, location: Position, opacity: int
):
    """
    Blit a surface on one other but with a specific opacity.

    Keyword arguments:
    target -- the destination pygame Surface
    source -- the pygame Surface that will be blitted
    location -- the position where the blit should be done
    opacity -- the opacity of the blitted surface
    """
    source.set_alpha(opacity)
    target.blit(source, location)


def distance(position: Position, other_position: Position) -> int:
    """
    Return the Euclidean distance of two 2D points.

    Keyword arguments:
    position -- the first position
    other_position -- the other position
    """
    return (
        sqrt(
            (position[0] - other_position[0]) ** 2
            + (position[1] - other_position[1]) ** 2
        )
        // TILE_SIZE
    )
