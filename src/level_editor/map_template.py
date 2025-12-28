"""
Map template model and JSON (de)serialization.

Template schema:
{
    "width": 22,
    "height": 14,
    "layers": {
        "ground": {"data": [[1,1,1,...], [...], ...], "visible": true},
        "obstacles": {"data": [[0,0,0,...], [...], ...], "visible": true},
        "allies": {"data": [[0,0,0,...], [...], ...], "visible": true},
        "foes": {"data": [[0,0,0,...], [...], ...], "visible": true}
    },
    "tilesets": ["imgs/tiled_tilesets/dungeon.tsx", ...]  # optional, order matters for firstgid
}
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
import json


@dataclass
class Layer:
    """Represents a single layer with data and visibility state."""
    data: List[List[int]]
    visible: bool = True
    
    def get(self, x: int, y: int) -> int:
        """Get tile at position (x, y)."""
        if 0 <= y < len(self.data) and 0 <= x < len(self.data[y]):
            return self.data[y][x]
        return 0
    
    def set(self, x: int, y: int, value: int) -> None:
        """Set tile at position (x, y)."""
        if 0 <= y < len(self.data) and 0 <= x < len(self.data[y]):
            self.data[y][x] = value


@dataclass
class MapTemplate:
    width: int
    height: int
    layers: Dict[str, Layer]
    # Optional list of TSX paths (relative to repo root) to reproduce firstgid ordering
    tilesets: List[str] = field(default_factory=list)

    @staticmethod
    def create(width: int, height: int, fill: int = 0, tilesets: List[str] | None = None) -> "MapTemplate":
        """Create a new map template with default layers."""
        empty_data = [[fill for _ in range(width)] for _ in range(height)]
        layers = {
            "ground": Layer([row[:] for row in empty_data]),
            "obstacles": Layer([[0 for _ in range(width)] for _ in range(height)]),
            "allies": Layer([[0 for _ in range(width)] for _ in range(height)]),
            "foes": Layer([[0 for _ in range(width)] for _ in range(height)])
        }
        return MapTemplate(width, height, layers, tilesets or [])

    def get_layer(self, layer_name: str) -> Layer:
        """Get layer by name, creating if it doesn't exist."""
        if layer_name not in self.layers:
            empty_data = [[0 for _ in range(self.width)] for _ in range(self.height)]
            self.layers[layer_name] = Layer(empty_data)
        return self.layers[layer_name]

    def set(self, x: int, y: int, tile_type_id: int, layer_name: str = "ground") -> None:
        """Set tile in specified layer."""
        layer = self.get_layer(layer_name)
        layer.set(x, y, tile_type_id)

    def get(self, x: int, y: int, layer_name: str = "ground") -> int:
        """Get tile from specified layer."""
        if layer_name not in self.layers:
            return 0
        return self.layers[layer_name].get(x, y)

    def save_json(self, path: Path) -> None:
        """Save map template to JSON file."""
        layers_data = {}
        for name, layer in self.layers.items():
            layers_data[name] = {
                "data": layer.data,
                "visible": layer.visible
            }
        
        obj = {
            "width": self.width,
            "height": self.height,
            "layers": layers_data
        }
        if self.tilesets:
            obj["tilesets"] = self.tilesets
        
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2), encoding="utf-8")

    @staticmethod
    def load_json(path: Path) -> "MapTemplate":
        """Load map template from JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        width = int(data["width"])
        height = int(data["height"])
        
        layers = {}
        if "layers" in data:
            # New format with named layers
            for name, layer_data in data["layers"].items():
                grid = layer_data["data"]
                visible = layer_data.get("visible", True)
                if len(grid) != height or any(len(row) != width for row in grid):
                    raise ValueError(f"Layer '{name}' dimensions do not match width/height")
                layers[name] = Layer(grid, visible)
        else:
            # Legacy format with single grid - convert to ground layer
            grid = data["grid"]
            if len(grid) != height or any(len(row) != width for row in grid):
                raise ValueError("Grid dimensions do not match width/height")
            layers["ground"] = Layer(grid)
            # Add empty layers for the others
            empty_data = [[0 for _ in range(width)] for _ in range(height)]
            layers["obstacles"] = Layer([row[:] for row in empty_data])
            layers["allies"] = Layer([row[:] for row in empty_data])
            layers["foes"] = Layer([row[:] for row in empty_data])
        
        tilesets = data.get("tilesets", [])
        return MapTemplate(width, height, layers, tilesets)
