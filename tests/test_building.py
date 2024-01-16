import random as rd
import unittest

from src.game_entities.building import Building
from tests.random_data_library import (random_building,
                                       random_character_entity, random_item,
                                       random_string)
from tests.tools import minimal_setup_for_game


class TestBuilding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_building_empty_interaction(self):
        name = "house"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        interaction = {}
        house = Building(name, pos, sprite, interaction)

        self.assertEqual(name, house.name)
        self.assertEqual(pos, house.position)
        self.assertEqual("House", str(house))

    def test_init_building_interactive(self):
        name = "house"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        interaction = {
            "talks": [
                random_string(min_len=10, max_len=100),
                random_string(min_len=10, max_len=100),
            ],
            "gold": rd.randint(10, 1000),
            "item": random_item(),
        }
        house = Building(name, pos, sprite, interaction)

        self.assertEqual(name, house.name)
        self.assertEqual(pos, house.position)
        self.assertEqual(interaction, house.interaction)
        self.assertEqual("House", str(house))

    def test_interact_talks_only(self):
        house = random_building(min_talks=1, gold=False, item=False)
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        house.interact(actor)

        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before, actor.items)

    def test_interact_gold_reward(self):
        house = random_building(min_gold=10, item=False)
        interaction = house.interaction
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        house.interact(actor)

        self.assertEqual(actor_gold_before + interaction["gold"], actor.gold)
        self.assertEqual(actor_items_before, actor.items)

    def test_interact_item_reward(self):
        house = random_building(gold=False)
        interaction = house.interaction
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        house.interact(actor)

        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before + [interaction["item"]], actor.items)

    def test_interact_gold_and_item(self):
        house = random_building(min_gold=10)
        interaction = house.interaction
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        house.interact(actor)

        self.assertEqual(actor_gold_before + interaction["gold"], actor.gold)
        self.assertEqual(actor_items_before + [interaction["item"]], actor.items)

    def test_interact_no_interaction(self):
        house = random_building(is_interactive=False)
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        house.interact(actor)

        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before, actor.items)

    def test_interact_multiple_times(self):
        house = random_building()
        actor = random_character_entity()
        house.interact(actor)

        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        house.interact(actor)

        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before, actor.items)


if __name__ == "__main__":
    unittest.main()
