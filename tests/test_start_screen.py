import os
import unittest

import pygame as pg
from pygame.rect import Rect
from random import randrange

from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT

NEW_GAME_BUTTON_POS = (325, 341)
LOAD_GAME_BUTTON_POS = (325, 381)
OPTIONS_BUTTON_POS = (325, 421)
EXIT_GAME_BUTTON_POS = (325, 461)
BUTTON_SIZE = (150, 30)

LEFT_BUTTON = 1
MIDDLE_BUTTON = 2
RIGHT_BUTTON = 3

os.chdir(os.getcwd() + '/..')


class TestStartScreen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init()
        cls.buttons = []
        cls.buttons.append(Rect(NEW_GAME_BUTTON_POS[0], NEW_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        cls.buttons.append(Rect(LOAD_GAME_BUTTON_POS[0], LOAD_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        cls.buttons.append(Rect(OPTIONS_BUTTON_POS[0], NEW_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))
        cls.buttons.append(Rect(EXIT_GAME_BUTTON_POS[0], NEW_GAME_BUTTON_POS[1], BUTTON_SIZE[0], BUTTON_SIZE[1]))

    def setUp(self):
        # Window parameters
        screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

        from src.Level import Level
        self.level_class = Level

        from src.StartScreen import StartScreen

        self.start_screen = StartScreen(screen)
        self.start_screen.display()

    def test_new_game(self):
        # Memorize old screen
        screen = self.start_screen.screen.copy()

        # Verify no game is actually launched
        self.assertIsNone(self.start_screen.level)
        self.assertIsNone(self.start_screen.level_id)

        # Generate random pos on new game button
        pos = (randrange(NEW_GAME_BUTTON_POS[0], NEW_GAME_BUTTON_POS[0] + BUTTON_SIZE[0] + 1),
               randrange(NEW_GAME_BUTTON_POS[1], NEW_GAME_BUTTON_POS[1] + BUTTON_SIZE[1] + 1))
        self.start_screen.click(LEFT_BUTTON, pos)

        self.assertIsInstance(self.start_screen.level, self.level_class)
        self.assertEqual(self.start_screen.level_id, 0)
        self.assertNotEqual(self.start_screen.screen.get_rect(), screen.get_rect())

    def test_load_nonexistent_save(self):
        # TODO
        pass

    def test_load_existent_save(self):
        # TODO
        pass

    def test_options_menu(self):
        # TODO
        pass

    def test_exit_game(self):
        # Generate random pos on exit game button
        pos = (randrange(EXIT_GAME_BUTTON_POS[0], EXIT_GAME_BUTTON_POS[0] + BUTTON_SIZE[0] + 1),
               randrange(EXIT_GAME_BUTTON_POS[1], EXIT_GAME_BUTTON_POS[1] + BUTTON_SIZE[1] + 1))

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

        self.start_screen.click(LEFT_BUTTON, pos)

        # Verify state is unchanged
        self.assertEqual(self.start_screen.screen.get_rect(), screen.get_rect())
        self.assertEqual(self.start_screen.level, old_level)
        self.assertEqual(self.start_screen.level_id, old_level_id)
        self.assertEqual(self.start_screen.active_menu, old_active_menu)

    def test_right_click(self):
        # TODO
        pass


if __name__ == '__main__':
    unittest.main()
