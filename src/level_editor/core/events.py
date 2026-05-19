"""Event handling for the level editor.

This module centralizes keyboard and mouse dispatch so ``app.py`` can focus on
setup and rendering orchestration.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional

import pygame

from ..map_template import MapTemplate
from ..palette_model import PaletteModel
from ..palette_ui import PalettePanel
from ..tileset_loader import TilesetData
from ..ui import modals
from . import commands
from . import palette_controller
from . import tileset_index as core_tilesets


@dataclass
class EventContext:
    tmpl: MapTemplate
    palette_model: Optional[PaletteModel]
    palette_panel: Optional[PalettePanel]
    tileset_index: List[tuple[str, TilesetData, int]]
    tileset_names: List[str]
    firstgid_map: Dict[str, int]
    current_path: Optional[Path]
    grid_w: int
    grid_h: int
    total_w: int
    tile_pixels: int
    layer_panel_width: int
    layer_button_height: int
    layer_spacing: int
    layer_names: List[str]
    refresh_load_files: Callable[[], None]
    perform_load: Callable[[Path], None]
    apply_initial_selection: Callable[[], None]
    save_template: Callable[[Path], None]
    log_error: Callable[[str, Exception], None]


def _handle_save_modal(event: pygame.event.Event, state, ctx: EventContext) -> bool:
    proceed = modals.handle_save_input(state, event)
    if not proceed:
        try:
            raw = state.save_input.strip()
            if not raw:
                raise ValueError("Path cannot be empty")
            candidate = Path(raw)
            if not candidate.is_absolute():
                candidate = (Path("maps") / "editor_templates" / candidate).resolve()
            if candidate.suffix == "":
                candidate = candidate.with_suffix(".json")
            ctx.save_template(candidate)
            state.save_message = f"Saved {candidate}"
            state.save_as_active = False
        except Exception as exc:
            state.save_message = f"Save failed: {exc}"
            ctx.log_error("Save failed", exc)
    return True


def _handle_load_modal(event: pygame.event.Event, state, ctx: EventContext) -> bool:
    proceed = modals.handle_load_input(state, event)
    if not proceed:
        target = Path(state.load_input.strip()) if state.load_input.strip() else (
            state.load_files[state.load_index] if state.load_files else None
        )
        if target:
            try:
                ctx.perform_load(target)
                state.load_message = f"Loaded {target}"
                state.load_active = False
            except Exception as exc:
                state.load_message = f"Load failed: {exc}"
                ctx.log_error("Load failed", exc)
    return True


def handle_event(
    event: pygame.event.Event,
    state,
    ctx: EventContext,
    *,
    fill_rectangle: Callable[[MapTemplate, int, int, int, int, int, str], None],
    flood_fill: Callable[[MapTemplate, int, int, int, str], None],
) -> bool:
    """Process a single pygame event. Returns False to request exit."""
    if event.type == pygame.QUIT:
        return False

    if event.type == pygame.KEYDOWN:
        if state.save_as_active:
            return _handle_save_modal(event, state, ctx)
        if state.load_active:
            return _handle_load_modal(event, state, ctx)

        if event.key == pygame.K_ESCAPE:
            if ctx.palette_panel is not None and getattr(ctx.palette_panel, "_active_filter", "none") != "none":
                ctx.palette_panel._apply_filter("none")
                return True
            return False
        if event.key == pygame.K_s:
            if event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT:
                state.save_as_active = True
                state.save_message = ""
                state.save_input = str(ctx.current_path) if ctx.current_path else "maps\\editor_templates\\template.json"
            elif event.mod & pygame.KMOD_CTRL:
                path = ctx.current_path or (Path("maps") / "editor_templates" / "template.json")
                try:
                    ctx.save_template(path)
                    print(f"Saved template to {path}")
                except Exception as exc:
                    state.save_message = f"Save failed: {exc}"
                    ctx.log_error("Save failed", exc)
            else:
                path = ctx.current_path or (Path("maps") / "editor_templates" / "template.json")
                try:
                    ctx.save_template(path)
                    print(f"Saved template to {path}")
                except Exception as exc:
                    state.save_message = f"Save failed: {exc}"
                    ctx.log_error("Save failed", exc)
        elif event.key == pygame.K_F2:
            state.save_as_active = True
            state.save_message = ""
            state.save_input = str(ctx.current_path) if ctx.current_path else "maps\\editor_templates\\template.json"
        elif event.key == pygame.K_l:
            if state.load_active:
                state.load_active = False
                state.load_message = ""
            else:
                state.load_active = True
                state.load_input = ""
                state.load_message = ""
                ctx.refresh_load_files()
                state.load_index = 0
                if state.load_files:
                    state.load_index = min(state.load_index, len(state.load_files) - 1)
        elif pygame.K_1 <= event.key <= pygame.K_4:
            layer_index = event.key - pygame.K_1
            commands.switch_layer(state, ctx.layer_names, layer_index)
            ctx.apply_initial_selection()
        elif event.key == pygame.K_h:
            commands.toggle_help(state)
        elif event.key == pygame.K_p:
            commands.set_tool(state, "PAINT")
        elif event.key == pygame.K_r:
            commands.set_tool(state, "RECT")
        elif event.key == pygame.K_f:
            if event.mod & pygame.KMOD_CTRL:
                commands.set_tool(state, "FILL")
        return True

    if event.type == pygame.MOUSEBUTTONDOWN:
        if state.load_active:
            mx, my = event.pos
            modal_w = min(760, ctx.total_w - 40)
            modal_h = min(420, ctx.grid_h - 40)
            modal_x = (ctx.total_w - modal_w) // 2
            modal_y = (ctx.grid_h - modal_h) // 2
            list_top = modal_y + 40
            list_h = modal_h - 80
            item_h = 22
            if modal_x <= mx <= modal_x + modal_w and list_top <= my <= list_top + list_h:
                visible = list_h // item_h
                start = max(0, state.load_index - visible + 1) if state.load_index >= visible else 0
                end = min(len(state.load_files), start + visible)
                idx = start + (my - list_top) // item_h
                if start <= idx < end:
                    state.load_index = idx
                    state.load_input = str(state.load_files[state.load_index]) if state.load_files else state.load_input
            elif not (modal_x <= mx <= modal_x + modal_w and modal_y <= my <= modal_y + modal_h):
                state.load_active = False
            return True

        if event.button == 1:
            mx, my = event.pos
            if mx < ctx.grid_w:
                x = mx // ctx.tile_pixels
                y = my // ctx.tile_pixels
                if state.tool == "PAINT":
                    commands.paint(state, x, y)
                elif state.tool == "RECT":
                    commands.rect_begin(state, x, y)
                elif state.tool == "FILL":
                    commands.flood(state, x, y, flood_fill)
            elif mx < ctx.grid_w + ctx.layer_panel_width:
                rel_x = mx - ctx.grid_w
                rel_y = my
                y_pos = 35
                for layer_name in ctx.layer_names:
                    button_rect = pygame.Rect(8, y_pos, ctx.layer_panel_width - 16, ctx.layer_button_height)
                    if button_rect.collidepoint(rel_x, rel_y):
                        eye_x = button_rect.right - 20
                        if rel_x > eye_x - 10:
                            commands.toggle_visibility(state, layer_name)
                        else:
                            state.current_layer = layer_name
                            ctx.apply_initial_selection()
                        break
                    y_pos += ctx.layer_button_height + ctx.layer_spacing
        elif event.button == 3:
            mx, my = event.pos
            if mx < ctx.grid_w:
                x = mx // ctx.tile_pixels
                y = my // ctx.tile_pixels
                try:
                    picked = ctx.tmpl.get(x, y, state.current_layer)
                    if isinstance(picked, int):
                        palette_controller.handle_eyedropper_selection(
                            state,
                            ctx.palette_model,
                            ctx.palette_panel,
                            ctx.tileset_names,
                            ctx.tileset_index,
                            picked,
                        )
                except (IndexError, KeyError):
                    pass
        return True

    if event.type == pygame.MOUSEMOTION:
        if state.rect_active and state.tool == "RECT":
            mx, my = event.pos
            if mx < ctx.grid_w:
                commands.rect_update(
                    state,
                    max(0, min(ctx.tmpl.width - 1, mx // ctx.tile_pixels)),
                    max(0, min(ctx.tmpl.height - 1, my // ctx.tile_pixels)),
                )
        return True

    if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1 and state.rect_active and state.tool == "RECT":
            mx, my = event.pos
            if mx < ctx.grid_w and state.rect_start is not None and state.rect_current is not None:
                x1 = mx // ctx.tile_pixels
                y1 = my // ctx.tile_pixels
                commands.rect_commit(state, x1, y1, fill_rectangle)
        return True

    return True
