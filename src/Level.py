from src.fonts import *
from src import LoadFromXMLManager as Loader
from src.Building import Building
from src.Shop import Shop
from src.Equipment import Equipment
from src.Consumable import Consumable
from src.Character import Character
from src.Player import Player
from src.Foe import Foe
from src.Movable import *
from src.Chest import Chest
from src.Portal import Portal
from src.Fountain import Fountain
from src.Breakable import Breakable
from src.InfoBox import InfoBox
from src.Sidebar import Sidebar
from src.Animation import Animation
from src.Mission import MissionType
from src.Menus import *
from src.SaveStateManager import SaveStateManager

MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10

LANDING_SPRITE = 'imgs/dungeon_crawl/misc/move.png'
LANDING = pg.transform.scale(pg.image.load(LANDING_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
LANDING_OPACITY = 80
ATTACKABLE_SPRITE = 'imgs/dungeon_crawl/misc/attackable.png'
ATTACKABLE = pg.transform.scale(pg.image.load(ATTACKABLE_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
ATTACKABLE_OPACITY = 80
INTERACTION_SPRITE = 'imgs/dungeon_crawl/misc/landing.png'
INTERACTION = pg.transform.scale(pg.image.load(INTERACTION_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
INTERACTION_OPACITY = 500

BUTTON_MENU_SIZE = (150, 30)
CLOSE_BUTTON_SIZE = (150, 50)
ITEM_BUTTON_MENU_SIZE = (180, TILE_SIZE + 30)

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
NEW_TURN_TEXT_POS = (NEW_TURN.get_width() / 2 - NEW_TURN_TEXT.get_width() / 2,
                     NEW_TURN.get_height() / 2 - NEW_TURN_TEXT.get_height() / 2)

VICTORY = NEW_TURN.copy()
VICTORY_POS = NEW_TURN_POS
VICTORY_TEXT = TITLE_FONT.render("VICTORY !", 1, WHITE)
VICTORY_TEXT_POS = (VICTORY.get_width() / 2 - VICTORY_TEXT.get_width() / 2,
                    VICTORY.get_height() / 2 - VICTORY_TEXT.get_height() / 2)
VICTORY.blit(VICTORY_TEXT, VICTORY_TEXT_POS)

DEFEAT = NEW_TURN.copy()
DEFEAT_POS = NEW_TURN_POS
DEFEAT_TEXT = TITLE_FONT.render("DEFEAT !", 1, WHITE)
DEFEAT_TEXT_POS = (DEFEAT.get_width() / 2 - DEFEAT_TEXT.get_width() / 2,
                   DEFEAT.get_height() / 2 - DEFEAT_TEXT.get_height() / 2)
DEFEAT.blit(DEFEAT_TEXT, DEFEAT_TEXT_POS)


def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pg.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)


class Status(IntEnum):
    INITIALIZATION = 0,
    IN_PROGRESS = 1,
    ENDED_VICTORY = 2,
    ENDED_DEFEAT = 3


class EntityTurn(IntEnum):
    PLAYER = 0,
    ALLIES = 1,
    FOES = 2

    def get_next(self):
        next_value = self.value + 1 if self.value + 1 < len(EntityTurn.__members__) else 0
        return EntityTurn(next_value)


class Level:
    def __init__(self, directory, players, nb_level, status='INITIALIZATION', turn=0, data=None):
        # Store directory path if player wants to save and exit game
        self.directory = directory
        self.map = pg.image.load(directory + 'map.png')

        self.quit_request = False

        self.nb_level = nb_level

        self.players = players

        self.entities = [] + self.players

        self.allies = []
        self.foes = []
        self.chests = []
        self.portals = []
        self.fountains = []
        self.breakables = []
        self.buildings = []
        self.obstacles = []

        # Reading of the XML file
        tree = etree.parse(directory + "data.xml").getroot()
        data_tree = tree
        from_save = False

        if status != Status.IN_PROGRESS.name:
            # Load available tiles for characters' placement
            self.possible_placements = Loader.load_placements(tree.findall('placementArea/position'))

            # Game is new, players' positions should be initialized
            if data is None:
                # Set initial pos of players arbitrarily
                for player in self.players:
                    for tile in self.possible_placements:
                        if self.case_is_empty(tile):
                            player.set_initial_pos(tile)
                            break
        else:
            # Data is extracted from saved game
            data_tree = data
            from_save = True

        # Load allies
        self.allies.extend(Loader.load_entities(Character, data_tree.findall('allies/ally'), from_save))

        # Load foes
        self.foes.extend(Loader.load_entities(Foe, data_tree.findall('foes/foe'), from_save))

        # Load breakables
        self.breakables.extend(Loader.load_entities(Breakable, data_tree.findall('breakables/breakable'), from_save))

        # Load chests
        self.chests.extend(Loader.load_entities(Chest, data_tree.findall('chests/chest'), from_save))

        # Load buildings
        self.buildings.extend(Loader.load_entities(Building, data_tree.findall('buildings/building'), from_save))

        # Load fountains
        self.fountains.extend(Loader.load_entities(Fountain, data_tree.findall('fountains/fountain'), from_save))

        # Load portals
        self.portals.extend(Loader.load_entities(Portal, data_tree.findall('portals/couple'), from_save))

        # Store all entities
        self.entities += \
            self.allies + self.foes + self.chests + self.portals + self.fountains + self.breakables + self.buildings

        # Load obstacles
        self.obstacles.extend(Loader.load_obstacles(tree.find('obstacles')))

        # Load missions
        self.missions, self.main_mission = Loader.load_missions(tree, self.players)

        # Booleans for end game
        self.victory = False
        self.defeat = False

        self.game_phase = Status[status]

        self.side_turn = EntityTurn.PLAYER

        self.turn = turn
        self.selected_item = None
        self.animation = None
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

    def save_game(self):
        save_state_manager = SaveStateManager(self)
        save_state_manager.save_game()

    def exit_game(self):
        # At next update, level will be destroyed
        self.quit_request = True

    def game_started(self):
        return self.game_phase is not Status.INITIALIZATION

    def end_level(self, anim_surf, pos):
        self.active_menu = None
        self.background_menus = []
        self.animation = Animation([{'sprite': anim_surf, 'pos': pos}], 180)

    def update_state(self):
        if self.quit_request:
            return self.game_phase

        if self.animation:
            if self.animation.anim():
                self.animation = None
                if self.game_phase > Status.IN_PROGRESS:
                    # End game animation is finished, level can be quit
                    self.exit_game()
            return None

        if not self.players and self.game_phase is Status.IN_PROGRESS:
            if not self.main_mission.succeeded_chars:
                self.defeat = True
            else:
                self.victory = True
        if self.victory or self.defeat:
            if self.victory:
                self.end_level(VICTORY, VICTORY_POS)
                self.game_phase = Status.ENDED_VICTORY
            else:
                self.end_level(DEFEAT, DEFEAT_POS)
                self.game_phase = Status.ENDED_DEFEAT
            # Set values to False to avoid infinite repetitions
            self.victory = False
            self.defeat = False
            return None
        if self.selected_player:
            if self.selected_player.move():
                # If movement is finished
                self.create_player_menu()
            return None

        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.allies
        elif self.side_turn is EntityTurn.FOES:
            entities = self.foes

        for ent in entities:
            if not ent.turn_is_finished():
                if self.side_turn is not EntityTurn.PLAYER:
                    self.entity_action(ent, (self.side_turn is EntityTurn.ALLIES))
                break
        else:
            self.side_turn = self.side_turn.get_next()
            self.begin_turn()

        return None

    def display(self, win):
        win.blit(self.map, (0, 0))
        self.sidebar.display(win, self.turn, self.hovered_ent, self.nb_level)
        for ent in self.entities:
            ent.display(win)
            if isinstance(ent, Destroyable):
                ent.display_hp(win)

        if self.watched_ent:
            self.show_possible_actions(self.watched_ent, win)

        if self.animation:
            self.animation.display(win)

        # If the game hasn't yet started
        if self.game_phase is Status.INITIALIZATION:
            self.show_possible_placements(win)
        else:
            if self.selected_player:
                # If player is waiting to move
                if self.possible_moves:
                    self.show_possible_actions(self.selected_player, win)
                elif self.possible_attacks:
                    self.show_possible_attacks(self.selected_player, win)
                elif self.possible_interactions:
                    self.show_possible_interactions(win)

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
            if movable.pos != tile:
                blit_alpha(win, ATTACKABLE, tile, ATTACKABLE_OPACITY)

    def show_possible_moves(self, movable, win):
        for tile in self.possible_moves.keys():
            if movable.pos != tile:
                blit_alpha(win, LANDING, tile, LANDING_OPACITY)

    def show_possible_interactions(self, win):
        for tile in self.possible_interactions:
            blit_alpha(win, INTERACTION, tile, INTERACTION_OPACITY)

    def show_possible_placements(self, win):
        for tile in self.possible_placements:
            blit_alpha(win, LANDING, tile, LANDING_OPACITY)

    def get_next_cases(self, pos):
        tiles = []
        for x in range(-1, 2):
            for y in {1 - abs(x), -1 + abs(x)}:
                case_x = pos[0] + (x * TILE_SIZE)
                case_y = pos[1] + (y * TILE_SIZE)
                case_pos = (case_x, case_y)
                if (0, 0) < case_pos < (MAP_WIDTH, MAP_HEIGHT):
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
                        if self.case_is_empty(case_pos) and case_pos not in tiles:
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
            ents += self.allies + self.players

        for ent in ents:
            pos = ent.pos
            for i in reach:
                for x in range(-i, i + 1):
                    for y in {i - abs(x), -i + abs(x)}:
                        case_x = pos[0] + (x * TILE_SIZE)
                        case_y = pos[1] + (y * TILE_SIZE)
                        case_pos = (case_x, case_y)
                        if case_pos in possible_moves:
                            tiles.append(ent.pos)

        return set(tiles)

    def case_is_empty(self, case):
        # Check all entities
        ent_cases = []
        for ent in self.entities:
            ent_cases.append(ent.pos)
        return (0, 0) < case < (MAP_WIDTH, MAP_HEIGHT) and case not in ent_cases and case not in self.obstacles

    def get_entity_on_case(self, case):
        # Check all entities
        for ent in self.entities:
            if ent.pos == case:
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

    def create_main_menu(self, pos):
        # Transform pos tuple into rect
        tile = pg.Rect(pos[0], pos[1], 1, 1)
        entries = [[{'name': 'Save', 'id': MainMenu.SAVE}],
                   [{'name': 'Suspend', 'id': MainMenu.SUSPEND}]]

        if self.game_phase is Status.INITIALIZATION:
            entries.append([{'name': 'Start', 'id': MainMenu.START}])
        elif self.game_phase is Status.IN_PROGRESS:
            entries.append([{'name': 'End Turn', 'id': MainMenu.END_TURN}])

        for row in entries:
            for entry in row:
                entry['type'] = 'button'

        # Avoid to create empty menu
        if entries:
            self.active_menu = InfoBox("Main Menu", MainMenu, "imgs/interface/PopUpMenu.png", entries,
                                       ACTION_MENU_WIDTH, el_rect_linked=tile)

    def create_player_menu(self):
        player_rect = self.selected_player.get_rect()
        entries = [[{'name': 'Inventory', 'id': CharacterMenu.INV}],
                   [{'name': 'Equipment', 'id': CharacterMenu.EQUIPMENT}],
                   [{'name': 'Status', 'id': CharacterMenu.STATUS}], [{'name': 'Wait', 'id': CharacterMenu.WAIT}]]

        # Options flags
        chest_option = False
        portal_option = False
        fountain_option = False
        talk_option = False

        case_x = player_rect.x
        case_y = player_rect.y - TILE_SIZE
        case_pos = (case_x, case_y)
        if (0, 0) < case_pos < (MAP_WIDTH, MAP_HEIGHT):
            case = self.get_entity_on_case(case_pos)
            if isinstance(case, Building):
                entries.insert(0, [{'name': 'Visit', 'id': CharacterMenu.VISIT}])

        for case_content in self.get_next_cases((player_rect.x, player_rect.y)):
            if isinstance(case_content, Chest) and not case_content.opened and not chest_option:
                entries.insert(0, [{'name': 'Open', 'id': CharacterMenu.OPEN_CHEST}])
                chest_option = True
            if isinstance(case_content, Portal) and not portal_option:
                entries.insert(0, [{'name': 'Use Portal', 'id': CharacterMenu.USE_PORTAL}])
                portal_option = True
            if isinstance(case_content, Fountain) and not fountain_option:
                entries.insert(0, [{'name': 'Drink', 'id': CharacterMenu.DRINK}])
                fountain_option = True
            if isinstance(case_content, Character) and not isinstance(case_content, Player) and not talk_option:
                entries.insert(0, [{'name': 'Talk', 'id': CharacterMenu.TALK}])
                talk_option = True

        # Check if player is on mission position
        player_pos = self.selected_player.pos
        for mission in self.missions:
            if mission.type is MissionType.POSITION:
                if mission.pos_is_valid(player_pos):
                    entries.insert(0, [{'name': 'Take', 'id': CharacterMenu.TAKE}])

        # Check if player could attack something, according to weapon range
        w = self.selected_player.get_weapon()
        w_range = [1] if w is None else w.reach
        if self.get_possible_attacks({(player_rect.x, player_rect.y): 0}, w_range, True):
            entries.insert(0, [{'name': 'Attack', 'id': CharacterMenu.ATTACK}])

        for row in entries:
            for entry in row:
                entry['type'] = 'button'

        self.active_menu = InfoBox("Select an action", CharacterMenu, "imgs/interface/PopUpMenu.png", entries,
                                   ACTION_MENU_WIDTH, el_rect_linked=player_rect)

    def interact(self, actor, target, target_pos):
        if isinstance(actor, Player):
            # Check if target is an empty pos
            if not target:
                if self.wait_for_dest_tp:
                    self.wait_for_dest_tp = False
                    actor.pos = target_pos

                    # Turn is finished
                    self.execute_action(CharacterMenu, (CharacterMenu.WAIT, None))
            # Check if player tries to open a chest
            elif isinstance(target, Chest):
                if actor.has_free_space():
                    # Key is used to open the chest
                    actor.remove_key()

                    # Get object inside the chest
                    item = target.open()
                    actor.set_item(item)

                    # Get item infos
                    name = item.get_formatted_name()
                    entry_item = {'type': 'item_button', 'item': item, 'index': -1, 'disabled': True,
                                  'id': InventoryMenu.INTERAC_ITEM}

                    entries = [[entry_item],
                               [{'type': 'text', 'text': "Item has been added to your inventory",
                                 'font': ITEM_DESC_FONT}]]
                    self.active_menu = InfoBox(name, "", "imgs/interface/PopUpMenu.png",
                                               entries, ITEM_MENU_WIDTH, close_button=FINAL_ACTION)
                    # No more menu : turn is finished
                    self.background_menus = []
                else:
                    self.active_menu = InfoBox("You have no free space in your inventory.", "",
                                               "imgs/interface/PopUpMenu.png", [], ITEM_MENU_WIDTH,
                                               close_button=UNFINAL_ACTION)
            # Check if player tries to use a portal
            elif isinstance(target, Portal):
                new_based_pos = target.linked_to.pos
                possible_pos = self.get_possible_moves(new_based_pos, 1)
                # Remove portal pos since player cannot be on the portal
                del possible_pos[new_based_pos]
                if possible_pos:
                    self.possible_interactions = possible_pos.keys()
                    self.wait_for_dest_tp = True
                else:
                    self.active_menu = InfoBox("There is no free square around the other portal", "",
                                               "imgs/interface/PopUpMenu.png",
                                               [], ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION)
            # Check if player tries to drink in a fountain
            elif isinstance(target, Fountain):
                entries = target.drink(actor)
                self.active_menu = InfoBox(target.get_formatted_name(), "", "imgs/interface/PopUpMenu.png",
                                           entries, ITEM_MENU_WIDTH, close_button=FINAL_ACTION)

                # No more menu : turn is finished
                self.background_menus = []
                self.possible_interactions = []
            # Check if player tries to talk to a character
            elif isinstance(target, Character):
                entries = target.talk(actor)
                self.active_menu = InfoBox(target.get_formatted_name(), "", "imgs/interface/PopUpMenu.png",
                                           entries, ITEM_MENU_WIDTH, close_button=FINAL_ACTION, title_color=ORANGE)
                # No more menu : turn is finished
                self.background_menus = []
                self.possible_interactions = []
            # Check if player tries to visit a building
            elif isinstance(target, Building):
                type = ""
                # Check if player tries to visit a shop
                if isinstance(target, Shop):
                    type = ShopMenu

                entries = target.interact(actor)
                self.active_menu = InfoBox(target.get_formatted_name(), type, "imgs/interface/PopUpMenu.png",
                                           entries, ITEM_MENU_WIDTH, close_button=FINAL_ACTION, title_color=ORANGE)

                # No more menu : turn is finished
                self.background_menus = []
                self.possible_interactions = []

    def duel(self, attacker, target, kind):
        damages = attacker.attack(target)
        # If target has less than 0 HP at the end of the duel
        if not target.attacked(attacker, damages, kind):
            # XP up
            if isinstance(target, Movable) and isinstance(attacker, Player):
                attacker.earn_xp(target.xp_gain)

            self.entities.remove(target)
            collec = None
            if isinstance(target, Foe):
                collec = self.foes
            elif isinstance(target, Player):
                collec = self.players
            elif isinstance(target, Breakable):
                collec = self.breakables
            elif isinstance(target, Character):
                collec = self.allies
            collec.remove(target)

    def entity_action(self, ent, is_ally):
        possible_moves = self.get_possible_moves(ent.pos, ent.max_moves)
        targets = self.foes if is_ally else self.players + self.allies
        case = ent.act(possible_moves, targets)

        if case:
            if case in possible_moves:
                # Entity choose to move to case
                self.hovered_ent = ent
                path = self.determine_path_to(case, possible_moves)
                ent.set_move(path)
            else:
                # Entity choose to attack the entity on the case
                ent_attacked = self.get_entity_on_case(case)
                self.duel(ent, ent_attacked, ent.attack_kind)
                ent.end_turn()

    @staticmethod
    def create_shop_entries(items, gold):
        entries = []
        row = []
        for i, it in enumerate(items):
            entry = {'type': 'item_button', 'item': it, 'price': it.price, 'index': i, 'id': BuyMenu.INTERAC_BUY}
            row.append(entry)
            if len(row) == 2:
                entries.append(row)
                row = []

        if row:
            entries.append(row)

        # Gold at end
        entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': ITEM_DESC_FONT}]
        entries.append(entry)

        return entries

    @staticmethod
    def create_inventory_entries(items, gold, price=False):
        entries = []
        row = []
        method_id = SellMenu.INTERAC_SELL if price else InventoryMenu.INTERAC_ITEM
        for i, it in enumerate(items):
            entry = {'type': 'item_button', 'item': it, 'index': i, 'id': method_id}
            # Test if price should appeared
            if price and it:
                entry['price'] = it.price // 2 if it.price != 0 else 0
            row.append(entry)
            if len(row) == 2:
                entries.append(row)
                row = []
        if row:
            entries.append(row)

        # Gold at end
        entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': ITEM_DESC_FONT}]
        entries.append(entry)

        return entries

    @staticmethod
    def create_equipment_entries(equipments):
        entries = []
        body_parts = [['head'], ['body'], ['left_hand', 'right_hand'], ['feet']]
        for part in body_parts:
            row = []
            for member in part:
                entry = {'type': 'item_button', 'item': None, 'index': -1, 'subtype': 'equip',
                         'id': InventoryMenu.INTERAC_ITEM}
                for i, eq in enumerate(equipments):
                    if member == eq.body_part:
                        entry = {'type': 'item_button', 'item': eq, 'index': i, 'subtype': 'equip',
                                 'id': InventoryMenu.INTERAC_ITEM}
                row.append(entry)
            entries.append(row)
        return entries

    @staticmethod
    def create_status_entries(player):
        entries = [[{'type': 'text', 'color': GREEN, 'text': 'Name :', 'font': ITALIC_ITEM_FONT},
                    {'type': 'text', 'text': player.get_formatted_name()}],
                   [{'type': 'text', 'color': GREEN, 'text': 'Class :', 'font': ITALIC_ITEM_FONT},
                    {'type': 'text', 'text': player.get_formatted_classes()}],
                   [{'type': 'text', 'color': GREEN, 'text': 'Race :', 'font': ITALIC_ITEM_FONT},
                    {'type': 'text', 'text': player.get_formatted_race()}],
                   [{'type': 'text', 'color': GREEN, 'text': 'Level :', 'font': ITALIC_ITEM_FONT},
                    {'type': 'text', 'text': str(player.lvl)}],
                   [{'type': 'text', 'color': GOLD, 'text': '   XP :', 'font': ITALIC_ITEM_FONT},
                    {'type': 'text', 'text': str(player.xp) + ' / ' + str(player.xp_next_lvl)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'STATS', 'font': MENU_SUB_TITLE_FONT,
                     'margin': (10, 0, 10, 0)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'HP :'},
                    {'type': 'text', 'text': str(player.hp) + ' / ' + str(player.hp_max),
                     'color': Level.determine_hp_color(player.hp, player.hp_max)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'MOVE :'},
                    {'type': 'text', 'text': str(player.max_moves)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'ATTACK :'},
                    {'type': 'text', 'text': str(player.strength)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'DEFENSE :'},
                    {'type': 'text', 'text': str(player.defense)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'MAGICAL RES :'},
                    {'type': 'text', 'text': str(player.res)}],
                   [{'type': 'text', 'color': WHITE, 'text': 'ALTERATIONS', 'font': MENU_SUB_TITLE_FONT,
                     'margin': (10, 0, 10, 0)}]]

        alts = player.alterations

        if not alts:
            entries.append([{'type': 'text', 'color': WHITE, 'text': 'None'}])

        for alt in alts:
            entries.append([{'type': 'text_button', 'name': alt.get_formatted_name(), 'id': StatusMenu.INFO_ALTERATION,
                             'color': WHITE, 'color_hover': TURQUOISE, 'obj': alt}])

        return entries

    def execute_buy_action(self, method_id, args):
        if method_id is BuyMenu.INTERAC_BUY:
            item_button_pos = args[0]
            item = args[1]
            price = args[2]

            self.selected_item = item
            formatted_item_name = self.selected_item.get_formatted_name()

            self.background_menus.append((self.active_menu, True))

            entries = [
                [{'name': 'Buy', 'id': ItemMenu.BUY_ITEM, 'type': 'button', 'args': [price]}],
                [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
            ]
            item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0],
                                ITEM_BUTTON_MENU_SIZE[1])

            self.active_menu = InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                                       entries,
                                       ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)
        else:
            print("Unknown action in buy menu... : " + str(method_id))

    def execute_sell_action(self, method_id, args):
        if method_id is SellMenu.INTERAC_SELL:
            item_button_pos = args[0]
            item = args[1]
            price = args[2]

            self.selected_item = item
            formatted_item_name = self.selected_item.get_formatted_name()

            self.background_menus.append((self.active_menu, True))

            entries = [
                [{'name': 'Sell', 'id': ItemMenu.SELL_ITEM, 'type': 'button', 'args': [price]}],
                [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]

            ]
            item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0],
                                ITEM_BUTTON_MENU_SIZE[1])

            self.active_menu = InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                                       entries,
                                       ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)
        else:
            print("Unknown action in sell menu... : " + str(method_id))

    def execute_shop_action(self, method_id, args):
        if method_id is ShopMenu.BUY:
            shop = args[2][0]

            self.background_menus.append((self.active_menu, False))
            entries = Level.create_shop_entries(shop.items, self.selected_player.gold)
            self.active_menu = InfoBox("Shop - Buying", BuyMenu, "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)
        elif method_id is ShopMenu.SELL:
            items_max = self.selected_player.nb_items_max

            items = list(self.selected_player.items)
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            self.background_menus.append((self.active_menu, False))
            entries = Level.create_inventory_entries(items, self.selected_player.gold, price=True)
            self.active_menu = InfoBox("Shop - Selling", SellMenu, "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)
        else:
            print("Unknown action in shop menu... : " + str(method_id))

    def execute_main_menu_action(self, method_id, args):
        if method_id is MainMenu.START:
            self.game_phase = Status.IN_PROGRESS
            self.active_menu = None
            self.new_turn()
        elif method_id is MainMenu.SAVE:
            self.save_game()
            self.background_menus.append((self.active_menu, True))
            self.active_menu = InfoBox("", "", "imgs/interface/PopUpMenu.png",
                                       [[{'type': 'text', 'text': "Game has been saved",
                                          'font': ITEM_DESC_FONT}]], ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION)
        elif method_id is MainMenu.END_TURN:
            self.active_menu = None
            self.side_turn = self.side_turn.get_next()
            self.begin_turn()
        elif method_id is MainMenu.SUSPEND:
            # Because player choose to leave game before end, it's obviously a defeat
            self.game_phase = Status.ENDED_DEFEAT
            self.exit_game()
        else:
            print("Unknown action in main menu... : " + str(method_id))

    def execute_character_menu_action(self, method_id, args):
        # Attack action : Character has to choose a target
        if method_id is CharacterMenu.ATTACK:
            self.selected_player.choose_target()
            w_range = self.selected_player.get_weapon().reach if self.selected_player.get_weapon() is not None else [1]
            self.possible_attacks = self.get_possible_attacks([self.selected_player.pos], w_range, True)
            self.possible_interactions = []
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
        # Item action : Character's inventory is opened
        elif method_id is CharacterMenu.INV:
            self.background_menus.append((self.active_menu, True))

            items_max = self.selected_player.nb_items_max

            items = list(self.selected_player.items)
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            entries = Level.create_inventory_entries(items, self.selected_player.gold)

            self.active_menu = InfoBox("Inventory", InventoryMenu, "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Equipment action : open the equipment screen
        elif method_id is CharacterMenu.EQUIPMENT:
            self.background_menus.append((self.active_menu, True))

            equipments = list(self.selected_player.equipments)
            entries = Level.create_equipment_entries(equipments)

            self.active_menu = InfoBox("Equipment", EquipmentMenu, "imgs/interface/PopUpMenu.png", entries,
                                       EQUIPMENT_MENU_WIDTH, close_button=True)
        # Display player's status
        elif method_id is CharacterMenu.STATUS:
            self.background_menus.append((self.active_menu, True))

            entries = Level.create_status_entries(self.selected_player)

            self.active_menu = InfoBox("Status", StatusMenu, "imgs/interface/PopUpMenu.png", entries,
                                       STATUS_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Wait action : Given Character's turn is finished
        elif method_id is CharacterMenu.WAIT:
            self.selected_item = None
            self.selected_player.turn_finished()
            self.selected_player = None
            self.possible_moves = []
            self.possible_attacks = []
            self.possible_interactions = []
            self.background_menus = []
            self.active_menu = None
        # Open a chest
        elif method_id is CharacterMenu.OPEN_CHEST:
            # Check if player has a key
            has_key = False
            for it in self.selected_player.items:
                if isinstance(it, Key):
                    has_key = True
                    break

            if not has_key:
                self.background_menus.append((self.active_menu, True))
                self.active_menu = InfoBox("You have no key to open a chest", "", "imgs/interface/PopUpMenu.png", [],
                                           ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION)
            else:
                self.background_menus.append((self.active_menu, False))
                self.active_menu = None
                self.selected_player.choose_target()
                self.possible_interactions = []
                for ent in self.get_next_cases(self.selected_player.pos):
                    if isinstance(ent, Chest) and not ent.opened:
                        self.possible_interactions.append(ent.pos)
        # Use a portal
        elif method_id is CharacterMenu.USE_PORTAL:
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = []
            for ent in self.get_next_cases(self.selected_player.pos):
                if isinstance(ent, Portal):
                    self.possible_interactions.append(ent.pos)
        # Drink into a fountain
        elif method_id is CharacterMenu.DRINK:
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = []
            for ent in self.get_next_cases(self.selected_player.pos):
                if isinstance(ent, Fountain):
                    self.possible_interactions.append(ent.pos)
        elif method_id is CharacterMenu.TALK:
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = []
            for ent in self.get_next_cases(self.selected_player.pos):
                if isinstance(ent, Character):
                    self.possible_interactions.append(ent.pos)
        # Visit a house
        elif method_id is CharacterMenu.VISIT:
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = [(self.selected_player.pos[0], self.selected_player.pos[1] - TILE_SIZE)]
            self.possible_attacks = []
        # Valid a mission position
        elif method_id is CharacterMenu.TAKE:
            for mission in self.missions:
                if mission.type is MissionType.POSITION:
                    # Verify that character is not the last if the mission is not the main one
                    if mission.main or len(self.players) > 1:
                        if mission.pos_is_valid(self.selected_player.pos):
                            # Check if player is able to complete this objective
                            if mission.update_state(self.selected_player):
                                self.players.remove(self.selected_player)
                                self.entities.remove(self.selected_player)
                                if mission.main and mission.ended:
                                    self.victory = True
                                # Turn is finished
                                self.execute_action(CharacterMenu, (CharacterMenu.WAIT, None))

    def execute_inv_action(self, method_id, args):
        # Watch item action : Open a menu to act with a given item
        if method_id is InventoryMenu.INTERAC_ITEM:
            self.background_menus.append((self.active_menu, True))

            item_button_pos = args[0]
            item = args[1]

            self.selected_item = item

            formatted_item_name = self.selected_item.get_formatted_name()

            entries = [
                [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
                [{'name': 'Throw', 'id': ItemMenu.THROW_ITEM}]
            ]

            if isinstance(self.selected_item, Consumable):
                entries.insert(0, [{'name': 'Use', 'id': ItemMenu.USE_ITEM}])
            elif isinstance(self.selected_item, Equipment):
                if self.selected_player.has_equipment(self.selected_item):
                    entries.insert(0, [{'name': 'Unequip', 'id': ItemMenu.UNEQUIP_ITEM}])
                else:
                    entries.insert(0, [{'name': 'Equip', 'id': ItemMenu.EQUIP_ITEM}])

            for row in entries:
                for entry in row:
                    entry['type'] = 'button'

            item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0],
                                ITEM_BUTTON_MENU_SIZE[1])
            self.active_menu = InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                                       entries,
                                       ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)

    def execute_equipment_action(self, method_id, args):
        # Watch item action : Open a menu to act with a given item
        if method_id is InventoryMenu.INTERAC_ITEM:
            self.background_menus.append([self.active_menu, True])

            item_button_pos = args[0]
            item = args[1]

            self.selected_item = item

            formatted_item_name = self.selected_item.get_formatted_name()

            entries = [
                [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
                [{'name': 'Throw', 'id': ItemMenu.THROW_ITEM}]
            ]

            if isinstance(self.selected_item, Consumable):
                entries.insert(0, [{'name': 'Use', 'id': ItemMenu.USE_ITEM}])
            elif isinstance(self.selected_item, Equipment):
                if self.selected_player.has_equipment(self.selected_item):
                    entries.insert(0, [{'name': 'Unequip', 'id': ItemMenu.UNEQUIP_ITEM}])
                else:
                    entries.insert(0, [{'name': 'Equip', 'id': ItemMenu.EQUIP_ITEM}])

            for row in entries:
                for entry in row:
                    entry['type'] = 'button'

            item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_MENU_SIZE[0],
                                ITEM_BUTTON_MENU_SIZE[1])
            self.active_menu = InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                                       entries,
                                       ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)

    def execute_item_action(self, method_id, args):
        # Get info about an item
        if method_id is ItemMenu.INFO_ITEM:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()
            description = self.selected_item.desc

            entries = [[{'type': 'text', 'text': description, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Remove an item
        elif method_id is ItemMenu.THROW_ITEM:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            # Remove item from inventory/equipment according to the index
            if self.selected_player.has_equipment(self.selected_item):
                self.selected_player.remove_equipment(self.selected_item)
                equipments = list(self.selected_player.equipments)
                entries = Level.create_equipment_entries(equipments)
            else:
                self.selected_player.remove_item(self.selected_item)
                items_max = self.selected_player.nb_items_max
                items = list(self.selected_player.items)
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items, self.selected_player.gold)

            # Cancel item menu
            self.background_menus.pop()
            # Update the inventory menu (i.e. first menu backward)
            self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            remove_msg_entries = [[{'type': 'text', 'text': 'Item has been thrown away.', 'font': ITEM_DESC_FONT,
                                    'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", remove_msg_entries,
                                       ITEM_DELETE_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Use an item from the inventory
        elif method_id is ItemMenu.USE_ITEM:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            # Try to use the object
            used, result_msg = self.selected_player.use_item(self.selected_item)

            # Inventory display is update if object has been used
            if used:
                items_max = self.selected_player.nb_items_max

                items = list(self.selected_player.items)
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items, self.selected_player.gold)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Equip an item
        elif method_id is ItemMenu.EQUIP_ITEM:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            # Try to equip the item
            equipped = self.selected_player.equip(self.selected_item)

            result_msg = "Item can't be equipped : you are already wearing an equipment of the same type."
            if equipped:
                result_msg = "The item has been equipped"

                # Item has been removed from inventory
                items_max = self.selected_player.nb_items_max

                items = list(self.selected_player.items)
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items, self.selected_player.gold)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Unequip an item
        elif method_id is ItemMenu.UNEQUIP_ITEM:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            # Try to unequip the item
            unequipped = self.selected_player.unequip(self.selected_item)
            result_msg = "The item can't be unequipped : Not enough space in your inventory."
            if unequipped:
                result_msg = "The item has been unequipped"

                # Update equipment screen content
                entries = Level.create_equipment_entries(self.selected_player.equipments)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Buy an item
        elif method_id is ItemMenu.BUY_ITEM:
            price = args[2][0]
            formatted_item_name = self.selected_item.get_formatted_name()

            # Try to buy the item
            if self.selected_player.gold >= price:
                if len(self.selected_player.items) < self.selected_player.nb_items_max:
                    # Item can be bought
                    self.selected_player.set_item(self.selected_item)
                    self.selected_player.gold -= price
                    result_msg = "The item has been bought."

                    # Update shop screen content (gold total amount has been reduced)
                    shop_menu = self.background_menus[len(self.background_menus) - 1][0]

                    for row in shop_menu.entries:
                        for entry in row:
                            if entry['type'] == 'text':
                                entry['text'] = 'Your gold : ' + str(self.selected_player.gold)

                    shop_menu.update_content(shop_menu.entries)
                else:
                    # Not enough space in inventory
                    result_msg = "Not enough space in inventory to buy this item."
            else:
                # Not enough gold to purchase item
                result_msg = "Not enough gold to buy this item."

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Sell an item
        elif method_id is ItemMenu.SELL_ITEM:
            price = args[2][0]
            formatted_item_name = self.selected_item.get_formatted_name()

            # Sell the item
            if price > 0:
                self.selected_player.remove_item(self.selected_item)
                self.selected_item = None
                self.selected_player.gold += price
                result_msg = "The item has been selled."

                # Update shop screen content (item has been removed from inventory)
                items_max = self.selected_player.nb_items_max

                items = list(self.selected_player.items)
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                entries = Level.create_inventory_entries(items, self.selected_player.gold, price=True)

                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1][0].update_content(entries)
            else:
                result_msg = "This item can't be selled !"
                self.background_menus.append([self.active_menu, False])

            entries = [[{'type': 'text', 'text': result_msg, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        else:
            print("Unknown action in item menu... : " + str(method_id))

    def execute_status_action(self, method_id, args):
        # Get infos about an alteration
        if method_id is StatusMenu.INFO_ALTERATION_ACTION:
            self.background_menus.append([self.active_menu, True])

            alteration = args[1]

            formatted_name = alteration.get_formatted_name()
            turns_left = alteration.get_turns_left()

            entries = [[{'type': 'text', 'text': alteration.desc, 'font': ITEM_DESC_FONT, 'margin': (20, 0, 20, 0)}],
                       [{'type': 'text', 'text': 'Turns left : ' + str(turns_left), 'font': ITEM_DESC_FONT,
                         'margin': (0, 0, 10, 0), 'color': ORANGE}]]
            self.active_menu = InfoBox(formatted_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       STATUS_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)

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
                # Test if active menu is main character's menu, in this case, it should be reloaded
                if self.active_menu.type is CharacterMenu:
                    self.create_player_menu()
            else:
                if len(args) >= 3 and args[2][0] == FINAL_ACTION:
                    # Turn is finished
                    self.execute_action(CharacterMenu, (CharacterMenu.WAIT, None))
            return

        # Search from which menu came the action
        if menu_type is CharacterMenu:
            self.execute_character_menu_action(method_id, args)
        elif menu_type is InventoryMenu:
            self.execute_inv_action(method_id, args)
        elif menu_type is EquipmentMenu:
            self.execute_equipment_action(method_id, args)
        elif menu_type is ItemMenu:
            self.execute_item_action(method_id, args)
        elif menu_type is StatusMenu:
            self.execute_status_action(method_id, args)
        elif menu_type is MainMenu:
            self.execute_main_menu_action(method_id, args)
        elif menu_type is ShopMenu:
            self.execute_shop_action(method_id, args)
        elif menu_type is BuyMenu:
            self.execute_buy_action(method_id, args)
        elif menu_type is SellMenu:
            self.execute_sell_action(method_id, args)
        else:
            print("Unknown menu... : " + str(menu_type))

    def begin_turn(self):
        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            self.new_turn()
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.allies
        elif self.side_turn is EntityTurn.FOES:
            entities = self.foes

        for ent in entities:
            ent.new_turn()

    def new_turn(self):
        self.turn += 1
        NEW_TURN.blit(NEW_TURN_TEXT, NEW_TURN_TEXT_POS)
        self.animation = Animation([{'sprite': NEW_TURN, 'pos': NEW_TURN_POS}], 60)

    def click(self, button, pos):
        # No event if there is an animation or it is not player turn
        if not self.animation and self.side_turn is EntityTurn.PLAYER:
            # 1 is equals to left button
            if button == 1:
                if self.active_menu:
                    self.execute_action(self.active_menu.type, self.active_menu.click(pos))
                else:
                    if self.selected_player is not None:
                        if self.game_phase is not Status.INITIALIZATION:
                            if self.possible_moves:
                                # Player is waiting to move
                                for move in self.possible_moves:
                                    if pg.Rect(move, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                        path = self.determine_path_to(move, self.possible_moves)
                                        self.selected_player.set_move(path)
                                        self.possible_moves = []
                                        self.possible_attacks = []
                                        return
                                # Player click somewhere that is not a valid pos
                                self.selected_player.selected = False
                                self.selected_player = None
                            elif self.possible_attacks:
                                # Player is waiting to attack
                                for attack in self.possible_attacks:
                                    if pg.Rect(attack, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                        ent = self.get_entity_on_case(attack)
                                        attack_kind = self.selected_player.get_weapon().attack_kind if \
                                            self.selected_player.get_weapon() is not None else DamageKind.PHYSICAL
                                        self.duel(self.selected_player, ent, attack_kind)
                                        # Turn is finished
                                        self.execute_action(CharacterMenu, (CharacterMenu.WAIT, None))
                                        return
                            elif self.possible_interactions:
                                # Player is waiting to interact
                                for interact in self.possible_interactions:
                                    if pg.Rect(interact, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                        ent = self.get_entity_on_case(interact)
                                        self.interact(self.selected_player, ent, interact)
                                        return
                        else:
                            # Initialization phase : player try to change the place of the selected character
                            for tile in self.possible_placements:
                                if pg.Rect(tile, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                                    # Test if a character is on the tile, in this case, characters are swapped
                                    ent = self.get_entity_on_case(tile)
                                    if ent:
                                        ent.set_initial_pos(self.selected_player.pos)

                                    self.selected_player.set_initial_pos(tile)
                                    return
                    else:
                        for player in self.players:
                            if player.is_on_pos(pos) and not player.turn_is_finished():
                                if self.selected_player:
                                    self.selected_player.selected = False
                                player.selected = True
                                self.selected_player = player
                                self.possible_moves = self.get_possible_moves(player.pos, player.max_moves)
                                w = self.selected_player.get_weapon()
                                w_range = [1] if w is None else w.reach
                                self.possible_attacks = self.get_possible_attacks(self.possible_moves, w_range, True)
                                return
                        self.create_main_menu(pos)
                    return
            # 3 is equals to right button
            if button == 3:
                if self.selected_player:
                    if self.possible_moves:
                        # Player was waiting to move
                        self.selected_player.selected = False
                        self.selected_player = None
                        self.possible_moves = []
                    elif self.active_menu is not None:
                        self.execute_action(self.active_menu.type, (GenericActions.CLOSE, ""))
                        # Test if player was on character's main menu, in this case, current move should be cancelled
                        if self.active_menu is None:
                            self.selected_player.cancel_move()
                            self.selected_player.selected = False
                            self.selected_player = None
                            self.possible_moves = []
                    # Want to cancel an interaction (not already performed)
                    elif self.possible_interactions or self.possible_attacks:
                        self.selected_player.cancel_interaction()
                        self.possible_interactions = []
                        self.possible_attacks = []
                        self.active_menu = self.background_menus.pop()[0]
                    return
                # Test if player is on main menu
                if self.active_menu is not None:
                    self.execute_action(self.active_menu.type, (GenericActions.CLOSE, ""))
                if self.watched_ent:
                    self.watched_ent = None
                    self.possible_moves = []
                    self.possible_attacks = []

    def button_down(self, button, pos):
        # 3 is equals to right button
        if button == 3:
            if not self.active_menu and not self.selected_player and self.side_turn is EntityTurn.PLAYER:
                for ent in self.entities:
                    if ent.get_rect().collidepoint(pos):
                        pos = ent.pos
                        self.watched_ent = ent
                        self.possible_moves = self.get_possible_moves(pos, ent.max_moves)

                        w_range = [1]
                        # TEMPO : Foes don't currently have weapon so it's impossible to test their range
                        if isinstance(self.watched_ent, Character):
                            w = self.watched_ent.get_weapon()
                            if w is not None:
                                w_range = w.reach

                        self.possible_attacks = self.get_possible_attacks(self.possible_moves,
                                                                          w_range, isinstance(ent, Character))
                        return

    def motion(self, pos):
        if self.active_menu:
            self.active_menu.motion(pos)
        else:
            self.hovered_ent = None
            for ent in self.entities:
                if ent.get_rect().collidepoint(pos):
                    self.hovered_ent = ent
                    return
