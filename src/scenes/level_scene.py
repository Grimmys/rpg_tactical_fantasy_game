"""
Define Level class, the main scene of the game,
corresponding to an ongoing level.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from enum import IntEnum, auto
from typing import Optional, Union

import pygame
import pytmx
from pygamepopup.components import BoxElement, Button, InfoBox, TextElement
from pygamepopup.components.image_button import ImageButton
from pygamepopup.menu_manager import MenuManager

from src.constants import (BLACK, GRID_HEIGHT, GRID_WIDTH,
                           ITEM_DELETE_MENU_WIDTH, ITEM_INFO_MENU_WIDTH,
                           ITEM_MENU_WIDTH, MAX_MAP_HEIGHT, MENU_HEIGHT,
                           MENU_WIDTH, ORANGE, TILE_SIZE, WIN_HEIGHT,
                           WIN_WIDTH)
from src.game_entities.alteration import Alteration
from src.game_entities.breakable import Breakable
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.destroyable import DamageKind, Destroyable
from src.game_entities.door import Door
from src.game_entities.effect import Effect
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Foe
from src.game_entities.fountain import Fountain
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.key import Key
from src.game_entities.mission import Mission, MissionType
from src.game_entities.movable import Movable
from src.game_entities.objective import Objective
from src.game_entities.obstacle import Obstacle
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.shop import Shop
from src.game_entities.skill import Skill
from src.game_entities.weapon import Weapon
from src.gui.animation import Animation, Frame
from src.gui.constant_sprites import (ATTACKABLE_OPACITY, INTERACTION_OPACITY,
                                      LANDING_OPACITY, constant_sprites)
from src.gui.fonts import fonts
from src.gui.position import Position
from src.gui.sidebar import Sidebar
from src.gui.tools import blit_alpha
from src.scenes.scene import QuitActionKind, Scene
from src.services import load_from_tmx_manager as tmx_loader
from src.services import load_from_xml_manager as loader
from src.services import menu_creator_manager
from src.services.language import *
from src.services.menu_creator_manager import (CHARACTER_ACTION_MENU_ID,
                                               INVENTORY_MENU_ID, SHOP_MENU_ID,
                                               create_event_dialog,
                                               create_save_dialog)
from src.services.menus import CharacterMenu
from src.services.save_state_manager import SaveStateManager


class LevelStatus(IntEnum):
    VERY_BEGINNING = auto()
    INITIALIZATION = auto()
    IN_PROGRESS = auto()
    ENDED_VICTORY = auto()
    ENDED_DEFEAT = auto()


class LevelEntityCollections:
    def __init__(self):
        self.obstacles: list[Obstacle] = []
        self.players: list[Player] = []
        self.allies: list[Character] = []
        self.foes: list[Foe] = []
        self.chests: list[Chest] = []
        self.buildings: list[Building] = []
        self.breakables: list[Breakable] = []
        self.portals: list[Portal] = []
        self.fountains: list[Fountain] = []
        self.objectives: list[Objective] = []
        self.doors: list[Door] = []

    def values(self):
        return self.__dict__.values()

    def update(self, entities: dict[str, Sequence[Entity]]):
        self.__dict__.update(entities)


class EntityTurn(IntEnum):
    PLAYER = 0
    ALLIES = 1
    FOES = 2

    def get_next(self) -> EntityTurn:
        """
        Return the next entity turn, according to the current one
        """
        next_value = (
            self.value + 1 if self.value + 1 < len(EntityTurn.__members__) else 0
        )
        return EntityTurn(next_value)


class LevelScene(Scene):
    """
    This class is the main scene of the game, handling all the actions of the players for
    an ongoing level, and also apply the game logic of the level (manage animations, IA turns etc.).

    Keywords arguments:
    screen -- the pygame Surface related to the level
    directory -- the relative path to the directory where all static data
    concerning the level are stored
    number -- the number identifying the level
    status -- the status of the game for this level
    turn -- the value of the current turn (0 by default for new game)
    data -- saved data in XML format in case where the game is loaded from a save
    players -- the list of players on the level

    Attributes:
    active_screen_part -- the sub part of the screen containing all the elements of the level
    directory -- the relative path to the directory where all static data
    concerning the level are stored
    number -- the number identifying the level
    map -- a dictionary containing the properties of the level's map
    chapter -- the id corresponding to the chapter in which the level is part
    name -- the full title of the level
    is_loaded -- whether the level is ready to be played or not
    obstacles -- the list of obstacles on the level
    events -- a structure containing the data about all the events that could occur
    possible_placements -- the list of available initial positions for players
    menu_manager -- the reference to the menu manager entity
    a boolean value is associated to each menu in the background to know
    if it should be displayed or not
    players -- the list of players that are still actives on the level
    entities -- the structure containing all the entities of the level by category
    passed_players -- the list of players who left the level
    missions -- the list of missions to be done
    main_mission -- the main mission that is the winning condition for players
    victory -- a boolean indicating whether the game is finished by a victory or not
    defeat -- a boolean indicating whether the game is finished by a defeat or not
    possible_moves -- the collection of moves that can be done by the active player
    possible_attacks -- the collection of attacks that can be made by the active player
    possible_interactions -- the collection of interactions that can be made by the active player
    selected_player -- the active player
    selected_item -- the currently selected item by a player
    active_shop -- the currently visited shop
    quit_request -- a boolean indicating if an exit request has been made
    game_phase -- the active phase of the game
    side_turn -- indicated which side should play (players, allies or foes)
    turn -- the value of the current turn
    animation -- a reference to the ongoing animation if there is any
    watched_entity -- the entity of the level for which its potential actions should be displayed
    hovered_entity -- the entity of the level which is currently hovered
    sidebar -- the reference to the sidebar displaying various information
    wait_for_teleportation_destination -- a boolean indicating if the level is waiting for player
    to choose for the destination of a teleportation
    diary_entries -- the log of the most recent battles
    traded_items -- the items that have been trade during the current player turn
    traded_gold -- the gold that have been trade during the current player turn
    wait_sfx -- the sound that should be started when a player ends his turn
    inventory_sfx -- the sound that should be started when the inventory screen is opening
    armor_sfx -- the sound that should be started when the equipment screen is opening
    talk_sfx -- the sound that should be started when a talk is started between two characters
    gold_sfx -- the sound that should be started when a player obtain gold
    """

    IDS = [0, 1, 2, 3]

    def __init__(
        self,
        screen: pygame.Surface,
        directory: str,
        number: int,
        status: LevelStatus = LevelStatus.VERY_BEGINNING,
        turn: int = 0,
        data: Optional[etree.Element] = None,
        players: Optional[Sequence[Player]] = None,
    ) -> None:
        if players is None:
            players = []

        super().__init__(screen)
        self.active_screen_part = self._compute_active_screen_part()

        Shop.interaction_callback = self.interact_item_shop
        Shop.buy_interface_callback = lambda: self.menu_manager.open_menu(
            self.active_shop.menu
        )
        Shop.sell_interface_callback = self.open_sell_interface

        self.directory: str = directory
        self.number: int = number

        self.tmx_data = pytmx.load_pygame(self.directory + "map.tmx")
        self.tmx_map_properties_data = pytmx.load_pygame(
            DATA_PATH + self.directory + "map_properties.tmx"
        )
        map_width, map_height = (
            self.tmx_data.width * TILE_SIZE,
            self.tmx_data.height * TILE_SIZE,
        )
        map_static_content = tmx_loader.load_ground(
            self.tmx_data, (map_width, map_height)
        )

        self.map: dict[str, any] = {
            "img": map_static_content,
            "width": map_width,
            "height": map_height,
            "x": (GRID_WIDTH - self.tmx_data.width) // 2 * TILE_SIZE,
            "y": (GRID_HEIGHT - self.tmx_data.height) // 2 * TILE_SIZE,
        }

        self.data: Optional[etree.Element] = data

        self.chapter: int = self.tmx_map_properties_data.properties["chapter_id"]
        self.name: str = self.tmx_map_properties_data.properties["level_name"]

        self.is_loaded: bool = False

        self.events: dict[str, any] = {}
        self.player_possible_placements: Sequence[Position] = []

        self.menu_manager = MenuManager(self.screen)
        self.players: list[Player] = players
        self.escaped_players: list[Player] = []

        self.entities: LevelEntityCollections = LevelEntityCollections()

        self.missions: Optional[list[Mission]] = None
        self.main_mission: Optional[Mission] = None

        # Booleans for end game
        # TODO : these booleans are mutually exclusive and so seem a little redundant.
        #  Having only one variable with three different states (victory, defeat or "not finished")
        #  may be better.
        self.victory: bool = False
        self.defeat: bool = False

        # Data structures for possible actions
        self.possible_moves: dict[Position, int] = {}
        self.possible_attacks: list[Position] = []
        self.possible_interactions: list[Position] = []

        # Storage of current selected entity
        self.selected_player: Optional[Player] = None
        self.selected_item: Optional[Item] = None
        self.active_shop: Optional[Shop] = None

        self.quit_request: bool = False
        self.game_phase: LevelStatus = status
        self.side_turn: EntityTurn = EntityTurn.PLAYER
        self.turn: int = turn
        self.animation: Optional[Animation] = None
        self.watched_entity: Optional[Movable] = None
        self.hovered_entity: Optional[Entity] = None
        self.sidebar: Optional[Sidebar] = None
        self.wait_for_teleportation_destination: bool = False
        self.diary_entries: list[list[BoxElement]] = []
        self.traded_items: list[list[Union[Item, Player]]] = []
        self.traded_gold: list[list[Union[int, Player]]] = []

        self.wait_sfx: Optional[pygame.mixer.Sound] = None
        self.inventory_sfx: Optional[pygame.mixer.Sound] = None
        self.armor_sfx: Optional[pygame.mixer.Sound] = None
        self.talk_sfx: Optional[pygame.mixer.Sound] = None
        self.gold_sfx: Optional[pygame.mixer.Sound] = None

    @property
    def diary_entries_text_element_set(self):
        """
        Return a list of TextElements being shown in the menu.
        """
        default_diary_entries = [
            [
                TextElement(
                    STR_DEFAULT_DIARY_BODY_CONTENT,
                    font=fonts["ITEM_DESC_FONT"],
                )
            ]
        ]
        if self.diary_entries:
            return self.diary_entries
        return default_diary_entries

    def no_dont_save(self):
        self.menu_manager.close_active_menu()

    def yes_save(self):
        self.menu_manager.close_active_menu()
        self.open_save_menu()

    def load_level_content(self) -> None:
        """
        Load all the content of the level
        """

        self.events = tmx_loader.load_events(
            self.tmx_data, DATA_PATH + self.directory, self.map["x"], self.map["y"]
        )

        self.player_possible_placements = tmx_loader.load_player_placements(
            self.tmx_data, self.map["x"], self.map["y"]
        )

        self.entities.players = self.players
        self.entities.obstacles = tmx_loader.load_obstacles(
            self.tmx_data, self.map["x"], self.map["y"]
        )

        if self.data is None:
            # Game is new
            gap_x, gap_y = (self.map["x"], self.map["y"])
            if "before_init" in self.events:
                if "dialogs" in self.events["before_init"]:
                    for dialog in self.events["before_init"]["dialogs"]:
                        self.menu_manager.open_menu(create_event_dialog(dialog))
                if "new_players" in self.events["before_init"]:
                    for player_el in self.events["before_init"]["new_players"]:
                        player = loader.init_player(player_el["name"])
                        player.position = player_el["position"]
                        self.players.append(player)
            if self.number != 0:
                # Level_0 doesn't need save reminder
                self.menu_manager.open_menu(
                    create_save_dialog({"yes": self.yes_save, "no": self.no_dont_save})
                )

            self._determine_players_initial_position()

            self.entities.foes = tmx_loader.load_foes(self.tmx_data, gap_x, gap_y)
            self.entities.chests = tmx_loader.load_chests(self.tmx_data, gap_x, gap_y)
            self.entities.allies = tmx_loader.load_allies(self.tmx_data, gap_x, gap_y)
            self.entities.buildings = tmx_loader.load_buildings(
                self.tmx_data, DATA_PATH + self.directory, gap_x, gap_y, 500
            )
            self.entities.breakables = tmx_loader.load_breakables(
                self.tmx_data, gap_x, gap_y
            )
            self.entities.portals = tmx_loader.load_portals(self.tmx_data, gap_x, gap_y)
            self.entities.doors = tmx_loader.load_doors(self.tmx_data, gap_x, gap_y)
            self.entities.fountains = tmx_loader.load_fountains(
                self.tmx_data, gap_x, gap_y
            )

        else:
            # Game is loaded from a save (data)
            gap_x, gap_y = (0, 0)
            if self.game_phase == LevelStatus.VERY_BEGINNING:
                # If game is in very beginning, show dialogs
                if "before_init" in self.events:
                    if "dialogs" in self.events["before_init"]:
                        for dialog in self.events["before_init"]["dialogs"]:
                            self.menu_manager.open_menu(create_event_dialog(dialog))
            self.players.extend(loader.load_players(self.data))
            self.escaped_players = loader.load_escaped_players(self.data)
            self.entities.update(
                loader.load_all_entities_from_save(self.data, gap_x, gap_y)
            )

        self.missions, self.main_mission = tmx_loader.load_missions(
            self.tmx_data,
            self.tmx_map_properties_data,
            self.players,
            self.map["x"],
            self.map["y"],
        )
        self.entities.objectives = [
            objective
            for mission in self.missions
            for objective in mission.objective_tiles
        ]

        self.sidebar = Sidebar(
            (MENU_WIDTH, MENU_HEIGHT),
            Position(0, MAX_MAP_HEIGHT),
            self.missions,
            self.number,
        )

        self.wait_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "waiting.ogg"))
        self.inventory_sfx = pygame.mixer.Sound(
            os.path.join("sound_fx", "inventory.ogg")
        )
        self.armor_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "armor.ogg"))
        self.talk_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "talking.ogg"))
        self.gold_sfx = pygame.mixer.Sound(os.path.join("sound_fx", "trade.ogg"))

        self.is_loaded = True

    def _determine_players_initial_position(self):
        for player in self.players:
            for tile in self.player_possible_placements:
                if self.get_entity_on_tile(tile) is None:
                    player.set_initial_pos(tile)
                    break
            else:
                print(STR_ERROR_NOT_ENOUGH_TILES_TO_SET_PLAYERS)

    def open_save_menu(self) -> None:
        """
        Replace the current active menu by a freshly created save game interface
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_save_menu(self.save_game)
        )

    def save_game(self, slot_id: int) -> None:
        """
        Save the current state of the game in a file on local disk

        Keyword arguments:
        slot_id -- the id of the slot that should be used to save
        """
        save_state_manager = SaveStateManager(self)
        save_state_manager.save_game(slot_id)
        self.menu_manager.open_menu(
            InfoBox(
                STR_GAME_HAS_BEEN_SAVED,
                [[]],
                width=ITEM_MENU_WIDTH,
            )
        )

    def exit_game(self) -> None:
        """
        Handle the end of the level
        """
        # At next update, level will be destroyed
        self.quit_request = True
        if self.game_phase not in (LevelStatus.ENDED_VICTORY, LevelStatus.ENDED_DEFEAT):
            self.game_phase = LevelStatus.ENDED_DEFEAT

    def is_game_started(self) -> bool:
        """
        Return whether the game is started or not
        """
        return self.game_phase is not LevelStatus.INITIALIZATION

    def end_level(self, animation_surface: pygame.Surface, position: Position) -> None:
        """
        Process to the end of level.
        In case of victory, verify for each secondary objectives if they have been accomplished.

        Keyword arguments:
        animation_surface -- the surface containing the final animation of the level
        position -- the position of the final animation
        """
        self.menu_manager.clear_menus()
        # Check if some optional objectives have been completed
        if self.main_mission.ended:
            for mission in self.missions:
                if not mission.main and mission.ended:
                    self.menu_manager.open_menu(
                        menu_creator_manager.create_reward_menu(mission)
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
                        self.menu_manager.open_menu(create_event_dialog(dialog))
        self.animation = Animation([Frame(animation_surface, position)], 180)

    def update_state(self) -> bool:
        """
        Update the state of the game.
        Let the animation progress if there is any.
        Verify if victory or defeat conditions are met.
        Handle next AI action if it's not player's turn.

        Return whether the game should be ended or not.
        """
        if self.quit_request:
            return True

        if self.animation:
            if self.animation.animate():
                self.animation = None
                if (
                    self.game_phase > LevelStatus.IN_PROGRESS
                    and not self.menu_manager.active_menu
                ):
                    self.exit_game()
            return False

        if self.menu_manager.active_menu is not None:
            return False

        if (
            self.game_phase is LevelStatus.ENDED_DEFEAT
            or self.game_phase is LevelStatus.ENDED_VICTORY
        ):
            return True

        for mission in self.missions:
            mission.update_state(entities=self.entities, turns=self.turn)
        if self.main_mission.ended:
            self.victory = True

        if not self.players:
            if not self.main_mission.succeeded_chars:
                self.defeat = True
            else:
                self.victory = True

        if self.victory:
            self.end_level(constant_sprites["victory"], constant_sprites["victory_pos"])
            self.game_phase = LevelStatus.ENDED_VICTORY
            self.victory = False
            return False
        if self.defeat:
            self.end_level(constant_sprites["defeat"], constant_sprites["defeat_pos"])
            self.game_phase = LevelStatus.ENDED_DEFEAT
            self.defeat = False
            return False

        if self.selected_player:
            self.selected_player.move()
            if (
                self.selected_player.is_waiting_post_action()
                and not self.possible_attacks
                and not self.possible_interactions
            ):
                self.open_player_menu()
            return False

        entities: list[Movable] = []
        if self.side_turn is EntityTurn.PLAYER:
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.entities.allies
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities.foes

        for entity in entities:
            if not entity.turn_is_finished():
                if self.side_turn is not EntityTurn.PLAYER:
                    self.process_entity_action(
                        entity, (self.side_turn is EntityTurn.ALLIES)
                    )
                break
        else:
            self.side_turn = self.side_turn.get_next()
            self.begin_turn()

        return False

    def open_player_menu(self) -> None:
        """
        Open the menu displaying all the actions a playable character can do
        """
        interactable_entities: list[Entity] = (
            self.entities.chests
            + self.entities.portals
            + self.entities.doors
            + self.entities.fountains
            + self.entities.allies
            + self.players
        )
        self.menu_manager.open_menu(
            menu_creator_manager.create_player_menu(
                {
                    "inventory": self.open_inventory,
                    "equipment": self.open_equipment,
                    "status": self.open_status_interface,
                    "wait": self.end_active_character_turn,
                    "visit": self.select_visit,
                    "trade": lambda: self.select_interaction_with(Player),
                    "open_chest": self.try_open_chest,
                    "pick_lock": self.select_pick_lock,
                    "open_door": self.try_open_door,
                    "use_portal": lambda: self.select_interaction_with(Portal),
                    "drink": lambda: self.select_interaction_with(Fountain),
                    "talk": self.select_talk,
                    "take": self.take_objective,
                    "attack": self.select_attack_target,
                },
                self.selected_player,
                self.entities.buildings,
                interactable_entities,
                self.missions,
                self.entities.foes,
            )
        )

    def display(self) -> None:
        """
        Display all the elements of the level.
        Display the ongoing animation if there is any.
        Display also all the menus in the background (that should be visible)
        and lastly the active menu.
        """
        self.active_screen_part.blit(self.map["img"], (self.map["x"], self.map["y"]))
        self.sidebar.display(self.active_screen_part, self.turn, self.hovered_entity)

        for mission in self.missions:
            mission.display(self.active_screen_part)

        for collection in self.entities.values():
            for entity in collection:
                entity.display(self.active_screen_part)
                if isinstance(entity, Destroyable):
                    entity.display_hit_points(self.active_screen_part)

        if self.watched_entity:
            self.show_possible_actions(self.watched_entity, self.active_screen_part)

        # If the game hasn't yet started
        if self.game_phase is LevelStatus.INITIALIZATION:
            self.show_possible_placements(self.active_screen_part)
        else:
            if self.selected_player:
                # If player is waiting to move
                if self.possible_moves:
                    self.show_possible_actions(
                        self.selected_player, self.active_screen_part
                    )
                elif self.possible_attacks:
                    self.show_possible_attacks(
                        self.selected_player, self.active_screen_part
                    )
                elif self.possible_interactions:
                    self.show_possible_interactions(self.active_screen_part)

        if self.animation:
            self.animation.display(self.active_screen_part)
        else:
            self.menu_manager.display()

    def show_possible_actions(self, movable: Movable, screen: pygame.Surface) -> None:
        """
        Display all the possible actions of the given movable entity

        Keyword arguments:
        movable -- the movable entity concerned
        screen -- the screen on which the possibilities should be drawn
        """
        self.show_possible_moves(movable, screen)
        self.show_possible_attacks(movable, screen)

    def show_possible_attacks(self, movable: Movable, screen: pygame.Surface) -> None:
        """
        Display all the possible attacks of the given movable entity

        Keyword arguments:
        movable -- the movable entity concerned
        screen -- the screen on which the possibilities should be drawn
        """
        for tile in self.possible_attacks:
            if movable.position != tile:
                blit_alpha(
                    screen, constant_sprites["attackable"], tile, ATTACKABLE_OPACITY
                )

    def show_possible_moves(self, movable: Movable, screen: pygame.Surface) -> None:
        """
        Display all the possible moves of the given movable entity

        Keyword arguments:
        movable -- the movable entity concerned
        screen -- the screen on which the possibilities should be drawn
        """
        for tile in self.possible_moves:
            if movable.position != tile:
                blit_alpha(screen, constant_sprites["landing"], tile, LANDING_OPACITY)

    def show_possible_interactions(self, screen: pygame.Surface) -> None:
        """
        Display all the possible interactions of the active player

        Keyword arguments:
        screen -- the screen on which the possibilities should be drawn
        """
        for tile in self.possible_interactions:
            blit_alpha(
                screen, constant_sprites["interaction"], tile, INTERACTION_OPACITY
            )

    def show_possible_placements(self, screen: pygame.Surface) -> None:
        """
        Display all the available tiles for initial placement of the player characters

        Keyword arguments:
        screen -- the screen on which the possibilities should be drawn
        """
        for tile in self.player_possible_placements:
            blit_alpha(screen, constant_sprites["landing"], tile, LANDING_OPACITY)

    def start_game(self) -> None:
        """
        Handle the launch of the game.
        Begin a new turn (the first one).
        Trigger the events that should happen after the initialization phase if any.
        """
        self.menu_manager.close_active_menu()
        self.game_phase = LevelStatus.IN_PROGRESS
        self.new_turn()
        if "after_init" in self.events:
            if "dialogs" in self.events["after_init"]:
                for dialog in self.events["after_init"]["dialogs"]:
                    self.menu_manager.open_menu(create_event_dialog(dialog))
            if "new_players" in self.events["after_init"]:
                for player_el in self.events["after_init"]["new_players"]:
                    player = loader.init_player(player_el["name"])
                    player.position = player_el["position"]
                    self.players.append(player)

    def get_next_cases(self, position: Position) -> list[Optional[Entity]]:
        """
        Return the entities that are next to the given tile

        Keyword arguments:
        position -- the position of the tile whose neighbors must be computed
        """
        tiles_content: list[Optional[Entity]] = []
        for x_coordinate in range(-1, 2):
            for y_coordinate in (1 - abs(x_coordinate), -1 + abs(x_coordinate)):
                tile_x: int = position[0] + (x_coordinate * TILE_SIZE)
                tile_y: int = position[1] + (y_coordinate * TILE_SIZE)
                tile_position: Position = Position(tile_x, tile_y)
                tile_content: Optional[Entity] = self.get_entity_on_tile(tile_position)
                tiles_content.append(tile_content)
        return tiles_content

    def get_possible_moves(
        self, position: Position, max_moves: int
    ) -> dict[Position, int]:
        """
        Return all the possible moves with their distance from the starting position

        Keyword arguments:
        position -- the starting position
        max_moves -- the maximum number of tiles that could be traveled
        """
        new_position = Position(position.x, position.y)
        tiles: dict[Position, int] = {new_position: 0}
        previously_computed_tiles: dict[Position, int] = tiles
        for i in range(1, max_moves + 1):
            tiles_current_level: dict[Position, int] = {}
            for tile in previously_computed_tiles:
                for x_coordinate in range(-1, 2):
                    for y_coordinate in (1 - abs(x_coordinate), -1 + abs(x_coordinate)):
                        tile_x: int = tile[0] + (x_coordinate * TILE_SIZE)
                        tile_y: int = tile[1] + (y_coordinate * TILE_SIZE)
                        tile_position = Position(tile_x, tile_y)
                        if (
                            self.is_tile_available(tile_position)
                            and tile_position not in tiles
                        ):
                            tiles_current_level[tile_position] = i
            tiles.update(previously_computed_tiles)
            previously_computed_tiles = tiles_current_level
        tiles.update(previously_computed_tiles)
        return tiles

    def get_possible_attacks(
        self,
        possible_moves: Sequence[Position],
        reach: Sequence[int],
        from_ally_side: bool,
    ) -> set[Position]:
        """
        Return all the tiles that could be targeted for an attack from a specific entity

        Keyword arguments:
        possible_moves -- the sequence of all possible movements
        reach -- the reach of the attacking entity
        from_ally_side -- a boolean indicating whether this is a friendly attack or not
        """
        tiles: list[Position] = []

        entities = list(self.entities.breakables)
        if from_ally_side:
            entities += self.entities.foes
        else:
            entities += self.entities.allies + self.players

        for entity in entities:
            for i in reach:
                for x_coordinate in range(-i, i + 1):
                    for y_coordinate in (i - abs(x_coordinate), -i + abs(x_coordinate)):
                        tile_x: int = entity.position[0] + (x_coordinate * TILE_SIZE)
                        tile_y: int = entity.position[1] + (y_coordinate * TILE_SIZE)
                        tile_position = Position(tile_x, tile_y)
                        if tile_position in possible_moves:
                            tiles.append(entity.position)

        return set([Position(i.x, i.y) for i in tiles])

    def is_tile_available(self, tile: Position) -> bool:
        """
        Return whether the given tile can be accessed or not

        Keyword arguments:
        tile -- the position of the tile
        """
        min_case: Position = Position(self.map["x"], self.map["y"])
        max_case: Position = Position(
            self.map["x"] + self.map["width"],
            self.map["y"] + self.map["height"],
        )
        if not (
            all(
                minimum <= case < maximum
                for minimum, case, maximum in zip(min_case, tile, max_case)
            )
        ):
            return False

        entity_on_tile = self.get_entity_on_tile(tile)
        if isinstance(entity_on_tile, Objective):
            if entity_on_tile.is_walkable:
                return True

        return entity_on_tile is None

    def get_entity_on_tile(self, tile: Position) -> Optional[Entity]:
        """
        Return the entity that is on the given tile if there is any

        Keyword arguments:
        tile -- the position of the tile
        """
        # Check all entities
        for collection in self.entities.values():
            for entity in collection:
                if entity.position == tile:
                    return entity
        return None

    def determine_path_to(
        self, destination_tile: Position, distance_for_tile: dict[Position, int]
    ) -> list[Position]:
        """
        Return an ordered list of position that represent the path from one tile to another

        Keyword arguments:
        destination_tile -- the position of the destination
        distance -- the distance between the starting tile and the destination
        """
        path: list[Position] = [destination_tile]
        current_tile: Position = destination_tile
        while distance_for_tile[current_tile] > 1:
            # Check for neighbour cases
            available_tiles: dict[Position, int] = self.get_possible_moves(current_tile, 1)
            for tile in available_tiles:
                if tile in distance_for_tile:
                    distance = distance_for_tile[tile]
                    if distance < distance_for_tile[current_tile]:
                        current_tile = tile
                        path.insert(0, current_tile)
        return path

    def distance_between_all(
        self, entity: Entity, all_other_entities: Sequence
    ) -> dict[Entity, int]:
        """
        Return the distance between each different given entities for a reference entity

        Keyword arguments:
        entity -- the entity for which the distance from all other entities should be computed
        all_other_entities -- all other entities for which the distance should be computed
        """
        free_tiles_distance: dict[Position, int] = self.get_possible_moves(
            entity.position,
            (self.map["width"] * self.map["height"]) // (TILE_SIZE * TILE_SIZE),
        )
        entities_distance: dict[Entity, int] = {
            entity: self.map["width"] * self.map["height"]
            for entity in all_other_entities
        }
        for tile, distance in free_tiles_distance.items():
            for neighbour in self.get_next_cases(tile):
                if (
                    neighbour in all_other_entities
                    and distance < entities_distance[neighbour]
                ):
                    entities_distance[neighbour] = distance
        return entities_distance

    def open_chest(self, actor: Character, chest: Chest) -> None:
        """
        Open a chest and send its content to the given character

        Keyword arguments:
        actor -- the character performing the action
        chest -- the object that is being opened
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
        item_element = ImageButton(
            image_path=item.sprite_path,
            title=str(item),
            disabled=True,
            frame_background_path="imgs/interface/blue_frame.png",
            frame_background_hover_path="imgs/interface/blue_frame.png",
            background_path="imgs/interface/item_frame.png",
            text_color=BLACK,
        )
        item_element.callback = (
            lambda button=item_element, item_reference=item: self.interact_item(
                item_reference, button, is_equipped=False
            )
        )
        element_grid = [
            [item_element],
            [
                TextElement(
                    STR_ITEM_HAS_BEEN_ADDED_TO_UR_INVENTORY,
                    font=fonts["ITEM_DESC_FONT"],
                )
            ],
        ]

        self.menu_manager.open_menu(
            InfoBox(
                STR_YOU_FOUND_IN_THE_CHEST,
                element_grid,
                width=ITEM_MENU_WIDTH,
            )
        )

        self.end_active_character_turn(clear_menus=False)

    def open_door(self, door: Door) -> None:
        """
        Handle the opening of a door.
        Remove it from the level if needed.

        Keyword arguments:
        door -- the door that should be opened
        """
        self.entities.doors.remove(door)

        # TODO: move the creation of the pop-up in menu_creator_manager
        grid_element = [
            [TextElement(STR_DOOR_HAS_BEEN_OPENED, font=fonts["ITEM_DESC_FONT"])]
        ]
        self.menu_manager.open_menu(
            InfoBox(
                str(door),
                grid_element,
                width=ITEM_MENU_WIDTH,
            )
        )

        self.end_active_character_turn(clear_menus=False)

    def ally_to_player(self, character: Character) -> None:
        """
        Cast a character entity to a player.
        It is use when an ally or neutral entity suddenly join the player team.

        Keyword argument:
        character -- the character that should be cast
        """
        self.entities.allies.remove(character)
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
        self.entities.players.append(player)
        player.earn_xp(character.experience)
        player.hit_points = character.hit_points
        player.position = character.position
        player.items = character.items

    def interact(
        self, actor: Character, target: Entity, target_position: Position
    ) -> None:
        """
        Handle the interaction of a character with a given entity

        Keyword arguments:
        actor -- the character starting the interaction
        target -- the target of the interaction
        target_position -- the position of the target
        """
        # Since player chose his interaction, possible interactions should be reset
        self.possible_interactions = []

        # The player is no longer waiting for a target
        self.selected_player.target_selected()

        # Check if target is an empty pos
        if not target:
            if self.wait_for_teleportation_destination:
                self.wait_for_teleportation_destination = False
                actor.position = target_position

                # Turn is finished
                self.end_active_character_turn()
        # Check if player tries to open a chest
        elif isinstance(target, Chest):
            if actor.has_free_space():
                if self.selected_player.current_action is CharacterMenu.OPEN_CHEST:
                    actor.remove_chest_key()
                    self.open_chest(actor, target)
                elif self.selected_player.current_action is CharacterMenu.PICK_LOCK:
                    if not target.pick_lock_initiated:
                        # Lock picking has not been already initiated
                        target.pick_lock_initiated = True
                        # TODO: move the creation of the pop-up in menu_creator_manager
                        element_grid = [
                            [
                                TextElement(
                                    STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO,
                                    font=fonts["ITEM_DESC_FONT"],
                                )
                            ]
                        ]
                        self.menu_manager.open_menu(
                            InfoBox(
                                STR_CHEST,
                                element_grid,
                                width=ITEM_MENU_WIDTH,
                            )
                        )
                        self.end_active_character_turn(clear_menus=False)
                    else:
                        # Lock picking is finished, get content
                        self.open_chest(actor, target)

            else:
                # TODO: move the creation of the pop-up in menu_creator_manager
                self.menu_manager.open_menu(
                    InfoBox(
                        STR_YOU_HAVE_NO_FREE_SPACE_IN_YOUR_INVENTORY,
                        [],
                        width=ITEM_MENU_WIDTH,
                    )
                )
        # Check if player tries to open a door
        elif isinstance(target, Door):
            if self.selected_player.current_action is CharacterMenu.OPEN_DOOR:
                actor.remove_door_key()
                self.open_door(target)
            elif self.selected_player.current_action is CharacterMenu.PICK_LOCK:
                if not target.pick_lock_initiated:
                    # Lock picking has not been already initiated
                    target.pick_lock_initiated = True
                    # TODO: move the creation of the pop-up in menu_creator_manager
                    grid_element = [
                        [
                            TextElement(
                                STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO,
                                font=fonts["ITEM_DESC_FONT"],
                            )
                        ]
                    ]
                    self.menu_manager.open_menu(
                        InfoBox(
                            str(target),
                            grid_element,
                            width=ITEM_MENU_WIDTH,
                        )
                    )
                    self.end_active_character_turn(clear_menus=False)
                else:
                    # Lock picking is finished, get content
                    self.open_door(target)
        # Check if player tries to use a portal
        elif isinstance(target, Portal):
            new_based_position: Position = target.linked_to.position
            possible_positions_with_distance: dict[
                Position, int
            ] = self.get_possible_moves(new_based_position, 1)
            # Remove portal pos since player cannot be on the portal
            del possible_positions_with_distance[new_based_position]
            if possible_positions_with_distance:
                self.possible_interactions = possible_positions_with_distance.keys()
                self.wait_for_teleportation_destination = True
            else:
                self.menu_manager.open_menu(
                    InfoBox(
                        STR_THERE_IS_NO_FREE_SQUARE_AROUND_THE_OTHER_PORTAL,
                        [],
                        width=ITEM_MENU_WIDTH,
                    )
                )
        # Check if player tries to drink in a fountain
        elif isinstance(target, Fountain):
            element_grid = target.drink(actor)
            self.menu_manager.open_menu(
                InfoBox(
                    str(target),
                    element_grid,
                    width=ITEM_MENU_WIDTH,
                )
            )

            self.end_active_character_turn(clear_menus=False)
        # Check if player tries to trade with another player
        elif isinstance(target, Player):
            self.menu_manager.open_menu(
                menu_creator_manager.create_trade_menu(
                    {
                        "interact_item": self.interact_trade_item,
                        "send_gold": self.send_gold,
                    },
                    self.selected_player,
                    target,
                )
            )
        # Check if player tries to talk to a character
        elif isinstance(target, Character):
            pygame.mixer.Sound.play(self.talk_sfx)

            element_grid = target.talk(actor)
            self.menu_manager.open_menu(
                InfoBox(
                    str(target),
                    element_grid,
                    width=ITEM_MENU_WIDTH,
                    title_color=ORANGE,
                )
            )
            # Check if character is now a player
            if target.join_team:
                self.ally_to_player(target)

            self.end_active_character_turn(clear_menus=False)
        # Check if player tries to visit a building
        elif isinstance(target, Building):
            if isinstance(target, Shop):
                self.active_shop = target

            element_grid = target.interact(actor)
            self.menu_manager.open_menu(
                InfoBox(
                    str(target),
                    element_grid,
                    width=ITEM_MENU_WIDTH,
                    title_color=ORANGE,
                )
            )

            self.end_active_character_turn(clear_menus=False)

    def remove_entity(self, entity: Entity) -> None:
        """
        Remove an entity from the level

        Keyword arguments:
        entity -- the entity that should be removed
        """
        collection = None
        if isinstance(entity, Foe):
            collection = self.entities.foes
        elif isinstance(entity, Player):
            collection = self.entities.players
        elif isinstance(entity, Breakable):
            collection = self.entities.breakables
        elif isinstance(entity, Character):
            collection = self.entities.allies
        collection.remove(entity)

    def duel(
        self,
        attacker: Movable,
        target: Destroyable,
        target_allies: Sequence[Destroyable],
        kind: DamageKind,
    ) -> None:
        """
        Handle the development of an attack from one entity to another

        Keyword arguments:
        attacker -- the entity that is making the attack
        target -- the target of the attack
        attacker_allies -- the allies of the attacker
        target_allies -- the allies of the target
        kind -- the nature of the damage that would be dealt
        """
        nb_attacks: int = 2 if "double_attack" in attacker.skills else 1
        for _ in range(nb_attacks):
            experience: int = 0

            if isinstance(target, Character) and target.parried():
                # Target parried attack
                message: str = f_ATTACKER_ATTACKED_TARGET_BUT_PARRIED(attacker, target)
                self.diary_entries.append(
                    [TextElement(message, font=fonts["ITEM_DESC_FONT"])]
                )
                continue

            damage: int = attacker.attack(target)
            real_damage: int = target.hit_points - target.attacked(
                attacker, damage, kind, target_allies
            )
            self.diary_entries.append(
                [
                    TextElement(
                        f_ATTACKER_DEALT_DAMAGE_TO_TARGET(
                            attacker, target, real_damage
                        ),
                        font=fonts["ITEM_DESC_FONT"],
                    )
                ]
            )
            # XP gain for dealt damage
            experience += real_damage // 2
            # If target has less than 0 HP at the end of the attack
            if target.hit_points <= 0:
                # XP gain increased
                if isinstance(attacker, Character) and isinstance(target, Foe):
                    experience += target.xp_gain

                self.diary_entries.append(
                    [TextElement(f_TARGET_DIED(target), font=fonts["ITEM_DESC_FONT"])]
                )
                # Loot
                if isinstance(attacker, Player) and isinstance(target, Foe):
                    # Check if foe dropped an item
                    loot: Sequence[Item] = target.roll_for_loot()
                    for item in loot:
                        self.diary_entries.append(
                            [
                                TextElement(
                                    f_TARGET_DROPPED_ITEM(target, item),
                                    font=fonts["ITEM_DESC_FONT"],
                                )
                            ]
                        )
                        if isinstance(item, Gold):
                            attacker.gold += item.amount
                        elif not attacker.set_item(item):
                            self.diary_entries.append(
                                [
                                    TextElement(
                                        STR_BUT_THERE_IS_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_TAKE_IT,
                                        font=fonts["ITEM_DESC_FONT"],
                                    )
                                ]
                            )
                self.remove_entity(target)
            else:
                self.diary_entries.append(
                    [
                        TextElement(
                            f_TARGET_HAS_NOW_NUMBER_HP(target, target.hit_points),
                            font=fonts["ITEM_DESC_FONT"],
                        )
                    ]
                )
                # Check if a side effect is applied to target
                if isinstance(attacker, Character):
                    weapon: Weapon = attacker.get_weapon()
                    if weapon:
                        applied_effects: Sequence[Effect] = weapon.apply_effects(
                            attacker, target
                        )
                        for effect in applied_effects:
                            _, message = effect.apply_on_ent(target)
                            self.diary_entries.append(
                                [TextElement(message, font=fonts["ITEM_DESC_FONT"])]
                            )

            # XP gain
            if isinstance(attacker, Player):
                self.diary_entries.append(
                    [
                        TextElement(
                            f_ATTACKER_EARNED_NUMBER_XP(attacker, experience),
                            font=fonts["ITEM_DESC_FONT"],
                        )
                    ]
                )
                if attacker.earn_xp(experience):
                    # Attacker gained a level
                    self.diary_entries.append(
                        [
                            TextElement(
                                f_ATTACKER_GAINED_A_LEVEL(attacker),
                                font=fonts["ITEM_DESC_FONT"],
                            )
                        ]
                    )

            if target.hit_points <= 0:
                # Target is dead, no more attack needed.
                break
        while len(self.diary_entries) > 10:
            self.diary_entries.pop(0)

    def process_entity_action(self, entity: Movable, is_ally: bool) -> None:
        """
        Compute the action of a non-playable entity (AI)

        Keyword arguments:
        entity -- the entity for which the action should be computed
        is_ally -- a boolean indicating if the entity is an ally or not
        """
        possible_moves: dict[Position, int] = self.get_possible_moves(
            entity.position, entity.max_moves
        )
        targets: Sequence[Movable] = (
            self.entities.foes if is_ally else self.players + self.entities.allies
        )
        tile: Optional[Position] = entity.act(
            possible_moves, self.distance_between_all(entity, targets)
        )

        if tile:
            if tuple(tile) in possible_moves:
                # Entity choose to move to case
                self.hovered_entity = entity
                path = self.determine_path_to(tile, possible_moves)
                entity.set_move(path)
            else:
                # Entity choose to attack the entity on the tile
                entity_attacked = self.get_entity_on_tile(tile)
                self.duel(entity, entity_attacked, targets, entity.attack_kind)
                entity.end_turn()

    def interact_item_shop(self, item: Item, item_button: Button) -> None:
        """
        Handle the interaction with an item in a shop

        Keyword arguments:
        item -- the concerned item
        button_position -- the position of the button representing the item on interface
        """
        self.selected_item = item
        self.menu_manager.open_menu(
            menu_creator_manager.create_item_shop_menu(
                {
                    "buy_item": self.try_buy_selected_item,
                    "info_item": self.open_selected_item_description,
                },
                item_button.position,
                item,
            )
        )

    def interact_sell_item(self, item: Item, item_button: Button) -> None:
        """
        Handle the interaction with an item from player inventory in a shop

        Keyword arguments:
        item -- the concerned item
        button_position -- the position of the button representing the item on interface
        """
        self.selected_item = item
        self.menu_manager.open_menu(
            menu_creator_manager.create_item_sell_menu(
                {
                    "sell_item": self.try_sell_selected_item,
                    "info_item": self.open_selected_item_description,
                },
                item_button.position,
                item,
            )
        )

    def open_sell_interface(self) -> None:
        """
        Handle the opening of the player inventory in a shop
        """
        free_spaces: int = self.active_shop.current_visitor.nb_items_max - len(
            self.active_shop.current_visitor.items
        )
        items: list[Optional[Item]] = (
            self.active_shop.current_visitor.items + [None] * free_spaces
        )
        self.menu_manager.open_menu(
            menu_creator_manager.create_inventory_menu(
                self.interact_sell_item,
                items,
                self.active_shop.current_visitor.gold,
                is_to_sell=True,
            )
        )

    def end_turn(self) -> None:
        """
        End the current turn
        """
        self.menu_manager.clear_menus()
        for player in self.players:
            player.end_turn()
        self.side_turn = self.side_turn.get_next()
        self.begin_turn()

    def select_visit(self):
        """
        Let the player select the building to visit for the active character
        """
        self.menu_manager.clear_menus()
        self.selected_player.choose_target()
        self.possible_interactions = [
            (
                self.selected_player.position[0],
                self.selected_player.position[1] - TILE_SIZE,
            )
        ]
        self.possible_attacks = []

    def take_objective(self) -> None:
        """
        Verify for each mission if the active player validated it
        """
        for mission in self.missions:
            if (
                mission.type is MissionType.POSITION
                or mission.type is MissionType.TOUCH_POSITION
            ):
                # Verify that character is not the last if the mission is not the main one
                if mission.main or len(self.players) > 1:
                    if mission.is_position_valid(self.selected_player.position):
                        mission.update_state(self.selected_player)
                        self.players.remove(self.selected_player)
                        self.escaped_players.append(self.selected_player)
                        if mission.main and mission.ended:
                            self.victory = True
                        # Turn is finished
                        self.end_active_character_turn()
                        break

    def select_talk(self) -> None:
        """
        Let the player select the character to talk with for the active character
        """
        self.menu_manager.clear_menus()
        self.selected_player.choose_target()
        self.possible_interactions = []
        for entity in self.get_next_cases(self.selected_player.position):
            if isinstance(entity, Character) and not isinstance(entity, Player):
                self.possible_interactions.append(entity.position)

    def select_pick_lock(self) -> None:
        """
        Let the player select the chest or door to pick lock for the active character
        """
        self.menu_manager.clear_menus()
        self.selected_player.current_action = CharacterMenu.PICK_LOCK
        self.selected_player.choose_target()
        self.possible_interactions = []
        for entity in self.get_next_cases(self.selected_player.position):
            if (isinstance(entity, Chest) and not entity.opened) or isinstance(
                entity, Door
            ):
                self.possible_interactions.append(entity.position)

    def try_open_door(self):
        """
        Handle the tentative of opening a door
        """
        # Check if player has a key
        has_key = False
        for item in self.selected_player.items:
            if isinstance(item, Key) and item.for_door:
                has_key = True
                break
        if not has_key:
            info_box = InfoBox(
                STR_YOU_HAVE_NO_KEY_TO_OPEN_A_DOOR,
                [],
                width=ITEM_MENU_WIDTH,
            )
            self.menu_manager.open_menu(info_box)
        else:
            self.selected_player.current_action = CharacterMenu.OPEN_DOOR
            self.select_interaction_with(Door)

    def try_open_chest(self) -> None:
        """
        Handle the tentative of opening a chest
        """
        has_key = False
        for item in self.selected_player.items:
            if isinstance(item, Key) and item.for_chest:
                has_key = True
                break
        if not has_key:
            info_box = InfoBox(
                STR_YOU_HAVE_NO_KEY_TO_OPEN_A_CHEST,
                [],
                width=ITEM_MENU_WIDTH,
            )
            self.menu_manager.open_menu(info_box)
        else:
            self.menu_manager.clear_menus()
            self.selected_player.current_action = CharacterMenu.OPEN_CHEST
            self.selected_player.choose_target()
            self.possible_interactions = []
            for entity in self.get_next_cases(self.selected_player.position):
                if isinstance(entity, Chest) and not entity.opened:
                    self.possible_interactions.append(entity.position)

    def select_attack_target(self):
        """
        Let the player select the foe to attack for the active character
        """
        self.menu_manager.clear_menus()
        self.selected_player.choose_target()
        self.possible_attacks = self.get_possible_attacks(
            [self.selected_player.position], self.selected_player.reach, True
        )
        self.possible_interactions = []

    def open_status_interface(self) -> None:
        """
        Handle the opening of the status interface for the active character
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_status_menu(
                {
                    "info_alteration": self.open_alteration_description,
                    "info_skill": self.open_skill_description,
                },
                self.selected_player,
            )
        )

    def end_active_character_turn(self, clear_menus=True) -> None:
        """
        End the turn of the active character
        """
        pygame.mixer.Sound.play(self.wait_sfx)
        self.selected_item = None
        self.selected_player.end_turn()
        self.selected_player = None
        self.traded_items.clear()
        self.traded_gold.clear()
        self.possible_moves.clear()
        self.possible_attacks.clear()
        self.possible_interactions.clear()
        if clear_menus:
            self.menu_manager.clear_menus()

    def open_equipment(self) -> None:
        """
        Handle the opening of the player equipment interface
        """
        equipments = list(self.selected_player.equipments)
        self.menu_manager.open_menu(
            menu_creator_manager.create_equipment_menu(self.interact_item, equipments),
        )
        pygame.mixer.Sound.play(self.armor_sfx)

    def open_inventory(self) -> None:
        """
        Replace the current active menu by the interface corresponding to the inventory of the
        selected player
        """
        free_spaces: int = self.selected_player.nb_items_max - len(
            self.selected_player.items
        )
        items: list[Optional[Item]] = (
            list(self.selected_player.items) + [None] * free_spaces
        )
        self.menu_manager.open_menu(
            menu_creator_manager.create_inventory_menu(
                self.interact_item, items, self.selected_player.gold
            )
        )
        pygame.mixer.Sound.play(self.inventory_sfx)

    def select_interaction_with(self, entity_kind: type[Entity]) -> None:
        """
        Let the player select the entity to interact with for the active character

        Keyword arguments:
        entity_kind -- the nature of entity for which the player should select an interaction
        """
        self.menu_manager.clear_menus()
        self.selected_player.choose_target()
        self.possible_interactions = []
        for entity in self.get_next_cases(self.selected_player.position):
            if isinstance(entity, entity_kind):
                self.possible_interactions.append(entity.position)

    def interact_item(self, item: Item, item_button: Button, is_equipped: bool) -> None:
        """
        Handle the interaction with an item from player inventory or equipment

        Keyword arguments:
        item -- the concerned item
        button_position -- the position of the button representing the item on interface
        is_equipped -- a boolean indicating if the item is equipped or not
        """
        self.selected_item = item
        self.menu_manager.open_menu(
            menu_creator_manager.create_item_menu(
                {
                    "info_item": self.open_selected_item_description,
                    "throw_item": self.throw_selected_item,
                    "use_item": self.use_selected_item,
                    "unequip_item": self.unequip_selected_item,
                    "equip_item": self.equip_selected_item,
                },
                item_button.get_rect(),
                item,
                is_equipped=is_equipped,
            )
        )

    def interact_trade_item(
        self,
        item: Item,
        item_button: Button,
        players: Sequence[Player],
        is_first_player_owner: bool,
    ) -> None:
        """
        Handle the interaction with an item from player inventory or equipment during a trade

        Keyword arguments:
        item -- the concerned item
        button_position -- the position of the button representing the item on interface
        players -- the players involved in the trade
        is_first_player_owner -- a boolean indicating if the player who initiated the trade is the
        owner of the item
        """
        self.selected_item = item
        self.menu_manager.open_menu(
            menu_creator_manager.create_trade_item_menu(
                {
                    "info_item": self.open_selected_item_description,
                    "trade_item": self.trade_item,
                },
                item_button.position,
                item,
                players,
                is_first_player_owner,
            ),
        )

    def trade_item(
        self, first_player: Player, second_player: Player, is_first_player_owner: bool
    ) -> None:
        """
        Trade an item between to playable characters

        Keyword arguments:
        first_player -- the player who initiated the trade
        second_player -- the partner of the trade
        is_first_player_owner -- a boolean indicating if the player who initiated the trade is the
        owner of the item
        """
        pygame.mixer.Sound.play(self.inventory_sfx)
        owner: Player = first_player if is_first_player_owner else second_player
        receiver: Player = second_player if is_first_player_owner else first_player
        # Add item if possible
        added: bool = receiver.set_item(self.selected_item)
        self.menu_manager.close_active_menu()
        if not added:
            grid_elements = [
                [
                    TextElement(
                        f_ITEM_CANNOT_BE_TRADED_NOT_ENOUGH_PLACE_IN_RECEIVERS_INVENTORY(
                            receiver
                        ),
                        font=fonts["ITEM_DESC_FONT"],
                        margin=(20, 0, 20, 0),
                    )
                ]
            ]
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
            self.menu_manager.close_active_menu()
            self.menu_manager.open_menu(new_trade_menu)

            grid_elements = [
                [
                    TextElement(
                        STR_ITEM_HAS_BEEN_TRADED,
                        font=fonts["ITEM_DESC_FONT"],
                        margin=(20, 0, 20, 0),
                    ),
                ]
            ]

            self.traded_items.append([self.selected_item, owner, receiver])

        self.menu_manager.open_menu(
            InfoBox(
                str(self.selected_item),
                grid_elements,
                width=ITEM_DELETE_MENU_WIDTH,
            )
        )

    def send_gold(
        self,
        first_player: Player,
        second_player: Player,
        is_first_player_sender: bool,
        value: int,
    ) -> None:
        """
        Trade some gold between to playable characters

        Keyword arguments:
        first_player -- the player who initiated the trade
        second_player -- the partner of the trade
        is_first_player_sender -- a boolean indicating if the player who initiated the trade is the
        owner of the gold
        value -- the quantity of gold that should be traded
        """
        pygame.mixer.Sound.play(self.gold_sfx)
        sender: Player = first_player if is_first_player_sender else second_player
        receiver: Player = second_player if is_first_player_sender else first_player
        Player.trade_gold(sender, receiver, value)
        self.traded_gold.append([value, sender, receiver])
        self.menu_manager.close_active_menu()
        self.menu_manager.open_menu(
            menu_creator_manager.create_trade_menu(
                {
                    "interact_item": self.interact_trade_item,
                    "send_gold": self.send_gold,
                },
                first_player,
                second_player,
            )
        )

    def throw_selected_item(self) -> None:
        """
        Remove the selected item from player inventory/equipment
        """
        self.menu_manager.close_active_menu()
        # Remove item from inventory/equipment according to the index
        if isinstance(
            self.selected_item, Equipment
        ) and self.selected_player.has_exact_equipment(self.selected_item):
            self.selected_player.remove_equipment(self.selected_item)
            equipments = list(self.selected_player.equipments)
            new_items_menu = menu_creator_manager.create_equipment_menu(
                self.interact_item, equipments
            )
        else:
            self.selected_player.remove_item(self.selected_item)
            free_spaces: int = self.selected_player.nb_items_max - len(
                self.selected_player.items
            )
            items: list[Optional[Item]] = (
                list(self.selected_player.items) + [None] * free_spaces
            )
            new_items_menu = menu_creator_manager.create_inventory_menu(
                self.interact_item, items, self.selected_player.gold
            )
        # Refresh the inventory menu
        self.menu_manager.replace_given_menu(INVENTORY_MENU_ID, new_items_menu)
        grid_elements = [
            [
                TextElement(
                    STR_ITEM_HAS_BEEN_THROWN_AWAY,
                    font=fonts["ITEM_DESC_FONT"],
                    margin=(20, 0, 20, 0),
                )
            ]
        ]
        self.menu_manager.open_menu(
            InfoBox(
                str(self.selected_item),
                grid_elements,
                width=ITEM_DELETE_MENU_WIDTH,
            )
        )
        self.selected_item = None

    def try_sell_selected_item(self) -> None:
        """
        Handle the sale of the selected item if possible
        """
        self.menu_manager.close_active_menu()
        sold, result_message = self.active_shop.sell(self.selected_item)
        popup_title = str(self.selected_item)
        if sold:
            # Remove ref to item
            self.selected_item = None

            # Update shop screen content (item has been removed from inventory)
            # TODO: very recurrent task that maybe should be extract to a method
            free_spaces: int = self.active_shop.current_visitor.nb_items_max - len(
                self.active_shop.current_visitor.items
            )
            items: list[Optional[Item]] = (
                list(self.active_shop.current_visitor.items) + [None] * free_spaces
            )
            new_sell_menu = menu_creator_manager.create_inventory_menu(
                self.interact_sell_item,
                items,
                self.active_shop.current_visitor.gold,
                is_to_sell=True,
            )
            self.menu_manager.replace_given_menu(SHOP_MENU_ID, new_sell_menu)
        element_grid = [
            [
                TextElement(
                    result_message, font=fonts["ITEM_DESC_FONT"], margin=(20, 0, 20, 0)
                )
            ]
        ]
        self.menu_manager.open_menu(
            InfoBox(
                popup_title,
                element_grid,
                width=ITEM_INFO_MENU_WIDTH,
            )
        )

    def try_buy_selected_item(self) -> None:
        """
        Handle the purchase of the selected item if possible
        """
        result_message = self.active_shop.buy(self.selected_item)
        element_grid = [
            [
                TextElement(
                    result_message, font=fonts["ITEM_DESC_FONT"], margin=(20, 0, 20, 0)
                )
            ]
        ]
        self.menu_manager.replace_given_menu(SHOP_MENU_ID, self.active_shop.menu)
        self.menu_manager.open_menu(
            InfoBox(
                str(self.selected_item),
                element_grid,
                width=ITEM_INFO_MENU_WIDTH,
            )
        )

    def unequip_selected_item(self) -> None:
        """
        Unequip the selected item of the active character if possible
        """
        self.menu_manager.close_active_menu()
        unequipped = self.selected_player.unequip(self.selected_item)
        result_message = (
            STR_THE_ITEM_CANNOT_BE_UNEQUIPPED_NOT_ENOUGH_SPACE_IN_UR_INVENTORY
        )
        if unequipped:
            result_message = STR_THE_ITEM_HAS_BEEN_UNEQUIPPED

            # Update equipment screen content
            new_equipment_menu = menu_creator_manager.create_equipment_menu(
                self.interact_item, self.selected_player.equipments
            )
            # Update the inventory menu (i.e. first menu backward)
            self.menu_manager.close_active_menu()
            self.menu_manager.open_menu(new_equipment_menu)
        element_grid = [
            [
                TextElement(
                    result_message, font=fonts["ITEM_DESC_FONT"], margin=(20, 0, 20, 0)
                )
            ]
        ]
        self.menu_manager.open_menu(
            InfoBox(
                str(self.selected_item),
                element_grid,
                width=ITEM_INFO_MENU_WIDTH,
            )
        )

    def equip_selected_item(self) -> None:
        """
        Equip the selected item of the active character if possible
        """
        self.menu_manager.close_active_menu()
        # Try to equip the item
        return_equipped: int = self.selected_player.equip(self.selected_item)
        if return_equipped == -1:
            # Item can't be equipped by this player
            result_message = (
                f_THIS_ITEM_CANNOT_BE_EQUIPPED_PLAYER_DOESNT_SATISFY_THE_REQUIREMENTS(
                    self.selected_player
                )
            )
        else:
            # In this case returned value is > 0, item has been equipped
            result_message = STR_THE_ITEM_HAS_BEEN_EQUIPPED
            if return_equipped == 1:
                result_message += (
                    STR_PREVIOUS_EQUIPPED_ITEM_HAS_BEEN_ADDED_TO_YOUR_INVENTORY
                )

            # Inventory has changed
            self.refresh_inventory()
        element_grid = [
            [
                TextElement(
                    result_message, font=fonts["ITEM_DESC_FONT"], margin=(20, 0, 20, 0)
                )
            ]
        ]
        self.menu_manager.open_menu(
            InfoBox(
                str(self.selected_item),
                element_grid,
                width=ITEM_INFO_MENU_WIDTH,
            )
        )

    def use_selected_item(self) -> None:
        """
        Handle the use of the selected item if possible.
        Remove it if it can't be used anymore.
        """
        # Try to use the object
        used, result_messages = self.selected_player.use_item(self.selected_item)
        # Inventory display is update if object has been used
        if used:
            self.menu_manager.close_active_menu()
            self.refresh_inventory()
        entries = [
            [TextElement(message, font=fonts["ITEM_DESC_FONT"], margin=(10, 0, 10, 0))]
            for message in result_messages
        ]
        self.menu_manager.open_menu(
            InfoBox(
                str(self.selected_item),
                entries,
                width=ITEM_INFO_MENU_WIDTH,
            )
        )

    def refresh_inventory(self) -> None:
        """
        Update inventory interface of active character
        """
        free_spaces: int = self.selected_player.nb_items_max - len(
            self.selected_player.items
        )
        items: list[Optional[Item]] = (
            list(self.selected_player.items) + [None] * free_spaces
        )
        new_inventory_menu = menu_creator_manager.create_inventory_menu(
            self.interact_item, items, self.selected_player.gold
        )
        # Update inventory menu
        self.menu_manager.replace_given_menu(INVENTORY_MENU_ID, new_inventory_menu)

    def open_selected_item_description(self) -> None:
        """
        Handle the opening of the selected item description pop-up
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_item_description_menu(self.selected_item)
        )

    def open_skill_description(self, skill: Skill) -> None:
        """
        Handle the opening of a skill description pop-up

        Keyword arguments:
        skill -- the concerned skill
        """
        self.menu_manager.open_menu(menu_creator_manager.create_skill_info_menu(skill))

    def open_alteration_description(self, alteration: Alteration) -> None:
        """
        Handle the opening of an alteration description pop-up

        Keyword arguments:
        alteration -- the concerned alteration
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_alteration_info_menu(alteration)
        )

    def begin_turn(self) -> None:
        """
        Begin next camp's turn
        """
        entities = []
        if self.side_turn is EntityTurn.PLAYER:
            self.new_turn()
            entities = self.players
        elif self.side_turn is EntityTurn.ALLIES:
            entities = self.entities.allies
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities.foes

        for entity in entities:
            entity.new_turn()

    def new_turn(self) -> None:
        """
        Begin of a new turn
        """
        self.turn += 1
        self.animation = Animation(
            [Frame(constant_sprites["new_turn"], constant_sprites["new_turn_pos"])],
            60,
        )

    def left_click(self, position: Position) -> None:
        """
        Handle the triggering of a left-click event.

        Keyword arguments:
        position -- the position of the mouse
        """
        if self.menu_manager.active_menu:
            if (
                not self.menu_manager.active_menu.is_position_inside(position)
                and self.menu_manager.active_menu.identifier != CHARACTER_ACTION_MENU_ID
            ):
                self.menu_manager.close_active_menu()
            # TODO: check if the raw value could be replaced by a meaningful constant
            self.menu_manager.click(1, position)
            return

        # Player can only react to active menu if it is not his turn
        if self.side_turn is not EntityTurn.PLAYER:
            return

        position_inside_level = self._compute_relative_position(position)
        if self.selected_player is not None:
            if self.game_phase is not LevelStatus.INITIALIZATION:
                if self.possible_moves:
                    # Player is waiting to move
                    for move in self.possible_moves:
                        if pygame.Rect(move, (TILE_SIZE, TILE_SIZE)).collidepoint(
                            position_inside_level
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
                            position_inside_level
                        ):
                            entity = self.get_entity_on_tile(attack)
                            self.duel(
                                self.selected_player,
                                entity,
                                self.entities.foes,
                                self.selected_player.attack_kind,
                            )
                            # Turn is finished
                            self.end_active_character_turn(clear_menus=False)
                            return
                elif self.possible_interactions:
                    # Player is waiting to interact
                    for interact in self.possible_interactions:
                        if pygame.Rect(interact, (TILE_SIZE, TILE_SIZE)).collidepoint(
                            position_inside_level
                        ):
                            entity = self.get_entity_on_tile(interact)
                            self.interact(self.selected_player, entity, interact)
                            return
            else:
                # Initialization phase : player try to change the place of the selected character
                for tile in self.player_possible_placements:
                    if pygame.Rect(tile, (TILE_SIZE, TILE_SIZE)).collidepoint(
                        position_inside_level
                    ):
                        # Test if a character is on the tile, in this case, characters are swapped
                        entity = self.get_entity_on_tile(tile)
                        if entity:
                            entity.set_initial_pos(self.selected_player.position)

                        self.selected_player.set_initial_pos(tile)
                        return
            return
        for player in self.players:
            if player.is_on_position(position_inside_level):
                if player.turn_is_finished():
                    self.menu_manager.open_menu(
                        menu_creator_manager.create_status_menu(
                            {
                                "info_alteration": self.open_alteration_description,
                                "info_skill": self.open_skill_description,
                            },
                            player,
                        )
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
        for entity in self.entities.foes + self.entities.allies:
            if entity.is_on_position(position_inside_level):
                self.menu_manager.open_menu(
                    menu_creator_manager.create_status_entity_menu(
                        {
                            "info_alteration": self.open_alteration_description,
                            "info_skill": self.open_skill_description,
                        },
                        entity,
                    )
                )
                return

        is_initialization = self.game_phase is LevelStatus.INITIALIZATION
        self.menu_manager.open_menu(
            menu_creator_manager.create_main_menu(
                {
                    "save": self.open_save_menu,
                    "suspend": self.exit_game,
                    "start": self.start_game,
                    "diary": lambda: self.menu_manager.open_menu(
                        menu_creator_manager.create_diary_menu(self.diary_entries_text_element_set),
                    ),
                    "end_turn": self.end_turn,
                },
                is_initialization,
                position,
            )
        )

    def right_click(self) -> None:
        """
        Handle the triggering of a right-click event.
        """
        if self.selected_player:
            if self.possible_moves:
                # Player was waiting to move
                self.selected_player.selected = False
                self.selected_player = None
                self.possible_moves = {}
            elif self.menu_manager.active_menu is not None:
                # Test if player is on character's main menu, in this case,
                # current move should be cancelled if possible
                if self.menu_manager.active_menu.identifier == CHARACTER_ACTION_MENU_ID:
                    if self.selected_player.cancel_move():
                        if self.traded_items:
                            # Return traded items
                            for item in self.traded_items:
                                if item[1] == self.selected_player:
                                    item[2].remove_item(item[0])
                                    self.selected_player.set_item(item[0])
                                else:
                                    self.selected_player.remove_item(item[0])
                                    item[1].set_item(item[0])
                            self.traded_items.clear()
                        if self.traded_gold:
                            # Return traded gold
                            for gold in self.traded_gold:
                                if gold[1] == self.selected_player:
                                    self.selected_player.gold += gold[0]
                                    gold[2].gold -= gold[0]
                                else:
                                    self.selected_player.gold -= gold[0]
                                    gold[2].gold += gold[0]
                            self.traded_gold.clear()
                        self.selected_player.selected = False
                        self.selected_player = None
                        self.possible_moves = {}
                        self.menu_manager.clear_menus()
                    return
                self.menu_manager.close_active_menu()
            # Want to cancel an interaction (not already performed)
            elif self.possible_interactions or self.possible_attacks:
                self.selected_player.cancel_interaction()
                self.possible_interactions = []
                self.possible_attacks = []
                self.menu_manager.close_active_menu()
            return
        if self.menu_manager.active_menu is not None:
            self.menu_manager.close_active_menu()
        if self.watched_entity:
            self.watched_entity = None
            self.possible_moves = {}
            self.possible_attacks = []

    def click(self, button: int, position: Position) -> QuitActionKind:
        """
        Handle the triggering of a click event.

        Keyword arguments:
        button -- an integer value representing which mouse button has been pressed
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        # No event if there is an animation or if it is not player turn
        if self.animation:
            return QuitActionKind.CONTINUE

        if button == 1:
            self.left_click(position)
        elif button == 3:
            self.right_click()

        if self.game_phase == LevelStatus.VERY_BEGINNING:
            # Update game phase if dialogs at the very beginning are all closed
            if not self.menu_manager.active_menu:
                self.game_phase = LevelStatus.INITIALIZATION

        return QuitActionKind.CONTINUE

    def button_down(self, button: int, position: Position) -> None:
        """
        Handle the triggering of a mouse button down event.

        Keyword arguments:
        button -- an integer value representing which mouse button is down
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
        """
        if button == 3:
            if (
                not self.menu_manager.active_menu
                and not self.selected_player
                and self.side_turn is EntityTurn.PLAYER
            ):
                position_inside_level = self._compute_relative_position(position)
                for collection in self.entities.values():
                    for entity in collection:
                        if isinstance(
                            entity, Movable
                        ) and entity.get_rect().collidepoint(position_inside_level):
                            self.watched_entity = entity
                            self.possible_moves = self.get_possible_moves(
                                entity.position, entity.max_moves
                            )
                            reach: Sequence[int] = self.watched_entity.reach
                            self.possible_attacks = {}
                            if entity.can_attack():
                                self.possible_attacks = self.get_possible_attacks(
                                    self.possible_moves,
                                    reach,
                                    isinstance(entity, Character),
                                )
                            return

    def key_down(self, keyname):
        """
        Handle the triggering of a key down event.

        Keyword arguments:
        keyname -- an integer value representing which key button is down
        """
        if keyname == pygame.K_ESCAPE:
            if (
                self.menu_manager.active_menu is not None
                and self.menu_manager.active_menu.identifier != CHARACTER_ACTION_MENU_ID
            ):
                self.menu_manager.close_active_menu()

    def motion(self, position: Position) -> None:
        """
        Handle the triggering of a motion event.

        Keyword arguments:
        position -- the position of the mouse
        """
        self.menu_manager.motion(position)

        if not self.menu_manager.active_menu:
            position_inside_level = self._compute_relative_position(position)
            self.hovered_entity = None
            for collection in self.entities.values():
                for entity in collection:
                    if entity.get_rect().collidepoint(position_inside_level):
                        self.hovered_entity = entity
                        return

    def _compute_active_screen_part(self) -> pygame.Surface:
        """
        Compute the part of the screen containing the level itself,
        i.e. the part where the map, the player interface and every entity are.

        Return the computed sub-screen part.
        """
        level_width: int = min(self.screen.get_width(), WIN_WIDTH)
        level_height: int = min(self.screen.get_height(), WIN_HEIGHT)
        return self.screen.subsurface(
            pygame.Rect(
                self.screen.get_width() // 2 - level_width // 2,
                self.screen.get_height() // 2 - level_height // 2,
                level_width,
                level_height,
            )
        )

    def _compute_relative_position(self, position: Position) -> Position:
        """
        Compute and return a position relative to the left top corner of the ongoing level screen
        Keyword arguments:
        position -- the absolute position to be converted
        """
        return position - Position(
            self.screen.get_width() // 2 - self.active_screen_part.get_width() // 2,
            self.screen.get_height() // 2 - self.active_screen_part.get_height() // 2,
        )
