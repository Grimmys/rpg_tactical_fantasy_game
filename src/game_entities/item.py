"""
Defines Item, the base class for all items in the game.
"""

from __future__ import annotations

import pygame

from src.constants import TILE_SIZE
from src.services.language import *


class Item:
    """
    An Item is something that can be found in a chest, in a house or bought at a shop.
    Until be used, it will stay on the inventory of the entity that is currently bearing it.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that may be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought

    Attributes:
    name -- the name of the item
    sprite -- the pygame surface representing the item on screen
    sprite_path -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    resell_price -- the price at which the item can be sold in a shop by a player
    identifier -- the unique value identifying the item
    """

    internal_identifier: int = 0

    def __init__(
        self, name: str, sprite: str, description: str, price: int = 0
    ) -> None:
        self.name: str = name
        self.sprite: pygame.Surface = pygame.transform.scale(
            pygame.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.sprite_path: str = sprite
        self.description: str = description
        self.price: int = price
        self.resell_price: int = price // 2
        self.identifier: int = Item.internal_identifier
        Item.internal_identifier += 1

    def __str__(self) -> str:
        try:
            return TRANSLATIONS["items"][self.name]
        except KeyError:
            return self.name.replace("_", " ").title().strip()

    def __eq__(self, item: Item) -> bool:
        return self.name == item.name

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the item in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        # Build XML tree
        tree: etree.Element = etree.Element(tree_name)

        # Save name
        name: etree.SubElement = etree.SubElement(tree, "name")
        name.text = self.name

        # Save resell price
        resell_price: etree.SubElement = etree.SubElement(tree, "value")
        resell_price.text = str(self.resell_price)

        return tree
