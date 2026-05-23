# Level Editor — MVP Guide

A minimal TMX-based map editor for the RPG Tactical Fantasy Game.
This document describes how to launch the editor and the conventions it expects
TMX maps to follow.

## Launching

From the repository root (with the project's virtual environment active or via
`uv run`):

```powershell
python main.py --editor
# Positional shortcut:
python main.py --editor maps/level_0/map.tmx
# Or the explicit form:
python main.py --editor --editor-template maps/level_0/map.tmx
# Custom dimensions for a brand-new empty map:
python main.py --editor --editor-width 30 --editor-height 20
```

If a TMX path is provided, the editor loads that map. Otherwise it starts with
an empty 22×14 tile map. Saves are written back to TMX (in place by default).

## Required Tile Layers

The editor preserves whatever tile layers exist in the source TMX, but the
canonical campaign layers are:

| Layer       | Purpose                                       |
|-------------|-----------------------------------------------|
| `ground`    | Walkable terrain tiles                        |
| `obstacles` | Impassable terrain / scenery                  |

When creating a new map the editor only seeds `ground` and `obstacles`.
Additional tile layers found in an existing TMX (e.g. a future `decor`) are
loaded, preserved on save, and keep their original opacity / draw order.

## Required Object Groups

| Object group   | Required | Purpose                                                                 |
|----------------|----------|-------------------------------------------------------------------------|
| `dynamic_data` | Yes      | Holds gameplay-relevant objects: placements, foes, allies, objectives, buildings, chests, fountains, doors, portals. |
| `events`       | Yes      | Holds map events (dialog triggers, mission flags). |

Both groups are preserved when present. Editor object placement only writes to
`dynamic_data`.

## Supported Object Types (MVP)

The editor supports placing, replacing, and deleting the following object
types only. Other object types (buildings, chests, fountains, doors, etc.) are
**preserved** through round-trip but cannot currently be edited via the UI.

| Type        | Default name | Required properties             | Notes                                  |
|-------------|--------------|---------------------------------|----------------------------------------|
| `placement` | `placement`  | (none)                          | Spawn slot for a player character.     |
| `foe`       | `skeleton`   | `level: int` (default 1)        | Enemy unit.                            |
| `ally`      | `jist`       | (none)                          | Allied non-player unit.                |
| `objective` | `Exit`       | `mission: str`, `walkable: bool`| Mission objective tile. Defaults: `mission="main"`, `walkable=true`. |

All editor-placed objects:

- Use the tile width / height of the map for `width` and `height` (32×32 by default).
- Have `x` / `y` snapped to tile boundaries (top-left corner of the tile in
  pixel coordinates).
- Receive a fresh `id` that does not collide with any existing TMX object id.

## Editing Controls

| Action                                  | Input                              |
|-----------------------------------------|------------------------------------|
| Switch to tile-paint tool               | `B`                                |
| Switch to eraser tool                   | `E`                                |
| Switch to eyedropper (in tile tool)     | Right-click on map                 |
| Switch to object tool                   | `O`                                |
| Cycle active object type (forward)      | `Tab` or `]`                       |
| Cycle active object type (backward)     | `[`                                |
| Place active object at cursor           | Left-click (with object tool)      |
| Delete editable object at cursor        | Right-click (with object tool)     |
| Save map                                | `Ctrl+S` (in-editor)               |

Placing an object on a tile that already holds an *editable* object of any
supported type replaces it. Unsupported objects (buildings, chests, ...) at
the same cell are left untouched — the editor will not destroy them.

## Save / Round-Trip Guarantees

The editor's save path preserves the following from the source TMX:

- All tile and object layers, in their original order.
- Layer opacity and visibility flags.
- The set of tilesets referenced by the map.
- All object groups, object ids, object types, and object properties for
  types **not** managed by the editor (buildings, chests, fountains, doors,
  portals, events, etc.).
- Property *type information* on object properties (booleans stay booleans,
  ints stay ints, etc.).

The TMX header fields (`version`, `tiledversion`, `renderorder`) and any
`<editorsettings>/<export>` block are captured at load time and rewritten on
save when no override is supplied.

These guarantees are exercised by:

- [tests/test_tmx_roundtrip_editor.py](tests/test_tmx_roundtrip_editor.py)
- [tests/test_level_editor_objects.py](tests/test_level_editor_objects.py)
- [tests/test_level_editor_smoke.py](tests/test_level_editor_smoke.py)

## Current MVP Limitations

The following are intentionally out of scope for the initial editor MVP:

- **No UI picker for foe / ally species** — placed foes default to `skeleton`,
  allies default to `jist`. Other species must be edited in the TMX directly.
- **Objective name** is fixed to `"Exit"` when placed.
- **No editing of buildings, chests, fountains, doors, portals or events**
  in the UI. They are preserved on save but must be authored in Tiled.
- **No property editor panel** — properties beyond the defaults must be set in
  Tiled.
- **No undo / redo**.
- **No multi-tile selection or marquee tools**.
- **No new tile layer / object layer creation** — the editor uses the layers
  already present in the TMX (or seeds `ground` + `obstacles` for brand-new
  maps).
- **Tileset palette** is loaded from the TMX's referenced tilesets only;
  adding new tilesets must be done in Tiled.

## Map Authoring Conventions

When authoring or hand-editing maps to remain compatible with the game and
editor:

1. Object `x` / `y` must be the **top-left pixel** of the target tile
   (multiples of `tilewidth` / `tileheight`).
2. Foe objects must include a `level` property (positive integer).
3. Objective objects must include `mission` (string) and `walkable` (bool).
4. Keep the `dynamic_data` and `events` object groups present even if empty —
   the game loader expects them.
5. Do not rename the `ground` / `obstacles` tile layers.
