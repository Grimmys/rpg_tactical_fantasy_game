"""
Defines useful dataclasses to organize the flow of information that should be displayed
in an informative pop-up.
"""
from collections import Callable
from enum import Enum
from typing import List, Union

from src.game_entities.item import Item

Margin = tuple[int, int, int, int]
# TODO: define precise dataclasses for entry and entries instead of only type aliases
Entry = dict[
    str,
    Union[
        str,
        int,
        Margin,
        dict[str, dict[str, str]],
        List[any],
        Enum,
        Item,
        Callable,
        None,
    ],
]
EntryLine = List[Entry]
Entries = List[EntryLine]
