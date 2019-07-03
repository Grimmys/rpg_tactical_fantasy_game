import pygame as pg

from src.Entity import Entity
from src.constants import TILE_SIZE

ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)


class Fountain(Entity):
    def __init__(self, name, pos, sprite, sprite_empty, effect, times):
        Entity.__init__(self, name, pos, sprite)
        self.effect = effect
        self.times = times
        self.sprite_empty = pg.transform.scale(pg.image.load(sprite_empty).convert_alpha(), (TILE_SIZE, TILE_SIZE))

    def drink(self, ent):
        entries = []
        if self.times > 0:
            result = self.effect.apply_on_ent(ent)
            if result[0]:
                self.times -= 1
                if self.times == 0:
                    self.sprite = self.sprite_empty
            entries.append([{'type': 'text', 'text': result[1], 'font': ITEM_DESC_FONT}])
            entries.append([{'type': 'text', 'text': str(self.times) + " remaining uses.", 'font': ITEM_DESC_FONT}])
        else:
            entries.append([{'type': 'text', 'text': 'The fountain is empty...', 'font': ITEM_DESC_FONT}])
        return entries
