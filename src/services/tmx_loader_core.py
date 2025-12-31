"""Shared TMX parsing utilities.

This module parses a TMX file with pytmx and returns structured data
without applying game/editor-specific semantics. Rendering scale and
entity wiring remain the responsibility of callers.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pygame
import pytmx
from pytmx.util_pygame import load_pygame


@dataclass
class ParsedTileset:
    name: str
    firstgid: int
    tilecount: int
    source: Optional[str]


@dataclass
class ParsedLayer:
    name: str
    width: int
    height: int
    data: List[List[int]]
    visible: bool


@dataclass
class ParsedObject:
    name: str
    type: Optional[str]
    gid: Optional[int]
    x: float
    y: float
    width: float
    height: float
    properties: Dict[str, Any]
    image: Optional[pygame.Surface]


@dataclass
class ParsedMap:
    width: int
    height: int
    tilewidth: int
    tileheight: int
    tilesets: List[ParsedTileset]
    layers: Dict[str, ParsedLayer]
    object_layers: Dict[str, List[ParsedObject]]
    properties: Dict[str, Any]
    gid_surfaces: Dict[int, pygame.Surface]


def _build_gid_surfaces(tmx: pytmx.TiledMap) -> Dict[int, pygame.Surface]:
    """Build a gid->surface map directly from the TMX (no TSX parsing).

    Surfaces are copied to avoid shared references and kept at TMX native
    tile dimensions; callers decide how to scale for rendering.
    """
    surfaces: Dict[int, pygame.Surface] = {}
    print(f"[tmx] tilesets: {len(tmx.tilesets)}")
    for ts in tmx.tilesets:
        firstgid = getattr(ts, "firstgid", 0) or 0
        tilecount = getattr(ts, "tilecount", 0) or 0
        source = getattr(ts, "source", None)
        print(f"  - name={getattr(ts, 'name', '<unnamed>')} firstgid={firstgid} tilecount={tilecount} source={source}")
        for local_id in range(tilecount):
            gid = firstgid + local_id
            try:
                surf = tmx.get_tile_image_by_gid(gid)
            except IndexError:
                # pytmx can raise if images array is sparse; skip missing gids
                continue
            if surf is None:
                continue
            # pytmx may return (Surface, duration) for animations
            if isinstance(surf, tuple) and surf and hasattr(surf[0], "copy"):
                surf = surf[0]
            if surf is None or not hasattr(surf, "copy"):
                continue
            surfaces[gid] = surf.copy()
    print(f"[tmx] gid surfaces built: {len(surfaces)} entries")
    return surfaces


def parse_tmx(path: Path) -> ParsedMap:
    """Parse a TMX file into a neutral structure for editor/game use.

    Does not apply scaling or gameplay semantics. Accepts TMX as-is,
    including image-backed tilesets; does not synthesize tilesets or gids.
    """
    # load_pygame ensures tile images are loaded as pygame Surfaces for image-backed tilesets
    tmx = load_pygame(str(path))

    tilesets: List[ParsedTileset] = []
    for ts in tmx.tilesets:
        tilesets.append(
            ParsedTileset(
                name=getattr(ts, "name", "<unnamed>"),
                firstgid=int(getattr(ts, "firstgid", 0) or 0),
                tilecount=int(getattr(ts, "tilecount", 0) or 0),
                source=getattr(ts, "source", None),
            )
        )

    layers: Dict[str, ParsedLayer] = {}
    for layer in tmx.layers:
        if hasattr(layer, "data"):
            width = getattr(layer, "width", tmx.width)
            height = getattr(layer, "height", tmx.height)
            grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
            for y in range(height):
                for x in range(width):
                    try:
                        grid[y][x] = layer.data[y][x]
                    except Exception:
                        grid[y][x] = 0
            visible = getattr(layer, "visible", True)
            layers[getattr(layer, "name", f"layer_{len(layers)}")] = ParsedLayer(
                name=getattr(layer, "name", ""),
                width=width,
                height=height,
                data=grid,
                visible=visible,
            )

    object_layers: Dict[str, List[ParsedObject]] = {}
    for layer in tmx.layers:
        if hasattr(layer, "data"):
            continue  # skip tile layers here
        if not hasattr(layer, "__iter__"):
            continue
        lname = getattr(layer, "name", "") or f"objectlayer_{len(object_layers)}"
        bucket: List[ParsedObject] = []
        for obj in layer:
            surf = getattr(obj, "image", None)
            if isinstance(surf, tuple) and surf and hasattr(surf[0], "copy"):
                surf = surf[0]
            if surf is not None and hasattr(surf, "copy"):
                surf = surf.copy()
            else:
                surf = None
            bucket.append(
                ParsedObject(
                    name=getattr(obj, "name", ""),
                    type=getattr(obj, "type", None),
                    gid=getattr(obj, "gid", None),
                    x=float(getattr(obj, "x", 0)),
                    y=float(getattr(obj, "y", 0)),
                    width=float(getattr(obj, "width", 0)),
                    height=float(getattr(obj, "height", 0)),
                    properties=dict(getattr(obj, "properties", {}) or {}),
                    image=surf,
                )
            )
        object_layers[lname] = bucket

    properties = dict(getattr(tmx, "properties", {}) or {})
    gid_surfaces = _build_gid_surfaces(tmx)

    return ParsedMap(
        width=tmx.width,
        height=tmx.height,
        tilewidth=tmx.tilewidth,
        tileheight=tmx.tileheight,
        tilesets=tilesets,
        layers=layers,
        object_layers=object_layers,
        properties=properties,
        gid_surfaces=gid_surfaces,
    )
