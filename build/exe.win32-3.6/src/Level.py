import pygame as pg
from lxml import etree
import random

from src.Destroyable import Destroyable
from src.Key import Key
from src.Equipment import Equipment
from src.Weapon import Weapon
from src.Effect import Effect
from src.Potion import Potion
from src.Consumable import Consumable
from src.Spellbook import Spellbook
from src.Character import Character
from src.Movable import Movable
from src.Player import Player
from src.Foe import Foe
from src.Chest import Chest
from src.Portal import Portal
from src.Fountain import Fountain
from src.Breakable import Breakable
from src.InfoBox import InfoBox
from src.Sidebar import Sidebar
from src.Animation import Animation
from src.Mission import Mission

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MARINE_BLUE = (34, 61, 200)
ORANGE = (255, 140, 0)
YELLOW = (143, 143, 5)
LIGHT_YELLOW = (255, 255, 0)
GOLD = (200, 172, 34)
BROWN = (139, 69, 19)
MAROON = (128, 0, 0)
BROWN_RED = (165, 42, 42)
TURQUOISE = (64, 224, 208)


TILE_SIZE = 48
MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10

TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 46)

MENU_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 26)
MENU_SUB_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)
ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITALIC_ITEM_FONT = pg.font.Font('fonts/minya_nouvelle_it.ttf', 14)


