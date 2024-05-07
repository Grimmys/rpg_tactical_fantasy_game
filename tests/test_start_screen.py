import os
import shutil
import unittest
from random import randrange

import pygame
from pygame.rect import Rect

from src.constants import BUTTON_SIZE, MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH
from src.gui.position import Position
from src.scenes.level_scene import LevelScene
from src.scenes.scene import QuitActionKind
from src.scenes.start_scene import StartScene
from tests.tools import minimal_setup_for_game

NEW_GAME_BUTTON_POS = Position(200, 230)
LOAD_GAME_BUTTON_POS = Position(200, 300)
LOAD_FIRST_SLOT_BUTTON_POS = Position(200, 203)
OPTIONS_BUTTON_POS = Position(200, 370)
EXIT_GAME_BUTTON_POS = Position(200, 440)

LEFT_BUTTON = 1
MIDDLE_BUTTON = 2
RIGHT_BUTTON = 3


class TestStartScreen(unittest.TestCase):
    buttons = []

    @classmethod
    def setUpClass(cls):
        super(TestStartScreen, cls).setUpClass()
        minimal_setup_for_game()
        cls.save_url = "saves/main_save.xml"
        cls.level_class = LevelScene
        cls.buttons.append(
            Rect(
                NEW_GAME_BUTTON_POS[0],
                NEW_GAME_BUTTON_POS[1],
                BUTTON_SIZE[0],
                BUTTON_SIZE[1],
            )
        )
        cls.buttons.append(
            Rect(
                LOAD_GAME_BUTTON_POS[0],
                LOAD_GAME_BUTTON_POS[1],
                BUTTON_SIZE[0],
                BUTTON_SIZE[1],
            )
        )
        cls.buttons.append(
            Rect(
                OPTIONS_BUTTON_POS[0],
                NEW_GAME_BUTTON_POS[1],
                BUTTON_SIZE[0],
                BUTTON_SIZE[1],
            )
        )
        cls.buttons.append(
            Rect(
                EXIT_GAME_BUTTON_POS[0],
                NEW_GAME_BUTTON_POS[1],
                BUTTON_SIZE[0],
                BUTTON_SIZE[1],
            )
        )

    @staticmethod
    def generate_position(start_position, end_position):
        # Generate random pos in a rect having start_pos as top left corner
        # and end_pos as bottom right corner
        position = Position(
            randrange(int(start_position.x), int(end_position.x)),
            randrange(int(start_position.y), int(end_position.y)),
        )
        # Print pos in case of test failure
        print(f"Generated position: {position}")
        return position

    def setUp(self):
        # Window parameters
        screen = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        self.start_screen = StartScene(screen)
        self.start_screen.display()

    def test_no_game_at_launch(self):
        # Verify no game is launched
        self.assertIsNone(self.start_screen.level)

    def test_new_game(self):
        # Memorize old screen
        screen = self.start_screen.screen.copy()

        # Generate random pos on new game button
        position = self.generate_position(
            NEW_GAME_BUTTON_POS, NEW_GAME_BUTTON_POS + BUTTON_SIZE
        )
        self.start_screen.click(LEFT_BUTTON, position)

        self.assertIsInstance(self.start_screen.level, self.level_class)
        self.assertEqual(self.start_screen.level.number, 0)
        self.assertNotEqual(self.start_screen.screen.get_rect(), screen.get_rect())

    def test_load_nonexistent_save(self):
        # Make a copy of the current window
        screen = self.start_screen.screen.copy()
        old_level = self.start_screen.level
        old_active_menu = self.start_screen.menu_manager.active_menu
        self.assertEqual(len(self.start_screen.menu_manager.background_menus), 0)

        # Erase save file if any
        if os.path.exists(self.save_url):
            os.remove(self.save_url)

        # Generate random pos on load game button
        position = self.generate_position(
            LOAD_GAME_BUTTON_POS, LOAD_GAME_BUTTON_POS + pygame.Vector2(BUTTON_SIZE)
        )
        self.start_screen.click(LEFT_BUTTON, position)

        self.assertIsNone(self.start_screen.level)
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(len(self.start_screen.menu_manager.background_menus), 1)
        self.assertEqual(
            self.start_screen.menu_manager.background_menus[0], old_active_menu
        )
        self.assertNotEqual(self.start_screen.menu_manager.active_menu, old_active_menu)

    def test_load_existent_save(self):
        # Memorize old screen
        screen = self.start_screen.screen.copy()

        # Import simple save file
        shutil.copyfile("tests/test_saves/simple_save.xml", self.save_url)

        # Generate random pos on load game buttons
        position = self.generate_position(
            LOAD_GAME_BUTTON_POS, LOAD_GAME_BUTTON_POS + pygame.Vector2(BUTTON_SIZE)
        )
        self.start_screen.click(LEFT_BUTTON, position)
        self.start_screen.display()
        position = self.generate_position(
            LOAD_FIRST_SLOT_BUTTON_POS, LOAD_FIRST_SLOT_BUTTON_POS + BUTTON_SIZE
        )
        self.start_screen.click(LEFT_BUTTON, position)

        self.assertIsInstance(self.start_screen.level, self.level_class)
        self.assertEqual(self.start_screen.level.number, 0)
        self.assertNotEqual(self.start_screen.screen.get_rect(), screen.get_rect())

    def test_options_menu(self):
        # Make a copy of the current window
        old_active_menu = self.start_screen.menu_manager.active_menu

        # Generate random pos on options button
        position = self.generate_position(
            OPTIONS_BUTTON_POS, OPTIONS_BUTTON_POS + pygame.Vector2(BUTTON_SIZE)
        )
        self.start_screen.click(LEFT_BUTTON, position)

        self.assertEqual(
            self.start_screen.menu_manager.background_menus[0], old_active_menu
        )
        self.assertNotEqual(self.start_screen.menu_manager.active_menu, old_active_menu)

    def test_exit_game(self):
        # Generate random pos on exit game button
        position = self.generate_position(
            EXIT_GAME_BUTTON_POS, EXIT_GAME_BUTTON_POS + BUTTON_SIZE
        )
        self.assertEqual(
            self.start_screen.click(LEFT_BUTTON, position), QuitActionKind.QUIT
        )

    def test_click_on_nothing(self):
        # Make a copy of the current window
        screen = self.start_screen.screen.copy()
        old_level = self.start_screen.level

        # Generate random pos not on any existent buttons
        valid_pos = False
        position = (0, 0)
        while not valid_pos:
            position = Position(
                randrange(0, self.start_screen.screen.get_size()[0]),
                randrange(0, self.start_screen.screen.get_size()[1]),
            )
            valid_pos = True
            for button in self.buttons:
                if button.collidepoint(position):
                    valid_pos = False
        # Print pos in case of a test failure
        print(f'test_click_on_nothing: {position}')

        self.start_screen.click(LEFT_BUTTON, position)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)

    def test_right_click(self):
        # Make a copy of the current window
        screen = self.start_screen.screen.copy()
        old_level = self.start_screen.level
        old_active_menu = self.start_screen.menu_manager.active_menu

        # Generate random position on new game button
        position = self.generate_position(
            NEW_GAME_BUTTON_POS, NEW_GAME_BUTTON_POS + BUTTON_SIZE
        )
        self.start_screen.click(RIGHT_BUTTON, position)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.menu_manager.active_menu, old_active_menu)

        # Generate random position on load game button
        position = self.generate_position(
            LOAD_GAME_BUTTON_POS, LOAD_GAME_BUTTON_POS + BUTTON_SIZE
        )
        self.start_screen.click(RIGHT_BUTTON, position)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.menu_manager.active_menu, old_active_menu)

        # Generate random position on options button
        position = self.generate_position(
            OPTIONS_BUTTON_POS, OPTIONS_BUTTON_POS + BUTTON_SIZE
        )
        self.start_screen.click(RIGHT_BUTTON, position)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.menu_manager.active_menu, old_active_menu)

        # Generate random position on exit game button
        position = self.generate_position(
            EXIT_GAME_BUTTON_POS, EXIT_GAME_BUTTON_POS + BUTTON_SIZE
        )
        self.start_screen.click(RIGHT_BUTTON, position)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.menu_manager.active_menu, old_active_menu)


if __name__ == "__main__":
    unittest.main()
