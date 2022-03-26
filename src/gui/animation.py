"""
Defines Animation class, useful for memorize frames of an ongoing animation.
"""

from __future__ import annotations

from typing import Union

import pygame

from src.gui.position import Position

FrameDescription = dict[str, Union[pygame.Surface, Position]]


class Frame:
    """
    Define the properties of a single animation frame

    Keyword arguments:
    surface -- the content of the frame
    position -- the position where the content should be displayed
    duration -- the duration of the frame, will be set to the default value for the animation if not provided

    Attributes:
    surface -- the content of the frame
    position -- the position where the content should be displayed
    duration -- the duration of the frame
    """

    def __init__(self, surface: pygame.Surface, position: Position, duration: int = 0):
        self.surface: pygame.Surface = surface
        self.position: Position = position
        self.duration: int = duration


class Animation:
    """
    Manage any kind of ongoing animation: not an already finished animation or a "planned" one.
    The list of frames should be ordered before the initialization of an instance.

    Keyword arguments:
    frames -- the ordered list of frames with their position and duration
    default_frame_delay -- default delay (in game frames) between each animation frame

    Attributes:
    frames -- the ordered list of frames with their position and duration
    current_frame -- the current displayed frame with its position
    timer -- the elapsed number of games frames since the previous frame has been displayed
    """

    def __init__(
        self,
        frames: list[Frame],
        default_frame_delay: int,
    ) -> None:
        self.frames: list[Frame] = frames
        self._init_frames(default_frame_delay)
        self.current_frame: Frame = self.frames.pop(0)
        self.timer: int = self.current_frame.duration

    def animate(self) -> bool:
        """
        Decrement the timer and check if the next frame should replace the current frame.

        Return whether the animation is ended or not.
        """
        self.timer -= 1
        if self.timer == 0:
            if self.frames:
                self.current_frame = self.frames.pop(0)
                self.timer = self.current_frame.duration
            else:
                return True
        return False

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the current frame on the given pygame Surface

        Keyword arguments:
        screen -- the screen on which the current frame should be drawn
        """
        screen.blit(self.current_frame.surface, self.current_frame.position)

    def _init_frames(self, default_frame_delay) -> None:
        for frame in self.frames:
            if frame.duration == 0:
                frame.duration = default_frame_delay
