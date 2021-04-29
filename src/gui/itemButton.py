from src.constants import *
from src.gui.fonts import *
from src.gui.button import Button

FRAME_SPRITE = 'imgs/interface/grey_frame.bmp'
FRAME_SPRITE_HOVER = 'imgs/interface/blue_frame.bmp'
ITEM_SPRITE = 'imgs/interface/item_frame.bmp'


class ItemButton(Button):
    def __init__(self, method_id, args, size, pos, item, margin, index, price=0, quantity=0, disabled=False):
        name = ""
        if item:
            name = str(item)
        price_text = ""
        if price > 0:
            price_text = "(" + str(price) + " gold)"
        quantity_text = ""
        if quantity > 0:
            quantity_text = "(" + str(quantity) + " in stock)"

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
            item_frame.blit(pg.transform.scale(item.sprite, (frame_size[0] - padding * 2, frame_size[1] - padding * 2)),
                            (frame_pos[0] + padding, frame_pos[1] + padding))

        name_rendering = fonts['ITEM_FONT'].render(name, 1, BLACK)
        nb_lines = 2
        if price_text:
            price_rendering = fonts['ITEM_FONT'].render(price_text, 1, BLACK)
            item_frame.blit(price_rendering, (frame.get_width() + padding * 2,
                                              2 * item_frame.get_height() / 3 - fonts['ITEM_FONT'].get_height() / 2))
            nb_lines = 3
        if quantity_text:
            quantity_rendering = fonts['ITEM_FONT'].render(quantity_text, 1, BLACK)
            item_frame.blit(quantity_rendering, (item_frame.get_width() - padding * 2 - quantity_rendering.get_width(),
                                                 2 * item_frame.get_height() / 3 - fonts['ITEM_FONT'].get_height() / 2))
            nb_lines = 3
        item_frame.blit(name_rendering, (frame.get_width() + padding * 2,
                                         item_frame.get_height() / nb_lines - fonts['ITEM_FONT'].get_height() / 2))

        item_frame_hover = item_frame
        if item and not disabled:
            item_frame_hover = pg.transform.scale(pg.image.load(ITEM_SPRITE).convert_alpha(), size)
            item_frame_hover.blit(frame_hover, frame_pos)
            item_frame_hover.blit(pg.transform.scale(item.sprite, (frame_size[0] - padding * 2,
                                                                   frame_size[1] - padding * 2)),
                                  (frame_pos[0] + padding, frame_pos[1] + padding))
            name_rendering_hover = fonts['ITEM_FONT_HOVER'].render(name, 1, MIDNIGHT_BLUE)
            nb_lines = 3 if price_text or quantity_text else 2
            if price_text:
                price_rendering_hover = fonts['ITEM_FONT_HOVER'].render(price_text, 1, MIDNIGHT_BLUE)
                item_frame_hover.blit(price_rendering_hover, (frame.get_width() + padding * 2,
                                                              2 * item_frame.get_height() / 3
                                                              - fonts['ITEM_FONT_HOVER'].get_height() / 2))
            if quantity_text:
                quantity_rendering = fonts['ITEM_FONT_HOVER'].render(quantity_text, 1, MIDNIGHT_BLUE)
                item_frame_hover.blit(quantity_rendering, (item_frame.get_width() - padding * 2
                                                           - quantity_rendering.get_width(),
                                                           2 * item_frame.get_height() / 3 - fonts[
                                                           'ITEM_FONT_HOVER'].get_height() / 2))
            item_frame_hover.blit(name_rendering_hover, (frame.get_width() + padding * 2,
                                                         item_frame.get_height() / nb_lines -
                                                         fonts['ITEM_FONT_HOVER'].get_height() / 2))

        Button.__init__(self, method_id, args, size, pos, item_frame, item_frame_hover, margin)
        self.item = item
        self.index = index
        self.disabled = disabled

    def action_triggered(self):
        if not self.item or self.disabled:
            return False
        return self.method_id, (self.pos, self.item, self.args)
