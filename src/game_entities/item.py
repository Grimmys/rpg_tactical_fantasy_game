import pygame as pg
from lxml import etree

from src.constants import TILE_SIZE


class Item:
    internal_id = 0

    def __init__(self, name, sprite, description, price=0):
        self.name = name
        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.desc = description
        self.price = price
        self.resell_price = price // 2
        self.id = Item.internal_id
        Item.internal_id += 1

    def __str__(self):
        return self.name.replace('_', ' ').title().strip()

    def __eq__(self, it):
        return self.name == it.name

    def save(self, tree_name):
        # Build XML tree
        tree = etree.Element(tree_name)

        # Save name
        name = etree.SubElement(tree, 'name')
        name.text = self.name

        # Save resell price
        resell_price = etree.SubElement(tree, 'value')
        resell_price.text = str(self.resell_price)

        return tree
