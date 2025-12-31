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

from .map_template import MapTemplate
from .metadata import apply_metadata, load_metadata
from .palette_model import PaletteModel
from .palette_ui import PalettePanel, PaletteUIConfig
from .tileset_loader import TileEntry, TilesetData, load_tilesets


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


def build_tileset_index(tsx_paths: List[Path]) -> tuple[
    Dict[str, TilesetData],
    List[tuple[str, TilesetData, int]],
    Dict[str, int],
    List[str],
]:
    """Load tilesets, apply metadata, and compute firstgid ordering."""
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
    for tsx_path in tsx_paths:
        match = next(
            (data for data in cache.values() if data.info.path.resolve() == tsx_path.resolve()),
            None,
        )
        if match is None:
            continue
        name = match.info.name
        index.append((name, match, gid_cursor))
        names.append(name)
        firstgid_map[name] = gid_cursor
        gid_cursor += match.info.tile_count

    return cache, index, firstgid_map, names


def tile_for_gid(tileset_index: List[tuple[str, TilesetData, int]], gid: int) -> Optional[TileEntry]:
    """Return the TileEntry matching a global id, or None if not found."""
    for name, data, firstgid in tileset_index:
        end = firstgid + data.info.tile_count
        if firstgid <= gid < end:
            local_id = gid - firstgid
            if 0 <= local_id < len(data.tiles):
                return data.tiles[local_id]
    return None


