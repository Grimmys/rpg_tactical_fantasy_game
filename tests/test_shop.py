import random as rd
import unittest

from src.game_entities.shop import Shop
from tests.random_data_library import random_item, random_character_entity
from tests.tools import minimal_setup_for_game


class TestShop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_shop(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        interaction = None
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, items, interaction)
        self.assertEqual(name, shop.name)
        self.assertEqual(pos, shop.position)
        self.assertEqual("Tavern", str(shop))
        self.assertTrue(items[0] in shop.stock)
        self.assertTrue(items[1] in shop.stock)

    def test_interact(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        interaction = None
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, items, interaction)
        actor = random_character_entity()
        shop.interact(actor)
        # No assert for the moment

    @unittest.skip
    def test_buy_item(self):
        pass

    @unittest.skip
    def test_buy_all_items(self):
        pass

    @unittest.skip
    def test_sell_item(self):
        pass


if __name__ == "__main__":
    unittest.main()
