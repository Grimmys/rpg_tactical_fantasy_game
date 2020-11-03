import unittest

import pygame as pg

import src.fonts as font
import src.LoadFromXMLManager as Loader
from src.Character import Character
from src.Shop import Shop
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from tests.random_data_library import random_item, random_character_entity

NB_TESTS_FOR_PROPORTIONS = 1000


class TestShop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestShop, cls).setUpClass()
        pg.init()
        font.init_fonts()
        # Window parameters
        pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        # Load some data
        races = Loader.load_races()
        classes = Loader.load_classes()
        Character.init_data(races, classes)

    def test_init_shop(self):
        name = 'tavern'
        pos = (3, 2)
        sprite = 'imgs/houses/blue_house.png'
        interaction = None
        items = [random_item(), random_item()]
        shop = Shop(name, pos, sprite, interaction, items)
        self.assertEqual(name, shop.name)
        self.assertEqual(pos, shop.pos)
        self.assertEqual('Tavern', str(shop))
        self.assertTrue(items[0] in shop.items)
        self.assertTrue(items[1] in shop.items)

    def test_interact(self):
        name = 'tavern'
        pos = (3, 2)
        sprite = 'imgs/houses/blue_house.png'
        interaction = None
        items = [random_item(), random_item()]
        shop = Shop(name, pos, sprite, interaction, items)
        actor = random_character_entity()
        entries = shop.interact(actor)
        print(entries)
        # No assert for the moment

if __name__ == '__main__':
    unittest.main()
