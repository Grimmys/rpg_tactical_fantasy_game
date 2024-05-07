from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

import pygame
import pytmx
from pytmx import TiledObject

from src.constants import TILE_SIZE
from src.game_entities.breakable import Breakable
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.door import Door
from src.game_entities.foe import Foe
from src.game_entities.fountain import Fountain
from src.game_entities.mission import Mission, MissionType
from src.game_entities.objective import Objective
from src.game_entities.obstacle import Obstacle
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.shop import Shop
from src.gui.position import Position
from src.services import load_from_xml_manager as xml_loader
from src.services.global_foes import foes_by_mission, link_foe_to_mission

objective_tile_by_mission: dict[str, list[Objective]] = {}


def _get_object_position(
        tile_object: TiledObject, horizontal_gap: int, vertical_gap: int
) -> Position:
    return Position(
        tile_object.x * 1.5 + horizontal_gap, tile_object.y * 1.5 + vertical_gap
    )


def load_ground(tmx_data: pytmx.TiledMap, size: tuple[int, int]) -> pygame.Surface:
    map_ground = pygame.Surface(size)
    for x, y, gid in tmx_data.get_layer_by_name("ground"):
        tile = tmx_data.get_tile_image_by_gid(gid)
        map_ground.blit(
            pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE)),
            (x * TILE_SIZE, y * TILE_SIZE),
        )
    return map_ground


def load_obstacles(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Obstacle]:
    obstacles = list()
    for x, y, gid in tmx_data.get_layer_by_name("obstacles"):
        tile = tmx_data.get_tile_properties_by_gid(gid)
        if tile and tile["type"] == "void":
            continue
        obstacle_image = pygame.transform.scale(
            tmx_data.get_tile_image_by_gid(gid), (TILE_SIZE, TILE_SIZE)
        )
        position = Position(x * TILE_SIZE + horizontal_gap, y * TILE_SIZE + vertical_gap)
        obstacles.append(Obstacle(position, obstacle_image))
    return obstacles


def _link_objective_to_mission(objective: Objective, mission_id: str) -> None:
    if mission_id not in objective_tile_by_mission:
        objective_tile_by_mission[mission_id] = []
    objective_tile_by_mission[mission_id].append(objective)


def _load_objectives(tmx_data, horizontal_gap, vertical_gap) -> None:
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "objective":
            objective_image = pygame.transform.scale(
                tile_object.image, (TILE_SIZE, TILE_SIZE)
            )
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            mission_id = tile_object.properties["mission"]
            walkable = tile_object.properties["walkable"]
            _link_objective_to_mission(
                Objective(tile_object.name, position, objective_image, walkable),
                mission_id,
            )


def _load_mission(
        tmx_data: pytmx.TiledMap, is_main: bool, mission_id: str, players: Sequence[Player]
) -> Mission:
    nature = MissionType[tmx_data.properties[f"{mission_id}_mission_type"]]
    description = tmx_data.properties[f"{mission_id}_mission_description"]
    objective_tiles: list[Objective] = []
    targets: Optional[Sequence[Foe]] = None
    turns_limit: Optional[int] = (
        tmx_data.properties[f"{mission_id}_mission_turns"]
        if f"{mission_id}_mission_turns" in tmx_data.properties
        else None
    )
    gold_reward = 0
    items_reward = []
    if nature in (MissionType.POSITION, MissionType.TOUCH_POSITION):
        objective_tiles = objective_tile_by_mission.pop(mission_id)
    elif nature is MissionType.KILL_TARGETS:
        targets = foes_by_mission.pop(mission_id)

    if f"{mission_id}_mission_number_players" in tmx_data.properties:
        min_players = tmx_data.properties[f"{mission_id}_mission_number_players"]
    else:
        min_players = len(players)

    if not is_main:
        if f"{mission_id}_mission_gold_reward" in tmx_data.properties:
            gold_reward = tmx_data.properties[f"{mission_id}_mission_gold_reward"]
        items_reward = []  # TODO: parsing of items reward

    return Mission(
        is_main,
        nature,
        objective_tiles,
        description,
        min_players,
        turns_limit,
        gold_reward,
        items_reward,
        targets,
    )


