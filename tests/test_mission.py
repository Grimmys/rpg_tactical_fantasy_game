import unittest
import random as rd

from src.constants import TILE_SIZE
from src.game_entities.foe import Foe
from src.game_entities.mission import Mission, MissionType
from tests.random_data_library import random_item, random_position, random_player_entity, random_entities
from tests.tools import minimal_setup_for_game


class TestMission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """

        """
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
        mission = Mission(is_main, nature, positions, description, nb_players,
                          turn_limit, gold_reward, items_reward)
        self.assertEqual(is_main, mission.main)
        self.assertEqual(nature, mission.type)
        self.assertEqual(positions, mission.positions)
        self.assertEqual(description, mission.description)
        self.assertFalse(mission.ended)
        self.assertEqual(turn_limit, mission.turn_limit)
        self.assertEqual(gold_reward, mission.gold)
        self.assertEqual(items_reward, mission.items)
        self.assertEqual(nb_players, mission.min_chars)
        self.assertEqual(0, len(mission.succeeded_chars))

    def test_position_is_valid_to_go(self):
        nature = MissionType.POSITION
        positions = [(1 * TILE_SIZE, 0 * TILE_SIZE), (3 * TILE_SIZE, 2 * TILE_SIZE)]
        mission = Mission(True, nature, positions, 'Test mission', 0)
        self.assertTrue(mission.is_position_valid(positions[0]))
        self.assertTrue(mission.is_position_valid(positions[1]))
        invalid_position = random_position()
        while invalid_position in positions:
            invalid_position = random_position()
        self.assertFalse(mission.is_position_valid(random_position))

    def test_position_is_valid_to_touch(self):
        nature = MissionType.TOUCH_POSITION
        positions = [(1 * TILE_SIZE, 0 * TILE_SIZE), (3 * TILE_SIZE, 2 * TILE_SIZE)]
        mission = Mission(True, nature, positions, 'Test mission', 0)
        self.assertFalse(mission.is_position_valid(positions[0]))
        self.assertFalse(mission.is_position_valid(positions[1]))

        first_position = positions[0]
        self.assertTrue(mission.is_position_valid((first_position[0] + TILE_SIZE, first_position[1])))
        self.assertTrue(mission.is_position_valid((first_position[0], first_position[1] + TILE_SIZE)))
        self.assertTrue(mission.is_position_valid((first_position[0] - TILE_SIZE, first_position[1])))
        self.assertTrue(mission.is_position_valid((first_position[0], first_position[1] - TILE_SIZE)))

        second_position = positions[1]
        self.assertTrue(mission.is_position_valid((second_position[0] + TILE_SIZE, second_position[1])))

    def test_update_state_position_objective(self):
        nature = rd.choice([MissionType.POSITION, MissionType.TOUCH_POSITION])
        position = [random_position()]
        players = [random_player_entity(), random_player_entity()]
        mission = Mission(True, nature, position, 'Test mission', 2)

        self.assertTrue(mission.update_state(players[0]))
        self.assertFalse(mission.ended)
        self.assertEqual(players[0], mission.succeeded_chars[0])

        self.assertTrue(mission.update_state(players[1]))
        self.assertTrue(mission.ended)
        self.assertEqual(players, mission.succeeded_chars)

    def test_update_state_kill_everybody_objective(self):
        nature = MissionType.KILL_EVERYBODY
        mission = Mission(True, nature, [], 'Test mission', 0)
        foes = random_entities(Foe, min=2)
        entities = {'foes': foes}

        self.assertTrue(mission.update_state(entities=entities))
        self.assertFalse(mission.ended)

        foes.pop()

        self.assertTrue(mission.update_state(entities=entities))
        self.assertFalse(mission.ended)

        while len(foes) != 0:
            foes.pop()

        self.assertTrue(mission.update_state(entities=entities))
        self.assertTrue(mission.ended)

    def test_update_state_objective_with_turn_limit(self):
        nature = MissionType.TURN_LIMIT
        turn_limit = rd.randint(1, 10)
        mission = Mission(True, nature, [], 'Test mission', 0, turn_limit=turn_limit)

        self.assertTrue(mission.update_state(turns=0))
        self.assertTrue(mission.ended)
        self.assertTrue(mission.update_state(turns=turn_limit))
        self.assertTrue(mission.ended)
        self.assertTrue(mission.update_state(turns=turn_limit+1))
        self.assertFalse(mission.ended)

