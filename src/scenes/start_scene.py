"""
Defines StartScreen class, the initial scene of the game,
corresponding to the main menu.
"""
from __future__ import annotations

from typing import Sequence, Callable, Optional

import pygame
from lxml import etree
from lxml.etree import XMLSyntaxError
from pygamepopup.components import InfoBox, TextElement
from pygamepopup.menu_manager import MenuManager

from src.constants import (
    SCREEN_SIZE,
    BLACK,
    WIN_WIDTH,
    WIN_HEIGHT,
    MAIN_WIN_WIDTH,
    MAIN_WIN_HEIGHT
)
from src.game_entities.movable import Movable
from src.game_entities.player import Player
from src.gui.fonts import fonts
from src.gui.position import Position
from src.scenes.level_scene import LevelScene, LevelStatus
from src.scenes.scene import Scene
from src.services import menu_creator_manager


class StartScene(Scene):
    """
    This class is the initial scene of the game, handling all kind of pygame events directly
    received from the main file.
    Also manage the display of different menus, the ability to read and edit configuration files
    or saved games and the request to quit the game.

    Keywords:
    screen -- the pygame Surface corresponding to the main menu screen

    Attributes:
    menu_screen -- copy of the main menu screen to keep it in memory if the scene change
    background -- the background pygame Surface of the scene
    menu_manager -- the reference to the menu manager entity
    level -- the reference to the current running level
    levels -- the list of level ids
    level_id -- the id of the current level
    exit -- a boolean indicating if an exit request has been made
    """

    screen_size: int = SCREEN_SIZE

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen)

        self.menu_screen: pygame.Surface = self.screen.copy()

        # Start screen loop
        background_image: pygame.Surface = pygame.image.load(
            "imgs/interface/main_menu_background.jpg"
        ).convert_alpha()
        self.background: pygame.Surface = pygame.transform.scale(
            background_image, screen.get_size()
        )

        self.menu_manager = MenuManager(screen)

        # Creating main menu
        self.menu_manager.open_menu(menu_creator_manager.create_start_menu(
            {
                "new_game": self.new_game,
                "load_menu": self.load_menu,
                "options_menu": self.options_menu,
                "exit_game": self.exit_game,
            }
        ))

        # Memorize if a game is currently being performed
        self.level: Optional[LevelScene] = None
        self.level_screen: Optional[pygame.Surface] = None

        self.levels: Sequence[int] = [0, 1, 2, 3]
        self.level_id: Optional[int] = None

        # Load current saved parameters
        StartScene.load_options()

        self.exit: bool = False

    @staticmethod
    def load_options():
        """
        Load the saved game configuration from local file.
        """
        # Load current move speed
        Movable.move_speed = int(StartScene.read_options_file("move_speed"))
        StartScene.screen_size = int(StartScene.read_options_file("screen_size"))

    @staticmethod
    def read_options_file(element_to_read: str) -> str:
        """
        Read and parse a specific option saved in the local configuration file.

        Return the parsed value option value.

        Keyword arguments:
        element_to_read -- a name corresponding to the option that should be read
        """
        # TODO: Might be interesting to not re-load the file for each different option to parse
        tree = etree.parse("saves/options.xml").getroot()
        element = tree.find(".//" + element_to_read)
        return element.text.strip()

    @staticmethod
    def modify_options_file(element_to_edit: str, new_value: str) -> None:
        """
        Edit the value of a specific option in the local configuration file.

        Keyword arguments:
        element_to_edit -- a name corresponding to the option that should be edited
        new_value -- the new value of the option
        """
        tree: etree.ElementTree = etree.parse("saves/options.xml")
        element: etree.Element = tree.find(".//" + element_to_edit)
        element.text = new_value
        tree.write("saves/options.xml")

    def display(self) -> None:
        """
        Display the level on screen if there is one, else display the background
        of the start screen, all the menus in the background and lastly the active menu.
        """
        if self.level:
            self.screen.fill(BLACK)
            self.level.display()
        else:
            self.screen.blit(self.background, (0, 0))
            self.menu_manager.display()

    def _generate_level_window(self) -> None:
        """
        Handle the generation of the part of the screen dedicated to the ongoing level and change the screen according
        to the set parameters
        """
        # Modify screen
        flags: int = 0
        size: tuple[int, int] = (WIN_WIDTH, WIN_HEIGHT)
        if StartScene.screen_size == 2:
            flags = pygame.FULLSCREEN
            size = (0, 0)
        self.screen = pygame.display.set_mode(size, flags)
        level_width: int = min(self.screen.get_width(), WIN_WIDTH)
        level_height: int = min(self.screen.get_height(), WIN_HEIGHT)
        self.level_screen = self.screen.subsurface(
            pygame.Rect(self.screen.get_width() // 2 - level_width // 2,
                        self.screen.get_height() // 2 - level_height // 2,
                        level_width, level_height)
        )

    def update_state(self) -> None:
        """
        Update the state of the game.
        If there is an ongoing level, update it and verify that it's not ended.
        If it's ended with a victory, start the next level.
        If it's a defeat or if there is no next level, let the start screen be the active screen
        again.
        """
        if self.level:
            status: int = self.level.update_state()
            if (
                status is LevelStatus.ENDED_VICTORY
                and (self.level_id + 1) in self.levels
            ):
                self.level_id += 1
                team: Sequence[Player] = self.level.passed_players + self.level.players
                for player in team:
                    # Players are fully restored between level
                    player.healed(player.hit_points_max)
                    # Reset player's state
                    player.new_turn()
                self._generate_level_window()
                self.level = StartScene.load_new_level(self.level_id, self.level_screen, team)
            elif (
                status is LevelStatus.ENDED_VICTORY
                or status is LevelStatus.ENDED_DEFEAT
            ):
                # TODO: Game win dialog?
                self.screen = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
                self.level = None

    @staticmethod
    def load_new_level(level: int, level_screen: pygame.Surface, team: Optional[Sequence[Player]] = None) -> LevelScene:
        """
        Load a specific level.

        Return the Level instance created.

        Keyword arguments:
        level -- the id of the level that should be loaded
        team -- the sequence of players that will be in this level
        """
        if team is None:
            team = []
        return LevelScene(level_screen, "maps/level_" + str(level) + "/", level, players=team)

    def new_game(self) -> None:
        """
        Load the first level of the game.
        """
        # Init the first level
        self.level_id = 0
        self._generate_level_window()
        self.level = StartScene.load_new_level(self.level_id, self.level_screen)

    def load_game(self, game_id: int) -> None:
        """
        Load a saved game from local directory.

        Keyword arguments:
        game_id -- the id of the saved file that should be load
        """
        try:
            with open(f"saves/save_{game_id}.xml", "r", encoding="utf-8") as save:
                tree_root: etree.Element = etree.parse(save).getroot()
                index: str = tree_root.find("level/index").text.strip()
                level_name: str = f"maps/level_{index}/"
                game_status: str = tree_root.find("level/phase").text.strip()
                turn_nb = int(tree_root.find("level/turn").text.strip())

                # Load level with current game status, foes states, and team
                self.level_id = int(index)
                self._generate_level_window()
                self.level = LevelScene(self.level_screen, level_name, self.level_id, LevelStatus[game_status], turn_nb,
                                        tree_root.find("level/entities"))

        except XMLSyntaxError:
            # File does not contain expected values and may be corrupt
            name: str = "Load Game"
            width: int = self.screen.get_width() // 2
            self.menu_manager.open_menu(InfoBox(
                name,
                [
                    [
                        TextElement(
                            "Unable to load saved game. Save file appears corrupt.",
                            font=fonts["MENU_SUB_TITLE_FONT"]
                        )
                    ]
                ],
                width=width,
                background_path="imgs/interface/PopUpMenu.png",
            ))

        except FileNotFoundError:
            # No saved game
            name: str = "Load Game"
            width: int = self.screen.get_width() // 2
            self.menu_manager.open_menu(InfoBox(
                name,
                [
                    [
                        TextElement(
                            "No saved game.",
                            font=fonts["MENU_SUB_TITLE_FONT"]
                        )
                    ]
                ],
                width=width,
                background_path="imgs/interface/PopUpMenu.png",
            ))

    def load_menu(self) -> None:
        """
        Move current active menu to the background and set a freshly created load game menu
        as the new active menu.
        """
        self.menu_manager.open_menu(menu_creator_manager.create_load_menu(self.load_game))

    def options_menu(self) -> None:
        """
        Move current active menu to the background and set a freshly created option menu
        as the new active menu.
        Current option values are read from the local configuration file.
        """
        self.menu_manager.open_menu(menu_creator_manager.create_options_menu(
            {
                "move_speed": int(self.read_options_file("move_speed")),
                "screen_size": int(self.read_options_file("screen_size")),
            },
            self.modify_option_value,
        ))

    def exit_game(self) -> None:
        """
        Handle an exit game request.
        """
        self.exit = True

    @staticmethod
    def modify_option_value(option_name: str, option_value: int) -> None:
        """

        Keyword arguments:
        option_name --
        option_value --
        """
        if option_name == "move_speed":
            Movable.move_speed = option_value
        elif option_name == "screen_size":
            StartScene.screen_size = option_value
        else:
            print(f"Unrecognized option name : {option_name} with value {option_value}")
            return
        StartScene.modify_options_file(option_name, str(option_value))

    @staticmethod
    def execute_action(action: Callable) -> None:
        """
        Manage actions related to a click on a button.
        Simply execute the given callable.

        Keyword arguments:
        action -- the callable associated to the clicked button
        """
        action()

    def motion(self, position: Position) -> None:
        """
        Handle the triggering of a motion event.
        Delegate the event to the current running level if there is one,
        else delegate it to the active menu.

        Keyword arguments:
        position -- the position of the mouse
        """
        if self.level is None:
            self.menu_manager.motion(position)
        else:
            relative_position: Position = self._compute_relative_position(position)
            if relative_position.length() >= 0:
                self.level.motion(relative_position)

    def click(self, button: int, position: Position) -> bool:
        """
        Handle the triggering of a click event.
        Delegate the event to the current running level if there is one,
        else delegate it to the active menu if it is a left-click.

        Return whether an exit request has been made or not.

        Keyword arguments:
        button -- an integer value representing which mouse button has been pressed
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        if self.level is None:
            self.menu_manager.click(button, position)
        else:
            relative_position: Position = self._compute_relative_position(position)
            if relative_position.length() >= 0:
                self.level.click(button, relative_position)
        return self.exit

    def button_down(self, button: int, position: Position) -> None:
        """
        Handle the triggering of a mouse button down event.
        Delegate the event to the current running level if there is one.

        Keyword arguments:
        button -- an integer value representing which mouse button is down
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        if self.level is not None:
            relative_position: Position = self._compute_relative_position(position)
            if relative_position.length() >= 0:
                self.level.button_down(button, relative_position)

    def _compute_relative_position(self, position: Position) -> Position:
        """
        Compute and return a position relative to the left top corner of the ongoing level screen

        Keyword arguments:
        position -- the absolute position to be converted
        """
        return position - pygame.Vector2(self.screen.get_width() // 2 - self.level_screen.get_width() // 2,
                                         self.screen.get_height() // 2 - self.level_screen.get_height() // 2)
