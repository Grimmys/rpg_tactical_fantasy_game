"""Minimal TMX round-trip helper for editor experiments.

Reads a TMX, applies an optional property edit, writes it back, and re-loads
with pytmx to ensure the file stays compatible with the game loader.

Usage examples (run from repo root):
    python -m level_editor.tmx_roundtrip --input maps/level_0/map.tmx --output tmp/map_copy.tmx

    python -m level_editor.tmx_roundtrip --input maps/level_0/map.tmx --set-property example_key example_value
"""
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Optional

import pytmx


def _ensure_properties_element(root: ET.Element) -> ET.Element:
    properties = root.find("properties")
    if properties is None:
        properties = ET.SubElement(root, "properties")
    return properties


def set_property(root: ET.Element, key: str, value: str) -> None:
    """Add or replace a map-level property on the TMX root element."""
    properties = _ensure_properties_element(root)
    for prop in properties.findall("property"):
        if prop.attrib.get("name") == key:
            prop.attrib["value"] = value
            return
    ET.SubElement(properties, "property", name=key, value=value)


def round_trip(
    input_path: Path,
    output_path: Optional[Path] = None,
    transform: Optional[Callable[[ET.Element], None]] = None,
) -> Path:
    # Preserve tileset-relative paths by defaulting relative outputs next to the input TMX.
    if output_path and not output_path.is_absolute():
        output_path = input_path.parent / output_path

    tree = ET.parse(input_path)
    root = tree.getroot()

    if transform:
        transform(root)

    output = output_path or input_path
    tree.write(output, encoding="utf-8", xml_declaration=True)

    # Validate the written file still loads.
    pytmx.TiledMap(str(output))
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="TMX round-trip utility")
    parser.add_argument("--input", required=True, type=Path, help="Path to source TMX")
    parser.add_argument(
        "--output", type=Path, default=None, help="Optional output path (defaults to in-place)"
    )
    parser.add_argument(
        "--set-property",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Set or update a map-level property before writing",
    )

    args = parser.parse_args()

    def transform(root: ET.Element) -> None:
        if args.set_property:
            key, value = args.set_property
            set_property(root, key, value)

    output = round_trip(args.input, args.output, transform if args.set_property else None)
    print(f"Wrote TMX to {output}")


if __name__ == "__main__":
    main()
