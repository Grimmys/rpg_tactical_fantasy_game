from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT


def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


if __name__ == "__main__":
    import pygame as pg
    from src.constants import *

    pg.init()

    # Load fonts
    from src.fonts import *

    # Window parameters
    pg.display.set_caption("In the name of the Five Cats")
    screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    from src.StartScreen import StartScreen

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
        show_fps(screen, clock, FPS_FONT)
        pg.display.update()
        clock.tick(60)
    raise SystemExit
