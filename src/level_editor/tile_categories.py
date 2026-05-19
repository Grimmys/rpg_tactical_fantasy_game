"""
Tile categorization system for organizing tiles by their intended layer use.

This module provides functionality to categorize tileset tiles based on their
intended use (ground, obstacles, etc.) and create layer-specific palettes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set
from pathlib import Path
from level_editor.tilesets import Tileset


@dataclass
class TileCategory:
    """Represents a category of tiles for a specific layer."""
    name: str
    layer: str
    tile_ids: Set[int] = field(default_factory=set)
    description: str = ""


class TileCategorizer:
    """Manages categorization of tiles by layer type."""
    
    def __init__(self):
        self.categories: Dict[str, TileCategory] = {}
        self._init_default_categories()
    
    def _init_default_categories(self):
        """Initialize default tile categories based on common patterns."""
        # Ground tiles (stone/dirt/grass patterns)
        self.categories["ground"] = TileCategory(
            name="Ground Tiles",
            layer="ground",
            tile_ids={
                # Stone/dirt variants
                589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599,
                # Floor patterns  
                562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573,
                574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585,
                # Additional floor types
                625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635,
                # Grass and outdoor terrain
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                # Additional stone patterns
                656, 657, 658, 659, 660, 661, 662, 663, 664,
            },
            description="Base terrain and floor tiles"
        )
        
        # Obstacle tiles (walls, rocks, etc.)
        self.categories["obstacles"] = TileCategory(
            name="Obstacle Tiles", 
            layer="obstacles",
            tile_ids={
                # Wall variants
                847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858,
                # Additional wall types
                911, 912, 913, 914, 915, 916, 917, 918, 919, 920,
                # Rocks/debris
                783, 784, 785, 786, 787, 788, 789, 790, 791, 792,
                # Special obstacles
                821, 822, 823, 824, 825,
                # Doors and barriers
                101, 102, 103, 104, 105,
            },
            description="Walls, rocks, and blocking elements"
        )
        
        # Ally placement tiles (typically special markers)
        self.categories["allies"] = TileCategory(
            name="Ally Markers",
            layer="allies", 
            tile_ids={
                # Portal/entry markers
                1099, 1093, 1094, 1095, 1096,
                # Special placement markers
                22, 23, 24, 25, 26,  # Altar and special items
                8, 9, 10, 11, 12,    # Chest variants for ally equipment
            },
            description="Player and ally placement markers"
        )
        
        # Foe placement tiles
        self.categories["foes"] = TileCategory(
            name="Foe Markers",
            layer="foes",
            tile_ids={
                # Enemy placement markers - we'll use some decorative tiles
                # that can represent enemy spawn points
                800, 801, 802, 803, 804, 805,  # Skull and bone decorations
                900, 901, 902, 903, 904, 905,  # Dark themed markers
            },
            description="Enemy placement markers"
        )
    
    def get_tiles_for_layer(self, layer: str) -> Set[int]:
        """Get all tile IDs that belong to a specific layer."""
        category = self.categories.get(layer)
        return category.tile_ids if category else set()
    
    def get_layer_for_tile(self, tile_id: int) -> str:
        """Determine which layer a tile ID belongs to."""
        for layer, category in self.categories.items():
            if tile_id in category.tile_ids:
                return layer
        # Default to ground if not categorized
        return "ground"
    
    def add_tile_to_category(self, tile_id: int, layer: str):
        """Add a tile ID to a specific layer category."""
        if layer in self.categories:
            self.categories[layer].tile_ids.add(tile_id)
    
    def create_layer_palette(self, tileset: Tileset, layer: str) -> List[int]:
        """Create a filtered palette of tiles for a specific layer."""
        layer_tiles = self.get_tiles_for_layer(layer)
        palette = []
        
        # Convert global IDs to local IDs within the tileset
        for tile_id in layer_tiles:
            if tileset.firstgid <= tile_id < tileset.firstgid + tileset.tilecount:
                local_id = tile_id - tileset.firstgid
                if 0 <= local_id < tileset.tilecount:
                    palette.append(local_id)
        
        # Sort for consistent ordering
        palette.sort()
        return palette


# Global instance
tile_categorizer = TileCategorizer()
