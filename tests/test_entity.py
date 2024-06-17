import random
import unittest

from src.constants import MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH, TILE_SIZE
from src.game_entities.entity import Entity
from src.gui.position import Position
from tests.random_data_library import random_position
from tests.tools import minimal_setup_for_game


class TestEntity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_entity(self):
        name = "entity"
        position = Position(3, 2)
        sprite = "imgs/dungeon_crawl/monster/angel.png"
        entity = Entity(name, position, sprite)
        self.assertEqual(name, entity.name)
        self.assertEqual(position, entity.position)
        self.assertEqual("Entity", str(entity))
        self.assertTrue(entity.is_on_position(position))

    def test_name_format(self):
        position = random_position()
        sprite = "imgs/dungeon_crawl/monster/angel.png"

        name = "test"
        entity = Entity(name, position, sprite)
        self.assertEqual("Test", str(entity))

        name = "Test"
        entity = Entity(name, position, sprite)
        self.assertEqual("Test", str(entity))

        name = "entity_test"
        entity = Entity(name, position, sprite)
        self.assertEqual("Entity Test", str(entity))

        name = "5entity_test_01"
        entity = Entity(name, position, sprite)
        self.assertEqual("Entity Test", str(entity))

    def test_position(self):
        name = "test"
        sprite = "imgs/dungeon_crawl/monster/angel.png"
        position = random_position()
        entity = Entity(name, position, sprite)

        self.assertTrue(entity.is_on_position(position))
        self.assertTrue(
            entity.is_on_position(
                Position(
                    position[0] + random.randrange(0, TILE_SIZE),
                    position[1] + random.randrange(0, TILE_SIZE),
                )
            )
        )
        self.assertFalse(
            entity.is_on_position(
                Position(position[0] - random.randrange(0, MAIN_WIN_WIDTH), position[1])
            )
        )
        self.assertFalse(
            entity.is_on_position(
                Position(position[0], position[1] - random.randrange(0, MAIN_WIN_HEIGHT))
            )
        )


if __name__ == "__main__":
    unittest.main()
