"""Rendering helpers for the level editor UI."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import pygame

from ..map_template import MapTemplate
from ..palette_ui import PaletteUIConfig
from ..tileset_loader import TileEntry, TilesetData
from src.services.tmx_loader_core import ParsedMap

TileFetcher = Callable[[List[tuple[str, TilesetData, int]], int, Optional[Dict[int, pygame.Surface]]], Optional[TileEntry | pygame.Surface]]


def draw_grid(
    screen: pygame.Surface,
    tmpl: MapTemplate,
    tileset_index: List[tuple[str, TilesetData, int]],
    font: pygame.font.Font,
    selected_gid: int,
    tool_name: str,
    current_layer: str,
    grid_w: int,
    grid_h: int,
    rect_preview: Optional[Tuple[int, int, int, int]] = None,
    tmx_gid_surfaces: Optional[Dict[int, pygame.Surface]] = None,
    parsed_map: Optional[ParsedMap] = None,
    *,
    tile_pixels: int,
    layer_names: Sequence[str],
    layer_colors: Dict[str, Tuple[int, int, int]],
    margin: int,
    tile_fetcher: TileFetcher,
) -> None:
    """Draw the editable tile grid on the left side of the window."""
    checker_a = (40, 40, 44)
    checker_b = (48, 48, 52)

    missing_gid_once: Dict[int, bool] = {}
    layer_stats: Dict[str, Dict[str, int]] = {ln: {"nz": 0, "min": 0, "max": 0} for ln in layer_names}

    for y in range(tmpl.height):
        for x in range(tmpl.width):
            rect = pygame.Rect(x * tile_pixels, y * tile_pixels, tile_pixels, tile_pixels)
            color = checker_a if (x + y) % 2 == 0 else checker_b
            pygame.draw.rect(screen, color, rect)

            for layer_name in layer_names:
                if layer_name in tmpl.layers and tmpl.layers[layer_name].visible:
                    gid = tmpl.layers[layer_name].get(x, y)
                    if gid > 0:
                        st = layer_stats[layer_name]
                        st["nz"] += 1
                        st["min"] = gid if st["min"] == 0 else min(st["min"], gid)
                        st["max"] = max(st["max"], gid)
                        surfaces = parsed_map.gid_surfaces if parsed_map is not None else tmx_gid_surfaces
                        tile_entry = tile_fetcher(tileset_index, gid, surfaces)
                        if isinstance(tile_entry, pygame.Surface):
                            surf = tile_entry
                        elif tile_entry is not None:
                            surf = tile_entry.surface
                        else:
                            surf = None
                        if surf is not None:
                            if surf.get_width() != tile_pixels or surf.get_height() != tile_pixels:
                                surf = pygame.transform.smoothscale(surf, (tile_pixels, tile_pixels))
                            screen.blit(surf, rect)
                        else:
                            pygame.draw.rect(screen, (80, 80, 80), rect)
                            if gid not in missing_gid_once:
                                missing_gid_once[gid] = True

            if current_layer in tmpl.layers:
                layer_color = layer_colors.get(current_layer, (255, 255, 255))
                pygame.draw.rect(screen, layer_color, rect, width=1)
            else:
                pygame.draw.rect(screen, (20, 20, 20), rect, width=margin)

    label = f"GID {selected_gid} (Tool: {tool_name}, Layer: {current_layer})"
    text_surface = font.render(f"Selected: {label}", True, (255, 255, 255))
    screen.blit(text_surface, (8, 8))
    if tool_name == "OBJECT":
        active_type = getattr(tmpl, "_editor_active_object_type", None)
        # Fallback annotation: caller passes via attribute or skip.
        hint_text = "Click: place  RClick: delete  Tab/]: next type  [: prev"
        screen.blit(font.render(hint_text, True, (200, 220, 255)), (8, 26))

    if rect_preview is not None:
        x0, y0, x1, y1 = rect_preview
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        left = x0 * tile_pixels
        top = y0 * tile_pixels
        width = (x1 - x0 + 1) * tile_pixels
        height = (y1 - y0 + 1) * tile_pixels
        preview_rect = pygame.Rect(left, top, width, height)
        pygame.draw.rect(screen, (255, 215, 0), preview_rect, width=2)

    hint = font.render("H: Help", True, (220, 220, 220))
    screen.blit(hint, (8, grid_h - hint.get_height() - 8))

    if parsed_map is not None:
        scale_x = tile_pixels / max(1, parsed_map.tilewidth)
        scale_y = tile_pixels / max(1, parsed_map.tileheight)
        for lname in ("dynamic_data", "events"):
            olayer = parsed_map.object_layers.get(lname)
            if olayer is None:
                continue
            for obj in getattr(olayer, "objects", []) or []:
                surf = obj.image
                if surf is None:
                    continue
                if surf.get_width() != tile_pixels or surf.get_height() != tile_pixels:
                    surf = pygame.transform.smoothscale(surf, (tile_pixels, tile_pixels))
                screen.blit(surf, (int(obj.x * scale_x), int(obj.y * scale_y)))

    # Editable object overlay (from MapTemplate) — colour-coded by type, drawn above tiles.
    object_palette = {
        "placement": (80, 200, 240),
        "foe": (220, 60, 60),
        "ally": (60, 180, 90),
        "objective": (240, 200, 60),
    }
    dynamic_layer = tmpl.object_layers.get("dynamic_data", [])
    tw = max(1, tmpl.tile_width)
    th = max(1, tmpl.tile_height)
    for obj in dynamic_layer:
        if obj.type not in object_palette:
            continue
        px = int(obj.x / tw * tile_pixels)
        py = int(obj.y / th * tile_pixels)
        rect = pygame.Rect(px + 3, py + 3, tile_pixels - 6, tile_pixels - 6)
        color = object_palette[obj.type]
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((*color, 90))
        screen.blit(overlay, rect.topleft)
        pygame.draw.rect(screen, color, rect, width=2)
        glyph = obj.type[0].upper()
        label = font.render(glyph, True, (10, 10, 10))
        screen.blit(label, (rect.x + 4, rect.y + 2))


def draw_layer_panel(
    screen: pygame.Surface,
    x_offset: int,
    height: int,
    tmpl: MapTemplate,
    font: pygame.font.Font,
    current_layer: str,
    *,
    layer_names: Sequence[str],
    layer_colors: Dict[str, Tuple[int, int, int]],
    panel_width: int,
    button_height: int,
    layer_spacing: int,
) -> None:
    panel_rect = pygame.Rect(x_offset, 0, panel_width, height)
    pygame.draw.rect(screen, (28, 28, 32), panel_rect)
    pygame.draw.rect(screen, (60, 60, 60), panel_rect, 1)

    title_surf = font.render("LAYERS", True, (255, 255, 255))
    screen.blit(title_surf, (x_offset + 8, 8))

    y_pos = 35
    for layer_name in layer_names:
        button_rect = pygame.Rect(x_offset + 8, y_pos, panel_width - 16, button_height)
        layer = tmpl.layers.get(layer_name)
        is_visible = layer.visible if layer else True

        if layer_name == current_layer:
            pygame.draw.rect(screen, layer_colors[layer_name], button_rect)
            text_color = (255, 255, 255)
        elif is_visible:
            dark_color = tuple(c // 2 for c in layer_colors[layer_name])
            pygame.draw.rect(screen, dark_color, button_rect)
            text_color = (220, 220, 220)
        else:
            pygame.draw.rect(screen, (40, 40, 40), button_rect)
            text_color = (120, 120, 120)

        pygame.draw.rect(screen, (80, 80, 80), button_rect, 1)

        name_surf = font.render(layer_name.upper(), True, text_color)
        text_x = button_rect.x + 8
        text_y = button_rect.y + (button_height - name_surf.get_height()) // 2
        screen.blit(name_surf, (text_x, text_y))

        eye_x = button_rect.right - 20
        eye_y = button_rect.y + button_height // 2
        if is_visible:
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 5, 1)
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 2)
        else:
            pygame.draw.line(screen, (150, 150, 150), (eye_x - 6, eye_y - 3), (eye_x + 6, eye_y + 3), 2)
            pygame.draw.line(screen, (150, 150, 150), (eye_x - 6, eye_y + 3), (eye_x + 6, eye_y - 3), 2)

        y_pos += button_height + layer_spacing


def draw_help_overlay(screen: pygame.Surface, total_w: int, grid_h: int, font: pygame.font.Font) -> None:
    overlay = pygame.Surface((total_w, grid_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    pad = 14
    box_w = min(820, total_w - pad * 2)
    lines = [
        "Controls:",
        "  P: Paint | R: Rectangle Fill | Ctrl+F: Flood Fill | H: Toggle Help",
        "  Left Click (grid): paint    | Right Click (grid): eyedrop",
        "  Palette: click dropdown to filter categories; Esc clears filter",
        "  Comma/Period: cycle palette category | PageUp/PageDown: palette page",
        "  1-4: Switch layers (Ground/Obstacles/Allies/Foes)",
        "  Click layer name: switch layer | Click eye: toggle visibility",
        "  Ctrl+S: Save | Ctrl+Shift+S or F2: Save As | L: Load | ESC: Exit",
    ]
    box_h = pad * 2 + len(lines) * (font.get_height() + 4)
    x = (total_w - box_w) // 2
    y = (grid_h - box_h) // 2
    box = pygame.Rect(x, y, box_w, box_h)
    pygame.draw.rect(screen, (34, 34, 40), box)
    pygame.draw.rect(screen, (210, 210, 210), box, 2)

    ty = y + pad
    for i, line in enumerate(lines):
        color = (255, 255, 255) if i == 0 else (235, 235, 235)
        surf = font.render(line, True, color)
        screen.blit(surf, (x + pad, ty))
        ty += font.get_height() + 4


def draw_save_modal(
    screen: pygame.Surface,
    total_w: int,
    grid_h: int,
    font: pygame.font.Font,
    save_input: str,
    save_message: str,
) -> None:
    overlay = pygame.Surface((total_w, grid_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    modal_w = min(760, total_w - 40)
    modal_h = 140
    modal_x = (total_w - modal_w) // 2
    modal_y = (grid_h - modal_h) // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
    pygame.draw.rect(screen, (38, 38, 44), modal_rect)
    pygame.draw.rect(screen, (200, 200, 200), modal_rect, 2)

    title = font.render("Save As (Enter to confirm, Esc to cancel)", True, (255, 255, 255))
    screen.blit(title, (modal_x + 12, modal_y + 10))

    input_rect = pygame.Rect(modal_x + 12, modal_y + 40, modal_w - 24, 30)
    pygame.draw.rect(screen, (18, 18, 18), input_rect)
    pygame.draw.rect(screen, (120, 120, 120), input_rect, 1)

    truncated = save_input
    while True:
        text_surf = font.render(truncated, True, (240, 240, 240))
        if text_surf.get_width() <= input_rect.width - 10 or len(truncated) <= 1:
            break
        truncated = truncated[1:]
    screen.blit(text_surf, (input_rect.x + 6, input_rect.y + 6))

    if save_message:
        msg = font.render(save_message, True, (255, 200, 120))
        screen.blit(msg, (modal_x + 12, modal_y + 80))


def draw_load_modal(
    screen: pygame.Surface,
    total_w: int,
    grid_h: int,
    font: pygame.font.Font,
    load_files: Sequence[Path],
    load_index: int,
    load_input: str,
    load_message: str,
) -> None:
    overlay = pygame.Surface((total_w, grid_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    modal_w = min(760, total_w - 40)
    modal_h = min(420, grid_h - 40)
    modal_x = (total_w - modal_w) // 2
    modal_y = (grid_h - modal_h) // 2
    modal_rect = pygame.Rect(modal_x, modal_y, modal_w, modal_h)
    pygame.draw.rect(screen, (38, 38, 44), modal_rect)
    pygame.draw.rect(screen, (200, 200, 200), modal_rect, 2)

    title = font.render("Load Map (Enter to load, Esc to cancel)", True, (255, 255, 255))
    screen.blit(title, (modal_x + 12, modal_y + 10))

    list_top = modal_y + 40
    list_h = modal_h - 80
    item_h = 22
    visible = list_h // item_h
    start = max(0, load_index - visible + 1) if load_index >= visible else 0
    end = min(len(load_files), start + visible)

    for i, p in enumerate(load_files[start:end], start):
        y = list_top + (i - start) * item_h
        row_rect = pygame.Rect(modal_x + 12, y, modal_w - 24, item_h - 2)
        if i == load_index:
            pygame.draw.rect(screen, (70, 110, 180), row_rect)
        else:
            pygame.draw.rect(screen, (26, 26, 30), row_rect)
        label = str(p)
        text = font.render(label, True, (240, 240, 240))
        screen.blit(text, (row_rect.x + 6, row_rect.y + 2))

    input_rect = pygame.Rect(modal_x + 12, modal_y + modal_h - 32, modal_w - 24, 24)
    pygame.draw.rect(screen, (18, 18, 18), input_rect)
    pygame.draw.rect(screen, (120, 120, 120), input_rect, 1)
    display_text = load_input or (str(load_files[load_index]) if load_files else "")
    text_surf = font.render(display_text, True, (240, 240, 240))
    screen.blit(text_surf, (input_rect.x + 6, input_rect.y + 4))

    if load_message:
        msg = font.render(load_message, True, (255, 200, 120))
        screen.blit(msg, (modal_x + 12, modal_y + modal_h - 56))
