import shutil
import unittest

import pygame as pg

import src.fonts as font
import src.loadFromXMLManager as Loader
from src.character import Character
from src.startScreen import StartScreen
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, TILE_SIZE
from tests.test_start_screen import LOAD_GAME_BUTTON_POS, LEFT_BUTTON

NB_TESTS_FOR_PROPORTIONS = 1000


class TestLevel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestLevel, cls).setUpClass()
        cls.save_url = "saves/main_save.xml"
        pg.init()
        font.init_fonts()
        # Window parameters
        screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        cls.start_screen = StartScreen(screen)
        cls.start_screen.display()
        # Load some data
        races = Loader.load_races()
        classes = Loader.load_classes()
        Character.init_data(races, classes)

    def test_distance_between_two_entities(self):
        # Import simple save file
        shutil.copyfile("tests/test_saves/simple_save.xml", self.save_url)
        self.start_screen.click(LEFT_BUTTON, LOAD_GAME_BUTTON_POS)

        level = self.start_screen.level
        players = level.players
        foe = level.entities['foes'][0]
        entities_with_dist = level.distance_between_all(foe, players)

        self.assertEqual(5, entities_with_dist[players[0]])

    def test_distance_between_many_entities(self):
        # Import complete save file
        shutil.copyfile("tests/test_saves/complete_first_level_save.xml", self.save_url)
        self.start_screen.click(LEFT_BUTTON, LOAD_GAME_BUTTON_POS)

        level = self.start_screen.level
        players = level.players
        foes = level.entities['foes']

        raimund = None
        braern = None
        thokdrum = None
        for p in players:
            pos = (p.pos[0] // TILE_SIZE, p.pos[1] // TILE_SIZE)
            if pos == (17, 10):
                raimund = p
            elif pos == (16, 9):
                braern = p
            elif pos == (16, 10):
                thokdrum = p

        specific_skeleton = None
        specific_necrophage = None
        for f in foes:
            pos = (f.pos[0] // TILE_SIZE, f.pos[1] // TILE_SIZE)
            if pos == (12, 8):
                specific_skeleton = f
            if pos == (13, 5):
                specific_necrophage = f

        entities_with_dist = level.distance_between_all(specific_skeleton, players)
        self.assertEqual(12, entities_with_dist[raimund])
        self.assertEqual(4, entities_with_dist[braern])
        self.assertEqual(5, entities_with_dist[thokdrum])

        entities_with_dist = level.distance_between_all(specific_necrophage, players)
        self.assertEqual(8, entities_with_dist[raimund])
        self.assertEqual(6, entities_with_dist[braern])
        self.assertEqual(7, entities_with_dist[thokdrum])


if __name__ == '__main__':
    unittest.main()
