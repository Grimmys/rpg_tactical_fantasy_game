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


def play(screen, level):
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

    # Restore default window
    pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))


def init_player(name):
    # -- Reading of the XML file
    tree = etree.parse("data/characters.xml").getroot()
    player_t = tree.xpath(name)[0]
    player_class = player_t.find('class').text.strip()
    lvl = player_t.find('lvl')
    if lvl is None:
        # If lvl is not informed, default value is assumes to be 1
        lvl = 1
    else:
        lvl = int(lvl.text.strip())
    defense = int(player_t.find('initDef').text.strip())
    res = int(player_t.find('initRes').text.strip())
    hp = int(player_t.find('initHP').text.strip())
    strength = int(player_t.find('initStrength').text.strip())
    move = int(player_t.find('move').text.strip())
    sprite = 'imgs/dungeon_crawl/player/' + player_t.find('sprite').text.strip()
    compl_sprite = player_t.find('complementSprite')
    if compl_sprite is not None:
        compl_sprite = 'imgs/dungeon_crawl/player/' + compl_sprite.text.strip()

    equipment = player_t.find('equipment')
    equipments = []
    for eq in equipment.findall('*'):
        equipments.append(Level.parse_item_file(eq.text.strip()))

    # Creating player instance
    player = Player(name, sprite, hp, defense, res, move, strength, [player_class], equipments, lvl,
                    compl_sprite=compl_sprite)

    # Up stats according to current lvl
    player.stats_up(lvl - 1)
    # Restore hp due to lvl up
    player.healed()

    inventory = player_t.find('inventory')
    for it in inventory.findall('item'):
        item = Level.parse_item_file(it.text.strip())
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

    team = [init_player("john"), init_player("archer")]

    # Init the first level
    level = load_level("test", team)

    play(screen, level)


def load_game():
    # Test if there is a current saved game
    save = open("saves/main_save.xml", "r")
    if save:
        tree_root = etree.parse("saves/main_save.xml").getroot()
        level_name = tree_root.find("level/name").text.strip()
        game_status = tree_root.find("level/phase").text.strip()
        turn_nb = 0
        if game_status != 'I':
            turn_nb = int(tree_root.find("level/turn").text.strip())
        team = []
        for player in tree_root.findall("team/player"):
            name = player.find("name").text.strip()
            level = int(player.find("level").text.strip())
            p_class = player.find("class").text.strip()
            exp = int(player.find("exp").text.strip())
            hp = int(player.find("hp").text.strip())
            strength = int(player.find("strength").text.strip())
            defense = int(player.find("defense").text.strip())
            res = int(player.find("res").text.strip())
            move = int(player.find("move").text.strip())
            current_hp = int(player.find("currentHp").text.strip())
            pos = (int(player.find("position/x").text.strip()),
                   int(player.find("position/y").text.strip()))
            inv = []
            for it in player.findall("inventory/item"):
                it_name = it.find("name").text.strip()
                item = Level.parse_item_file(it_name)
                inv.append(item)

            equipments = []
            for eq in player.findall("equipments/equipment"):
                eq_name = eq.find("name").text.strip()
                eq = Level.parse_item_file(eq_name)
                equipments.append(eq)

            # -- Reading of the XML file for default character's values (i.e. sprites)
            tree = etree.parse("data/characters.xml").getroot()
            player_t = tree.xpath(name)[0]

            sprite = 'imgs/dungeon_crawl/player/' + player_t.find('sprite').text.strip()
            compl_sprite = player_t.find('complementSprite')
            if compl_sprite is not None:
                compl_sprite = 'imgs/dungeon_crawl/player/' + compl_sprite.text.strip()

            p = Player(name, sprite, hp, defense, res, move, strength, [p_class], equipments, level,
                    compl_sprite=compl_sprite)
            p.earn_xp(exp)
            p.set_items(inv)
            p.set_current_hp(current_hp)
            p.set_pos(pos)

            team.append(p)

        # Load level with current game status, foes states, and team
        level = Level(level_name, team, game_status, turn_nb, tree_root.find("level/entities"))
        screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        play(screen, level)
    else :
        print("Error : no saved game")

    save.close()


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

    # Window parameters
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
