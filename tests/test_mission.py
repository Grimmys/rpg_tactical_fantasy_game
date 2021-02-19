import unittest

from src.constants import TILE_SIZE
from src.game_entities.mission import Mission, MissionType
from tests.random_data_library import random_item, random_position
from tests.tools import minimal_setup_for_game


class TestMission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_mision(self):
        is_main = True
        nature = MissionType.POSITION
        positions = [(1 * TILE_SIZE, 2 * TILE_SIZE), (3 * TILE_SIZE, 4 * TILE_SIZE)]
        description = 'Test main mission'
        nb_players = 2
        turn_limit = 10
        gold_reward = 200
        items_reward = [random_item()]
        mission = Mission(is_main, nature, positions, description, nb_players, turn_limit, gold_reward, items_reward)
        self.assertEqual(is_main, mission.main)
        self.assertEqual(nature, mission.type)
        self.assertEqual(positions, mission.positions)
        self.assertEqual(description, mission.desc)
        self.assertFalse(mission.ended)
        self.assertEqual(turn_limit, mission.turn_limit)
        self.assertEqual(gold_reward, mission.gold)
        self.assertEqual(items_reward, mission.items)
        self.assertEqual(nb_players, mission.min_chars)
        self.assertEqual(0, len(mission.succeeded_chars))

    def test_position_is_valid_to_go(self):
        nature = MissionType.POSITION
        positions = [(1 * TILE_SIZE, 0 * TILE_SIZE), (3 * TILE_SIZE, 2 * TILE_SIZE)]
        mission = Mission(True, nature, positions, 'Test mission', 0, 0)
        self.assertTrue(mission.pos_is_valid(positions[0]))
        self.assertTrue(mission.pos_is_valid(positions[1]))
        self.assertFalse(mission.pos_is_valid(random_position()))

    def test_position_is_valid_to_touch(self):
        nature = MissionType.TOUCH_POSITION
        positions = [(1 * TILE_SIZE, 0 * TILE_SIZE), (3 * TILE_SIZE, 2 * TILE_SIZE)]
        mission = Mission(True, nature, positions, 'Test mission', 0, 0)
        self.assertFalse(mission.pos_is_valid(positions[0]))
        self.assertFalse(mission.pos_is_valid(positions[1]))

        first_position = positions[0]
        self.assertTrue(mission.pos_is_valid((first_position[0] + TILE_SIZE, first_position[1])))
        self.assertTrue(mission.pos_is_valid((first_position[0], first_position[1] + TILE_SIZE)))
        self.assertTrue(mission.pos_is_valid((first_position[0] - TILE_SIZE, first_position[1])))
        self.assertTrue(mission.pos_is_valid((first_position[0], first_position[1] - TILE_SIZE)))

        second_position = positions[1]
        self.assertTrue(mission.pos_is_valid((second_position[0] + TILE_SIZE, second_position[1])))