def gid_for_tile(firstgid_map: Dict[str, int], tile: TileEntry) -> int:
    """Convert a TileEntry to its global id using firstgid ordering."""
    base = firstgid_map.get(tile.tileset_name)
    if base is None:
        return 0
    return base + tile.local_id


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
                        tile_entry = tile_for_gid(tileset_index, gid)
                        if tile_entry is not None:
                            surf = tile_entry.surface
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
    repo_root = Path(__file__).resolve().parents[2]
    default_tsx_dir = repo_root / "imgs" / "tiled_tilesets"
    tsx_paths = sorted(default_tsx_dir.glob("*.tsx"))

    current_path: Optional[Path] = template_path
    if template_path and template_path.exists():
        tmpl = MapTemplate.load_json(template_path)
        if tmpl.tilesets:
            tsx_paths = [(repo_root / p).resolve() for p in tmpl.tilesets]
        grid_w = tmpl.width * TILE_PIXELS
        grid_h = tmpl.height * TILE_PIXELS
        total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
        screen = pygame.display.set_mode((total_w, grid_h))
    else:
        tmpl = MapTemplate.create(
            width,
            height,
            fill=0,
            tilesets=[str(p.relative_to(repo_root)) for p in tsx_paths],
        )
        if current_path is None:
            current_path = Path("maps") / "editor_templates" / "template.json"

    tileset_cache: Dict[str, TilesetData] = {}
    tileset_index: List[tuple[str, TilesetData, int]] = []
    tileset_names: List[str] = []
    firstgid_map: Dict[str, int] = {}

    palette_model: Optional[PaletteModel] = None
    palette_panel: Optional[PalettePanel] = None
    active_tileset_index = 0
    selected_gid = 0

    def refresh_palette_panel() -> None:
        nonlocal palette_panel
        if palette_model is None:
            return
        palette_panel = PalettePanel(
            palette_model,
            pygame.Rect(grid_w + LAYER_PANEL_WIDTH, 0, PALETTE_WIDTH, grid_h),
            on_tileset_menu=lambda: cycle_tileset(1),
            config=PaletteUIConfig(
                tile_render_size=PALETTE_TILE,
                grid_cols=8,
                grid_rows=6,
                padding=PALETTE_MARGIN,
                gutter=max(2, PALETTE_MARGIN // 2),
            ),
        )

    def apply_initial_selection() -> None:
        nonlocal selected_gid
        if palette_model is None or palette_panel is None:
            return
        tiles = palette_model.page_tiles()
        if not tiles:
            return
        palette_panel.selected = tiles[0]
        selected_gid = gid_for_tile(firstgid_map, tiles[0])

    def cycle_tileset(delta: int = 1) -> None:
        nonlocal active_tileset_index
        if not tileset_names or palette_model is None:
            return
        active_tileset_index = (active_tileset_index + delta) % len(tileset_names)
        palette_model.set_tileset(tileset_names[active_tileset_index])
        if palette_panel is not None:
            palette_panel.selected = None
        apply_initial_selection()

    def rebuild_tilesets() -> None:
        nonlocal tileset_cache, tileset_index, tileset_names, firstgid_map, palette_model, active_tileset_index
        tileset_cache, tileset_index, firstgid_map, tileset_names = build_tileset_index(tsx_paths)
        palette_model = PaletteModel(tileset_cache)
        active_tileset_index = 0
        if tileset_names:
            palette_model.set_tileset(tileset_names[active_tileset_index])
        refresh_palette_panel()
        apply_initial_selection()

    rebuild_tilesets()

    current_layer = "ground"

    tool = "PAINT"
    rect_active = False
    rect_start: Optional[Tuple[int, int]] = None
    rect_current: Optional[Tuple[int, int]] = None

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

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if palette_panel is not None:
                palette_panel.handle_event(event)
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
                    if palette_panel is not None and getattr(palette_panel, "_active_filter", "none") != "none":
                        palette_panel._apply_filter("none")
                        continue
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
                        if tmpl.tilesets:
                            tsx_paths = [(repo_root / p).resolve() for p in tmpl.tilesets]
                        grid_w = tmpl.width * TILE_PIXELS
                        grid_h = tmpl.height * TILE_PIXELS
                        total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
                        screen = pygame.display.set_mode((total_w, grid_h))
                        print(f"Loaded template from {path}")
                        current_path = path
                        rebuild_tilesets()
                        refresh_palette_panel()
                        apply_initial_selection()
                elif pygame.K_1 <= event.key <= pygame.K_4:
                    # Layer switching (1-4 for ground, obstacles, allies, foes)
                    layer_index = event.key - pygame.K_1
                    if layer_index < len(LAYER_NAMES):
                        current_layer = LAYER_NAMES[layer_index]
                        apply_initial_selection()
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
                                    apply_initial_selection()
                                break
                            y_pos += LAYER_BUTTON_HEIGHT + LAYER_SPACING
                elif event.button == 3:  # right click eyedropper on grid
                    mx, my = event.pos
                    if mx < grid_w:
                        x = mx // TILE_PIXELS
                        y = my // TILE_PIXELS
                        try:
                            picked = tmpl.get(x, y, current_layer)
                            if isinstance(picked, int):
                                selected_gid = picked
                                tile_entry = tile_for_gid(tileset_index, picked)
                                if tile_entry is not None:
                                    if palette_model and palette_model.state.tileset_name != tile_entry.tileset_name:
                                        palette_model.set_tileset(tile_entry.tileset_name)
                                        if tile_entry.tileset_name in tileset_names:
                                            active_tileset_index = tileset_names.index(tile_entry.tileset_name)
                                    if palette_panel is not None:
                                        palette_panel.selected = tile_entry
                        except (IndexError, KeyError):
                            pass
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

            if palette_panel is not None and palette_panel.selected is not None:
                gid = gid_for_tile(firstgid_map, palette_panel.selected)
                if gid:
                    selected_gid = gid

        screen.fill((0, 0, 0))
        rect_preview = None
        if rect_active and rect_start is not None and rect_current is not None:
            x0, y0 = rect_start
            x1, y1 = rect_current
            rect_preview = (x0, y0, x1, y1)

        draw_grid(screen, tmpl, tileset_index, font, selected_gid, tool, current_layer, grid_w, grid_h, rect_preview)
        draw_layer_panel(screen, grid_w, grid_h, tmpl, font, current_layer)
        if palette_panel is not None:
            palette_panel.draw(screen)
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
