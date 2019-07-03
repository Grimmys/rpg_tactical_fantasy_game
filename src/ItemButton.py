import pygame as pg

from src.Button import Button
from src.constants import *

ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 18)
ITEM_FONT_HOVER = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITALIC_ITEM_FONT = pg.font.Font('fonts/minya_nouvelle_it.ttf', 16)
ITALIC_ITEM_FONT_HOVER = pg.font.Font('fonts/minya_nouvelle_it.ttf', 16)

FRAME_SPRITE = 'imgs/interface/grey_frame.png'
FRAME_SPRITE_HOVER = 'imgs/interface/blue_frame.png'
ITEM_SPRITE = 'imgs/interface/item_frame.png'

INTERAC_ITEM_ACTION_ID = 0


class ItemButton(Button):
    def __init__(self, size, pos, item, margin, index, disabled=False):
        name = ""
        if item:
            name = item.get_formatted_name()

        padding = size[1] // 10
        frame_pos = (padding, padding)
        frame_size = (size[1] - padding * 2, size[1] - padding * 2)
        frame = pg.transform.scale(pg.image.load(FRAME_SPRITE).convert_alpha(),
                                   frame_size)
        frame_hover = pg.transform.scale(pg.image.load(FRAME_SPRITE_HOVER).convert_alpha(),
                                         frame_size)

        item_frame = pg.transform.scale(pg.image.load(ITEM_SPRITE).convert_alpha(), size)
        item_frame.blit(frame, frame_pos)
        if item:
            item_frame.blit(pg.transform.scale(item.get_sprite(), (frame_size[0] - padding * 2, frame_size[1] - padding * 2)),
                            (frame_pos[0] + padding, frame_pos[1] + padding))
        item_sprite = ITALIC_ITEM_FONT.render(name, 1, BLACK)
        item_frame.blit(item_sprite, (frame.get_width() + padding * 2, item_frame.get_height() / 2 - ITALIC_ITEM_FONT.get_height() / 2))

        item_frame_hover = item_frame
        if item and not disabled:
            item_frame_hover = pg.transform.scale(pg.image.load(ITEM_SPRITE).convert_alpha(), size)
            item_frame_hover.blit(frame_hover, frame_pos)
            item_frame_hover.blit(pg.transform.scale(item.get_sprite(), (frame_size[0] - padding * 2, frame_size[1] - padding * 2)),
                                  (frame_pos[0] + padding, frame_pos[1] + padding))
            item_sprite_hover = ITALIC_ITEM_FONT_HOVER.render(name, 1, MIDNIGHT_BLUE)
            item_frame_hover.blit(item_sprite_hover, (frame.get_width() + padding * 2, item_frame.get_height() / 2 - ITALIC_ITEM_FONT.get_height() / 2))

        Button.__init__(self, INTERAC_ITEM_ACTION_ID, size, pos, item_frame, item_frame_hover, margin)
        self.item = item
        self.index = index
        self.disabled = disabled

    def action_triggered(self):
        if not self.item or self.disabled:
            return False
        return self.method_id, (self.pos, self.item)
