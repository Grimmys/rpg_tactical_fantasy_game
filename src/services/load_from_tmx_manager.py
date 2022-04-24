from __future__ import annotations

from typing import Sequence, Optional

import pygame
import pytmx

from src.constants import TILE_SIZE
from src.game_entities.chest import Chest
from src.game_entities.foe import Foe
from src.game_entities.mission import Mission, MissionType
from src.game_entities.objective import Objective
from src.game_entities.obstacle import Obstacle
from src.game_entities.player import Player
from src.gui.position import Position
from src.services import load_from_xml_manager as xml_loader

objective_tile_by_mission: dict[str, list[Objective]] = {}


def load_ground(tmx_data: pytmx.TiledMap, size: tuple[int, int]) -> pygame.Surface:
    map_ground = pygame.Surface(size)
    for x, y, gid in tmx_data.get_layer_by_name("ground"):
        tile = tmx_data.get_tile_image_by_gid(gid)
        map_ground.blit(pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE)),
                        (x * TILE_SIZE, y * TILE_SIZE))
    return map_ground


def load_obstacles(tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int) -> set[Obstacle]:
    obstacles = set()
    for x, y, gid in tmx_data.get_layer_by_name("obstacles"):
        tile = tmx_data.get_tile_properties_by_gid(gid)
        if tile and tile["type"] == "void":
            continue
        obstacle_image = pygame.transform.scale(tmx_data.get_tile_image_by_gid(gid), (TILE_SIZE, TILE_SIZE))
        position = (x * TILE_SIZE + horizontal_gap, y * TILE_SIZE + vertical_gap)
        obstacles.add(Obstacle(position, obstacle_image))
    return obstacles


def _link_objective_to_mission(objective: Objective, mission_id: str) -> None:
    if mission_id not in objective_tile_by_mission:
        objective_tile_by_mission[mission_id] = []
    objective_tile_by_mission[mission_id].append(objective)


def _load_objectives(tmx_data, horizontal_gap, vertical_gap) -> None:
    for tile_object in tmx_data.get_layer_by_name("dynamic_data"):
        if tile_object.type == "objective":
            objective_image = pygame.transform.scale(tile_object.image, (TILE_SIZE, TILE_SIZE))
            position = (tile_object.x * 1.5 + horizontal_gap, tile_object.y * 1.5 + vertical_gap)
            mission_id = tile_object.properties["mission"]
            walkable = tile_object.properties["walkable"]
            _link_objective_to_mission(Objective(position, objective_image, walkable), mission_id)


def _load_mission(tmx_data: pytmx.TiledMap, is_main: bool, mission_id: str, players: Sequence[Player]) -> Mission:
    nature = MissionType[tmx_data.properties[f"{mission_id}_mission_type"]]
    description = tmx_data.properties[f"{mission_id}_mission_description"]
    objective_tiles: list[Objective] = []
    targets: Optional[Sequence[Foe]] = None
    turns_limit: Optional[int] = tmx_data.properties[
        f"{mission_id}_mission_turns"] if f"{mission_id}_mission_turns" in tmx_data.properties else None
    gold_reward = 0
    items_reward = []
    if nature in (MissionType.POSITION, MissionType.TOUCH_POSITION):
        objective_tiles = objective_tile_by_mission[mission_id]

    if f"{mission_id}_mission_number_players" in tmx_data.properties:
        min_players = tmx_data.properties[f"{mission_id}_mission_number_players"]
    else:
        min_players = len(players)

    if not is_main:
        if f"{mission_id}_mission_gold_reward" in tmx_data.properties:
            gold_reward = tmx_data.properties[f"{mission_id}_mission_gold_reward"]
        items_reward = []  # TODO: parsing of items reward

    return Mission(is_main, nature, objective_tiles, description, min_players, turns_limit, gold_reward, items_reward,
                   targets)


def load_missions(tmx_data: pytmx.TiledMap,
                  players: Sequence[Player],
                  horizontal_gap: int, vertical_gap: int) -> tuple[Sequence[Mission], Mission]:
    _load_objectives(tmx_data, horizontal_gap, vertical_gap)
    main_mission = _load_mission(tmx_data, True, "main", players)
    missions = [main_mission]
    if "secondary_missions" in tmx_data.properties:
        secondary_missions = tmx_data.properties["secondary_missions"].split(",")
        for mission_id in secondary_missions:
            missions.append(_load_mission(tmx_data, False, mission_id, players))

    return missions, main_mission


def load_foes(tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int) -> Sequence[Foe]:
    foes = []
    for dynamic_object in tmx_data.get_layer_by_name("dynamic_data"):
        if dynamic_object.type == "foe":
            position = (dynamic_object.x * 1.5 + horizontal_gap, dynamic_object.y * 1.5 + vertical_gap)
            level = dynamic_object.properties["level"]
            strategy = dynamic_object.properties["strategy"] if "strategy" in dynamic_object.properties else None
            foes.append(xml_loader.load_foe(dynamic_object.name, position, level, strategy))
    return foes


def load_player_placements(tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int) -> Sequence[Position]:
    placements = []
    for dynamic_object in tmx_data.get_layer_by_name("dynamic_data"):
        if dynamic_object.type == "placement":
            placements.append((dynamic_object.x * 1.5 + horizontal_gap, dynamic_object.y * 1.5 + vertical_gap))
    return placements


def load_chests(tmx_data: pytmx.TiledMap, horizontal_gap: int, vertical_gap: int) -> Sequence[Chest]:
    chests = []
    for dynamic_object in tmx_data.get_layer_by_name("dynamic_data"):
        if dynamic_object.type == "chest":
            position = (dynamic_object.x * 1.5 + horizontal_gap, dynamic_object.y * 1.5 + vertical_gap)
            image = pygame.transform.scale(dynamic_object.image, (TILE_SIZE, TILE_SIZE))
            content_possibilities = []
            for index in range(dynamic_object.properties["content_possibilities"]):
                item = xml_loader.parse_item_file(dynamic_object.properties[f"item_{index}_name"])
                content_possibilities.append((item,
                                              dynamic_object.properties[f"item_{index}_probability"]))

            chests.append(Chest(position, image, dynamic_object.properties["opened_sprite"],
                                content_possibilities))
    return chests
