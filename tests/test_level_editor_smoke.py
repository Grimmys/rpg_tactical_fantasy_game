"""Editor entry-point and game-loader compatibility smoke tests."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pygame
import pytest

from src.level_editor.map_template import MapTemplate
from src.level_editor import object_model
from src.services.tmx_loader_core import parse_tmx


@pytest.fixture(scope="module", autouse=True)
def _display():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    if not pygame.get_init():
        pygame.init()
    if not pygame.display.get_init():
        pygame.display.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))
    yield
    # Do NOT call pygame.quit() here - it tears down the mixer.


def test_editor_module_imports():
    """Editor entry point can be imported without launching pygame UI."""
    from src.level_editor import editor_main
    assert callable(editor_main)


def test_main_module_exposes_editor_flag():
    """`python main.py --editor` is wired in the CLI parser."""
    text = Path("main.py").read_text(encoding="utf-8")
    assert "--editor" in text
    assert "editor_main" in text


def test_main_help_runs_without_starting_game(tmp_path: Path):
    """Running `python main.py --help` must not boot the game scene."""
    result = subprocess.run(
        [sys.executable, "main.py", "--help"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert "--editor" in result.stdout


def test_game_loader_parses_editor_saved_map(tmp_path: Path):
    """A map saved through the editor with editor-placed objects must be
    consumable by the existing game TMX parser (parse_tmx)."""
    tmpl = MapTemplate.create(10, 8)
    # Add canonical entity objects
    placement = object_model.place_object(tmpl, "placement", 1, 1)
    foe = object_model.place_object(tmpl, "foe", 2, 2)
    ally = object_model.place_object(tmpl, "ally", 3, 3)
    objective = object_model.place_object(tmpl, "objective", 4, 4)

    out = tmp_path / "editor_saved.tmx"
    tmpl.save_tmx(out, tileset_index=[], tsx_paths=[])

    parsed = parse_tmx(out)
    # Required tile layers
    assert "ground" in parsed.layers
    assert "obstacles" in parsed.layers
    # Required objectgroups
    assert "dynamic_data" in parsed.object_layers
    assert "events" in parsed.object_layers

    dyn_objs = parsed.object_layers["dynamic_data"].objects
    by_type = {o.type: o for o in dyn_objs}
    # All four MVP types present
    assert by_type["placement"].name == "placement"
    assert by_type["foe"].name == "skeleton"
    assert by_type["foe"].properties.get("level") == 1
    assert by_type["ally"].name == "jist"
    assert by_type["objective"].name == "Exit"
    assert by_type["objective"].properties.get("mission") == "main"
    assert by_type["objective"].properties.get("walkable") is True

    # Game loader-style coordinate convention: x/y are pixel coords aligned to tile size
    assert by_type["foe"].x == 2 * tmpl.tile_width
    assert by_type["foe"].y == 2 * tmpl.tile_height
