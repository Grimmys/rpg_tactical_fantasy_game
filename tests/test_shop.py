import random as rd
import unittest

from src.game_entities.shop import Shop
from tests.random_data_library import random_character_entity, random_item
from tests.tools import minimal_setup_for_game
from src.services.language import *


class TestShop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_shop(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        interaction = None
        shop_balance = 500
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, shop_balance, items, interaction)
        self.assertEqual(name, shop.name)
        self.assertEqual(pos, shop.position)
        self.assertEqual("Tavern", str(shop))
        self.assertEqual(shop_balance, shop.shop_balance)
        self.assertTrue(items[0] in shop.stock)
        self.assertTrue(items[1] in shop.stock)

    def test_interact(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        shop_balance = 500
        interaction = None
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, shop_balance, items, interaction)
        actor = random_character_entity()
        shop.interact(actor)
        # No assert for the moment

    def test_buy_item(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        shop_balance = 500
        interaction = None
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, shop_balance, items, interaction)
        actor = random_character_entity()
        actor.gold = 10000
        shop.interact(actor)
        self.assertEqual(STR_THE_ITEM_HAS_BEEN_BOUGHT, shop.buy(items[0]["item"]))
        actor.nb_items_max = len(actor.items)
        self.assertEqual(STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM, shop.buy(items[0]["item"]))
        actor.nb_items_max = len(actor.items) + 1
        actor.gold = 0
        self.assertEqual(STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM, shop.buy(items[0]["item"]))


    @unittest.skip
    def test_buy_all_items(self):
        pass

    @unittest.skip
    def test_sell_item(self):
        pass


if __name__ == "__main__":
    unittest.main()
