"""
Defines Level class, the main scene of the game,
corresponding to an ongoing level.
"""

from __future__ import annotations

import os
from enum import IntEnum, auto, Enum
from typing import Sequence, Union, List, Optional, Set, Type

import pygame
from lxml import etree
from pygamepopup.components import InfoBox as new_InfoBox, BoxElement, Button
from pygamepopup.menu_manager import MenuManager

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
from src.game_entities.alteration import Alteration
from src.game_entities.breakable import Breakable
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.destroyable import Destroyable, DamageKind
from src.game_entities.door import Door
from src.game_entities.effect import Effect
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
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
from src.game_entities.skill import Skill
from src.game_entities.weapon import Weapon
from src.gui.animation import Animation
from src.gui.constant_sprites import (
    ATTACKABLE_OPACITY,
    LANDING_OPACITY,
    INTERACTION_OPACITY,
    constant_sprites,
)
from src.gui.entries import Entry, Entries
from src.gui.fonts import fonts
from src.gui.info_box import InfoBox
from src.gui.position import Position
from src.gui.sidebar import Sidebar
from src.gui.tools import blit_alpha
from src.services import load_from_xml_manager as loader, menu_creator_manager
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

    def get_next(self) -> EntityTurn:
        """
        Return the next entity turn, according to the current one
        """
        next_value = (
            self.value + 1 if self.value + 1 < len(EntityTurn.__members__) else 0
        )
        return EntityTurn(next_value)


