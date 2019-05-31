import pygame as pg
import random
random.seed()

from src.Entity import Entity

TILE_SIZE = 48

class Chest(Entity):
    def __init__(self, name, pos, sprite_close, sprite_open, potential_items):
        Entity.__init__(self, name, pos, sprite_close)
        self.sprite_open = pg.transform.scale(pg.image.load(sprite_open).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.item = Chest.determine_item(potential_items)
        self.opened = False

    @staticmethod
    def determine_item(potential_items):
        bag = []
        # entry : (proba, item)
        # proba : between 0.1 and 1
        for entry in potential_items:
            times = int(entry[0] * 10)
            bag += [entry[1]] * times

        return random.choice(bag)

    def is_open(self):
        return self.opened

    def open(self):
        self.sprite = self.sprite_open
        self.opened = True
        return self.item
