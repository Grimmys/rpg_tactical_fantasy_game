def update_screen_display(win, level):
    #Blit the current state of the level
    level.display(win)

if __name__ == "__main__":
    import pygame as pg
    pg.init()

    TILE_SIZE = 48
    MENU_WIDTH = TILE_SIZE * 20
    MENU_HEIGHT = 100
    WIN_WIDTH = TILE_SIZE * 20
    WIN_HEIGHT = TILE_SIZE * 10 + MENU_HEIGHT

    WHITE = (255, 255, 255)
    GREY = (128, 128, 128)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    #Window paramaters
    screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT), pg.RESIZABLE)
    pg.display.set_caption('On testing...')

    clock = pg.time.Clock()

    from src.Level import Level

    # Init the first level
    level = Level('maps/level_test/')

    end = False
    while not level.is_ended():
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
        pg.display.update()
        clock.tick(120)
    pg.quit()
    raise SystemExit
