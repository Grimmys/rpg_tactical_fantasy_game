"""Tileset loader and cache for the level editor.

Parses .tsx tilesets, validates basic metadata, slices tile images, and caches
per-tile surfaces and properties for fast palette access.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pygame


@dataclass
class TilesetInfo:
    name: str
    path: Path
    image_path: Optional[Path]
    tile_width: int
    tile_height: int
    margin: int
    spacing: int
    columns: int
    tile_count: int


@dataclass
class TileEntry:
    tileset_name: str
    local_id: int
    surface: pygame.Surface
    properties: Dict[str, str]
    is_animated: bool = False


@dataclass
class TilesetData:
    info: TilesetInfo
    tiles: List[TileEntry]


class TilesetLoadError(Exception):
    pass


def _parse_properties(node: ET.Element) -> Dict[str, str]:
    props: Dict[str, str] = {}
    props_node = node.find("properties")
    if props_node is None:
        return props
    for prop in props_node.findall("property"):
        name = prop.attrib.get("name")
        value = prop.attrib.get("value", "")
        if name:
            props[name] = value
    return props


def _load_tileset_xml(tsx_path: Path) -> ET.Element:
    try:
        tree = ET.parse(tsx_path)
    except ET.ParseError as exc:
        raise TilesetLoadError(f"Invalid TSX XML: {tsx_path}") from exc
    return tree.getroot()


def _slice_tiles(
    tileset_info: TilesetInfo,
    image: pygame.Surface,
    tile_props: Dict[int, Dict[str, str]],
    animations: Dict[int, bool],
) -> List[TileEntry]:
    tiles: List[TileEntry] = []
    tw, th = tileset_info.tile_width, tileset_info.tile_height
    margin, spacing = tileset_info.margin, tileset_info.spacing
    cols = max(1, tileset_info.columns)

    for local_id in range(tileset_info.tile_count):
        col = local_id % cols
        row = local_id // cols
        x = margin + col * (tw + spacing)
        y = margin + row * (th + spacing)
        surface = pygame.Surface((tw, th), pygame.SRCALPHA)
        surface.blit(image, (0, 0), (x, y, tw, th))
        entry = TileEntry(
            tileset_name=tileset_info.name,
            local_id=local_id,
            surface=surface,
            properties=tile_props.get(local_id, {}),
            is_animated=animations.get(local_id, False),
        )
        tiles.append(entry)
    return tiles


def _load_collection_tiles(
    root: ET.Element,
    tsx_path: Path,
    tile_width: int,
    tile_height: int,
    tile_props: Dict[int, Dict[str, str]],
    animations: Dict[int, bool],
) -> List[TileEntry]:
    tiles: List[TileEntry] = []
    for tile_node in root.findall("tile"):
        tid = int(tile_node.attrib.get("id", -1))
        image_node = tile_node.find("image")
        if tid < 0 or image_node is None:
            continue
        source = image_node.attrib.get("source")
        if not source:
            continue
        image_path = (tsx_path.parent / source).resolve()
        if not image_path.exists():
            raise TilesetLoadError(f"Tile image not found: {image_path}")
        try:
            image_surface = pygame.image.load(str(image_path)).convert_alpha()
        except pygame.error as exc:
            raise TilesetLoadError(f"Failed to load tile image: {image_path}") from exc

        surface = pygame.transform.smoothscale(image_surface, (tile_width, tile_height))
        tiles.append(
            TileEntry(
                tileset_name=root.attrib.get("name", tsx_path.stem),
                local_id=tid,
                surface=surface,
                properties=tile_props.get(tid, {}),
                is_animated=animations.get(tid, False),
            )
        )
    return sorted(tiles, key=lambda t: t.local_id)


def load_tileset(tsx_path: Path, base_dir: Optional[Path] = None) -> TilesetData:
    tsx_path = tsx_path.resolve()
    base_dir = base_dir or tsx_path.parent
    root = _load_tileset_xml(tsx_path)

    name = root.attrib.get("name", tsx_path.stem)
    tile_width = int(root.attrib["tilewidth"])
    tile_height = int(root.attrib["tileheight"])
    tile_count = int(root.attrib.get("tilecount", 0))
    columns = int(root.attrib.get("columns", 1))
    margin = int(root.attrib.get("margin", 0))
    spacing = int(root.attrib.get("spacing", 0))

    tile_props: Dict[int, Dict[str, str]] = {}
    animations: Dict[int, bool] = {}
    for tile_node in root.findall("tile"):
        tid = int(tile_node.attrib.get("id", -1))
        if tid < 0:
            continue
        props = _parse_properties(tile_node)
        tile_type = tile_node.attrib.get("type")
        if tile_type:
            props.setdefault("type", tile_type)
        tile_props[tid] = props
        if tile_node.find("animation") is not None:
            animations[tid] = True

    image_node = root.find("image")
    if image_node is not None:
        image_source = image_node.attrib.get("source")
        if not image_source:
            raise TilesetLoadError(f"Tileset image source missing: {tsx_path}")
        image_path = (tsx_path.parent / image_source).resolve()

        if not image_path.exists():
            raise TilesetLoadError(f"Tileset image not found: {image_path}")

        try:
            image_surface = pygame.image.load(str(image_path)).convert_alpha()
        except pygame.error as exc:
            raise TilesetLoadError(f"Failed to load tileset image: {image_path}") from exc

        if tile_count == 0:
            # Derive tile count from image if not specified
            cols = columns if columns > 0 else max(1, image_surface.get_width() // tile_width)
            rows = max(1, image_surface.get_height() // tile_height)
            tile_count = cols * rows

        info = TilesetInfo(
            name=name,
            path=tsx_path,
            image_path=image_path,
            tile_width=tile_width,
            tile_height=tile_height,
            margin=margin,
            spacing=spacing,
            columns=columns,
            tile_count=tile_count,
        )

        tiles = _slice_tiles(info, image_surface, tile_props, animations)
        return TilesetData(info=info, tiles=tiles)

    # Collection tileset (tiles reference their own images)
    tiles = _load_collection_tiles(root, tsx_path, tile_width, tile_height, tile_props, animations)
    if not tiles:
        raise TilesetLoadError(f"Tileset missing <image> and no tile images found: {tsx_path}")

    info = TilesetInfo(
        name=name,
        path=tsx_path,
        image_path=None,
        tile_width=tile_width,
        tile_height=tile_height,
        margin=0,
        spacing=0,
        columns=max(1, columns if columns > 0 else len(tiles)),
        tile_count=len(tiles),
    )
    return TilesetData(info=info, tiles=tiles)


def load_tilesets(tsx_paths: List[Path]) -> Dict[str, TilesetData]:
    cache: Dict[str, TilesetData] = {}
    for tsx_path in tsx_paths:
        data = load_tileset(tsx_path)
        cache[data.info.name] = data
    return cache


def discover_tilesets(root: Path) -> List[Path]:
    if not root.exists():
        return []
    return list(root.rglob("*.tsx"))
