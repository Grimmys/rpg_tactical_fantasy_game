"""
Tileset loader and GID utilities for the editor.

Supports TSX tilesets that are either:
- Image-based spritesheets (<image> on <tileset>)
- Per-tile images (<tile><image .../></tile>)

Exposes:
- Tileset: dataclass holding metadata, pre-sliced tile Surfaces, and firstgid
- load_tilesets(tsx_paths): parse TSX files and compute cumulative firstgid
- gid_lookup(tilesets, gid): find (tileset, local_id) for a global id
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import pygame
from lxml import etree


@dataclass
class Tileset:
    name: str
    source: Path  # path to the TSX file
    tilewidth: int
    tileheight: int
    tilecount: int
    columns: int
    firstgid: int = 1
    # Pre-sliced tile images indexed by local tile id
    tiles: List[pygame.Surface] = field(default_factory=list)

    def gid_range(self) -> range:
        return range(self.firstgid, self.firstgid + self.tilecount)

    def get_surface_by_local_id(self, local_id: int) -> Optional[pygame.Surface]:
        if 0 <= local_id < len(self.tiles):
            return self.tiles[local_id]
        return None


def _load_sheet_tiles(image_path: Path, tilewidth: int, tileheight: int, columns: int, tilecount: int) -> List[pygame.Surface]:
    image = pygame.image.load(str(image_path)).convert_alpha()
    tiles: List[pygame.Surface] = []
    if columns <= 0:
        # Derive columns from image width
        columns = max(1, image.get_width() // tilewidth)
    rows = (tilecount + columns - 1) // columns
    for idx in range(tilecount):
        col = idx % columns
        row = idx // columns
        x = col * tilewidth
        y = row * tileheight
        rect = pygame.Rect(x, y, tilewidth, tileheight)
        surf = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
        surf.blit(image, (0, 0), rect)
        tiles.append(surf)
    return tiles


def _load_per_tile_images(tsx_dir: Path, tileset_el: etree._Element, tilewidth: int, tileheight: int) -> Tuple[List[pygame.Surface], int, int]:
    # Determine max tile id to size the array
    max_id = 0
    for tile_el in tileset_el.findall("tile"):
        tid = int(tile_el.get("id", "0"))
        if tid > max_id:
            max_id = tid
    size = max_id + 1
    tiles: List[pygame.Surface] = [pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA) for _ in range(size)]
    for tile_el in tileset_el.findall("tile"):
        tid = int(tile_el.get("id", "0"))
        img_el = tile_el.find("image")
        if img_el is None:
            continue
        src = img_el.get("source")
        if not src:
            continue
        img_path = (tsx_dir / src).resolve()
        image = pygame.image.load(str(img_path)).convert_alpha()
        # If image size differs from tilewidth/height, center blit
        surf = pygame.Surface((tilewidth, tileheight), pygame.SRCALPHA)
        x = max(0, (tilewidth - image.get_width()) // 2)
        y = max(0, (tileheight - image.get_height()) // 2)
        surf.blit(image, (x, y))
        tiles[tid] = surf
    tilecount = size
    columns = max(1, size)  # arbitrary for per-tile; used only for math fallback
    return tiles, tilecount, columns


def load_tileset(tsx_path: Path) -> Tileset:
    tsx_path = tsx_path.resolve()
    tree = etree.parse(str(tsx_path))
    root = tree.getroot()
    if root.tag != "tileset":
        raise ValueError(f"Not a TSX tileset: {tsx_path}")

    name = root.get("name", tsx_path.stem)
    tilewidth = int(root.get("tilewidth", "32"))
    tileheight = int(root.get("tileheight", "32"))
    tilecount = int(root.get("tilecount", "0"))
    columns = int(root.get("columns", "0"))

    image_el = root.find("image")
    if image_el is not None and image_el.get("source"):
        src = image_el.get("source")
        img_path = (tsx_path.parent / src).resolve()
        tiles = _load_sheet_tiles(img_path, tilewidth, tileheight, columns, tilecount)
    else:
        # per-tile images
        tiles, tilecount, columns = _load_per_tile_images(tsx_path.parent, root, tilewidth, tileheight)

    return Tileset(
        name=name,
        source=tsx_path,
        tilewidth=tilewidth,
        tileheight=tileheight,
        tilecount=tilecount,
        columns=columns,
        tiles=tiles,
    )


def load_tilesets(tsx_paths: Sequence[Path]) -> List[Tileset]:
    tilesets: List[Tileset] = []
    firstgid = 1
    for p in tsx_paths:
        ts = load_tileset(p)
        ts.firstgid = firstgid
        tilesets.append(ts)
        firstgid += ts.tilecount
    return tilesets


def gid_lookup(tilesets: Sequence[Tileset], gid: int) -> Tuple[Optional[Tileset], Optional[int]]:
    if gid <= 0:
        return None, None
    for ts in tilesets:
        if gid in ts.gid_range():
            return ts, gid - ts.firstgid
    return None, None
