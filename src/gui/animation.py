"""
Defines Animation class, useful for memorize frames of an ongoing animation.
"""

from __future__ import annotations

from typing import Union, List

import pygame

from src.gui.position import Position


class Animation:
    """
    Manage any kind of ongoing animation: not an already finished animation or a "planned" one.
    The list of frames should be ordered before the initialization of an instance.

    Keyword arguments:
    sprites_positions -- the ordered list of the frames with their position
    timer -- the delay between the displaying of the next frame

    Attributes:
    sprites_positions -- the ordered list of the frames with their position
    timer_max -- the delay between the displaying of the next frame
    timer -- the elapsed time since the previous frame has been displayed
    current_frame -- the current displayed frame with its position
    """

    def __init__(
        self,
        sprites_positions: List[dict[str, Union[pygame.Surface, Position]]],
        timer: int,
    ) -> None:
        self.sprites_positions: List[
            dict[str, Union[pygame.Surface, Position]]
        ] = sprites_positions
        self.timer_max: int = timer
        self.timer: int = timer
        self.current_frame: dict[
            str, Union[pygame.Surface, Position]
        ] = self.sprites_positions.pop(0)

    def animate(self) -> bool:
        """
        Increment the timer and check if the next frame should replace the current frame.

        Return whether the animation is ended or not.
        """
        self.timer -= 1
        if self.timer == 0:
            if self.sprites_positions:
                self.timer = self.timer_max
                self.current_frame = self.sprites_positions.pop(0)
            else:
                return True
        return False

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the current frame on the given pygame Surface

        Keyword arguments:
        screen -- the screen on which the current frame should be drawn
        """
        screen.blit(self.current_frame["sprite"], self.current_frame["pos"])
