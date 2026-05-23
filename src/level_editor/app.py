"""
Minimal Pygame-based level editor.

Now tileset-driven: paint a grid of GIDs (global tile ids) from TSX tilesets
and save/load JSON templates that include tileset ordering for firstgid.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

import pygame

from .palette_model import PaletteModel
from .palette_ui import PalettePanel
from .tileset_loader import TilesetData
from .core.app_state import EditorState
from .core import bootstrap
from .core import commands
from .core import events
from .core import io as core_io
from .core import palette_controller
from .core import tileset_index as core_tilesets
from .core.io import log_ui_error
from .core.diagnostics import log_diagnostics
from .ui.draw import (
    draw_grid,
    draw_help_overlay,
    draw_layer_panel,
)
from .ui import modals


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
    "foes": (200, 100, 100),
}

def editor_main(width: int = 22, height: int = 14, template_path: Optional[Path] = None) -> None:
    pygame.init()
    # pytmx's pygame loader calls Surface.convert_alpha(), which requires an
    # active display surface. Create a tiny placeholder window now; we resize
    # it to the real editor dimensions once the template has been loaded.
    pygame.display.set_mode((1, 1))
    repo_root = Path(__file__).resolve().parents[2]
    default_tsx_dir = repo_root / "imgs" / "tiled_tilesets"
    tsx_paths = sorted(default_tsx_dir.glob("*.tsx"))

    tmpl, tsx_paths, tmx_gid_surfaces, parsed_map, current_path = bootstrap.load_or_create_template(
        template_path,
        tsx_paths,
        repo_root,
        width,
        height,
    )
    grid_w, grid_h, total_w = bootstrap.compute_dimensions(tmpl, TILE_PIXELS, LAYER_PANEL_WIDTH, PALETTE_WIDTH)
    screen = pygame.display.set_mode((total_w, grid_h))
    pygame.display.set_caption("Level Editor")
    font = pygame.font.SysFont(None, 20)
    if parsed_map:
        log_diagnostics(tmpl, parsed_map)

    tileset_cache: Dict[str, TilesetData] = {}
    tileset_index: List[tuple[str, TilesetData, int]] = []
    tileset_names: List[str] = []
    firstgid_map: Dict[str, int] = {}

    palette_model: Optional[PaletteModel] = None
    palette_panel: Optional[PalettePanel] = None

    state = EditorState(tmpl=tmpl, tileset_names=[])

    def apply_initial_selection() -> None:
        palette_controller.apply_initial_selection(state, palette_panel, palette_model, firstgid_map)

    def cycle_tileset(delta: int = 1) -> None:
        palette_controller.cycle_tileset(state, palette_model, palette_panel, tileset_names, firstgid_map, delta)

    def rebuild_palette() -> None:
        nonlocal palette_model, palette_panel, tileset_cache, tileset_index, tileset_names, firstgid_map
        palette_model, palette_panel, tileset_cache, tileset_index, tileset_names, firstgid_map = palette_controller.rebuild_palette(
            state,
            tmpl,
            tsx_paths,
            grid_w,
            grid_h,
            layer_panel_width=LAYER_PANEL_WIDTH,
            palette_width=PALETTE_WIDTH,
            tile_render_size=PALETTE_TILE,
            grid_cols=8,
            grid_rows=6,
            padding=PALETTE_MARGIN,
            gutter=max(2, PALETTE_MARGIN // 2),
            on_tileset_menu=lambda: cycle_tileset(1),
        )

    rebuild_palette()

    def save_to_path(path: Path) -> None:
        nonlocal current_path
        current_path = bootstrap.save_template(path, tmpl, tsx_paths, repo_root, tileset_index)
        state.save_input = str(current_path)

    def build_event_context() -> events.EventContext:
        return events.EventContext(
            tmpl=tmpl,
            palette_model=palette_model,
            palette_panel=palette_panel,
            tileset_index=tileset_index,
            tileset_names=tileset_names,
            firstgid_map=firstgid_map,
            current_path=current_path,
            grid_w=grid_w,
            grid_h=grid_h,
            total_w=total_w,
            tile_pixels=TILE_PIXELS,
            layer_panel_width=LAYER_PANEL_WIDTH,
            layer_button_height=LAYER_BUTTON_HEIGHT,
            layer_spacing=LAYER_SPACING,
            layer_names=LAYER_NAMES,
            refresh_load_files=refresh_load_files,
            perform_load=perform_load,
            apply_initial_selection=apply_initial_selection,
            save_template=save_to_path,
            log_error=log_ui_error,
        )

    state.save_input = str(current_path) if current_path is not None else "maps\\editor_templates\\template.json"

    def refresh_load_files() -> None:
        state.load_files = bootstrap.refresh_load_files()

    def perform_load(path: Path) -> None:
        nonlocal tmpl, tsx_paths, grid_w, grid_h, total_w, screen, current_path, tmx_gid_surfaces, parsed_map
        tmpl, tsx_paths, tmx_gid_surfaces, parsed_map, grid_w, grid_h, total_w, current_path = bootstrap.perform_load(
            path,
            TILE_PIXELS,
            LAYER_PANEL_WIDTH,
            PALETTE_WIDTH,
        )
        screen = pygame.display.set_mode((total_w, grid_h))
        state.save_input = str(current_path)
        rebuild_palette()
        log_diagnostics(tmpl, parsed_map)

    # Help overlay
    state.help_active = False

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            modals_active = state.save_as_active or state.load_active
            if palette_panel is not None and not modals_active:
                palette_panel.handle_event(event)

            ctx = build_event_context()
            running = events.handle_event(
                event,
                state,
                ctx,
                fill_rectangle=commands.fill_rectangle,
                flood_fill=commands.flood_fill,
            )
            if not running:
                break

        if not running:
            break

        palette_controller.sync_selected_gid_from_palette(state, palette_panel, firstgid_map)

        screen.fill((0, 0, 0))
        rect_preview = None
        if state.rect_active and state.rect_start is not None and state.rect_current is not None:
            x0, y0 = state.rect_start
            x1, y1 = state.rect_current
            rect_preview = (x0, y0, x1, y1)

        draw_grid(
            screen,
            tmpl,
            tileset_index,
            font,
            state.selected_gid,
            state.tool,
            state.current_layer,
            grid_w,
            grid_h,
            rect_preview,
            tmx_gid_surfaces,
            parsed_map,
            tile_pixels=TILE_PIXELS,
            layer_names=LAYER_NAMES,
            layer_colors=LAYER_COLORS,
            margin=MARGIN,
            tile_fetcher=core_tilesets.tile_for_gid,
        )
        draw_layer_panel(
            screen,
            grid_w,
            grid_h,
            tmpl,
            font,
            state.current_layer,
            layer_names=LAYER_NAMES,
            layer_colors=LAYER_COLORS,
            panel_width=LAYER_PANEL_WIDTH,
            button_height=LAYER_BUTTON_HEIGHT,
            layer_spacing=LAYER_SPACING,
        )
        if palette_panel is not None:
            palette_panel.draw(screen)
        if state.save_as_active:
            modals.draw_save_modal(screen, total_w, grid_h, font, state.save_input, state.save_message)
        elif state.load_active:
            modals.draw_load_modal(screen, total_w, grid_h, font, state.load_files, state.load_index, state.load_input, state.load_message)
        elif state.help_active:
            draw_help_overlay(screen, total_w, grid_h, font)
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
