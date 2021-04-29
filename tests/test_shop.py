import unittest

import random as rd

from src.game_entities.shop import Shop
from tests.random_data_library import random_item, random_character_entity
from tests.tools import minimal_setup_for_game

NB_TESTS_FOR_PROPORTIONS = 1000


class TestShop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_shop(self):
        name = 'tavern'
        pos = (3, 2)
        sprite = 'imgs/houses/blue_house.bmp'
        interaction = None
        items = [{'item': random_item(), 'quantity': rd.randint(1, 10)},
                 {'item': random_item(), 'quantity': rd.randint(1, 10)}]
        shop = Shop(name, pos, sprite, interaction, items)
        self.assertEqual(name, shop.name)
        self.assertEqual(pos, shop.pos)
        self.assertEqual('Tavern', str(shop))
        self.assertTrue(items[0] in shop.stock)
        self.assertTrue(items[1] in shop.stock)

    def test_interact(self):
        name = 'tavern'
        pos = (3, 2)
        sprite = 'imgs/houses/blue_house.bmp'
        interaction = None
        items = [{'item': random_item(), 'quantity': rd.randint(1, 10)},
                 {'item': random_item(), 'quantity': rd.randint(1, 10)}]
        shop = Shop(name, pos, sprite, interaction, items)
        actor = random_character_entity()
        entries = shop.interact(actor)
        print(entries)
        # No assert for the moment

    def test_buy_item(self):
        pass

    def test_buy_all_items(self):
        pass

    def test_sell_item(self):
        pass


if __name__ == '__main__':
    unittest.main()
