from lxml import etree
from src.constants import *
import pygame as pg

from src.Level import Level
from src.Player import Player
from src.InfoBox import InfoBox
from src.Movable import Movable

START_MENU_WIDTH = 600

ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)

# Interaction ids
#  > Generic
#    - To close any menu
CLOSE_ACTION_ID = -1

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

# > Options menu
OPTIONS_MENU_ID = 1
#   - Modify movement speed
CHANGE_MOVE_SPEED = 0


class StartScreen:
    def __init__(self, screen):
        self.screen = screen
        self.menu_screen = self.screen.copy()

        # Start screen loop
        bg_image = pg.image.load('imgs/interface/main_menu_background.jpg').convert_alpha()
        self.background = pg.transform.scale(bg_image, screen.get_size())

        # Creating menu
        self.active_menu = StartScreen.create_menu()
        self.background_menus = []

        # Memorize if a game is currently being performed
        self.started_game = False
        self.level = None

        # Load current saved parameters
        self.load_options()

    def load_options(self):
        # Load current move speed
        Movable.move_speed = int(self.read_options_file("move_speed"))

    @staticmethod
    def create_menu():
        entries = [[{'name': 'New game', 'id': NEW_GAME_ACTION_ID}], [{'name': 'Load game', 'id': LOAD_GAME_ACTION_ID}],
                   [{'name': 'Options', 'id': OPTIONS_ACTION_ID}], [{'name': 'Exit game', 'id': EXIT_ACTION_ID}]]

        for row in entries:
            for entry in row:
                entry['type'] = 'button'

        return InfoBox("In the name of the Five Cats", START_MENU_ID,
                       "imgs/interface/PopUpMenu.png", entries, START_MENU_WIDTH)

    @staticmethod
    def load_parameter_entry(param, formatted_name, values, id):
        val = int(StartScreen.read_options_file(param))

        entry = {'name': formatted_name, 'values': values, 'id': id, 'current_value_ind': 0}

        for i in range(len(entry['values'])):
            if entry['values'][i]['value'] == val:
                entry['current_value_ind'] = i

        return entry

    @staticmethod
    def create_options_menu():
        entries = [[StartScreen.load_parameter_entry("move_speed", "Move speed : ",
                                                        [{'label': 'Slow', 'value': ANIMATION_SPEED // 2},
                                                         {'label': 'Normal', 'value': ANIMATION_SPEED},
                                                         {'label': 'Fast', 'value': ANIMATION_SPEED * 2}],
                                                     CHANGE_MOVE_SPEED)]]
        for row in entries:
            for entry in row:
                entry['type'] = 'parameter_button'

        return InfoBox("Options", OPTIONS_MENU_ID,
                       "imgs/interface/PopUpMenu.png", entries, START_MENU_WIDTH, close_button=1)

    @staticmethod
    def modify_options_file(el_to_edit, new_value):
        tree = etree.parse("saves/options.xml")
        el = tree.find(".//" + el_to_edit)
        el.text = str(new_value)
        tree.write("saves/options.xml")

    @staticmethod
    def read_options_file(el_to_read):
        tree = etree.parse("saves/options.xml").getroot()

        el = tree.find(".//" + el_to_read)
        return el.text.strip()

    def display(self):
        if self.level:
            self.screen.fill(GREY)
            self.level.display(self.screen)
        else:
            self.screen.blit(self.background, (0, 0))
            for menu in self.background_menus:
                if menu[1]:
                    menu[0].display(self.screen)
            if self.active_menu:
                self.active_menu.display(self.screen)

    def play(self, level):
        # Modify screen
        self.screen = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.started_game = True
        self.level = level

    def update_state(self):
        if self.level:
            exit = self.level.update_state()
            if exit:
                self.screen = pg.display.set_mode((self.menu_screen.get_width(), self.menu_screen.get_height()))
                self.level = None

    def level_is_ended(self):
        return self.level.is_ended()

    @staticmethod
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

    @staticmethod
    def load_level(level, team):
        return Level('maps/level_' + level + '/', team)

    def new_game(self):
        # Init player's team (one character at beginning)
        team = [self.init_player("john"), self.init_player("archer")]

        # Init the first level
        level = StartScreen.load_level("test", team)

        self.play(level)

    def load_game(self):
        try:
            save = open("saves/main_save.xml", "r")

            # Test if there is a current saved game
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
                    state = player.find("turnFinished").text.strip()
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
                    if state == "True":
                        p.turn_finished()

                    team.append(p)

                # Load level with current game status, foes states, and team
                level = Level(level_name, team, game_status, turn_nb, tree_root.find("level/entities"))
                self.play(level)
                save.close()
                return
        except FileNotFoundError as err:
            pass

        # No saved game
        self.background_menus.append([self.active_menu, True])

        name = "Load Game"
        entries = [[{'type': 'text', 'text': "No saved game.", 'font': ITEM_DESC_FONT}]]
        width = self.screen.get_width() // 2
        self.active_menu = InfoBox(name, "", "imgs/interface/PopUpMenu.png",
                                   entries, width, close_button=1)

    def options_menu(self):
        self.background_menus.append([self.active_menu, False])
        self.active_menu = StartScreen.create_options_menu()

    @staticmethod
    def exit_game():
        pg.quit()
        raise SystemExit

    def main_menu_action(self, method_id, args):
        # Execute action
        if method_id == NEW_GAME_ACTION_ID:
            self.new_game()
        elif method_id == LOAD_GAME_ACTION_ID:
            self.load_game()
        elif method_id == OPTIONS_ACTION_ID:
            self.options_menu()
        elif method_id == EXIT_ACTION_ID:
            self.exit_game()
        else:
            print("Unknown action... : ", method_id)

    def options_menu_action(self, method_id, args):
        # Execute action
        if method_id == CHANGE_MOVE_SPEED:
            Movable.move_speed = args[2][0]
            StartScreen.modify_options_file("move_speed", args[2][0])
        else:
            print("Unknown action... : ", method_id)

    def execute_action(self, menu_type, action):
        if not action:
            return
        method_id = action[0]
        args = action[1]

        # Test if the action is a generic one (according to the method_id)
        # Close menu : Active menu is closed
        if method_id == CLOSE_ACTION_ID:
            self.active_menu = None
            if self.background_menus:
                self.active_menu = self.background_menus.pop()[0]
            return

        if menu_type == START_MENU_ID:
            self.main_menu_action(method_id, args)
        elif menu_type == OPTIONS_MENU_ID:
            self.options_menu_action(method_id, args)
        else:
            print("Unknown menu... : ", menu_type)

    def motion(self, pos):
        if self.level is None:
            self.active_menu.motion(pos)
        else:
            self.level.motion(pos)

    def click(self, button, pos):
        if self.level is None:
            if button == 1:
                self.execute_action(self.active_menu.get_type(), self.active_menu.click(pos))
                return self.started_game
        else:
            self.level.click(button, pos)

    def button_down(self, button, pos):
        if self.level is not None:
            self.level.button_down(button, pos)