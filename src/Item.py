import pygame as pg
from src.constants import TILE_SIZE


class Item:
    internal_id = 0

    def __init__(self, name, sprite, description, price=0):
        self.name = name
        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.desc = description
        self.price = price
        self.id = Item.internal_id
        Item.internal_id += 1

    def get_formatted_name(self):
        return self.name.replace('_', ' ').title()
