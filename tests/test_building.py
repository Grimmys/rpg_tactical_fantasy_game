import unittest

import pygame as pg
import random as rd

import src.fonts as font
import src.loadFromXMLManager as Loader
from src.building import Building
from src.character import Character
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from tests.random_data_library import random_item, random_string, random_building, random_character_entity

NB_TESTS_FOR_PROPORTIONS = 1000


class TestBuilding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestBuilding, cls).setUpClass()
        pg.init()
        font.init_fonts()
        # Window parameters
        pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        # Load some data
        races = Loader.load_races()
        classes = Loader.load_classes()
        Character.init_data(races, classes)

    def test_init_building_no_interaction(self):
        name = 'house'
        pos = (3, 2)
        sprite = 'imgs/houses/blue_house.png'
        house = Building(name, pos, sprite)
        self.assertEqual(name, house.name)
        self.assertEqual(pos, house.pos)
        self.assertEqual('House', str(house))

    def test_init_building_interactive(self):
        name = 'house'
        pos = (3, 2)
        sprite = 'imgs/houses/blue_house.png'
        interaction = {'talks': [random_string(min_len=10, max_len=100), random_string(min_len=10, max_len=100)],
                       'gold': rd.randint(10, 1000),
                       'item': random_item()}
        house = Building(name, pos, sprite, interaction)
        self.assertEqual(name, house.name)
        self.assertEqual(pos, house.pos)
        self.assertEqual(interaction, house.interaction)
        self.assertEqual('House', str(house))

    def test_interact_talks_only(self):
        house = random_building(min_talks=1, gold=False, item=False)
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        entries = house.interact(actor)
        print(entries)
        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before, actor.items)

    def test_interact_gold_reward(self):
        house = random_building(min_gold=10, item=False)
        interaction = house.interaction
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        entries = house.interact(actor)
        print(entries)
        self.assertEqual(actor_gold_before + interaction['gold'], actor.gold)
        self.assertEqual(actor_items_before, actor.items)

    def test_interact_item_reward(self):
        house = random_building(gold=False)
        interaction = house.interaction
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        entries = house.interact(actor)
        print(entries)
        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before + [interaction['item']], actor.items)

    def test_interact_gold_and_item(self):
        house = random_building(min_gold=10)
        interaction = house.interaction
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        entries = house.interact(actor)
        print(entries)
        self.assertEqual(actor_gold_before + interaction['gold'], actor.gold)
        self.assertEqual(actor_items_before + [interaction['item']], actor.items)

    def test_interact_no_interaction(self):
        house = random_building(is_interactive=False)
        actor = random_character_entity()
        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        entries = house.interact(actor)
        print(entries)
        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before, actor.items)

    def test_interact_multiple_times(self):
        house = random_building()
        actor = random_character_entity()
        entries = house.interact(actor)
        print("-- FIRST VISIT --")
        print(entries)

        actor_gold_before = actor.gold
        actor_items_before = actor.items.copy()
        entries = house.interact(actor)
        print("-- SECOND VISIT --")
        print(entries)
        self.assertEqual(actor_gold_before, actor.gold)
        self.assertEqual(actor_items_before, actor.items)


if __name__ == '__main__':
    unittest.main()
