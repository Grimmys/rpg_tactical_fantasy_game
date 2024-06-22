import unittest

from src.gui.animation import *
from tests.tools import minimal_setup_for_game
from typing import Optional
from src.gui.constant_sprites import constant_sprites


class TestAnimate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_animation(self):
        self.animation: Optional[Animation] = None
        self.animation = Animation(
            [Frame(constant_sprites["new_turn"], constant_sprites["new_turn_pos"])],
            60,
        )
        self.assertFalse(self.animation.animate())
        self.animation.timer = 1
        self.assertTrue(self.animation.animate())