"""
Defines utility functions for stuff related to GUI.
"""

from __future__ import annotations

from math import sqrt

import pygame

from src.constants import (DARK_GREEN, LIGHT_YELLOW, ORANGE, RED, TILE_SIZE,
                           YELLOW)
from src.gui.position import Position


def show_fps(
    surface: pygame.Surface, inner_clock: pygame.time.Clock, font: pygame.font.Font
) -> None:
    """
    Display in the top left corner of the screen the current frame rate.

    Keyword arguments:
    screen -- the surface on which the framerate should be drawn
    inner_clock -- the pygame clock running and containing the current frame rate
    font -- the font used to display the frame rate
    """
    fps_text = font.render(f"FPS: {inner_clock.get_fps():.0f}", True, LIGHT_YELLOW)
    surface.blit(fps_text, (2, 2))


def blit_alpha(
    target: pygame.Surface,
    source: pygame.Surface,
    location: Position,
    opacity: int,
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
    target.blit(source, (location.x, location.y))


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


def determine_gauge_color(
    current_value: int, max_value: int, default_color: pygame.Color
) -> pygame.Color:
    """
    Return the color that should be used to display the gauge of a measure
    (for example the hit points of an entity).

    Keyword arguments:
    current_value -- the current value of the measure
    max_value -- the maximum value that could be reached
    default_color -- the default color that should be returned when the gauge is relatively full
    """
    if current_value == max_value:
        return default_color
    if current_value >= max_value * 0.75:
        return DARK_GREEN
    if current_value >= max_value * 0.5:
        return YELLOW
    if current_value >= max_value * 0.30:
        return ORANGE
    return RED
