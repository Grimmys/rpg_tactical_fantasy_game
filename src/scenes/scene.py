"""
Define Scene class, the abstract base class for any other scene.
"""

from __future__ import annotations

from enum import IntEnum, auto

import pygame

from src.gui.position import Position


class QuitActionKind(IntEnum):
    """
    Defines the different kind of actions when trying to quit game
    """

    CONTINUE = auto()
    QUIT = auto()
    RESTART = auto()


class Scene:
    """
    This class is the abstract base class for every specific scene.
    It is defining common stuff shared by all of them so the scene manager could do the same basic operations on
    any scene without needing to know its kind.

    Keyword arguments:
    screen -- the pygame Surface related to the scene

    Attributes:
    screen -- the pygame Surface related to the scene
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def display(self) -> None:
        """
        Display all the content of the scene.
        """
        pass

    def update_state(self) -> bool:
        """
        Take care of updating the state of the scene and returning whether it's finished or not.

        Return whether the scene should be ended or not.
        """
        pass

    def motion(self, position: Position) -> None:
        """
        Handle motion event.

        Keyword arguments:
        position -- the position of the mouse
        """
        pass

    def click(self, button: int, position: Position) -> QuitActionKind:
        """
        Handle the triggering of a click event.

        Keyword arguments:
        button -- an integer value representing which mouse button has been pressed
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        return QuitActionKind.CONTINUE

    def button_down(self, button: int, position: Position) -> None:
        """
        Handle the triggering of a mouse button down event.

        Keyword arguments:
        button -- an integer value representing which mouse button is down
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        pass

    def key_down(self, keyname: int) -> None:
        """
        Handle the triggering of a key down event.

        Keyword arguments:
        keyname -- an integer value representing which key button is down
        (27 for Escape key)
        """
        pass
