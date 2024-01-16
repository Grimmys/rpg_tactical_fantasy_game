import unittest

from src.game_entities.item import Item
from tests.random_data_library import random_item
from tests.tools import NB_TESTS_FOR_PROPORTIONS, minimal_setup_for_game


class TestItem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_item(self):
        name = "life_potion"
        sprite = "imgs/dungeon_crawl/item/potion/magenta_new.png"
        description = "This is a test description"
        item = Item(name, sprite, description)
        self.assertEqual(name, item.name)
        self.assertEqual(description, item.description)
        self.assertEqual("Life Potion", str(item))

    def test_init_item_with_price(self):
        name = "life_potion"
        sprite = "imgs/dungeon_crawl/item/potion/magenta_new.png"
        description = "This is a test description"
        price = 200
        item = Item(name, sprite, description, price)
        self.assertEqual(name, item.name)
        self.assertEqual(description, item.description)
        self.assertEqual("Life Potion", str(item))
        self.assertEqual(price, item.price)
        self.assertEqual(price // 2, item.resell_price)

    def test_name_format(self):
        sprite = "imgs/dungeon_crawl/item/potion/magenta_new.png"
        description = "This is a test description"

        name = "test"
        item = Item(name, sprite, description)
        self.assertEqual("Test", str(item))

        name = "Test"
        item = Item(name, sprite, description)
        self.assertEqual("Test", str(item))

        name = "item_test"
        item = Item(name, sprite, description)
        self.assertEqual("Item Test", str(item))

        name = "5item_test_01"
        item = Item(name, sprite, description)
        self.assertEqual("5Item Test 01", str(item))

    def test_id_uniqueness(self):
        items = []
        for _ in range(NB_TESTS_FOR_PROPORTIONS):
            items.append(random_item())

        self.assertTrue(
            len(set(map(lambda it: it.identifier, items))), NB_TESTS_FOR_PROPORTIONS
        )


if __name__ == "__main__":
    unittest.main()