def load_missions(
        tmx_data: pytmx.TiledMap,
        tmx_map_properties_data: pytmx.TiledMap,
        players: Sequence[Player],
        horizontal_gap: int,
        vertical_gap: int,
) -> tuple[Sequence[Mission], Mission]:
    _load_objectives(tmx_data, horizontal_gap, vertical_gap)
    main_mission = _load_mission(tmx_map_properties_data, True, "main", players)
    missions = [main_mission]
    if "secondary_missions" in tmx_map_properties_data.properties:
        secondary_missions = tmx_map_properties_data.properties[
            "secondary_missions"
        ].split(",")
        for mission_id in secondary_missions:
            missions.append(
                _load_mission(tmx_map_properties_data, False, mission_id, players)
            )

    return missions, main_mission


def load_foes(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Foe]:
    foes = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "foe":
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            level = tile_object.properties["level"]
            strategy = (
                tile_object.properties["strategy"]
                if "strategy" in tile_object.properties
                else None
            )
            specific_loot = []
            if "number_items" in tile_object.properties:
                for index in range(tile_object.properties["number_items"]):
                    specific_loot.append(
                        xml_loader.parse_item_file(
                            tile_object.properties[f"loot_item_{index}_name"]
                        )
                    )
            mission_target = (
                tile_object.properties["mission_target"]
                if "mission_target" in tile_object.properties
                else None
            )

            foe = xml_loader.load_foe(
                tile_object.name,
                position,
                level,
                strategy,
                specific_loot,
                mission_target,
            )
            foes.append(foe)

            if mission_target:
                link_foe_to_mission(foe, mission_target)

    return foes


def load_allies(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Character]:
    allies = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "ally":
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            allies.append(xml_loader.load_ally(tile_object.name, position))
    return allies


