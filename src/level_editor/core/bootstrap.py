"""Bootstrap helpers for initializing editor templates and dimensions."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from src.services.tmx_loader_core import ParsedMap

from ..map_template import MapTemplate
from . import io as core_io


def load_or_create_template(
    template_path: Optional[Path],
    default_tsx_paths: list[Path],
    repo_root: Path,
    width: int,
    height: int,
) -> tuple[MapTemplate, list[Path], Optional[dict[int, object]], Optional[ParsedMap], Optional[Path]]:
    """Load a TMX/JSON template if present, else create a fresh one."""
    tsx_paths = default_tsx_paths
    current_path = template_path
    parsed_map: Optional[ParsedMap] = None
    tmx_gid_surfaces = None

    if template_path and template_path.exists():
        tmpl, tmx_gid_surfaces, parsed_map = core_io.load_template(template_path)
        if tmpl.tilesets:
            tsx_paths = core_io.resolve_tileset_paths(tmpl.tilesets, template_path.parent)
    else:
        tmpl = MapTemplate.create(
            width,
            height,
            fill=0,
            tilesets=core_io.persistable_tileset_strings(tsx_paths, repo_root),
        )
        if current_path is None:
            current_path = Path("maps") / "editor_templates" / "template.json"
    return tmpl, tsx_paths, tmx_gid_surfaces, parsed_map, current_path


def compute_dimensions(tmpl: MapTemplate, tile_pixels: int, layer_panel_width: int, palette_width: int) -> tuple[int, int, int]:
    grid_w = tmpl.width * tile_pixels
    grid_h = tmpl.height * tile_pixels
    total_w = grid_w + layer_panel_width + palette_width
    return grid_w, grid_h, total_w


def refresh_load_files(base_dirs: Optional[list[Path]] = None, exts: Optional[set[str]] = None) -> list[Path]:
    base_dirs = base_dirs or [Path("maps") / "editor_templates", Path("maps")]
    exts = exts or {".json", ".tmx"}
    candidates: list[Path] = []
    for base in base_dirs:
        if base.exists():
            for p in sorted(base.rglob("*")):
                if p.is_file() and p.suffix.lower() in exts:
                    candidates.append(p)
    return candidates


def perform_load(path: Path, tile_pixels: int, layer_panel_width: int, palette_width: int):
    tmpl, tmx_gid_surfaces, parsed_map = core_io.load_template(path)
    tsx_paths = core_io.resolve_tileset_paths(tmpl.tilesets, path.parent) if tmpl.tilesets else []
    grid_w, grid_h, total_w = compute_dimensions(tmpl, tile_pixels, layer_panel_width, palette_width)
    return tmpl, tsx_paths, tmx_gid_surfaces, parsed_map, grid_w, grid_h, total_w, path


def save_template(path: Path, tmpl: MapTemplate, tsx_paths: list[Path], repo_root: Path, tileset_index) -> Path:
    tmpl.tilesets = core_io.persistable_tileset_strings(tsx_paths, repo_root)
    tmpl.tileset_firstgids = [fg for _, _, fg in tileset_index]
    core_io.save_template(tmpl, path, tileset_index, tsx_paths)
    return path
