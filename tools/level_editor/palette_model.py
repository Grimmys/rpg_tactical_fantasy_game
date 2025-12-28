"""Palette model for paging and filtering tiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from apps.level_editor.tileset_loader import TileEntry, TilesetData

FilterFn = Callable[[TileEntry], bool]


@dataclass
class PaletteState:
    tileset_name: Optional[str] = None
    page_size: int = 25
    page_index: int = 0
    filter_fn: Optional[FilterFn] = None


@dataclass
class PaletteModel:
    tilesets: Dict[str, TilesetData]
    state: PaletteState = field(default_factory=PaletteState)

    def set_tileset(self, name: str) -> None:
        if name not in self.tilesets:
            raise ValueError(f"Unknown tileset: {name}")
        self.state.tileset_name = name
        self.state.page_index = 0

    def set_filter(self, predicate: Optional[FilterFn]) -> None:
        self.state.filter_fn = predicate
        self.state.page_index = 0

    def set_page(self, index: int) -> None:
        self.state.page_index = max(0, min(index, self.page_count - 1))

    @property
    def active_tiles(self) -> List[TileEntry]:
        if not self.state.tileset_name:
            return []
        tiles = self.tilesets[self.state.tileset_name].tiles
        if self.state.filter_fn:
            tiles = [t for t in tiles if self.state.filter_fn(t)]
        return tiles

    @property
    def page_count(self) -> int:
        if not self.active_tiles:
            return 0
        total = len(self.active_tiles)
        return (total + self.state.page_size - 1) // self.state.page_size

    def page_tiles(self) -> List[TileEntry]:
        start = self.state.page_index * self.state.page_size
        end = start + self.state.page_size
        return self.active_tiles[start:end]

    def next_page(self) -> None:
        if self.state.page_index + 1 < self.page_count:
            self.state.page_index += 1

    def prev_page(self) -> None:
        if self.state.page_index > 0:
            self.state.page_index -= 1


def property_filter(key: str, value: Optional[str] = None) -> FilterFn:
    def _pred(tile: TileEntry) -> bool:
        if key not in tile.properties:
            return False
        if value is None:
            return True
        return tile.properties.get(key) == value

    return _pred


def has_properties_filter() -> FilterFn:
    return lambda tile: bool(tile.properties)


def animated_filter() -> FilterFn:
    return lambda tile: tile.is_animated


def category_filter(category: str) -> FilterFn:
    category_lower = category.lower()

    def _pred(tile: TileEntry) -> bool:
        cat_value = tile.properties.get("category", "")
        return any(part.strip().lower() == category_lower for part in cat_value.split(",")) if cat_value else False

    return _pred
