import unittest

from src.game_entities.chest import Chest
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from tests.random_data_library import (random_chest, random_item,
                                       random_item_or_gold)
from tests.tools import NB_TESTS_FOR_PROPORTIONS, minimal_setup_for_game


class TestChest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_chest(self):
        pos = (0, 0)
        sprite_close = "imgs/dungeon_crawl/dungeon/chest_2_closed.png"
        sprite_open = "imgs/dungeon_crawl/dungeon/chest_2_open.png"
        item = Item(
            "TestItem",
            "imgs/dungeon_crawl/item/potion/yellow_new.png",
            "This is a desc",
            50,
        )
        potential_items = [(item, 1.0)]
        chest = Chest(pos, sprite_close, sprite_open, potential_items)
        self.assertEqual(pos, chest.position)
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
        chest = random_chest(gold_proportion=1.0)
        self.assertTrue(isinstance(chest.open(), Gold))

    def test_open_chest_multiple_possibilities(self):
        item_1 = random_item_or_gold()
        item_2 = random_item_or_gold()
        item_3 = random_item_or_gold()
        potential_items = [(item_1, 0.3), (item_2, 0.6), (item_3, 0.1)]
        items = [item_1, item_2, item_3]
        chest = random_chest(item_set=potential_items)
        self.assertTrue(
            isinstance(chest.item, Item)
        )  # Test that there is only one item selected
        self.assertTrue(
            chest.item in items
        )  # Test that this item is one of the eligible

    def test_open_chest_choose_same_probabilities(self):
        item_1 = random_item_or_gold()
        item_2 = random_item_or_gold()
        potential_items = [(item_1, 0.5), (item_2, 0.5)]

        proportion_item_1 = 0.0
        proportion_item_2 = 0.0
        for i in range(NB_TESTS_FOR_PROPORTIONS):
            chest = random_chest(item_set=potential_items)
            if chest.item is item_1:
                proportion_item_1 += 1
            if chest.item is item_2:
                proportion_item_2 += 1
        proportion_item_1 /= NB_TESTS_FOR_PROPORTIONS
        proportion_item_2 /= NB_TESTS_FOR_PROPORTIONS

        self.assertAlmostEqual(proportion_item_1, 0.5, delta=0.1)
        self.assertAlmostEqual(proportion_item_2, 0.5, delta=0.1)

    def test_open_chest_choose_diff_probabilities(self):
        item_1 = random_item_or_gold()
        item_2 = random_item_or_gold()
        item_3 = random_item_or_gold()
        potential_items = [(item_1, 0.3), (item_2, 0.6), (item_3, 0.1)]

        proportion_item_1 = 0.0
        proportion_item_2 = 0.0
        proportion_item_3 = 0.0
        for i in range(NB_TESTS_FOR_PROPORTIONS):
            chest = random_chest(item_set=potential_items)
            if chest.item is item_1:
                proportion_item_1 += 1
            if chest.item is item_2:
                proportion_item_2 += 1
            if chest.item is item_3:
                proportion_item_3 += 1
        proportion_item_1 /= NB_TESTS_FOR_PROPORTIONS
        proportion_item_2 /= NB_TESTS_FOR_PROPORTIONS
        proportion_item_3 /= NB_TESTS_FOR_PROPORTIONS

        self.assertAlmostEqual(proportion_item_1, 0.3, delta=0.05)
        self.assertAlmostEqual(proportion_item_2, 0.6, delta=0.05)
        self.assertAlmostEqual(proportion_item_3, 0.1, delta=0.05)

    def test_open_chest_twice(self):
        chest = random_chest()
        chest.open()
        self.assertFalse(chest.open())


if __name__ == "__main__":
    unittest.main()
