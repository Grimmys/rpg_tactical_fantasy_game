import unittest

import pygame as pg
import random as rd

import src.fonts as font
from src.entity import Entity
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, TILE_SIZE
from tests.random_data_library import random_pos

NB_TESTS_FOR_PROPORTIONS = 1000


class TestEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestEntity, cls).setUpClass()
        pg.init()
        font.init_fonts()
        # Window parameters
        pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    def test_init_entity(self):
        name = 'entity'
        pos = (3, 2)
        sprite = 'imgs/dungeon_crawl/monster/angel.png'
        entity = Entity(name, pos, sprite)
        self.assertEqual(name, entity.name)
        self.assertEqual(pos, entity.pos)
        self.assertEqual('Entity', str(entity))
        self.assertTrue(entity.is_on_pos(pos))

    def test_name_format(self):
        pos = random_pos()
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
        pos = random_pos()
        entity = Entity(name, pos, sprite)

        self.assertTrue(entity.is_on_pos(pos))
        self.assertTrue(entity.is_on_pos((pos[0] + rd.randint(0, TILE_SIZE), pos[1] + rd.randint(0, TILE_SIZE))))
        self.assertFalse(entity.is_on_pos((pos[0] - rd.randint(0, MAIN_WIN_WIDTH), pos[1])))
        self.assertFalse(entity.is_on_pos((pos[0], pos[1] - rd.randint(0, MAIN_WIN_HEIGHT))))


if __name__ == '__main__':
    unittest.main()
