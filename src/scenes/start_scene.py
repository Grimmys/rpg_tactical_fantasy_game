"""
Defines StartScreen class, the initial scene of the game,
corresponding to the main menu.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Optional

import pygame
from lxml.etree import XMLSyntaxError
from pygamepopup.components import InfoBox, TextElement
from pygamepopup.menu_manager import MenuManager

from src.constants import SCREEN_SIZE, WIN_HEIGHT, WIN_WIDTH
from src.game_entities.movable import Movable
from src.game_entities.player import Player
from src.gui.fonts import fonts
from src.gui.position import Position
from src.scenes.level_scene import LevelScene, LevelStatus
from src.scenes.scene import QuitActionKind, Scene
from src.services import menu_creator_manager
from src.services.language import *


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
        self.menu_manager.open_menu(
            menu_creator_manager.create_start_menu(
                {
                    "new_game": self.new_game,
                    "load_menu": self.load_menu,
                    "options_menu": self.options_menu,
                    "exit_game": self.exit_game,
                }
            )
        )

        self.level: Optional[LevelScene] = None
        self.exit: QuitActionKind = QuitActionKind.CONTINUE

        self.options_file = None
        self.load_options()

    def load_options(self):
        """
        Load the saved game configuration from local file.
        """
        # Load current move speed
        self.options_file = etree.parse("saves/options.xml").getroot()
        Movable.move_speed = int(self.read_option("move_speed"))
        StartScene.screen_size = int(self.read_option("screen_size"))

    def read_option(self, element_to_read: str) -> str:
        """
        Read and parse a specific option saved in the local configuration file.

        Return the parsed value option value.

        Keyword arguments:
        element_to_read -- a name corresponding to the option that should be read
        """
        element = self.options_file.find(".//" + element_to_read)
        return element.text.strip()

    def modify_options_file(self, element_to_edit: str, new_value: str) -> None:
        """
        Edit the value of a specific option in the local configuration file.

        Keyword arguments:
        element_to_edit -- a name corresponding to the option that should be edited
        new_value -- the new value of the option
        """
        element: etree.Element = self.options_file.find(".//" + element_to_edit)
        element.text = new_value
        et = etree.ElementTree(self.options_file)
        et.write("saves/options.xml")

    def display(self) -> None:
        """
        Display the background of the start screen, and all the menus.
        """
        self.screen.blit(self.background, (0, 0))
        self.menu_manager.display()

    @staticmethod
    def generate_level_window() -> pygame.Surface:
        """
        Handle the generation of the screen dedicated to the ongoing level according to set parameters
        """
        # Modify screen
        flags: int = 0
        size: tuple[int, int] = (WIN_WIDTH, WIN_HEIGHT)
        if StartScene.screen_size == 2:
            flags = pygame.FULLSCREEN
            size = (0, 0)
        return pygame.display.set_mode(size, flags)

    def update_state(self) -> bool:
        """
        Update the state of the game.

        Return whether a level has been start or not to let the scene manager switch to this scene
        """
        return self.level is not None

    @staticmethod
    def load_new_level(
        level: int,
        level_screen: pygame.Surface,
        team: Optional[Sequence[Player]] = None,
    ) -> LevelScene:
        """
        Load a specific level.

        Return the Level instance created.

        Keyword arguments:
        level -- the id of the level that should be loaded
        team -- the sequence of players that will be in this level
        """
        if team is None:
            team = []
        return LevelScene(
            level_screen, "maps/level_" + str(level) + "/", level, players=team
        )

    def new_game(self) -> None:
        """
        Load the first level of the game.
        """
        # Init the first level
        self.level = StartScene.load_new_level(0, self.generate_level_window())

    def load_game(self, game_id: int) -> None:
        """
        Load a saved game from local directory.

        Keyword arguments:
        game_id -- the id of the saved file that should be load
        """
        try:
            with open(f"saves/save_{game_id}.xml", "r", encoding="utf-8") as save:
                tree_root: etree.Element = etree.parse(save).getroot()
                level_id = int(tree_root.find("level/index").text.strip())
                level_path = f"maps/level_{level_id}/"
                game_status = tree_root.find("level/phase").text.strip()
                turn_nb = int(tree_root.find("level/turn").text.strip())

                self.level = LevelScene(
                    StartScene.generate_level_window(),
                    level_path,
                    level_id,
                    LevelStatus[game_status],
                    turn_nb,
                    tree_root.find("level/entities"),
                )

        except XMLSyntaxError:
            # File does not contain expected values and may be corrupt
            name: str = "Load Game"
            width: int = self.screen.get_width() // 2
            self.menu_manager.open_menu(
                InfoBox(
                    name,
                    [
                        [
                            TextElement(
                                "Unable to load saved game. Save file appears corrupt.",
                                font=fonts["MENU_SUB_TITLE_FONT"],
                            )
                        ]
                    ],
                    width=width,
                    background_path="imgs/interface/PopUpMenu.png",
                )
            )

        except FileNotFoundError:
            # No saved game
            name: str = "Load Game"
            width: int = self.screen.get_width() // 2
            self.menu_manager.open_menu(
                InfoBox(
                    name,
                    [
                        [
                            TextElement(
                                "No saved game.", font=fonts["MENU_SUB_TITLE_FONT"]
                            )
                        ]
                    ],
                    width=width,
                    background_path="imgs/interface/PopUpMenu.png",
                )
            )

    def load_menu(self) -> None:
        """
        Move current active menu to the background and set a freshly created load game menu
        as the new active menu.
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_load_menu(self.load_game)
        )

    def options_menu(self) -> None:
        """
        Move current active menu to the background and set a freshly created option menu
        as the new active menu.
        Current option values are read from the local configuration file.
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_options_menu(
                {
                    "language": str(self.read_option("language")),
                    "move_speed": int(self.read_option("move_speed")),
                    "screen_size": int(self.read_option("screen_size")),
                },
                self.modify_option_value,
            )
        )

    def choose_language_menu(self) -> None:
        self.menu_manager.open_menu(
            menu_creator_manager.create_choose_language_menu(self.change_language)
        )

    def change_language(self, new_language) -> None:
        self.modify_options_file("language", new_language)
        self.exit = QuitActionKind.RESTART

    def exit_game(self) -> None:
        """
        Handle an exit game request.
        """
        self.exit = QuitActionKind.QUIT

    def modify_option_value(self, option_name: str, option_value: int = 0) -> None:
        """

        Keyword arguments:
        option_name --
        option_value --
        """
        if option_name == "language":
            self.choose_language_menu()
            return
        elif option_name == "move_speed":
            Movable.move_speed = option_value
        elif option_name == "screen_size":
            StartScene.screen_size = option_value
        else:
            print(f"Unrecognized option name : {option_name} with value {option_value}")
            return
        self.modify_options_file(option_name, str(option_value))

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
        Delegate it to the active menu.

        Keyword arguments:
        position -- the position of the mouse
        """
        self.menu_manager.motion(position)

    def click(self, button: int, position: Position) -> QuitActionKind:
        """
        Handle the triggering of a click event.
        Delegate it to the active menu if it is a left-click.

        Return whether an exit request has been made or not.

        Keyword arguments:
        button -- an integer value representing which mouse button has been pressed
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        self.menu_manager.click(button, position)
        return self.exit
