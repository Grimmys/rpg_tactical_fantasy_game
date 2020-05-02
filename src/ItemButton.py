from src.constants import *
from src.fonts import *
from src.Button import Button

FRAME_SPRITE = 'imgs/interface/grey_frame.png'
FRAME_SPRITE_HOVER = 'imgs/interface/blue_frame.png'
ITEM_SPRITE = 'imgs/interface/item_frame.png'


class ItemButton(Button):
    def __init__(self, method_id, args, size, pos, item, margin, index, price, disabled=False):
        name = ""
        if item:
            name = item.get_formatted_name()
        price_text = ""
        if price > 0:
            price_text = "(" + str(price) + " gold)"

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
        if price_text:
            price_rendering = fonts['ITEM_FONT'].render(price_text, 1, BLACK)
            item_frame.blit(name_rendering, (frame.get_width() + padding * 2,
                                             item_frame.get_height() / 3 - fonts['ITEM_FONT'].get_height() / 2))
            item_frame.blit(price_rendering, (frame.get_width() + padding * 2,
                                              2 * item_frame.get_height() / 3 - fonts['ITEM_FONT'].get_height() / 2))
        else:
            item_frame.blit(name_rendering, (frame.get_width() + padding * 2,
                                             item_frame.get_height() / 2 - fonts['ITEM_FONT'].get_height() / 2))

        item_frame_hover = item_frame
        if item and not disabled:
            item_frame_hover = pg.transform.scale(pg.image.load(ITEM_SPRITE).convert_alpha(), size)
            item_frame_hover.blit(frame_hover, frame_pos)
            item_frame_hover.blit(pg.transform.scale(item.sprite, (frame_size[0] - padding * 2,
                                                                   frame_size[1] - padding * 2)),
                                  (frame_pos[0] + padding, frame_pos[1] + padding))
            name_rendering_hover = fonts['ITEM_FONT_HOVER'].render(name, 1, MIDNIGHT_BLUE)
            if price_text:
                price_rendering_hover = fonts['ITEM_FONT_HOVER'].render(price_text, 1, MIDNIGHT_BLUE)
                item_frame_hover.blit(name_rendering_hover, (frame.get_width() + padding * 2,
                                                             item_frame.get_height() / 3
                                                             - fonts['ITEM_FONT_HOVER'].get_height() / 2))
                item_frame_hover.blit(price_rendering_hover, (frame.get_width() + padding * 2,
                                                              2 * item_frame.get_height() / 3
                                                              - fonts['ITEM_FONT_HOVER'].get_height() / 2))
            else:
                item_frame_hover.blit(name_rendering_hover, (frame.get_width() + padding * 2,
                                                             item_frame.get_height() / 2
                                                             - fonts['ITEM_FONT_HOVER'].get_height() / 2))

        args.append(price)
        Button.__init__(self, method_id, args, size, pos, item_frame, item_frame_hover, margin)
        self.item = item
        self.index = index
        self.disabled = disabled

    def action_triggered(self):
        if not self.item or self.disabled:
            return False
        return self.method_id, (self.pos, self.item, self.args)
