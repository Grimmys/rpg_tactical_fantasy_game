from __future__ import annotations

import pygame
from lxml import etree

from src.constants import TILE_SIZE


class Item:
    internal_identifier: int = 0

    def __init__(self, name: str, sprite: str, description: str, price: int = 0) -> None:
        self.name: str = name
        self.sprite: pygame.Surface = pygame.transform.scale(
            pygame.image.load(sprite).convert_alpha(),
            (TILE_SIZE, TILE_SIZE))
        self.description: str = description
        self.price: int = price
        self.resell_price: int = price // 2
        self.identifier: int = Item.internal_identifier
        Item.internal_identifier += 1

    def __str__(self) -> str:
        return self.name.replace('_', ' ').title().strip()

    def __eq__(self, it: Item) -> bool:
        return self.name == it.name

    def save(self, tree_name: str) -> etree.Element:
        # Build XML tree
        tree: etree.Element = etree.Element(tree_name)

        # Save name
        name: etree.SubElement = etree.SubElement(tree, 'name')
        name.text = self.name

        # Save resell price
        resell_price: etree.SubElement = etree.SubElement(tree, 'value')
        resell_price.text = str(self.resell_price)

        return tree
