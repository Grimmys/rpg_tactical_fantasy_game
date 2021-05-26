"""
Defines StartScreen class, the initial scene of the game,
corresponding to the main menu.
"""
from enum import Enum
from typing import Sequence, List, Union

import pygame
from lxml import etree

from src.constants import SCREEN_SIZE, BLACK, WIN_WIDTH, WIN_HEIGHT, MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from src.game_entities.player import Player
from src.gui.position import Position
from src.services import menu_creator_manager
from src.gui.fonts import fonts
from src.scenes.level import Level, LevelStatus
from src.gui.info_box import InfoBox
from src.game_entities.movable import Movable
from src.services.menus import StartMenu, OptionsMenu, GenericActions, LoadMenu


class StartScreen:
    """
    This class is the initial scene of the game, handling all kind of pyame events directly
    received from the main file.
    Also manage the display of different menus, the ability to read and edit configuration files
    or saved games and the request to quit the game.

    Keywords:
    screen -- the pygame Surface corresponding to the main menu screen

    Attributes:
    screen -- the pygame Surface corresponding to the active scene
    menu_screen -- copy of the main menu screen to keep it in memory if the scene change
    background -- the background pygame Surface of the scene
    active_menu -- the reference to the menu in the foreground: it's always the active one
    background_menus -- the stack of menus in the background,
    a boolean value is associated to each menu in the background to know
    if it should be displayed or not
    level -- the reference to the current running level
    levels -- the list of level ids
    level_id -- the id of the current level
    exit -- the boolean value indicating if an exit request has been made
    """
    screen_size = SCREEN_SIZE

    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen
        self.menu_screen: pygame.Surface = self.screen.copy()

        # Start screen loop
        background_image: pygame.Surface = pygame.image.load(
            'imgs/interface/main_menu_background.jpg').convert_alpha()
        self.background: pygame.Surface = pygame.transform.scale(background_image,
                                                                 screen.get_size())

        # Creating menu
        self.active_menu: InfoBox = menu_creator_manager.create_start_menu()
        self.background_menus: List[tuple[InfoBox, bool]] = []

        # Memorize if a game is currently being performed
        self.level = None

        self.levels = [0, 1, 2, 3]
        self.level_id = None

        # Load current saved parameters
        StartScreen.load_options()

        self.exit = False

    @staticmethod
    def load_options():
        """

        """
        # Load current move speed
        Movable.move_speed = int(StartScreen.read_options_file("move_speed"))
        StartScreen.screen_size = int(StartScreen.read_options_file("screen_size"))

    @staticmethod
    def read_options_file(element_to_read: str) -> str:
        """

        :param element_to_read:
        :return:
        """
        tree = etree.parse("saves/options.xml").getroot()
        element = tree.find(".//" + element_to_read)
        return element.text.strip()

    @staticmethod
    def modify_options_file(element_to_edit: str, new_value: str) -> None:
        """

        :param element_to_edit:
        :param new_value:
        """
        tree = etree.parse("saves/options.xml")
        element = tree.find(".//" + element_to_edit)
        element.text = new_value
        tree.write("saves/options.xml")

    def display(self) -> None:
        """

        """
        if self.level:
            self.screen.fill(BLACK)
            self.level.display(self.screen)
        else:
            self.screen.blit(self.background, (0, 0))
            for menu in self.background_menus:
                if menu[1]:
                    menu[0].display(self.screen)
            if self.active_menu:
                self.active_menu.display(self.screen)

    def play(self, level: Level) -> None:
        """

        :param level:
        """
        # Modify screen
        flags = pygame.FULLSCREEN if StartScreen.screen_size == 2 else 0
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), flags)
        self.level = level

    def update_state(self) -> None:
        """

        """
        if self.level:
            status = self.level.update_state()
            if status is LevelStatus.ENDED_VICTORY and (self.level_id + 1) in self.levels:
                self.level_id += 1
                team = self.level.passed_players + self.level.players
                for player in team:
                    # Players are fully restored between level
                    player.healed(player.hp_max)
                    # Reset player's state
                    player.new_turn()
                self.play(StartScreen.load_level(self.level_id, team))
            elif status is LevelStatus.ENDED_VICTORY or status is LevelStatus.ENDED_DEFEAT:
                # TODO: Game win dialog?
                self.screen = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
                self.level = None

    @staticmethod
    def load_level(level: int, team: Sequence[Player] = None):
        """

        :param level:
        :param team:
        :return:
        """
        if team is None:
            team = []
        return Level('maps/level_' + str(level) + '/', level, players=team)

    def new_game(self) -> None:
        """

        """
        # Init the first level
        self.level_id = 0
        self.play(StartScreen.load_level(self.level_id))

    def load_game(self, game_id: int):
        """

        :param game_id:
        :return:
        """
        try:
            save = open(f"saves/save_{game_id}.xml", "r")

            # Test if there is a current saved game
            if save:
                tree_root = etree.parse(save).getroot()
                index = tree_root.find("level/index").text.strip()
                level_name = 'maps/level_' + index + '/'
                game_status = tree_root.find("level/phase").text.strip()
                turn_nb = 0
                if game_status != 'I':
                    turn_nb = int(tree_root.find("level/turn").text.strip())

                # Load level with current game status, foes states, and team
                self.level_id = int(index)
                level = Level(level_name, self.level_id, LevelStatus[game_status], turn_nb,
                              tree_root.find("level/entities"))
                self.play(level)
                save.close()
                return
        except FileNotFoundError:
            # No saved game
            self.background_menus.append((self.active_menu, True))

            name = "Load Game"
            entries = [[{'type': 'text', 'text': "No saved game.",
                         'font': fonts['MENU_SUB_TITLE_FONT']}]]
            width = self.screen.get_width() // 2
            self.active_menu = InfoBox(name, "imgs/interface/PopUpMenu.png", entries, "", width,
                                       close_button=1)

    def load_menu(self) -> None:
        """
        Move current active menu to the background and set a freshly created load game menu
        as the new active menu.
        """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = menu_creator_manager.create_load_menu()

    def options_menu(self) -> None:
        """
        Move current active menu to the background and set a freshly created option menu
        as the new active menu.
        Current option values are read from the local configuration file.
        """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = menu_creator_manager.create_options_menu(
            {'move_speed': int(self.read_options_file('move_speed')),
             'screen_size': int(self.read_options_file('screen_size'))})

    def exit_game(self) -> None:
        """
        Handle an exit game request.
        """
        self.exit = True

    def main_menu_action(self, method_id: StartMenu, arguments: Sequence[any]) -> None:
        """
        Execute the method corresponding to the id provided for an action related to the main menu.
        Currently, no arguments are required for any of the available methods.

        Keyword arguments:
        method_id -- the id referencing the method that should be called
        arguments -- the arguments that should be passed to the called method
        (unused for the moment)
        """
        # Execute action
        if method_id is StartMenu.NEW_GAME:
            self.new_game()
        elif method_id is StartMenu.LOAD_GAME:
            self.load_menu()
        elif method_id is StartMenu.OPTIONS:
            self.options_menu()
        elif method_id is StartMenu.EXIT:
            self.exit_game()
        else:
            print(f"Unknown action : {method_id}")

    def load_menu_action(self, method_id: LoadMenu, arguments: Sequence[any]) -> None:
        """
        Execute the method corresponding to the id provided for an action related to the load menu.

        Keyword arguments:
        method_id -- the id referencing the method that should be called
        arguments -- the arguments that should be passed to the called method
        """
        # Execute action
        if method_id is LoadMenu.LOAD:
            self.load_game(arguments[2][0])
        else:
            print(f"Unknown action: {method_id}")

    @staticmethod
    def options_menu_action(method_id: OptionsMenu, arguments: Sequence[any]) -> None:
        """
        Execute the method corresponding to the id provided for an action related to the
        options menu.

        Keyword arguments:
        method_id -- the id referencing the method that should be called
        arguments -- the arguments that should be passed to the called method
        """
        # Execute action
        if method_id is OptionsMenu.CHANGE_MOVE_SPEED:
            Movable.move_speed = arguments[2][0]
            StartScreen.modify_options_file("move_speed", str(arguments[2][0]))
        elif method_id is OptionsMenu.CHANGE_SCREEN_SIZE:
            StartScreen.screen_size = arguments[2][0]
            StartScreen.modify_options_file("screen_size", str(arguments[2][0]))
        else:
            print(f"Unknown action : {method_id}")

    def execute_action(self, menu_type: int, action: Union[tuple[Union
                                                                 [StartMenu, OptionsMenu, LoadMenu],
                                                                 tuple[Position,
                                                                       any, List[
                                                                           any]]], bool]) -> None:
        """
        Manager of actions related to a click on a button.
        Delegate the responsibility to execute the action to the dedicated handler.

        Keyword arguments:
        menu_type -- the type of menu on which the click has been done
        action -- the data relative to the action that should been done (id to reference the method,
        arguments to send to the called method)
        """
        if not action:
            return

        method_id = action[0]
        arguments = action[1]

        # Test if the action is a generic one (according to the method_id)
        # Close menu : Active menu is closed
        if method_id is GenericActions.CLOSE:
            self.active_menu = self.background_menus.pop()[0] if self.background_menus else None
            return

        if menu_type is StartMenu:
            self.main_menu_action(method_id, arguments)
        elif menu_type is OptionsMenu:
            StartScreen.options_menu_action(method_id, arguments)
        elif menu_type is LoadMenu:
            self.load_menu_action(method_id, arguments)
        else:
            print(f"Unknown menu : {menu_type}")

    def motion(self, position: Position) -> None:
        """
        Handle the triggering of a motion event.
        Delegate the event to the current running level if there is one,
        else delegate it to the active menu.

        Keyword arguments:
        position -- the position of the mouse
        """
        if self.level is None:
            self.active_menu.motion(position)
        else:
            self.level.motion(position)

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
            if button == 1:
                self.execute_action(self.active_menu.type, self.active_menu.click(position))
        else:
            self.level.click(button, position)
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
            self.level.button_down(button, position)
