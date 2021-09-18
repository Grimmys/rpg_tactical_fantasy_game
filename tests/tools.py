import pygame
import pygamepopup

import src.services.load_from_xml_manager as loader
import src.gui.fonts as font
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from src.game_entities.character import Character

NB_TESTS_FOR_PROPORTIONS = 1000

already_set_up = False


def minimal_setup_for_game():
    global already_set_up
    if already_set_up:
        return
    pygame.init()
    pygamepopup.init()
    font.init_fonts()
    # Window parameters
    pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
    # Load some data
    races = loader.load_races()
    classes = loader.load_classes()
    Character.init_data(races, classes)
    already_set_up = True
