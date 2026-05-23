"""Object/entity helpers for the level editor.

Entities the main game expects in the `dynamic_data` objectgroup are placed
through these presets and helpers. Coordinates follow the existing TMX
convention used by the game loader: the object's ``(x, y)`` is the
**top-left** pixel of the tile, with ``width``/``height`` equal to the tile
size.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .map_template import MapObject, MapTemplate


# Object types editable in the MVP.
SUPPORTED_OBJECT_TYPES = ("placement", "foe", "ally", "objective")

# Object types that exist in the data files but are NOT edited by the MVP.
# They must round-trip without being deleted.
PRESERVED_OBJECT_TYPES = ("building", "chest", "door", "fountain")

# Object layer the supported types are written into.
DYNAMIC_DATA_LAYER = "dynamic_data"


@dataclass(frozen=True)
class ObjectPreset:
    """Defaults used when the editor stamps a new object into a map."""

    type: str
    name: Optional[str]
    width: int = 32
    height: int = 32
    properties: Dict[str, Any] = field(default_factory=dict)


OBJECT_PRESETS: Dict[str, ObjectPreset] = {
    "placement": ObjectPreset(
        type="placement",
        name="placement",
    ),
    "foe": ObjectPreset(
        type="foe",
        name="skeleton",
        properties={"level": 1},
    ),
    "ally": ObjectPreset(
        type="ally",
        name="jist",
    ),
    "objective": ObjectPreset(
        type="objective",
        name="Exit",
        properties={"mission": "main", "walkable": True},
    ),
}


def next_object_id(tmpl: MapTemplate) -> int:
    """Allocate a fresh TMX object id, respecting existing/preserved ids."""
    candidate = tmpl.next_object_id or 1
    used: set[int] = set()
    for objs in tmpl.object_layers.values():
        for obj in objs:
            if obj.object_id is not None:
                used.add(obj.object_id)
    while candidate in used or candidate < 1:
        candidate += 1
    return candidate


def ensure_dynamic_data_layer(tmpl: MapTemplate) -> List[MapObject]:
    """Return (creating if needed) the dynamic_data object layer."""
    if DYNAMIC_DATA_LAYER not in tmpl.object_layers:
        tmpl.object_layers[DYNAMIC_DATA_LAYER] = []
    if DYNAMIC_DATA_LAYER not in tmpl.object_layer_order:
        tmpl.object_layer_order.append(DYNAMIC_DATA_LAYER)
    return tmpl.object_layers[DYNAMIC_DATA_LAYER]


def place_object(
    tmpl: MapTemplate,
    object_type: str,
    tile_x: int,
    tile_y: int,
    *,
    name: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
) -> MapObject:
    """Stamp a new object on the dynamic_data layer at the given tile cell.

    The object replaces any existing supported-type object on the same tile
    (placement/foe/ally/objective) to keep the edit intent simple. Preserved
    types are never overwritten by this helper.
    """
    if object_type not in OBJECT_PRESETS:
        raise ValueError(f"Unsupported object type: {object_type}")

    preset = OBJECT_PRESETS[object_type]
    pixel_x = tile_x * tmpl.tile_width
    pixel_y = tile_y * tmpl.tile_height
    layer = ensure_dynamic_data_layer(tmpl)

    # Replace any existing editable object at this cell
    layer[:] = [
        obj
        for obj in layer
        if not (
            obj.type in SUPPORTED_OBJECT_TYPES
            and int(obj.x) == pixel_x
            and int(obj.y) == pixel_y
        )
    ]

    merged_props: Dict[str, Any] = dict(preset.properties)
    if properties:
        merged_props.update(properties)

    new_obj = MapObject(
        name=name if name is not None else preset.name,
        type=preset.type,
        x=float(pixel_x),
        y=float(pixel_y),
        width=preset.width,
        height=preset.height,
        properties=merged_props,
        object_id=next_object_id(tmpl),
    )
    layer.append(new_obj)

    # Keep next_object_id monotonic so future saves stay stable
    if tmpl.next_object_id is None or new_obj.object_id >= tmpl.next_object_id:
        tmpl.next_object_id = new_obj.object_id + 1
    return new_obj


def find_object_at(
    tmpl: MapTemplate,
    tile_x: int,
    tile_y: int,
    *,
    editable_only: bool = True,
) -> Optional[MapObject]:
    """Return the topmost object at the given tile cell, if any."""
    pixel_x = tile_x * tmpl.tile_width
    pixel_y = tile_y * tmpl.tile_height
    layer = tmpl.object_layers.get(DYNAMIC_DATA_LAYER, [])
    for obj in reversed(layer):
        if int(obj.x) != pixel_x or int(obj.y) != pixel_y:
            continue
        if editable_only and obj.type not in SUPPORTED_OBJECT_TYPES:
            continue
        return obj
    return None


def delete_object_at(tmpl: MapTemplate, tile_x: int, tile_y: int) -> bool:
    """Delete the editable object at the given tile cell. Returns True if removed."""
    obj = find_object_at(tmpl, tile_x, tile_y, editable_only=True)
    if obj is None:
        return False
    layer = tmpl.object_layers.get(DYNAMIC_DATA_LAYER, [])
    layer.remove(obj)
    return True
