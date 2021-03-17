from src.gui import constantSprites


def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


if __name__ == "__main__":
    from src.constants import *
    import src.gui.fonts as fonts
    from src.game_entities.movable import Movable
    from src.game_entities.character import Character
    from src.scenes.startScreen import StartScreen
    from src.services import loadFromXMLManager as Loader

    # beiba
    import pygame.mixer
    import os

    pg.init()

    # Load fonts
    fonts.init_fonts()

    # Window parameters
    pg.display.set_caption("In the name of the Five Cats")
    screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Load constant sprites
    Movable.init_constant_sprites()
    constantSprites.init_constant_sprites()

    # Load some data
    races = Loader.load_races()
    classes = Loader.load_classes()
    Character.init_data(races, classes)

    clock = pg.time.Clock()

    start_screen = StartScreen(screen)

    pygame.mixer.music.load(os.path.join('sound_fx', 'sndtrk.ogg'))
    pygame.mixer.music.play(-1)

    quit_game = False
    while not quit_game:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit_game = True
            elif e.type == pg.MOUSEMOTION:
                start_screen.motion(e.pos)
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 3:
                    quit_game = start_screen.click(e.button, e.pos)
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1 or e.button == 3:
                    start_screen.button_down(e.button, e.pos)
        start_screen.update_state()
        start_screen.display()
        show_fps(screen, clock, fonts.fonts['FPS_FONT'])
        pg.display.update()
        clock.tick(60)
    raise SystemExit
