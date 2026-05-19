"""Shared TMX parsing utilities.

This module parses a TMX file with pytmx and returns structured data
without applying game/editor-specific semantics. Rendering scale and
entity wiring remain the responsibility of callers.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

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
    id: int
    name: str
    width: int
    height: int
    data: List[List[int]]
    visible: bool
    opacity: Optional[float] = None


@dataclass
class ParsedObject:
    id: Optional[int]
    name: str
    type: Optional[str]
    gid: Optional[int]
    x: float
    y: float
    width: float
    height: float
    rotation: float
    visible: bool
    properties: Dict[str, Any]
    image: Optional[pygame.Surface]


@dataclass
class ParsedObjectLayer:
    id: int
    name: str
    visible: bool
    opacity: Optional[float]
    objects: List[ParsedObject]


@dataclass
class ParsedMap:
    version: Optional[str]
    tiledversion: Optional[str]
    renderorder: Optional[str]
    width: int
    height: int
    tilewidth: int
    tileheight: int
    nextlayerid: Optional[int]
    nextobjectid: Optional[int]
    editorsettings_export: Optional[str]
    tilesets: List[ParsedTileset]
    layers: Dict[str, ParsedLayer]
    object_layers: Dict[str, ParsedObjectLayer]
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
    # Parse XML to capture metadata not exposed by pytmx
    root = ET.parse(path).getroot()
    version = root.attrib.get("version")
    tiledversion = root.attrib.get("tiledversion")
    renderorder = root.attrib.get("renderorder")
    nextlayerid = root.attrib.get("nextlayerid")
    nextobjectid = root.attrib.get("nextobjectid")
    editorsettings_el = root.find("editorsettings/export")
    editorsettings_export = editorsettings_el.attrib.get("format") if editorsettings_el is not None else None

    layer_id_map: Dict[str, int] = {}
    tileset_source_by_firstgid: Dict[int, str] = {}
    for ts_el in root.findall("tileset"):
        fg = ts_el.attrib.get("firstgid")
        src = ts_el.attrib.get("source")
        if fg and src:
            try:
                tileset_source_by_firstgid[int(fg)] = src
            except ValueError:
                continue
    for layer_el in root.findall("layer"):
        lname = layer_el.attrib.get("name", "")
        lid = layer_el.attrib.get("id")
        if lname and lid is not None:
            try:
                layer_id_map[lname] = int(lid)
            except ValueError:
                continue
    for obj_group_el in root.findall("objectgroup"):
        lname = obj_group_el.attrib.get("name", "")
        lid = obj_group_el.attrib.get("id")
        if lname and lid is not None:
            try:
                layer_id_map[lname] = int(lid)
            except ValueError:
                continue

    # load_pygame ensures tile images are loaded as pygame Surfaces for image-backed tilesets
    tmx = load_pygame(str(path))

    tilesets: List[ParsedTileset] = []
    for ts in tmx.tilesets:
        fg_val = int(getattr(ts, "firstgid", 0) or 0)
        tilesets.append(
            ParsedTileset(
                name=getattr(ts, "name", "<unnamed>"),
                firstgid=fg_val,
                tilecount=int(getattr(ts, "tilecount", 0) or 0),
                source=getattr(ts, "source", None) or tileset_source_by_firstgid.get(fg_val),
            )
        )

    layers: Dict[str, ParsedLayer] = {}
    for layer in tmx.layers:
        if hasattr(layer, "data"):
            width = getattr(layer, "width", tmx.width)
            height = getattr(layer, "height", tmx.height)
            lid = layer_id_map.get(getattr(layer, "name", "")) or int(
                getattr(layer, "id", len(layers) + 1) or (len(layers) + 1)
            )
            opacity = getattr(layer, "opacity", None)
            grid: List[List[int]] = [[0 for _ in range(width)] for _ in range(height)]
            for y in range(height):
                for x in range(width):
                    try:
                        grid[y][x] = layer.data[y][x]
                    except Exception:
                        grid[y][x] = 0
            visible = getattr(layer, "visible", True)
            layers[getattr(layer, "name", f"layer_{len(layers)}")] = ParsedLayer(
                id=lid,
                name=getattr(layer, "name", ""),
                width=width,
                height=height,
                data=grid,
                visible=visible,
                opacity=opacity,
            )

    object_layers: Dict[str, List[ParsedObject]] = {}
    for layer in tmx.layers:
        if hasattr(layer, "data"):
            continue  # skip tile layers here
        if not hasattr(layer, "__iter__"):
            continue
        lname = getattr(layer, "name", "") or f"objectlayer_{len(object_layers)}"
        lid = layer_id_map.get(lname) or int(
            getattr(layer, "id", len(object_layers) + len(layers) + 1) or (len(object_layers) + len(layers) + 1)
        )
        visible = getattr(layer, "visible", True)
        opacity = getattr(layer, "opacity", None)
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
                    id=getattr(obj, "id", None),
                    name=getattr(obj, "name", ""),
                    type=getattr(obj, "type", None),
                    gid=getattr(obj, "gid", None),
                    x=float(getattr(obj, "x", 0)),
                    y=float(getattr(obj, "y", 0)),
                    width=float(getattr(obj, "width", 0)),
                    height=float(getattr(obj, "height", 0)),
                    rotation=float(getattr(obj, "rotation", 0)),
                    visible=bool(getattr(obj, "visible", True)),
                    properties=dict(getattr(obj, "properties", {}) or {}),
                    image=surf,
                )
            )
        object_layers[lname] = ParsedObjectLayer(
            id=lid,
            name=lname,
            visible=visible,
            opacity=opacity,
            objects=bucket,
        )

    properties = dict(getattr(tmx, "properties", {}) or {})
    gid_surfaces = _build_gid_surfaces(tmx)

    return ParsedMap(
        version=version,
        tiledversion=tiledversion,
        renderorder=renderorder,
        width=tmx.width,
        height=tmx.height,
        tilewidth=tmx.tilewidth,
        tileheight=tmx.tileheight,
        nextlayerid=int(nextlayerid) if nextlayerid is not None else None,
        nextobjectid=int(nextobjectid) if nextobjectid is not None else None,
        editorsettings_export=editorsettings_export,
        tilesets=tilesets,
        layers=layers,
        object_layers=object_layers,
        properties=properties,
        gid_surfaces=gid_surfaces,
    )
