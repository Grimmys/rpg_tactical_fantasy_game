"""
Defines useful dataclasses to organize the flow of information that should be displayed
in an informative pop-up.
"""
from collections import Callable
from enum import Enum
from typing import List, Union, Tuple, Dict

from src.game_entities.item import Item

Margin = Tuple[int, int, int, int]
# TODO: define precise dataclasses for entry and entries instead of only type aliases
Entry = Dict[
    str,
    Union[
        str,
        int,
        Margin,
        Dict[str, Dict[str, str]],
        List[any],
        Enum,
        Item,
        Callable,
        None,
    ],
]
EntryLine = List[Entry]
Entries = List[EntryLine]
