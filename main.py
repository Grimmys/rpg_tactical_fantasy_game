def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


if __name__ == "__main__":
    import pygame as pg
    from src.constants import *
    import src.fonts as fonts
    from src.Destroyable import Destroyable
    from src.Breakable import Breakable
    from src.Movable import Movable
    from src.Character import Character
    from src.Sidebar import Sidebar
    from src.Level import Level
    from src.StartScreen import StartScreen
    from src import LoadFromXMLManager as Loader

    pg.init()

    # Load fonts
    fonts.init_fonts()

    # Window parameters
    pg.display.set_caption("In the name of the Five Cats")
    screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Load constant sprites
    Destroyable.init_constant_sprites()
    Breakable.init_constant_sprites()
    Movable.init_constant_sprites()
    Sidebar.init_constant_sprites()
    Level.init_constant_sprites()

    # Load some data
    races = Loader.load_races()
    classes = Loader.load_classes()
    Character.init_data(races, classes)

    clock = pg.time.Clock()

    start_screen = StartScreen(screen)

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
