"""
Map template model and JSON/TMX (de)serialization.

Authoritative editor schema (TMX-aligned, minimal):
{
    "width": 22,
    "height": 14,
    "tile_width": 32,
    "tile_height": 32,
    "layers": {
        "ground": {"data": [[...]], "visible": true},
        "obstacles": {"data": [[...]], "visible": true},
        "allies": {"data": [[...]], "visible": true},
        "foes": {"data": [[...]], "visible": true}
    },
    "object_layers": {
        "dynamic_data": [ {"name": "Exit", "type": "objective", "gid": 1099, "x": 0, "y": 96, "width": 32, "height": 32, "properties": {"mission": "main", "walkable": true}} ],
        "events": [ {"name": "before_init", "type": "before_init", "x": 0, "y": 0, "width": 32, "height": 32, "properties": {"dialogs": "0"}} ]
    },
    "map_properties": {"level_name": "Prototype", "main_mission_type": "TOUCH_POSITION"},
    "tilesets": ["imgs/tiled_tilesets/dungeon.tsx", ...],
    "tileset_firstgids": [1, 6081]
}

Missing sections are defaulted to empty-but-valid TMX structures so exported
maps remain compatible with the in-game schema while the editor UI is still
under construction.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

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
class MapObject:
    """Simple TMX object representation (objectgroups in the schema)."""

    name: str | None
    type: str | None
    x: float
    y: float
    width: float = 32
    height: float = 32
    gid: int | None = None
    properties: Dict[str, Any] = field(default_factory=dict)
    # Preserve original TMX object ids when present to avoid losing references
    object_id: int | None = None
    rotation: float = 0.0
    visible: bool = True

    def to_xml(self, parent: ET.Element, object_id: int) -> None:
        """Serialize this object under the given parent element."""

        attrs: Dict[str, str] = {
            "id": str(self.object_id if self.object_id is not None else object_id),
            "x": str(self.x),
            "y": str(self.y),
            "width": str(self.width),
            "height": str(self.height),
        }
        if self.name is not None:
            attrs["name"] = self.name
        if self.type:
            attrs["type"] = self.type
        if self.gid is not None:
            attrs["gid"] = str(self.gid)
        if self.rotation:
            attrs["rotation"] = str(self.rotation)
        if not self.visible:
            attrs["visible"] = "0"

        obj_el = ET.SubElement(parent, "object", attrs)

        if not self.properties:
            return

        props_el = ET.SubElement(obj_el, "properties")
        for key, value in self.properties.items():
            prop_attrs = {"name": key}
            if isinstance(value, bool):
                prop_attrs["type"] = "bool"
                prop_attrs["value"] = "true" if value else "false"
            elif isinstance(value, int):
                prop_attrs["type"] = "int"
                prop_attrs["value"] = str(value)
            elif isinstance(value, float):
                prop_attrs["type"] = "float"
                prop_attrs["value"] = str(value)
            else:
                prop_attrs["value"] = str(value)
            ET.SubElement(props_el, "property", prop_attrs)


@dataclass
class MapTemplate:
    width: int
    height: int
    layers: Dict[str, Layer]
    # Optional list of TSX paths (relative to repo root) to reproduce firstgid ordering
    tilesets: List[str] = field(default_factory=list)
    # Optional list of explicit firstgid values aligned with tilesets
    tileset_firstgids: List[int] = field(default_factory=list)
    # Map-level TMX properties (mission metadata, chapter id, etc.)
    map_properties: Dict[str, Any] = field(default_factory=dict)
    # Object layers keyed by layer name (e.g., dynamic_data, events)
    object_layers: Dict[str, List[MapObject]] = field(default_factory=dict)
    # Tile dimensions (TMX tilewidth/tileheight); default matches shipped maps
    tile_width: int = 32
    tile_height: int = 32
    # Preserve TMX ids to avoid losing references/order on round-trip
    next_layer_id: int | None = None
    next_object_id: int | None = None
    layer_ids: Dict[str, int] = field(default_factory=dict)
    raw_tileset_sources: Dict[int, str] = field(default_factory=dict)
    # Preserved TMX metadata so a no-op save reproduces the original document
    map_version: str | None = None
    map_tiledversion: str | None = None
    map_renderorder: str | None = None
    editorsettings_export: str | None = None
    layer_opacity: Dict[str, float] = field(default_factory=dict)
    object_layer_visibility: Dict[str, bool] = field(default_factory=dict)
    object_layer_opacity: Dict[str, float] = field(default_factory=dict)
    # Ordered list of tile-layer names actually present in the source TMX
    tile_layer_order: List[str] = field(default_factory=list)
    # Ordered list of object-layer names actually present in the source TMX
    object_layer_order: List[str] = field(default_factory=list)

    @staticmethod
    def create(
        width: int,
        height: int,
        fill: int = 0,
        tilesets: List[str] | None = None,
        tile_width: int = 32,
        tile_height: int = 32,
    ) -> "MapTemplate":
        """Create a new map template with default layers and empty object groups."""

        empty_data = [[fill for _ in range(width)] for _ in range(height)]
        layers = {
            "ground": Layer([row[:] for row in empty_data]),
            "obstacles": Layer([[0 for _ in range(width)] for _ in range(height)]),
        }
        default_obj_layers: Dict[str, List[MapObject]] = {
            "dynamic_data": [],
            "events": [],
        }
        return MapTemplate(
            width,
            height,
            layers,
            tilesets or [],
            [],
            {},
            default_obj_layers,
            tile_width,
            tile_height,
        )

    @staticmethod
    def load_tmx(path: Path) -> "MapTemplate":
        """Load a TMX map file and convert it to a MapTemplate for editing."""

        parsed = parse_tmx(path)
        width, height = parsed.width, parsed.height
        # Extract tileset sources/firstgids, raw layer data, and id bookkeeping directly from the TMX XML.
        tilesets: List[str] = []
        firstgids: List[int] = []
        raw_tileset_sources: Dict[int, str] = {}
        layer_ids: Dict[str, int] = {}
        next_layer_id: int | None = None
        next_object_id: int | None = None
        object_gid_map: Dict[int, int] = {}
        object_geom_map: Dict[int, tuple[float, float, float, float, float, bool]] = {}
        tile_data_by_name: Dict[str, List[List[int]]] = {}
        try:
            root = ET.parse(path).getroot()
            next_layer_id = int(root.attrib.get("nextlayerid")) if root.attrib.get("nextlayerid") else None
            next_object_id = int(root.attrib.get("nextobjectid")) if root.attrib.get("nextobjectid") else None
            for ts_el in root.findall("tileset"):
                src_attr = ts_el.attrib.get("source")
                if not src_attr:
                    continue
                # Keep the raw source exactly as in TMX (relative) and also a resolved path
                raw_tileset_sources[int(ts_el.attrib.get("firstgid", "0") or 0)] = src_attr
                ts_path = (path.parent / src_attr).resolve()
                tilesets.append(str(ts_path))
                fg_attr = ts_el.attrib.get("firstgid")
                if fg_attr is not None:
                    firstgids.append(int(fg_attr))
            for layer_el in root.findall("layer"):
                lname = layer_el.attrib.get("name")
                lid = layer_el.attrib.get("id")
                if lname and lid is not None:
                    layer_ids[lname] = int(lid)
                data_el = layer_el.find("data")
                if lname and data_el is not None and data_el.text:
                    try:
                        raw = data_el.text.strip().replace("\r", "")
                        rows = [r for r in raw.split("\n") if r]
                        parsed_rows: List[List[int]] = []
                        for row in rows:
                            parsed_rows.append([int(tok) if tok else 0 for tok in row.split(",") if tok != ""])
                        tile_data_by_name[lname] = parsed_rows
                    except Exception:
                        pass
            for obj_el in root.findall("objectgroup/object"):
                oid = obj_el.attrib.get("id")
                gid_attr = obj_el.attrib.get("gid")
                if oid is not None and gid_attr is not None:
                    try:
                        object_gid_map[int(oid)] = int(gid_attr)
                    except ValueError:
                        continue
                if oid is not None:
                    try:
                        ox = float(obj_el.attrib.get("x", "0"))
                        oy = float(obj_el.attrib.get("y", "0"))
                        ow = float(obj_el.attrib.get("width", "0"))
                        oh = float(obj_el.attrib.get("height", "0"))
                        rot = float(obj_el.attrib.get("rotation", "0"))
                        vis_attr = obj_el.attrib.get("visible")
                        vis = False if vis_attr == "0" else True
                        object_geom_map[int(oid)] = (ox, oy, ow, oh, rot, vis)
                    except ValueError:
                        pass
            for obj_group_el in root.findall("objectgroup"):
                lname = obj_group_el.attrib.get("name")
                lid = obj_group_el.attrib.get("id")
                if lname and lid is not None:
                    layer_ids[lname] = int(lid)
        except Exception as exc:
            print(f"[editor] Warning: failed to read tilesets from TMX XML: {exc}")

        # Only materialise tile layers that exist in the source TMX (preserves order).
        # This avoids accidentally adding allies/foes tile layers, which the main
        # game does NOT model as tile layers (see Phase 2: entities live in objects).
        layers: Dict[str, Layer] = {}
        layer_opacity: Dict[str, float] = {}
        tile_layer_order: List[str] = list(parsed.layers.keys())
        for lname in tile_layer_order:
            p_layer = parsed.layers[lname]
            grid = [[0 for _ in range(width)] for _ in range(height)]
            source_data = tile_data_by_name.get(lname) or p_layer.data
            for y in range(min(height, len(source_data))):
                row = source_data[y]
                for x in range(min(width, len(row))):
                    grid[y][x] = row[x]
            layers[lname] = Layer(grid, p_layer.visible)
            if p_layer.opacity is not None:
                layer_opacity[lname] = p_layer.opacity

        # Map properties and object layers
        map_props = dict(parsed.properties)
        object_layers: Dict[str, List[MapObject]] = {}
        object_layer_visibility: Dict[str, bool] = {}
        object_layer_opacity: Dict[str, float] = {}
        object_layer_order: List[str] = list(parsed.object_layers.keys())
        for lname, olayer in parsed.object_layers.items():
            object_layer_visibility[lname] = olayer.visible
            if olayer.opacity is not None:
                object_layer_opacity[lname] = olayer.opacity
            collected: List[MapObject] = []
            for obj in olayer.objects:
                raw = object_geom_map.get(getattr(obj, "id", None))
                ox, oy, ow, oh, rot, vis = (
                    raw
                    if raw is not None
                    else (
                        obj.x,
                        obj.y,
                        obj.width if obj.width else parsed.tilewidth,
                        obj.height if obj.height else parsed.tileheight,
                        getattr(obj, "rotation", 0),
                        getattr(obj, "visible", True),
                    )
                )
                collected.append(
                    MapObject(
                        name=obj.name if obj.name != "" else None,
                        type=obj.type,
                        gid=object_gid_map.get(getattr(obj, "id", None), obj.gid),
                        x=ox,
                        y=oy,
                        width=ow,
                        height=oh,
                        properties=dict(obj.properties),
                        object_id=getattr(obj, "id", None),
                        rotation=rot,
                        visible=vis,
                    )
                )
            object_layers[lname] = collected

        # Ensure the canonical object layers exist
        for required in ("dynamic_data", "events"):
            object_layers.setdefault(required, [])
            if required not in object_layer_order:
                object_layer_order.append(required)

        return MapTemplate(
            width,
            height,
            layers,
            tilesets,
            firstgids,
            map_props,
            object_layers,
            parsed.tilewidth,
            parsed.tileheight,
            next_layer_id,
            next_object_id,
            layer_ids,
            raw_tileset_sources,
            map_version=parsed.version,
            map_tiledversion=parsed.tiledversion,
            map_renderorder=parsed.renderorder,
            editorsettings_export=parsed.editorsettings_export,
            layer_opacity=layer_opacity,
            object_layer_visibility=object_layer_visibility,
            object_layer_opacity=object_layer_opacity,
            tile_layer_order=tile_layer_order,
            object_layer_order=object_layer_order,
        )

    def save_tmx(
        self,
        path: Path,
        tileset_index: List[tuple[str, Any, int]],
        tsx_paths: List[Path],
        tile_width: int | None = None,
        tile_height: int | None = None,
        parsed_tilesets: List[Any] | None = None,
        parsed_layers: Dict[str, Any] | None = None,
        parsed_object_layers: Dict[str, Any] | None = None,
        map_properties: Dict[str, Any] | None = None,
        map_version: str | None = None,
        map_tiledversion: str | None = None,
        nextlayerid: int | None = None,
        nextobjectid: int | None = None,
        include_editorsettings: Any | None = None,
        renderorder: str | None = None,
    ) -> None:
        """Export the map to a TMX file using the provided tileset ordering."""

        # Resolve tile dimensions from template if not explicitly provided
        tw = tile_width or self.tile_width or 32
        th = tile_height or self.tile_height or 32

        # Map-level metadata overrides; fall back to stored values from the source TMX
        m_version = map_version or self.map_version or "1.10"
        m_tiledversion = map_tiledversion or self.map_tiledversion or "1.11.2"
        m_renderorder = renderorder or self.map_renderorder or "right-down"

        # Prefer the template's stored tilesets/firstgids for exact round-trips
        tileset_sources: List[Path]
        if self.tilesets:
            tileset_sources = [Path(p) for p in self.tilesets]
        else:
            tileset_sources = list(tsx_paths)

        firstgid_map: Dict[str, int] = {}
        if self.tileset_firstgids and len(self.tileset_firstgids) == len(tileset_sources):
            for ts_path, fg in zip(tileset_sources, self.tileset_firstgids):
                firstgid_map[ts_path.stem] = int(fg)
        else:
            for name, _, fg in tileset_index:
                firstgid_map[name] = fg

        map_el = ET.Element(
            "map",
            {
                "version": m_version,
                "tiledversion": m_tiledversion,
                "orientation": "orthogonal",
                "renderorder": m_renderorder,
                "compressionlevel": "0",
                "width": str(self.width),
                "height": str(self.height),
                "tilewidth": str(tw),
                "tileheight": str(th),
                "infinite": "0",
            },
        )

        # Editor export settings (optional). Honour stored value when not overridden.
        editor_export_fmt = include_editorsettings if include_editorsettings is not None else self.editorsettings_export
        if editor_export_fmt:
            fmt = editor_export_fmt if isinstance(editor_export_fmt, str) else "tmx"
            editor_el = ET.SubElement(map_el, "editorsettings")
            ET.SubElement(editor_el, "export", {"format": fmt})

        effective_props = map_properties if map_properties is not None else self.map_properties

        # Map-level properties (mission metadata, etc.)
        if effective_props:
            props_el = ET.SubElement(map_el, "properties")
            for key, value in effective_props.items():
                prop_attrs = {"name": key}
                if isinstance(value, bool):
                    prop_attrs["type"] = "bool"
                    prop_attrs["value"] = "true" if value else "false"
                elif isinstance(value, int):
                    prop_attrs["type"] = "int"
                    prop_attrs["value"] = str(value)
                elif isinstance(value, float):
                    prop_attrs["type"] = "float"
                    prop_attrs["value"] = str(value)
                else:
                    prop_attrs["value"] = str(value)
                ET.SubElement(props_el, "property", prop_attrs)

        # Tilesets
        def _relativize(src_path: Path) -> str:
            rel_source = src_path
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            try:
                rel_source = src_path.relative_to(path.parent)
            except ValueError:
                rel_source = src_path
            return str(rel_source).replace("\\", "/")

        def _resolve_raw_source(ts_firstgid: int, idx: int) -> str | None:
            # Prefer the raw TMX source captured at load (already relative in legacy maps)
            raw = self.raw_tileset_sources.get(ts_firstgid)
            if raw:
                return raw.replace("\\", "/")
            # Fallback to stored tilesets list
            if self.tilesets and idx < len(self.tilesets):
                return _relativize(Path(self.tilesets[idx]).resolve())
            return None

        if parsed_tilesets:
            for idx, ts in enumerate(parsed_tilesets):
                src_str = None
                # Prefer raw TSX source from TMX
                src_str = _resolve_raw_source(ts.firstgid, idx)
                if src_str is None and ts.source:
                    # Only relativize if we have a path; do not allow absolute
                    candidate = Path(ts.source)
                    if not candidate.is_absolute():
                        src_str = candidate.as_posix()
                    else:
                        try:
                            src_str = _relativize(candidate)
                        except Exception:
                            src_str = None
                if src_str is None:
                    src_str = ""
                ET.SubElement(
                    map_el,
                    "tileset",
                    {
                        "firstgid": str(ts.firstgid),
                        "source": src_str,
                    },
                )
        else:
            for idx, tsx_path in enumerate(tileset_sources):
                name = tsx_path.stem
                if name not in firstgid_map:
                    continue
                src_str = _resolve_raw_source(firstgid_map[name], idx)
                if src_str is None:
                    src_str = _relativize(Path(tsx_path).resolve())
                ET.SubElement(
                    map_el,
                    "tileset",
                    {
                        "firstgid": str(firstgid_map[name]),
                        "source": src_str,
                    },
                )

        # Layers (only those present in the template). Prefer parsed_layers if given,
        # else use the source-TMX ordering captured at load time, else dict order.
        layer_id = 1
        max_layer_id = 0
        if parsed_layers:
            layer_items = list(parsed_layers.items())
        elif self.tile_layer_order:
            layer_items = [(n, None) for n in self.tile_layer_order if n in self.layers]
            # Append any layers added after load
            for n in self.layers.keys():
                if n not in self.tile_layer_order:
                    layer_items.append((n, None))
        else:
            layer_items = list(self.layers.items())
        for layer_name, layer_meta in layer_items:
            layer = self.layers.get(layer_name, Layer([[0 for _ in range(self.width)] for _ in range(self.height)]))
            parsed_layer = layer_meta if parsed_layers else None
            lid = (
                parsed_layer.id
                if parsed_layer and getattr(parsed_layer, "id", None) is not None
                else self.layer_ids.get(layer_name, layer_id)
            )
            layer_el = ET.SubElement(
                map_el,
                "layer",
                {
                    "id": str(lid),
                    "name": layer_name,
                    "width": str(self.width),
                    "height": str(self.height),
                },
            )
            max_layer_id = max(max_layer_id, int(layer_el.attrib["id"]))
            layer_id += 1
            layer_visible = parsed_layer.visible if parsed_layer is not None else layer.visible
            if not layer_visible:
                layer_el.set("visible", "0")
            if parsed_layer is not None:
                layer_opacity_val = getattr(parsed_layer, "opacity", None)
            else:
                layer_opacity_val = self.layer_opacity.get(layer_name)
            if layer_opacity_val is not None:
                layer_el.set("opacity", str(layer_opacity_val))

            data_el = ET.SubElement(layer_el, "data", {"encoding": "csv"})
            rows: List[str] = []
            source_data = layer.data
            for y in range(self.height):
                row = [str(source_data[y][x] if x < len(source_data[y]) else 0) for x in range(self.width)]
                rows.append(",".join(row))
            data_el.text = "\n" + ",\n".join(rows) + "\n"

        # Object layers (dynamic_data, events, etc.)
        object_id = 1
        max_object_id = 0
        canonical_order = ["dynamic_data", "events"]
        remaining = [k for k in self.object_layers.keys() if k not in canonical_order]
        if parsed_object_layers:
            obj_layer_items = list(parsed_object_layers.items())
        elif self.object_layer_order:
            ordered = [(n, None) for n in self.object_layer_order if n in self.object_layers]
            for n in self.object_layers.keys():
                if n not in self.object_layer_order:
                    ordered.append((n, None))
            obj_layer_items = ordered
        else:
            # Fall back to canonical order when no parsed object layers provided
            obj_layer_items = [(lname, None) for lname in canonical_order + remaining]

        for lname, parsed_obj_layer in obj_layer_items:
            objects = self.object_layers.get(lname, [])
            oid = (
                parsed_obj_layer.id
                if parsed_obj_layer and getattr(parsed_obj_layer, "id", None) is not None
                else self.layer_ids.get(lname, layer_id)
            )
            obj_layer_el = ET.SubElement(
                map_el,
                "objectgroup",
                {
                    "id": str(oid),
                    "name": lname,
                },
            )
            max_layer_id = max(max_layer_id, int(obj_layer_el.attrib["id"]))
            layer_id += 1
            if parsed_obj_layer is not None:
                if not getattr(parsed_obj_layer, "visible", True):
                    obj_layer_el.set("visible", "0")
                if getattr(parsed_obj_layer, "opacity", None) is not None:
                    obj_layer_el.set("opacity", str(parsed_obj_layer.opacity))
            else:
                if not self.object_layer_visibility.get(lname, True):
                    obj_layer_el.set("visible", "0")
                stored_opacity = self.object_layer_opacity.get(lname)
                if stored_opacity is not None:
                    obj_layer_el.set("opacity", str(stored_opacity))
            for obj in objects:
                actual_id = obj.object_id if obj.object_id is not None else object_id
                obj.to_xml(obj_layer_el, actual_id)
                max_object_id = max(max_object_id, actual_id)
                object_id += 1

        # nextlayerid/nextobjectid keep ids stable for Tiled round-trips
        candidate_next_lid = self.next_layer_id if self.next_layer_id is not None else (max_layer_id + 1)
        candidate_next_oid = self.next_object_id if self.next_object_id is not None else (max_object_id + 1)
        next_lid = nextlayerid if nextlayerid is not None else candidate_next_lid
        next_oid = nextobjectid if nextobjectid is not None else candidate_next_oid
        map_el.set("nextlayerid", str(next_lid))
        map_el.set("nextobjectid", str(next_oid))

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
                "visible": layer.visible,
            }

        obj_layers_data: Dict[str, List[dict]] = {}
        for lname, objs in self.object_layers.items():
            obj_layers_data[lname] = [
                {
                    "name": obj.name,
                    "type": obj.type,
                    "gid": obj.gid,
                    "x": obj.x,
                    "y": obj.y,
                    "width": obj.width,
                    "height": obj.height,
                    "properties": obj.properties,
                }
                for obj in objs
            ]

        obj = {
            "width": self.width,
            "height": self.height,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "layers": layers_data,
            "object_layers": obj_layers_data,
            "map_properties": self.map_properties,
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
        tile_width = int(data.get("tile_width", 32))
        tile_height = int(data.get("tile_height", 32))

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
            empty_data = [[0 for _ in range(width)] for _ in range(height)]
            layers["obstacles"] = Layer([row[:] for row in empty_data])
            layers["allies"] = Layer([row[:] for row in empty_data])
            layers["foes"] = Layer([row[:] for row in empty_data])

        object_layers: Dict[str, List[MapObject]] = {}
        for lname, objs in data.get("object_layers", {}).items():
            bucket: List[MapObject] = []
            for obj in objs:
                bucket.append(
                    MapObject(
                        name=obj.get("name", ""),
                        type=obj.get("type"),
                        gid=obj.get("gid"),
                        x=float(obj.get("x", 0)),
                        y=float(obj.get("y", 0)),
                        width=float(obj.get("width", tile_width)),
                        height=float(obj.get("height", tile_height)),
                        properties=dict(obj.get("properties", {})),
                    )
                )
            object_layers[lname] = bucket

        for required in ("dynamic_data", "events"):
            object_layers.setdefault(required, [])

        map_properties = dict(data.get("map_properties", {}))
        tilesets = data.get("tilesets", [])
        tileset_firstgids = [int(x) for x in data.get("tileset_firstgids", [])]

        return MapTemplate(
            width,
            height,
            layers,
            tilesets,
            tileset_firstgids,
            map_properties,
            object_layers,
            tile_width,
            tile_height,
        )
