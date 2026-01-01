"""
Minimal Pygame-based level editor.

Now tileset-driven: paint a grid of GIDs (global tile ids) from TSX tilesets
and save/load JSON templates that include tileset ordering for firstgid.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pygame
import pytmx

from src.services.tmx_loader_core import ParsedMap, parse_tmx

from .map_template import MapTemplate
from .metadata import apply_metadata, load_metadata
from .palette_model import PaletteModel
from .palette_ui import PalettePanel, PaletteUIConfig
from .tileset_loader import TileEntry, TilesetData, load_tilesets


TILE_PIXELS = 48  # Match game TILE_SIZE for visual parity
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
LAYER_NAMES = ["ground", "obstacles"]  # Align with game tile layers
LAYER_COLORS = {
    "ground": (100, 150, 100),
    "obstacles": (150, 100, 100),
    "allies": (100, 100, 200),
    "foes": (200, 100, 100)
}


def build_tileset_index(tsx_paths: List[Path], explicit_firstgids: Optional[List[int]] = None) -> tuple[
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


def log_ui_error(message: str, exc: Optional[Exception] = None) -> None:
    """Log UI-facing errors to stderr so they are visible in the terminal."""
    if exc is not None:
        print(f"[editor][error] {message}: {exc}", file=sys.stderr)
        traceback.print_exception(exc, file=sys.stderr)
    else:
        print(f"[editor][error] {message}", file=sys.stderr)


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
                # pytmx can raise if images array is sparse; skip missing gids
                continue
            if surf is None:
                continue
            # pytmx may return (Surface, duration) for animations
            if isinstance(surf, tuple) and surf and hasattr(surf[0], "copy"):
                surf = surf[0]
            if hasattr(surf, "copy"):
                surfaces[gid] = surf.copy()
    print(f"[editor] TMX gid surfaces built: {len(surfaces)} entries")
    return surfaces


def tile_for_gid(
    tileset_index: List[tuple[str, TilesetData, int]],
    gid: int,
    tmx_gid_surfaces: Optional[Dict[int, pygame.Surface]] = None,
) -> Optional[TileEntry | pygame.Surface]:
    """Return a TileEntry or surface for a gid, preferring TMX surfaces if provided."""
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
    tmx_gid_surfaces: Optional[Dict[int, pygame.Surface]] = None,
    parsed_map: Optional[ParsedMap] = None,
) -> None:
    """Draw the editable tile grid on the left side of the window."""
    # Background checker for empty cells
    checker_a = (40, 40, 44)
    checker_b = (48, 48, 52)
    
    # Diagnostics
    missing_gid_once: Dict[int, bool] = {}
    layer_stats: Dict[str, Dict[str, int]] = {ln: {"nz": 0, "min": 0, "max": 0} for ln in LAYER_NAMES}

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
                        st = layer_stats[layer_name]
                        st["nz"] += 1
                        st["min"] = gid if st["min"] == 0 else min(st["min"], gid)
                        st["max"] = max(st["max"], gid)
                        surfaces = parsed_map.gid_surfaces if parsed_map is not None else tmx_gid_surfaces
                        tile_entry = tile_for_gid(tileset_index, gid, surfaces)
                        if isinstance(tile_entry, pygame.Surface):
                            surf = tile_entry
                        elif tile_entry is not None:
                            surf = tile_entry.surface
                        else:
                            surf = None
                        if surf is not None:
                            if surf.get_width() != TILE_PIXELS or surf.get_height() != TILE_PIXELS:
                                surf = pygame.transform.smoothscale(surf, (TILE_PIXELS, TILE_PIXELS))
                            screen.blit(surf, rect)
                        else:
                            pygame.draw.rect(screen, (80, 80, 80), rect)
                            if gid not in missing_gid_once:
                                missing_gid_once[gid] = True
            
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

    # Render object layers similar to game (dynamic_data, events) using parsed map data
    if parsed_map is not None:
        scale_x = TILE_PIXELS / max(1, parsed_map.tilewidth)
        scale_y = TILE_PIXELS / max(1, parsed_map.tileheight)
        for lname in ("dynamic_data", "events"):
            olayer = parsed_map.object_layers.get(lname)
            if olayer is None:
                continue
            for obj in getattr(olayer, "objects", []) or []:
                surf = obj.image
                if surf is None:
                    continue
                if surf.get_width() != TILE_PIXELS or surf.get_height() != TILE_PIXELS:
                    surf = pygame.transform.smoothscale(surf, (TILE_PIXELS, TILE_PIXELS))
                screen.blit(surf, (int(obj.x * scale_x), int(obj.y * scale_y)))


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

    def resolve_tileset_paths(raw_paths: List[str], base: Path) -> List[Path]:
        resolved: List[Path] = []
        for p in raw_paths:
            candidate = Path(p)
            if candidate.suffix.lower() != ".tsx":
                print(f"[editor] Ignoring non-TSX tileset path from template: {candidate}")
                continue
            if not candidate.is_absolute():
                candidate = (base / candidate).resolve()
            else:
                candidate = candidate.resolve()
            resolved.append(candidate)
        return resolved

    current_path: Optional[Path] = template_path
    parsed_map: Optional[ParsedMap] = None
    if template_path and template_path.exists():
        if template_path.suffix.lower() == ".tmx":
            parsed_map = parse_tmx(template_path)
            tmpl = MapTemplate.load_tmx(template_path)
            tmx_gid_surfaces = parsed_map.gid_surfaces
        else:
            tmpl = MapTemplate.load_json(template_path)
            tmx_gid_surfaces = None
        if tmpl.tilesets:
            tsx_paths = resolve_tileset_paths(tmpl.tilesets, template_path.parent)
        grid_w = tmpl.width * TILE_PIXELS
        grid_h = tmpl.height * TILE_PIXELS
        total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
        screen = pygame.display.set_mode((total_w, grid_h))
        log_diagnostics(tmpl, parsed_map)
    else:
        tmpl = MapTemplate.create(
            width,
            height,
            fill=0,
            tilesets=[str(p.relative_to(repo_root)) for p in tsx_paths],
        )
        if current_path is None:
            current_path = Path("maps") / "editor_templates" / "template.json"
        tmx_gid_surfaces = None
        parsed_map = None

    tileset_cache: Dict[str, TilesetData] = {}
    tileset_index: List[tuple[str, TilesetData, int]] = []
    tileset_names: List[str] = []
    firstgid_map: Dict[str, int] = {}

    def persistable_tileset_strings(paths: List[Path]) -> List[str]:
        result: List[str] = []
        for p in paths:
            try:
                result.append(str(p.relative_to(repo_root)))
            except ValueError:
                result.append(str(p))
        return result

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
        explicit_fg = getattr(tmpl, "tileset_firstgids", None)
        if explicit_fg and len(explicit_fg) != len(tsx_paths):
            print(
                f"[editor] Warning: tileset_firstgids length ({len(explicit_fg)}) does not match tilesets ({len(tsx_paths)}); falling back to computed firstgid order"
            )
        tileset_cache, tileset_index, firstgid_map, tileset_names = build_tileset_index(tsx_paths, explicit_fg)
        print("[editor] Tileset order:", tileset_names)
        print("[editor] Firstgid map:", firstgid_map)
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

    load_active = False
    load_input = ""
    load_message = ""
    load_files: List[Path] = []
    load_index = 0

    def refresh_load_files() -> None:
        nonlocal load_files
        candidates = []
        base_dirs = [Path("maps") / "editor_templates", Path("maps")]
        exts = {".json", ".tmx"}
        for base in base_dirs:
            if base.exists():
                for p in sorted(base.rglob("*")):
                    if p.is_file() and p.suffix.lower() in exts:
                        candidates.append(p)
        load_files = candidates

    def draw_load_modal() -> None:
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

        # File list viewport
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

        # Input box showing current selection
        input_rect = pygame.Rect(modal_x + 12, modal_y + modal_h - 32, modal_w - 24, 24)
        pygame.draw.rect(screen, (18, 18, 18), input_rect)
        pygame.draw.rect(screen, (120, 120, 120), input_rect, 1)
        display_text = load_input or (str(load_files[load_index]) if load_files else "")
        text_surf = font.render(display_text, True, (240, 240, 240))
        screen.blit(text_surf, (input_rect.x + 6, input_rect.y + 4))

        if load_message:
            msg = font.render(load_message, True, (255, 200, 120))
            screen.blit(msg, (modal_x + 12, modal_y + modal_h - 56))

    def perform_load(path: Path) -> None:
        nonlocal tmpl, tsx_paths, grid_w, grid_h, total_w, screen, current_path, tmx_gid_surfaces, parsed_map
        if path.suffix.lower() == ".tmx":
            parsed_map = parse_tmx(path)
            tmpl = MapTemplate.load_tmx(path)
            tmx_gid_surfaces = parsed_map.gid_surfaces
        else:
            tmpl = MapTemplate.load_json(path)
            tmx_gid_surfaces = None
            parsed_map = None
        if tmpl.tilesets:
            tsx_paths = resolve_tileset_paths(tmpl.tilesets, path.parent)
        grid_w = tmpl.width * TILE_PIXELS
        grid_h = tmpl.height * TILE_PIXELS
        total_w = grid_w + LAYER_PANEL_WIDTH + PALETTE_WIDTH
        screen = pygame.display.set_mode((total_w, grid_h))
        current_path = path
        rebuild_tilesets()
        refresh_palette_panel()
        apply_initial_selection()
        log_diagnostics(tmpl, parsed_map)

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
            modals_active = save_as_active or load_active
            if palette_panel is not None and not modals_active:
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
                            if candidate.suffix == "":
                                candidate = candidate.with_suffix(".json")
                            ext = candidate.suffix.lower()
                            # Persist tileset order for reproducible firstgid
                            tmpl.tilesets = persistable_tileset_strings(tsx_paths)
                            tmpl.tileset_firstgids = [fg for _, _, fg in tileset_index]
                            if ext == ".tmx":
                                tmpl.save_tmx(
                                    candidate,
                                    tileset_index,
                                    tsx_paths,
                                    tile_width=tmpl.tile_width,
                                    tile_height=tmpl.tile_height,
                                )
                            else:
                                tmpl.save_json(candidate)
                            current_path = candidate
                            save_message = f"Saved to {candidate}"
                            save_as_active = False
                        except Exception as e:
                            save_message = f"Save failed: {e}"
                            log_ui_error("Save failed", e)
                    elif event.key == pygame.K_BACKSPACE:
                        save_input = save_input[:-1]
                    else:
                        # Append printable characters
                        if event.unicode and 31 < ord(event.unicode) < 127:
                            save_input += event.unicode
                    continue
                if load_active:
                    if event.key == pygame.K_ESCAPE:
                        load_active = False
                        load_message = ""
                    elif event.key == pygame.K_RETURN:
                        target = Path(load_input.strip()) if load_input.strip() else (load_files[load_index] if load_files else None)
                        if target:
                            try:
                                perform_load(target)
                                load_message = f"Loaded {target}"
                                load_active = False
                            except Exception as e:
                                load_message = f"Load failed: {e}"
                                log_ui_error("Load failed", e)
                    elif event.key == pygame.K_BACKSPACE:
                        load_input = load_input[:-1]
                    elif event.key == pygame.K_UP:
                        if load_files:
                            load_index = max(0, load_index - 1)
                    elif event.key == pygame.K_DOWN:
                        if load_files:
                            load_index = min(len(load_files) - 1, load_index + 1)
                    else:
                        if event.unicode and 31 < ord(event.unicode) < 127:
                            load_input += event.unicode
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
                        ext = path.suffix.lower()
                        tmpl.tilesets = persistable_tileset_strings(tsx_paths)
                        tmpl.tileset_firstgids = [fg for _, _, fg in tileset_index]
                        if ext == ".tmx":
                            tmpl.save_tmx(
                                path,
                                tileset_index,
                                tsx_paths,
                                tile_width=tmpl.tile_width,
                                tile_height=tmpl.tile_height,
                            )
                        else:
                            tmpl.save_json(path)
                        print(f"Saved template to {path}")
                    else:
                        # Backwards compat: plain S also saves to current path
                        path = current_path or (Path("maps") / "editor_templates" / "template.json")
                        ext = path.suffix.lower()
                        tmpl.tilesets = persistable_tileset_strings(tsx_paths)
                        tmpl.tileset_firstgids = [fg for _, _, fg in tileset_index]
                        if ext == ".tmx":
                            tmpl.save_tmx(
                                path,
                                tileset_index,
                                tsx_paths,
                                tile_width=tmpl.tile_width,
                                tile_height=tmpl.tile_height,
                            )
                        else:
                            tmpl.save_json(path)
                        print(f"Saved template to {path}")
                elif event.key == pygame.K_F2:
                    # F2 opens Save As modal
                    save_as_active = True
                    save_message = ""
                    save_input = str(current_path) if current_path else "maps\\editor_templates\\template.json"
                elif event.key == pygame.K_l:
                    if load_active:
                        load_active = False
                        load_message = ""
                    else:
                        load_active = True
                        load_input = ""
                        load_message = ""
                        refresh_load_files()
                        load_index = 0
                        if load_files:
                            load_index = min(load_index, len(load_files) - 1)
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
                if load_active:
                    mx, my = event.pos
                    # Hit test list area of modal
                    modal_w = min(760, total_w - 40)
                    modal_h = min(420, grid_h - 40)
                    modal_x = (total_w - modal_w) // 2
                    modal_y = (grid_h - modal_h) // 2
                    list_top = modal_y + 40
                    list_h = modal_h - 80
                    item_h = 22
                    if modal_x <= mx <= modal_x + modal_w and list_top <= my <= list_top + list_h:
                        visible = list_h // item_h
                        start = max(0, load_index - visible + 1) if load_index >= visible else 0
                        end = min(len(load_files), start + visible)
                        idx = start + (my - list_top) // item_h
                        if start <= idx < end:
                            load_index = idx
                            load_input = str(load_files[load_index]) if load_files else load_input
                    elif modal_x <= mx <= modal_x + modal_w and modal_y <= my <= modal_y + modal_h:
                        # Click outside list but inside modal does nothing
                        pass
                    else:
                        # Click outside modal closes it
                        load_active = False
                    continue
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

        draw_grid(screen, tmpl, tileset_index, font, selected_gid, tool, current_layer, grid_w, grid_h, rect_preview, tmx_gid_surfaces, parsed_map)
        draw_layer_panel(screen, grid_w, grid_h, tmpl, font, current_layer)
        if palette_panel is not None:
            palette_panel.draw(screen)
        if save_as_active:
            draw_save_modal()
        elif load_active:
            draw_load_modal()
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
