import random as rd
import unittest

from src.constants import TILE_SIZE
from src.game_entities.foe import Foe
from src.game_entities.mission import Mission, MissionType
from src.gui.position import Position
from src.scenes.level_scene import LevelEntityCollections
from tests.random_data_library import (random_entities, random_foe_entity,
                                       random_item, random_objective,
                                       random_player_entity, random_position)
from tests.tools import minimal_setup_for_game


class TestMission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_mission(self):
        is_main = True
        nature = MissionType.POSITION
        objectives = [random_objective(), random_objective()]
        description = "Test main mission"
        nb_players = 2
        turn_limit = 10
        gold_reward = 200
        items_reward = [random_item()]
        mission = Mission(
            is_main,
            nature,
            objectives,
            description,
            nb_players,
            turn_limit,
            gold_reward,
            items_reward,
        )
        self.assertEqual(is_main, mission.main)
        self.assertEqual(nature, mission.type)
        self.assertEqual(objectives, mission.objective_tiles)
        self.assertEqual(description, mission.description)
        self.assertFalse(mission.ended)
        self.assertEqual(turn_limit, mission.turn_limit)
        self.assertEqual(gold_reward, mission.gold)
        self.assertEqual(items_reward, mission.items)
        self.assertEqual(nb_players, mission.min_chars)
        self.assertEqual(0, len(mission.succeeded_chars))

    def test_position_is_valid_to_go(self):
        nature = MissionType.POSITION
        objectives = [
            random_objective(position=Position(1 * TILE_SIZE, 0 * TILE_SIZE)),
            random_objective(position=Position(3 * TILE_SIZE, 2 * TILE_SIZE)),
        ]
        mission = Mission(True, nature, objectives, "Test mission", 0)
        self.assertTrue(mission.is_position_valid(objectives[0].position))
        self.assertTrue(mission.is_position_valid(objectives[1].position))
        invalid_position = random_position()
        while invalid_position in map(lambda objective: objective.position, objectives):
            invalid_position = random_position()
        self.assertFalse(mission.is_position_valid(invalid_position))

    def test_position_is_valid_to_touch(self):
        nature = MissionType.TOUCH_POSITION
        objectives = [
            random_objective(position=Position(1 * TILE_SIZE, 0 * TILE_SIZE)),
            random_objective(position=Position(3 * TILE_SIZE, 2 * TILE_SIZE)),
        ]
        mission = Mission(True, nature, objectives, "Test mission", 0)
        self.assertFalse(mission.is_position_valid(objectives[0].position))
        self.assertFalse(mission.is_position_valid(objectives[1].position))

        first_position = objectives[0].position
        self.assertTrue(
            mission.is_position_valid(
                Position(first_position[0] + TILE_SIZE, first_position[1])
            )
        )
        self.assertTrue(
            mission.is_position_valid(
                Position(first_position[0], first_position[1] + TILE_SIZE)
            )
        )
        self.assertTrue(
            mission.is_position_valid(
                Position(first_position[0] - TILE_SIZE, first_position[1])
            )
        )
        self.assertTrue(
            mission.is_position_valid(
                Position(first_position[0], first_position[1] - TILE_SIZE)
            )
        )

        second_position = objectives[1].position
        self.assertTrue(
            mission.is_position_valid(
                Position(second_position[0] + TILE_SIZE, second_position[1])
            )
        )

    def test_update_state_position_objective(self):
        nature = rd.choice([MissionType.POSITION, MissionType.TOUCH_POSITION])
        objective = [random_objective()]
        players = [random_player_entity(), random_player_entity()]
        mission = Mission(True, nature, objective, "Test mission", 2)

        mission.update_state(players[0])
        self.assertFalse(mission.ended)
        self.assertEqual(players[0], mission.succeeded_chars[0])

        mission.update_state(players[1])
        self.assertTrue(mission.ended)
        self.assertEqual(players, mission.succeeded_chars)

    def test_update_state_kill_everybody_objective(self):
        nature = MissionType.KILL_EVERYBODY
        mission = Mission(True, nature, [], "Test mission", 0)
        foes = random_entities(Foe, min_number=2)
        entities = LevelEntityCollections()
        entities.foes = foes

        mission.update_state(entities=entities)
        self.assertFalse(mission.ended)

        foes.pop()

        mission.update_state(entities=entities)
        self.assertFalse(mission.ended)

        while len(foes) != 0:
            foes.pop()

        mission.update_state(entities=entities)
        self.assertTrue(mission.ended)

    def test_update_state_objective_with_turn_limit(self):
        nature = MissionType.TURN_LIMIT
        turn_limit = rd.randint(1, 10)
        mission = Mission(True, nature, [], "Test mission", 0, turn_limit=turn_limit)

        mission.update_state(turns=0)
        self.assertTrue(mission.ended)

        mission.update_state(turns=turn_limit)
        self.assertTrue(mission.ended)

        mission.update_state(turns=turn_limit + 1)
        self.assertFalse(mission.ended)

    def test_update_state_kill_target_objective(self):
        nature = MissionType.KILL_TARGETS
        target = random_foe_entity()
        mission = Mission(True, nature, [], "Test mission", 0, targets=[target])

        mission.update_state()
        self.assertFalse(mission.ended)

        target.hit_points -= target.hit_points_max // 2

        mission.update_state()
        self.assertFalse(mission.ended)

        target.hit_points = 0

        mission.update_state()
        self.assertTrue(mission.ended)

    def test_update_state_kill_multiple_targets_objective(self):
        nature = MissionType.KILL_TARGETS
        targets = random_entities(Foe, min_number=2)
        mission = Mission(True, nature, [], "Test mission", 0, targets=targets)

        mission.update_state()
        self.assertFalse(mission.ended)

        targets[0].hit_points = 0

        mission.update_state()
        self.assertFalse(mission.ended)

        for foe in targets:
            foe.hit_points = 0

        mission.update_state()
        self.assertTrue(mission.ended)
