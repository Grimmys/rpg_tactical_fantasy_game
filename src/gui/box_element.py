"""
Defines BoxElement class, useful for drawing elements.
All other GUI elements inherit from this class.
"""

from typing import Union

import pygame

from src.gui.position import Position

Margin = tuple[int, int, int, int]


class BoxElement:
    """
    This element acts as a wrapper for a gui element.
    In fact, it adds a margin to any border of an element to have a cleaner interface.

    Keyword arguments:
    position -- the position of the box on the screen
    content -- a pygame surface that will be wrapped by the box
    margin -- a tuple containing the margins of the box,
    should be in the form "(top_margin, right_margin, bottom_margin, left_margin)"

    Attributes:
    position -- the position of the box on the screen
    content -- the element wrapped in the box
    size -- the size of the content following the format "(width, height)"
    margin -- a dict containing all the values for margins TOP, BOTTOM, LEFT and RIGHT
    """

    def __init__(
        self,
        position: Position,
        content: Union[pygame.Surface, None],
        margin: Margin = (0, 0, 0, 0),
    ) -> None:
        self.position: Position = position
        self.content: pygame.Surface = content
        self.size: tuple[int, int] = (0, 0)
        if self.content:
            self.size = (self.content.get_width(), self.content.get_height())
        self.margin: dict[str, int] = {
            "TOP": margin[0],
            "BOTTOM": margin[2],
            "LEFT": margin[3],
            "RIGHT": margin[1],
        }

    def get_width(self) -> int:
        """
        Return the width of the content more the left and right margins
        """
        return self.margin["LEFT"] + self.size[0] + self.margin["RIGHT"]

    def get_height(self) -> int:
        """
        Return the height of the content more the top and bottom margins
        """
        return self.margin["TOP"] + self.size[1] + self.margin["BOTTOM"]

    def get_margin_top(self) -> int:
        """
        Return top margin
        """
        return self.margin["TOP"]

    def get_margin_bottom(self) -> int:
        """
        Return bottom margin
        """
        return self.margin["BOTTOM"]

    def get_margin_left(self) -> int:
        """
        Return left margin
        """
        return self.margin["LEFT"]

    def get_margin_right(self) -> int:
        """
        Return right margin
        """
        return self.margin["RIGHT"]

    def get_rect(self) -> pygame.Rect:
        """
        Return a pygame rect containing the position of the element and its size
        """
        return pygame.Rect(
            self.position[0], self.position[1], self.size[0], self.size[1]
        )

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the content of the box, following the margins that should be added around it.

        Keyword arguments:
        screen -- the screen on which the content of the box should be drawn
        """
        screen.blit(
            self.content, (self.position[0] + self.margin["LEFT"], self.position[1])
        )
