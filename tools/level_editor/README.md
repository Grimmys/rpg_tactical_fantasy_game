# Level Editor (Prototype)

This is a minimal, working level editor to kickstart custom map creation.
It paints GIDs (global tile IDs) from real Tiled TSX tilesets and saves/loads templates in JSON.

## Concepts

- Tilesets: TSX files under `imgs/tiled_tilesets/` (e.g., `dungeon.tsx`, `houses.tsx`).
  - The editor reads TSX metadata (tile size, tilecount, image or per-tile images) and pre-slices thumbnails.
  - Firstgid offsets are computed cumulatively in the order the TSX files are loaded.
- Map Template: `{ width, height, grid, tilesets? }` where `grid[y][x]` stores a GID (0 = empty)
  - The optional `tilesets` array stores the TSX list (relative paths) to preserve firstgid ordering when reloading.

## Run the editor

From the project root (no PYTHONPATH needed):

```powershell
# Width=22, Height=14, optional template path
python level_editor.py 22 14 maps\editor_templates\template.json
```

Controls:
- Left click (grid): paint current tile (GID) on a cell
- Right click (grid): eyedrop (pick GID from cell)
- Mouse wheel (over palette): scroll tiles in the active tileset tab
- Click a tileset tab to switch; click a tile thumbnail to select it
- Number keys 1..9: quick-select a visible tile in the active tab
- P: Paint tool (default)
- R: Rectangle fill tool (click-drag to fill a rectangle)
- F: Flood fill (click a region to fill contiguous tiles of the same type)
- H: Toggle help overlay with controls
- S: Save to JSON (to the provided template path or `maps/editor_templates/template.json`)
- L: Load from JSON (same path)
- ESC/Window close: Exit

### Saving to a specific location

- Ctrl+S: Save to the current path (shown in the console when saving)
- Ctrl+Shift+S or F2: Open a Save As modal; type a relative or absolute path and press Enter
  - Relative paths will be saved under `maps/editor_templates/`
  - The `.json` extension is added automatically if missing

## Notes

- The editor loads all `.tsx` under `imgs/tiled_tilesets/` by default (alphabetically).
- When saving, the current tileset order is saved into the JSON so firstgid stays stable on reload.
- TMX export/import and multi-layer editing will come next.
