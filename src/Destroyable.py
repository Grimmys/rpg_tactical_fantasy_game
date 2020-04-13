import pygame as pg
from lxml import etree
from enum import Enum, auto

from src.Entity import Entity
from src.constants import *

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


class DamageKind(Enum):
    PHYSICAL = auto(),
    SPIRITUAL = auto()


class Destroyable(Entity):
    def __init__(self, name, pos, sprite, hp, defense, res):
        Entity.__init__(self, name, pos, sprite)
        self.hp_max = hp
        self.hp = hp
        self.defense = defense
        self.res = res

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

    def set_current_hp(self, hp):
        self.hp = hp

    def attacked(self, ent, damages, kind):
        if kind is DamageKind.SPIRITUAL:
            real_damages = damages - self.res
        elif kind is DamageKind.PHYSICAL:
            real_damages = damages - self.defense
        if real_damages < 0:
            real_damages = 0
        self.hp -= real_damages
        return self.hp > 0

    def healed(self, value=None):
        if not value:
            # Full heal
            hp_recovered = self.hp_max - self.hp
        else:
            hp_recovered = value if self.hp + value <= self.hp_max else self.hp_max - self.hp
        self.hp += hp_recovered
        return hp_recovered

    def save(self, tree_name):
        tree = Entity.save(self, tree_name)

        # Save current hp
        hp = etree.SubElement(tree, 'currentHp')
        hp.text = str(self.hp)

        return tree


