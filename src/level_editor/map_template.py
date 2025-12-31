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

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

import pytmx

from src.services.tmx_loader_core import parse_tmx


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
    # Optional list of explicit firstgid values aligned with tilesets
    tileset_firstgids: List[int] = field(default_factory=list)

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
        return MapTemplate(width, height, layers, tilesets or [], [])

    @staticmethod
    def load_tmx(path: Path) -> "MapTemplate":
        """Load a TMX map file and convert it to a MapTemplate for editing."""
        parsed = parse_tmx(path)
        width, height = parsed.width, parsed.height

        layers: Dict[str, Layer] = {}
        for lname in ["ground", "obstacles", "allies", "foes"]:
            p_layer = parsed.layers.get(lname)
            grid = [[0 for _ in range(width)] for _ in range(height)]
            if p_layer is not None:
                for y in range(min(height, len(p_layer.data))):
                    row = p_layer.data[y]
                    for x in range(min(width, len(row))):
                        grid[y][x] = row[x]
                visible = p_layer.visible
            else:
                visible = True
            layers[lname] = Layer(grid, visible)

        # Extract tileset sources and firstgids directly from the TMX XML to keep TSX paths.
        tilesets: List[str] = []
        firstgids: List[int] = []
        try:
            root = ET.parse(path).getroot()
            for ts_el in root.findall("tileset"):
                src_attr = ts_el.attrib.get("source")
                if not src_attr:
                    continue
                ts_path = (path.parent / src_attr).resolve()
                tilesets.append(str(ts_path))
                fg_attr = ts_el.attrib.get("firstgid")
                if fg_attr is not None:
                    firstgids.append(int(fg_attr))
        except Exception as exc:
            print(f"[editor] Warning: failed to read tilesets from TMX XML: {exc}")

        return MapTemplate(width, height, layers, tilesets, firstgids)

    def save_tmx(
        self,
        path: Path,
        tileset_index: List[tuple[str, Any, int]],
        tsx_paths: List[Path],
        tile_width: int = 32,
        tile_height: int = 32,
    ) -> None:
        """Export the map to a TMX file using the provided tileset ordering."""

        # Build firstgid map from tileset_index (already ordered)
        firstgid_map: Dict[str, int] = {name: fg for name, _, fg in tileset_index}

        map_el = ET.Element(
            "map",
            {
                "version": "1.10",
                "tiledversion": "1.10.2",
                "orientation": "orthogonal",
                "renderorder": "right-down",
                "width": str(self.width),
                "height": str(self.height),
                "tilewidth": str(tile_width),
                "tileheight": str(tile_height),
                "infinite": "0",
            },
        )

        # Tilesets
        for tsx_path in tsx_paths:
            name = tsx_path.stem
            if name not in firstgid_map:
                continue
            rel_source = Path(tsx_path).resolve()
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            try:
                rel_source = rel_source.relative_to(path.parent)
            except ValueError:
                rel_source = rel_source
            ET.SubElement(
                map_el,
                "tileset",
                {
                    "firstgid": str(firstgid_map[name]),
                    "source": str(rel_source).replace("\\", "/"),
                },
            )

        # Layers (only those present in the template)
        for layer_name, layer in self.layers.items():
            layer_el = ET.SubElement(
                map_el,
                "layer",
                {
                    "name": layer_name,
                    "width": str(self.width),
                    "height": str(self.height),
                },
            )
            if not layer.visible:
                layer_el.set("visible", "0")

            data_el = ET.SubElement(layer_el, "data", {"encoding": "csv"})
            # Flatten row-major
            rows = []
            for y in range(self.height):
                row = [str(layer.data[y][x] if x < len(layer.data[y]) else 0) for x in range(self.width)]
                rows.append(",".join(row))
            data_el.text = "\n" + "\n".join(rows) + "\n"

        tree = ET.ElementTree(map_el)
        path.parent.mkdir(parents=True, exist_ok=True)
        tree.write(path, encoding="utf-8", xml_declaration=True)

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
        if self.tileset_firstgids:
            obj["tileset_firstgids"] = self.tileset_firstgids
        
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
        tileset_firstgids = [int(x) for x in data.get("tileset_firstgids", [])]
        return MapTemplate(width, height, layers, tilesets, tileset_firstgids)
