"""Ad-hoc runnable demo for the palette panel.

Usage:
    uv run python apps/level_editor/palette_demo.py

Notes:
- Picks the first discovered tileset if none is specified.
- Mouse wheel or PageUp/PageDown to page.
- Click a tile to select/start a drag payload; hold Shift to mark stamp mode.
- Click the tileset bar to trigger a placeholder callback.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

# Ensure repo root is on sys.path when running as a script.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.level_editor.metadata import apply_metadata, load_metadata
from apps.level_editor.palette_model import PaletteModel
from apps.level_editor.palette_ui import PalettePanel
from apps.level_editor.tileset_loader import discover_tilesets, load_tilesets


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((640, 620))
    pygame.display.set_caption("Palette Demo")

    search_roots = [Path("maps"), Path("imgs/tiled_tilesets")]
    tileset_paths = []
    for root in search_roots:
        tileset_paths.extend(discover_tilesets(root))

    if not tileset_paths:
        print("No .tsx tilesets found under: " + ", ".join(str(r) for r in search_roots), file=sys.stderr)
        return

    cache = load_tilesets(tileset_paths)

    # Apply optional editor metadata
    meta_path = Path("apps/level_editor/tileset_metadata.json")
    metadata = load_metadata(meta_path)
    if metadata:
        apply_metadata(cache, metadata)
        print(f"Applied metadata from {meta_path}")
    else:
        print(f"No metadata file found at {meta_path}; using raw TSX data")
    model = PaletteModel(cache)
    tileset_names = list(cache.keys())
    tileset_index = 0
    model.set_tileset(tileset_names[tileset_index])
    print("Loaded tilesets:", tileset_names)

    panel_rect = pygame.Rect(10, 30, 620, 560)
    panel = PalettePanel(model, panel_rect, on_tileset_menu=lambda: print("Tileset menu placeholder"))

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFTBRACKET:  # '[' cycles backward
                    tileset_index = (tileset_index - 1) % len(tileset_names)
                    model.set_tileset(tileset_names[tileset_index])
                elif event.key == pygame.K_RIGHTBRACKET:  # ']' cycles forward
                    tileset_index = (tileset_index + 1) % len(tileset_names)
                    model.set_tileset(tileset_names[tileset_index])
            panel.handle_event(event)

        screen.fill((12, 12, 12))
        panel.draw(screen)

        # Draw current tileset label at top-left
        label = f"Tileset: {tileset_names[tileset_index]}  ([/]=cycle, category buttons click, Esc=all)"
        font = pygame.font.SysFont(None, 18)
        text = font.render(label, True, (230, 230, 230))
        screen.blit(text, (14, 6))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Last drag payload:", panel.drag_payload)


if __name__ == "__main__":
    main()
