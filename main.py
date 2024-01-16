#!/usr/bin/env python3

"""
The entry point of the game.
Initiate pygame, load game generic data & fonts, initiate pygame window
and let the main loop running.
The pygame events are caught here and delegated to the start screen.
"""

import pygame
import pygamepopup

from src.gui.tools import show_fps
from src.services.scene_manager import QuitActionKind, SceneManager


def main_loop(
    game_controller: SceneManager, screen: pygame.Surface, clock: pygame.time.Clock
) -> QuitActionKind:
    """
    Run the game until a quit request happened.
    Pygame events are catch and delegated to the scene manager.
    The state and display of the active scene are updated at each iteration.

    Keyword arguments:
    controller -- the scene manager acting as the main controller of the game
    screen -- the screen on which the current frame rate is displayed
    clock -- the clock regulating the maximum frame rate of the game

    Returns:
    whether quit or restart
    """
    action: QuitActionKind = QuitActionKind.CONTINUE
    while action == QuitActionKind.CONTINUE:
        screen.fill(BLACK)
        action = game_controller.process_game_iteration()
        show_fps(screen, clock, fonts.fonts["FPS_FONT"])
        pygame.display.update()
        clock.tick(FRAME_RATE)
    return action


if __name__ == "__main__":
    import os
    import platform
    import subprocess
    import sys

    from src.constants import (BLACK, FRAME_RATE, MAIN_WIN_HEIGHT,
                               MAIN_WIN_WIDTH)
    from src.game_entities.character import Character
    from src.game_entities.movable import Movable
    from src.gui import constant_sprites, fonts
    from src.services import load_from_xml_manager as loader
    from src.services.language import *
    from src.services.language import STR_GAME_TITLE

    pygame.init()
    pygamepopup.init()

    fonts.init_fonts()

    # Configure pygame-popup manager : set default assets to be used
    pygamepopup.configuration.set_info_box_title_font(fonts.fonts["MENU_TITLE_FONT"])
    pygamepopup.configuration.set_info_box_background("imgs/interface/PopUpMenu.png")
    pygamepopup.configuration.set_button_title_font(fonts.fonts["BUTTON_FONT"])
    pygamepopup.configuration.set_dynamic_button_title_font(fonts.fonts["BUTTON_FONT"])
    pygamepopup.configuration.set_button_background(
        "imgs/interface/MenuButtonInactiv.png", "imgs/interface/MenuButtonPreLight.png"
    )
    pygamepopup.configuration.set_text_element_font(fonts.fonts["ITEM_FONT"])
    pygamepopup.configuration.set_close_button_text(STR_CLOSE)

    pygame.display.set_caption(STR_GAME_TITLE)
    main_screen = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Make sure the game will display correctly on high DPI monitors on Windows.
    if platform.system() == "Windows":
        from ctypes import windll

        try:
            windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass

    Movable.init_constant_sprites()
    constant_sprites.init_constant_sprites()

    races = loader.load_races()
    classes = loader.load_classes()
    Character.init_data(races, classes)

    scene_manager = SceneManager(main_screen)

    pygame.mixer.music.load(os.path.join("sound_fx", "soundtrack.ogg"))
    pygame.mixer.music.play(-1)

    # Lets the game start!
    quit_action = main_loop(scene_manager, main_screen, pygame.time.Clock())

    pygame.quit()

    if quit_action == QuitActionKind.RESTART:
        # Restart game
        subprocess.Popen([sys.executable, "main.py"]).wait()
