"""
Defines Key class, an item permitting to unlock specific entities.
"""

from src.game_entities.item import Item


class Key(Item):
    """
    A Key is an Item that can permits to open doors or chests.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    for_chest -- whether the key can be used to open a chest or not
    for_door -- whether the key can be used to open a door or not

    Attributes:
    for_chest -- whether the key can be used to open a chest or not
    for_door -- whether the key can be used to open a door or not
    """

    def __init__(
        self,
        name: str,
        sprite: str,
        description: str,
        price: int,
        for_chest: bool,
        for_door: bool,
    ) -> None:
        super().__init__(name, sprite, description, price)
        self.for_chest: bool = for_chest
        self.for_door: bool = for_door
