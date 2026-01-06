"""Tileset indexing and gid helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from ..metadata import apply_metadata, load_metadata
from ..tileset_loader import TileEntry, TilesetData, load_tilesets


def build_tileset_index(tsx_paths: List[Path], explicit_firstgids: Optional[List[int]] = None) -> tuple[
    Dict[str, TilesetData],
    List[tuple[str, TilesetData, int]],
    Dict[str, int],
    List[str],
]:
    cache = load_tilesets(tsx_paths)

    meta_candidates = [
        Path("src/level_editor/tileset_metadata.json"),
        Path("tools/level_editor/tileset_metadata.json"),
    ]
    for meta_path in meta_candidates:
        metadata = load_metadata(meta_path)
        if metadata:
            apply_metadata(cache, metadata)
            break

    index: List[tuple[str, TilesetData, int]] = []
    firstgid_map: Dict[str, int] = {}
    names: List[str] = []
    gid_cursor = 1
    for idx, tsx_path in enumerate(tsx_paths):
        match = next(
            (data for data in cache.values() if data.info.path.resolve() == tsx_path.resolve()),
            None,
        )
        if match is None:
            continue
        name = match.info.name
        if explicit_firstgids and len(explicit_firstgids) == len(tsx_paths):
            fg = explicit_firstgids[idx]
            if fg is None:
                fg = gid_cursor
        else:
            fg = gid_cursor
        index.append((name, match, fg))
        names.append(name)
        firstgid_map[name] = fg
        gid_cursor = max(gid_cursor, fg + match.info.tile_count)

    return cache, index, firstgid_map, names


def tile_for_gid(
    tileset_index: List[tuple[str, TilesetData, int]],
    gid: int,
    tmx_gid_surfaces: Optional[Dict[int, pygame.Surface]] = None,
) -> Optional[TileEntry | pygame.Surface]:
    if tmx_gid_surfaces is not None and gid in tmx_gid_surfaces:
        return tmx_gid_surfaces[gid]
    for name, data, firstgid in tileset_index:
        end = firstgid + data.info.tile_count
        if firstgid <= gid < end:
            local_id = gid - firstgid
            if 0 <= local_id < len(data.tiles):
                return data.tiles[local_id]
    return None


def gid_for_tile(firstgid_map: Dict[str, int], tile: TileEntry) -> int:
    base = firstgid_map.get(tile.tileset_name)
    if base is None:
        return 0
    return base + tile.local_id
