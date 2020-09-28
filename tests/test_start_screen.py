import os
import shutil
import unittest

import pygame as pg
from pygame.rect import Rect
from random import randrange

from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from src.StartScreen import StartScreen

NEW_GAME_BUTTON_POS = (325, 349)
LOAD_GAME_BUTTON_POS = (325, 389)
OPTIONS_BUTTON_POS = (325, 429)
EXIT_GAME_BUTTON_POS = (325, 469)
BUTTON_SIZE = (150, 30)

LEFT_BUTTON = 1
MIDDLE_BUTTON = 2
RIGHT_BUTTON = 3


class TestStartScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.Level import Level
        from src.Character import Character
        from src import LoadFromXMLManager as Loader
        import src.fonts as font
        os.chdir(os.getcwd() + '/..')
        pg.init()
        font.init_fonts()
        cls.save_url = "saves/main_save.xml"
        cls.level_class = Level
        cls.buttons = []
        cls.buttons.append(Rect(NEW_GAME_BUTTON_POS[0], NEW_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        cls.buttons.append(Rect(LOAD_GAME_BUTTON_POS[0], LOAD_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        cls.buttons.append(Rect(OPTIONS_BUTTON_POS[0], NEW_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        cls.buttons.append(Rect(EXIT_GAME_BUTTON_POS[0], NEW_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        races = Loader.load_races()
        classes = Loader.load_classes()
        Character.init_data(races, classes)

    @staticmethod
    def generate_position(start_pos, end_pos):
        # Generate random pos in a rect having start_pos as top left corner, and end_pos as bottom right corner
        pos = (randrange(start_pos[0], end_pos[0] + 1),
               randrange(start_pos[1], end_pos[1] + 1))
        # Print pos in case of test failure
        print("Generated position : " + str(pos))
        return pos

    def setUp(self):
        # Window parameters
        screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        self.start_screen = StartScreen(screen)
        self.start_screen.display()

    def test_no_game_at_launch(self):
        # Verify no game is launched
        self.assertIsNone(self.start_screen.level)
        self.assertIsNone(self.start_screen.level_id)

    def test_new_game(self):
        # Memorize old screen
        screen = self.start_screen.screen.copy()

        # Generate random pos on new game button
        pos = self.generate_position(NEW_GAME_BUTTON_POS, NEW_GAME_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(LEFT_BUTTON, pos)

        self.assertIsInstance(self.start_screen.level, self.level_class)
        self.assertEqual(self.start_screen.level_id, 0)
        self.assertNotEqual(self.start_screen.screen.get_rect(), screen.get_rect())

    def test_load_nonexistent_save(self):
        # Make a copy of the current window
        screen = self.start_screen.screen.copy()
        old_level = self.start_screen.level
        old_level_id = self.start_screen.level_id
        old_active_menu = self.start_screen.active_menu
        self.assertEqual(len(self.start_screen.background_menus), 0)

        # Erase save file if any
        if os.path.exists(self.save_url):
            os.remove(self.save_url)

        # Generate random pos on load game button
        pos = self.generate_position(LOAD_GAME_BUTTON_POS, LOAD_GAME_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(LEFT_BUTTON, pos)

        self.assertIsNone(self.start_screen.level)
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(len(self.start_screen.background_menus), 1)
        self.assertEqual(self.start_screen.background_menus[0][0], old_active_menu)
        self.assertNotEqual(self.start_screen.active_menu, old_active_menu)

    def test_load_existent_save(self):
        # Memorize old screen
        screen = self.start_screen.screen.copy()

        # Import simple save file
        shutil.copyfile("tests/test_saves/simple_save.xml", self.save_url)

        # Generate random pos on load game button
        pos = self.generate_position(LOAD_GAME_BUTTON_POS, LOAD_GAME_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(LEFT_BUTTON, pos)

        self.assertIsInstance(self.start_screen.level, self.level_class)
        self.assertEqual(self.start_screen.level_id, 0)
        self.assertNotEqual(self.start_screen.screen.get_rect(), screen.get_rect())

    def test_options_menu(self):
        # Make a copy of the current window
        old_active_menu = self.start_screen.active_menu

        # Generate random pos on options button
        pos = self.generate_position(OPTIONS_BUTTON_POS, OPTIONS_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(LEFT_BUTTON, pos)

        self.assertEqual(self.start_screen.background_menus[0][0], old_active_menu)
        self.assertNotEqual(self.start_screen.active_menu, old_active_menu)

    def test_exit_game(self):
        # Generate random pos on exit game button
        pos = self.generate_position(EXIT_GAME_BUTTON_POS, EXIT_GAME_BUTTON_POS + BUTTON_SIZE)
        self.assertEqual(self.start_screen.click(LEFT_BUTTON, pos), True)

    def test_click_on_nothing(self):
        # Make a copy of the current window
        screen = self.start_screen.screen.copy()
        old_level = self.start_screen.level
        old_level_id = self.start_screen.level_id
        old_active_menu = self.start_screen.active_menu

        # Generate random pos not on any existent buttons
        valid_pos = False
        while not valid_pos:
            pos = (randrange(0, self.start_screen.screen.get_size()[0]),
                   randrange(0, self.start_screen.screen.get_size()[1]))
            valid_pos = True
            for button in self.buttons:
                if button.collidepoint(pos):
                    valid_pos = False
        # Print pos in case of a test failure
        print(pos)

        self.start_screen.click(LEFT_BUTTON, pos)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(self.start_screen.active_menu, old_active_menu)

    def test_right_click(self):
        # Make a copy of the current window
        screen = self.start_screen.screen.copy()
        old_level = self.start_screen.level
        old_level_id = self.start_screen.level_id
        old_active_menu = self.start_screen.active_menu

        # Generate random pos on new game button
        pos = self.generate_position(NEW_GAME_BUTTON_POS, NEW_GAME_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(RIGHT_BUTTON, pos)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(self.start_screen.active_menu, old_active_menu)

        # Generate random pos on load game button
        pos = self.generate_position(LOAD_GAME_BUTTON_POS, LOAD_GAME_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(RIGHT_BUTTON, pos)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(self.start_screen.active_menu, old_active_menu)

        # Generate random pos on options button
        pos = self.generate_position(OPTIONS_BUTTON_POS, OPTIONS_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(RIGHT_BUTTON, pos)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(self.start_screen.active_menu, old_active_menu)

        # Generate random pos on exit game button
        pos = self.generate_position(EXIT_GAME_BUTTON_POS, EXIT_GAME_BUTTON_POS + BUTTON_SIZE)
        self.start_screen.click(RIGHT_BUTTON, pos)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(self.start_screen.active_menu, old_active_menu)


if __name__ == '__main__':
    unittest.main()
