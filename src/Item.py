import pygame as pg
from src.constants import TILE_SIZE


class Item:
    id = 0

    def __init__(self, name, sprite, description):
        self.name = name
        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.desc = description
        self.id = Item.id
        Item.id += 1

    def get_name(self):
        return self.name

    def get_formatted_name(self):
        return self.name.replace('_', ' ').title()

    def get_description(self):
        return self.desc

    def get_sprite(self):
        return self.sprite

    def get_id(self):
        return self.id