class Level:
    """
    This class is the main scene of the game, handling all the actions of the players for
    an ongoing level, and also apply the game logic of the level (manage animations, IA turns etc.).

    Keywords:
    directory -- the relative path to the directory where all static data
    concerning the level are stored
    nb_level -- the number identifying the level
    screen -- the pygame Surface related to the level
    status -- the status of the game for this level
    turn -- the value of the current turn (0 by default for new game)
    data -- saved data in XML format in case where the game is loaded from a save
    players -- the list of players on the level

    Attributes:
    directory -- the relative path to the directory where all static data
    concerning the level are stored
    nb_level -- the number identifying the level
    map -- a dictionary containing the properties of the level's map
    obstacles -- the list of obstacles on the level
    events -- a structure containing the data about all the events that could occur
    possible_placements -- the list of available initial positions for players
    screen -- the pygame Surface related to the level
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
    turn_items -- the items that have been trade during the current player turn
    wait_sfx -- the sound that should be started when a player ends his turn
    inventory_sfx -- the sound that should be started when the inventory screen is opening
    armor_sfx -- the sound that should be started when the equipment screen is opening
    talk_sfx -- the sound that should be started when a talk is started between two characters
    gold_sfx -- the sound that should be started when a player obtain gold
    """

    def __init__(
            self,
            directory: str,
            nb_level: int,
            screen: pygame.Surface,
            status: LevelStatus = LevelStatus.INITIALIZATION,
            turn: int = 0,
            data: etree.Element = None,
            players: Sequence[Player] = None,
    ) -> None:
        if players is None:
            players = []

        Shop.interaction_callback = self.interact_item_shop
        Shop.buy_interface_callback = lambda: self.open_menu(self.active_shop.menu)
        Shop.sell_interface_callback = self.open_sell_interface

        # Store directory path if player wants to save and exit game
        self.directory: str = directory
        self.nb_level: int = nb_level

        # Reading of the XML file
        tree: etree.Element = etree.parse(directory + "data.xml").getroot()
        map_image: pygame.Surface = pygame.image.load(self.directory + "map.png")
        self.map: dict[str, any] = {
            "img": map_image,
            "width": map_image.get_width(),
            "height": map_image.get_height(),
            "x": (MAX_MAP_WIDTH - map_image.get_width()) // 2,
            "y": (MAX_MAP_HEIGHT - map_image.get_height()) // 2,
        }

        # Load obstacles
        self.obstacles: List[Position] = loader.load_obstacles(
            tree.find("obstacles"), self.map["x"], self.map["y"]
        )

        # Load events
        self.events: dict[str, any] = loader.load_events(
            tree.find("events"), self.map["x"], self.map["y"]
        )

        # Load available tiles for characters' placement
        self.possible_placements: List[Position] = loader.load_placements(
            tree.findall("placementArea/position"), self.map["x"], self.map["y"]
        )

        self.screen = screen
        self.menu_manager = MenuManager(self.screen)
        self.players: List[Player] = players
        self.entities: dict[str, List[Entity]] = {"players": self.players}
        if data is None:
            # Game is new
            from_save: bool = False
            data_tree: etree.Element = tree
            gap_x, gap_y = (self.map["x"], self.map["y"])
            self.passed_players: List[Player] = []
            if "before_init" in self.events:
                if "dialogs" in self.events["before_init"]:
                    for dialog in self.events["before_init"]["dialogs"]:
                        self.menu_manager.open_menu(
                            create_event_dialog(dialog)
                        )
                if "new_players" in self.events["before_init"]:
                    for player_el in self.events["before_init"]["new_players"]:
                        player = loader.init_player(player_el["name"])
                        player.position = player_el["position"]
                        self.players.append(player)

            # Set initial pos of players arbitrarily
            for player in self.players:
                for tile in self.possible_placements:
                    if self.get_entity_on_tile(tile) is None:
                        player.set_initial_pos(tile)
                        break
                else:
                    print("Error ! Not enough free tiles to set players...")
        else:
            # Game is loaded from a save (data)
            from_save = True
            data_tree = data
            gap_x, gap_y = (0, 0)
            self.players = loader.load_players(data_tree)
            # List for players who are no longer in the level
            self.passed_players = loader.load_escaped_players(data_tree)

        # Load missions
        self.missions, self.main_mission = loader.load_missions(
            tree, self.players, self.map["x"], self.map["y"]
        )

        # Load and store all entities
        self.entities = loader.load_all_entities(data_tree, from_save, gap_x, gap_y)
        self.entities["players"] = self.players

        # Booleans for end game
        # TODO : these booleans are mutually exclusive and so seem a little redundant.
        #  Having only one variable with three different states (victory, defeat or "not finished")
        #  may be better.
        self.victory: bool = False
        self.defeat: bool = False

        # Data structures for possible actions
        self.possible_moves: dict[Position, int] = {}
        self.possible_attacks: List[Position] = []
        self.possible_interactions: List[Position] = []

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
        self.sidebar: Sidebar = Sidebar(
            (MENU_WIDTH, MENU_HEIGHT), (0, MAX_MAP_HEIGHT), self.missions, self.nb_level
        )
        self.wait_for_teleportation_destination: bool = False
        self.diary_entries: List[List[BoxElement]] = []
        self.turn_items: List[List[Union[Item, Player]]] = []

        self.wait_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "waiting.ogg")
        )
        self.inventory_sfx = pygame.mixer.Sound(
            os.path.join("sound_fx", "inventory.ogg")
        )
        self.armor_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "armor.ogg")
        )
        self.talk_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "talking.ogg")
        )
        self.gold_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "trade.ogg")
        )

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
                self.background_menus.pop()[0] if len(self.background_menus) else None
            )
            # Test if active menu is main character's menu, in this case, it should be reloaded
            if self.active_menu and self.active_menu.type is CharacterMenu:
                self.open_player_menu()

    def open_save_menu(self) -> None:
        """
        Replace the current active menu by the a freshly created save game interface
        """
        self.menu_manager.open_menu(menu_creator_manager.create_save_menu(self.save_game))

    def save_game(self, slot_id: int) -> None:
        """
        Save the current state of the game in a file on local disk

        Keyword arguments:
        slot_id -- the id of the slot that should be used to save
        """
        save_state_manager = SaveStateManager(self)
        save_state_manager.save_game(slot_id)
        self.menu_manager.open_menu(new_InfoBox(
            "Game has been saved",
            [[]],
            width=ITEM_MENU_WIDTH
        ))

    def exit_game(self) -> None:
        """
        Handle the end of the level
        """
        # At next update, level will be destroyed
        self.quit_request = True
        if (
                self.game_phase != LevelStatus.ENDED_VICTORY
                and self.game_phase != LevelStatus.ENDED_DEFEAT
        ):
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

    def update_state(self) -> Optional[LevelStatus]:
        """
        Update the state of the game.
        Let the animation progress if there is any.
        Verify if victory or defeat conditions are met.
        Handle next AI action if it's not player's turn.

        Return the game phase if the level should be ended.
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
        if self.menu_manager.active_menu is not None:
            return None

        # Game should be left if it's ended and there is no more animation nor menu
        if (
                self.game_phase is LevelStatus.ENDED_DEFEAT
                or self.game_phase is LevelStatus.ENDED_VICTORY
        ):
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

        for entity in entities:
            if not entity.turn_is_finished():
                if self.side_turn is not EntityTurn.PLAYER:
                    self.entity_action(entity, (self.side_turn is EntityTurn.ALLIES))
                break
        else:
            self.side_turn = self.side_turn.get_next()
            self.begin_turn()

        return None

    def open_player_menu(self) -> None:
        """
        Open the menu displaying all the actions a playable character can do
        """
        interactable_entities = (
                self.entities["chests"]
                + self.entities["portals"]
                + self.entities["doors"]
                + self.entities["fountains"]
                + self.entities["allies"]
                + self.players
        )
        self.menu_manager.open_menu(menu_creator_manager.create_player_menu(
            {
                "inventory": self.open_inventory,
                "equipment": self.open_equipment,
                "status": self.open_status_interface,
                "wait": self.end_character_turn,
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
            self.entities["buildings"],
            interactable_entities,
            self.missions,
            self.entities["foes"],
        ))

    def display(self) -> None:
        """
        Display all the elements of the level.
        Display the ongoing animation if there is any.
        Display also all the menus in the background (that should be visible)
        and lastly the active menu.
        """
        self.screen.blit(self.map["img"], (self.map["x"], self.map["y"]))
        self.sidebar.display(self.screen, self.turn, self.hovered_entity)

        for collection in self.entities.values():
            for ent in collection:
                ent.display(self.screen)
                if isinstance(ent, Destroyable):
                    ent.display_hit_points(self.screen)

        if self.watched_entity:
            self.show_possible_actions(self.watched_entity, self.screen)

        # If the game hasn't yet started
        if self.game_phase is LevelStatus.INITIALIZATION:
            self.show_possible_placements(self.screen)
        else:
            if self.selected_player:
                # If player is waiting to move
                if self.possible_moves:
                    self.show_possible_actions(self.selected_player, self.screen)
                elif self.possible_attacks:
                    self.show_possible_attacks(self.selected_player, self.screen)
                elif self.possible_interactions:
                    self.show_possible_interactions(self.screen)

        if self.animation:
            self.animation.display(self.screen)
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
        for tile in self.possible_moves.keys():
            if movable.position != tile:
                blit_alpha(screen, constant_sprites["landing"], tile, LANDING_OPACITY)

    def show_possible_interactions(self, screen: pygame.Surface) -> None:
        """
        Display all the possible interactions of the active player

        Keyword arguments:
        screen -- the screen on which the possibilities should be drawn
        """
        for tile in self.possible_interactions:
            blit_alpha(screen, constant_sprites["interaction"], tile, INTERACTION_OPACITY)

    def show_possible_placements(self, screen: pygame.Surface) -> None:
        """
        Display all the available tiles for initial placement of the player characters

        Keyword arguments:
        screen -- the screen on which the possibilities should be drawn
        """
        for tile in self.possible_placements:
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
                    self.background_menus.append((create_event_dialog(dialog), False))
            self.active_menu = (
                self.background_menus.pop(0)[0] if self.background_menus else None
            )
            if "new_players" in self.events["after_init"]:
                for player_el in self.events["after_init"]["new_players"]:
                    player = loader.init_player(player_el["name"])
                    player.position = player_el["position"]
                    self.players.append(player)

    def get_next_cases(self, position: Position) -> List[Optional[Entity]]:
        """
        Return the entities that are next to the given tile

        Keyword arguments:
        position -- the position of the tile whose neighbors must be computed
        """
        tiles_content: List[Optional[Entity]] = []
        for x_coordinate in range(-1, 2):
            for y_coordinate in {1 - abs(x_coordinate), -1 + abs(x_coordinate)}:
                tile_x: int = position[0] + (x_coordinate * TILE_SIZE)
                tile_y: int = position[1] + (y_coordinate * TILE_SIZE)
                tile_position: Position = (tile_x, tile_y)
                tile_content: Optional[Entity] = self.get_entity_on_tile(tile_position)
                tiles_content.append(tile_content)
        return tiles_content

    def get_possible_moves(self, position: Position, max_moves: int) -> dict[Position, int]:
        """
        Return all the possible moves with their distance from the starting position

        Keyword arguments:
        position -- the starting position
        max_moves -- the maximum number of tiles that could be traveled
        """
        tiles: dict[Position, int] = {position: 0}
        previously_computed_tiles: dict[Position, int] = tiles
        for i in range(1, max_moves + 1):
            tiles_current_level: dict[Position, int] = {}
            for tile in previously_computed_tiles:
                for x_coordinate in range(-1, 2):
                    for y_coordinate in {1 - abs(x_coordinate), -1 + abs(x_coordinate)}:
                        tile_x: int = tile[0] + (x_coordinate * TILE_SIZE)
                        tile_y: int = tile[1] + (y_coordinate * TILE_SIZE)
                        tile_position: Position = (tile_x, tile_y)
                        if self.is_tile_available(tile_position) and tile_position not in tiles:
                            tiles_current_level[tile_position] = i
            tiles.update(previously_computed_tiles)
            previously_computed_tiles = tiles_current_level
        tiles.update(previously_computed_tiles)
        return tiles

    def get_possible_attacks(self, possible_moves: Sequence[Position],
                             reach: Sequence[int], from_ally_side: bool) -> Set[Position]:
        """
        Return all the tiles that could be targeted for an attack from a specific entity

        Keyword arguments:
        possible_moves -- the sequence of all possible movements
        reach -- the reach of the attacking entity
        from_ally_side -- a boolean indicating whether this is a friendly attack or not
        """
        tiles: List[Position] = []

        entities = list(self.entities["breakables"])
        if from_ally_side:
            entities += self.entities["foes"]
        else:
            entities += self.entities["allies"] + self.players

        for entity in entities:
            for i in reach:
                for x_coordinate in range(-i, i + 1):
                    for y_coordinate in {i - abs(x_coordinate), -i + abs(x_coordinate)}:
                        tile_x: int = entity.position[0] + (x_coordinate * TILE_SIZE)
                        tile_y: int = entity.position[1] + (y_coordinate * TILE_SIZE)
                        tile_position: Position = (tile_x, tile_y)
                        if tile_position in possible_moves:
                            tiles.append(entity.position)

        return set(tiles)

    def is_tile_available(self, tile: Position) -> bool:
        """
        Return whether the given tile can be accessed or not

        Keyword arguments:
        tile -- the position of the tile
        """
        min_case: Position = pygame.Vector2(self.map["x"], self.map["y"])
        max_case: Position = pygame.Vector2(
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

        return self.get_entity_on_tile(tile) is None and tile not in self.obstacles

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

    def determine_path_to(self, destination_tile: Position,
                          distance_for_tile: dict[Position, int]) -> List[Position]:
        """
        Return an ordered list of position that represent the path from one tile to another

        Keyword arguments:
        destination_tile -- the position of the destination
        distance -- the distance between the starting tile and the destination
        """
        path: List[Position] = [destination_tile]
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

    def distance_between_all(self, entity: Entity, all_other_entities: Sequence) -> \
            dict[Entity, int]:
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
            entity: self.map["width"] * self.map["height"] for entity in all_other_entities
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
        actor -- the character opening the chest
        chest -- the chest that is being open
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
        entry_item: Entry = {
            "type": "item_button",
            "item": item,
            "index": -1,
            "disabled": True,
            "callback": lambda button_position, item_reference=item: self.interact_item(
                item_reference, button_position, is_equipped=False
            ),
        }
        entries: Entries = [
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

    def open_door(self, door: Door) -> None:
        """
        Handle the opening of a door.
        Remove it from the level if needed.

        Keyword arguments:
        door -- the door that should be opened
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

    def ally_to_player(self, character: Character) -> None:
        """
        Cast a character entity to a player.
        It is use when an ally or neutral entity suddenly join the player team.

        Keyword argument:
        character -- the character that should be cast
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

    def interact(self, actor: Character, target: Entity, target_position: Position) -> None:
        """
        Handle the interaction of a character with a given entity

        Keyword arguments:
        actor -- the character starting the interaction
        target -- the target of the interaction
        target_position -- the position of the target
        """
        # Since player chose his interaction, possible interactions should be reset
        self.possible_interactions = []

        # Check if target is an empty pos
        if not target:
            if self.wait_for_teleportation_destination:
                self.wait_for_teleportation_destination = False
                actor.position = target_position

                # Turn is finished
                self.background_menus = []
                self.selected_player.end_turn()
                self.selected_player = None
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
                actor.remove_door_key()
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
            new_based_position: Position = target.linked_to.position
            possible_positions_with_distance: dict[Position, int] = \
                self.get_possible_moves(new_based_position, 1)
            # Remove portal pos since player cannot be on the portal
            del possible_positions_with_distance[new_based_position]
            if possible_positions_with_distance:
                self.possible_interactions = possible_positions_with_distance.keys()
                self.wait_for_teleportation_destination = True
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
            kind: Union[Type[Enum], str] = ""
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

    def remove_entity(self, entity: Entity) -> None:
        """
        Remove an entity from the level

        Keyword arguments:
        entity -- the entity that should be removed
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

    def duel(self, attacker: Movable, target: Destroyable, attacker_allies: Sequence[Destroyable],
             target_allies: Sequence[Destroyable], kind: DamageKind) -> None:
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
        for i in range(nb_attacks):
            experience: int = 0

            if isinstance(target, Character) and target.parried():
                # Target parried attack
                message: str = (
                        str(attacker)
                        + " attacked "
                        + str(target)
                        + "... But "
                        + str(target)
                        + " parried !"
                )
                self.diary_entries.append(
                    [{"type": "text", "text": message, "font": fonts["ITEM_DESC_FONT"]}]
                )
                continue

            damage: int = attacker.attack(target)
            real_damage: int = target.hit_points - target.attacked(
                attacker, damage, kind, target_allies
            )
            self.diary_entries.append(
                [
                    {
                        "type": "text",
                        "text": str(attacker)
                                + " dealt "
                                + str(real_damage)
                                + " damage to "
                                + str(target),
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            )
            # XP gain for dealt damage
            experience += real_damage // 2
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
                    loot: Sequence[Item] = target.roll_for_loot()
                    for item in loot:
                        self.diary_entries.append(
                            [
                                {
                                    "type": "text",
                                    "text": f"{target} dropped {item}",
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
                    weapon: Weapon = attacker.get_weapon()
                    if weapon:
                        applied_effects: Sequence[Effect] = weapon.apply_effects(attacker, target)
                        for effect in applied_effects:
                            _, message = effect.apply_on_ent(target)
                            self.diary_entries.append(
                                [
                                    {
                                        "type": "text",
                                        "text": message,
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

    def entity_action(self, entity: Movable, is_ally: bool) -> None:
        """
        Compute the action of a non-playable entity (AI)

        Keyword arguments:
        entity -- the entity for which the action should be computed
        is_ally -- a boolean indicating if the entity is an ally or not
        """
        possible_moves: dict[Position, int] = self.get_possible_moves(entity.position,
                                                                      entity.max_moves)
        targets: Sequence[Movable] = (
            self.entities["foes"] if is_ally else self.players + self.entities["allies"]
        )
        allies: Sequence[Movable] = (
            self.players + self.entities["allies"] if is_ally else self.entities["foes"]
        )
        tile: Position = entity.act(possible_moves, self.distance_between_all(entity, targets))

        if tile:
            if tile in possible_moves:
                # Entity choose to move to case
                self.hovered_entity = entity
                path = self.determine_path_to(tile, possible_moves)
                entity.set_move(path)
            else:
                # Entity choose to attack the entity on the tile
                entity_attacked = self.get_entity_on_tile(tile)
                self.duel(entity, entity_attacked, allies, targets, entity.attack_kind)
                entity.end_turn()

    def interact_item_shop(self, item: Item, button_position: Position) -> None:
        """
        Handle the interaction with an item in a shop

        Keyword arguments:
        item -- the concerned item
        button_position -- the position of the button representing the item on interface
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
        Handle the interaction with an item from player inventory in a shop

        Keyword arguments:
        item -- the concerned item
        button_position -- the position of the button representing the item on interface
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

    def open_sell_interface(self) -> None:
        """
        Handle the opening of the player inventory in a shop
        """
        free_spaces: int = self.selected_player.nb_items_max - len(
            self.selected_player.items
        )
        items: List[Optional[Item]] = list(self.selected_player.items) + [None] * free_spaces
        self.open_menu(
            menu_creator_manager.create_inventory_menu(
                self.interact_sell_item,
                items,
                self.selected_player.gold,
                is_to_sell=True,
            )
        )

    def end_turn(self) -> None:
        """
        End the current turn
        """
        self.menu_manager.close_menu()
        for player in self.players:
            player.end_turn()
        self.side_turn = self.side_turn.get_next()
        self.begin_turn()

    def select_visit(self):
        """
        Let the player select the building to visit for the active character
        """
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
                        # Check if player is able to complete this objective
                        if mission.update_state(self.selected_player):
                            self.players.remove(self.selected_player)
                            self.passed_players.append(self.selected_player)
                            if mission.main and mission.ended:
                                self.victory = True
                            # Turn is finished
                            self.menu_manager.close_menu()
                            self.menu_manager.background_menus.clear()
                            self.selected_player.end_turn()
                            self.selected_player = None
                            break

    def select_talk(self) -> None:
        """
        Let the player select the character to talk with for the active character
        """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
        self.selected_player.choose_target()
        self.possible_interactions = []
        for entity in self.get_next_cases(self.selected_player.position):
            if isinstance(entity, Character) and not isinstance(entity, Player):
                self.possible_interactions.append(entity.position)

    def select_pick_lock(self) -> None:
        """
        Let the player select the chest or door to pick lock for the active character
        """
        self.selected_player.current_action = CharacterMenu.PICK_LOCK
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
        self.selected_player.choose_target()
        self.possible_interactions = []
        for entity in self.get_next_cases(self.selected_player.position):
            if (isinstance(entity, Chest) and not entity.opened) or isinstance(entity, Door):
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
                "You have no key to open a door",
                "imgs/interface/PopUpMenu.png",
                [],
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(False),
            )
            self.open_menu(info_box, is_visible_on_background=True)
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
                "You have no key to open a chest",
                "imgs/interface/PopUpMenu.png",
                [],
                width=ITEM_MENU_WIDTH,
                close_button=lambda: self.close_active_menu(False),
            )
            self.open_menu(info_box, is_visible_on_background=True)
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
        """
        Let the player select the foe to attack for the active character
        """
        self.background_menus.append((self.active_menu, False))
        self.selected_player.choose_target()
        self.possible_attacks = self.get_possible_attacks(
            [self.selected_player.position], self.selected_player.reach, True
        )
        self.possible_interactions = []
        self.active_menu = None

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

    def end_character_turn(self) -> None:
        """
        End the turn of the active character
        """
        pygame.mixer.Sound.play(self.wait_sfx)
        self.selected_item = None
        self.selected_player.end_turn()
        self.selected_player = None
        self.possible_moves = []
        self.possible_attacks = []
        self.possible_interactions = []

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
        items: List[Optional[Item]] = list(self.selected_player.items) + [None] * free_spaces
        self.open_menu(
            menu_creator_manager.create_inventory_menu(
                self.interact_item, items, self.selected_player.gold
            ),
            is_visible_on_background=True,
            sound=self.inventory_sfx,
        )

    def select_interaction_with(self, entity_kind: Type[Entity]) -> None:
        """
        Let the player select the entity to interact with for the active character

        Keyword arguments:
        entity_kind -- the nature of entity for which the player should select an interaction
        """
        self.background_menus.append((self.active_menu, False))
        self.active_menu = None
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
            button_position: Position,
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
            is_visible_on_background=True,
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
        if not added:
            entries = [
                [
                    {
                        "type": "text",
                        "text": f"Item can't be traded : not enough place in {receiver}'s "
                                f"inventory .",
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

            entries = [
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
            entries,
            width=ITEM_DELETE_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
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
        self.active_menu = menu_creator_manager.create_trade_menu(
            {"interact_item": self.interact_trade_item, "send_gold": self.send_gold},
            first_player,
            second_player,
        )

    def throw_selected_item(self) -> None:
        """
        Remove the selected item from player inventory/equipment
        """
        # Remove item from inventory/equipment according to the index
        if isinstance(self.selected_item, Equipment) \
                and self.selected_player.has_equipment(self.selected_item):
            self.selected_player.remove_equipment(self.selected_item)
            equipments = list(self.selected_player.equipments)
            new_items_menu = menu_creator_manager.create_equipment_menu(
                self.interact_item, equipments
            )
        else:
            free_spaces: int = self.selected_player.nb_items_max - len(
                self.selected_player.items
            )
            items: List[Optional[Item]] = list(self.selected_player.items) + [None] * free_spaces
            new_items_menu = menu_creator_manager.create_inventory_menu(
                self.interact_item, items, self.selected_player.gold
            )
        # Update the inventory menu (i.e. first menu backward)
        self.background_menus[len(self.background_menus) - 1] = (new_items_menu, True)
        entries = [
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
            entries,
            width=ITEM_DELETE_MENU_WIDTH,
            close_button=lambda: self.close_active_menu(False),
        )

    def try_sell_selected_item(self) -> None:
        """
        Handle the sale of the selected item if possible
        """
        sold, result_message = self.active_shop.sell(
            self.selected_player, self.selected_item
        )
        if sold:
            # Remove ref to item
            self.selected_item = None

            # Update shop screen content (item has been removed from inventory)
            # TODO: very recurrent task that maybe should be extract to a method
            free_spaces: int = self.selected_player.nb_items_max - len(
                self.selected_player.items
            )
            items: List[Optional[Item]] = list(self.selected_player.items) + [None] * free_spaces
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
                    "text": result_message,
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

    def try_buy_selected_item(self) -> None:
        """
        Handle the purchase of the selected item if possible
        """
        result_message = self.active_shop.buy(self.selected_player, self.selected_item)
        entries = [
            [
                {
                    "type": "text",
                    "text": result_message,
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

    def unequip_selected_item(self) -> None:
        """
        Unequip the selected item of the active character if possible
        """
        self.background_menus.append((self.active_menu, False))
        unequipped = self.selected_player.unequip(self.selected_item)
        result_message = (
            "The item can't be unequipped : Not enough space in your inventory."
        )
        if unequipped:
            result_message = "The item has been unequipped"

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
                    "text": result_message,
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

    def equip_selected_item(self) -> None:
        """
        Equip the selected item of the active character if possible
        """
        # Try to equip the item
        return_equipped: int = self.selected_player.equip(self.selected_item)
        if return_equipped == -1:
            # Item can't be equipped by this player
            result_message = (
                    "This item can't be equipped : "
                    + str(self.selected_player)
                    + " doesn't satisfy the requirements."
            )
        else:
            # In this case returned value is > 0, item has been equipped
            result_message = "The item has been equipped."
            if return_equipped == 1:
                result_message += (
                    " Previous equipped item has been added to your inventory."
                )

            # Inventory has changed
            self.refresh_inventory()
        entries = [
            [
                {
                    "type": "text",
                    "text": result_message,
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

    def use_selected_item(self) -> None:
        """
        Handle the use of the selected item if possible.
        Remove it if it can't be used anymore.
        """
        # Try to use the object
        used, result_messages = self.selected_player.use_item(self.selected_item)
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
            for msg in result_messages
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

    def refresh_inventory(self) -> None:
        """
        Update inventory interface of active character
        """
        free_spaces: int = self.selected_player.nb_items_max - len(
            self.selected_player.items
        )
        items: List[Optional[Item]] = list(self.selected_player.items) + [None] * free_spaces
        new_inventory_menu = menu_creator_manager.create_inventory_menu(
            self.interact_item, items, self.selected_player.gold
        )
        # Cancel item menu
        self.active_menu = None
        # Update the inventory menu (i.e. first menu backward)
        self.background_menus[len(self.background_menus) - 1] = (
            new_inventory_menu,
            True
        )

    def open_selected_item_description(self) -> None:
        """
        Handle the opening of the selected item description pop-up
        """
        self.open_menu(
            menu_creator_manager.create_item_description_menu(self.selected_item)
        )

    def open_skill_description(self, skill: Skill) -> None:
        """
        Handle the opening of a skill description pop-up

        Keyword arguments:
        skill -- the concerned skill
        """
        self.menu_manager.open_menu(
            menu_creator_manager.create_skill_info_menu(skill)
        )

    def open_alteration_description(self, alteration: Alteration) -> None:
        """
        Handle the opening of an alteration description pop-up

        Keyword arguments:
        alteration -- the concerned alteration
        """
        self.open_menu(
            menu_creator_manager.create_alteration_info_menu(alteration),
            is_visible_on_background=True,
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
            entities = self.entities["allies"]
        elif self.side_turn is EntityTurn.FOES:
            entities = self.entities["foes"]

        for entity in entities:
            entity.new_turn()

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

    def left_click(self, position: Position) -> None:
        """
        Handle the triggering of a left-click event.

        Keyword arguments:
        position -- the position of the mouse
        """
        if self.menu_manager.active_menu:
            self.menu_manager.click(1, position)
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
                            entity = self.get_entity_on_tile(attack)
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
                            entity = self.get_entity_on_tile(interact)
                            self.interact(self.selected_player, entity, interact)
                            return
            else:
                # Initialization phase : player try to change the place of the selected character
                for tile in self.possible_placements:
                    if pygame.Rect(tile, (TILE_SIZE, TILE_SIZE)).collidepoint(position):
                        # Test if a character is on the tile, in this case, characters are swapped
                        entity = self.get_entity_on_tile(tile)
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
                self.menu_manager.open_menu(menu_creator_manager.create_status_entity_menu(
                    self.open_alteration_description, entity
                ))
                return

        is_initialization = self.game_phase is LevelStatus.INITIALIZATION
        self.menu_manager.open_menu(menu_creator_manager.create_main_menu(
            {
                "save": self.open_save_menu,
                "suspend": self.exit_game,
                "start": self.start_game,
                "diary": lambda: self.menu_manager.open_menu(
                    menu_creator_manager.create_diary_menu(self.diary_entries),
                ),
                "end_turn": self.end_turn,
            },
            is_initialization,
            position,
        ))

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
                if self.menu_manager.active_menu.type == "character_menu":
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

    def click(self, button: int, position: Position) -> None:
        """
        Handle the triggering of a click event.

        Keyword arguments:
        button -- an integer value representing which mouse button has been pressed
        (1 for left button, 2 for middle button, 3 for right button)
        position -- the position of the mouse
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
                for collection in self.entities.values():
                    for entity in collection:
                        if isinstance(
                                entity, Movable
                        ) and entity.get_rect().collidepoint(position):
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

    def motion(self, position: Position) -> None:
        """
        Handle the triggering of a motion event.

        Keyword arguments:
        position -- the position of the mouse
        """
        self.menu_manager.motion(position)

        if not self.menu_manager.active_menu:
            self.hovered_entity = None
            for collection in self.entities.values():
                for entity in collection:
                    if entity.get_rect().collidepoint(position):
                        self.hovered_entity = entity
                        return
