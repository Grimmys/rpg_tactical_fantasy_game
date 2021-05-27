#!/usr/bin/env python3

"""
The entry point of the game.
Initiate pygame, load game generic data & fonts, initiate pygame window
and let the main loop running.
The pygame events are catch here and delegated to the start screen.
"""

import pygame

from src.scenes.start_screen import StartScreen


def show_fps(surface: pygame.Surface, inner_clock: pygame.time.Clock,
             font: pygame.font.Font) -> None:
    """
    Display at the top left corner of the screen the current frame rate.

    Keyword arguments:
    screen -- the surface on which the framerate should be drawn
    inner_clock -- the pygame clock running and containing the current frame rate
    font -- the font used to display the frame rate
    """
    fps_text: pygame.Surface = font.render("FPS: " + str(round(inner_clock.get_fps())),
                                           True, (255, 255, 0))
    surface.blit(fps_text, (2, 2))


def main_loop(scene: StartScreen, window: pygame.Surface, clock: pygame.time.Clock) -> None:
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
                if event.button == 1 or event.button == 3:
                    quit_game = scene.click(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 or event.button == 3:
                    scene.button_down(event.button, event.pos)
        scene.update_state()
        scene.display()
        show_fps(window, clock, fonts.fonts['FPS_FONT'])
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    import os

    from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, GAME_TITLE
    from src.gui import constant_sprites, fonts
    from src.game_entities.movable import Movable
    from src.game_entities.character import Character
    from src.services import load_from_xml_manager as loader

    pygame.init()

    # Load fonts
    fonts.init_fonts()

    # Window parameters
    pygame.display.set_caption(GAME_TITLE)
    main_window = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Load constant sprites
    Movable.init_constant_sprites()
    constant_sprites.init_constant_sprites()

    # Load some data
    races = loader.load_races()
    classes = loader.load_classes()
    Character.init_data(races, classes)

    start_screen = StartScreen(main_window)

    # Load and start menu soundtrack
    pygame.mixer.music.load(os.path.join('sound_fx', 'soundtrack.ogg'))
    pygame.mixer.music.play(-1)

    # Let's the game start!
    main_loop(start_screen, main_window, pygame.time.Clock())

    raise SystemExit
