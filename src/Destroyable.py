from lxml import etree
from enum import Enum

from src.Entity import Entity
from src.constants import *

LIGHTLY_DAMAGED = None
MODERATELY_DAMAGED = None
HEAVILY_DAMAGED = None
SEVERELY_DAMAGED = None
ALMOST_DEAD = None
HP_BAR = None


class DamageKind(Enum):
    PHYSICAL = 'Physical'
    SPIRITUAL = 'Spiritual'


class Destroyable(Entity):
    @staticmethod
    def init_constant_sprites():
        global LIGHTLY_DAMAGED, MODERATELY_DAMAGED, HEAVILY_DAMAGED, SEVERELY_DAMAGED, ALMOST_DEAD, HP_BAR

        lightly_damaged_sprite = 'imgs/dungeon_crawl/misc/damage_meter_lightly_damaged.png'
        LIGHTLY_DAMAGED = pg.transform.scale(pg.image.load(lightly_damaged_sprite).convert_alpha(),
                                             (TILE_SIZE, TILE_SIZE))
        moderately_damaged_sprite = 'imgs/dungeon_crawl/misc/damage_meter_moderately_damaged.png'
        MODERATELY_DAMAGED = pg.transform.scale(pg.image.load(moderately_damaged_sprite).convert_alpha(),
                                                (TILE_SIZE, TILE_SIZE))
        heavily_damaged_sprite = 'imgs/dungeon_crawl/misc/damage_meter_heavily_damaged.png'
        HEAVILY_DAMAGED = pg.transform.scale(pg.image.load(heavily_damaged_sprite).convert_alpha(),
                                             (TILE_SIZE, TILE_SIZE))
        severely_damaged_sprite = 'imgs/dungeon_crawl/misc/damage_meter_severely_damaged.png'
        SEVERELY_DAMAGED = pg.transform.scale(pg.image.load(severely_damaged_sprite).convert_alpha(),
                                              (TILE_SIZE, TILE_SIZE))
        almost_dead_sprite = 'imgs/dungeon_crawl/misc/damage_meter_almost_dead.png'
        ALMOST_DEAD = pg.transform.scale(pg.image.load(almost_dead_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

        hp_bar_sprite = 'imgs/dungeon_crawl/misc/damage_meter_sample.png'
        HP_BAR = pg.transform.scale(pg.image.load(hp_bar_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

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
            damage_bar = pg.transform.scale(damage_bar, (int(damage_bar.get_width() * self.hp / self.hp_max),
                                                         damage_bar.get_height()))
            screen.blit(HP_BAR, self.pos)
            screen.blit(damage_bar, self.pos)

    def set_current_hp(self, hp):
        self.hp = hp

    def attacked(self, ent, damages, kind):
        if kind is DamageKind.SPIRITUAL:
            real_damages = damages - self.res
        elif kind is DamageKind.PHYSICAL:
            real_damages = damages - self.defense
        else:
            print('Error : Invalid kind of attack : ' + str(kind))
            raise SystemError
        if real_damages < 0:
            real_damages = 0
        self.hp -= real_damages
        return self.hp

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
