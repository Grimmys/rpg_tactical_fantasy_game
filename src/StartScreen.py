from lxml import etree

from src.constants import *
from src.fonts import fonts
from src.Level import Level, Status
from src.InfoBox import InfoBox
from src.Movable import Movable
from src.Menus import StartMenu, OptionsMenu, GenericActions


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
        self.level = None

        self.levels = [0, 1, 2]
        self.level_id = None

        # Load current saved parameters
        self.load_options()

        self.exit = False

    def load_options(self):
        # Load current move speed
        Movable.move_speed = int(self.read_options_file("move_speed"))

    @staticmethod
    def create_menu():
        entries = [[{'name': 'New game', 'id': StartMenu.NEW_GAME}], [{'name': 'Load game', 'id': StartMenu.LOAD_GAME}],
                   [{'name': 'Options', 'id': StartMenu.OPTIONS}], [{'name': 'Exit game', 'id': StartMenu.EXIT}]]

        for row in entries:
            for entry in row:
                entry['type'] = 'button'

        return InfoBox("In the name of the Five Cats", StartMenu,
                       "imgs/interface/PopUpMenu.png", entries, START_MENU_WIDTH)

    @staticmethod
    def load_parameter_entry(param, formatted_name, values, identifier):
        val = int(StartScreen.read_options_file(param))

        entry = {'name': formatted_name, 'values': values, 'id': identifier, 'current_value_ind': 0}

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
                                                     OptionsMenu.CHANGE_MOVE_SPEED)]]
        for row in entries:
            for entry in row:
                entry['type'] = 'parameter_button'

        return InfoBox("Options", OptionsMenu,
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
            self.screen.fill(BLACK)
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
        self.level = level

    def update_state(self):
        if self.level:
            status = self.level.update_state()
            if status is Status.ENDED_VICTORY:
                self.level_id += 1
                if self.level_id in self.levels:
                    team = self.level.passed_players + self.level.players
                    for player in team:
                        # Players are fully restored between level
                        player.healed(player.hp_max)
                        # Reset player's state
                        player.new_turn()
                    self.play(StartScreen.load_level(self.level_id, team))
                else:
                    # TODO: Game win dialog?
                    self.screen = pg.display.set_mode((self.menu_screen.get_width(), self.menu_screen.get_height()))
                    self.level = None
            elif status is Status.ENDED_DEFEAT:
                self.screen = pg.display.set_mode((self.menu_screen.get_width(), self.menu_screen.get_height()))
                self.level = None

    @staticmethod
    def load_level(level):
        return Level('maps/level_' + str(level) + '/', level)

    def new_game(self):
        # Init the first level
        self.level_id = 0
        self.play(StartScreen.load_level(self.level_id))

    def load_game(self):
        try:
            save = open("saves/main_save.xml", "r")

            # Test if there is a current saved game
            if save:
                tree_root = etree.parse("saves/main_save.xml").getroot()
                index = tree_root.find("level/index").text.strip()
                level_name = 'maps/level_' + index + '/'
                game_status = tree_root.find("level/phase").text.strip()
                turn_nb = 0
                if game_status != 'I':
                    turn_nb = int(tree_root.find("level/turn").text.strip())

                # Load level with current game status, foes states, and team
                self.level_id = int(index)
                level = Level(level_name, self.level_id, game_status, turn_nb, tree_root.find("level/entities"))
                self.play(level)
                save.close()
                return
        except FileNotFoundError:
            # No saved game
            self.background_menus.append([self.active_menu, True])

            name = "Load Game"
            entries = [[{'type': 'text', 'text': "No saved game.", 'font': fonts['MENU_SUB_TITLE_FONT']}]]
            width = self.screen.get_width() // 2
            self.active_menu = InfoBox(name, "", "imgs/interface/PopUpMenu.png",
                                       entries, width, close_button=1)

    def options_menu(self):
        self.background_menus.append([self.active_menu, False])
        self.active_menu = StartScreen.create_options_menu()

    def exit_game(self):
        self.exit = True

    def main_menu_action(self, method_id, args):
        # Execute action
        if method_id is StartMenu.NEW_GAME:
            self.new_game()
        elif method_id is StartMenu.LOAD_GAME:
            self.load_game()
        elif method_id is StartMenu.OPTIONS:
            self.options_menu()
        elif method_id is StartMenu.EXIT:
            self.exit_game()
        else:
            print("Unknown action... : ", str(method_id))

    @staticmethod
    def options_menu_action(method_id, args):
        # Execute action
        if method_id is OptionsMenu.CHANGE_MOVE_SPEED:
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
        if method_id is GenericActions.CLOSE:
            self.active_menu = None
            if self.background_menus:
                self.active_menu = self.background_menus.pop()[0]
            return

        if menu_type is StartMenu:
            self.main_menu_action(method_id, args)
        elif menu_type is OptionsMenu:
            self.options_menu_action(method_id, args)
        else:
            print("Unknown menu... : ", str(menu_type))

    def motion(self, pos):
        if self.level is None:
            self.active_menu.motion(pos)
        else:
            self.level.motion(pos)

    def click(self, button, pos):
        if self.level is None:
            if button == 1:
                self.execute_action(self.active_menu.type, self.active_menu.click(pos))
        else:
            self.level.click(button, pos)
        return self.exit

    def button_down(self, button, pos):
        if self.level is not None:
            self.level.button_down(button, pos)
