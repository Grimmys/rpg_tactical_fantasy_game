import os
from pathlib import Path

import pygame
import pytest

from src.level_editor.map_template import MapTemplate
from src.services.tmx_loader_core import parse_tmx


GAME_MAP_PATHS = [
    Path("maps/level_0/map.tmx"),
    Path("maps/level_1/map.tmx"),
    Path("maps/level_2/map.tmx"),
    Path("maps/level_3/map.tmx"),
]


@pytest.fixture(scope="session", autouse=True)
def _init_pygame_display():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.display.quit()
    pygame.quit()


def _normalized_source_name(source: str | None) -> str | None:
    if source is None:
        return None
    return Path(source).name


def _assert_tilesets_match(ref, out):
    # tilesets must align by name/firstgid; allow source to differ only by extension (.png -> .tsx)
    assert len(ref.tilesets) == len(out.tilesets)
    for a, b in zip(ref.tilesets, out.tilesets):
        assert a.name == b.name
        assert a.firstgid == b.firstgid
        src_a = _normalized_source_name(a.source)
        src_b = _normalized_source_name(b.source)
        if src_a and src_b:
            stem_a = Path(src_a).stem
            stem_b = Path(src_b).stem
            assert stem_a == stem_b


def _assert_layers_match(ref, out):
    assert list(ref.layers.keys()) == list(out.layers.keys())
    for lname, ref_layer in ref.layers.items():
        out_layer = out.layers[lname]
        assert ref_layer.id == out_layer.id
        assert ref_layer.width == out_layer.width
        assert ref_layer.height == out_layer.height
        assert ref_layer.visible == out_layer.visible
        assert ref_layer.data == out_layer.data


def _assert_object_layers_match(ref, out):
    assert set(ref.object_layers.keys()) == set(out.object_layers.keys())
    for lname, ref_ol in ref.object_layers.items():
        out_ol = out.object_layers[lname]
        assert ref_ol.id == out_ol.id
        assert ref_ol.visible == out_ol.visible
        if ref_ol.opacity is None:
            assert out_ol.opacity in (None, 1.0)
        else:
            assert out_ol.opacity == pytest.approx(ref_ol.opacity)
        assert len(ref_ol.objects) == len(out_ol.objects)
        # Compare objects by id when available, otherwise by index
        ref_objs = sorted(ref_ol.objects, key=lambda o: (o.id is None, o.id, o.name, o.x, o.y))
        out_objs = sorted(out_ol.objects, key=lambda o: (o.id is None, o.id, o.name, o.x, o.y))
        for ra, rb in zip(ref_objs, out_objs):
            assert ra.id == rb.id
            assert ra.name == rb.name
            assert ra.type == rb.type
            assert ra.gid == rb.gid
            assert int(ra.x) == int(rb.x)
            assert int(ra.y) == int(rb.y)
            assert int(ra.width) == int(rb.width)
            assert int(ra.height) == int(rb.height)
            assert pytest.approx(ra.rotation) == rb.rotation
            assert ra.visible == rb.visible
            assert ra.properties == rb.properties


def _assert_map_meta(ref, out):
    assert ref.version == out.version
    assert ref.tiledversion == out.tiledversion
    assert (ref.renderorder or "right-down") == (out.renderorder or "right-down")
    assert ref.width == out.width
    assert ref.height == out.height
    assert ref.tilewidth == out.tilewidth
    assert ref.tileheight == out.tileheight
    assert ref.nextlayerid == out.nextlayerid
    assert ref.nextobjectid == out.nextobjectid
    assert ref.editorsettings_export == out.editorsettings_export
    assert ref.properties == out.properties


def _round_trip(map_path: Path, tmp_path: Path) -> None:
    parsed_in = parse_tmx(map_path)
    tmpl = MapTemplate.load_tmx(map_path)

    tileset_index = [(ts.name, None, ts.firstgid) for ts in parsed_in.tilesets]
    tsx_paths = [Path(p) for p in tmpl.tilesets]

    # Save alongside the source map so relative tileset paths remain valid
    out_path = map_path.parent / f"__roundtrip_{map_path.stem}.tmx"
    try:
        tmpl.save_tmx(
            out_path,
            tileset_index,
            tsx_paths,
            parsed_in.tilewidth,
            parsed_in.tileheight,
            parsed_tilesets=parsed_in.tilesets,
            parsed_layers=parsed_in.layers,
            parsed_object_layers=parsed_in.object_layers,
            map_properties=parsed_in.properties,
            map_version=parsed_in.version,
            map_tiledversion=parsed_in.tiledversion,
            nextlayerid=parsed_in.nextlayerid,
            nextobjectid=parsed_in.nextobjectid,
            include_editorsettings=parsed_in.editorsettings_export,
            renderorder=parsed_in.renderorder or "right-down",
        )

        parsed_out = parse_tmx(out_path)

        _assert_map_meta(parsed_in, parsed_out)
        _assert_tilesets_match(parsed_in, parsed_out)
        _assert_layers_match(parsed_in, parsed_out)
        _assert_object_layers_match(parsed_in, parsed_out)
    finally:
        try:
            out_path.unlink()
        except FileNotFoundError:
            pass


@pytest.mark.parametrize("map_path", GAME_MAP_PATHS)
def test_tmx_round_trip_noop(map_path: Path, tmp_path: Path) -> None:
    _round_trip(map_path, tmp_path)
