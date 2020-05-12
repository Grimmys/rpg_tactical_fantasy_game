from src.fonts import fonts
from src import LoadFromXMLManager as Loader, MenuCreatorManager
from src.Building import Building
from src.Shop import Shop
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

LANDING = None
LANDING_OPACITY = 80
ATTACKABLE = None
ATTACKABLE_OPACITY = 80
INTERACTION = None
INTERACTION_OPACITY = 500

NEW_TURN = None
NEW_TURN_POS = None

VICTORY = None
VICTORY_POS = None

DEFEAT = None
DEFEAT_POS = None


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

    @staticmethod
    def init_constant_sprites():
        global LANDING, ATTACKABLE, INTERACTION, NEW_TURN, NEW_TURN_POS, VICTORY, VICTORY_POS, DEFEAT, DEFEAT_POS
        landing_sprite = 'imgs/dungeon_crawl/misc/move.png'
        LANDING = pg.transform.scale(pg.image.load(landing_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        attackable_sprite = 'imgs/dungeon_crawl/misc/attackable.png'
        ATTACKABLE = pg.transform.scale(pg.image.load(attackable_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        interaction_sprite = 'imgs/dungeon_crawl/misc/landing.png'
        INTERACTION = pg.transform.scale(pg.image.load(interaction_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

        new_turn_sprite = 'imgs/interface/new_turn.png'
        NEW_TURN = pg.transform.scale(pg.image.load(new_turn_sprite).convert_alpha(), (int(392 * 1.5), int(107 * 1.5)))
        VICTORY = NEW_TURN.copy()
        DEFEAT = NEW_TURN.copy()

        NEW_TURN_POS = (MAX_MAP_WIDTH / 2 - NEW_TURN.get_width() / 2, MAX_MAP_HEIGHT / 2 - NEW_TURN.get_height() / 2)
        new_turn_text = fonts['TITLE_FONT'].render("New turn !", 1, WHITE)
        new_turn_text_pos = (NEW_TURN.get_width() / 2 - new_turn_text.get_width() / 2,
                             NEW_TURN.get_height() / 2 - new_turn_text.get_height() / 2)
        NEW_TURN.blit(new_turn_text, new_turn_text_pos)

        VICTORY_POS = NEW_TURN_POS
        victory_text = fonts['TITLE_FONT'].render("VICTORY !", 1, WHITE)
        victory_text_pos = (VICTORY.get_width() / 2 - victory_text.get_width() / 2,
                            VICTORY.get_height() / 2 - victory_text.get_height() / 2)
        VICTORY.blit(victory_text, victory_text_pos)

        DEFEAT_POS = NEW_TURN_POS
        defeat_text = fonts['TITLE_FONT'].render("DEFEAT !", 1, WHITE)
        defeat_text_pos = (DEFEAT.get_width() / 2 - defeat_text.get_width() / 2,
                           DEFEAT.get_height() / 2 - defeat_text.get_height() / 2)
        DEFEAT.blit(defeat_text, defeat_text_pos)

    def __init__(self, directory, players, nb_level, status=Status.INITIALIZATION.name, turn=0, data=None):
        # Store directory path if player wants to save and exit game
        self.directory = directory
        self.quit_request = False
        self.nb_level = nb_level

        # Reading of the XML file
        tree = etree.parse(directory + "data.xml").getroot()
        map_width = int(tree.find('width').text.strip()) * TILE_SIZE
        map_height = int(tree.find('height').text.strip()) * TILE_SIZE
        self.map = {
            'img': pg.image.load(self.directory + 'map.png'),
            'width': map_width,
            'height': map_height,
            'x': (MAX_MAP_WIDTH - map_width) // 2,
            'y': (MAX_MAP_HEIGHT - map_height) // 2,
        }

        # Load events
        self.events = Loader.load_events(tree.find('events'), self.map['x'], self.map['y'])

        if status is Status.INITIALIZATION.name:
            # Load available tiles for characters' placement
            self.possible_placements = Loader.load_placements(tree.findall('placementArea/position'),
                                                              self.map['x'], self.map['y'])

        self.active_menu = None
        if data is None:
            # Game is new
            data_tree = tree
            from_save = False
            if 'before_init' in self.events:
                if 'dialog' in self.events['before_init']:
                    entries = [[{'type': 'text', 'text': s, 'font': fonts['ITEM_DESC_FONT']}]
                               for s in self.events['before_init']['dialog']['talks']]
                    self.active_menu = InfoBox(self.events['before_init']['dialog']['title'], "",
                                               "imgs/interface/PopUpMenu.png",
                                               entries, DIALOG_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)
        else:
            data_tree = data
            from_save = True

        # Load obstacles
        self.obstacles = Loader.load_obstacles(tree.find('obstacles'), self.map['x'], self.map['y'])
        # Load players
        self.players = players
        # List for players who are now longer in the level
        self.passed_players = []

        # Load and store all entities
        gap_x, gap_y = (self.map['x'], self.map['y']) if data is None else (0, 0)
        self.entities = Loader.load_all_entities(data_tree, from_save, gap_x, gap_y)
        self.entities['players'] = self.players

        # Game is new, players' positions should be initialized
        if data is None:
            # Set initial pos of players arbitrarily
            for player in self.players:
                for tile in self.possible_placements:
                    if self.case_is_empty(tile):
                        player.set_initial_pos(tile)
                        break
                else:
                    print("Error ! Not enough free tiles to set players...")

        # Load missions
        self.missions, self.main_mission = Loader.load_missions(tree, self.players, self.map['x'], self.map['y'])

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
        self.possible_moves = {}
        self.possible_attacks = []
        self.possible_interactions = []
        self.background_menus = []
        self.hovered_ent = None
        self.sidebar = Sidebar((MENU_WIDTH, MENU_HEIGHT), (0, MAX_MAP_HEIGHT), self.missions)
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

        # Game can't evolve if there is an active menu
        if self.active_menu is not None:
            return None

        self.main_mission.update_state(entities=self.entities)
        if self.main_mission.ended:
            self.victory = True

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
                interactable_entities = self.entities['chests'] + self.entities['portals'] + \
                                        self.entities['fountains'] + self.entities['allies'] + self.players
                self.active_menu = MenuCreatorManager.create_player_menu(self.selected_player,
                                                                         self.entities['buildings'],
                                                                         interactable_entities, self.missions,
                                                                         self.entities['foes'])
            return None

        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.entities['allies']
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities['foes']

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
        win.blit(self.map['img'], (self.map['x'], self.map['y']))
        self.sidebar.display(win, self.turn, self.hovered_ent, self.nb_level)

        for collection in self.entities.values():
            for ent in collection:
                ent.display(win)
                if isinstance(ent, Destroyable):
                    ent.display_hp(win)

        if self.watched_ent:
            self.show_possible_actions(self.watched_ent, win)

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

        if self.animation:
            self.animation.display(win)
        else:
            for menu in self.background_menus:
                if menu[1]:
                    menu[0].display(win)
            if self.active_menu:
                self.active_menu.display(win)

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

    def start_game(self):
        self.active_menu = None
        self.game_phase = Status.IN_PROGRESS
        self.new_turn()
        if 'after_init' in self.events:
            if 'dialog' in self.events['after_init']:
                entries = [[{'type': 'text', 'text': s, 'font': fonts['ITEM_DESC_FONT']}]
                           for s in self.events['after_init']['dialog']['talks']]
                self.active_menu = InfoBox(self.events['after_init']['dialog']['title'], "",
                                           "imgs/interface/PopUpMenu.png",
                                           entries, DIALOG_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)
            if 'new_player' in self.events['after_init']:
                player = Loader.load_player(self.events['after_init']['new_player']['name'])
                player.pos = self.events['after_init']['new_player']['position']
                self.players.append(player)

    def get_next_cases(self, pos):
        tiles = []
        for x in range(-1, 2):
            for y in {1 - abs(x), -1 + abs(x)}:
                case_x = pos[0] + (x * TILE_SIZE)
                case_y = pos[1] + (y * TILE_SIZE)
                case_pos = (case_x, case_y)
                if (self.map['x'], self.map['y']) < case_pos < (self.map['x'] + self.map['width'], self.map['y'] + self.map['height']):
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

        entities = list(self.entities['breakables'])
        if from_ally_side:
            entities += self.entities['foes']
        else:
            entities += self.entities['allies'] + self.players

        for ent in entities:
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
        min_case = (self.map['x'], self.map['y'])
        max_case = (self.map['x'] + self.map['width'], self.map['y'] + self.map['height'])
        if not(all([(minimum <= case < maximum) for minimum, case, maximum in zip(min_case, case, max_case)])):
            return False

        # Check all entities
        ent_cases = []
        for collection in self.entities.values():
            for ent in collection:
                ent_cases.append(ent.pos)

        return case not in ent_cases and case not in self.obstacles

    def get_entity_on_case(self, case):
        # Check all entities
        for collection in self.entities.values():
            for ent in collection:
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

    def interact(self, actor, target, target_pos):
        # Since player chose his interaction, possible interactions should be reseted
        self.possible_interactions = []

        # Check if target is an empty pos
        if not target:
            if self.wait_for_dest_tp:
                self.wait_for_dest_tp = False
                actor.pos = target_pos

                # Turn is finished
                self.background_menus = []
                self.selected_player.turn_finished()
                self.selected_player = None
        # Check if player tries to open a chest
        elif isinstance(target, Chest):
            if actor.has_free_space():
                # Key is used to open the chest
                actor.remove_key()

                # Get object inside the chest
                item = target.open()
                actor.set_item(item)

                # Get item data
                name = item.get_formatted_name()
                entry_item = {'type': 'item_button', 'item': item, 'index': -1, 'disabled': True,
                              'id': InventoryMenu.INTERAC_ITEM}

                entries = [[entry_item],
                           [{'type': 'text', 'text': "Item has been added to your inventory",
                             'font': fonts['ITEM_DESC_FONT']}]]
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
        # Check if player tries to trade with another player
        elif isinstance(target, Player):
            self.active_menu = MenuCreatorManager.create_trade_menu(self.selected_player, target)
        # Check if player tries to talk to a character
        elif isinstance(target, Character):
            entries = target.talk(actor)
            self.active_menu = InfoBox(target.get_formatted_name(), "", "imgs/interface/PopUpMenu.png",
                                       entries, ITEM_MENU_WIDTH, close_button=FINAL_ACTION, title_color=ORANGE)
            # No more menu : turn is finished
            self.background_menus = []
        # Check if player tries to visit a building
        elif isinstance(target, Building):
            kind = ""
            # Check if player tries to visit a shop
            if isinstance(target, Shop):
                kind = ShopMenu

            entries = target.interact(actor)
            self.active_menu = InfoBox(target.get_formatted_name(), kind, "imgs/interface/PopUpMenu.png",
                                       entries, ITEM_MENU_WIDTH, close_button=FINAL_ACTION, title_color=ORANGE)

            # No more menu : turn is finished
            self.background_menus = []

    def duel(self, attacker, target, kind):
        if isinstance(target, Character) and target.parried():
            # Target parried attack
            msg = attacker.get_formatted_name() + " attacked " + target.get_formatted_name() + \
                  "... But " + target.get_formatted_name() + " parried !"
            entries = [[{'type': 'text', 'text': msg, 'font': fonts['ITEM_DESC_FONT']}]]
        else:
            old_hp = target.hp
            damages = attacker.attack(target)
            remaining_hp = target.attacked(attacker, damages, kind)
            entries = [[{'type': 'text',
                         'text': attacker.get_formatted_name() + " dealed " + str(old_hp - remaining_hp) +
                                 " damages to " + target.get_formatted_name(), 'font': fonts['ITEM_DESC_FONT']}]]
            # If target has less than 0 HP at the end of the duel
            if remaining_hp <= 0:
                entries.append([{'type': 'text', 'text': target.get_formatted_name() + " died !",
                                 'font': fonts['ITEM_DESC_FONT']}])
                # XP up
                if isinstance(target, Foe) and isinstance(attacker, Player):
                    attacker.earn_xp(target.xp_gain)
                    entries.append([{'type': 'text',
                                     'text': attacker.get_formatted_name() + " earned " + str(target.xp_gain) + " XP",
                                     'font': fonts['ITEM_DESC_FONT']}])
                collection = None
                if isinstance(target, Foe):
                    collection = self.entities['foes']
                elif isinstance(target, Player):
                    collection = self.entities['players']
                elif isinstance(target, Breakable):
                    collection = self.entities['breakables']
                elif isinstance(target, Character):
                    collection = self.entities['allies']
                collection.remove(target)
            else:
                entries.append([{'type': 'text', 'text': target.get_formatted_name() + " has now " +
                                                         str(remaining_hp) + " HP",
                                 'font': fonts['ITEM_DESC_FONT']}])

        self.active_menu = InfoBox("Fight Summary", "", "imgs/interface/PopUpMenu.png", entries, BATTLE_SUMMARY_WIDTH,
                                   close_button=UNFINAL_ACTION)

    def entity_action(self, ent, is_ally):
        possible_moves = self.get_possible_moves(ent.pos, ent.max_moves)
        targets = self.entities['foes'] if is_ally else self.players + self.entities['allies']
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

    def execute_buy_action(self, method_id, args):
        if method_id is BuyMenu.INTERAC_BUY:
            item_button_pos = args[0]
            item = args[1]
            price = args[2][0]

            self.selected_item = item

            self.background_menus.append((self.active_menu, True))
            self.active_menu = MenuCreatorManager.create_item_shop_menu(item_button_pos, item, price)
        else:
            print("Unknown action in buy menu... : " + str(method_id))

    def execute_sell_action(self, method_id, args):
        if method_id is SellMenu.INTERAC_SELL:
            item_button_pos = args[0]
            item = args[1]
            price = args[2]

            self.selected_item = item

            self.background_menus.append((self.active_menu, True))
            self.active_menu = MenuCreatorManager.create_item_sell_menu(item_button_pos, item, price)
        else:
            print("Unknown action in sell menu... : " + str(method_id))

    def execute_shop_action(self, method_id, args):
        if method_id is ShopMenu.BUY:
            shop = args[2][0]

            self.background_menus.append((self.active_menu, False))
            self.active_menu = MenuCreatorManager.create_shop_menu(shop.items, self.selected_player.gold)
        elif method_id is ShopMenu.SELL:
            items_max = self.selected_player.nb_items_max

            items = list(self.selected_player.items)
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            self.background_menus.append((self.active_menu, False))
            self.active_menu = MenuCreatorManager.create_inventory_menu(items, self.selected_player.gold, price=True)
        else:
            print("Unknown action in shop menu... : " + str(method_id))

    def execute_main_menu_action(self, method_id, args):
        if method_id is MainMenu.START:
            self.start_game()
        elif method_id is MainMenu.SAVE:
            self.save_game()
            self.background_menus.append((self.active_menu, True))
            self.active_menu = InfoBox("", "", "imgs/interface/PopUpMenu.png",
                                       [[{'type': 'text', 'text': "Game has been saved",
                                          'font': fonts['ITEM_DESC_FONT']}]],
                                       ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION)
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
            reach = self.selected_player.get_reach()
            self.possible_attacks = self.get_possible_attacks([self.selected_player.pos], reach, True)
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

            self.active_menu = MenuCreatorManager.create_inventory_menu(items, self.selected_player.gold)
        # Equipment action : open the equipment screen
        elif method_id is CharacterMenu.EQUIPMENT:
            self.background_menus.append((self.active_menu, True))

            equipments = list(self.selected_player.equipments)
            self.active_menu = MenuCreatorManager.create_equipment_menu(equipments)
        # Display player's status
        elif method_id is CharacterMenu.STATUS:
            self.background_menus.append((self.active_menu, True))
            self.active_menu = MenuCreatorManager.create_status_menu(self.selected_player)
        # Wait action : Given Character's turn is finished
        elif method_id is CharacterMenu.WAIT:
            self.active_menu = None
            self.selected_item = None
            self.selected_player.turn_finished()
            self.selected_player = None
            self.possible_moves = []
            self.possible_attacks = []
            self.possible_interactions = []
            self.background_menus = []
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
        # Talk with an ally
        elif method_id is CharacterMenu.TALK:
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = []
            for ent in self.get_next_cases(self.selected_player.pos):
                if isinstance(ent, Character) and not isinstance(ent, Player):
                    self.possible_interactions.append(ent.pos)
        elif method_id is CharacterMenu.TRADE:
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = []
            for ent in self.get_next_cases(self.selected_player.pos):
                if isinstance(ent, Player):
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
                                self.passed_players.append(self.selected_player)
                                if mission.main and mission.ended:
                                    self.victory = True
                                # Turn is finished
                                self.active_menu = None
                                self.background_menus = []
                                self.selected_player.turn_finished()
                                self.selected_player = None

    def execute_inv_action(self, method_id, args):
        # Watch item action : Open a menu to act with a given item
        if method_id is InventoryMenu.INTERAC_ITEM:
            item_button_pos = args[0]
            item = args[1]

            self.selected_item = item
            self.background_menus.append((self.active_menu, True))
            self.active_menu = MenuCreatorManager.create_item_menu(item_button_pos, item)

    def execute_equipment_action(self, method_id, args):
        # Watch item action : Open a menu to act with a given item
        if method_id is EquipmentMenu.INTERAC_EQUIPMENT:
            item_button_pos = args[0]
            item = args[1]

            self.selected_item = item
            self.background_menus.append([self.active_menu, True])
            self.active_menu = MenuCreatorManager.create_item_menu(item_button_pos, item, True)

    def execute_item_action(self, method_id, args):
        # Get info about an item
        if method_id is ItemMenu.INFO_ITEM:
            self.background_menus.append([self.active_menu, False])
            self.active_menu = MenuCreatorManager.create_item_desc_menu(self.selected_item)
        # Remove an item
        elif method_id is ItemMenu.THROW_ITEM:
            formatted_item_name = self.selected_item.get_formatted_name()

            # Remove item from inventory/equipment according to the index
            if self.selected_player.has_equipment(self.selected_item):
                self.selected_player.remove_equipment(self.selected_item)
                equipments = list(self.selected_player.equipments)
                new_items_menu = MenuCreatorManager.create_equipment_menu(equipments)
            else:
                self.selected_player.remove_item(self.selected_item)
                items_max = self.selected_player.nb_items_max
                items = list(self.selected_player.items)
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                new_items_menu = MenuCreatorManager.create_inventory_menu(items, self.selected_player.gold)

            # Update the inventory menu (i.e. first menu backward)
            self.background_menus[len(self.background_menus) - 1] = (new_items_menu, True)

            remove_msg_entries = [[{'type': 'text', 'text': 'Item has been thrown away.',
                                    'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]
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

                new_inventory_menu = MenuCreatorManager.create_inventory_menu(items, self.selected_player.gold)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1] = (new_inventory_menu, True)

            entries = [[{'type': 'text', 'text': result_msg,
                         'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Equip an item
        elif method_id is ItemMenu.EQUIP_ITEM:
            self.background_menus.append([self.active_menu, False])

            formatted_item_name = self.selected_item.get_formatted_name()

            # Try to equip the item
            return_equipped = self.selected_player.equip(self.selected_item)
            if return_equipped == -1:
                # Item can't be equipped by this player
                result_msg = "This item can't be equipped : " \
                             + self.selected_player.get_formatted_name() + " doesn't satisfy the requirements."
            else:
                # In this case returned value is > 0, item has been equipped
                result_msg = "The item has been equipped."
                if return_equipped == 1:
                    result_msg += " Previous equipped item has been added to your inventory."

                # Inventory has changed
                items_max = self.selected_player.nb_items_max
                items = list(self.selected_player.items)
                free_spaces = items_max - len(items)
                items += [None] * free_spaces

                new_inventory_menu = MenuCreatorManager.create_inventory_menu(items, self.selected_player.gold)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1] = (new_inventory_menu, True)

            entries = [[{'type': 'text', 'text': result_msg,
                         'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]
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
                new_equipment_menu = MenuCreatorManager.create_equipment_menu(self.selected_player.equipments)

                # Cancel item menu
                self.background_menus.pop()
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1] = (new_equipment_menu, True)

            entries = [[{'type': 'text', 'text': result_msg, 'font': fonts['ITEM_DESC_FONT'],
                         'margin': (20, 0, 20, 0)}]]
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

            entries = [[{'type': 'text', 'text': result_msg,
                         'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        # Sell an item
        elif method_id is ItemMenu.SELL_ITEM:
            price = args[2][0][0]
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

                new_sell_menu = MenuCreatorManager.create_inventory_menu(items, self.selected_player.gold, price=True)

                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1] = (new_sell_menu, True)
            else:
                result_msg = "This item can't be selled !"
                self.background_menus.append([self.active_menu, False])

            entries = [[{'type': 'text', 'text': result_msg,
                         'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]
            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", entries,
                                       ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)
        elif method_id is ItemMenu.TRADE_ITEM:
            first_player = args[2][0]
            second_player = args[2][1]
            owner = first_player if args[2][2] == 0 else second_player
            receiver = second_player if args[2][2] == 0 else first_player

            formatted_item_name = self.selected_item.get_formatted_name()

            # Add item if possible
            added = receiver.set_item(self.selected_item)
            if not added:
                msg_entries = [[{'type': 'text', 'text': 'Item can\'t be traded : not enough place in'
                                                         + receiver.get_formatted_name() + '\'s inventory .',
                                 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]

                self.background_menus.append((self.active_menu, False))
            else:
                # Remove item from owner inventory according to index
                owner.remove_item(self.selected_item)

                new_trade_menu = MenuCreatorManager.create_trade_menu(first_player, second_player)
                # Update the inventory menu (i.e. first menu backward)
                self.background_menus[len(self.background_menus) - 1] = (new_trade_menu, True)

                msg_entries = [[{'type': 'text', 'text': 'Item has been traded.',
                                 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]

            self.active_menu = InfoBox(formatted_item_name, "", "imgs/interface/PopUpMenu.png", msg_entries,
                                       ITEM_DELETE_MENU_WIDTH, close_button=UNFINAL_ACTION)
        else:
            print("Unknown action in item menu... : " + str(method_id))

    def execute_status_action(self, method_id, args):
        # Get infos about an alteration
        if method_id is StatusMenu.INFO_ALTERATION_ACTION:
            alteration = args[1]

            self.background_menus.append([self.active_menu, True])
            self.active_menu = MenuCreatorManager.create_alteration_info_menu(alteration)

    def execute_trade_action(self, method_id, args):
        # Watch item action : Open a menu to act with a given item
        if method_id is TradeMenu.INTERAC_ITEM:
            item_button_pos = args[0]
            item = args[1]
            players = args[2]

            self.selected_item = item
            self.background_menus.append([self.active_menu, True])
            self.active_menu = MenuCreatorManager.create_trade_item_menu(item_button_pos, item, players)

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
                    interactable_entities = self.entities['chests'] + self.entities['portals'] + \
                                            self.entities['fountains'] + self.entities['allies'] + self.players
                    self.active_menu = MenuCreatorManager.create_player_menu(self.selected_player,
                                                                             self.entities['buildings'],
                                                                             interactable_entities, self.missions,
                                                                             self.entities['foes'])
            else:
                if len(args) >= 3 and args[2][0] == FINAL_ACTION:
                    # Turn is finished
                    self.background_menus = []
                    self.selected_player.turn_finished()
                    self.selected_player = None
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
        elif menu_type is TradeMenu:
            self.execute_trade_action(method_id, args)
        else:
            print("Unknown menu... : " + str(menu_type))

    def begin_turn(self):
        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            self.new_turn()
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.entities['allies']
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities['foes']

        for ent in entities:
            ent.new_turn()

    def new_turn(self):
        self.turn += 1
        self.animation = Animation([{'sprite': NEW_TURN, 'pos': NEW_TURN_POS}], 60)

    def left_click(self, pos):
        if self.active_menu:
            self.execute_action(self.active_menu.type, self.active_menu.click(pos))
            return

        # Player can only react to active menu if it is not his turn
        if self.side_turn is not EntityTurn.PLAYER:
            return

        if self.selected_player is not None:
            if self.game_phase is not Status.INITIALIZATION:
                if self.possible_moves:
                    # Player is waiting to move
                    for move in self.possible_moves:
                        if pg.Rect(move, (TILE_SIZE, TILE_SIZE)).collidepoint(pos):
                            path = self.determine_path_to(move, self.possible_moves)
                            self.selected_player.set_move(path)
                            self.possible_moves = {}
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
                            self.background_menus = []
                            self.selected_player.turn_finished()
                            self.selected_player = None
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
                    player.selected = True
                    self.selected_player = player
                    self.possible_moves = self.get_possible_moves(player.pos, player.max_moves)
                    reach = self.selected_player.get_reach()
                    self.possible_attacks = self.get_possible_attacks(self.possible_moves, reach, True)
                    return
            for foe in self.entities['foes']:
                if foe.is_on_pos(pos):
                    self.active_menu = MenuCreatorManager.create_foe_menu(foe)
                    return

            is_initialization = self.game_phase is Status.INITIALIZATION
            self.active_menu = MenuCreatorManager.create_main_menu(is_initialization, pos)

    def right_click(self):
        if self.selected_player:
            if self.possible_moves:
                # Player was waiting to move
                self.selected_player.selected = False
                self.selected_player = None
                self.possible_moves = {}
            elif self.active_menu is not None:
                self.execute_action(self.active_menu.type, (GenericActions.CLOSE, ""))
                # Test if player was on character's main menu, in this case, current move should be cancelled
                if self.active_menu is None:
                    self.selected_player.cancel_move()
                    self.selected_player.selected = False
                    self.selected_player = None
                    self.possible_moves = {}
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
            self.possible_moves = {}
            self.possible_attacks = []

    def click(self, button, pos):
        # No event if there is an animation or it is not player turn
        if self.animation:
            return

        # 1 is equals to left button
        if button == 1:
            self.left_click(pos)
        # 3 is equals to right button
        elif button == 3:
            self.right_click()

    def button_down(self, button, pos):
        # 3 is equals to right button
        if button == 3:
            if not self.active_menu and not self.selected_player and self.side_turn is EntityTurn.PLAYER:
                for collection in self.entities.values():
                    for ent in collection:
                        if isinstance(ent, Movable) and ent.get_rect().collidepoint(pos):
                            pos = ent.pos
                            self.watched_ent = ent
                            self.possible_moves = self.get_possible_moves(pos, ent.max_moves)
                            reach = self.watched_ent.get_reach()
                            self.possible_attacks = self.get_possible_attacks(self.possible_moves,
                                                                              reach, isinstance(ent, Character))
                            return

    def motion(self, pos):
        if self.active_menu:
            self.active_menu.motion(pos)
        else:
            self.hovered_ent = None
            for collection in self.entities.values():
                for ent in collection:
                    if ent.get_rect().collidepoint(pos):
                        self.hovered_ent = ent
                        return
