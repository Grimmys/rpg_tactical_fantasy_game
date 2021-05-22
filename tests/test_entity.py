import unittest

import random as rd

from src.game_entities.entity import Entity
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, TILE_SIZE
from tests.random_data_library import random_position
from tests.tools import minimal_setup_for_game


class TestEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """

        """
        minimal_setup_for_game()

    def test_init_entity(self):
        name = 'entity'
        pos = (3, 2)
        sprite = 'imgs/dungeon_crawl/monster/angel.png'
        entity = Entity(name, pos, sprite)
        self.assertEqual(name, entity.name)
        self.assertEqual(pos, entity.position)
        self.assertEqual('Entity', str(entity))
        self.assertTrue(entity.is_on_pos(pos))

    def test_name_format(self):
        pos = random_position()
        sprite = 'imgs/dungeon_crawl/monster/angel.png'

        name = 'test'
        entity = Entity(name, pos, sprite)
        self.assertEqual('Test', str(entity))

        name = 'Test'
        entity = Entity(name, pos, sprite)
        self.assertEqual('Test', str(entity))

        name = 'entity_test'
        entity = Entity(name, pos, sprite)
        self.assertEqual('Entity Test', str(entity))

        name = '5entity_test_01'
        entity = Entity(name, pos, sprite)
        self.assertEqual('Entity Test', str(entity))

    def test_position(self):
        name = 'test'
        sprite = 'imgs/dungeon_crawl/monster/angel.png'
        pos = random_position()
        entity = Entity(name, pos, sprite)

        self.assertTrue(entity.is_on_pos(pos))
        self.assertTrue(entity.is_on_pos(
            (pos[0] + rd.randrange(0, TILE_SIZE), pos[1] + rd.randrange(0, TILE_SIZE))))
        self.assertFalse(entity.is_on_pos((pos[0] - rd.randrange(0, MAIN_WIN_WIDTH), pos[1])))
        self.assertFalse(entity.is_on_pos((pos[0], pos[1] - rd.randrange(0, MAIN_WIN_HEIGHT))))


if __name__ == '__main__':
    unittest.main()
