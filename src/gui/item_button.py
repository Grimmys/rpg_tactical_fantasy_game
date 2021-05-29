"""
Defines ItemButton class, a special Button used to represent items on an interface.
"""

from typing import Callable

import pygame

from src.constants import BLACK, MIDNIGHT_BLUE
from src.game_entities.item import Item
from src.gui.button import Button
from src.gui.entries import Margin
from src.gui.fonts import fonts
from src.gui.position import Position

FRAME_SPRITE = 'imgs/interface/grey_frame.png'
FRAME_SPRITE_HOVER = 'imgs/interface/blue_frame.png'
ITEM_SPRITE = 'imgs/interface/item_frame.png'


class ItemButton(Button):
    """
    This class is representing a button for an Item visible on any kind of interface 
    (a player inventory, a shop etc.).
    A squared frame is reserved to the image of the button, and there is space at the right 
    to display the name of the item and other data.
    
    Keyword attributes:
    callback -- the reference to the function that should be call after a click
    size -- the size of the button following the format "(width, height)"
    position -- the position of the element on the screen
    item -- the concerned Item
    margin -- a tuple containing the margins of the box,
    should be in the form "(top_margin, right_margin, bottom_margin, left_margin)"
    price -- the price of the Item if it's for sale
    quantity -- the quantity of the Item if it's in a shop
    disabled -- a boolean value indicating whether the button can be triggered or not

    Attributes:
    item -- the concerned Item
    disabled -- a boolean value indicating whether the button can be triggered or not
    """
    def __init__(self, callback, size: tuple[int, int], position: Position, item: Item,
                 margin: Margin, price: int = 0, quantity: int = 0,
                 disabled: bool = False) -> None:
        name: str = ""
        if item:
            name = str(item)
        price_text: str = ""
        if price > 0:
            price_text = f"({price} gold)"
        quantity_text: str = ""
        if quantity > 0:
            quantity_text = f"({quantity} in stock)"

        padding: int = size[1] // 10
        frame_position: Position = (padding, padding)
        frame_size: tuple[int, int] = (size[1] - padding * 2, size[1] - padding * 2)
        frame: pygame.Surface = pygame.transform.scale(
            pygame.image.load(FRAME_SPRITE).convert_alpha(), frame_size)
        frame_hover: pygame.Surface = pygame.transform.scale(
            pygame.image.load(FRAME_SPRITE_HOVER).convert_alpha(), frame_size)

        item_frame: pygame.Surface = pygame.transform.scale(
            pygame.image.load(ITEM_SPRITE).convert_alpha(), size)
        item_frame.blit(frame, frame_position)
        if item:
            item_frame.blit(pygame.transform.scale(item.sprite,
                                                   (frame_size[0] - padding * 2,
                                                    frame_size[1] - padding * 2)),
                            (frame_position[0] + padding, frame_position[1] + padding))

        name_rendering: pygame.Surface = fonts['ITEM_FONT'].render(name, True, BLACK)
        nb_lines: int = 2
        if price_text:
            price_rendering = fonts['ITEM_FONT'].render(price_text, True, BLACK)
            item_frame.blit(price_rendering,
                            (frame.get_width() + padding * 2,
                             2 * item_frame.get_height() / 3 - fonts['ITEM_FONT'].get_height() / 2))
            nb_lines = 3
        if quantity_text:
            quantity_rendering = fonts['ITEM_FONT'].render(quantity_text, True, BLACK)
            item_frame.blit(quantity_rendering,
                            (item_frame.get_width() - padding * 2 - quantity_rendering.get_width(),
                             2 * item_frame.get_height() / 3 - fonts['ITEM_FONT'].get_height() / 2))
            nb_lines = 3
        item_frame.blit(name_rendering, (frame.get_width() + padding * 2,
                                         item_frame.get_height() / nb_lines
                                         - fonts['ITEM_FONT'].get_height() / 2))

        item_frame_hover: pygame.Surface = item_frame
        if item and not disabled:
            raw_item_frame_hover: pygame.Surface = pygame.image.load(ITEM_SPRITE).convert_alpha()
            item_frame_hover = pygame.transform.scale(raw_item_frame_hover, size)
            item_frame_hover.blit(frame_hover, frame_position)
            item_frame_hover.blit(pygame.transform.scale(item.sprite,
                                                         (frame_size[0] - padding * 2,
                                                          frame_size[1] - padding * 2)),
                                  (frame_position[0] + padding, frame_position[1] + padding))
            name_rendering_hover: pygame.Surface = fonts['ITEM_FONT_HOVER'].render(name,
                                                                                   True,
                                                                                   MIDNIGHT_BLUE)
            nb_lines = 3 if price_text or quantity_text else 2
            if price_text:
                price_rendering_hover = fonts['ITEM_FONT_HOVER'].render(price_text, True,
                                                                        MIDNIGHT_BLUE)
                item_frame_hover.blit(price_rendering_hover,
                                      (frame.get_width() + padding * 2,
                                       2 * item_frame.get_height() / 3
                                       - fonts['ITEM_FONT_HOVER'].get_height() / 2))
            if quantity_text:
                quantity_rendering = fonts['ITEM_FONT_HOVER'].render(quantity_text, True,
                                                                     MIDNIGHT_BLUE)
                item_frame_hover.blit(quantity_rendering,
                                      (item_frame.get_width() - padding * 2
                                       - quantity_rendering.get_width(),
                                       2 * item_frame.get_height() / 3 - fonts[
                                           'ITEM_FONT_HOVER'].get_height() / 2))
            item_frame_hover.blit(name_rendering_hover,
                                  (frame.get_width() + padding * 2,
                                   item_frame.get_height() / nb_lines -
                                   fonts['ITEM_FONT_HOVER'].get_height() / 2))

        super().__init__(callback, size, position, item_frame, item_frame_hover, margin,
                         linked_object=item)
        self.item: Item = item
        self.disabled: bool = disabled

    def action_triggered(self) -> Callable:
        """
        Method that should be called after a click.

        Behavior similar to the implementation for Button, except that it will rejects the action
        request if there is no reference to an Item or if the button is disabled.
        """
        if not self.item or self.disabled:
            return lambda: None
        return super().action_triggered()
