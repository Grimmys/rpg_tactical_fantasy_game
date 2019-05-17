import pygame as pg
from lxml import etree
import random

from src.Destroyable import Destroyable
from src.Key import Key
from src.Equipment import Equipment
from src.Weapon import Weapon
from src.Potion import Potion
from src.Consumable import Consumable
from src.Character import Character
from src.Player import Player
from src.Foe import Foe
from src.Chest import Chest
from src.Portals import Portals
from src.Fountain import Fountain
from src.Breakable import Breakable
from src.InfoBox import InfoBox
from src.Sidebar import Sidebar
from src.Animation import Animation

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MARINE_BLUE = (34, 61, 200)
ORANGE = (255, 140, 0)
YELLOW = (143, 143, 5)
GOLD = (200, 172, 34)
BROWN = (139, 69, 19)
MAROON = (128, 0, 0)
BROWN_RED = (165, 42, 42)

TILE_SIZE = 48
MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10

TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 46)
MENU_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 26)
MENU_SUB_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)
ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITALIC_ITEM_FONT = pg.font.Font('fonts/minya_nouvelle_it.ttf', 14)

LANDING_SPRITE = 'imgs/dungeon_crawl/misc/landing.png'
LANDING = pg.transform.scale(pg.image.load(LANDING_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
LANDING_OPACITY = 100
ATTACKABLE_SPRITE = 'imgs/dungeon_crawl/misc/attackable.png'
ATTACKABLE = pg.transform.scale(pg.image.load(ATTACKABLE_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
ATTACKABLE_OPACITY = 40

BUTTON_MENU_SIZE = (150, 30)
CLOSE_BUTTON_SIZE = (150, 50)
ITEM_BUTTON_MENU_SIZE = (180, TILE_SIZE + 30)
MENU_WIDTH = TILE_SIZE * 20
MENU_HEIGHT = 100

ACTION_MENU_WIDTH = 200
ITEM_MENU_WIDTH = 500
ITEM_INFO_MENU_WIDTH = 600
ITEM_DELETE_MENU_WIDTH = 350
STATUS_MENU_WIDTH = 300

MARGINTOP = 10

SIDEBAR_SPRITE = 'imgs/interface/sidebar.png'
NEW_TURN_SPRITE = 'imgs/interface/new_turn.png'
NEW_TURN = pg.transform.scale(pg.image.load(NEW_TURN_SPRITE).convert_alpha(), (int(392 * 1.5), int(107 * 1.5)))
NEW_TURN_POS = (MAP_WIDTH / 2 - NEW_TURN.get_width() / 2, MAP_HEIGHT / 2 - NEW_TURN.get_height() / 2)
NEW_TURN_TEXT = TITLE_FONT.render("New turn !", 1, WHITE)
NEW_TURN_TEXT_POS = (NEW_TURN.get_width() / 2 - NEW_TURN_TEXT.get_width() / 2, NEW_TURN.get_height() / 2 - NEW_TURN_TEXT.get_height() / 2)

def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pg.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

class Level:
    def __init__(self, directory):
        self.map = pg.image.load(directory + 'map.png')

        self.players = []
        #Reading of the XML file
        tree = etree.parse(directory + "data.xml")
        #Load player
        for player in tree.xpath("/level/player"):
            name = player.find('name').text.strip()
            x = int(player.find('position/x').text) * TILE_SIZE
            y = int(player.find('position/y').text) * TILE_SIZE
            pos = (x, y)
            sprite = 'imgs/dungeon_crawl/player/' + player.find('sprite').text.strip()
            head = 'imgs/dungeon_crawl/item/' + player.find('equipment/head').text.strip()
            body = 'imgs/dungeon_crawl/item/' + player.find('equipment/body').text.strip()
            gloves = 'imgs/dungeon_crawl/item/' + player.find('equipment/gloves').text.strip()
            feet = 'imgs/dungeon_crawl/item/' + player.find('equipment/feet').text.strip()
            head_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/head_equipped').text.strip()
            body_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/body_equipped').text.strip()
            gloves_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/gloves_equipped').text.strip()
            feet_equipped = 'imgs/dungeon_crawl/player/' + player.find('equipment/feet_equipped').text.strip()
            equipments = [
                Equipment('Gold Helmet', head, "", head_equipped, "head", 0, 0, 0, 0),
                Equipment('Gold Armor', body, "", body_equipped, "body", 0, 0, 0, 0),
                Equipment('Gold Gloves', gloves, "", gloves_equipped, "wrist", 0, 0, 0, 0),
                Equipment('Gold Boots', feet, "", feet_equipped, "feet", 0, 0, 0, 0)
            ]
            lvl = 3
            player = Player(name, pos, sprite, 20, 15, 1, ['warrior'], equipments, lvl)

            items_id = ['life_potion', 'key', 'club']
            for name in items_id:
                it_tree_root = etree.parse('data/items/' + name + '.xml').getroot()

                sprite = 'imgs/dungeon_crawl/item/' + it_tree_root.find('sprite').text.strip()
                info = it_tree_root.find('info').text.strip()
                category = it_tree_root.find('category').text.strip()

                if category == 'potion':
                    effect = it_tree_root.find('effect').text.strip()
                    power = int(it_tree_root.find('power').text.strip())
                    item = Potion(name, sprite, info, effect, power)
                elif category == 'weapon':
                    power = int(it_tree_root.find('power').text.strip())
                    weight = int(it_tree_root.find('weight').text.strip())
                    fragility = int(it_tree_root.find('fragility').text.strip())
                    equipped_sprite = 'imgs/dungeon_crawl/player/hand_right/' + it_tree_root.find('equipped_sprite').text.strip()
                    item = Weapon(name, sprite, info, equipped_sprite, power, weight, fragility, range)
                elif category == 'key':
                    item = Key(name, sprite, info)

                player.set_item(item)

            self.players.append(player)
        #Load foes
        foes_infos = {}
        self.foes = []
        for foe in tree.xpath("/level/foes/foe"):
            name = foe.find('type').text.strip()
            x = int(foe.find('position/x').text) * TILE_SIZE
            y = int(foe.find('position/y').text) * TILE_SIZE
            pos = (x, y)
            if name not in foes_infos:
                foes_infos[name] = etree.parse('data/foes/' + name + '.xml').getroot()
            sprite = 'imgs/dungeon_crawl/monster/' + foes_infos[name].find('sprite').text.strip()
            self.foes.append(Foe(name, pos, sprite, 5, 2, 1))
        #Load chests
        self.chests = []
        for chest in tree.xpath("/level/chests/chest"):
            name = "Chest"
            x = int(chest.find('position/x').text) * TILE_SIZE
            y = int(chest.find('position/y').text) * TILE_SIZE
            pos = (x, y)
            sprite_closed = 'imgs/dungeon_crawl/' + chest.find('closed/sprite').text.strip()
            sprite_opened = 'imgs/dungeon_crawl/' + chest.find('opened/sprite').text.strip()
            self.chests.append(Chest(name, pos, sprite_closed, sprite_opened))
        #Load portals
        self.portals = []
        i = 0
        for portal_couple in tree.xpath("/level/portals/couple"):
            name = "Portal " + str(i)
            first_x = int(portal_couple.find('first/position/x').text) * TILE_SIZE
            first_y = int(portal_couple.find('first/position/y').text) * TILE_SIZE
            first_pos = (first_x, first_y)
            second_x = int(portal_couple.find('second/position/x').text) * TILE_SIZE
            second_y = int(portal_couple.find('second/position/y').text) * TILE_SIZE
            second_pos = (second_x, second_y)
            sprite = 'imgs/dungeon_crawl/' + portal_couple.find('sprite').text.strip()
            self.portals.append(Portals(name, first_pos, second_pos, sprite))
            i += 1
        #Load fountains
        fountains_infos = {}
        self.fountains = []
        for fountain in tree.xpath("/level/fountains/fountain"):
            name = fountain.find('type').text.strip()
            x = int(fountain.find('position/x').text) * TILE_SIZE
            y = int(fountain.find('position/y').text) * TILE_SIZE
            pos = (x, y)
            if name not in fountains_infos:
                fountains_infos[name] = etree.parse('data/fountains/' + name + '.xml').getroot()
            sprite = 'imgs/dungeon_crawl/' + fountains_infos[name].find('sprite').text.strip()
            self.fountains.append(Fountain(name, pos, sprite))
        #Load breakables
        self.breakables = []
        for breakable in tree.xpath("/level/breakables/breakable"):
            name = "Breakable"
            x = int(breakable.find('position/x').text) * TILE_SIZE
            y = int(breakable.find('position/y').text) * TILE_SIZE
            pos = (x, y)
            sprite = 'imgs/dungeon_crawl/dungeon/' + breakable.find('sprite').text.strip()
            res = int(breakable.find('resistance').text.strip())
            self.breakables.append(Breakable(name, pos, sprite, res))

        #Store all entities
        self.entities = self.players + self.foes + self.chests + self.portals + self.fountains + self.breakables

        #Load obstacles
        self.obstacles = []
        for obstacle in tree.xpath("/level/obstacles/position"):
            x = int(obstacle.find('x').text) * TILE_SIZE
            y = int(obstacle.find('y').text) * TILE_SIZE
            pos = (x, y)
            self.obstacles.append(pos)

        self.item_infos = {}
        self.selected_item = None
        self.turn = 1
        self.animation = None
        '''Possible turn :
                - P : Player's turn
                - O : Opponent's turn
                - A : Ally's turn
        '''
        self.side_turn = 'P'
        self.selected_player = None
        self.watched_ent = None
        self.possible_moves = None
        self.possible_attacks = None
        self.active_menu = None
        self.background_menus = []
        self.hovered_ent = None
        self.sidebar = Sidebar((MENU_WIDTH, MENU_HEIGHT), (0, MAP_HEIGHT), SIDEBAR_SPRITE)

    def update_state(self):
        if self.animation:
            return
        if self.selected_player:
            if self.selected_player.get_move():
                self.selected_player.move()
            if self.selected_player.get_state() == 3 and not self.active_menu:
                self.create_player_menu()
        if self.side_turn == 'P':
            turn_finished = True
            for player in self.players:
                if not player.turn_is_finished():
                    turn_finished = False
            if turn_finished:
                self.side_turn = 'O'
                self.begin_turn()
        elif self.side_turn == 'O':
            for foe in self.foes:
                state = foe.get_state()
                if state != 3:
                    self.foe_action(foe)
                    break
            else:
                self.new_turn()


    def display(self, win):
        win.blit(self.map, (0, 0))
        self.sidebar.display(win, self.turn, self.hovered_ent)
        for ent in self.entities:
            ent.display(win)
            if isinstance(ent, Destroyable):
                ent.display_hp(win)
        if self.selected_player:
            #If player is waiting to move
            state = self.selected_player.get_state()
            if state == 1:
                self.show_possible_actions(self.selected_player, win, self.possible_moves, self.possible_attacks)
            elif state == 4:
                self.show_possible_attacks(self.selected_player, win, self.possible_attacks)
        elif self.watched_ent:
            self.show_possible_actions(self.watched_ent, win, self.possible_moves, self.possible_attacks)

        if self.animation:
            if self.animation.anim(win):
                self.animation = None

        for menu in self.background_menus:
            if menu[1]:
                menu[0].display(win)
        if self.active_menu:
            self.active_menu.display(win)

    @staticmethod
    def determine_hp_color(hp, hp_max):
        if hp == hp_max:
            return WHITE
        if hp >= hp_max * 0.75:
            return GREEN
        if hp >= hp_max * 0.5:
            return YELLOW
        if hp >= hp_max * 0.30:
            return ORANGE
        else:
            return RED

    def show_possible_actions(self, movable, win, possible_moves, possible_attacks):
        self.show_possible_moves(movable, win, possible_moves)
        self.show_possible_attacks(movable, win, possible_attacks)

    def show_possible_attacks(self, movable, win, possible_attacks):
        for tile in possible_attacks:
            if movable.get_pos() != tile:
                blit_alpha(win, ATTACKABLE, tile, ATTACKABLE_OPACITY)

    def show_possible_moves(self, movable, win, possible_moves):
        for (tile, level) in possible_moves.items():
            if movable.get_pos() != tile:
                blit_alpha(win, LANDING, tile, LANDING_OPACITY)

    def get_possible_moves(self, pos, max_moves):
        tiles = {pos: 0}
        tiles_prev_level = tiles
        for i in range(1, max_moves + 1):
            tiles_next_level = {}
            for tile in tiles_prev_level:
                for x in range(-1, 1 + 1):
                    for y in {1 - abs(x), -1 + abs(x)}:
                        case_x = tile[0] + (x * TILE_SIZE)
                        case_y = tile[1] + (y * TILE_SIZE)
                        case_pos = (case_x, case_y)
                        if self.case_is_empty(case_pos) and not case_pos in tiles:
                            tiles_next_level[case_pos] = i
            tiles.update(tiles_prev_level)
            tiles_prev_level = tiles_next_level
        tiles.update(tiles_prev_level)
        return tiles

    def get_possible_attacks(self, possible_moves, reach, from_ally_side):
        tiles = []

        ents = list(self.breakables)
        if from_ally_side:
            ents += self.foes
        else:
            ents += self.players

        for ent in ents:
            pos = ent.get_pos()
            for i in range(1, reach + 1):
                for x in range(-1, i + 1):
                    for y in {i - abs(x), -i + abs(x)}:
                        case_x = pos[0] + (x * TILE_SIZE)
                        case_y = pos[1] + (y * TILE_SIZE)
                        case_pos = (case_x, case_y)
                        if case_pos in possible_moves:
                            tiles.append(ent.get_pos())

        return set(tiles)

    def case_is_empty(self, case):
        #Check all entities
        ent_cases = []
        for ent in self.entities:
            pos = ent.get_pos()
            if type(pos) == list:
                for el in pos:
                    ent_cases.append(el)
            else:
                ent_cases.append(pos)
        return case > (0, 0) and case < (MAP_WIDTH, MAP_HEIGHT) and case not in ent_cases and case not in self.obstacles

    def get_target_from_case(self, case, prnt=False):
        # Check all entities
        for ent in self.foes + self.players + self.breakables:
            pos = ent.get_pos()
            if pos == case:
                return ent
        return False

    def determine_path_to(self, case_from, case_to, distance):
        path = [case_to]
        current_case = case_to
        while distance[current_case] > 1:
            # Check for neighbour cases
            available_cases = self.get_possible_moves(current_case, 1)
            for case in available_cases:
                if case in distance:
                    dist = distance[case]
                    if dist < distance[current_case]:
                        current_case = case
                        path.insert(0, current_case)
        return path

    def create_player_menu(self):
        player_rect = self.selected_player.get_rect()
        entries = [[{'name': 'Inventory', 'id': 1}], [{'name': 'Status', 'id': 2}], [{'name': 'Wait', 'id': 3}]]
        if self.get_possible_attacks({(player_rect.x, player_rect.y): 0}, 1, True):
            entries.insert(0, [{'name': 'Attack', 'id': 0}])
        for row in entries:
            for entry in row:
                entry['type'] = 'button'

        self.active_menu = InfoBox("Select an action", "imgs/interface/PopUpMenu.png", entries, ACTION_MENU_WIDTH, el_rect_linked=player_rect)

    def duel(self, attacker, target):
        damages = attacker.attack(target)
        # If target has less than 0 HP at the end of the duel
        if not target.attacked(attacker, damages):
            self.entities.remove(target)
            collec = None
            if isinstance(target, Foe):
                collec = self.foes
            elif isinstance(target, Player):
                collec = self.players
            elif isinstance(target, Breakable):
                collec = self.breakables
            collec.remove(target)

    def foe_action(self, foe):
        if foe.get_state() == 0:
            pos = foe.get_pos()
            possible_moves = self.get_possible_moves(pos, foe.get_max_moves())
            move = random.choice(list(possible_moves.keys()))
            path = self.determine_path_to(pos, move, possible_moves)
            foe.set_move(path)
        elif foe.get_state() == 1:
            foe.move()
        elif foe.get_state() == 2:
            # Foe try to attack someone
            possible_attacks = self.get_possible_attacks([foe.get_pos()], 1, False)
            if possible_attacks:
                ent_attacked = self.get_target_from_case(random.choice(list(possible_attacks)))
                self.duel(foe, ent_attacked)
            foe.end_turn()

    @staticmethod
    def create_inventory_entries(items):
        entries = []
        row = []
        for i, it in enumerate(items):
            entry = {'type': 'item_button', 'item': it, 'index': i}
            row.append(entry)
            if len(row) == 2:
                entries.append(row)
                row = []
        if row:
            entries.append(row)

        return entries

    def execute_action(self, action):
        if not action:
            return
        method_id = action[0]
        args = action[1]
        # Close menu : Active menu is closed
        if method_id == -1:
            self.active_menu = None
            if self.background_menus:
                self.active_menu = self.background_menus.pop()[0]
        # Attack action : Character has to choose a target
        elif method_id == 0:
            self.selected_player.choose_target()
            self.possible_attacks = self.get_possible_attacks([self.selected_player.get_pos()], 1, True)
            self.background_menus.append([self.active_menu, False])
            self.active_menu = None
        # Item action : Character's inventory is opened
        elif method_id == 1:
            self.background_menus.append([self.active_menu, True])

            items_max = self.selected_player.get_nb_items_max()

            items = list(self.selected_player.get_items())
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            entries = Level.create_inventory_entries(items)

            self.active_menu = InfoBox("Inventory", "imgs/Interface/PopUpMenu.png", entries, ITEM_MENU_WIDTH, close_button=True)
        # Display player's status
        elif method_id == 2:
            self.background_menus.append([self.active_menu, True])

            hp = self.selected_player.get_hp()
            hp_max = self.selected_player.get_hp_max()

            xp = self.selected_player.get_xp()
            xp_next_level = self.selected_player.get_next_lvl_xp()

            entries = [[{'type': 'text', 'color': GREEN, 'text': 'Name :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': self.selected_player.get_formatted_name()}],
                       [{'type': 'text', 'color': GREEN, 'text': 'Class :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': self.selected_player.get_formatted_classes()}],
                       [{'type': 'text', 'color': GREEN, 'text': 'Level :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': str(self.selected_player.get_lvl())}],
                       [{'type': 'text', 'color': GOLD, 'text': '    -> XP :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': str(xp) + ' / ' + str(xp_next_level)}],
                       [{'type': 'text', 'color': WHITE, 'text': 'STATS', 'font': MENU_SUB_TITLE_FONT, 'margin': (10, 0, 10, 0)}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'HP :'},
                        {'type': 'text', 'text': str(hp) + ' / ' + str(hp_max), 'color': Level.determine_hp_color(hp, hp_max)}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'MOVE :'},
                        {'type': 'text', 'text': str(self.selected_player.get_max_moves())}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'ATTACK :'},
                        {'type': 'text', 'text': str(self.selected_player.get_strength())}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'DEFENSE :'},
                        {'type': 'text', 'text': str(self.selected_player.get_defense())}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'MAGICAL RES :'},
                        {'type': 'text', 'text': str(self.selected_player.get_resistance())}],
                       [{'type': 'text', 'color': WHITE, 'text': 'ALTERATIONS', 'font': MENU_SUB_TITLE_FONT, 'margin': (10, 0, 10, 0)}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': self.selected_player.get_formatted_alterations()}]]

            self.active_menu = InfoBox("Status", "imgs/Interface/PopUpMenu.png", entries, STATUS_MENU_WIDTH, close_button=True)
        # Wait action : Given Character's turn is finished
        elif method_id == 3:
            self.selected_item = None
            self.selected_player.turn_finished()
            self.selected_player = None
            self.possible_moves = None
            self.possible_attacks = None
            self.background_menus = []
            self.active_menu = None
        # Watch item action : Open a menu to act with a given item
        elif method_id == 5:
            self.background_menus.append([self.active_menu, True])

            item_button_pos = args[0]
            item_index = args[1]

            self.selected_item = self.selected_player.get_item(item_index)

            formatted_item_name = self.selected_item.get_formatted_name()

            entries = [
                [{'name': 'Info', 'id': 6}],
                [{'name': 'Throw', 'id': 7}]
            ]

            if isinstance(self.selected_item, Consumable):
                entries.insert(0, [{'name': 'Use', 'id': 8}])
            elif isinstance(self.selected_item, Equipment):
                entries.insert(0, [{'name': 'Equip', 'id': 9}])

            for row in entries:
                for entry in row:
                    entry['type'] = 'button'

            item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0], ITEM_BUTTON_MENU_SIZE[1])
            self.active_menu = InfoBox(formatted_item_name, "imgs/Interface/PopUpMenu.png", entries, ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=True)

        # Get info about an item
        elif method_id == 6:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()
            description = self.selected_item.get_description()

            entries = [[{'type' : 'text', 'text' : description, 'font' : ITEM_DESC_FONT, 'margin' : (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "imgs/Interface/PopUpMenu.png", entries, ITEM_INFO_MENU_WIDTH, close_button=True)

        # Remove an item from the inventory
        elif method_id == 7:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            # Remove item from inventory according to the index
            self.selected_player.remove_item(self.selected_item)

            items_max = self.selected_player.get_nb_items_max()

            items = list(self.selected_player.get_items())
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            entries = Level.create_inventory_entries(items)

            # Cancel item menu
            self.background_menus.pop()
            # Update the inventory menu (i.e. first menu backward)
            self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            remove_msg_entries = [[{'type': 'text', 'text': 'Item has been thrown away.', 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "imgs/Interface/PopUpMenu.png", remove_msg_entries, ITEM_DELETE_MENU_WIDTH, close_button=True)
        # Use an item from the inventory
        elif method_id == 8:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            #Try to use the object
            used, result_msg = self.selected_player.use_item(self.selected_item)

            #Inventory display is update if object has been used
            if used:
                items_max = self.selected_player.get_nb_items_max()

                items = list(self.selected_player.get_items())
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "imgs/Interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=True)
        # Equip an item
        elif method_id == 9:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            #Try to equip the item
            equipped = self.selected_player.equip(self.selected_item)

            result_msg = "The item can't be equipped : You already have an item of the same type equipped."
            if equipped:
                result_msg = "The item has been equipped"

                #Item has been removed from inventory
                items_max = self.selected_player.get_nb_items_max()

                items = list(self.selected_player.get_items())
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "imgs/Interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=True)

    def begin_turn(self):
        if self.side_turn == 'P':
            for player in self.players:
                player.new_turn()
        elif self.side_turn == 'O':
            for foe in self.foes:
                foe.new_turn()

    def new_turn(self):
        self.turn += 1
        self.side_turn = 'P'
        self.begin_turn()
        NEW_TURN.blit(NEW_TURN_TEXT, NEW_TURN_TEXT_POS)
        self.animation = Animation([{'sprite': NEW_TURN, 'pos': NEW_TURN_POS}], 60)

    def click(self, button, pos):
        #No event if there is an animation or it is not player turn
        if not self.animation and self.side_turn == 'P':
            #1 is equals to left button
            if button == 1:
                if self.active_menu:
                    self.execute_action(self.active_menu.click(pos))
                else:
                    if self.selected_player:
                        state = self.selected_player.get_state()
                        if state == 1:
                            for move in self.possible_moves:
                                if pg.Rect(move, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                    path = self.determine_path_to(self.selected_player.get_pos(), move, self.possible_moves)
                                    self.selected_player.set_move(path)
                                    return
                        if state == 4:
                            for attack in self.possible_attacks:
                                if pg.Rect(attack, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                    ent = self.get_target_from_case(attack, True)
                                    self.duel(self.selected_player, ent)
                                    #Turn finished
                                    self.execute_action((3, None))
                                    return
                    for player in self.players:
                        if player.is_on_pos(pos) and not player == self.selected_player:
                            player.set_selected(True)
                            self.selected_player = player
                            self.possible_moves = self.get_possible_moves(player.get_pos(), player.get_max_moves())
                            self.possible_attacks = self.get_possible_attacks(self.possible_moves, 1, True)
                            return
            #3 is equals to right button
            if button == 3:
                if self.selected_player and self.selected_player.get_state() == 1:
                    self.selected_player.set_selected(False)
                    self.selected_player = None
                    self.possible_moves = None
                if self.watched_ent:
                    self.watched_ent = None
                    self.possible_moves = False
                    self.possible_attacks = False

    def button_down(self, button, pos):
        # 3 is equals to right button
        if button == 3:
            if not self.selected_player and self.side_turn == 'P':
                for ent in self.entities:
                    if ent.get_rect().collidepoint(pos):
                        pos = ent.get_pos()
                        self.watched_ent = ent
                        self.possible_moves = self.get_possible_moves(pos, ent.get_max_moves())
                        self.possible_attacks = self.get_possible_attacks(self.possible_moves, 1, isinstance(ent, Character))
                        return

    def motion(self, pos):
        if self.active_menu:
            self.active_menu.motion(pos)
        else:
            self.hovered_ent = None
            for ent in self.foes + self.players + self.breakables:
                if ent.get_rect().collidepoint(pos):
                    self.hovered_ent = ent
                    return
