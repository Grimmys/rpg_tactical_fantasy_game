"""Editor runtime state container."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from ..map_template import MapTemplate


@dataclass
class EditorState:
    tmpl: MapTemplate
    tileset_names: List[str]
    selected_gid: int = 0
    current_layer: str = "ground"
    tool: str = "PAINT"
    rect_active: bool = False
    rect_start: Optional[Tuple[int, int]] = None
    rect_current: Optional[Tuple[int, int]] = None
    active_tileset_index: int = 0
    save_as_active: bool = False
    save_input: str = ""
    save_message: str = ""
    load_active: bool = False
    load_input: str = ""
    load_message: str = ""
    load_files: List[Path] = field(default_factory=list)
    load_index: int = 0
    help_active: bool = False
    dirty: bool = False

    def reset_rect(self) -> None:
        self.rect_active = False
        self.rect_start = None
        self.rect_current = None
