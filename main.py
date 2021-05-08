#!/usr/bin/env python3


def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


if __name__ == "__main__":
    import os

    import pygame

    from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
    from src.gui import constantSprites, fonts
    from src.game_entities.movable import Movable
    from src.game_entities.character import Character
    from src.scenes.startScreen import StartScreen
    from src.services import loadFromXMLManager as Loader

    pygame.init()

    # Load fonts
    fonts.init_fonts()

    # Window parameters
    pygame.display.set_caption("In the name of the Five Cats")
    screen = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Load constant sprites
    Movable.init_constant_sprites()
    constantSprites.init_constant_sprites()

    # Load some data
    races = Loader.load_races()
    classes = Loader.load_classes()
    Character.init_data(races, classes)

    clock = pygame.time.Clock()

    start_screen = StartScreen(screen)

    pygame.mixer.music.load(os.path.join('sound_fx', 'sndtrk.ogg'))
    pygame.mixer.music.play(-1)

    quit_game = False
    while not quit_game:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit_game = True
            elif e.type == pygame.MOUSEMOTION:
                start_screen.motion(e.pos)
            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 3:
                    quit_game = start_screen.click(e.button, e.pos)
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1 or e.button == 3:
                    start_screen.button_down(e.button, e.pos)
        start_screen.update_state()
        start_screen.display()
        show_fps(screen, clock, fonts.fonts['FPS_FONT'])
        pygame.display.update()
        clock.tick(60)
    raise SystemExit
