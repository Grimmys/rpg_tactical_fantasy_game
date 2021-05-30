import unittest

from src.game_entities.alteration import Alteration
from tests.random_data_library import random_alteration
from tests.tools import minimal_setup_for_game


class TestAlteration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_alteration(self):
        name = "test_alteration"
        abbr = "ta"
        power = 3
        duration = 2
        description = "This is a test description"
        specificites = ["no_attack", "defense_up"]
        alteration = Alteration(name, abbr, power, duration, description, specificites)
        self.assertEqual(name, alteration.name)
        self.assertEqual("Test alteration", str(alteration))
        self.assertEqual(abbr, alteration.abbreviated_name)
        self.assertEqual(power, alteration.power)
        self.assertEqual(duration, alteration.duration)
        self.assertEqual(description, alteration.description)
        self.assertEqual(specificites, alteration.specificities)
        self.assertFalse(alteration.is_finished())

    def test_alteration_not_ended(self):
        alteration = random_alteration(min_duration=2)

        self.assertEqual(alteration.duration, alteration.get_turns_left())
        self.assertFalse(alteration.is_finished())
        alteration.increment()
        self.assertEqual(alteration.duration - 1, alteration.get_turns_left())
        self.assertFalse(alteration.is_finished())

    def test_alteration_end(self):
        alteration = random_alteration()

        self.assertEqual(alteration.duration, alteration.get_turns_left())
        self.assertFalse(alteration.is_finished())
        for i in range(alteration.duration):
            alteration.increment()
        self.assertEqual(0, alteration.get_turns_left())
        self.assertTrue(alteration.is_finished())
