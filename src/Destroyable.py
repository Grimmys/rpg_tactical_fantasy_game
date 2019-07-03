import pygame as pg

from src.Entity import Entity
from src.constants import TILE_SIZE

LIGHTLY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_lightly_damaged.png'
LIGHTLY_DAMAGED = pg.transform.scale(pg.image.load(LIGHTLY_DAMAGED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
MODERATELY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_moderately_damaged.png'
MODERATELY_DAMAGED = pg.transform.scale(pg.image.load(MODERATELY_DAMAGED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
HEAVILY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_heavily_damaged.png'
HEAVILY_DAMAGED = pg.transform.scale(pg.image.load(HEAVILY_DAMAGED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
SEVERELY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_severely_damaged.png'
SEVERELY_DAMAGED = pg.transform.scale(pg.image.load(SEVERELY_DAMAGED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
ALMOST_DEAD_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_almost_dead.png'
ALMOST_DEAD = pg.transform.scale(pg.image.load(ALMOST_DEAD_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))
HP_BAR_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_sample.png'
HP_BAR = pg.transform.scale(pg.image.load(HP_BAR_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))


class Destroyable(Entity):
    def __init__(self, name, pos, sprite, hp, defense, res):
        Entity.__init__(self, name, pos, sprite)
        self.hp_max = hp
        self.hp = hp
        self.defense = defense
        self.res = res

    def get_defense(self):
        return self.defense

    def get_resistance(self):
        return self.res

    def display_hp(self, screen):
        if self.hp != self.hp_max:
            damage_bar = LIGHTLY_DAMAGED
            if self.hp < self.hp_max * 0.1:
                damage_bar = ALMOST_DEAD
            elif self.hp < self.hp_max * 0.25:
                damage_bar = SEVERELY_DAMAGED
            elif self.hp < self.hp_max * 0.5:
                damage_bar = HEAVILY_DAMAGED
            elif self.hp < self.hp_max * 0.75:
                damage_bar = MODERATELY_DAMAGED
            damage_bar = pg.transform.scale(damage_bar, (int(damage_bar.get_width() * self.hp / self.hp_max), damage_bar.get_height()))
            screen.blit(HP_BAR, self.pos)
            screen.blit(damage_bar, self.pos)

    def get_hp(self):
        return self.hp

    def get_hp_max(self):
        return self.hp_max

    def attacked(self, ent, damages):
        self.hp -= damages
        return self.hp > 0

    def healed(self, value):
        hp_recovered = value if self.hp + value <= self.hp_max else self.hp_max - self.hp
        self.hp += hp_recovered
        return hp_recovered
