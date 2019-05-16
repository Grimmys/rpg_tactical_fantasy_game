import pygame as pg

from src.BoxElement import BoxElement

ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Button(BoxElement):
    def __init__(self, name, method_id, size, pos, sprite, sprite_hover, margin, sprite_is_img=True):
        BoxElement.__init__(self, pos, None, margin)

        self.size = size
        self.name = ITEM_FONT.render(name, 1, WHITE)
        self.method_id = method_id
        self.sprite = sprite
        self.sprite_hover = sprite_hover
        if sprite_is_img:
            self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), self.size)
            self.sprite_hover = pg.transform.scale(pg.image.load(sprite_hover).convert_alpha(), self.size)
        self.content = self.sprite

    def display(self, win):
        BoxElement.display(self, win)
        win.blit(self.name, (self.pos[0] + (self.size[0] // 2) - (self.name.get_width() // 2), self.pos[1] + (self.size[1] // 2) - (self.name.get_height() // 2)))

    def set_hover(self, hover):
        if hover:
            self.content = self.sprite_hover
        else:
            self.content = self.sprite

    def action_triggered(self):
        return self.method_id, self.pos