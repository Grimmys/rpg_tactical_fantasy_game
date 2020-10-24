import os
import unittest

import pygame as pg

import src.fonts as font
from src.Chest import Chest
from src.Item import Item
from src.StartScreen import StartScreen
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from tests.random_data_library import random_chest, random_item


class TestChest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.chdir(os.getcwd() + '/..')
        pg.init()
        font.init_fonts()

    def setUp(self):
        # Window parameters
        screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        self.start_screen = StartScreen(screen)
        self.start_screen.display()

    def test_init_chest(self):
        pos = (0, 0)
        sprite_close = 'imgs/dungeon_crawl/dungeon/chest_2_closed.png'
        sprite_open = 'imgs/dungeon_crawl/dungeon/chest_2_open.png'
        item = Item("TestItem", 'imgs/dungeon_crawl/item/potion/yellow_new.png', "This is a desc", 50)
        potential_items = [(item, 1.0)]
        chest = Chest(pos, sprite_close, sprite_open, potential_items)
        self.assertEqual(pos, chest.pos)
        self.assertEqual(sprite_close, chest.sprite_close_link)
        self.assertEqual(sprite_open, chest.sprite_open_link)
        self.assertEqual(chest.item, item)
        self.assertFalse(chest.opened)
        self.assertFalse(chest.pick_lock_initiated)
        # Chest's current sprite should be the closed one
        self.assertNotEqual(chest.sprite_open, chest.sprite)

    def test_open_chest(self):
        chest = random_chest()
        self.assertFalse(chest.opened)
        chest.open()
        self.assertTrue(chest.opened)

    def test_open_chest_item(self):
        item = random_item()
        potential_items = [(item, 1.0)]
        chest = random_chest(item_set=potential_items)
        self.assertEqual(item, chest.open())

    def test_open_chest_gold(self):
        pass

    def test_open_chest_choose_two_items(self):
        pass

    def test_open_chest_choose_diff_probabilities(self):
        pass


if __name__ == '__main__':
    unittest.main()
