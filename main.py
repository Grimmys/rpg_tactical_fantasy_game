#!/usr/bin/env python3

"""
The entry point of the game.
Initiate pygame, load game generic data & fonts, initiate pygame window
and let the main loop running.
The pygame events are catch here and delegated to the start screen.
"""

import pygame
import pygamepopup

from src.gui.tools import show_fps
from src.scenes.start_scene import StartScene


def main_loop(
    scene: StartScene, window: pygame.Surface, clock: pygame.time.Clock
) -> None:
    """
    Run the game until a quit request happened.
    Pygame events are catch and delegated to the scene.
    The scene state and display are updated at each iteration.

    Keyword arguments:
    scene -- the scene acting as the main controller of the game
    window -- the window on which the current frame rate is displayed
    clock -- the clock regulating the maximum frame rate of the game
    """
    quit_game: bool = False
    while not quit_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game = True
            elif event.type == pygame.MOUSEMOTION:
                scene.motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    quit_game = scene.click(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    scene.button_down(event.button, event.pos)
        scene.update_state()
        scene.display()
        show_fps(window, clock, fonts.fonts["FPS_FONT"])
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    import os
    import platform

    from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, GAME_TITLE
    from src.gui import constant_sprites, fonts
    from src.game_entities.movable import Movable
    from src.game_entities.character import Character
    from src.services import load_from_xml_manager as loader

    pygame.init()
    pygamepopup.init()

    # Load fonts
    fonts.init_fonts()

    # Configure pygame-popup manager : set default assets to be used
    pygamepopup.configuration.set_info_box_title_font(fonts.fonts["MENU_TITLE_FONT"])
    pygamepopup.configuration.set_info_box_background("imgs/interface/PopUpMenu.png")
    pygamepopup.configuration.set_button_title_font(fonts.fonts["BUTTON_FONT"])
    pygamepopup.configuration.set_dynamic_button_title_font(fonts.fonts["BUTTON_FONT"])
    pygamepopup.configuration.set_button_background("imgs/interface/MenuButtonInactiv.png",
                                                    "imgs/interface/MenuButtonPreLight.png")
    pygamepopup.configuration.set_text_element_font(fonts.fonts["ITEM_FONT"])

    # Window parameters
    pygame.display.set_caption(GAME_TITLE)
    main_window = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Make sure the game will display correctly on high DPI monitors on Windows.
    if platform.system() == 'Windows':
        from ctypes import windll

        try:
            windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass

    # Load constant sprites
    Movable.init_constant_sprites()
    constant_sprites.init_constant_sprites()

    # Load some data
    races = loader.load_races()
    classes = loader.load_classes()
    Character.init_data(races, classes)

    start_scene = StartScene(main_window)

    # Load and start menu soundtrack
    pygame.mixer.music.load(os.path.join("sound_fx", "soundtrack.ogg"))
    pygame.mixer.music.play(-1)

    # Let's the game start!
    main_loop(start_scene, main_window, pygame.time.Clock())

    raise SystemExit
