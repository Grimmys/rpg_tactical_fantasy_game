import pygame as pg

from src.Button import Button

ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 18)
ITEM_FONT_HOVER = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITALIC_ITEM_FONT = pg.font.Font('fonts/minya_nouvelle_it.ttf', 16)
ITALIC_ITEM_FONT_HOVER = pg.font.Font('fonts/minya_nouvelle_it.ttf', 16)

MIDNIGHT_BLUE = (75, 75, 212)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

TILE_SIZE = 48
FRAME_SPRITE = 'imgs/interface/grey_frame.png'
FRAME = pg.transform.scale(pg.image.load(FRAME_SPRITE).convert_alpha(), (TILE_SIZE + 10, TILE_SIZE + 10))
FRAME_SPRITE_HOVER = 'imgs/interface/blue_frame.png'
FRAME_HOVER = pg.transform.scale(pg.image.load(FRAME_SPRITE_HOVER).convert_alpha(), (TILE_SIZE + 10, TILE_SIZE + 10))
ITEM_SPRITE = 'imgs/interface/item_frame.png'


class ItemButton(Button):
    def __init__(self, size, pos, item, margin, index):
        name = ""
        if item:
            name = item.get_formatted_name()

        self.frame_pos = (10, 10)
        item_frame = pg.transform.scale(pg.image.load(ITEM_SPRITE).convert_alpha(), size)
        item_frame.blit(FRAME, self.frame_pos)
        if item:
            item_frame.blit(item.get_sprite(), (self.frame_pos[0] + 5, self.frame_pos[1] + 5))
        item_sprite = ITALIC_ITEM_FONT.render(name, 1, BLACK)
        item_frame.blit(item_sprite, (FRAME.get_width() + 15, item_frame.get_height() / 2 - ITALIC_ITEM_FONT.get_height() / 2))

        item_frame_hover = item_frame
        if item:
            item_frame_hover = pg.transform.scale(pg.image.load(ITEM_SPRITE).convert_alpha(), size)
            item_frame_hover.blit(FRAME_HOVER, self.frame_pos)
            item_frame_hover.blit(item.get_sprite(), (self.frame_pos[0] + 5, self.frame_pos[1] + 5))
            item_sprite_hover = ITALIC_ITEM_FONT_HOVER.render(name, 1, MIDNIGHT_BLUE)
            item_frame_hover.blit(item_sprite_hover, (FRAME.get_width() + 15, item_frame.get_height() / 2 - ITALIC_ITEM_FONT.get_height() / 2))

        Button.__init__(self, name, 5, size, pos, item_frame, item_frame_hover, margin, False)
        self.item = item
        self.index = index

    def display(self, win):
        win.blit(self.content, self.pos)

    def action_triggered(self):
        if not self.item:
            return False
        return self.method_id, (self.pos, self.index)