def load_player_placements(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> Sequence[Position]:
    placements = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "placement":
            placements.append(
                _get_object_position(tile_object, horizontal_gap, vertical_gap)
            )
    return placements


def load_chests(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Chest]:
    chests = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "chest":
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            image = pygame.transform.scale(tile_object.image, (TILE_SIZE, TILE_SIZE))
            content_possibilities = []
            for index in range(tile_object.properties["content_possibilities"]):
                item = xml_loader.parse_item_file(
                    tile_object.properties[f"item_{index}_name"]
                )
                content_possibilities.append(
                    (item, tile_object.properties[f"item_{index}_probability"])
                )

            chests.append(
                Chest(
                    position,
                    tile_object.properties["closed_sprite"],
                    tile_object.properties["opened_sprite"],
                    content_possibilities,
                    image,
                )
            )
    return chests


def load_dialog(directory: str, dialog_file_index: str) -> dict[str, any]:
    dialog = {}
    try:
        with open(f"{directory}dialog_{dialog_file_index}.txt") as dialog_file:
            dialog["title"] = dialog_file.readline().rstrip("\n")
            dialog_file.readline()  # Skip splitting line between title and body
            dialog["talks"] = dialog_file.read().splitlines()
    except UnicodeDecodeError:
        with open(
                f"{directory}dialog_{dialog_file_index}.txt", encoding="utf-8"
        ) as dialog_file:
            dialog["title"] = dialog_file.readline().rstrip("\n")
            dialog_file.readline()  # Skip splitting line between title and body
            dialog["talks"] = dialog_file.read().splitlines()
    return dialog


def load_house_dialog(directory: str, dialog_file_index: str) -> Sequence[str]:
    try:
        with open(f"{directory}house_dialog_{dialog_file_index}.txt") as dialog_file:
            return dialog_file.read().splitlines()
    except UnicodeDecodeError:
        with open(
                f"{directory}house_dialog_{dialog_file_index}.txt", encoding="utf-8"
        ) as dialog_file:
            return dialog_file.read().splitlines()


def load_events(
        tmx_data: pytmx.TiledMap, directory: str, horizontal_gap: int, vertical_gap: int
) -> dict[str, any]:
    events = {}
    for tile_object in tmx_data.get_layer_by_name("events"):
        events[tile_object.type] = {}
        dialogs: Optional[Sequence[str]] = (
            tile_object.properties["dialogs"].split(",")
            if "dialogs" in tile_object.properties
            else None
        )
        if dialogs:
            events[tile_object.type]["dialogs"] = []
            for dialog in dialogs:
                events[tile_object.type]["dialogs"].append(
                    load_dialog(directory, dialog)
                )
        new_players: Optional[Sequence[str]] = (
            tile_object.properties["new_players"].split(",")
            if "new_players" in tile_object.properties
            else None
        )
        if new_players:
            events[tile_object.type]["new_players"] = []
            players_position: Position = _get_object_position(
                tile_object, horizontal_gap, vertical_gap
            )
            for player in new_players:
                events[tile_object.type]["new_players"].append(
                    {"name": player, "position": players_position}
                )

    return events


def load_buildings(
        tmx_data: pytmx.TiledMap, directory: str, horizontal_gap: int, vertical_gap: int, shop_balance: int
) -> list[Building]:
    buildings = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "building":
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            image = pygame.transform.scale(tile_object.image, (TILE_SIZE, TILE_SIZE))
            interaction: Optional[dict[str, any]] = {}
            dialog_ids: Optional[Sequence[str]] = (
                tile_object.properties["house_dialogs"].split(",")
                if "house_dialogs" in tile_object.properties
                else None
            )
            if dialog_ids:
                for dialog_id in dialog_ids:
                    interaction["talks"] = load_house_dialog(directory, dialog_id)
            if "gold" in tile_object.properties:
                interaction["gold"] = tile_object.properties["gold"]
            if "items" in tile_object.properties:
                interaction["item"] = xml_loader.parse_item_file(
                    tile_object.properties["items"]
                )

            if not interaction:
                interaction = None

            nature = (
                tile_object.properties["kind"]
                if "kind" in tile_object.properties
                else None
            )
            if not nature:
                buildings.append(
                    Building(
                        tile_object.name,
                        position,
                        tile_object.properties["sprite_link"],
                        interaction,
                        image,
                    )
                )
                continue

            if nature == "shop":
                stock = []
                for item_id in range(tile_object.properties["number_items"]):
                    item_entry = {
                        "item": xml_loader.parse_item_file(
                            tile_object.properties[f"item_{item_id}_name"]
                        ),
                        "quantity": tile_object.properties[f"item_{item_id}_quantity"],
                    }
                    stock.append(item_entry)
                buildings.append(
                    Shop(
                        tile_object.name,
                        position,
                        tile_object.properties["sprite_link"],
                        shop_balance,
                        stock,
                        interaction,
                        image,
                    )
                )
            else:
                print("Error: building type isn't recognized: ", nature)
                raise SystemError

    return buildings


def load_breakables(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Breakable]:
    # TODO: implementation
    return []


def load_portals(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Portal]:
    # TODO: implementation
    return []


def load_doors(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Door]:
    doors = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "door":
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            image = pygame.transform.scale(tile_object.image, (TILE_SIZE, TILE_SIZE))
            doors.append(
                Door(position, tile_object.properties["sprite_link"], sprite=image)
            )
    return doors


def load_fountains(
        tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int
) -> list[Fountain]:
    fountains = []
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "fountain":
            position = _get_object_position(tile_object, horizontal_gap, vertical_gap)
            fountains.append(xml_loader.load_fountain(tile_object.name, position))
    return fountains