LANDING_SPRITE = 'imgs/dungeon_crawl/misc/move.png'
LANDING = pg.transform.scale(pg.image.load(LANDING_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
LANDING_OPACITY = 40
ATTACKABLE_SPRITE = 'imgs/dungeon_crawl/misc/attackable.png'
ATTACKABLE = pg.transform.scale(pg.image.load(ATTACKABLE_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
ATTACKABLE_OPACITY = 40
INTERACTION_SPRITE = 'imgs/dungeon_crawl/misc/landing.png'
INTERACTION = pg.transform.scale(pg.image.load(INTERACTION_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
INTERACTION_OPACITY = 100

BUTTON_MENU_SIZE = (150, 30)
CLOSE_BUTTON_SIZE = (150, 50)
ITEM_BUTTON_MENU_SIZE = (180, TILE_SIZE + 30)
MENU_WIDTH = TILE_SIZE * 20
MENU_HEIGHT = 100

ACTION_MENU_WIDTH = 200
ITEM_MENU_WIDTH = 550
ITEM_INFO_MENU_WIDTH = 800
ITEM_DELETE_MENU_WIDTH = 350
STATUS_MENU_WIDTH = 300
STATUS_INFO_MENU_WIDTH = 500
EQUIPMENT_MENU_WIDTH = 500

MARGINTOP = 10

SIDEBAR_SPRITE = 'imgs/interface/sidebar.png'

NEW_TURN_SPRITE = 'imgs/interface/new_turn.png'
NEW_TURN = pg.transform.scale(pg.image.load(NEW_TURN_SPRITE).convert_alpha(), (int(392 * 1.5), int(107 * 1.5)))
NEW_TURN_POS = (MAP_WIDTH / 2 - NEW_TURN.get_width() / 2, MAP_HEIGHT / 2 - NEW_TURN.get_height() / 2)
NEW_TURN_TEXT = TITLE_FONT.render("New turn !", 1, WHITE)
NEW_TURN_TEXT_POS = (NEW_TURN.get_width() / 2 - NEW_TURN_TEXT.get_width() / 2, NEW_TURN.get_height() / 2 - NEW_TURN_TEXT.get_height() / 2)

VICTORY = NEW_TURN.copy()
VICTORY_POS = NEW_TURN_POS
VICTORY_TEXT = TITLE_FONT.render("VICTORY !", 1, WHITE)
VICTORY_TEXT_POS = (VICTORY.get_width() / 2 - VICTORY_TEXT.get_width() / 2, VICTORY.get_height() / 2 - VICTORY_TEXT.get_height() / 2)

DEFEAT = NEW_TURN.copy()
DEFEAT_POS = NEW_TURN_POS
DEFEAT_TEXT = TITLE_FONT.render("DEFEAT !", 1, WHITE)
DEFEAT_TEXT_POS = (DEFEAT.get_width() / 2 - DEFEAT_TEXT.get_width() / 2, DEFEAT.get_height() / 2 - DEFEAT_TEXT.get_height() / 2)

# Interaction ids
#  > Generic
#    - To close any menu
CLOSE_ACTION_ID = -1

# > Main character menu
MAIN_MENU_ID = 0
#   - Access to inventory
INV_ACTION_ID = 0
#   - Access to equipment
EQUIPMENT_ACTION_ID = 1
#   - Access to status screen
STATUS_ACTION_ID = 2
#   - End character's turn
WAIT_ACTION_ID = 3
#   - Attack an opponent
ATTACK_ACTION_ID = 4
#   - Open a chest
OPEN_CHEST_ACTION_ID = 5
#   - Use portal
USE_PORTAL_ACTION_ID = 6
#   - Drink in fountain
DRINK_ACTION_ID = 7
#   - Valid mission position
TAKE_ACTION_ID = 8

# > Inventory menu
INV_MENU_ID = 1
#   - Interact with item
INTERAC_ITEM_ACTION_ID = 0

# > Item menu
ITEM_MENU_ID = 2
#   - Use item
USE_ITEM_ACTION_ID = 0
#   - Get infos about item
INFO_ITEM_ACTION_ID = 1
#   - Throw item
THROW_ITEM_ACTION_ID = 2
#   - Equip item
EQUIP_ITEM_ACTION_ID = 3
#   - Unequip item
UNEQUIP_ITEM_ACTION_ID = 4

# > Status menu
STATUS_MENU_ID = 3
#   - Get infos about alteration
INFO_ALTERATION_ACTION_ID = 0

# > Equipment menu
EQUIPMENT_MENU_ID = 4
#   - Interact with equipment
INTERAC_EQUIPMENT_ACTION_ID = 0


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
            tree = etree.parse(directory + "data.xml").getroot()
            #Load players
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
                defense = 0
                res = 0
                hp = 10
                move = 5
                strength = 1
                player = Player(name, pos, sprite, hp, defense, res, move, strength, ['warrior'], equipments, lvl)

                items_id = ['life_potion', 'key', 'club']
                for name in items_id:
                    item = Level.parse_item_file(name)
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
                lvl = int(foe.find('lvl').text.strip())
                if name not in foes_infos:
                    foes_infos[name] = etree.parse('data/foes/' + name + '.xml').getroot()
                sprite = 'imgs/dungeon_crawl/monster/' + foes_infos[name].find('sprite').text.strip()
                hp = int(foes_infos[name].find('hp').text.strip())
                move = int(foes_infos[name].find('move').text.strip())
                strength = int(foes_infos[name].find('strength').text.strip())
                defense = int(foes_infos[name].find('def').text.strip())
                res = int(foes_infos[name].find('res').text.strip())
                xp_gain = int(foes_infos[name].find('xp_gain').text.strip())
                self.foes.append(Foe(name, pos, sprite, hp, defense, res, move, strength, xp_gain, lvl))
            #Load chests
            self.chests = []
            for chest in tree.xpath("/level/chests/chest"):
                name = "Chest"
                x = int(chest.find('position/x').text) * TILE_SIZE
                y = int(chest.find('position/y').text) * TILE_SIZE
                pos = (x, y)
                sprite_closed = 'imgs/dungeon_crawl/' + chest.find('closed/sprite').text.strip()
                sprite_opened = 'imgs/dungeon_crawl/' + chest.find('opened/sprite').text.strip()
                potential_items = []
                for item in chest.xpath("contains/item"):
                    name = item.find('name').text.strip()
                    it = Level.parse_item_file(name)
                    proba = float(item.find('probability').text)

                    potential_items.append((proba, it))
                self.chests.append(Chest(name, pos, sprite_closed, sprite_opened, potential_items))
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
                first_portal = Portal(name, first_pos, sprite)
                second_portal = Portal(name, second_pos, sprite)
                Portal.link_portals(first_portal, second_portal)
                self.portals.append(first_portal)
                self.portals.append(second_portal)
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
                sprite_empty = 'imgs/dungeon_crawl/' + fountains_infos[name].find('sprite_empty').text.strip()
                effect_name = fountains_infos[name].find('effect').text.strip()
                power = int(fountains_infos[name].find('power').text.strip())
                duration = int(fountains_infos[name].find('duration').text.strip())
                effect = Effect(effect_name, power, duration)
                times = int(fountains_infos[name].find('times').text.strip())
                self.fountains.append(Fountain(name, pos, sprite, sprite_empty, effect, times))
            #Load breakables
            self.breakables = []
            for breakable in tree.xpath("/level/breakables/breakable"):
                name = "Breakable"
                x = int(breakable.find('position/x').text) * TILE_SIZE
                y = int(breakable.find('position/y').text) * TILE_SIZE
                pos = (x, y)
                sprite = 'imgs/dungeon_crawl/dungeon/' + breakable.find('sprite').text.strip()
                hp = int(breakable.find('resistance').text.strip())
                self.breakables.append(Breakable(name, pos, sprite, hp, 0, 0))

            #Store all entities
            self.entities = self.players + self.foes + self.chests + self.portals + self.fountains + self.breakables

            #Load obstacles
            self.obstacles = []
            for obstacle in tree.xpath("/level/obstacles/position"):
                x = int(obstacle.find('x').text) * TILE_SIZE
                y = int(obstacle.find('y').text) * TILE_SIZE
                pos = (x, y)
                self.obstacles.append(pos)
            # Load missions
            self.missions = []

            #  > Load main mission
            main_mission = tree.find('missions/main')
            nature = main_mission.find('type').text
            main = True
            positions = []
            desc = main_mission.find('description').text.strip()
            nb_players = len(self.players)
            if nature == 'position':
                for coords in main_mission.xpath('position'):
                    x = int(coords.find('x').text) * TILE_SIZE
                    y = int(coords.find('y').text) * TILE_SIZE
                    pos = (x, y)
                    positions.append(pos)
                mission = Mission(main, nature, positions, desc, nb_players)
            self.missions.append(mission)

            # Booleans for end game
            self.victory = False
            self.defeat = False
            self.game_ended = False

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
            self.possible_moves = []
            self.possible_attacks = []
            self.possible_interactions = []
            self.active_menu = None
            self.background_menus = []
            self.hovered_ent = None
            self.sidebar = Sidebar((MENU_WIDTH, MENU_HEIGHT), (0, MAP_HEIGHT), SIDEBAR_SPRITE, self.missions.copy())
            self.wait_for_dest_tp = False

        @staticmethod
        def parse_item_file(name):
            it_tree_root = etree.parse('data/items/' + name + '.xml').getroot()

            sprite = 'imgs/dungeon_crawl/item/' + it_tree_root.find('sprite').text.strip()
            info = it_tree_root.find('info').text.strip()
            category = it_tree_root.find('category').text.strip()

            item = None
            if category == 'potion':
                effect_name = it_tree_root.find('effect').text.strip()
                power = int(it_tree_root.find('power').text.strip())
                duration = int(it_tree_root.find('duration').text.strip())
                effect = Effect(effect_name, power, duration)
                item = Potion(name, sprite, info, effect)
            elif category == 'armor':
                body_part = it_tree_root.find('bodypart').text.strip()
                defense = int(it_tree_root.find('def').text.strip())
                weight = int(it_tree_root.find('weight').text.strip())
                equipped_sprite = 'imgs/dungeon_crawl/player/' + body_part + '/' + it_tree_root.find(
                    'equipped_sprite').text.strip()
                item = Equipment(name, sprite, info, equipped_sprite, body_part, defense, 0, 0, weight)
            elif category == 'weapon':
                power = int(it_tree_root.find('power').text.strip())
                weight = int(it_tree_root.find('weight').text.strip())
                fragility = int(it_tree_root.find('fragility').text.strip())
                equipped_sprite = 'imgs/dungeon_crawl/player/hand_right/' + it_tree_root.find(
                    'equipped_sprite').text.strip()
                item = Weapon(name, sprite, info, equipped_sprite, power, weight, fragility, range)
            elif category == 'key':
                item = Key(name, sprite, info)
            elif category == 'spellbook':
                spell = it_tree_root.find('effect').text.strip()
                item = Spellbook(name, sprite, info, spell)

            return item

        def is_ended(self):
            return not self.animation and self.game_ended

        def update_state(self):
            if self.animation:
                return
            if self.victory:
                self.active_menu = None
                self.background_menus = []
                VICTORY.blit(VICTORY_TEXT, VICTORY_TEXT_POS)
                self.animation = Animation([{'sprite': VICTORY, 'pos': DEFEAT_POS}], 180)
                self.game_ended = True
                return
            if not self.players:
                self.defeat = True
            if self.defeat:
                self.active_menu = None
                self.background_menus = []
                DEFEAT.blit(DEFEAT_TEXT, DEFEAT_TEXT_POS)
                self.animation = Animation([{'sprite': DEFEAT, 'pos': VICTORY_POS}], 180)
                self.game_ended = True
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
                # If player is waiting to move
                state = self.selected_player.get_state()
                if state == 1:
                    self.show_possible_actions(self.selected_player, win)
                elif state == 4:
                    if self.possible_attacks:
                        self.show_possible_attacks(self.selected_player, win)
                    elif self.possible_interactions:
                        self.show_possible_interactions(win)
            elif self.watched_ent:
                self.show_possible_actions(self.watched_ent, win)

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

        def show_possible_actions(self, movable, win):
            self.show_possible_moves(movable, win)
            self.show_possible_attacks(movable, win)

        def show_possible_attacks(self, movable, win):
            for tile in self.possible_attacks:
                if movable.get_pos() != tile:
                    blit_alpha(win, ATTACKABLE, tile, ATTACKABLE_OPACITY)

        def show_possible_moves(self, movable, win):
            for tile in self.possible_moves.keys():
                if movable.get_pos() != tile:
                    blit_alpha(win, LANDING, tile, LANDING_OPACITY)

        def show_possible_interactions(self, win):
            for tile in self.possible_interactions:
                blit_alpha(win, INTERACTION, tile, INTERACTION_OPACITY)

        def get_next_cases(self, pos):
            tiles = []
            for x in range(-1, 2):
                for y in {1 - abs(x), -1 + abs(x)}:
                    case_x = pos[0] + (x * TILE_SIZE)
                    case_y = pos[1] + (y * TILE_SIZE)
                    case_pos = (case_x, case_y)
                    if case_pos > (0, 0) and case_pos < (MAP_WIDTH, MAP_HEIGHT):
                        case = self.get_entity_on_case(case_pos)
                        tiles.append(case)
            return tiles

        def get_possible_moves(self, pos, max_moves):
            tiles = {pos: 0}
            tiles_prev_level = tiles
            for i in range(1, max_moves + 1):
                tiles_next_level = {}
                for tile in tiles_prev_level:
                    for x in range(-1, 2):
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
            # Check all entities
            ent_cases = []
            for ent in self.entities:
                pos = ent.get_pos()
                ent_cases.append(pos)
            return case > (0, 0) and case < (MAP_WIDTH, MAP_HEIGHT) and case not in ent_cases and case not in self.obstacles

        def get_entity_on_case(self, case):
            # Check all entities
            for ent in self.entities:
                pos = ent.get_pos()
                if pos == case:
                    return ent
            return None

        def determine_path_to(self, case_to, distance):
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
            entries = [[{'name': 'Inventory', 'id': INV_ACTION_ID}], [{'name': 'Equipment', 'id': EQUIPMENT_ACTION_ID}],
                       [{'name': 'Status', 'id': STATUS_ACTION_ID}], [{'name': 'Wait', 'id': WAIT_ACTION_ID}]]

            # Options flags
            chest_option = False
            portal_option = False
            fountain_option = False
            for case_content in self.get_next_cases((player_rect.x, player_rect.y)):
                if isinstance(case_content, Chest) and not case_content.is_open() and not chest_option:
                    entries.insert(0, [{'name': 'Open', 'id': OPEN_CHEST_ACTION_ID}])
                    chest_option = True
                if isinstance(case_content, Portal) and not portal_option:
                    entries.insert(0, [{'name': 'Use Portal', 'id': USE_PORTAL_ACTION_ID}])
                    portal_option = True
                if isinstance(case_content, Fountain) and not fountain_option:
                    entries.insert(0, [{'name': 'Drink', 'id': DRINK_ACTION_ID}])
                    fountain_option = True

            # Check if player is on mission position
            player_pos = self.selected_player.get_pos()
            for mission in self.missions:
                if mission.get_type() == 'position':
                    if mission.pos_is_valid(player_pos):
                        entries.insert(0, [{'name': 'Take', 'id': TAKE_ACTION_ID}])

            if self.get_possible_attacks({(player_rect.x, player_rect.y): 0}, 1, True):
                entries.insert(0, [{'name': 'Attack', 'id': ATTACK_ACTION_ID}])

            for row in entries:
                for entry in row:
                    entry['type'] = 'button'

            self.active_menu = InfoBox("Select an action", MAIN_MENU_ID, "imgs/interface/PopUpMenu.png", entries, ACTION_MENU_WIDTH, el_rect_linked=player_rect)

        def interact(self, actor, target, target_pos):
            if isinstance(actor, Player):
                # Check if target is an empty pos
                if not target:
                    if self.wait_for_dest_tp:
                        self.wait_for_dest_tp = False
                        actor.set_pos(target_pos)

                        # Turn is finished
                        self.execute_action(MAIN_MENU_ID, (WAIT_ACTION_ID, None))
                # Check if player try to open a chest
                elif isinstance(target, Chest):
                    if actor.has_free_space():
                        # Key is used to open the chest
                        actor.remove_key()

                        # Get object inside the chest
                        item = target.open()
                        actor.set_item(item)

                        # Get item infos
                        name = item.get_formatted_name()
                        entry_item = {'type': 'item_button', 'item': item, 'index': -1, 'disabled': True}

                        entries = [[entry_item],
                                   [{'type': 'text', 'text': "Item has been added to your inventory", 'font': ITEM_DESC_FONT}]]
                        self.active_menu = InfoBox(name, "", "imgs/interface/PopUpMenu.png",
                                                   entries, ITEM_MENU_WIDTH, close_button=True)
                        # No more menu : turn is finished
                        self.background_menus = []
                    else:
                        self.active_menu = InfoBox("You have no free space in your inventory.", "", "imgs/interface/PopUpMenu.png",
                                                   [], ITEM_MENU_WIDTH, close_button=True)
                # Check if player try to use a portal
                elif isinstance(target, Portal):
                    new_based_pos = target.get_linked_portal().get_pos()
                    possible_pos = self.get_possible_moves(new_based_pos, 1)
                    # Remove portal pos since player cannot be on the portal
                    del possible_pos[new_based_pos]
                    if possible_pos:
                        self.possible_interactions = possible_pos.keys()
                        self.wait_for_dest_tp = True
                    else:
                        self.active_menu = InfoBox("There is no free square around the other portal", "",
                                                   "imgs/interface/PopUpMenu.png",
                                                   [], ITEM_MENU_WIDTH, close_button=True)
                elif isinstance(target, Fountain):
                    entries = target.drink(actor)
                    self.active_menu = InfoBox(target.get_formatted_name(), "", "imgs/interface/PopUpMenu.png",
                                               entries, ITEM_MENU_WIDTH, close_button=True)

                    # No more menu : turn is finished
                    self.background_menus = []

        def duel(self, attacker, target):
            damages = attacker.attack(target)
            # If target has less than 0 HP at the end of the duel
            if not target.attacked(attacker, damages):

                # XP up
                if isinstance(target, Movable) and isinstance(attacker, Player):
                    xp_gain = target.get_xp_obtained()
                    attacker.earn_xp(xp_gain)

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
                path = self.determine_path_to(move, possible_moves)
                foe.set_move(path)
            elif foe.get_state() == 1:
                foe.move()
            elif foe.get_state() == 2:
                # Foe try to attack someone
                possible_attacks = self.get_possible_attacks([foe.get_pos()], 1, False)
                if possible_attacks:
                    ent_attacked = self.get_entity_on_case(random.choice(list(possible_attacks)))
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

        @staticmethod
        def create_equipment_entries(equipments):
            entries = []
            body_parts = [['head'], ['body'], ['wrist'], ['left_hand', 'right_hand'], ['legs'], ['feet']]
            for part in body_parts:
                row = []
                for member in part:
                    entry = {'type': 'item_button', 'item': None, 'index': -1, 'subtype': 'equip'}
                    for i, eq in enumerate(equipments):
                        if member == eq.get_body_part():
                            entry = {'type': 'item_button', 'item': eq, 'index': i, 'subtype': 'equip'}
                    row.append(entry)
                entries.append(row)
            return entries

        @staticmethod
        def create_status_entries(player):
            # Health
            hp = player.get_hp()
            hp_max = player.get_hp_max()

            # XP
            xp = player.get_xp()
            xp_next_level = player.get_next_lvl_xp()

            entries = [[{'type': 'text', 'color': GREEN, 'text': 'Name :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': player.get_formatted_name()}],
                       [{'type': 'text', 'color': GREEN, 'text': 'Class :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': player.get_formatted_classes()}],
                       [{'type': 'text', 'color': GREEN, 'text': 'Level :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': str(player.get_lvl())}],
                       [{'type': 'text', 'color': GOLD, 'text': '    -> XP :', 'font': ITALIC_ITEM_FONT},
                        {'type': 'text', 'text': str(xp) + ' / ' + str(xp_next_level)}],
                       [{'type': 'text', 'color': WHITE, 'text': 'STATS', 'font': MENU_SUB_TITLE_FONT, 'margin': (10, 0, 10, 0)}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'HP :'},
                        {'type': 'text', 'text': str(hp) + ' / ' + str(hp_max), 'color': Level.determine_hp_color(hp, hp_max)}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'MOVE :'},
                        {'type': 'text', 'text': str(player.get_max_moves())}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'ATTACK :'},
                        {'type': 'text', 'text': str(player.get_strength())}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'DEFENSE :'},
                        {'type': 'text', 'text': str(player.get_defense())}],
                       [{'type': 'text', 'color': MARINE_BLUE, 'text': 'MAGICAL RES :'},
                        {'type': 'text', 'text': str(player.get_resistance())}],
                       [{'type': 'text', 'color': WHITE, 'text': 'ALTERATIONS', 'font': MENU_SUB_TITLE_FONT,
                         'margin': (10, 0, 10, 0)}]]

            alts = player.get_alterations()

            if not alts:
                entries.append([{'type': 'text', 'color': MARINE_BLUE, 'text': 'None'}])

            for alt in alts:
                entries.append([{'type': 'text_button', 'name': alt.get_formatted_name(), 'id': INFO_ALTERATION_ACTION_ID, 'color': WHITE, 'color_hover': TURQUOISE, 'obj': alt}])

            return entries

        def execute_main_menu_action(self, method_id, args):
            # Attack action : Character has to choose a target
            if method_id == ATTACK_ACTION_ID:
                self.selected_player.choose_target()
                self.possible_attacks = self.get_possible_attacks([self.selected_player.get_pos()], 1, True)
                self.background_menus.append([self.active_menu, False])
                self.active_menu = None
            # Item action : Character's inventory is opened
            elif method_id == INV_ACTION_ID:
                self.background_menus.append([self.active_menu, True])

                items_max = self.selected_player.get_nb_items_max()

                items = list(self.selected_player.get_items())
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items)

                self.active_menu = InfoBox("Inventory", INV_MENU_ID, "imgs/Interface/PopUpMenu.png", entries,
                                           ITEM_MENU_WIDTH, close_button=True)
            # Equipment action : open the equipment screen
            elif method_id == EQUIPMENT_ACTION_ID:
                self.background_menus.append([self.active_menu, True])

                equipments = self.selected_player.get_equipments()
                entries = Level.create_equipment_entries(equipments)

                self.active_menu = InfoBox("Equipment", EQUIPMENT_MENU_ID, "imgs/Interface/PopUpMenu.png", entries, EQUIPMENT_MENU_WIDTH, close_button=True)
            # Display player's status
            elif method_id == STATUS_ACTION_ID:
                self.background_menus.append([self.active_menu, True])

                entries = Level.create_status_entries(self.selected_player)

                self.active_menu = InfoBox("Status", STATUS_MENU_ID, "imgs/Interface/PopUpMenu.png", entries, STATUS_MENU_WIDTH,
                                           close_button=True)
            # Wait action : Given Character's turn is finished
            elif method_id == WAIT_ACTION_ID:
                self.selected_item = None
                self.selected_player.turn_finished()
                self.selected_player = None
                self.possible_moves = []
                self.possible_attacks = []
                self.possible_interactions = []
                self.background_menus = []
                self.active_menu = None
            # Open a chest
            elif method_id == OPEN_CHEST_ACTION_ID:
                # Check if player has a key
                has_key = False
                for it in self.selected_player.get_items():
                    if isinstance(it, Key):
                        has_key = True
                        break

                if not has_key:
                    self.background_menus.append([self.active_menu, True])
                    self.active_menu = InfoBox("You have no key to open a chest", "", "imgs/Interface/PopUpMenu.png", [],
                                               ITEM_MENU_WIDTH, close_button=True)
                else:
                    self.background_menus.append([self.active_menu, False])
                    self.active_menu = None
                    self.selected_player.choose_interaction()
                    self.possible_interactions = []
                    for ent in self.get_next_cases(self.selected_player.get_pos()):
                        if isinstance(ent, Chest) and not ent.is_open():
                            self.possible_interactions.append(ent.get_pos())
            # Use a portal
            elif method_id == USE_PORTAL_ACTION_ID:
                self.background_menus.append([self.active_menu, False])
                self.active_menu = None
                self.selected_player.choose_interaction()
                self.possible_interactions = []
                for ent in self.get_next_cases(self.selected_player.get_pos()):
                    if isinstance(ent, Portal):
                        self.possible_interactions.append(ent.get_pos())
            # Drink into a fountain
            elif method_id == DRINK_ACTION_ID:
                self.background_menus.append([self.active_menu, False])
                self.active_menu = None
                self.selected_player.choose_interaction()
                self.possible_interactions = []
                for ent in self.get_next_cases(self.selected_player.get_pos()):
                    if isinstance(ent, Fountain):
                        self.possible_interactions.append(ent.get_pos())
            # Valid a mission position
            elif method_id == TAKE_ACTION_ID:
                for mission in self.missions:
                    if mission.get_type() == 'position':
                        # Verify that character is not the last if the mission is not the main one
                        if mission.is_main() or len(self.players) > 1:
                            if mission.pos_is_valid(self.selected_player.get_pos()):
                                # Check if player is able to complete this objective
                                if mission.update_state(self.selected_player):
                                    self.players.remove(self.selected_player)
                                    if not self.players:
                                        self.victory = True

        def execute_inv_action(self, method_id, args):
            # Watch item action : Open a menu to act with a given item
            if method_id == INTERAC_ITEM_ACTION_ID:
                self.background_menus.append([self.active_menu, True])

                item_button_pos = args[0]
                item = args[1]

                self.selected_item = item

                formatted_item_name = self.selected_item.get_formatted_name()

                entries = [
                    [{'name': 'Info', 'id': INFO_ITEM_ACTION_ID}],
                    [{'name': 'Throw', 'id': THROW_ITEM_ACTION_ID}]
                ]

                if isinstance(self.selected_item, Consumable):
                    entries.insert(0, [{'name': 'Use', 'id': USE_ITEM_ACTION_ID}])
                elif isinstance(self.selected_item, Equipment):
                    if self.selected_player.has_equipment(self.selected_item):
                        entries.insert(0, [{'name': 'Unequip', 'id': UNEQUIP_ITEM_ACTION_ID}])
                    else:
                        entries.insert(0, [{'name': 'Equip', 'id': EQUIP_ITEM_ACTION_ID}])

                for row in entries:
                    for entry in row:
                        entry['type'] = 'button'

                item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0],
                                    ITEM_BUTTON_MENU_SIZE[1])
                self.active_menu = InfoBox(formatted_item_name, ITEM_MENU_ID, "imgs/Interface/PopUpMenu.png",
                                           entries,
                                           ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=True)

        def execute_equipment_action(self, method_id, args):
            # Watch item action : Open a menu to act with a given item
            if method_id == INTERAC_ITEM_ACTION_ID:
                self.background_menus.append([self.active_menu, True])

                item_button_pos = args[0]
                item = args[1]

                self.selected_item = item

                formatted_item_name = self.selected_item.get_formatted_name()

                entries = [
                    [{'name': 'Info', 'id': INFO_ITEM_ACTION_ID}],
                    [{'name': 'Throw', 'id': THROW_ITEM_ACTION_ID}]
                ]

                if isinstance(self.selected_item, Consumable):
                    entries.insert(0, [{'name': 'Use', 'id': USE_ITEM_ACTION_ID}])
                elif isinstance(self.selected_item, Equipment):
                    if self.selected_player.has_equipment(self.selected_item):
                        entries.insert(0, [{'name': 'Unequip', 'id': UNEQUIP_ITEM_ACTION_ID}])
                    else:
                        entries.insert(0, [{'name': 'Equip', 'id': EQUIP_ITEM_ACTION_ID}])

                for row in entries:
                    for entry in row:
                        entry['type'] = 'button'

                item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0],
                                    ITEM_BUTTON_MENU_SIZE[1])
                self.active_menu = InfoBox(formatted_item_name, ITEM_MENU_ID, "imgs/Interface/PopUpMenu.png",
                                           entries,
                                           ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=True)

        def execute_item_action(self, method_id, args):
            # Get info about an item
            if method_id == INFO_ITEM_ACTION_ID:
                self.background_menus.append([self.active_menu, False])

                formatted_item_name = self.selected_item.get_formatted_name()
                description = self.selected_item.get_description()

                entries = [[{'type': 'text', 'text': description, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
                self.active_menu = InfoBox(formatted_item_name, "", "imgs/Interface/PopUpMenu.png", entries, ITEM_INFO_MENU_WIDTH, close_button=True)
            # Remove an item
            elif method_id == THROW_ITEM_ACTION_ID:
                self.background_menus.append([self.active_menu, False])

                formatted_item_name = self.selected_item.get_formatted_name()

                # Remove item from inventory/equipment according to the index
                if self.selected_player.has_equipment(self.selected_item):
                    self.selected_player.remove_equipment(self.selected_item)
                    equipments = self.selected_player.get_equipments()
                    entries = Level.create_equipment_entries(equipments)
                else:
                    self.selected_player.remove_item(self.selected_item)
                    items_max = self.selected_player.get_nb_items_max()
                    items = self.selected_player.get_items()
                    free_spaces = items_max - len(items)
                    items += [None] * free_spaces
                    entries = Level.create_inventory_entries(items)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

                remove_msg_entries = [[{'type': 'text', 'text': 'Item has been thrown away.', 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
                self.active_menu = InfoBox(formatted_item_name, "", "imgs/Interface/PopUpMenu.png", remove_msg_entries, ITEM_DELETE_MENU_WIDTH, close_button=True)
            # Use an item from the inventory
            elif method_id == USE_ITEM_ACTION_ID:
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
                self.active_menu = InfoBox(formatted_item_name, "", "imgs/Interface/PopUpMenu.png", entries,
                                           ITEM_INFO_MENU_WIDTH, close_button=True)
            # Equip an item
            elif method_id == EQUIP_ITEM_ACTION_ID:
                self.background_menus.append([self.active_menu, False])

                formatted_item_name = self.selected_item.get_formatted_name()

                #Try to equip the item
                equipped = self.selected_player.equip(self.selected_item)

                result_msg = "Item can't be equipped : You already wear an equipment of the same type."
                if equipped:
                    result_msg = "The item has been equipped"

                    #Item has been removed from inventory
                    items_max = self.selected_player.get_nb_items_max()

                    items = self.selected_player.get_items()
                    free_spaces = items_max - len(items)
                    items += [None] * free_spaces

                    entries = Level.create_inventory_entries(items)

                    # Cancel item menu
                    self.background_menus.pop()
                    # Update the inventory menu (i.e. first menu backward)
                    self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

                entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
                self.active_menu = InfoBox(formatted_item_name, "", "imgs/Interface/PopUpMenu.png", entries,
                                           ITEM_INFO_MENU_WIDTH, close_button=True)
            # Unequip an item
            elif method_id == UNEQUIP_ITEM_ACTION_ID:
                self.background_menus.append([self.active_menu, False])

                formatted_item_name = self.selected_item.get_formatted_name()

                # Try to unequip the item
                unequipped = self.selected_player.unequip(self.selected_item)
                result_msg = "The item can't be unequipped : Not enough space in your inventory."
                if unequipped:
                    result_msg = "The item has been unequipped"

                    # Update equipment screen content
                    equipments = self.selected_player.get_equipments()
                    entries = Level.create_equipment_entries(equipments)

                    # Cancel item menu
                    self.background_menus.pop()
                    # Update the inventory menu (i.e. first menu backward)
                    self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

                entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
                self.active_menu = InfoBox(formatted_item_name, "", "imgs/Interface/PopUpMenu.png", entries,
                                           ITEM_INFO_MENU_WIDTH, close_button=True)

        def execute_status_action(self, method_id, args):
            # Get infos about an alteration
            if method_id == INFO_ALTERATION_ACTION_ID:
                self.background_menus.append([self.active_menu, True])

                alteration = args[1]

                formatted_name = alteration.get_formatted_name()
                description = alteration.get_description()
                turns_left = alteration.get_turns_left()

                entries = [[{'type': 'text', 'text': description, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}],
                           [{'type': 'text', 'text': 'Turns left : ' + str(turns_left), 'font': ITEM_DESC_FONT, 'margin': (0, 0, 10, 0), 'color': ORANGE}]]
                self.active_menu = InfoBox(formatted_name, "", "imgs/Interface/PopUpMenu.png", entries, STATUS_INFO_MENU_WIDTH, close_button=True)

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
                else:
                    # Turn is finished
                    self.execute_action(MAIN_MENU_ID, (WAIT_ACTION_ID, None))

            # Search from which menu came the action
            if menu_type == MAIN_MENU_ID:
                self.execute_main_menu_action(method_id, args)
            elif menu_type == INV_MENU_ID:
                self.execute_inv_action(method_id, args)
            elif menu_type == EQUIPMENT_MENU_ID:
                self.execute_equipment_action(method_id, args)
            elif menu_type == ITEM_MENU_ID:
                self.execute_item_action(method_id, args)
            elif menu_type == STATUS_MENU_ID:
                self.execute_status_action(method_id, args)
            else:
                print("Unknown menu... : " + menu_type)

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
            # No event if there is an animation or it is not player turn
            if not self.animation and self.side_turn == 'P':
                # 1 is equals to left button
                if button == 1:
                    if self.active_menu:
                        self.execute_action(self.active_menu.get_type(), self.active_menu.click(pos))
                    else:
                        if self.selected_player:
                            state = self.selected_player.get_state()
                            if state == 1:
                                for move in self.possible_moves:
                                    if pg.Rect(move, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                        path = self.determine_path_to(move, self.possible_moves)
                                        self.selected_player.set_move(path)
                                        self.possible_moves = []
                                        self.possible_attacks = []
                                        return
                            if state == 4:
                                for attack in self.possible_attacks:
                                    if pg.Rect(attack, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                        ent = self.get_entity_on_case(attack)
                                        self.duel(self.selected_player, ent)
                                        #Turn is finished
                                        self.execute_action(MAIN_MENU_ID, (WAIT_ACTION_ID, None))
                                        return
                                for interact in self.possible_interactions:
                                    if pg.Rect(interact, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                        ent = self.get_entity_on_case(interact)
                                        self.interact(self.selected_player, ent, interact)
                                        return
                        for player in self.players:
                            if player.is_on_pos(pos) and not player == self.selected_player and not player.turn_is_finished():
                                player.set_selected(True)
                                self.selected_player = player
                                self.possible_moves = self.get_possible_moves(player.get_pos(), player.get_max_moves())
                                self.possible_attacks = self.get_possible_attacks(self.possible_moves, 1, True)
                                return
                # 3 is equals to right button
                if button == 3:
                    if self.selected_player and self.selected_player.get_state() == 1:
                        self.selected_player.set_selected(False)
                        self.selected_player = None
                        self.possible_moves = []
                    if self.watched_ent:
                        self.watched_ent = None
                        self.possible_moves = []
                        self.possible_attacks = []

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
