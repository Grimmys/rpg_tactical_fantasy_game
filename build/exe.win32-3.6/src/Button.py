import pygame as pg

from src.BoxElement import BoxElement

ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Button(BoxElement):
    def __init__(self, method_id, size, pos, sprite, sprite_hover, margin, linked_object=None):
        BoxElement.__init__(self, pos, None, margin)

        self.size = size
        self.method_id = method_id
        self.sprite = sprite
        self.sprite_hover = sprite_hover
        self.content = self.sprite
        self.linked_object = linked_object

    def set_hover(self, hover):
        self.content = self.sprite_hover if hover else self.sprite

    def action_triggered(self):
        return self.method_id, (self.pos, self.linked_object)
