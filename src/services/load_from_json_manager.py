"""JSON loading utilities with precise type hints for class data.

This module loads the class growth / definition data from ``data/classes.json``.
The raw JSON may omit several optional fields (``constitution``, ``move``,
``skills``). We normalize those by injecting defaults and converting skill
names to fully built ``Skill`` instances via ``get_skill_data``.
"""

from __future__ import annotations

import json
from typing import NotRequired, TypedDict

from src.game_entities.skill import Skill
from .load_from_xml_manager import get_skill_data

CLASSES_DATA_PATH = "data/classes.json"


# NOTE: ``def`` is a reserved keyword in Python and cannot be used as a
# field name in the class-based ``TypedDict`` syntax. We therefore define
# ``StatsUp`` using the functional form so that we can keep the original JSON
# key names intact ("def" for defense, "str" for strength, etc.).
StatsUp = TypedDict(
    "StatsUp",
    {
        "hp": list[int],
        "def": list[int],
        "res": list[int],
        "str": list[int],
    },
    total=True,
)


class ClassEntry(TypedDict):
    """Typed structure for each class entry after normalization.

    constitution / move / skills may be missing in the source JSON and are
    therefore marked ``NotRequired``. After calling ``load_classes`` they will
    always be present (with defaults 0 / 0 / empty list or converted skills).
    """
    constitution: NotRequired[int]
    move: NotRequired[int]
    skills: NotRequired[list[Skill]]
    stats_up: StatsUp


def load_classes() -> dict[str, ClassEntry]:
    """Load, normalize and return the class data structure.

    Returns a mapping ``class_name -> ClassEntry`` with guaranteed presence of
    the optional keys (defaulted if absent) and converted skill objects.
    """
    with open(CLASSES_DATA_PATH, "r", encoding="utf-8") as file:
        classes: dict[str, ClassEntry] = json.load(file)

    for _class in classes.values():
        # Inject missing numeric defaults.
        _class.setdefault("constitution", 0)
        _class.setdefault("move", 0)

        # Ensure stats_up sub-keys exist as lists.
        stats = _class["stats_up"]
        stats.setdefault("hp", [])
        stats.setdefault("def", [])
        stats.setdefault("res", [])
        stats.setdefault("str", [])

        # Replace skill name strings by Skill instances.
        _class["skills"] = [
            get_skill_data(skill_name) for skill_name in _class.get("skills", ())
        ]

    return classes