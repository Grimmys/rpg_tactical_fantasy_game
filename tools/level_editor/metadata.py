"""Metadata loader/applier for tilesets.

Allows editor-only categorization and per-tile properties without editing TSX.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Set

from apps.level_editor.tileset_loader import TilesetData

Metadata = Dict[str, dict]


def _expand_ids(id_entry) -> List[int]:
    # Accept single ints or [start, end] inclusive ranges
    if isinstance(id_entry, int):
        return [id_entry]
    if isinstance(id_entry, list) and len(id_entry) == 2:
        start, end = id_entry
        return list(range(int(start), int(end) + 1))
    return []


def load_metadata(path: Path) -> Metadata:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def apply_metadata(cache: Dict[str, TilesetData], metadata: Metadata) -> None:
    """Mutates the tileset cache, overlaying properties/categories from metadata."""
    for tileset_name, meta in metadata.items():
        if tileset_name not in cache:
            continue
        tileset = cache[tileset_name]

        # Build category mapping per tile id
        cats_by_id: Dict[int, Set[str]] = {}
        for cat in meta.get("categories", []):
            cat_name = cat.get("name")
            if not cat_name:
                continue
            for id_entry in cat.get("ids", []):
                for tid in _expand_ids(id_entry):
                    cats_by_id.setdefault(tid, set()).add(cat_name)

        # Build property mapping per tile id
        props_meta = meta.get("properties", {})
        props_by_id: Dict[int, Dict[str, str]] = {
            int(tid): {k: str(v) for k, v in props.items()} for tid, props in props_meta.items()
        }

        for tile in tileset.tiles:
            if tile.local_id in props_by_id:
                tile.properties.update(props_by_id[tile.local_id])
            if tile.local_id in cats_by_id:
                tile.properties["category"] = ",".join(sorted(cats_by_id[tile.local_id]))
