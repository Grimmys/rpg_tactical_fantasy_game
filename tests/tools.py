import pygame
import pygamepopup

import src.gui.fonts as font
import src.services.load_from_xml_manager as loader
from src.constants import MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH
from src.game_entities.character import Character
from src.gui.constant_sprites import init_constant_sprites

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
    init_constant_sprites()
    already_set_up = True
