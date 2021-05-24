"""
Defines DynamicButton class, a special Button iterating through a list of values
on each click.
"""

from src.constants import WHITE
from src.gui.fonts import fonts
from src.gui.button import Button


class DynamicButton(Button):
    """
    This class is representing a special button with an inner value changing after each click.
    A DynamicButton has a sequence of values given at initialization, and a initial value.
    The sequence will be iterated to determine the next inner value after a click.
    This fluctuating value is the one that will be send has the first argument of
    the method called on click, and a different label will be displayed on the button for
    each different value of the sequence.

    Keyword arguments:
    method_id -- the id permitting to know the function that should be called on click
    args -- a data structure containing any argument that can be useful to send to
    the function called on click
    size -- the size of the button following the format "(width, height)"
    position -- the position of the element on the screen
    sprite -- the pygame Surface corresponding to the sprite of the element
    sprite_hover -- the pygame Surface corresponding to the sprite of the element
    when it has the focus
    margin -- a tuple containing the margins of the box,
    should be in the form "(top_margin, right_margin, bottom_margin, left_margin)"
    values -- the sequence of values that will be iterated to determine the next inner value
    current_value -- the initial value of the button
    base_title -- the initial label associated to the initial value
    base_sprite --
    base_sprite_hover --
    linked_object --

    Attributes:
    values -- the sequence of values that will be iterated to determine the next inner value
    current_value -- the initial value of the button
    base_title -- the initial label associated to the initial value
    base_sprite --
    base_sprite_hover --
    """

    def __init__(self, method_id, args, size, position, sprite, sprite_hover, margin, values,
                 current_value, base_title, base_sprite, base_sprite_hover, linked_object=None):
        super().__init__(method_id, args, size, position, sprite, sprite_hover,
                         margin, linked_object)
        self.values = values
        self.current_value_ind = current_value
        self.base_title = base_title
        self.base_sprite = base_sprite
        self.base_sprite_hover = base_sprite_hover
        self.args.append(self.values[self.current_value_ind]['value'])

    def __update_sprite(self):
        """

        """
        name = fonts['ITEM_FONT'].render(self.base_title + ' ' +
                                         self.values[self.current_value_ind]['label'], 1, WHITE)

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
        """

        :return:
        """
        # Search for next value
        self.current_value_ind += 1
        if self.current_value_ind == len(self.values):
            self.current_value_ind = 0
        self.__update_sprite()
        self.args[0] = self.values[self.current_value_ind]['value']
        return self.method_id, (self.position, self.linked_object, self.args)
