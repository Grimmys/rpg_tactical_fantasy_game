import pygame
from lxml import etree

from src.constants import SCREEN_SIZE, BLACK, WIN_WIDTH, WIN_HEIGHT, MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT
from src.services import menuCreatorManager
from src.gui.fonts import fonts
from src.scenes.level import Level, LevelStatus
from src.gui.infoBox import InfoBox
from src.game_entities.movable import Movable
from src.services.menus import StartMenu, OptionsMenu, GenericActions, LoadMenu


class StartScreen:
    screen_size = SCREEN_SIZE

    def __init__(self, screen):
        self.screen = screen
        self.menu_screen = self.screen.copy()

        # Start screen loop
        background_image = pygame.image.load(
            'imgs/interface/main_menu_background.jpg').convert_alpha()
        self.background = pygame.transform.scale(background_image, screen.get_size())

        # Creating menu
        self.active_menu = menuCreatorManager.create_start_menu()
        self.background_menus = []

        # Memorize if a game is currently being performed
        self.level = None

        self.levels = [0, 1, 2, 3]
        self.level_id = None

        # Load current saved parameters
        StartScreen.load_options()

        self.exit = False

    @staticmethod
    def load_options():
        # Load current move speed
        Movable.move_speed = int(StartScreen.read_options_file("move_speed"))
        StartScreen.screen_size = int(StartScreen.read_options_file("screen_size"))

    @staticmethod
    def read_options_file(el_to_read):
        tree = etree.parse("saves/options.xml").getroot()
        element = tree.find(".//" + el_to_read)
        return element.text.strip()

    @staticmethod
    def modify_options_file(element_to_edit, new_value):
        tree = etree.parse("saves/options.xml")
        element = tree.find(".//" + element_to_edit)
        element.text = str(new_value)
        tree.write("saves/options.xml")

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
        flags = pygame.FULLSCREEN if StartScreen.screen_size == 2 else 0
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT), flags)
        self.level = level

    def update_state(self):
        if self.level:
            status = self.level.update_state()
            if status is LevelStatus.ENDED_VICTORY and (self.level_id + 1) in self.levels:
                self.level_id += 1
                team = self.level.passed_players + self.level.players
                for player in team:
                    # Players are fully restored between level
                    player.healed(player.hp_max)
                    # Reset player's state
                    player.new_turn()
                self.play(StartScreen.load_level(self.level_id, team))
            elif status is LevelStatus.ENDED_VICTORY or status is LevelStatus.ENDED_DEFEAT:
                # TODO: Game win dialog?
                self.screen = pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
                self.level = None

    @staticmethod
    def load_level(level, team=None):
        if team is None:
            team = []
        return Level('maps/level_' + str(level) + '/', level, players=team)

    def new_game(self):
        # Init the first level
        self.level_id = 0
        self.play(StartScreen.load_level(self.level_id))

    def load_game(self, game_id):
        try:
            save = open(f"saves/save_{game_id}.xml", "r")

            # Test if there is a current saved game
            if save:
                tree_root = etree.parse(save).getroot()
                index = tree_root.find("level/index").text.strip()
                level_name = 'maps/level_' + index + '/'
                game_status = tree_root.find("level/phase").text.strip()
                turn_nb = 0
                if game_status != 'I':
                    turn_nb = int(tree_root.find("level/turn").text.strip())

                # Load level with current game status, foes states, and team
                self.level_id = int(index)
                level = Level(level_name, self.level_id, LevelStatus[game_status], turn_nb,
                              tree_root.find("level/entities"))
                self.play(level)
                save.close()
                return
        except FileNotFoundError:
            # No saved game
            self.background_menus.append([self.active_menu, True])

            name = "Load Game"
            entries = [[{'type': 'text', 'text': "No saved game.", 'font':
                fonts['MENU_SUB_TITLE_FONT']}]]
            width = self.screen.get_width() // 2
            self.active_menu = InfoBox(name, "", "imgs/interface/PopUpMenu.png",
                                       entries, width, close_button=1)

    def load_menu(self):
        self.background_menus.append([self.active_menu, False])
        self.active_menu = menuCreatorManager.create_load_menu()

    def options_menu(self):
        self.background_menus.append([self.active_menu, False])
        self.active_menu = menuCreatorManager.create_options_menu(
            {'move_speed': int(self.read_options_file('move_speed')),
             'screen_size': int(self.read_options_file('screen_size'))})

    def exit_game(self):
        self.exit = True

    def main_menu_action(self, method_id, args):
        # Execute action
        if method_id is StartMenu.NEW_GAME:
            self.new_game()
        elif method_id is StartMenu.LOAD_GAME:
            self.load_menu()
        elif method_id is StartMenu.OPTIONS:
            self.options_menu()
        elif method_id is StartMenu.EXIT:
            self.exit_game()
        else:
            print(f"Unknown action : {method_id}")

    def load_menu_action(self, method_id, args):
        # Execute action
        if method_id is LoadMenu.LOAD:
            self.load_game(args[2][0])
        else:
            print(f"Unknown action: {method_id}")

    @staticmethod
    def options_menu_action(method_id, args):
        # Execute action
        if method_id is OptionsMenu.CHANGE_MOVE_SPEED:
            Movable.move_speed = args[2][0]
            StartScreen.modify_options_file("move_speed", args[2][0])
        elif method_id is OptionsMenu.CHANGE_SCREEN_SIZE:
            StartScreen.screen_size = args[2][0]
            StartScreen.modify_options_file("screen_size", args[2][0])
        else:
            print(f"Unknown action : {method_id}")

    def execute_action(self, menu_type, action):
        if not action:
            return
        method_id = action[0]
        args = action[1]

        # Test if the action is a generic one (according to the method_id)
        # Close menu : Active menu is closed
        if method_id is GenericActions.CLOSE:
            self.active_menu = self.background_menus.pop()[0] if self.background_menus else None
            return

        if menu_type is StartMenu:
            self.main_menu_action(method_id, args)
        elif menu_type is OptionsMenu:
            StartScreen.options_menu_action(method_id, args)
        elif menu_type is LoadMenu:
            self.load_menu_action(method_id, args)
        else:
            print(f"Unknown menu : {menu_type}")

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
