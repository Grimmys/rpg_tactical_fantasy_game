"""
Minimal Pygame-based level editor.

Now tileset-driven: paint a grid of GIDs (global tile ids) from TSX tilesets
and save/load JSON templates that include tileset ordering for firstgid.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame

from level_editor.tilesets import Tileset, gid_lookup, load_tilesets
from level_editor.map_template import MapTemplate
from level_editor.tile_categories import tile_categorizer


TILE_PIXELS = 32  # Size of map tiles in the editor grid
MARGIN = 1        # Grid border thickness

# Palette layout
PALETTE_WIDTH = 350  # Increased width to show more sprites
PALETTE_MARGIN = 8
PALETTE_TILE = 28   # Slightly smaller tile thumbnails to fit more
PALETTE_TEXT_COLOR = (240, 240, 240)
TAB_HEIGHT = 28
TAB_PAD_X = 10
TAB_SPACING = 8

# Layer management
LAYER_PANEL_WIDTH = 150
LAYER_BUTTON_HEIGHT = 25
LAYER_SPACING = 5
LAYER_NAMES = ["ground", "obstacles", "allies", "foes"]
LAYER_COLORS = {
    "ground": (100, 150, 100),
    "obstacles": (150, 100, 100),
    "allies": (100, 100, 200),
    "foes": (200, 100, 100)
}


def draw_grid(
    screen: pygame.Surface,
    tmpl: MapTemplate,
    tilesets: List[Tileset],
    font: pygame.font.Font,
    selected_gid: int,
    tool_name: str,
    current_layer: str,
    grid_w: int,
    grid_h: int,
    rect_preview: Optional[Tuple[int, int, int, int]] = None,
) -> None:
    """Draw the editable tile grid on the left side of the window."""
    # Background checker for empty cells
    checker_a = (40, 40, 44)
    checker_b = (48, 48, 52)
    
    for y in range(tmpl.height):
        for x in range(tmpl.width):
            rect = pygame.Rect(x * TILE_PIXELS, y * TILE_PIXELS, TILE_PIXELS, TILE_PIXELS)
            
            # Draw background checker
            color = checker_a if (x + y) % 2 == 0 else checker_b
            pygame.draw.rect(screen, color, rect)
            
            # Draw all visible layers from bottom to top
            for layer_name in LAYER_NAMES:
                if layer_name in tmpl.layers and tmpl.layers[layer_name].visible:
                    gid = tmpl.layers[layer_name].get(x, y)
                    if gid > 0:
                        ts, local_id = gid_lookup(tilesets, gid)
                        if ts is not None and local_id is not None:
                            surf = ts.get_surface_by_local_id(local_id)
                            if surf is not None:
                                if surf.get_width() != TILE_PIXELS or surf.get_height() != TILE_PIXELS:
                                    surf = pygame.transform.smoothscale(surf, (TILE_PIXELS, TILE_PIXELS))
                                
                                # Add slight tint for non-ground layers for visual distinction
                                if layer_name != "ground":
                                    tinted_surf = surf.copy()
                                    tint_color = LAYER_COLORS.get(layer_name, (255, 255, 255))
                                    tint_overlay = pygame.Surface((TILE_PIXELS, TILE_PIXELS))
                                    tint_overlay.fill(tint_color)
                                    tint_overlay.set_alpha(30)
                                    tinted_surf.blit(tint_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
                                    screen.blit(tinted_surf, rect)
                                else:
                                    screen.blit(surf, rect)
                            else:
                                pygame.draw.rect(screen, (120, 40, 40), rect)
                        else:
                            pygame.draw.rect(screen, (80, 80, 80), rect)
            
            # Highlight current layer with border
            if current_layer in tmpl.layers:
                layer_color = LAYER_COLORS.get(current_layer, (255, 255, 255))
                pygame.draw.rect(screen, layer_color, rect, width=1)
            else:
                pygame.draw.rect(screen, (20, 20, 20), rect, width=MARGIN)

    label = f"GID {selected_gid} (Tool: {tool_name}, Layer: {current_layer})"
    text_surface = font.render(f"Selected: {label}", True, (255, 255, 255))
    screen.blit(text_surface, (8, 8))

    # Draw rectangle selection preview if any
    if rect_preview is not None:
        x0, y0, x1, y1 = rect_preview
        if x0 > x1:
            x0, x1 = x1, x0
        if y0 > y1:
            y0, y1 = y1, y0
        left = x0 * TILE_PIXELS
        top = y0 * TILE_PIXELS
        width = (x1 - x0 + 1) * TILE_PIXELS
        height = (y1 - y0 + 1) * TILE_PIXELS
        preview_rect = pygame.Rect(left, top, width, height)
        # Border highlight
        pygame.draw.rect(screen, (255, 215, 0), preview_rect, width=2)

    # Small help hint at bottom-left
    hint = font.render("H: Help", True, (220, 220, 220))
    screen.blit(hint, (8, grid_h - hint.get_height() - 8))


def draw_layer_panel(
    screen: pygame.Surface,
    x_offset: int,
    height: int,
    tmpl: MapTemplate,
    font: pygame.font.Font,
    current_layer: str,
) -> None:
    """Draw the layer management panel."""
    # Background
    panel_rect = pygame.Rect(x_offset, 0, LAYER_PANEL_WIDTH, height)
    pygame.draw.rect(screen, (28, 28, 32), panel_rect)
    pygame.draw.rect(screen, (60, 60, 60), panel_rect, 1)

    # Title
    title_surf = font.render("LAYERS", True, (255, 255, 255))
    screen.blit(title_surf, (x_offset + 8, 8))

    # Layer buttons
    y_pos = 35
    for i, layer_name in enumerate(LAYER_NAMES):
        button_rect = pygame.Rect(
            x_offset + 8, y_pos, LAYER_PANEL_WIDTH - 16, LAYER_BUTTON_HEIGHT
        )
        
        # Get layer visibility
        layer = tmpl.layers.get(layer_name)
        is_visible = layer.visible if layer else True
        
        # Button background
        if layer_name == current_layer:
            # Current layer highlight
            pygame.draw.rect(screen, LAYER_COLORS[layer_name], button_rect)
            text_color = (255, 255, 255)
        elif is_visible:
            # Visible but not current
            dark_color = tuple(c // 2 for c in LAYER_COLORS[layer_name])
            pygame.draw.rect(screen, dark_color, button_rect)
            text_color = (220, 220, 220)
        else:
            # Hidden layer
            pygame.draw.rect(screen, (40, 40, 40), button_rect)
            text_color = (120, 120, 120)
        
        # Button border
        pygame.draw.rect(screen, (80, 80, 80), button_rect, 1)
        
        # Layer name
        name_surf = font.render(layer_name.upper(), True, text_color)
        text_x = button_rect.x + 8
        text_y = button_rect.y + (LAYER_BUTTON_HEIGHT - name_surf.get_height()) // 2
        screen.blit(name_surf, (text_x, text_y))
        
        # Visibility toggle (eye icon approximation)
        eye_x = button_rect.right - 20
        eye_y = button_rect.y + LAYER_BUTTON_HEIGHT // 2
        if is_visible:
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 5, 1)
            pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 2)
        else:
            pygame.draw.line(screen, (150, 150, 150), (eye_x - 6, eye_y - 3), (eye_x + 6, eye_y + 3), 2)
            pygame.draw.line(screen, (150, 150, 150), (eye_x - 6, eye_y + 3), (eye_x + 6, eye_y - 3), 2)
        
        y_pos += LAYER_BUTTON_HEIGHT + LAYER_SPACING


def draw_palette_tilesets(
    screen: pygame.Surface,
    x_offset: int,
    height: int,
    tilesets: List[Tileset],
    font: pygame.font.Font,
    active_ts_index: int,
    selected_gid: int,
    scroll_by_ts: Dict[int, int],
    current_layer: str,
    show_all_sprites: bool = True,
) -> None:
    """Draw the palette panel with layer-filtered tiles and tileset tabs."""
    # Background
    palette_rect = pygame.Rect(x_offset, 0, PALETTE_WIDTH, height)
    pygame.draw.rect(screen, (32, 32, 36), palette_rect)

    # Header with layer indicator and filter toggle
    header_y = 5
    if show_all_sprites:
        header_text = f"ALL SPRITES (Layer: {current_layer.upper()})"
        header_color = (255, 255, 200)
    else:
        header_text = f"FILTERED: {current_layer.upper()}"
        header_color = LAYER_COLORS.get(current_layer, (255, 255, 255))
    
    header_surf = font.render(header_text, True, header_color)
    screen.blit(header_surf, (x_offset + PALETTE_MARGIN, header_y))
    
    # Filter toggle button
    toggle_text = "[F] Filter" if show_all_sprites else "[F] Show All"
    toggle_surf = font.render(toggle_text, True, (200, 200, 200))
    toggle_x = x_offset + PALETTE_WIDTH - toggle_surf.get_width() - PALETTE_MARGIN
    screen.blit(toggle_surf, (toggle_x, header_y))
    
    # Tabs
    tab_x = x_offset + PALETTE_MARGIN
    tab_y = 25  # Moved down to make room for header
    for i, ts in enumerate(tilesets):
        title = ts.name
        t_surf = font.render(title, True, (0, 0, 0))
        tab_w = t_surf.get_width() + TAB_PAD_X * 2
        tab_rect = pygame.Rect(tab_x, tab_y, tab_w, TAB_HEIGHT)
        color = (200, 200, 200) if i == active_ts_index else (120, 120, 120)
        pygame.draw.rect(screen, color, tab_rect, border_radius=6)
        pygame.draw.rect(screen, (24, 24, 24), tab_rect, 1, border_radius=6)
        screen.blit(t_surf, (tab_rect.x + TAB_PAD_X, tab_rect.y + (TAB_HEIGHT - t_surf.get_height()) // 2))
        tab_x += tab_w + TAB_SPACING

    # Grid of tiles for active tileset
    start_y = tab_y + TAB_HEIGHT + PALETTE_MARGIN
    # Compute columns that fit (more columns with smaller tiles)
    cols = max(1, (PALETTE_WIDTH - PALETTE_MARGIN * 2) // (PALETTE_TILE + PALETTE_MARGIN))
    rows_fit = max(1, (height - start_y - PALETTE_MARGIN) // (PALETTE_TILE + PALETTE_MARGIN))

    ts = tilesets[active_ts_index] if tilesets else None
    if not ts:
        return
        
    # Choose palette based on filter setting
    if show_all_sprites:
        # Show ALL sprites from the tileset
        sprite_palette = list(range(ts.tilecount))
        palette_info = f"Showing all {ts.tilecount} sprites"
    else:
        # Show layer-specific sprites only
        sprite_palette = tile_categorizer.create_layer_palette(ts, current_layer)
        if not sprite_palette:
            sprite_palette = list(range(min(100, ts.tilecount)))  # Show first 100 as fallback
        palette_info = f"Filtered: {len(sprite_palette)} sprites for {current_layer}"
    
    # Display palette info
    info_surf = font.render(palette_info, True, (180, 180, 180))
    info_y = start_y - 15
    screen.blit(info_surf, (x_offset + PALETTE_MARGIN, info_y))
    
    scroll = scroll_by_ts.get(active_ts_index, 0)
    max_rows = (len(sprite_palette) + cols - 1) // cols
    scroll = max(0, min(scroll, max(0, max_rows - rows_fit)))
    scroll_by_ts[active_ts_index] = scroll

    start_index = scroll * cols
    end_index = min(len(sprite_palette), start_index + cols * rows_fit)
    
    # Draw sprite grid
    for idx in range(start_index, end_index):
        local_id = sprite_palette[idx]
        display_idx = idx - start_index
        r = display_idx // cols
        c = display_idx % cols
        x = x_offset + PALETTE_MARGIN + c * (PALETTE_TILE + PALETTE_MARGIN)
        y = start_y + r * (PALETTE_TILE + PALETTE_MARGIN)
        rect = pygame.Rect(x, y, PALETTE_TILE, PALETTE_TILE)
        
        surf = ts.get_surface_by_local_id(local_id)
        if surf is not None:
            if surf.get_width() != PALETTE_TILE or surf.get_height() != PALETTE_TILE:
                surf = pygame.transform.smoothscale(surf, (PALETTE_TILE, PALETTE_TILE))
            screen.blit(surf, rect)
            
            # Add small text overlay showing tile ID for reference
            if PALETTE_TILE >= 24:  # Only if tiles are big enough
                id_text = str(local_id)
                id_surf = pygame.font.Font(None, 16).render(id_text, True, (255, 255, 255))
                id_bg = pygame.Surface((id_surf.get_width() + 2, id_surf.get_height()), pygame.SRCALPHA)
                id_bg.fill((0, 0, 0, 180))
                screen.blit(id_bg, (x, y))
                screen.blit(id_surf, (x + 1, y))
        else:
            # Draw placeholder for missing sprites
            pygame.draw.rect(screen, (60, 60, 60), rect)
            
        pygame.draw.rect(screen, (20, 20, 20), rect, 1)

        gid = ts.firstgid + local_id
        if gid == selected_gid:
            pygame.draw.rect(screen, (255, 215, 0), rect.inflate(4, 4), 2)


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
    """Flood fill from (sx,sy) replacing the original id with new_id on specified layer.

    Uses an explicit stack (non-recursive) to avoid recursion limits.
    """
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


def editor_main(width: int = 22, height: int = 14, template_path: Optional[Path] = None) -> None:
    pygame.init()
    grid_w = width * TILE_PIXELS
    grid_h = height * TILE_PIXELS
    total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
    screen = pygame.display.set_mode((total_w, grid_h))
    pygame.display.set_caption("Level Editor")
    font = pygame.font.SysFont(None, 20)

    # Load tilesets (default: all .tsx in imgs/tiled_tilesets, order by name)
    repo_root = Path(__file__).resolve().parents[2]
    default_tsx_dir = repo_root / "imgs" / "tiled_tilesets"
    tsx_paths = sorted(default_tsx_dir.glob("*.tsx"))
    tilesets: List[Tileset] = load_tilesets(tsx_paths)

    # Track current save/load path (defaults to maps/editor_templates/template.json)
    current_path: Optional[Path] = template_path
    if template_path and template_path.exists():
        tmpl = MapTemplate.load_json(template_path)
        # If template has tilesets, load them in that order
        if tmpl.tilesets:
            tsx_paths = [ (repo_root / p).resolve() for p in tmpl.tilesets ]
            tilesets = load_tilesets(tsx_paths)
        grid_w = tmpl.width * TILE_PIXELS
        grid_h = tmpl.height * TILE_PIXELS
        total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
        screen = pygame.display.set_mode((total_w, grid_h))
    else:
        tmpl = MapTemplate.create(width, height, fill=0, tilesets=[str(p.relative_to(repo_root)) for p in tsx_paths])
        # initialize a default path if none provided
        if current_path is None:
            current_path = Path("maps") / "editor_templates" / "template.json"

    # Selected tile: gid 0 means empty
    selected_gid = 0
    
    # Current layer
    current_layer = "ground"
    
    # Sprite display mode
    show_all_sprites = True  # Start in "show all" mode

    # Palette state
    active_tileset_index = 0
    palette_scroll_by_ts: Dict[int, int] = {}

    # Tools: PAINT (default), RECT (rectangle fill), FILL (flood fill)
    tool = "PAINT"
    rect_active = False
    rect_start: Optional[Tuple[int, int]] = None
    rect_current: Optional[Tuple[int, int]] = None

    # Save As modal state
    save_as_active = False
    save_input = str(current_path) if current_path is not None else "maps\\editor_templates\\template.json"
    save_message = ""

    def draw_save_modal():
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

        # Input box
        input_rect = pygame.Rect(modal_x + 12, modal_y + 40, modal_w - 24, 30)
        pygame.draw.rect(screen, (18, 18, 18), input_rect)
        pygame.draw.rect(screen, (120, 120, 120), input_rect, 1)

        truncated = save_input
        # Render input text; truncate if too long for box
        while True:
            text_surf = font.render(truncated, True, (240, 240, 240))
            if text_surf.get_width() <= input_rect.width - 10 or len(truncated) <= 1:
                break
            truncated = truncated[1:]
        screen.blit(text_surf, (input_rect.x + 6, input_rect.y + 6))

        if save_message:
            msg = font.render(save_message, True, (255, 200, 120))
            screen.blit(msg, (modal_x + 12, modal_y + 80))

    # Help overlay
    help_active = False

    def draw_help_overlay():
        overlay = pygame.Surface((total_w, grid_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        pad = 14
        box_w = min(820, total_w - pad * 2)
        # Rough height calc based on lines
        lines = [
            "Controls:",
            "  P: Paint | R: Rectangle Fill | Ctrl+F: Flood Fill | H: Toggle Help",
            "  F: Toggle Sprite Filter (All vs Layer-specific)",
            "  Left Click (grid): paint    | Right Click (grid): eyedrop",
            "  Mouse Wheel (palette): scroll tiles in active tileset tab",
            "  Click a tab to switch tileset; click a tile to select",
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

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # If modal open, route typing to it
                if save_as_active:
                    if event.key == pygame.K_ESCAPE:
                        save_as_active = False
                        save_message = ""
                    elif event.key == pygame.K_RETURN:
                        # Resolve path (relative -> maps/editor_templates)
                        try:
                            raw = save_input.strip()
                            if not raw:
                                raise ValueError("Path cannot be empty")
                            candidate = Path(raw)
                            if not candidate.is_absolute():
                                base = Path("maps") / "editor_templates"
                                candidate = base / candidate
                            if candidate.suffix.lower() != ".json":
                                candidate = candidate.with_suffix(".json")
                            # Persist tileset order for reproducible firstgid
                            tmpl.tilesets = [str(p.relative_to(repo_root)) for p in tsx_paths]
                            tmpl.save_json(candidate)
                            current_path = candidate
                            save_message = f"Saved to {candidate}"
                            save_as_active = False
                        except Exception as e:
                            save_message = f"Save failed: {e}"
                    elif event.key == pygame.K_BACKSPACE:
                        save_input = save_input[:-1]
                    else:
                        # Append printable characters
                        if event.unicode and 31 < ord(event.unicode) < 127:
                            save_input += event.unicode
                    continue
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    # Ctrl+S -> Save to current path, Shift+Ctrl+S -> Save As
                    if event.mod & pygame.KMOD_CTRL and event.mod & pygame.KMOD_SHIFT:
                        save_as_active = True
                        save_message = ""
                        save_input = str(current_path) if current_path else "maps\\editor_templates\\template.json"
                    elif event.mod & pygame.KMOD_CTRL:
                        path = current_path or (Path("maps") / "editor_templates" / "template.json")
                        tmpl.tilesets = [str(p.relative_to(repo_root)) for p in tsx_paths]
                        tmpl.save_json(path)
                        print(f"Saved template to {path}")
                    else:
                        # Backwards compat: plain S also saves to current path
                        path = current_path or (Path("maps") / "editor_templates" / "template.json")
                        tmpl.tilesets = [str(p.relative_to(repo_root)) for p in tsx_paths]
                        tmpl.save_json(path)
                        print(f"Saved template to {path}")
                elif event.key == pygame.K_F2:
                    # F2 opens Save As modal
                    save_as_active = True
                    save_message = ""
                    save_input = str(current_path) if current_path else "maps\\editor_templates\\template.json"
                elif event.key == pygame.K_l:
                    path = current_path or (Path("maps") / "editor_templates" / "template.json")
                    if path.exists():
                        tmpl = MapTemplate.load_json(path)
                        grid_w = tmpl.width * TILE_PIXELS
                        grid_h = tmpl.height * TILE_PIXELS
                        total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
                        screen = pygame.display.set_mode((total_w, grid_h))
                        print(f"Loaded template from {path}")
                        current_path = path
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    # Layer switching (1-4 for ground, obstacles, allies, foes)
                    layer_index = event.key - pygame.K_1
                    if layer_index < len(LAYER_NAMES):
                        current_layer = LAYER_NAMES[layer_index]
                        # Auto-select a default tile for this layer
                        ts = tilesets[active_tileset_index] if tilesets else None
                        if ts:
                            layer_palette = tile_categorizer.create_layer_palette(ts, current_layer)
                            if layer_palette:
                                selected_gid = ts.firstgid + layer_palette[0]
                elif pygame.K_5 <= event.key <= pygame.K_9:
                    # Quick-select nth visible tile in active tileset (5-9 to avoid conflict with layers)
                    n = event.key - pygame.K_5
                    ts = tilesets[active_tileset_index]
                    scroll = palette_scroll_by_ts.get(active_tileset_index, 0)
                    cols = max(1, (PALETTE_WIDTH - PALETTE_MARGIN * 2) // (PALETTE_TILE + PALETTE_MARGIN))
                    index = scroll * cols + n
                    if 0 <= index < ts.tilecount:
                        selected_gid = ts.firstgid + index
                elif event.key == pygame.K_h:
                    help_active = not help_active
                elif event.key == pygame.K_p:
                    tool = "PAINT"
                    rect_active = False
                elif event.key == pygame.K_r:
                    tool = "RECT"
                    rect_active = False
                elif event.key == pygame.K_f:
                    if event.mod & pygame.KMOD_CTRL:
                        # Ctrl+F is flood fill
                        tool = "FILL"
                        rect_active = False
                    else:
                        # F toggles sprite filter
                        show_all_sprites = not show_all_sprites
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # paint
                    mx, my = event.pos
                    if mx < grid_w:  # grid paint
                        x = mx // TILE_PIXELS
                        y = my // TILE_PIXELS
                        if tool == "PAINT":
                            tmpl.set(x, y, selected_gid, current_layer)
                        elif tool == "RECT":
                            rect_active = True
                            rect_start = (x, y)
                            rect_current = (x, y)
                        elif tool == "FILL":
                            flood_fill(tmpl, x, y, selected_gid, current_layer)
                    elif mx < grid_w + LAYER_PANEL_WIDTH:  # layer panel click
                        rel_x = mx - grid_w
                        rel_y = my
                        # Check layer button clicks
                        y_pos = 35
                        for i, layer_name in enumerate(LAYER_NAMES):
                            button_rect = pygame.Rect(
                                8, y_pos, LAYER_PANEL_WIDTH - 16, LAYER_BUTTON_HEIGHT
                            )
                            if button_rect.collidepoint(rel_x, rel_y):
                                # Check if clicking on visibility toggle (eye icon area)
                                eye_x = button_rect.right - 20
                                if rel_x > eye_x - 10:  # Clicking near eye icon
                                    # Toggle visibility
                                    layer = tmpl.get_layer(layer_name)
                                    layer.visible = not layer.visible
                                else:
                                    # Switch to this layer
                                    current_layer = layer_name
                                    # Auto-select a default tile for this layer
                                    ts = tilesets[active_tileset_index] if tilesets else None
                                    if ts:
                                        layer_palette = tile_categorizer.create_layer_palette(ts, current_layer)
                                        if layer_palette:
                                            selected_gid = ts.firstgid + layer_palette[0]
                                break
                            y_pos += LAYER_BUTTON_HEIGHT + LAYER_SPACING
                    else:  # palette click
                        rel_x = mx - grid_w - LAYER_PANEL_WIDTH
                        rel_y = my
                        # Tabs area  
                        tab_x = PALETTE_MARGIN
                        tab_y = 25  # Updated to match new tab position
                        tx = tab_x
                        clicked_tab = None
                        for i, ts in enumerate(tilesets):
                            t_surf = font.render(ts.name, True, (0, 0, 0))
                            tab_w = t_surf.get_width() + TAB_PAD_X * 2
                            tab_rect = pygame.Rect(tx, tab_y, tab_w, TAB_HEIGHT)
                            if tab_rect.collidepoint(rel_x, rel_y):
                                clicked_tab = i
                                break
                            tx += tab_w + TAB_SPACING
                        if clicked_tab is not None:
                            active_tileset_index = clicked_tab
                        else:
                            # Tile grid area - now using all sprites or layer-specific palette
                            start_y = tab_y + TAB_HEIGHT + PALETTE_MARGIN
                            if rel_y >= start_y:
                                ts = tilesets[active_tileset_index]
                                
                                # Choose palette based on filter setting
                                if show_all_sprites:
                                    sprite_palette = list(range(ts.tilecount))
                                else:
                                    sprite_palette = tile_categorizer.create_layer_palette(ts, current_layer)
                                    if not sprite_palette:
                                        sprite_palette = list(range(min(100, ts.tilecount)))
                                
                                cols = max(1, (PALETTE_WIDTH - PALETTE_MARGIN * 2) // (PALETTE_TILE + PALETTE_MARGIN))
                                rows_fit = max(1, (grid_h - start_y - PALETTE_MARGIN) // (PALETTE_TILE + PALETTE_MARGIN))
                                scroll = palette_scroll_by_ts.get(active_tileset_index, 0)
                                c = (rel_x - PALETTE_MARGIN) // (PALETTE_TILE + PALETTE_MARGIN)
                                r = (rel_y - start_y) // (PALETTE_TILE + PALETTE_MARGIN)
                                if 0 <= c < cols and 0 <= r < rows_fit:
                                    palette_index = scroll * cols + r * cols + c
                                    if 0 <= palette_index < len(sprite_palette):
                                        local_id = sprite_palette[palette_index]
                                        selected_gid = ts.firstgid + local_id
                elif event.button == 3:  # right click eyedropper on grid
                    mx, my = event.pos
                    if mx < grid_w:
                        x = mx // TILE_PIXELS
                        y = my // TILE_PIXELS
                        try:
                            picked = tmpl.get(x, y, current_layer)
                            if isinstance(picked, int):
                                selected_gid = picked
                        except (IndexError, KeyError):
                            pass
                elif event.button == 4:  # wheel up
                    mx, my = event.pos
                    if mx >= grid_w + LAYER_PANEL_WIDTH:
                        # Scroll active tileset up
                        scroll = palette_scroll_by_ts.get(active_tileset_index, 0)
                        palette_scroll_by_ts[active_tileset_index] = max(0, scroll - 1)
                elif event.button == 5:  # wheel down
                    mx, my = event.pos
                    if mx >= grid_w + LAYER_PANEL_WIDTH:
                        ts = tilesets[active_tileset_index]
                        
                        # Choose palette based on filter setting for scroll calculation
                        if show_all_sprites:
                            sprite_palette = list(range(ts.tilecount))
                        else:
                            sprite_palette = tile_categorizer.create_layer_palette(ts, current_layer)
                            if not sprite_palette:
                                sprite_palette = list(range(min(100, ts.tilecount)))
                        
                        cols = max(1, (PALETTE_WIDTH - PALETTE_MARGIN * 2) // (PALETTE_TILE + PALETTE_MARGIN))
                        rows_fit = max(1, (grid_h - (25 + TAB_HEIGHT + PALETTE_MARGIN) - PALETTE_MARGIN) // (PALETTE_TILE + PALETTE_MARGIN))
                        max_rows = (len(sprite_palette) + cols - 1) // cols
                        max_scroll = max(0, max_rows - rows_fit)
                        scroll = palette_scroll_by_ts.get(active_tileset_index, 0)
                        palette_scroll_by_ts[active_tileset_index] = min(max_scroll, scroll + 1)
            elif event.type == pygame.MOUSEMOTION:
                if rect_active and tool == "RECT":
                    mx, my = event.pos
                    if mx < grid_w:
                        rect_current = (max(0, min(tmpl.width - 1, mx // TILE_PIXELS)),
                                        max(0, min(tmpl.height - 1, my // TILE_PIXELS)))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and rect_active and tool == "RECT":
                    mx, my = event.pos
                    if mx < grid_w and rect_start is not None and rect_current is not None:
                        x1 = mx // TILE_PIXELS
                        y1 = my // TILE_PIXELS
                        x0, y0 = rect_start
                        fill_rectangle(tmpl, x0, y0, x1, y1, selected_gid, current_layer)
                    rect_active = False
                    rect_start = None
                    rect_current = None

        screen.fill((0, 0, 0))
        rect_preview = None
        if rect_active and rect_start is not None and rect_current is not None:
            x0, y0 = rect_start
            x1, y1 = rect_current
            rect_preview = (x0, y0, x1, y1)

        draw_grid(screen, tmpl, tilesets, font, selected_gid, tool, current_layer, grid_w, grid_h, rect_preview)
        draw_layer_panel(screen, grid_w, grid_h, tmpl, font, current_layer)
        draw_palette_tilesets(screen, grid_w + LAYER_PANEL_WIDTH, grid_h, tilesets, font, active_tileset_index, selected_gid, palette_scroll_by_ts, current_layer, show_all_sprites)
        if save_as_active:
            draw_save_modal()
        elif help_active:
            draw_help_overlay()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    w = 22
    h = 14
    path: Optional[Path] = None
    if len(sys.argv) >= 3:
        try:
            w = int(sys.argv[1])
            h = int(sys.argv[2])
        except ValueError:
            print("Width/height must be integers.")
    if len(sys.argv) >= 4:
        path = Path(sys.argv[3])
    editor_main(w, h, path)
