import os
from enum import IntEnum, auto
from typing import Callable, Sequence

import pygame
from lxml import etree

from src.constants import (
    MAX_MAP_WIDTH,
    MAX_MAP_HEIGHT,
    MENU_WIDTH,
    MENU_HEIGHT,
    ITEM_MENU_WIDTH,
    ORANGE,
    ITEM_DELETE_MENU_WIDTH,
    ITEM_INFO_MENU_WIDTH,
    TILE_SIZE,
)
from src.game_entities.breakable import Breakable
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.destroyable import Destroyable
from src.game_entities.door import Door
from src.game_entities.foe import Foe
from src.game_entities.fountain import Fountain
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.key import Key
from src.game_entities.mission import MissionType
from src.game_entities.movable import Movable
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.shop import Shop
from src.gui.animation import Animation
from src.gui.constant_sprites import (
    ATTACKABLE_OPACITY,
    LANDING_OPACITY,
    INTERACTION_OPACITY,
    constant_sprites,
)
from src.gui.fonts import fonts
from src.gui.info_box import InfoBox
from src.gui.position import Position
from src.gui.sidebar import Sidebar
from src.gui.tools import blit_alpha
from src.services import load_from_xml_manager as Loader, menu_creator_manager
from src.services.menu_creator_manager import create_event_dialog
from src.services.menus import CharacterMenu, ShopMenu
from src.services.save_state_manager import SaveStateManager


class LevelStatus(IntEnum):
    INITIALIZATION = auto()
    IN_PROGRESS = auto()
    ENDED_VICTORY = auto()
    ENDED_DEFEAT = auto()


class EntityTurn(IntEnum):
    PLAYER = 0
    ALLIES = 1
    FOES = 2

    def get_next(self):
        """

        :return:
        """
        next_value = (
            self.value + 1 if self.value + 1 < len(EntityTurn.__members__) else 0
        )
        return EntityTurn(next_value)


