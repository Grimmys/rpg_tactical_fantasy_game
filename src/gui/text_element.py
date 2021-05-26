"""
Defines TextElement class, a BoxElement permitting to easily draw text and let it
be centered on an interface.
"""

import pygame
from pygame.constants import SRCALPHA

from src.constants import WHITE
from src.gui.box_element import BoxElement
from src.gui.entries import Margin
from src.gui.position import Position


class TextElement(BoxElement):
    """
    This class is representing a paragraph of text, displayed on a interface and horizontally
    centered according to its position.

    Keyword arguments:
    text -- the text that should be rendered
    container_width -- the width o the interface that will contained the text
    position -- the position of the text in the interface
    font -- the font that should be used to render the text
    margin -- a tuple containing the margins of the box,
    should be in the form "(top_margin, right_margin, bottom_margin, left_margin)"
    text_color -- the color of the rendered text
    """

    def __init__(self, text: str, container_width: int, position: Position, font: pygame.font.Font,
                 margin: Margin, text_color: pygame.Color = WHITE) -> None:
        initial_text: pygame.Surface = font.render(text, True, text_color)
        final_text: pygame.Surface = TextElement.verify_rendered_text_size(initial_text, text,
                                                                           container_width, font,
                                                                           text_color)

        BoxElement.__init__(self, position, final_text, margin)

    @staticmethod
    def verify_rendered_text_size(rendered_text: pygame.Surface, text: str,
                                  container_width: int, font: pygame.font.Font,
                                  text_color: pygame.Color) -> pygame.Surface:
        """
        Split a given text in multiple lines until it could fit properly in its container

        Return the final rendered text

        Keyword arguments:
        rendered_text -- the current rendering of the text, to check if it fits in the container
        text -- the text that would be split if necessary
        container_width -- the width of the container
        font -- the font that should be used to render the text
        text_color -- the color that should be used to render the text
        """
        final_render = rendered_text

        if final_render.get_width() + 20 > container_width:
            first_part, second_part = TextElement.divide_text(text)
            first_part_render = font.render(first_part, 1, text_color)
            first_part_render = TextElement.verify_rendered_text_size(first_part_render, first_part,
                                                                      container_width, font,
                                                                      text_color)
            second_part_render = font.render(second_part, 1, text_color)
            second_part_render = TextElement.verify_rendered_text_size(second_part_render,
                                                                       second_part, container_width,
                                                                       font, text_color)
            final_render = pygame.Surface((container_width, first_part_render.get_height() +
                                           second_part_render.get_height()), SRCALPHA)
            first_part_x = final_render.get_width() // 2 - first_part_render.get_width() // 2
            final_render.blit(first_part_render, (first_part_x, 0))
            second_part_x = final_render.get_width() // 2 - second_part_render.get_width() // 2
            final_render.blit(second_part_render, (second_part_x, first_part_render.get_height()))
        return final_render

    @staticmethod
    def divide_text(text: str) -> tuple[str, str]:
        """
        Divide a text in two parts of a similar size, avoiding to cut a word in two.

        Return the split text in two different strings.

        Keyword argument:
        text -- the text that should be divided
        """
        separation_index: int = TextElement.get_middle_text(text)
        return text[:separation_index], text[separation_index:]

    @staticmethod
    def get_middle_text(text: str) -> int:
        """
        Returns the index of the first whitespace character that is after the middle of the provided
        string.
        If there is no whitespace character after the middle of the string, -1 is returned.

        Keyword attributes:
        text -- the string that should be used to make the computation
        """
        absolute_middle = len(text) // 2
        for i in range(absolute_middle, len(text)):
            if text[i] == ' ':
                return i
        return -1
