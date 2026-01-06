"""Editor commands that mutate MapTemplate and EditorState."""
from __future__ import annotations

from typing import Optional

from ..map_template import MapTemplate
from .app_state import EditorState


def set_tool(state: EditorState, tool: str) -> None:
    state.tool = tool
    state.reset_rect()


def switch_layer(state: EditorState, layer_names: list[str], idx: int) -> None:
    if 0 <= idx < len(layer_names):
        state.current_layer = layer_names[idx]
        state.reset_rect()


def toggle_help(state: EditorState) -> None:
    state.help_active = not state.help_active


def toggle_visibility(state: EditorState, layer_name: str) -> None:
    layer = state.tmpl.get_layer(layer_name)
    layer.visible = not layer.visible


def fill_rectangle(tmpl: MapTemplate, x0: int, y0: int, x1: int, y1: int, tile_id: int, layer_name: str) -> None:
    """Fill rectangle bounded by (x0,y0) and (x1,y1) inclusive with tile_id on specified layer."""
    if x0 > x1:
        x0, x1 = x1, x0
    if y0 > y1:
        y0, y1 = y1, y0
    for y in range(max(0, y0), min(tmpl.height - 1, y1) + 1):
        for x in range(max(0, x0), min(tmpl.width - 1, x1) + 1):
            tmpl.set(x, y, tile_id, layer_name)


def flood_fill(tmpl: MapTemplate, sx: int, sy: int, new_id: int, layer_name: str) -> None:
    """Flood fill from (sx,sy) replacing the original id with new_id on specified layer."""
    if not (0 <= sx < tmpl.width and 0 <= sy < tmpl.height):
        return
    original = tmpl.get(sx, sy, layer_name)
    if original == new_id:
        return
    w, h = tmpl.width, tmpl.height
    stack = [(sx, sy)]
    while stack:
        x, y = stack.pop()
        if tmpl.get(x, y, layer_name) != original:
            continue
        tmpl.set(x, y, new_id, layer_name)
        if x > 0 and tmpl.get(x - 1, y, layer_name) == original:
            stack.append((x - 1, y))
        if x + 1 < w and tmpl.get(x + 1, y, layer_name) == original:
            stack.append((x + 1, y))
        if y > 0 and tmpl.get(x, y - 1, layer_name) == original:
            stack.append((x, y - 1))
        if y + 1 < h and tmpl.get(x, y + 1, layer_name) == original:
            stack.append((x, y + 1))


def paint(state: EditorState, x: int, y: int) -> None:
    state.tmpl.set(x, y, state.selected_gid, state.current_layer)
    state.dirty = True


def rect_begin(state: EditorState, x: int, y: int) -> None:
    state.rect_active = True
    state.rect_start = (x, y)
    state.rect_current = (x, y)


def rect_update(state: EditorState, x: int, y: int) -> None:
    if state.rect_active:
        state.rect_current = (x, y)


def rect_commit(state: EditorState, x: int, y: int, fill_fn) -> None:
    if not (state.rect_active and state.rect_start):
        return
    x0, y0 = state.rect_start
    fill_fn(state.tmpl, x0, y0, x, y, state.selected_gid, state.current_layer)
    state.reset_rect()
    state.dirty = True


def flood(state: EditorState, x: int, y: int, flood_fn) -> None:
    flood_fn(state.tmpl, x, y, state.selected_gid, state.current_layer)
    state.dirty = True


def eyedrop(state: EditorState, gid: int) -> None:
    state.selected_gid = gid


def cycle_tileset(state: EditorState, delta: int) -> None:
    if not state.tileset_names:
        return
    state.active_tileset_index = (state.active_tileset_index + delta) % len(state.tileset_names)


def set_selected_gid(state: EditorState, gid: int) -> None:
    state.selected_gid = gid
