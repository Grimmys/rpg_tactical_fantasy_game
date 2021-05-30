"""
Defines Book, an item that is a book and can be read
"""

from src.game_entities.item import Item


class Book(Item):
    """
    A Book is a particular item that some characters are able to read.
    This item is generally not disappearing after use.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    """

    def __init__(self, name: str, sprite: str, description: str, price: int):
        super().__init__(name, sprite, description, price)
