import unittest

from src.services.load_from_tmx_manager import *
from tests.tools import minimal_setup_for_game
from src.scenes.level_scene import *
from src.scenes.start_scene import *


class TestSaveAndLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_load_buildings(self):
        level_screen = StartScene.generate_level_window()
        level = 0

        lvScene = LevelScene(level_screen, "maps/level_" + str(level) + "/", level)
        lvScene.load_level_content()
        self.assertNotEqual(0, len(lvScene.entities.buildings))