class Level:
    """ """

    def __init__(
        self,
        directory,
        nb_level,
        status=LevelStatus.INITIALIZATION,
        turn=0,
        data=None,
        players=None,
    ):
        if players is None:
            players = []

        Shop.interaction_callback = self.interact_item_shop
        Shop.buy_interface_callback = lambda: self.open_menu(self.active_shop.menu)
        Shop.sell_interface_callback = self.open_sell_interface

        # Store directory path if player wants to save and exit game
        self.directory = directory
        self.nb_level = nb_level

        # Reading of the XML file
        tree = etree.parse(directory + "data.xml").getroot()
        map_image = pygame.image.load(self.directory + "map.png")
        self.map = {
            "img": map_image,
            "width": map_image.get_width(),
            "height": map_image.get_height(),
            "x": (MAX_MAP_WIDTH - map_image.get_width()) // 2,
            "y": (MAX_MAP_HEIGHT - map_image.get_height()) // 2,
        }

        # Load obstacles
        self.obstacles = Loader.load_obstacles(
            tree.find("obstacles"), self.map["x"], self.map["y"]
        )

        # Load events
        self.events = Loader.load_events(
            tree.find("events"), self.map["x"], self.map["y"]
        )

        # Load available tiles for characters' placement
        self.possible_placements = Loader.load_placements(
            tree.findall("placementArea/position"), self.map["x"], self.map["y"]
        )

        self.active_menu = None
        self.background_menus = []
        self.players = players
        self.entities = {"players": self.players}
        # List for players who are now longer in the level
        if data is None:
            # Game is new
            from_save = False
            data_tree = tree
            gap_x, gap_y = (self.map["x"], self.map["y"])
            self.passed_players = []
            if "before_init" in self.events:
                if "dialogs" in self.events["before_init"]:
                    for dialog in self.events["before_init"]["dialogs"]:
                        self.background_menus.append(
                            (create_event_dialog(dialog), False)
                        )
                self.active_menu = (
                    self.background_menus.pop(0)[0] if self.background_menus else None
                )
                if "new_players" in self.events["before_init"]:
                    for player_el in self.events["before_init"]["new_players"]:
                        player = Loader.init_player(player_el["name"])
                        player.position = player_el["position"]
                        self.players.append(player)

            # Set initial pos of players arbitrarily
            for player in self.players:
                for tile in self.possible_placements:
                    if self.get_entity_on_case(tile) is None:
                        player.set_initial_pos(tile)
                        break
                else:
                    print("Error ! Not enough free tiles to set players...")
        else:
            # Game is loaded from a save (data)
            from_save = True
            data_tree = data
            gap_x, gap_y = (0, 0)
            self.players = Loader.load_players(data_tree)
            self.passed_players = Loader.load_escaped_players(data_tree)

        # Load missions
        self.missions, self.main_mission = Loader.load_missions(
            tree, self.players, self.map["x"], self.map["y"]
        )

        # Load and store all entities
        self.entities = Loader.load_all_entities(data_tree, from_save, gap_x, gap_y)
        self.entities["players"] = self.players

        # Booleans for end game
        self.victory = False
        self.defeat = False

        # Data structures for possible actions
        self.possible_moves = {}
        self.possible_attacks = []
        self.possible_interactions = []

        # Storage of current selected entity
        self.selected_player = None
        self.selected_item = None
        self.active_shop = None

        self.quit_request = False
        self.game_phase = status
        self.side_turn = EntityTurn.PLAYER
        self.turn = turn
        self.animation = None
        self.watched_ent = None
        self.hovered_ent = None
        self.sidebar = Sidebar(
            (MENU_WIDTH, MENU_HEIGHT), (0, MAX_MAP_HEIGHT), self.missions, self.nb_level
        )
        self.wait_for_dest_tp = False
        self.diary_entries = []
        self.turn_items = []

        self.wait_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "waiting.ogg"))
        self.inventory_sfx = pygame.mixer.Sound(
            os.path.join("sound_fx", "inventory.ogg")
        )
        self.armor_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "armor.ogg"))
        self.talk_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "talking.ogg"))
        self.gold_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "trade.ogg"))

    def close_active_menu(self, is_action_final: bool = False) -> None:
        """
        Replace the active menu by the first menu in background if there is any.
        """
        if is_action_final:
            # Turn is finished
            self.active_menu = None
            self.background_menus = []
            self.selected_player.end_turn()
            self.selected_player = None
        else:
            self.active_menu = (
                self.background_menus.pop()[0] if self.background_menus else None
            )
            # Test if active menu is main character's menu, in this case, it should be reloaded
            if self.active_menu and self.active_menu.type is CharacterMenu:
                self.open_player_menu()

    def open_save_menu(self) -> None:
        """
        Replace the current active menu by the a freshly created save game interface
        """
        self.background_menus.append((self.active_menu, True))
        self.active_menu = menu_creator_manager.create_save_menu(self.save_game)

    def save_game(self, slot_id: int) -> None:
        """

        :param slot_id:
        """
        save_state_manager = SaveStateManager(self)
        save_state_manager.save_game(slot_id)
        self.background_menus.append((self.active_menu, True))
        self.active_menu = InfoBox(
            "",
            "imgs/interface/PopUpMenu.png",
            [
                [
                    {
                        "type": "text",
                        "text": "Game has been saved",
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            ],
            width=ITEM_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def exit_game(self):
        """
        Handle the end of the level
        """
        # At next update, level will be destroyed
        self.quit_request = True
        # If current level is not finish, end it as a defeat
        if (
            self.game_phase != LevelStatus.ENDED_VICTORY
            and self.game_phase != LevelStatus.ENDED_DEFEAT
        ):
            self.game_phase = LevelStatus.ENDED_DEFEAT

    def is_game_started(self):
        """

        :return:
        """
        return self.game_phase is not LevelStatus.INITIALIZATION

    def end_level(self, animation_surface, position):
        """

        :param animation_surface:
        :param position:
        """
        self.background_menus = []
        # Check if some optional objectives have been completed
        if self.main_mission.ended:
            for mission in self.missions:
                if not mission.main and mission.ended:
                    self.background_menus.append(
                        (menu_creator_manager.create_reward_menu(mission), False)
                    )
                    if mission.gold:
                        for player in self.players:
                            player.gold += mission.gold
                    if mission.items:
                        # TODO : Add items reward of optional objective to players
                        pass
            # Check if there are some post-level events
            if "at_end" in self.events:
                if "dialogs" in self.events["at_end"]:
                    for dialog in self.events["at_end"]["dialogs"]:
                        self.background_menus.append(
                            (create_event_dialog(dialog), False)
                        )

        self.active_menu = (
            self.background_menus.pop(0)[0] if self.background_menus else None
        )
        self.animation = Animation(
            [{"sprite": animation_surface, "pos": position}], 180
        )

    def update_state(self):
        """

        :return:
        """
        if self.quit_request:
            return self.game_phase

        if self.animation:
            if self.animation.animate():
                self.animation = None
                if self.game_phase > LevelStatus.IN_PROGRESS and not self.active_menu:
                    # End game animation is finished, level can be quit if there is no more menu
                    self.exit_game()
            return None

        # Game can't evolve if there is an active menu
        if self.active_menu:
            return None

        # Game should be left if it's ended and there is no more animation nor menu
        if (
            self.game_phase is LevelStatus.ENDED_DEFEAT
            or self.game_phase is LevelStatus.ENDED_VICTORY
        ):
            print("Passed in 'ENDED_DEFEAT / ENDED_VICTORY' condition")
            return self.game_phase

        for mission in self.missions:
            mission.update_state(entities=self.entities, turns=self.turn)
        if self.main_mission.ended:
            self.victory = True

        if not self.players:
            if not self.main_mission.succeeded_chars:
                self.defeat = True
            else:
                self.victory = True

        # Verify if game should be ended
        if self.victory:
            self.end_level(constant_sprites["victory"], constant_sprites["victory_pos"])
            self.game_phase = LevelStatus.ENDED_VICTORY
            self.victory = False
            return None
        if self.defeat:
            self.end_level(constant_sprites["defeat"], constant_sprites["defeat_pos"])
            self.game_phase = LevelStatus.ENDED_DEFEAT
            self.defeat = False
            return None

        if self.selected_player:
            if self.selected_player.move():
                # If movement is finished
                self.open_player_menu()
            return None

        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.entities["allies"]
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities["foes"]

        for ent in entities:
            if not ent.turn_is_finished():
                if self.side_turn is not EntityTurn.PLAYER:
                    self.entity_action(ent, (self.side_turn is EntityTurn.ALLIES))
                break
        else:
            self.side_turn = self.side_turn.get_next()
            self.begin_turn()

        return None

    def open_player_menu(self):
        interactable_entities = (
            self.entities["chests"]
            + self.entities["portals"]
            + self.entities["doors"]
            + self.entities["fountains"]
            + self.entities["allies"]
            + self.players
        )
        self.active_menu = menu_creator_manager.create_player_menu(
            {
                "inventory": self.open_inventory,
                "equipment": self.open_equipment,
                "status": self.open_status_interface,
                "wait": self.end_character_turn,
                "visit": self.select_visit,
                "trade": lambda: self.select_interaction_with(Player),
                "open_chest": self.try_open_chest,
                "pick_lock": self.pick_lock,
                "open_door": self.try_open_door,
                "use_portal": lambda: self.select_interaction_with(Portal),
                "drink": lambda: self.select_interaction_with(Fountain),
                "talk": self.talk,
                "take": self.take_objective,
                "attack": self.select_attack_target,
            },
            self.selected_player,
            self.entities["buildings"],
            interactable_entities,
            self.missions,
            self.entities["foes"],
        )

    def display(self, screen):
        """

        :param screen:
        """
        screen.blit(self.map["img"], (self.map["x"], self.map["y"]))
        self.sidebar.display(screen, self.turn, self.hovered_ent)

        for collection in self.entities.values():
            for ent in collection:
                ent.display(screen)
                if isinstance(ent, Destroyable):
                    ent.display_hit_points(screen)

        if self.watched_ent:
            self.show_possible_actions(self.watched_ent, screen)

        # If the game hasn't yet started
        if self.game_phase is LevelStatus.INITIALIZATION:
            self.show_possible_placements(screen)
        else:
            if self.selected_player:
                # If player is waiting to move
                if self.possible_moves:
                    self.show_possible_actions(self.selected_player, screen)
                elif self.possible_attacks:
                    self.show_possible_attacks(self.selected_player, screen)
                elif self.possible_interactions:
                    self.show_possible_interactions(screen)

        if self.animation:
            self.animation.display(screen)
        else:
            for menu in self.background_menus:
                if menu[1]:
                    menu[0].display(screen)
            if self.active_menu:
                self.active_menu.display(screen)

    def show_possible_actions(self, movable, screen):
        """

        :param movable:
        :param screen:
        """
        self.show_possible_moves(movable, screen)
        self.show_possible_attacks(movable, screen)

    def show_possible_attacks(self, movable, screen):
        """

        :param movable:
        :param screen:
        """
        for tile in self.possible_attacks:
            if movable.position != tile:
                blit_alpha(
                    screen, constant_sprites["attackable"], tile, ATTACKABLE_OPACITY
                )

    def show_possible_moves(self, movable, win):
        """

        :param movable:
        :param win:
        """
        for tile in self.possible_moves.keys():
            if movable.position != tile:
                blit_alpha(win, constant_sprites["landing"], tile, LANDING_OPACITY)

    def show_possible_interactions(self, win):
        """

        :param win:
        """
        for tile in self.possible_interactions:
            blit_alpha(win, constant_sprites["interaction"], tile, INTERACTION_OPACITY)

    def show_possible_placements(self, win):
        """

        :param win:
        """
        for tile in self.possible_placements:
            blit_alpha(win, constant_sprites["landing"], tile, LANDING_OPACITY)

    def start_game(self):
        """ """
        self.active_menu = None
        self.game_phase = LevelStatus.IN_PROGRESS
        self.new_turn()
        if "after_init" in self.events:
            if "dialogs" in self.events["after_init"]:
                for dialog in self.events["after_init"]["dialogs"]:
                    self.background_menus.append((create_event_dialog(dialog), False))
            self.active_menu = (
                self.background_menus.pop(0)[0] if self.background_menus else None
            )
            if "new_players" in self.events["after_init"]:
                for player_el in self.events["after_init"]["new_players"]:
                    player = Loader.init_player(player_el["name"])
                    player.position = player_el["position"]
                    self.players.append(player)

    def get_next_cases(self, pos):
        """

        :param pos:
        :return:
        """
        tiles = []
        for x_coordinate in range(-1, 2):
            for y_coordinate in {1 - abs(x_coordinate), -1 + abs(x_coordinate)}:
                case_x = pos[0] + (x_coordinate * TILE_SIZE)
                case_y = pos[1] + (y_coordinate * TILE_SIZE)
                case_pos = (case_x, case_y)
                case = self.get_entity_on_case(case_pos)
                tiles.append(case)
        return tiles

    def get_possible_moves(self, pos, max_moves):
        """

        :param pos:
        :param max_moves:
        :return:
        """
        tiles = {pos: 0}
        tiles_prev_level = tiles
        for i in range(1, max_moves + 1):
            tiles_next_level = {}
            for tile in tiles_prev_level:
                for x_coordinate in range(-1, 2):
                    for y_coordinate in {1 - abs(x_coordinate), -1 + abs(x_coordinate)}:
                        case_x = tile[0] + (x_coordinate * TILE_SIZE)
                        case_y = tile[1] + (y_coordinate * TILE_SIZE)
                        case_pos = (case_x, case_y)
                        if self.case_is_available(case_pos) and case_pos not in tiles:
                            tiles_next_level[case_pos] = i
            tiles.update(tiles_prev_level)
            tiles_prev_level = tiles_next_level
        tiles.update(tiles_prev_level)
        return tiles

    def get_possible_attacks(self, possible_moves, reach, from_ally_side):
        """

        :param possible_moves:
        :param reach:
        :param from_ally_side:
        :return:
        """
        tiles = []

        entities = list(self.entities["breakables"])
        if from_ally_side:
            entities += self.entities["foes"]
        else:
            entities += self.entities["allies"] + self.players

        for ent in entities:
            for i in reach:
                for x_coordinate in range(-i, i + 1):
                    for y_coordinate in {i - abs(x_coordinate), -i + abs(x_coordinate)}:
                        case_x = ent.position[0] + (x_coordinate * TILE_SIZE)
                        case_y = ent.position[1] + (y_coordinate * TILE_SIZE)
                        case_pos = (case_x, case_y)
                        if case_pos in possible_moves:
                            tiles.append(ent.position)

        return set(tiles)

    def case_is_available(self, case):
        """

        :param case:
        :return:
        """
        min_case = (self.map["x"], self.map["y"])
        max_case = (
            self.map["x"] + self.map["width"],
            self.map["y"] + self.map["height"],
        )
        if not (
            all(
                minimum <= case < maximum
                for minimum, case, maximum in zip(min_case, case, max_case)
            )
        ):
            return False

        return self.get_entity_on_case(case) is None and case not in self.obstacles

    def get_entity_on_case(self, case):
        """

        :param case:
        :return:
        """
        # Check all entities
        for collection in self.entities.values():
            for ent in collection:
                if ent.position == case:
                    return ent
        return None

    def determine_path_to(self, case_to, distance):
        """

        :param case_to:
        :param distance:
        :return:
        """
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

    def open_chest(self, actor, chest):
        """

        :param actor:
        :param chest:
        """
        # Get object inside the chest
        item = chest.open()

        if isinstance(item, Gold):
            # If it was some gold, it should be added to the total amount of the player
            actor.gold += item.amount
        else:
            # Else the item should be added to the inventory
            actor.set_item(item)

        # TODO: move the creation of the pop-up in menu_creator_manager
        entry_item = {
            "type": "item_button",
            "item": item,
            "index": -1,
            "disabled": True,
            "callback": lambda button_position, item_reference=item: self.interact_item(
                item_reference, button_position, is_equipped=False
            ),
        }
        entries = [
            [entry_item],
            [
                {
                    "type": "text",
                    "text": "Item has been added to your inventory",
                    "font": fonts["ITEM_DESC_FONT"],
                }
            ],
        ]
        self.active_menu = InfoBox(
            "You found in the chest",
            "imgs/interface/PopUpMenu.png",
            entries,
            width=ITEM_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(True),
        )

    def open_door(self, door):
        """

        :param door:
        """
        self.entities["doors"].remove(door)

        # TODO: move the creation of the pop-up in menu_creator_manager
        entries = [
            [
                {
                    "type": "text",
                    "text": "Door has been opened.",
                    "font": fonts["ITEM_DESC_FONT"],
                }
            ]
        ]
        self.active_menu = InfoBox(
            str(door),
            "imgs/interface/PopUpMenu.png",
            entries,
            width=ITEM_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(True),
        )

    def ally_to_player(self, character):
        """

        :param character:
        """
        self.entities["allies"].remove(character)
        player = Player(
            name=character.name,
            sprite=character.sprite,
            hit_points=character.hit_points,
            defense=character.defense,
            resistance=character.resistance,
            strength=character.strength,
            classes=character.classes,
            equipments=character.equipments,
            race=character.race,
            gold=character.gold,
            lvl=character.lvl,
            skills=character.skills,
            alterations=character.alterations,
        )
        self.entities["players"].append(player)
        player.earn_xp(character.experience)
        player.hit_points = character.hit_points
        player.position = character.position
        player.items = character.items

    def interact(self, actor, target, target_pos):
        """

        :param actor:
        :param target:
        :param target_pos:
        """
        # Since player chose his interaction, possible interactions should be reset
        self.possible_interactions = []

        # Check if target is an empty pos
        if not target:
            if self.wait_for_dest_tp:
                self.wait_for_dest_tp = False
                actor.position = target_pos

                # Turn is finished
                self.background_menus = []
                self.selected_player.end_turn()
                self.selected_player = None
        # Check if player tries to open a chest
        elif isinstance(target, Chest):
            if actor.has_free_space():
                if self.selected_player.current_action is CharacterMenu.OPEN_CHEST:
                    # Key is used to open the chest
                    actor.remove_chest_key()

                    # Get content
                    self.open_chest(actor, target)
                elif self.selected_player.current_action is CharacterMenu.PICK_LOCK:
                    if not target.pick_lock_initiated:
                        # Lock picking has not been already initiated
                        target.pick_lock_initiated = True
                        # TODO: move the creation of the pop-up in menu_creator_manager
                        entries = [
                            [
                                {
                                    "type": "text",
                                    "text": "Started picking, one more turn to go.",
                                    "font": fonts["ITEM_DESC_FONT"],
                                }
                            ]
                        ]
                        self.active_menu = InfoBox(
                            "Chest",
                            "imgs/interface/PopUpMenu.png",
                            entries,
                            width=ITEM_MENU_WIDTH,
                            close_button=lambda: self.close_active_menu(True),
                        )
                    else:
                        # Lock picking is finished, get content
                        self.open_chest(actor, target)

            else:
                # TODO: move the creation of the pop-up in menu_creator_manager
                self.active_menu = InfoBox(
                    "You have no free space in your inventory",
                    "imgs/interface/PopUpMenu.png",
                    [],
                    width=ITEM_MENU_WIDTH,
                    close_button=lambda: self.close_active_menu(False),
                )
        # Check if player tries to open a door
        elif isinstance(target, Door):
            if self.selected_player.current_action is CharacterMenu.OPEN_DOOR:
                # Key is used to open the door
                actor.remove_door_key()

                # Remove door
                self.open_door(target)

                # No more menu : turn is finished
                self.background_menus = []
            elif self.selected_player.current_action is CharacterMenu.PICK_LOCK:
                if not target.pick_lock_initiated:
                    # Lock picking has not been already initiated
                    target.pick_lock_initiated = True
                    # TODO: move the creation of the pop-up in menu_creator_manager
                    entries = [
                        [
                            {
                                "type": "text",
                                "text": "Started picking, one more turn to go.",
                                "font": fonts["ITEM_DESC_FONT"],
                            }
                        ]
                    ]
                    self.active_menu = InfoBox(
                        str(target),
                        "imgs/interface/PopUpMenu.png",
                        entries,
                        width=ITEM_MENU_WIDTH,
                        close_button=lambda: self.close_active_menu(True),
                    )
                else:
                    # Lock picking is finished, get content
                    self.open_door(target)
        # Check if player tries to use a portal
        elif isinstance(target, Portal):
            new_based_pos = target.linked_to.position
            possible_pos = self.get_possible_moves(new_based_pos, 1)
            # Remove portal pos since player cannot be on the portal
            del possible_pos[new_based_pos]
            if possible_pos:
                self.possible_interactions = possible_pos.keys()
                self.wait_for_dest_tp = True
            else:
                self.active_menu = InfoBox(
                    "There is no free square around the other portal",
                    "imgs/interface/PopUpMenu.png",
                    [],
                    width=ITEM_MENU_WIDTH,
                    close_button=lambda: self.close_active_menu(False),
                )
        # Check if player tries to drink in a fountain
        elif isinstance(target, Fountain):
            entries = target.drink(actor)
            self.active_menu = InfoBox(
                str(target),
                "imgs/interface/PopUpMenu.png",
                entries,
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(True),
            )

            # No more menu : turn is finished
            self.background_menus = []
        # Check if player tries to trade with another player
        elif isinstance(target, Player):
            self.active_menu = menu_creator_manager.create_trade_menu(
                {
                    "interact_item": self.interact_trade_item,
                    "send_gold": self.send_gold,
                },
                self.selected_player,
                target,
            )
        # Check if player tries to talk to a character
        elif isinstance(target, Character):
            pygame.mixer.Sound.play(self.talk_sfx)

            entries = target.talk(actor)
            self.active_menu = InfoBox(
                str(target),
                "imgs/interface/PopUpMenu.png",
                entries,
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(True),
                title_color=ORANGE,
            )
            # No more menu : turn is finished
            self.background_menus = []
            # Check if character is now a player
            if target.join_team:
                self.ally_to_player(target)
        # Check if player tries to visit a building
        elif isinstance(target, Building):
            kind = ""
            # Check if player tries to visit a shop
            if isinstance(target, Shop):
                self.active_shop = target
                kind = ShopMenu

            entries = target.interact(actor)
            self.active_menu = InfoBox(
                str(target),
                "imgs/interface/PopUpMenu.png",
                entries,
                id_type=kind,
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(True),
                title_color=ORANGE,
            )

            # No more menu : turn is finished
            self.background_menus = []

    def remove_entity(self, entity):
        """

        :param entity:
        """
        collection = None
        if isinstance(entity, Foe):
            collection = self.entities["foes"]
        elif isinstance(entity, Player):
            collection = self.entities["players"]
        elif isinstance(entity, Breakable):
            collection = self.entities["breakables"]
        elif isinstance(entity, Character):
            collection = self.entities["allies"]
        collection.remove(entity)

    def duel(self, attacker, target, attacker_allies, target_allies, kind):
        """

        :param attacker:
        :param target:
        :param attacker_allies:
        :param target_allies:
        :param kind:
        """
        nb_attacks = 2 if "double_attack" in attacker.skills else 1
        for i in range(nb_attacks):
            experience = 0

            if isinstance(target, Character) and target.parried():
                # Target parried attack
                msg = (
                    str(attacker)
                    + " attacked "
                    + str(target)
                    + "... But "
                    + str(target)
                    + " parried !"
                )
                self.diary_entries.append(
                    [{"type": "text", "text": msg, "font": fonts["ITEM_DESC_FONT"]}]
                )
                # Current attack is ended
                continue

            damages = attacker.attack(target)
            real_damages = target.hit_points - target.attacked(
                attacker, damages, kind, target_allies
            )
            self.diary_entries.append(
                [
                    {
                        "type": "text",
                        "text": str(attacker)
                        + " dealt "
                        + str(real_damages)
                        + " damage to "
                        + str(target),
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            )
            # XP gain for dealt damages
            experience += real_damages // 2
            # If target has less than 0 HP at the end of the attack
            if target.hit_points <= 0:
                # XP gain increased
                if isinstance(attacker, Character):
                    experience += target.xp_gain

                self.diary_entries.append(
                    [
                        {
                            "type": "text",
                            "text": str(target) + " died !",
                            "font": fonts["ITEM_DESC_FONT"],
                        }
                    ]
                )
                # Loot
                if isinstance(attacker, Player):
                    # Check if foe dropped an item
                    loot = target.roll_for_loot()
                    for item in loot:
                        if isinstance(item, Item):
                            self.diary_entries.append(
                                [
                                    {
                                        "type": "text",
                                        "text": str(target) + " dropped " + str(item),
                                        "font": fonts["ITEM_DESC_FONT"],
                                    }
                                ]
                            )
                            if isinstance(item, Gold):
                                attacker.gold += item.amount
                            elif not attacker.set_item(item):
                                self.diary_entries.append(
                                    [
                                        {
                                            "type": "text",
                                            "text": "But there is not enough space "
                                            "in inventory to take it !",
                                            "font": fonts["ITEM_DESC_FONT"],
                                        }
                                    ]
                                )
                self.remove_entity(target)
            else:
                self.diary_entries.append(
                    [
                        {
                            "type": "text",
                            "text": f"{target} now has {target.hit_points}  HP",
                            "font": fonts["ITEM_DESC_FONT"],
                        }
                    ]
                )
                # Check if a side effect is applied to target
                if isinstance(attacker, Character):
                    weapon = attacker.get_weapon()
                    if weapon:
                        applied_effects = weapon.applied_effects(attacker, target)
                        for eff in applied_effects:
                            _, msg = eff.apply_on_ent(target)
                            self.diary_entries.append(
                                [
                                    {
                                        "type": "text",
                                        "text": msg,
                                        "font": fonts["ITEM_DESC_FONT"],
                                    }
                                ]
                            )

            # XP gain
            if isinstance(attacker, Player):
                self.diary_entries.append(
                    [
                        {
                            "type": "text",
                            "text": str(attacker)
                            + " earned "
                            + str(experience)
                            + " XP",
                            "font": fonts["ITEM_DESC_FONT"],
                        }
                    ]
                )
                if attacker.earn_xp(experience):
                    # Attacker gained a level
                    self.diary_entries.append(
                        [
                            {
                                "type": "text",
                                "text": str(attacker) + " gained a level !",
                                "font": fonts["ITEM_DESC_FONT"],
                            }
                        ]
                    )

            if target.hit_points <= 0:
                # Target is dead, no more attack needed.
                break
        while len(self.diary_entries) > 10:
            self.diary_entries.pop(0)

    def distance_between_all(self, entity, all_other_entities):
        """

        :param entity:
        :param all_other_entities:
        :return:
        """
        free_tiles_distance = self.get_possible_moves(
            entity.position,
            (self.map["width"] * self.map["height"]) // (TILE_SIZE * TILE_SIZE),
        )
        entities_distance = {
            ent: self.map["width"] * self.map["height"] for ent in all_other_entities
        }
        for tile, dist in free_tiles_distance.items():
            for neighbour in self.get_next_cases(tile):
                if (
                    neighbour in all_other_entities
                    and dist < entities_distance[neighbour]
                ):
                    entities_distance[neighbour] = dist
        return entities_distance

    def entity_action(self, entity, is_ally):
        """

        :param entity:
        :param is_ally:
        """
        possible_moves = self.get_possible_moves(entity.position, entity.max_moves)
        targets = (
            self.entities["foes"] if is_ally else self.players + self.entities["allies"]
        )
        allies = (
            self.players + self.entities["allies"] if is_ally else self.entities["foes"]
        )
        case = entity.act(possible_moves, self.distance_between_all(entity, targets))

        if case:
            if case in possible_moves:
                # Entity choose to move to case
                self.hovered_ent = entity
                path = self.determine_path_to(case, possible_moves)
                entity.set_move(path)
            else:
                # Entity choose to attack the entity on the case
                ent_attacked = self.get_entity_on_case(case)
                self.duel(entity, ent_attacked, allies, targets, entity.attack_kind)
                entity.end_turn()

    def interact_item_shop(self, item: Item, button_position: Position) -> None:
        """

        :param button_position:
        :param item:
        """
        self.selected_item = item
        self.background_menus.append((self.active_menu, True))
        self.active_menu = menu_creator_manager.create_item_shop_menu(
            {
                "buy_item": self.try_buy_selected_item,
                "info_item": self.open_selected_item_description,
            },
            button_position,
            item,
        )

    def interact_sell_item(self, item: Item, button_position: Position) -> None:
        """

        :param item:
        :param button_position:
        """
        self.selected_item = item
        self.background_menus.append((self.active_menu, True))
        self.active_menu = menu_creator_manager.create_item_sell_menu(
            {
                "sell_item": self.try_sell_selected_item,
                "info_item": self.open_selected_item_description,
            },
            button_position,
            item,
        )

    def open_sell_interface(self):
        """ """
        items_max = self.selected_player.nb_items_max
        items = list(self.selected_player.items)
        free_spaces = items_max - len(items)
        items += [None] * free_spaces
        self.open_menu(
            menu_creator_manager.create_inventory_menu(
                self.interact_sell_item,
                items,
                self.selected_player.gold,
                is_to_sell=True,
            )
        )

    def open_menu(
        self,
        menu: InfoBox,
        is_previous_visible: bool = False,
        sound: pygame.mixer.Sound = None,
    ) -> None:
        """

        :param sound:
        :param menu:
        :param is_previous_visible:
        """
        if sound is not None:
            pygame.mixer.Sound.play(sound)
        self.background_menus.append((self.active_menu, is_previous_visible))
        self.active_menu = menu

    def end_turn(self) -> None:
        """
        End the current turn
        """
        self.active_menu = None
        for player in self.players:
            player.end_turn()
        self.side_turn = self.side_turn.get_next()
        self.begin_turn()

    def select_visit(self):
        """ """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
        self.selected_player.choose_target()
        self.possible_interactions = [
            (
                self.selected_player.position[0],
                self.selected_player.position[1] - TILE_SIZE,
            )
        ]
        self.possible_attacks = []

    def take_objective(self):
        """ """
        for mission in self.missions:
            if (
                mission.type is MissionType.POSITION
                or mission.type is MissionType.TOUCH_POSITION
            ):
                # Verify that character is not the last if the mission is not the main one
                if mission.main or len(self.players) > 1:
                    if mission.is_position_valid(self.selected_player.position):
                        # Check if player is able to complete this objective
                        if mission.update_state(self.selected_player):
                            self.players.remove(self.selected_player)
                            self.passed_players.append(self.selected_player)
                            if mission.main and mission.ended:
                                self.victory = True
                            # Turn is finished
                            self.active_menu = None
                            self.background_menus = []
                            self.selected_player.end_turn()
                            self.selected_player = None
                            break

    def talk(self):
        """ """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
        self.selected_player.choose_target()
        self.possible_interactions = []
        for ent in self.get_next_cases(self.selected_player.position):
            if isinstance(ent, Character) and not isinstance(ent, Player):
                self.possible_interactions.append(ent.position)

    def pick_lock(self):
        """ """
        self.selected_player.current_action = CharacterMenu.PICK_LOCK
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
        self.selected_player.choose_target()
        self.possible_interactions = []
        for ent in self.get_next_cases(self.selected_player.position):
            if (isinstance(ent, Chest) and not ent.opened) or isinstance(ent, Door):
                self.possible_interactions.append(ent.position)

    def try_open_door(self):
        """ """
        # Check if player has a key
        has_key = False
        for item in self.selected_player.items:
            if isinstance(item, Key) and item.for_door:
                has_key = True
                break
        if not has_key:
            info_box = InfoBox(
                "You have no key to open a door",
                "imgs/interface/PopUpMenu.png",
                [],
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(False),
            )
            self.open_menu(info_box, is_previous_visible=True)
        else:
            self.selected_player.current_action = CharacterMenu.OPEN_DOOR
            self.select_interaction_with(Door)

    def try_open_chest(self):
        """ """
        # Check if player has a key
        has_key = False
        for item in self.selected_player.items:
            if isinstance(item, Key) and item.for_chest:
                has_key = True
                break
        if not has_key:
            info_box = InfoBox(
                "You have no key to open a chest",
                "imgs/interface/PopUpMenu.png",
                [],
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(False),
            )
            self.open_menu(info_box, is_previous_visible=True)
        else:
            self.selected_player.current_action = CharacterMenu.OPEN_CHEST
            self.background_menus.append((self.active_menu, False))
            self.active_menu = None
            self.selected_player.choose_target()
            self.possible_interactions = []
            for ent in self.get_next_cases(self.selected_player.position):
                if isinstance(ent, Chest) and not ent.opened:
                    self.possible_interactions.append(ent.position)

    def select_attack_target(self):
        """ """
        self.background_menus.append((self.active_menu, False))
        self.selected_player.choose_target()
        self.possible_attacks = self.get_possible_attacks(
            [self.selected_player.position], self.selected_player.reach, True
        )
        self.possible_interactions = []
        self.active_menu = None

    def open_status_interface(self):
        """ """
        self.open_menu(
            menu_creator_manager.create_status_menu(
                {
                    "info_alteration": self.open_alteration_description,
                    "info_skill": self.open_skill_description,
                },
                self.selected_player,
            ),
            is_previous_visible=True,
        )

    def end_character_turn(self):
        """ """
        pygame.mixer.Sound.play(self.wait_sfx)
        self.active_menu = None
        self.selected_item = None
        self.selected_player.end_turn()
        self.selected_player = None
        self.possible_moves = []
        self.possible_attacks = []
        self.possible_interactions = []
        self.background_menus = []

    def open_equipment(self) -> None:
        """ """
        equipments = list(self.selected_player.equipments)
        self.open_menu(
            menu_creator_manager.create_equipment_menu(self.interact_item, equipments),
            is_previous_visible=True,
            sound=self.armor_sfx,
        )

    def open_inventory(self) -> None:
        """
        Replace the current active menu by the interface corresponding to the inventory of the
        selected player
        """
        free_spaces = self.selected_player.nb_items_max - len(
            self.selected_player.items
        )
        items = list(self.selected_player.items) + [None] * free_spaces
        self.open_menu(
            menu_creator_manager.create_inventory_menu(
                self.interact_item, items, self.selected_player.gold
            ),
            is_previous_visible=True,
            sound=self.inventory_sfx,
        )

    def select_interaction_with(self, entity_kind):
        """

        :param entity_kind:
        """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
        self.selected_player.choose_target()
        self.possible_interactions = []
        for entity in self.get_next_cases(self.selected_player.position):
            if isinstance(entity, entity_kind):
                self.possible_interactions.append(entity.position)

    def interact_item(self, item, button_position, is_equipped):
        """

        :param is_equipped:
        :param item:
        :param button_position:
        """
        self.selected_item = item
        self.open_menu(
            menu_creator_manager.create_item_menu(
                {
                    "info_item": self.open_selected_item_description,
                    "throw_item": self.throw_selected_item,
                    "use_item": self.use_selected_item,
                    "unequip_item": self.unequip_selected_item,
                    "equip_item": self.equip_selected_item,
                },
                button_position,
                item,
                is_equipped=is_equipped,
            ),
            is_previous_visible=True,
        )

    def trade_item(
        self, first_player: Player, second_player: Player, is_first_player_owner: bool
    ):
        """

        :param first_player:
        :param second_player:
        :param is_first_player_owner:
        """
        pygame.mixer.Sound.play(self.inventory_sfx)
        owner = first_player if is_first_player_owner else second_player
        receiver = second_player if is_first_player_owner else first_player
        # Add item if possible
        added = receiver.set_item(self.selected_item)
        if not added:
            msg_entries = [
                [
                    {
                        "type": "text",
                        "text": "Item can't be traded : not enough place in"
                        + str(receiver)
                        + "'s inventory .",
                        "font": fonts["ITEM_DESC_FONT"],
                        "margin": (20, 0, 20, 0),
                    }
                ]
            ]

            self.background_menus.append((self.active_menu, False))
        else:
            # Remove item from owner inventory according to index
            owner.remove_item(self.selected_item)

            new_trade_menu = menu_creator_manager.create_trade_menu(
                {
                    "interact_item": self.interact_trade_item,
                    "send_gold": self.send_gold,
                },
                first_player,
                second_player,
            )
            # Update the inventory menu (i.e. first menu backward)
            self.background_menus[len(self.background_menus) - 1] = (
                new_trade_menu,
                True,
            )

            msg_entries = [
                [
                    {
                        "type": "text",
                        "text": "Item has been traded.",
                        "font": fonts["ITEM_DESC_FONT"],
                        "margin": (20, 0, 20, 0),
                    }
                ]
            ]
        self.turn_items.append([self.selected_item, owner, receiver])
        self.active_menu = InfoBox(
            str(self.selected_item),
            "imgs/interface/PopUpMenu.png",
            msg_entries,
            width=ITEM_DELETE_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def throw_selected_item(self):
        """ """
        # Remove item from inventory/equipment according to the index
        if self.selected_player.has_equipment(self.selected_item):
            self.selected_player.remove_equipment(self.selected_item)
            equipments = list(self.selected_player.equipments)
            new_items_menu = menu_creator_manager.create_equipment_menu(
                self.interact_item, equipments
            )
        else:
            self.selected_player.remove_item(self.selected_item)
            items_max = self.selected_player.nb_items_max
            items = list(self.selected_player.items)
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            new_items_menu = menu_creator_manager.create_inventory_menu(
                self.interact_item, items, self.selected_player.gold
            )
        # Update the inventory menu (i.e. first menu backward)
        self.background_menus[len(self.background_menus) - 1] = (new_items_menu, True)
        remove_msg_entries = [
            [
                {
                    "type": "text",
                    "text": "Item has been thrown away.",
                    "font": fonts["ITEM_DESC_FONT"],
                    "margin": (20, 0, 20, 0),
                }
            ]
        ]
        self.active_menu = InfoBox(
            str(self.selected_item),
            "imgs/interface/PopUpMenu.png",
            remove_msg_entries,
            width=ITEM_DELETE_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def try_sell_selected_item(self):
        """ """
        sold, result_msg = self.active_shop.sell(
            self.selected_player, self.selected_item
        )
        if sold:
            # Remove ref to item
            self.selected_item = None

            # Update shop screen content (item has been removed from inventory)
            items_max = self.selected_player.nb_items_max

            items = list(self.selected_player.items)
            free_spaces = items_max - len(items)
            items += [None] * free_spaces

            new_sell_menu = menu_creator_manager.create_inventory_menu(
                self.interact_sell_item,
                items,
                self.selected_player.gold,
                is_to_sell=True,
            )

            # Update the inventory menu (i.e. first menu backward)
            self.background_menus[len(self.background_menus) - 1] = (
                new_sell_menu,
                True,
            )
        else:
            self.background_menus.append((self.active_menu, False))
        entries = [
            [
                {
                    "type": "text",
                    "text": result_msg,
                    "font": fonts["ITEM_DESC_FONT"],
                    "margin": (20, 0, 20, 0),
                }
            ]
        ]
        self.active_menu = InfoBox(
            str(self.selected_item),
            "imgs/interface/PopUpMenu.png",
            entries,
            width=ITEM_INFO_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def try_buy_selected_item(self):
        """ """
        # Try to buy the item
        result_msg = self.active_shop.buy(self.selected_player, self.selected_item)
        entries = [
            [
                {
                    "type": "text",
                    "text": result_msg,
                    "font": fonts["ITEM_DESC_FONT"],
                    "margin": (20, 0, 20, 0),
                }
            ]
        ]
        self.active_menu = InfoBox(
            str(self.selected_item),
            "imgs/interface/PopUpMenu.png",
            entries,
            width=ITEM_INFO_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def unequip_selected_item(self):
        """ """
        self.background_menus.append((self.active_menu, False))
        # Try to unequip the item
        unequipped = self.selected_player.unequip(self.selected_item)
        result_msg = (
            "The item can't be unequipped : Not enough space in your inventory."
        )
        if unequipped:
            result_msg = "The item has been unequipped"

            # Update equipment screen content
            new_equipment_menu = menu_creator_manager.create_equipment_menu(
                self.interact_item, self.selected_player.equipments
            )

            # Cancel item menu
            self.background_menus.pop()
            # Update the inventory menu (i.e. first menu backward)
            self.background_menus[len(self.background_menus) - 1] = (
                new_equipment_menu,
                True,
            )
        entries = [
            [
                {
                    "type": "text",
                    "text": result_msg,
                    "font": fonts["ITEM_DESC_FONT"],
                    "margin": (20, 0, 20, 0),
                }
            ]
        ]
        self.active_menu = InfoBox(
            str(self.selected_item),
            "imgs/interface/PopUpMenu.png",
            entries,
            width=ITEM_INFO_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def equip_selected_item(self):
        """ """
        # Try to equip the item
        return_equipped = self.selected_player.equip(self.selected_item)
        if return_equipped == -1:
            # Item can't be equipped by this player
            result_msg = (
                "This item can't be equipped : "
                + str(self.selected_player)
                + " doesn't satisfy the requirements."
            )
        else:
            # In this case returned value is > 0, item has been equipped
            result_msg = "The item has been equipped."
            if return_equipped == 1:
                result_msg += (
                    " Previous equipped item has been added to your inventory."
                )

            # Inventory has changed
            self.refresh_inventory()
        entries = [
            [
                {
                    "type": "text",
                    "text": result_msg,
                    "font": fonts["ITEM_DESC_FONT"],
                    "margin": (20, 0, 20, 0),
                }
            ]
        ]
        self.open_menu(
            InfoBox(
                str(self.selected_item),
                "imgs/interface/PopUpMenu.png",
                entries,
                width=ITEM_INFO_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(False),
            )
        )

    def use_selected_item(self):
        """ """
        # Try to use the object
        used, result_msgs = self.selected_player.use_item(self.selected_item)
        # Inventory display is update if object has been used
        if used:
            self.refresh_inventory()
        entries = [
            [
                {
                    "type": "text",
                    "text": msg,
                    "font": fonts["ITEM_DESC_FONT"],
                    "margin": (10, 0, 10, 0),
                }
            ]
            for msg in result_msgs
        ]
        self.open_menu(
            InfoBox(
                str(self.selected_item),
                "imgs/interface/PopUpMenu.png",
                entries,
                width=ITEM_INFO_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(False),
            )
        )

    def open_selected_item_description(self):
        """ """
        self.open_menu(
            menu_creator_manager.create_item_description_menu(self.selected_item)
        )

    def refresh_inventory(self):
        """ """
        free_spaces = self.selected_player.nb_items_max - len(
            self.selected_player.items
        )
        items = list(self.selected_player.items) + [None] * free_spaces
        new_inventory_menu = menu_creator_manager.create_inventory_menu(
            self.interact_item, items, self.selected_player.gold
        )
        # Cancel item menu
        self.background_menus.pop()
        # Update the inventory menu (i.e. first menu backward)
        self.background_menus[len(self.background_menus) - 1] = (
            new_inventory_menu,
            True,
        )

    def open_skill_description(self, skill):
        self.open_menu(
            menu_creator_manager.create_skill_info_menu(skill), is_previous_visible=True
        )

    def open_alteration_description(self, alteration):
        self.open_menu(
            menu_creator_manager.create_alteration_info_menu(alteration),
            is_previous_visible=True,
        )

    def send_gold(
        self,
        first_player: Player,
        second_player: Player,
        is_first_player_sender: bool,
        value: int,
    ) -> None:
        pygame.mixer.Sound.play(self.gold_sfx)
        sender = first_player if is_first_player_sender else second_player
        receiver = second_player if is_first_player_sender else first_player
        Player.trade_gold(sender, receiver, value)
        self.active_menu = menu_creator_manager.create_trade_menu(
            {"interact_item": self.interact_trade_item, "send_gold": self.send_gold},
            first_player,
            second_player,
        )

    def interact_trade_item(
        self,
        item: Item,
        button_position: Position,
        players: Sequence[Player],
        is_first_player_owner: bool,
    ) -> None:
        self.selected_item = item
        self.open_menu(
            menu_creator_manager.create_trade_item_menu(
                {
                    "info_item": self.open_selected_item_description,
                    "trade_item": self.trade_item,
                },
                button_position,
                item,
                players,
                is_first_player_owner,
            ),
            is_previous_visible=True,
        )

    @staticmethod
    def execute_action(action: Callable) -> None:
        """
        Manage actions related to a click on a button.
        Simply execute the given callable.

        Keyword arguments:
        action -- the callable associated to the clicked button
        """
        action()

    def begin_turn(self) -> None:
        """
        Begin next camp's turn
        """
        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            self.new_turn()
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.entities["allies"]
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities["foes"]

        for ent in entities:
            ent.new_turn()

    def new_turn(self) -> None:
        """
        Begin of a new turn
        """
        self.turn += 1
        self.animation = Animation(
            [
                {
                    "sprite": constant_sprites["new_turn"],
                    "pos": constant_sprites["new_turn_pos"],
                }
            ],
            60,
        )

    def left_click(self, position):
        """

        :param position:
        :return:
        """
        if self.active_menu:
            self.execute_action(self.active_menu.click(position))
            return

        # Player can only react to active menu if it is not his turn
        if self.side_turn is not EntityTurn.PLAYER:
            return

        if self.selected_player is not None:
            if self.game_phase is not LevelStatus.INITIALIZATION:
                if self.possible_moves:
                    # Player is waiting to move
                    for move in self.possible_moves:
                        if pygame.Rect(move, (TILE_SIZE, TILE_SIZE)).collidepoint(
                            position
                        ):
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
                        if pygame.Rect(attack, (TILE_SIZE, TILE_SIZE)).collidepoint(
                            position
                        ):
                            entity = self.get_entity_on_case(attack)
                            self.duel(
                                self.selected_player,
                                entity,
                                self.players + self.entities["allies"],
                                self.entities["foes"],
                                self.selected_player.attack_kind,
                            )
                            # Turn is finished
                            self.background_menus = []
                            self.selected_player.end_turn()
                            self.selected_player = None
                            return
                elif self.possible_interactions:
                    # Player is waiting to interact
                    for interact in self.possible_interactions:
                        if pygame.Rect(interact, (TILE_SIZE, TILE_SIZE)).collidepoint(
                            position
                        ):
                            entity = self.get_entity_on_case(interact)
                            self.interact(self.selected_player, entity, interact)
                            return
            else:
                # Initialization phase : player try to change the place of the selected character
                for tile in self.possible_placements:
                    if pygame.Rect(tile, (TILE_SIZE, TILE_SIZE)).collidepoint(position):
                        # Test if a character is on the tile, in this case, characters are swapped
                        entity = self.get_entity_on_case(tile)
                        if entity:
                            entity.set_initial_pos(self.selected_player.position)

                        self.selected_player.set_initial_pos(tile)
                        return
            return
        for player in self.players:
            if player.is_on_position(position):
                if player.turn_is_finished():
                    self.active_menu = menu_creator_manager.create_status_menu(
                        {
                            "info_alteration": self.open_alteration_description,
                            "info_skill": self.open_skill_description,
                        },
                        player,
                    )
                else:
                    player.selected = True
                    self.selected_player = player
                    self.possible_moves = self.get_possible_moves(
                        player.position,
                        player.max_moves + player.get_stat_change("speed"),
                    )
                    self.possible_attacks = (
                        self.get_possible_attacks(
                            self.possible_moves, self.selected_player.reach, True
                        )
                        if player.can_attack()
                        else {}
                    )
                return
        for entity in self.entities["foes"] + self.entities["allies"]:
            if entity.is_on_position(position):
                self.active_menu = menu_creator_manager.create_status_entity_menu(
                    self.open_alteration_description, entity
                )
                return

        is_initialization = self.game_phase is LevelStatus.INITIALIZATION
        self.active_menu = menu_creator_manager.create_main_menu(
            {
                "save": self.open_save_menu,
                "suspend": self.exit_game,
                "start": self.start_game,
                "diary": lambda: self.open_menu(
                    menu_creator_manager.create_diary_menu(self.diary_entries),
                    is_previous_visible=True,
                ),
                "end_turn": self.end_turn,
            },
            is_initialization,
            position,
        )

    def right_click(self):
        """

        :return:
        """
        if self.selected_player:
            if self.possible_moves:
                # Player was waiting to move
                self.selected_player.selected = False
                self.selected_player = None
                self.possible_moves = {}
            elif self.active_menu is not None:
                # Test if player is on character's main menu, in this case,
                # current move should be cancelled if possible
                if self.active_menu.type is CharacterMenu:
                    if self.selected_player.cancel_move():
                        if self.turn_items is not None:
                            for item in self.turn_items:
                                if item[1] == self.selected_player:
                                    item[2].remove_item(item[0])
                                    self.selected_player.set_item(item[0])
                                else:
                                    self.selected_player.remove_item(item[0])
                                    item[1].set_item(item[0])
                            self.turn_items.clear()
                        self.selected_player.selected = False
                        self.selected_player = None
                        self.possible_moves = {}
                        self.active_menu = None
                    return
                self.execute_action(
                    self.active_menu.buttons[
                        len(self.active_menu.buttons) - 1
                    ].action_triggered()
                )
            # Want to cancel an interaction (not already performed)
            elif self.possible_interactions or self.possible_attacks:
                self.selected_player.cancel_interaction()
                self.possible_interactions = []
                self.possible_attacks = []
                self.active_menu = self.background_menus.pop()[0]
            return
        # Test if player is on main menu
        if self.active_menu is not None:
            self.execute_action(lambda: self.close_active_menu(False))
        if self.watched_ent:
            self.watched_ent = None
            self.possible_moves = {}
            self.possible_attacks = []

    def click(self, button, position):
        """

        :param button:
        :param position:
        :return:
        """
        # No event if there is an animation or it is not player turn
        if self.animation:
            return

        # 1 is equals to left button
        if button == 1:
            self.left_click(position)
        # 3 is equals to right button
        elif button == 3:
            self.right_click()

    def button_down(self, button, position):
        """

        :param button:
        :param position:
        :return:
        """
        # 3 is equals to right button
        if button == 3:
            if (
                not self.active_menu
                and not self.selected_player
                and self.side_turn is EntityTurn.PLAYER
            ):
                for collection in self.entities.values():
                    for entity in collection:
                        if isinstance(
                            entity, Movable
                        ) and entity.get_rect().collidepoint(position):
                            self.watched_ent = entity
                            self.possible_moves = self.get_possible_moves(
                                entity.position, entity.max_moves
                            )
                            reach = self.watched_ent.reach
                            self.possible_attacks = {}
                            if entity.can_attack():
                                self.possible_attacks = self.get_possible_attacks(
                                    self.possible_moves,
                                    reach,
                                    isinstance(entity, Character),
                                )
                            return

    def motion(self, position):
        """

        :param position:
        :return:
        """
        if self.active_menu:
            self.active_menu.motion(position)
        else:
            self.hovered_ent = None
            for collection in self.entities.values():
                for ent in collection:
                    if ent.get_rect().collidepoint(position):
                        self.hovered_ent = ent
                        return
