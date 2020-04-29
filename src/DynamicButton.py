from src.fonts import fonts
from src.constants import *
from src.Button import Button


class DynamicButton(Button):
    def __init__(self, method_id, args, size, pos, sprite, sprite_hover, margin, values, current_value,
                 base_title, base_sprite, base_sprite_hover, linked_object=None):
        Button.__init__(self, method_id, args, size, pos, sprite, sprite_hover, margin, linked_object)
        self.values = values
        self.current_value_ind = current_value
        self.base_title = base_title
        self.base_sprite = base_sprite
        self.base_sprite_hover = base_sprite_hover
        self.args.append(ANIMATION_SPEED)

    def update_sprite(self):
        name = fonts['ITEM_FONT'].render(self.base_title + ' ' + self.values[self.current_value_ind]['label'], 1, WHITE)

        tmp_sprite = self.base_sprite.copy()
        tmp_sprite.blit(name, (tmp_sprite.get_width() // 2 - name.get_width() // 2,
                               tmp_sprite.get_height() // 2 - name.get_height() // 2))
        self.sprite = tmp_sprite

        tmp_sprite_hover = self.base_sprite_hover.copy()
        tmp_sprite_hover.blit(name, (tmp_sprite_hover.get_width() // 2 - name.get_width() // 2,
                                     tmp_sprite_hover.get_height() // 2 - name.get_height() // 2))
        self.sprite_hover = tmp_sprite_hover

        # Force display update
        self.set_hover(True)

    def action_triggered(self):
        # Search for next value
        self.current_value_ind += 1
        if self.current_value_ind == len(self.values):
            self.current_value_ind = 0
        self.update_sprite()
        self.args[0] = self.values[self.current_value_ind]['value']
        return self.method_id, (self.pos, self.linked_object, self.args)

    def display(self, win):
        win.blit(self.content, self.pos)
