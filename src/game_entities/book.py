"""
Defines Book, an item that is a book and can be read
"""

from src.game_entities.item import Item
from pathlib import Path


class Book(Item):
    """
    A Book is a particular item that some characters are able to read.
    This item is generally not disappearing after use.

    Keyword arguments:
    name -- the name of the item
    sprite_path -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    """

    def __init__(self, name: str, sprite_path: Path, description: str, price: int):
        super().__init__(name, sprite_path, description, price)
