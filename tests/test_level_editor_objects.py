"""Editor object-editing MVP tests.

These tests exercise object placement, deletion, and round-trip preservation
of unsupported object types through the editor's MapTemplate path.
"""
from __future__ import annotations

import os
from pathlib import Path

import pygame
import pytest

from src.level_editor.map_template import MapObject, MapTemplate
from src.level_editor import object_model
from src.services.tmx_loader_core import parse_tmx


CAMPAIGN_MAP = Path("maps/level_0/map.tmx")


@pytest.fixture(scope="module", autouse=True)
def _init_display():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))
    yield
    # Do NOT call pygame.quit() here - it tears down the mixer and breaks
    # other tests in the same pytest session.


def _fresh_template() -> MapTemplate:
    return MapTemplate.create(8, 6)


def test_object_presets_have_expected_metadata():
    presets = object_model.OBJECT_PRESETS
    assert set(presets.keys()) == {"placement", "foe", "ally", "objective"}
    assert presets["objective"].properties == {"mission": "main", "walkable": True}
    assert presets["foe"].properties == {"level": 1}
    assert presets["placement"].properties == {}
    assert presets["ally"].properties == {}
    for preset in presets.values():
        assert preset.width == 32
        assert preset.height == 32


def test_place_object_writes_to_dynamic_data_with_pixel_coords():
    tmpl = _fresh_template()
    obj = object_model.place_object(tmpl, "foe", 3, 2)
    layer = tmpl.object_layers["dynamic_data"]
    assert obj in layer
    assert obj.type == "foe"
    assert obj.name == "skeleton"
    assert obj.x == 3 * tmpl.tile_width
    assert obj.y == 2 * tmpl.tile_height
    assert obj.properties == {"level": 1}
    assert obj.object_id is not None and obj.object_id >= 1


def test_place_object_replaces_supported_on_same_cell():
    tmpl = _fresh_template()
    first = object_model.place_object(tmpl, "foe", 1, 1)
    second = object_model.place_object(tmpl, "ally", 1, 1)
    layer = tmpl.object_layers["dynamic_data"]
    assert first not in layer
    assert second in layer
    assert second.object_id != first.object_id


def test_place_object_preserves_unrelated_unsupported_object():
    tmpl = _fresh_template()
    preserved = MapObject(
        name="house",
        type="building",
        x=32.0,
        y=32.0,
        gid=42,
        properties={"sprite_link": "imgs/houses/blue_house.png"},
        object_id=99,
    )
    tmpl.object_layers["dynamic_data"].append(preserved)
    object_model.place_object(tmpl, "foe", 1, 1)
    assert preserved in tmpl.object_layers["dynamic_data"]


def test_delete_object_only_removes_editable():
    tmpl = _fresh_template()
    object_model.place_object(tmpl, "placement", 0, 0)
    preserved = MapObject(
        name="chest", type="chest", x=64.0, y=0.0, gid=1, object_id=77
    )
    tmpl.object_layers["dynamic_data"].append(preserved)

    assert object_model.delete_object_at(tmpl, 0, 0) is True
    # Trying again returns False; preserved chest stays untouched
    assert object_model.delete_object_at(tmpl, 0, 0) is False
    assert object_model.delete_object_at(tmpl, 2, 0) is False
    assert preserved in tmpl.object_layers["dynamic_data"]


def test_next_object_id_skips_existing_ids():
    tmpl = _fresh_template()
    tmpl.next_object_id = 10
    tmpl.object_layers["dynamic_data"].append(
        MapObject(name="x", type="placement", x=0, y=0, object_id=10)
    )
    new_id = object_model.next_object_id(tmpl)
    assert new_id > 10


def test_objective_preset_includes_required_properties():
    tmpl = _fresh_template()
    obj = object_model.place_object(tmpl, "objective", 4, 3)
    assert obj.type == "objective"
    assert obj.name == "Exit"
    assert obj.properties == {"mission": "main", "walkable": True}


def test_save_reload_preserves_new_objects(tmp_path: Path):
    tmpl = _fresh_template()
    placement = object_model.place_object(tmpl, "placement", 1, 1)
    foe = object_model.place_object(tmpl, "foe", 2, 1)
    ally = object_model.place_object(tmpl, "ally", 3, 1)
    objective = object_model.place_object(tmpl, "objective", 4, 1)

    out_path = tmp_path / "edited.tmx"
    tmpl.save_tmx(out_path, tileset_index=[], tsx_paths=[])

    parsed = parse_tmx(out_path)
    dyn = parsed.object_layers.get("dynamic_data")
    assert dyn is not None
    by_id = {obj.id: obj for obj in dyn.objects}
    assert placement.object_id in by_id
    assert by_id[placement.object_id].type == "placement"
    assert by_id[foe.object_id].properties.get("level") == 1
    saved_objective = by_id[objective.object_id]
    assert saved_objective.properties.get("mission") == "main"
    assert saved_objective.properties.get("walkable") is True


def test_editor_save_path_preserves_campaign_objects(tmp_path: Path):
    """Round-trip via the editor's actual save_template path (no parsed_* args)."""
    from src.level_editor.core import io as core_io

    tmpl = MapTemplate.load_tmx(CAMPAIGN_MAP)
    parsed_before = parse_tmx(CAMPAIGN_MAP)

    out_path = CAMPAIGN_MAP.parent / "__editor_save_roundtrip.tmx"
    try:
        # Use the editor's high-level save path which does NOT pass parsed_* args
        core_io.save_template(tmpl, out_path, tileset_index=[], tsx_paths=[])
        parsed_after = parse_tmx(out_path)
    finally:
        if out_path.exists():
            out_path.unlink()

    # dynamic_data + events objects must be preserved by ids and type
    for lname in ("dynamic_data", "events"):
        before = parsed_before.object_layers.get(lname)
        after = parsed_after.object_layers.get(lname)
        assert before is not None and after is not None
        before_ids = {o.id for o in before.objects}
        after_ids = {o.id for o in after.objects}
        assert before_ids == after_ids, f"{lname} object ids differ"
        before_types = sorted((o.id, o.type) for o in before.objects)
        after_types = sorted((o.id, o.type) for o in after.objects)
        assert before_types == after_types
        # Property type preservation (bools stay bool, ints stay int)
        for ob, oa in zip(
            sorted(before.objects, key=lambda o: o.id or 0),
            sorted(after.objects, key=lambda o: o.id or 0),
        ):
            for key, value in ob.properties.items():
                assert key in oa.properties, f"missing prop {key} on object {ob.id}"
                assert type(oa.properties[key]) is type(value), (
                    f"property {key} type changed on object {ob.id}: "
                    f"{type(value)} -> {type(oa.properties[key])}"
                )
                assert oa.properties[key] == value


def test_editor_save_path_preserves_tile_layer_order(tmp_path: Path):
    """The editor must not invent new tile layers (e.g., allies/foes)."""
    from src.level_editor.core import io as core_io

    tmpl = MapTemplate.load_tmx(CAMPAIGN_MAP)
    parsed_before = parse_tmx(CAMPAIGN_MAP)

    out_path = CAMPAIGN_MAP.parent / "__editor_save_layers.tmx"
    try:
        core_io.save_template(tmpl, out_path, tileset_index=[], tsx_paths=[])
        parsed_after = parse_tmx(out_path)
    finally:
        if out_path.exists():
            out_path.unlink()

    assert list(parsed_before.layers.keys()) == list(parsed_after.layers.keys())
