"""
Defines MenuManager class, the main class to handle the displaying of all menus on a screen and
handle the triggering of user events on the elements of the active menu
"""

from __future__ import annotations

from typing import Optional, Sequence

import pygame

from ..gui.info_box import InfoBox
from pygamepopup.types import Position


class MenuManager:
    """
    This class represents a manager for the interfaces of a screen.

    It displays all the menus currently registered in the manager.

    Handle the opening of a new menu and the closing of the active one.
    Handle the triggering of user motion events and user click events on the active menu.

    Keyword arguments:
        screen (pygame.Surface): the screen on which the menus should be displayed and on which the
            user events should be handled

    Attributes:
        screen (pygame.Surface): the screen on which the menus should be displayed and on which the
            user events should be handled
        active_menu (Optional[InfoBox]): the current menu in the foreground, the only one that will react to user events
        background_menus (list[InfoBox]): the ordered sequence of menus that are in the background
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen: pygame.Surface = screen
        self.active_menu: Optional[InfoBox] = None
        self.background_menus: list[InfoBox] = []

    def open_menu(self, menu: InfoBox) -> None:
        """
        Open the given menu.
        Initialize the rendering of the menu, and set it as the new active menu.

        Previous active menu is sent to the background.

        Keyword arguments:
            menu (InfoBox): the popup that should be open
        """
        self._prepare_menu(menu)
        if self.active_menu:
            self.background_menus.append(self.active_menu)
        self.active_menu = menu

    def replace_given_menu(
        self, menu_identifier: str, new_menu: InfoBox, all_occurrences: bool = False
    ) -> bool:
        """
        Replace a menu by a new one according to its identifier.

        By default, only first occurrence is replaced if many menus in the manager have the given identifier.

        Keyword arguments:
            menu_identifier (str): the identifier of the menu to be replaced
            new_menu (InfoBox): the menu that should replace the given one
            all_occurrences (bool): whether all found occurrences should be replaced or only the first one

        Returns:
             bool: whether the replacement has succeeded or not
        """
        has_replacement_been_done = False
        if self.active_menu and self.active_menu.identifier == menu_identifier:
            self._prepare_menu(new_menu)
            self.active_menu = new_menu
            if not all_occurrences:
                return True
            has_replacement_been_done = True
        for index, menu in enumerate(self.background_menus):
            if menu.identifier == menu_identifier:
                self._prepare_menu(new_menu)
                self.background_menus[index] = new_menu
                if not all_occurrences:
                    return True
                has_replacement_been_done = True
        return has_replacement_been_done

    def close_active_menu(self) -> None:
        """
        Close the active menu by 'destroying' it.

        Take the next menu in the background to move it to foreground if there is any.
        """
        self.active_menu = (
            self.background_menus.pop() if len(self.background_menus) != 0 else None
        )
        if self.active_menu:
            # Trigger an irrelevant motion event to refresh the hovering of buttons on the new menu
            self.active_menu.motion(pygame.Vector2(pygame.mouse.get_pos()))

    def close_given_menu(
        self, menu_identifier: str, all_occurrences: bool = False
    ) -> bool:
        """
        Close menu corresponding to the given identifier.

        By default, only first occurrence is closed if many menus in the manager have the given identifier.

        Keyword arguments:
            menu_identifier (str): the identifier of the menu to be closed
            all_occurrences (bool): whether all found occurrences should be closed or only the first one,
                defaults to False

        Returns:
             bool: whether at least one menu has been closed or not
        """
        if self.active_menu and self.active_menu.identifier == menu_identifier:
            self.active_menu = None
            if not all_occurrences:
                return True

        matching_menus_in_background = self._get_given_menus_from_background(
            menu_identifier
        )
        for menu in matching_menus_in_background:
            self.background_menus.remove(menu)
            if not all_occurrences:
                break
        return len(matching_menus_in_background) > 0

    def clear_menus(self) -> None:
        """
        Close all the menus (in foreground and in background)
        """
        self.active_menu = None
        self.background_menus.clear()

    def reduce_active_menu(self) -> None:
        """
        Move the active menu to the background.
        """
        if self.active_menu:
            self.background_menus.append(self.active_menu)
            self.active_menu = None

    def display(self) -> None:
        """
        Display all the visible menus in the background in order first, then display the active menu
        """
        for menu in self.background_menus:
            if menu.visible_on_background:
                menu.display(self.screen)
        if self.active_menu:
            self.active_menu.display(self.screen)

    def click(self, button: int, position: Position) -> None:
        """
        Handle the triggering of a click event.
        Delegate this event to the active menu if there is any and if it's a left click.

        Keyword arguments:
            button (int): a value representing which mouse button has been pressed
                (1 for left button, 2 for middle button, 3 for right button)
            position (Position): the position of the mouse
        """
        if button == 1:
            if self.active_menu:
                self.active_menu.click(position)()

    def motion(self, position: Position) -> None:
        """
        Handle the triggering of a motion event.
        Delegate this event to the active menu if there is any.

        Keyword arguments:
            position (Position): the position of the mouse
        """
        if self.active_menu:
            self.active_menu.motion(position)

    def _prepare_menu(self, menu: InfoBox) -> None:
        """
        Prepare the given menu to be rendered according to the current setup.

        Keyword arguments:
            menu (InfoBox): the menu to be initialized
        """
        menu.init_render(self.screen, close_button_callback=self.close_active_menu)

    def _get_given_menus_from_background(
        self, menu_identifier: str
    ) -> Sequence[InfoBox]:
        """
        Returns:
             Sequence[InfoBox]: all the menus in background matching the given identifier

        Keyword arguments:
            menu_identifier (str): the identifier to look for
        """
        return [
            menu for menu in self.background_menus if menu.identifier == menu_identifier
        ]
