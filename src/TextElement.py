import pygame as pg

from src.BoxElement import BoxElement

ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class TextElement(BoxElement):
    def __init__(self, txt, pos, font, margin, color=WHITE):
        BoxElement.__init__(self, pos, font.render(txt, 1, color), margin)