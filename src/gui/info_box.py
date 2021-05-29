"""
Defines InfoBox class, an helper to draw any kind of pop-up (menu or informative message).
"""

from enum import Enum
from typing import Union, Sequence, List, Type, Callable

import pygame

from src.constants import WHITE, BUTTON_SIZE, ITEM_BUTTON_SIZE, TRADE_ITEM_BUTTON_SIZE, \
    MARGIN_BOX, MARGIN_TOP, CLOSE_BUTTON_SIZE, MAX_MAP_HEIGHT, MAX_MAP_WIDTH
from src.gui.box_element import BoxElement
from src.gui.entries import Entries
from src.gui.fonts import fonts
from src.gui.text_element import TextElement
from src.gui.button import Button
from src.gui.dynamic_button import DynamicButton
from src.gui.item_button import ItemButton
from src.services.menus import GenericActions

BUTTON_INACTIVE = "imgs/interface/MenuButtonInactiv.png"
BUTTON_ACTIVE = "imgs/interface/MenuButtonPreLight.png"

CLOSE_BUTTON_MARGIN_TOP = 20

DEFAULT_WIDTH = 400


class InfoBox:
    """
    This class is defining any kind of pop-up that can be found in the game.
    It can be used to represent the interface of a menu, or a simple text message.
    Some elements can be buttons, that will react to user clicks (see the button module
    for more information).


    Keyword arguments:
    name -- the title of the infoBox
    id_type -- the reference to the menu which the infoBox is linked if there is one
    sprite -- a relative path to the image that will be the sprite of the infoBox
    entries -- a data structure describing the information wrapped in the infoBox
    width -- the width of the infoBox, DEFAULT_WIDTH will be assigned if none is given
    element_linked -- the pygame Rect of the element linked to this infoBox if any
    The infoBox will be displayed beside the element if provided
    close_button -- the callback to run when pressing the close button if there should be one
    separator -- a boolean indicating if there should be a line splitting the infoBox
    at middle width or not
    title_color -- the color of the title

    Attributes:
    name -- the title of the infoBox
    type -- the reference to the menu which the infoBox is linked if there is one
    element_linked -- the pygame Rect of the element linked to this infoBox if there is one
    close_button -- the callback to run when pressing the close button if there should be one
    title_color -- the color of the title
    separator -- the structure containing the following information about the splitting line:
    if it should be drawn, its vertical position, and its height
    entries -- the data structure describing the information wrapped in the infoBox
    elements -- the 2D structure containing all the visual elements of the infoBox
    size -- the size of the infoBox following the format (width, height)
    position -- the position of the infoBox. Will be beside the linked element if present,
    or only computed at display time otherwise
    buttons -- the sequence of buttons of the infoBox, including the close button if present
    sprite -- the pygame Surface corresponding to the sprite of the infoBox
    """

    def __init__(self, name: str, sprite: str, entries: Entries, id_type: Type[Enum] = None,
                 width: int = DEFAULT_WIDTH, element_linked: pygame.Rect = None,
                 close_button: Callable = None, separator: bool = False,
                 title_color: pygame.Color = WHITE) -> None:
        self.name: str = name
        self.type: Type[Enum] = id_type
        self.element_linked: pygame.Rect = element_linked
        self.close_button: Callable = close_button
        self.title_color: pygame.Color = title_color
        self.separator: dict[str, Union[bool, int]] = {'display': separator,
                                                       'posY': 0,
                                                       'height': 0}
        self.entries: Entries = entries
        self.elements: List[List[Union[BoxElement, int]]] = self.init_elements(self.entries, width)
        height: int = self.determine_height(close_button)
        self.size: tuple[int, int] = (width, height)
        self.position: Union[tuple[int, int], tuple] = self.determine_position()
        self.separator['height'] += self.size[1]
        if self.position:
            self.determine_elements_position()
        self.buttons: Sequence[Button] = self.find_buttons()
        self.sprite: pygame.Surface = pygame.transform.scale(
            pygame.image.load(sprite).convert_alpha(), self.size)

    def init_elements(self, entries: Entries, width: int) -> List[List[BoxElement]]:
        """
        Initialize the graphical elements associated to the formal data that the infoBox should
        represent.

        Return the elements in a 2D structure to know the relative position of each element.
        Keyword arguments:
        entries -- the data structure describing the information wrapped in the infoBox
        width -- the width of the infoBox
        """
        elements: List[List[BoxElement]] = []
        for row in entries:
            element: List[BoxElement] = []
            for entry in row:
                if 'margin' not in entry:
                    entry['margin'] = (0, 0, 0, 0)

                if 'type' not in entry:
                    # It is an empty element
                    element.append(BoxElement((0, 0), pygame.Surface((0, 0)), entry['margin']))
                elif entry['type'] == 'button':
                    if 'size' not in entry:
                        size = BUTTON_SIZE
                    else:
                        size = entry['size']
                    if 'font' not in entry:
                        font = fonts['BUTTON_FONT']
                    else:
                        font = entry['font']
                    name = font.render(entry['name'], True, WHITE)
                    sprite = pygame.transform.scale(
                        pygame.image.load(BUTTON_INACTIVE).convert_alpha(), size)
                    sprite.blit(name, (sprite.get_width() // 2 - name.get_width() // 2,
                                       sprite.get_height() // 2 - name.get_height() // 2))
                    sprite_hover = pygame.transform.scale(
                        pygame.image.load(BUTTON_ACTIVE).convert_alpha(), size)
                    sprite_hover.blit(name, (sprite_hover.get_width() // 2 - name.get_width() // 2,
                                             sprite_hover.get_height() // 2 - name.get_height() // 2
                                             ))
                    element.append(
                        Button(entry['callback'], size, (0, 0), sprite, sprite_hover,
                               entry['margin']))
                elif entry['type'] == 'parameter_button':
                    name = fonts['ITEM_FONT'].render(entry['name'] + ' ' +
                                                     entry['values'][entry['current_value_ind']][
                                                         'label'],
                                                     True, WHITE)
                    raw_inactive_button = pygame.image.load(BUTTON_INACTIVE).convert_alpha()
                    base_sprite = pygame.transform.scale(raw_inactive_button, BUTTON_SIZE)
                    sprite = base_sprite.copy()
                    sprite.blit(name, (base_sprite.get_width() // 2 - name.get_width() // 2,
                                       base_sprite.get_height() // 2 - name.get_height() // 2))
                    raw_active_button = pygame.image.load(BUTTON_ACTIVE).convert_alpha()
                    base_sprite_hover = pygame.transform.scale(raw_active_button, BUTTON_SIZE)
                    sprite_hover = base_sprite_hover.copy()
                    sprite_hover.blit(name,
                                      (base_sprite_hover.get_width() // 2
                                       - name.get_width() // 2,
                                       base_sprite_hover.get_height() // 2
                                       - name.get_height() // 2))
                    element.append(DynamicButton(entry['callback'], BUTTON_SIZE, (0, 0),
                                                 base_sprite, base_sprite_hover, entry['margin'],
                                                 entry['values'], entry['current_value_ind'],
                                                 entry['name']))
                elif entry['type'] == 'text_button':
                    name = fonts['ITEM_FONT'].render(entry['name'], True, entry['color'])
                    name_hover = fonts['ITEM_FONT'].render(entry['name'], True,
                                                           entry['color_hover'])
                    if 'obj' not in entry:
                        entry['obj'] = None
                    element.append(Button(entry['id'], name.get_size(), (0, 0), name,
                                          name_hover, entry['margin'], entry['obj']))

                elif entry['type'] == 'item_button':
                    button_size = entry['size'] if 'size' in entry else ITEM_BUTTON_SIZE

                    disabled = 'disabled' in entry
                    if 'subtype' in entry:
                        if entry['subtype'] == 'trade':
                            button_size = TRADE_ITEM_BUTTON_SIZE
                    if 'price' not in entry:
                        entry['price'] = 0
                    if 'quantity' not in entry:
                        entry['quantity'] = 0
                    element.append(ItemButton(entry['id'], button_size,
                                              (0, 0), entry['item'], entry['margin'],
                                              entry['price'], entry['quantity'], disabled))
                elif entry['type'] == 'text':
                    if 'font' not in entry:
                        entry['font'] = fonts['ITEM_FONT']
                    if 'color' not in entry:
                        entry['color'] = WHITE
                    element.append(TextElement(entry['text'], width, (0, 0), entry['font'],
                                               entry['margin'], entry['color']))
            elements.append(element)
        title = TextElement(self.name, width, (0, 0), fonts['MENU_TITLE_FONT'],
                            (len(entries), 0, 20, 0), self.title_color)
        self.separator['posY'] += title.get_height()
        elements.insert(0, [title])
        return elements

    def determine_height(self, close_button: Callable) -> int:
        """
        Compute the total height of the infoBox, defined according
        to the height of each element in it and the separator if present.
        Return the computed height.

        Keyword arguments:
        close_button -- the callback to run when pressing the close button if there should be one
        """
        # Margin to be add at begin and at end
        height: int = MARGIN_BOX * 2
        self.separator['height'] -= height
        self.separator['posY'] += height
        for row in self.elements:
            max_height: int = 0
            for element in row:
                el_height = element.get_height() + MARGIN_TOP
                if el_height > max_height:
                    max_height = el_height
            height += max_height
            row.insert(0, max_height)
        if close_button:
            close_button_height: int = CLOSE_BUTTON_SIZE[1] + MARGIN_TOP + CLOSE_BUTTON_MARGIN_TOP
            height += close_button_height
            self.separator['height'] -= close_button_height

            # Button sprites
            name = fonts['ITEM_FONT'].render("Close", True, WHITE)
            raw_inactive_button = pygame.image.load(BUTTON_INACTIVE).convert_alpha()
            sprite = pygame.transform.scale(raw_inactive_button, CLOSE_BUTTON_SIZE)
            sprite.blit(name, (sprite.get_width() // 2 - name.get_width() // 2,
                               sprite.get_height() // 2 - name.get_height() // 2))
            raw_active_button = pygame.image.load(BUTTON_ACTIVE).convert_alpha()
            sprite_hover = pygame.transform.scale(raw_active_button, CLOSE_BUTTON_SIZE)
            sprite_hover.blit(name, (sprite_hover.get_width() // 2 - name.get_width() // 2,
                                     sprite_hover.get_height() // 2 - name.get_height() // 2))

            self.elements.append([close_button_height,
                                  Button(close_button,
                                         CLOSE_BUTTON_SIZE, (0, 0), sprite,
                                         sprite_hover, (CLOSE_BUTTON_MARGIN_TOP, 0, 0, 0))])
        return height

    def determine_position(self) -> Union[tuple[int, int], tuple]:
        """
        Compute the position of the infoBox to be beside the linked element.
        If no element is linked to the infoBox, the position will be determine at display time
        according to the screen.
        Return the computed position.
        """
        if self.element_linked:
            position: list[int, int] = [self.element_linked.x + self.element_linked.width,
                                        self.element_linked.y + self.element_linked.height -
                                        self.size[1] // 2]
            if position[1] < 0:
                position[1] = 0
            elif position[1] + self.size[1] > MAX_MAP_HEIGHT:
                position[1] = MAX_MAP_HEIGHT - self.size[1]
            if position[0] + self.size[0] > MAX_MAP_WIDTH:
                position[0] = self.element_linked.x - self.size[0]
            return position[0], position[1]
        return ()

    def find_buttons(self) -> Sequence[Button]:
        """
        Search in all elements for buttons.
        Return the sequence of buttons.
        """
        buttons: List[Button] = []
        for row in self.elements:
            for element in row[1:]:
                if isinstance(element, Button):
                    buttons.append(element)
        return buttons

    def determine_elements_position(self):
        """
        Compute the position of each element and update it if needed.
        """
        y_coordinate = self.position[1] + MARGIN_BOX
        # Memorize mouse position in case it is over a button
        mouse_pos = pygame.mouse.get_pos()
        # A row begins by a value identifying its height, followed by its elements
        for row in self.elements:
            nb_elements = len(row) - 1
            i = 1
            for element in row[1:]:
                base_x = self.position[0] + (self.size[0] // (2 * nb_elements)) * i
                x_coordinate = base_x - element.get_width() // 2
                element.position = (x_coordinate, y_coordinate + element.get_margin_top())
                if isinstance(element, Button):
                    element.set_hover(element.get_rect().collidepoint(mouse_pos))
                i += 2
            y_coordinate += row[0]

    def update_content(self, entries: Entries) -> None:
        """
        Change the data contains in the infoBox by the one provided.

        Keyword arguments:
        entries -- the new data structure describing the updated data
        """
        self.elements = self.init_elements(entries, self.size[0])
        self.size = (self.size[0], self.determine_height(self.close_button))
        self.sprite = pygame.transform.scale(self.sprite, self.size)
        self.position = []
        self.buttons = self.find_buttons()

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the infoBox and all its elements.

        Keyword arguments:
        screen -- the screen on which the displaying should be done
        """
        if self.position:
            screen.blit(self.sprite, self.position)
        else:
            win_size = screen.get_size()
            self.position = [win_size[0] // 2 - self.size[0] // 2,
                             win_size[1] // 2 - self.size[1] // 2]
            screen.blit(self.sprite, self.position)
            self.determine_elements_position()

        for row in self.elements:
            for element in row[1:]:
                element.display(screen)

        if self.separator['display']:
            pygame.draw.line(screen, WHITE,
                             (self.position[0] + self.size[0] / 2,
                              self.position[1] + self.separator['posY']),
                             (self.position[0] + self.size[0] / 2,
                              self.position[1] + self.separator['height']), 2)

    def motion(self, position: tuple[int, int]) -> None:
        """
        Handle the triggering of a motion event.
        Test if the mouse entered in a button or quited one.

        Keyword arguments:
        position -- the position of the mouse
        """
        for button in self.buttons:
            button.set_hover(button.get_rect().collidepoint(position))

    def click(self, position: tuple[int, int]) -> Callable:
        """
        Handle the triggering of a click event.
        Return the data corresponding of the action that should be done if the click was done
        on a button, else False.

        Keyword arguments:
        position -- the position of the mouse
        """
        for button in self.buttons:
            if button.get_rect().collidepoint(position):
                return button.action_triggered()
        # Return a " do nothing " callable when clicking on empty space
        return lambda: None
