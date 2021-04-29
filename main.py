N_LEVELS = {0.0: 1, 0.25: 2, 0.5: 3, 0.75: 4}

def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))

if __name__ == "__main__":
    import os
    import sys
    from src.constants import *
    from pygame import mixer
    from src.gui import constantSprites, fonts
    from src.game_entities.movable import Movable
    from src.game_entities.character import Character
    from src.scenes.startScreen import StartScreen
    from src.services import loadFromXMLManager as Loader
    pg.init()
    experiment = False
    if sys.argv[0] == '-experiment':
        experiment = True
    # Load fonts
    fonts.init_fonts()

    # Window parameters
    pg.display.set_caption("Tactical RPG Game")
    screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
    # Load constant sprites
    Movable.init_constant_sprites()
    constantSprites.init_constant_sprites()

    # Load some data
    races = Loader.load_races()
    classes = Loader.load_classes()
    Character.init_data(races, classes)

    clock = pg.time.Clock()


    #mixer.music.load(os.path.join('sound_fx', 'sndtrk.ogg'))
    #mixer.music.play(-1)
    iterations = 2
    nLevels = 0
    if experiment:
        for diff in [x*0.1 for x in range(1,11)]:
            for difficulty in N_LEVELS.keys():
                if diff >= difficulty:
                    nLevels = N_LEVELS[difficulty]
            for _ in range(iterations):
                start_screen = StartScreen(screen, nLevels)
                start_screen.modify_options_file('difficuty', diff)
                start_screen.new_game()
                #look in level.py for AI bot functions
    else:
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
