"""
Tile types model and loader for the level editor and gameplay.

Defines:
 - TileType: immutable record with id, name, walk_cost, defense, color_hex
 - TileTypes: container with lookups by id/name
 - load_tile_types(): reads data/tile_types.xml using lxml
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from lxml import etree


@dataclass(frozen=True)
class TileType:
    id: int
    name: str
    walk_cost: int
    defense: int
    color_hex: str

    def color_rgb(self) -> tuple[int, int, int]:
        s = self.color_hex.strip().lstrip("#")
        try:
            if len(s) == 3:
                r, g, b = (int(c * 2, 16) for c in s)
            elif len(s) == 6:
                r = int(s[0:2], 16)
                g = int(s[2:4], 16)
                b = int(s[4:6], 16)
            else:
                raise ValueError
            return (r, g, b)
        except Exception:
            return (255, 255, 255)


class TileTypes:
    def __init__(self, types: Iterable[TileType]) -> None:
        self._by_id: Dict[int, TileType] = {t.id: t for t in types}
        self._by_name: Dict[str, TileType] = {t.name: t for t in types}

    def get(self, tile_type_id: int) -> Optional[TileType]:
        return self._by_id.get(tile_type_id)

    def by_name(self, name: str) -> Optional[TileType]:
        return self._by_name.get(name)

    def all(self) -> list[TileType]:
        return list(self._by_id.values())


def _text_or_default(el: etree._Element, path: str, default: str) -> str:
    node = el.find(path)
    return node.text.strip() if node is not None and node.text is not None else default


def load_tile_types(xml_path: Optional[Path] = None) -> TileTypes:
    """Load tile types from data/tile_types.xml, resolving path from repo root by default."""
    if xml_path is None:
        xml_path = Path(__file__).resolve().parents[2] / "data" / "tile_types.xml"

    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    types: list[TileType] = []
    for el in root.findall("tiletype"):
        id_attr = el.get("id")
        name_attr = el.get("name")
        if not id_attr or not name_attr:
            continue
        try:
            t_id = int(id_attr)
        except ValueError:
            continue

        walk_cost = int(_text_or_default(el, "walk_cost", "1"))
        defense = int(_text_or_default(el, "def", "0"))
        color = _text_or_default(el, "color", "#FFFFFF")

        types.append(TileType(t_id, name_attr, walk_cost, defense, color))

    return TileTypes(types)
