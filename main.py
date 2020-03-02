MAIN_WIN_WIDTH = 800
MAIN_WIN_HEIGHT = 800


def update_screen_display(win, level):
    # Blit the current state of the level
    level.display(win)


def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


def play(sScreen):
    end = False
    while not (sScreen.level_is_ended() or end):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 3:
                    sScreen.click(e.button, e.pos)
            elif e.type == pg.MOUSEMOTION:
                sScreen.motion(e.pos)
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1 or e.button == 3:
                    sScreen.button_down(e.button, e.pos)
        sScreen.update_state()
        show_fps(screen, clock, fps_font)
        pg.display.update()
        clock.tick(120)


if __name__ == "__main__":
    from src.constants import *
    import pygame as pg

    pg.init()

    # Window parameters
    screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    from src.StartScreen import StartScreen


    clock = pg.time.Clock()
    fps_font = pg.font.SysFont(None, 20, True)  # Use pygame's default font

    pg.display.set_caption('In the name of the Five Cats')

    startScreen = StartScreen(screen)

    quit_game = False
    while not quit_game:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit_game = True
            elif e.type == pg.MOUSEMOTION:
                startScreen.motion(e.pos)
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 3:
                    startedGame = startScreen.click(e.button, e.pos)
                    # Test if a game has been launched
                    if startedGame:
                        play(startScreen)
        startScreen.display()
        pg.display.update()
    pg.quit()
    raise SystemExit
