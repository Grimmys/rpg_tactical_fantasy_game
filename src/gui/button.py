"""
Defines Button class, a BoxElement able to react to user actions.
"""
from enum import Enum
from typing import List, Union, Callable, Tuple

import pygame

from src.gui.box_element import BoxElement, Margin
from src.gui.position import Position


class Button(BoxElement):
    """
    This class is representing any kind of button that could be seen on an interface.
    A button is receptive to user clicks and returns an id corresponding to a method,
    it may have specific arguments too.
    Mouse motion is also handled: the button appearance can change according to current focus.

    Keyword arguments:
    callback -- the reference to the function that should be call after a click
    size -- the size of the button following the format "(width, height)"
    position -- the position of the element on the screen
    sprite -- the pygame Surface corresponding to the sprite of the element
    sprite_hover -- the pygame Surface corresponding to the sprite of the element
    when it has the focus
    margin -- a tuple containing the margins of the box,
    should be in the form "(top_margin, right_margin, bottom_margin, left_margin)"
    linked_object -- the game entity linked to the button if there is one

    Attributes:
    callback -- the reference to the function that should be call after a click
    sprite -- the pygame Surface corresponding to the sprite of the element
    sprite_hover -- the pygame Surface corresponding to the sprite of the element
    when it has the focus
    linked_object -- the game entity linked to the button if there is one,
    would be returned on click
    """

    def __init__(
        self,
        callback: Union[Enum, Callable],
        size: Tuple[int, int],
        position: Position,
        sprite: pygame.Surface,
        sprite_hover: pygame.Surface,
        margin: Margin,
        linked_object: any = None,
    ) -> None:
        super().__init__(position, None, margin)
        self.callback: Union[Enum, Callable] = callback
        self.size: Tuple[int, int] = size
        self.sprite = sprite
        self.sprite_hover = sprite_hover
        self.content = self.sprite
        self.linked_object = linked_object

    def set_hover(self, is_mouse_hover: bool) -> None:
        """
        Change the current sprite between sprite or sprite_hover
        depending on whether the mouse is over the element or not.

        Keyword arguments:
        is_mouse_hover -- a boolean value indicating if the mouse is over the element or not
        """
        self.content = self.sprite_hover if is_mouse_hover else self.sprite

    def action_triggered(self) -> Callable:
        """
        Method that should be called after a click.

        Return the callback that should be executed.
        """
        return self.callback
