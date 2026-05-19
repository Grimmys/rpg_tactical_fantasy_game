"""Palette-related helper functions."""
from __future__ import annotations

from typing import Optional, List

import pygame

from ..palette_model import PaletteModel
from ..palette_ui import PalettePanel, PaletteUIConfig
from ..tileset_loader import TilesetData
from . import commands
from . import tileset_index as core_tilesets


def build_panel(
    palette_model: PaletteModel,
    grid_w: int,
    grid_h: int,
    *,
    layer_panel_width: int,
    palette_width: int,
    tile_render_size: int,
    grid_cols: int,
    grid_rows: int,
    padding: int,
    gutter: int,
    on_tileset_menu,
) -> PalettePanel:
    return PalettePanel(
        palette_model,
        pygame.Rect(grid_w + layer_panel_width, 0, palette_width, grid_h),
        on_tileset_menu=on_tileset_menu,
        config=PaletteUIConfig(
            tile_render_size=tile_render_size,
            grid_cols=grid_cols,
            grid_rows=grid_rows,
            padding=padding,
            gutter=gutter,
        ),
    )


def apply_initial_selection(state, palette_panel: Optional[PalettePanel], palette_model: Optional[PaletteModel], firstgid_map) -> None:
    if palette_model is None or palette_panel is None:
        return
    tiles = palette_model.page_tiles()
    if not tiles:
        return
    palette_panel.selected = tiles[0]
    state.selected_gid = core_tilesets.gid_for_tile(firstgid_map, tiles[0])


def sync_selected_gid_from_palette(state, palette_panel: Optional[PalettePanel], firstgid_map) -> None:
    if palette_panel is not None and palette_panel.selected is not None:
        gid = core_tilesets.gid_for_tile(firstgid_map, palette_panel.selected)
        if gid:
            state.selected_gid = gid


def rebuild_palette(
    state,
    tmpl,
    tsx_paths,
    grid_w: int,
    grid_h: int,
    *,
    layer_panel_width: int,
    palette_width: int,
    tile_render_size: int,
    grid_cols: int,
    grid_rows: int,
    padding: int,
    gutter: int,
    on_tileset_menu,
):
    explicit_fg = getattr(tmpl, "tileset_firstgids", None)
    if explicit_fg and len(explicit_fg) != len(tsx_paths):
        print(
            f"[editor] Warning: tileset_firstgids length ({len(explicit_fg)}) does not match tilesets ({len(tsx_paths)}); falling back to computed firstgid order"
        )
    tileset_cache, tileset_index, firstgid_map, tileset_names = core_tilesets.build_tileset_index(tsx_paths, explicit_fg)
    palette_model = PaletteModel(tileset_cache)
    state.tileset_names = tileset_names
    state.active_tileset_index = 0
    if tileset_names:
        palette_model.set_tileset(tileset_names[state.active_tileset_index])
    palette_panel = build_panel(
        palette_model,
        grid_w,
        grid_h,
        layer_panel_width=layer_panel_width,
        palette_width=palette_width,
        tile_render_size=tile_render_size,
        grid_cols=grid_cols,
        grid_rows=grid_rows,
        padding=padding,
        gutter=gutter,
        on_tileset_menu=on_tileset_menu,
    )
    apply_initial_selection(state, palette_panel, palette_model, firstgid_map)
    print("[editor] Tileset order:", tileset_names)
    print("[editor] Firstgid map:", firstgid_map)
    return palette_model, palette_panel, tileset_cache, tileset_index, tileset_names, firstgid_map


def cycle_tileset(state, palette_model: Optional[PaletteModel], palette_panel: Optional[PalettePanel], tileset_names: List[str], firstgid_map, delta: int = 1) -> None:
    if not tileset_names or palette_model is None:
        return
    commands.cycle_tileset(state, delta)
    palette_model.set_tileset(tileset_names[state.active_tileset_index])
    if palette_panel is not None:
        palette_panel.selected = None
    apply_initial_selection(state, palette_panel, palette_model, firstgid_map)


def handle_eyedropper_selection(
    state,
    palette_model: Optional[PaletteModel],
    palette_panel: Optional[PalettePanel],
    tileset_names: List[str],
    tileset_index: List[tuple[str, TilesetData, int]],
    picked_gid: int,
) -> None:
    state.selected_gid = picked_gid
    tile_entry = core_tilesets.tile_for_gid(tileset_index, picked_gid)
    if tile_entry is None:
        return
    if palette_model and palette_model.state.tileset_name != tile_entry.tileset_name:
        palette_model.set_tileset(tile_entry.tileset_name)
        if tile_entry.tileset_name in tileset_names:
            state.active_tileset_index = tileset_names.index(tile_entry.tileset_name)
    if palette_panel is not None:
        palette_panel.selected = tile_entry
