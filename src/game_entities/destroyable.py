from lxml import etree
from enum import Enum
import os

from src.game_entities.entity import Entity
from src.constants import *
from src.gui.constantSprites import constant_sprites


class DamageKind(Enum):
    PHYSICAL = 'Physical'
    SPIRITUAL = 'Spiritual'


class Destroyable(Entity):

    def __init__(self, name, pos, sprite, hp, defense, res):
        Entity.__init__(self, name, pos, sprite)
        self.hp_max = hp
        self.hp = hp
        self.defense = defense
        self.res = res

        self.attack_sfx = pg.mixer.Sound(os.path.join('sound_fx', 'attack.ogg'))

    def display_hp(self, screen):
        if self.hp != self.hp_max:
            damage_bar = constant_sprites['lightly_damaged']
            if self.hp < self.hp_max * 0.1:
                damage_bar = constant_sprites['almost_dead']
            elif self.hp < self.hp_max * 0.25:
                damage_bar = constant_sprites['severely_damaged']
            elif self.hp < self.hp_max * 0.5:
                damage_bar = constant_sprites['heavily_damaged']
            elif self.hp < self.hp_max * 0.75:
                damage_bar = constant_sprites['moderately_damaged']
            damage_bar = pg.transform.scale(damage_bar, (int(damage_bar.get_width() * (self.hp / self.hp_max)),
                                                         damage_bar.get_height()))
            screen.blit(constant_sprites['hp_bar'], self.pos)
            screen.blit(damage_bar, self.pos)

    def attacked(self, ent, damage, kind, allies):
        if kind is DamageKind.SPIRITUAL:
            real_damage = damage - self.res
        elif kind is DamageKind.PHYSICAL:
            real_damage = damage - self.defense
            pg.mixer.Sound.play(self.attack_sfx)
        else:
            print('Error : Invalid kind of attack : ' + str(kind))
            raise SystemError
        if real_damage < 0:
            real_damage = 0
        elif real_damage > self.hp:
            real_damage = self.hp
        self.hp -= real_damage
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
        hp = etree.SubElement(tree, 'current_hp')
        hp.text = str(self.hp)

        return tree
