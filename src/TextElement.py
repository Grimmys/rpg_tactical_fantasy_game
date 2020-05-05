import pygame as pg
from pygame.locals import *

from src.constants import WHITE
from src.BoxElement import BoxElement


class TextElement(BoxElement):
    def __init__(self, text, container_width, pos, font, margin, text_color=WHITE):
        init_text = font.render(text, 1, text_color)
        final_text = TextElement.verify_rendered_text_size(init_text, text, container_width, font, text_color)

        BoxElement.__init__(self, pos, final_text, margin)

    @staticmethod
    def verify_rendered_text_size(rendered_txt, txt, container_width, font, text_color):
        final_render = rendered_txt

        if final_render.get_width() > container_width:
            first_part, second_part = TextElement.divide_text(txt)
            first_part_render = font.render(first_part, 1, text_color)
            first_part_render = TextElement.verify_rendered_text_size(first_part_render, first_part,
                                                                      container_width, font, text_color)
            second_part_render = font.render(second_part, 1, text_color)
            second_part_render = TextElement.verify_rendered_text_size(second_part_render, second_part,
                                                                       container_width, font, text_color)
            final_render = pg.Surface((first_part_render.get_width(), first_part_render.get_height() +
                                       second_part_render.get_height()), SRCALPHA)
            final_render.blit(first_part_render, (0, 0))
            second_part_x = final_render.get_width() // 2 - second_part_render.get_width() // 2
            final_render.blit(second_part_render, (second_part_x, first_part_render.get_height()))
        return final_render

    @staticmethod
    def divide_text(txt):
        sep_i = TextElement.get_middle_text(txt)
        return txt[:sep_i], txt[sep_i:]

    @staticmethod
    def get_middle_text(txt):
        absolute_middle = len(txt) // 2
        for i in range(absolute_middle, len(txt)):
            if txt[i] == ' ':
                return i
