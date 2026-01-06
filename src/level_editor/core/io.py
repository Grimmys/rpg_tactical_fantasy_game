"""Save/load helpers for the editor."""
from __future__ import annotations

import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..map_template import MapTemplate
from ..tileset_loader import TilesetData


def persistable_tileset_strings(tsx_paths: List[Path], repo_root: Path) -> List[str]:
    result: List[str] = []
    for p in tsx_paths:
        try:
            result.append(str(p.relative_to(repo_root)))
        except ValueError:
            result.append(str(p))
    return result


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


def log_ui_error(message: str, exc: Optional[Exception] = None) -> None:
    """Log UI-facing errors to stderr/stdout for visibility."""
    if exc is not None:
        print(f"[editor][error] {message}: {exc}")
        traceback.print_exception(exc)
    else:
        print(f"[editor][error] {message}")


def save_template(
    tmpl: MapTemplate,
    path: Path,
    tileset_index: List[tuple[str, TilesetData, int]],
    tsx_paths: List[Path],
) -> None:
    ext = path.suffix.lower()
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


def load_template(path: Path) -> Tuple[MapTemplate, Optional[Dict[int, object]], Optional[object]]:
    from src.services.tmx_loader_core import parse_tmx

    tmx_gid_surfaces = None
    parsed_map = None
    if path.suffix.lower() == ".tmx":
        parsed_map = parse_tmx(path)
        tmpl = MapTemplate.load_tmx(path)
        tmx_gid_surfaces = parsed_map.gid_surfaces
    else:
        tmpl = MapTemplate.load_json(path)
    return tmpl, tmx_gid_surfaces, parsed_map
