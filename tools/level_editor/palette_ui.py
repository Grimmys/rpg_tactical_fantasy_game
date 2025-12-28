"""Dockable palette panel for tileset browsing and drag/drop selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

import pygame

from apps.level_editor.palette_model import PaletteModel, TileEntry, category_filter


@dataclass
class DragPayload:
    tileset_name: str
    local_id: int
    surface: pygame.Surface
    stamp_mode: bool = False


@dataclass
class PaletteUIConfig:
    tile_render_size: int = 48
    grid_cols: int = 10
    grid_rows: int = 6
    padding: int = 8
    gutter: int = 4
    bg_color: Tuple[int, int, int] = (30, 30, 30)
    grid_color: Tuple[int, int, int] = (45, 45, 45)
    border_color: Tuple[int, int, int] = (70, 70, 70)
    text_color: Tuple[int, int, int] = (220, 220, 220)
    font_name: Optional[str] = None
    font_size: int = 14


class PalettePanel:
    def __init__(
        self,
        model: PaletteModel,
        rect: pygame.Rect,
        on_tileset_menu: Optional[Callable[[], None]] = None,
        config: PaletteUIConfig = PaletteUIConfig(),
    ) -> None:
        self.model = model
        self.rect = rect
        self.config = config
        self.on_tileset_menu = on_tileset_menu

        # Align model page size with visible grid capacity
        self.model.state.page_size = self.config.grid_cols * self.config.grid_rows

        self.font = pygame.font.SysFont(self.config.font_name, self.config.font_size)
        self.selected: Optional[TileEntry] = None
        self.hovered: Optional[int] = None
        self.drag_payload: Optional[DragPayload] = None

        # UI elements
        self._tileset_button = pygame.Rect(
            self.rect.x + self.config.padding,
            self.rect.y + self.config.padding,
            self.rect.width - 2 * self.config.padding,
            24,
        )

        # Filter buttons: None + dynamic categories from metadata
        # Category dropdown
        self._active_filter: str = "none"
        self._categories: List[str] = []
        self._dropdown_rect = pygame.Rect(
            self.rect.x + self.config.padding,
            self.rect.y + self.config.padding + self._tileset_button.height + self.config.gutter,
            140,
            24,
        )
        self._dropdown_expanded: bool = False
        self._dropdown_scroll: int = 0
        self._max_visible_items: int = 10
        self._prev_button = pygame.Rect(
            self.rect.x + self.config.padding,
            self.rect.bottom - self.config.padding - 24,
            50,
            24,
        )
        self._next_button = pygame.Rect(
            self.rect.x + self.rect.width - self.config.padding - 50,
            self.rect.bottom - self.config.padding - 24,
            50,
            24,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self._tileset_button.collidepoint(event.pos) and self.on_tileset_menu:
                    self.on_tileset_menu()
                    return
                if self._dropdown_rect.collidepoint(event.pos):
                    self._dropdown_expanded = not self._dropdown_expanded
                    return
                if self._dropdown_expanded:
                    clicked = self._dropdown_item_at(event.pos)
                    if clicked is not None:
                        self._apply_filter(clicked)
                        self._dropdown_expanded = False
                        return
                if self._prev_button.collidepoint(event.pos):
                    self.model.prev_page()
                    return
                if self._next_button.collidepoint(event.pos):
                    self.model.next_page()
                    return
                tile_index = self._tile_index_at(event.pos)
                if tile_index is not None:
                    tiles = self.model.page_tiles()
                    if tile_index < len(tiles):
                        tile = tiles[tile_index]
                        self.selected = tile
                        stamp = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
                        self.drag_payload = DragPayload(
                            tileset_name=tile.tileset_name,
                            local_id=tile.local_id,
                            surface=tile.surface,
                            stamp_mode=stamp,
                        )
            elif event.button == 4:
                if self._dropdown_expanded:
                    self._scroll_dropdown(-1)
                else:
                    self.model.prev_page()
            elif event.button == 5:
                if self._dropdown_expanded:
                    self._scroll_dropdown(1)
                else:
                    self.model.next_page()

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button in (1, 3):
                self.drag_payload = None

        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self._tile_index_at(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                self.model.prev_page()
            elif event.key == pygame.K_PAGEDOWN:
                self.model.next_page()
            elif event.key == pygame.K_ESCAPE:
                self._apply_filter("none")
            elif event.key == pygame.K_COMMA:  # cycle categories backward
                self._cycle_category(-1)
            elif event.key == pygame.K_PERIOD:  # cycle categories forward
                self._cycle_category(1)

    def _tile_index_at(self, pos: Tuple[int, int]) -> Optional[int]:
        grid_origin_y = self._grid_origin_y
        grid_origin_x = self.rect.x + self.config.padding
        tw = self.config.tile_render_size
        gh = self.config.gutter
        for row in range(self.config.grid_rows):
            for col in range(self.config.grid_cols):
                idx = row * self.config.grid_cols + col
                x = grid_origin_x + col * (tw + gh)
                y = grid_origin_y + row * (tw + gh)
                cell = pygame.Rect(x, y, tw, tw)
                if cell.collidepoint(pos):
                    return idx
        return None

    @property
    def _grid_origin_y(self) -> int:
        # Tileset bar + gutter + dropdown height + gutter
        fb_height = self._dropdown_rect.height
        return (
            self.rect.y
            + self.config.padding
            + self._tileset_button.height
            + self.config.gutter
            + fb_height
            + self.config.gutter
        )

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.config.bg_color, self.rect)
        pygame.draw.rect(surface, self.config.border_color, self.rect, 1)

        self._draw_tileset_bar(surface)
        self._ensure_categories()
        self._draw_grid(surface)
        self._draw_paging(surface)
        # Draw dropdown after grid/paging so the expanded list overlays tiles
        self._draw_dropdown(surface)
        self._draw_tooltip(surface)

    def _draw_tileset_bar(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.config.grid_color, self._tileset_button)
        pygame.draw.rect(surface, self.config.border_color, self._tileset_button, 1)
        name = self.model.state.tileset_name or "Select tileset"
        text = self.font.render(name, True, self.config.text_color)
        surface.blit(
            text,
            (
                self._tileset_button.x + 6,
                self._tileset_button.y + (self._tileset_button.height - text.get_height()) // 2,
            ),
        )

    def _draw_dropdown(self, surface: pygame.Surface) -> None:
        # Header
        pygame.draw.rect(surface, self.config.grid_color, self._dropdown_rect)
        pygame.draw.rect(surface, self.config.border_color, self._dropdown_rect, 1)
        label = "All" if self._active_filter == "none" else self._active_filter.capitalize()
        text = self.font.render(label, True, self.config.text_color)
        surface.blit(
            text,
            (
                self._dropdown_rect.x + 6,
                self._dropdown_rect.y + (self._dropdown_rect.height - text.get_height()) // 2,
            ),
        )
        # Chevron
        chevron = "▾" if not self._dropdown_expanded else "▴"
        ch = self.font.render(chevron, True, self.config.text_color)
        surface.blit(
            ch,
            (
                self._dropdown_rect.right - ch.get_width() - 6,
                self._dropdown_rect.y + (self._dropdown_rect.height - ch.get_height()) // 2,
            ),
        )

        if not self._dropdown_expanded:
            return

        items = ["none"] + self._categories
        visible = items[self._dropdown_scroll : self._dropdown_scroll + self._max_visible_items]
        item_height = self._dropdown_rect.height
        list_height = item_height * len(visible)
        list_rect = pygame.Rect(
            self._dropdown_rect.x,
            self._dropdown_rect.bottom + self.config.gutter,
            self._dropdown_rect.width,
            list_height,
        )
        pygame.draw.rect(surface, self.config.grid_color, list_rect)
        pygame.draw.rect(surface, self.config.border_color, list_rect, 1)

        for idx, key in enumerate(visible):
            row_rect = pygame.Rect(
                list_rect.x,
                list_rect.y + idx * item_height,
                list_rect.width,
                item_height,
            )
            active = key == self._active_filter
            if active:
                pygame.draw.rect(surface, (70, 70, 90), row_rect)
            text = self.font.render("All" if key == "none" else key.capitalize(), True, self.config.text_color)
            surface.blit(
                text,
                (
                    row_rect.x + 6,
                    row_rect.y + (row_rect.height - text.get_height()) // 2,
                ),
            )

    def _draw_grid(self, surface: pygame.Surface) -> None:
        tiles = self.model.page_tiles()
        tw = self.config.tile_render_size
        gh = self.config.gutter
        origin_x = self.rect.x + self.config.padding
        origin_y = self._grid_origin_y

        for idx in range(self.config.grid_rows * self.config.grid_cols):
            col = idx % self.config.grid_cols
            row = idx // self.config.grid_cols
            x = origin_x + col * (tw + gh)
            y = origin_y + row * (tw + gh)
            cell = pygame.Rect(x, y, tw, tw)
            pygame.draw.rect(surface, self.config.grid_color, cell)
            pygame.draw.rect(surface, self.config.border_color, cell, 1)

            if idx < len(tiles):
                tile = tiles[idx]
                tile_img = pygame.transform.smoothscale(tile.surface, (tw, tw))
                surface.blit(tile_img, (x, y))
                if self.selected and tile.local_id == self.selected.local_id and tile.tileset_name == self.selected.tileset_name:
                    pygame.draw.rect(surface, (200, 200, 50), cell, 2)
                elif self.hovered == idx:
                    pygame.draw.rect(surface, (150, 150, 150), cell, 1)

    def _draw_tooltip(self, surface: pygame.Surface) -> None:
        if self.hovered is None:
            return
        tiles = self.model.page_tiles()
        if self.hovered >= len(tiles):
            return
        tile = tiles[self.hovered]
        lines = [f"ID: {tile.local_id}"]
        if tile.properties:
            lines += [f"{k}: {v}" for k, v in tile.properties.items()]
        else:
            lines.append("(no properties)")

        padding = 6
        font = self.font
        text_surfs = [font.render(l, True, self.config.text_color) for l in lines]
        width = max(ts.get_width() for ts in text_surfs) + 2 * padding
        height = sum(ts.get_height() for ts in text_surfs) + 2 * padding
        x = self.rect.right - width - self.config.padding
        y = self.rect.bottom - height - self.config.padding
        box = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (25, 25, 25), box)
        pygame.draw.rect(surface, self.config.border_color, box, 1)
        cy = y + padding
        for ts in text_surfs:
            surface.blit(ts, (x + padding, cy))
            cy += ts.get_height()

    def _draw_paging(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.config.grid_color, self._prev_button)
        pygame.draw.rect(surface, self.config.border_color, self._prev_button, 1)
        prev_text = self.font.render("<", True, self.config.text_color)
        surface.blit(
            prev_text,
            (
                self._prev_button.centerx - prev_text.get_width() // 2,
                self._prev_button.centery - prev_text.get_height() // 2,
            ),
        )

        pygame.draw.rect(surface, self.config.grid_color, self._next_button)
        pygame.draw.rect(surface, self.config.border_color, self._next_button, 1)
        next_text = self.font.render(">", True, self.config.text_color)
        surface.blit(
            next_text,
            (
                self._next_button.centerx - next_text.get_width() // 2,
                self._next_button.centery - next_text.get_height() // 2,
            ),
        )

        page_label = f"{self.model.state.page_index + 1}/{max(1, self.model.page_count)}"
        label_surf = self.font.render(page_label, True, self.config.text_color)
        surface.blit(
            label_surf,
            (
                self.rect.centerx - label_surf.get_width() // 2,
                self._prev_button.y + (self._prev_button.height - label_surf.get_height()) // 2,
            ),
        )

        # Counts label: filtered/total
        total = 0
        filtered = 0
        if self.model.state.tileset_name:
            total = len(self.model.tilesets[self.model.state.tileset_name].tiles)
            filtered = len(self.model.active_tiles)
        counts_label = f"{filtered}/{total}"
        counts_surf = self.font.render(counts_label, True, self.config.text_color)
        surface.blit(
            counts_surf,
            (
                self._next_button.right - counts_surf.get_width(),
                self._next_button.y - counts_surf.get_height() - 2,
            ),
        )

    def _apply_filter(self, key: str) -> None:
        if key == "none":
            self.model.set_filter(None)
        elif key in self._categories:
            self.model.set_filter(category_filter(key))
        else:
            return
        self._active_filter = key
        self.hovered = None
        self.selected = None
        self.drag_payload = None

    def _ensure_categories(self) -> None:
        tileset_name = self.model.state.tileset_name
        if not tileset_name:
            return
        tiles = self.model.tilesets[tileset_name].tiles
        categories: List[str] = []
        seen = set()
        for tile in tiles:
            cat_val = tile.properties.get("category")
            if not cat_val:
                continue
            for part in cat_val.split(","):
                cat = part.strip()
                if cat and cat not in seen:
                    seen.add(cat)
                    categories.append(cat)
        categories.sort()
        if categories == self._categories:
            return
        self._categories = categories
        if self._active_filter not in ("none", *categories):
            self._active_filter = "none"
        self._dropdown_scroll = 0

    def _dropdown_item_at(self, pos: Tuple[int, int]) -> Optional[str]:
        if not self._dropdown_expanded:
            return None
        items = ["none"] + self._categories
        visible = items[self._dropdown_scroll : self._dropdown_scroll + self._max_visible_items]
        item_height = self._dropdown_rect.height
        list_rect = pygame.Rect(
            self._dropdown_rect.x,
            self._dropdown_rect.bottom + self.config.gutter,
            self._dropdown_rect.width,
            item_height * len(visible),
        )
        if not list_rect.collidepoint(pos):
            return None
        rel_y = pos[1] - list_rect.y
        idx = rel_y // item_height
        if 0 <= idx < len(visible):
            return visible[idx]
        return None

    def _scroll_dropdown(self, delta: int) -> None:
        items = ["none"] + self._categories
        max_start = max(0, len(items) - self._max_visible_items)
        self._dropdown_scroll = min(max(0, self._dropdown_scroll + delta), max_start)

    def _cycle_category(self, delta: int) -> None:
        items = ["none"] + self._categories
        if not items:
            return
        try:
            idx = items.index(self._active_filter)
        except ValueError:
            idx = 0
        new_idx = (idx + delta) % len(items)
        self._apply_filter(items[new_idx])
