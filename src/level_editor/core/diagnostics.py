"""Diagnostic helpers for the level editor."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pygame
import pytmx

from src.services.tmx_loader_core import ParsedMap
from ..map_template import MapTemplate


def log_diagnostics(tmpl: MapTemplate, parsed_map: Optional[ParsedMap]) -> None:
    """Emit a concise diagnostic summary for tilesets, gids, layers, and objects."""
    if parsed_map is not None:
        print("[diag] tilesets:")
        for ts in parsed_map.tilesets:
            print(f"  - name={ts.name} firstgid={ts.firstgid} tilecount={ts.tilecount} source={ts.source}")
        print(f"[diag] gid surfaces: {len(parsed_map.gid_surfaces)}")
        obj_total = 0
        for lname, olayer in parsed_map.object_layers.items():
            count = len(getattr(olayer, "objects", []) or [])
            print(f"[diag] objects {lname}: {count}")
            obj_total += count
        print(f"[diag] objects total: {obj_total}")
    else:
        print("[diag] no parsed TMX available (JSON load)")

    for lname, layer in tmpl.layers.items():
        nz = 0
        lmin, lmax = 0, 0
        for row in layer.data:
            for gid in row:
                if gid:
                    nz += 1
                    lmin = gid if lmin == 0 else min(lmin, gid)
                    lmax = max(lmax, gid)
        print(f"[diag] layer {lname}: nz={nz} min={lmin} max={lmax} visible={layer.visible}")


def build_tmx_gid_surfaces(tmx_path: Path, tmx_obj: Optional[pytmx.TiledMap] = None) -> Dict[int, pygame.Surface]:
    """Build a gid->surface map directly from a TMX using pytmx, skipping TSX parsing."""
    tmx = tmx_obj or pytmx.TiledMap(str(tmx_path))
    surfaces: Dict[int, pygame.Surface] = {}
    print(f"[editor] TMX tilesets ({len(tmx.tilesets)}):")
    for ts in tmx.tilesets:
        firstgid = ts.firstgid
        tilecount = getattr(ts, "tilecount", 0) or 0
        source = getattr(ts, "source", None)
        print(f"  - name={getattr(ts, 'name', '<unnamed>')} firstgid={firstgid} tilecount={tilecount} source={source}")
        for local_id in range(tilecount):
            gid = firstgid + local_id
            try:
                surf = tmx.get_tile_image_by_gid(gid)
            except IndexError:
                continue
            if surf is None:
                continue
            if isinstance(surf, tuple) and surf and hasattr(surf[0], "copy"):
                surf = surf[0]
            if hasattr(surf, "copy"):
                surfaces[gid] = surf.copy()
    print(f"[editor] TMX gid surfaces built: {len(surfaces)} entries")
    return surfaces
