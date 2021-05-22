import pygame as pg
import src.services.load_from_xml_manager as Loader
import src.gui.fonts as font
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from src.game_entities.character import Character

NB_TESTS_FOR_PROPORTIONS = 1000


def minimal_setup_for_game():
    """

    """
    pg.init()
    font.init_fonts()
    # Window parameters
    pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
    # Load some data
    races = Loader.load_races()
    classes = Loader.load_classes()
    Character.init_data(races, classes)
