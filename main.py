MAIN_WIN_WIDTH = 800
MAIN_WIN_HEIGHT = 800

START_MENU_WIDTH = 600

# > Start menu
START_MENU_ID = 0
#   - Launch new game
NEW_GAME_ACTION_ID = 0
#   - Load game
LOAD_GAME_ACTION_ID = 1
#   - Access to options screen
OPTIONS_ACTION_ID = 2
#   - Exit game
EXIT_ACTION_ID = 3


def update_screen_display(win, level):
    # Blit the current state of the level
    level.display(win)


def create_menu():
    entries = [[{'name': 'New game', 'id': NEW_GAME_ACTION_ID}], [{'name': 'Load game', 'id': LOAD_GAME_ACTION_ID}],
               [{'name': 'Options', 'id': OPTIONS_ACTION_ID}], [{'name': 'Exit game', 'id': EXIT_ACTION_ID}]]
    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("In the name of the Five Cats", START_MENU_ID,
                   "imgs/interface/PopUpMenu.png", entries, START_MENU_WIDTH)


def show_fps(win, inner_clock, font):
    fps_text = font.render("FPS: " + str(round(inner_clock.get_fps())), True, (255, 255, 0))
    win.blit(fps_text, (2, 2))


def init_player(name):
    # -- Reading of the XML file
    tree = etree.parse("data/characters.xml").getroot()
    player = tree.xpath(name)[0]
    print(player)
    name = player.find('name').text.strip()
    sprite = 'imgs/dungeon_crawl/player/' + player.find('sprite').text.strip()
    head = 'imgs/dungeon_crawl/item/' + player.find('equipment/head').text.strip()
    body = 'imgs/dungeon_crawl/item/' + player.find('equipment/body').text.strip()
    feet = 'imgs/dungeon_crawl/item/' + player.find('equipment/feet').text.strip()
    head_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/head_equipped').text.strip()
    body_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/body_equipped').text.strip()
    feet_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/feet_equipped').text.strip()
    equipments = [
        Equipment('Gold Helmet', head, "", head_equipped, "head", 0, 0, 0, 0),
        Equipment('Gold Armor', body, "", body_equipped, "body", 0, 0, 0, 0),
        Equipment('Gold Boots', feet, "", feet_equipped, "feet", 0, 0, 0, 0)
    ]
    lvl = 3
    defense = 0
    res = 0
    hp = 10
    move = 5
    strength = 1

    # Creating player instance
    player = Player(name, sprite, hp, defense, res, move, strength, ['warrior'], equipments, lvl)

    items_id = ['life_potion', 'key', 'club']
    for name in items_id:
        item = Level.parse_item_file(name)
        player.set_item(item)

    return player


def load_level(level, team):
    return Level('maps/level_' + level + '/', team)


def execute_action(menu_type, action):
    if not action:
        return
    method_id = action[0]
    args = action[1]

    if menu_type == START_MENU_ID:
        main_menu_action(method_id, args)
    else:
        print("Unknown menu... : " + menu_type)


def main_menu_action(method_id, args):
    # Execute action
    if method_id == NEW_GAME_ACTION_ID:
        new_game()
    elif method_id == LOAD_GAME_ACTION_ID:
        load_game()
    elif method_id == OPTIONS_ACTION_ID:
        options_menu()
    elif method_id == EXIT_ACTION_ID:
        exit_game()
    else:
        print("Unknown action... : " + method_id)


def new_game():
    # Modify screen
    screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))

    # Init player's team (one character at beginning)

    team = [init_player("john")]

    # Init the first level
    level = load_level("test", team)

    end = False
    while not (level.is_ended() or end):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                end = True
                exit_game()
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


def load_game():
    print("Load game !")


def options_menu():
    print("Access to options menu !")


def exit_game():
    global quit_game
    quit_game = True


if __name__ == "__main__":
    from lxml import etree
    from src.constants import *
    import pygame as pg
    pg.init()

    # Window paramaters
    screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    from src.Level import Level
    from src.Equipment import Equipment
    from src.Player import Player
    from src.InfoBox import InfoBox

    clock = pg.time.Clock()
    fps_font = pg.font.SysFont(None, 20, True)  # Use pygame's default font

    pg.display.set_caption('In the name of the Five Cats')

    # Start screen loop
    background = pg.image.load('imgs/interface/main_menu_background.jpg').convert_alpha()
    background = pg.transform.scale(background, (MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))

    # Creating menu
    main_menu = create_menu()

    quit_game = False
    while not quit_game:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit_game = True
            elif e.type == pg.MOUSEMOTION:
                main_menu.motion(e.pos)
            elif e.type == pg.MOUSEBUTTONUP:
                if e.button == 1 or e.button == 3:
                    execute_action(main_menu.get_type(), main_menu.click(e.pos))

        screen.blit(background, (0, 0))
        main_menu.display(screen)
        pg.display.update()
    pg.quit()
    raise SystemExit
