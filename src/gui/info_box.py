"""
Defines InfoBox class, an helper to draw any kind of popup (menu or informative message).
"""

from __future__ import annotations

import os.path
from typing import Union, Sequence, Callable, Optional

import pygame

from pygamepopup.configuration import _default_sprites, _default_fonts
from pygamepopup.constants import (
    WHITE,
    CLOSE_BUTTON_MARGIN_TOP,
    MARGIN_BOX,
    DEFAULT_MARGIN_TOP,
    CLOSE_BUTTON_SIZE,
    MARGIN_LINKED_ELEMENT,
    DEFAULT_POPUP_WIDTH,
)
from pygamepopup.components.box_element import BoxElement
from pygamepopup.components.text_element import TextElement
from pygamepopup.components.button import Button
from pygamepopup.types import Position

from src.services.language import STR_CLOSE

class _Row:
    def __init__(self, elements: list[BoxElement], height: int = 0):
        self.elements = elements
        self.height = height


class InfoBox:
    """
    This class is defining any kind of popup that can be found in the app.

    It can be used to represent the interface of a menu, or a simple text message.
    Some elements can be buttons, that will react to user clicks (see the button component
    for more information).


    Keyword arguments:
        title (str): the title of the infoBox
        element_grid (list[list[BoxElement]]): a grid containing the components that should be rendered by the infoBox
        width (int): the width of the infoBox, defaults to DEFAULT_POPUP_WIDTH
        element_linked (pygame.Rect): the pygame Rect of the element linked to this infoBox,
            the infoBox will be displayed beside the element if provided
        has_close_button (bool): whether a close button should be added at the bottom or not, defaults to True
        title_color (pygame.Color): the color of the title
        background_path (str): the path corresponding to the image that should be the sprite of the infoBox
        close_button_background_path (str): the path to the image corresponding to the sprite of the close button
            if there should be one
        close_button_background_hover_path (str): the path to the image corresponding to the sprite of
            the close button when it is hovered if there should be one
        visible_on_background (bool): whether the popup is visible on background or not, defaults to True
        has_vertical_separator (bool): whether there should be a line splitting the infoBox in two at middle width or
            not, defaults to False
        identifier (str): a string permitting to identify the menu among others if needed

    Attributes:
        title (str): the title of the infoBox
        element_linked (pygame.Rect): the pygame Rect of the element linked to this infoBox if there is one
        has_close_button (bool): whether the infoBox has a close button or not
        title_color (pygame.Color): the color of the title
        element_grid (list[list[BoxElement]): the grid containing the components that should be rendered by the infoBox
        buttons (Sequence[Button]): the sequence of buttons of the infoBox, including the close button if present
        sprite (pygame.Surface): the pygame Surface corresponding to the sprite of the infoBox
        visible_on_background (bool): whether the popup is visible on background or not
        identifier (str): a string permitting to identify the menu among others if needed
    """

    def __init__(
        self,
        title: str,
        element_grid: list[list[BoxElement]],
        width: int = DEFAULT_POPUP_WIDTH,
        element_linked: pygame.Rect = None,
        position: Position = (0, 0),
        has_close_button: bool = True,
        title_color: pygame.Color = WHITE,
        background_path: str = None,
        close_button_background_path: str = None,
        close_button_background_hover_path: str = None,
        visible_on_background: bool = True,
        has_vertical_separator: bool = False,
        identifier: str = "",
    ) -> None:
        self.title: str = title
        self.element_linked: pygame.Rect = element_linked
        self.has_close_button: bool = has_close_button
        self.title_color: pygame.Color = title_color
        self.element_grid: list[list[BoxElement]] = element_grid
        self.__separator: dict[str, Union[bool, int]] = {
            "display": has_vertical_separator,
            "vertical_position": 0,
            "height": 0,
        }
        background_path = (
            os.path.abspath(background_path)
            if background_path
            else _default_sprites["info_box_background"]
        )
        self.sprite: pygame.Surface = pygame.image.load(background_path)
        self.__close_button_background_path: str = close_button_background_path
        self.__close_button_background_hover_path: str = (
            close_button_background_hover_path
        )
        self.__elements: list[_Row] = self.init_elements()
        self.buttons: Sequence[Button] = []
        self.__size: tuple[int, int] = (width, 0)
        self.position: Position = pygame.Vector2(position)
        self.__is_position_static: bool = self.position != pygame.Vector2(0, 0)
        self.visible_on_background: bool = visible_on_background
        self.identifier: str = identifier

    def __repr__(self):
        return f"InfoBox with identifier '{self.identifier}'"

    def init_render(
        self, screen: pygame.Surface, close_button_callback: Callable = None
    ) -> None:
        """
        Initialize the rendering of the popup.

        Compute it size and its position according to the given screen.
        Determine the position of each component.

        Keyword arguments:
            screen (pygame.Surface): the screen on which the popup is
            close_button_callback (Callable): the callback that should be executed when clicking on
                the close button if there is any
        """
        if self.has_close_button:
            self.__elements[-1].elements[0].callback = close_button_callback
        self.__resize_elements()
        height: int = self.__determine_height()
        self.__size = (self.__size[0], height)
        if not self.__is_position_static:
            self.position = self.determine_position(screen)
        if self.position:
            self.determine_elements_position()
        self.buttons = self.find_buttons()
        self.sprite = pygame.transform.scale(self.sprite.convert_alpha(), self.__size)
        self.__separator["height"] += height

    def init_elements(self) -> list[_Row]:
        """
        Initialize the graphical elements associated to the formal data that the infoBox should
        represent.

        Returns:
             the elements in a 2D structure corresponding to the relative position of each element.
        """
        elements: list[_Row] = [
            _Row(element_line) for element_line in self.element_grid
        ]
        title = TextElement(
            self.title,
            pygame.Vector2(0, 0),
            _default_fonts["info_box_title"],
            (20, 0, 20, 0),
            self.title_color,
        )
        self.__separator["vertical_position"] += title.get_height()
        elements.insert(0, _Row([title]))
        if self.has_close_button:
            elements.append(
                _Row(
                    [
                        Button(
                            size=CLOSE_BUTTON_SIZE,
                            title=STR_CLOSE,
                            background_path=self.__close_button_background_path,
                            background_hover_path=self.__close_button_background_hover_path,
                            margin=(CLOSE_BUTTON_MARGIN_TOP, 0, 0, 0),
                        )
                    ]
                )
            )
        return elements

    def __determine_height(self) -> int:
        """
        Compute the total height of the infoBox, defined according
        to the height of each element in it.

        Returns:
             int: the computed height.
        """
        # Margin to be add at begin and at end
        height: int = MARGIN_BOX * 2
        self.__separator["height"] -= height
        self.__separator["vertical_position"] += height

        for row in self.__elements:
            max_height: int = 0
            for element in row.elements:
                el_height = element.get_height() + DEFAULT_MARGIN_TOP
                if el_height > max_height:
                    max_height = el_height
            height += max_height
            row.height = max_height

        if self.has_close_button:
            self.__separator["height"] -= self.__elements[-1].height

        return height

    def __resize_elements(self) -> None:
        """
        Resize elements according to the current width of the infoBox
        """
        for row in self.__elements:
            for element in row.elements:
                if isinstance(element, TextElement):
                    element.content = element._verify_rendered_text_size(
                        element.content,
                        element._text,
                        self.__size[0]
                        - element.get_margin_left()
                        - element.get_margin_right(),
                    )
                    element.size = element.content.get_size()

    def determine_position(self, screen: pygame.Surface) -> Optional[Position]:
        """
        Compute the position of the infoBox to be beside the linked element.

        If no element is linked to the infoBox, the position will be determined at display time
        according to the screen.

        Returns:
             Optional[Position]: the computed position.

        Keyword arguments:
            screen (pygame.Surface): The screen on which the infoBox is rendered.
        """
        if self.element_linked:
            position: Position = pygame.Vector2(
                self.element_linked.x
                + self.element_linked.width
                + MARGIN_LINKED_ELEMENT,
                self.element_linked.y
                + self.element_linked.height // 2
                - self.__size[1] // 2,
            )
            if position.y < 0:
                position.y = 0
            elif position.y + self.__size[1] > screen.get_height():
                position.y = screen.get_height() - self.__size[1]
            if position.x + self.__size[0] > screen.get_width():
                position.x = self.element_linked.x - self.__size[0]
            return position
        return None

    def find_buttons(self) -> Sequence[Button]:
        """
        Search in all elements for buttons.

        Returns:
             Sequence[Button]: the sequence of buttons.
        """
        buttons: list[Button] = []
        for row in self.__elements:
            for element in row.elements:
                if isinstance(element, Button):
                    buttons.append(element)
        return buttons

    def determine_elements_position(self) -> None:
        """
        Compute the position of each element and update it if needed.
        """
        y_coordinate: int = self.position[1] + MARGIN_BOX
        # Memorize mouse position in case it is over a button
        mouse_pos = pygame.mouse.get_pos()
        # A row begins by a value identifying its height, followed by its elements
        for row in self.__elements:
            nb_elements = len(row.elements)
            i = 1
            for element in row.elements:
                base_x = self.position.x + (self.__size[0] // (2 * nb_elements)) * i
                x_coordinate = base_x - element.get_width() // 2
                element.position = pygame.Vector2(
                    x_coordinate,
                    y_coordinate + element.get_margin_top(),
                )
                if isinstance(element, Button):
                    element.set_hover(element.get_rect().collidepoint(mouse_pos))
                i += 2
            y_coordinate += row.height

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the infoBox and all its elements.

        Keyword arguments:
            screen (pygame.Surface): the screen on which the displaying should be done
        """
        if self.position:
            screen.blit(self.sprite, self.position)
        else:
            win_size = screen.get_size()
            self.position = pygame.Vector2(
                win_size[0] // 2 - self.__size[0] // 2,
                win_size[1] // 2 - self.__size[1] // 2,
            )
            screen.blit(self.sprite, self.position)
            self.determine_elements_position()

        for row in self.__elements:
            for element in row.elements:
                element.display(screen)

        if self.__separator["display"]:
            pygame.draw.line(
                screen,
                WHITE,
                (
                    self.position.x + self.__size[0] / 2,
                    self.position.y + self.__separator["vertical_position"],
                ),
                (
                    self.position.x + self.__size[0] / 2,
                    self.position.y + self.__separator["height"],
                ),
                2,
            )

    def click(self, position: Position) -> Optional[Callable]:
        """
        Handle the triggering of a click event.

        Returns:
            Optional[Callable]: the data corresponding to the action that should be done if the click was done
                on a button, else None.

        Keyword arguments:
            position (Position): the position of the mouse
        """
        for button in self.buttons:
            if button.get_rect().collidepoint(position):
                return button.action_triggered()
        # Return a " do nothing " callable when clicking on empty space
        return lambda: None

    def motion(self, position: Position) -> None:
        """
        Handle the triggering of a motion event.
        Test if the mouse entered in a button or left one.

        Keyword arguments:
            position (Position): the position of the mouse
        """
        for button in self.buttons:
            mouse_is_on_button: bool = button.get_rect().collidepoint(position)
            button.set_hover(mouse_is_on_button and not button.disabled)
