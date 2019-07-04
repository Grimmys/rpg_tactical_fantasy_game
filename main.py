def update_screen_display(win, level):
    #Blit the current state of the level
    level.display(win)


def show_fps(win, clock, font):
    fps_text = font.render("FPS: " + str(round(clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


if __name__ == "__main__":
    from src.constants import *
    import pygame as pg
    pg.init()

    #Window paramaters
    screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.RESIZABLE)
    pg.display.set_caption('On testing...')

    clock = pg.time.Clock()
    fps_font = pg.font.SysFont(None, 20, True)  # Use pygame's default font

    from src.Level import Level

    # Init the first level
    level = Level('maps/level_test/')

    end = False
    while not (level.is_ended() or end):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                end = True
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 3:
                    level.click(e.button, e.pos)
            elif e.type == pg.MOUSEMOTION:
                level.motion(e.pos)
            elif e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1 or e.button == 3:
                    level.button_down(e.button, e.pos)
        level.update_state()
        screen.fill(GREY)
        update_screen_display(screen, level)
        show_fps(screen, clock, fps_font)
        pg.display.update()
        clock.tick(120)
    pg.quit()
    raise SystemExit
