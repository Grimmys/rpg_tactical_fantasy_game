from enum import Enum
import os

import pygame
from lxml import etree

from src.game_entities.entity import Entity
from src.gui.constantSprites import constant_sprites


class DamageKind(Enum):
    PHYSICAL = 'Physical'
    SPIRITUAL = 'Spiritual'


class Destroyable(Entity):

    def __init__(self, name, pos, sprite, hp, defense, res):
        Entity.__init__(self, name, pos, sprite)
        self.hp_max = hp
        self.hit_points = hp
        self.defense = defense
        self.res = res

        self.attack_sfx = pygame.mixer.Sound(os.path.join('sound_fx', 'attack.ogg'))

    def display_hp(self, screen):
        if self.hit_points != self.hp_max:
            damage_bar = constant_sprites['lightly_damaged']
            if self.hit_points < self.hp_max * 0.1:
                damage_bar = constant_sprites['almost_dead']
            elif self.hit_points < self.hp_max * 0.25:
                damage_bar = constant_sprites['severely_damaged']
            elif self.hit_points < self.hp_max * 0.5:
                damage_bar = constant_sprites['heavily_damaged']
            elif self.hit_points < self.hp_max * 0.75:
                damage_bar = constant_sprites['moderately_damaged']
            damage_bar = pygame.transform.scale(damage_bar,
                                                (int(damage_bar.get_width() *
                                                     (self.hit_points / self.hp_max)),
                                                 damage_bar.get_height()))
            screen.blit(constant_sprites['hp_bar'], self.position)
            screen.blit(damage_bar, self.position)

    def attacked(self, ent, damage, kind, allies):
        if kind is DamageKind.SPIRITUAL:
            real_damage = damage - self.res
        elif kind is DamageKind.PHYSICAL:
            real_damage = damage - self.defense
            pygame.mixer.Sound.play(self.attack_sfx)
        else:
            print('Error : Invalid kind of attack : ' + str(kind))
            raise SystemError
        if real_damage < 0:
            real_damage = 0
        elif real_damage > self.hit_points:
            real_damage = self.hit_points
        self.hit_points -= real_damage
        return self.hit_points

    def healed(self, value=None):
        if not value:
            # Full heal
            hp_recovered = self.hp_max - self.hit_points
        else:
            hp_recovered = value if self.hit_points + value <= self.hp_max \
                else self.hp_max - self.hit_points
        self.hit_points += hp_recovered
        return hp_recovered

    def save(self, tree_name):
        tree = Entity.save(self, tree_name)

        # Save current hp
        hit_points = etree.SubElement(tree, 'current_hp')
        hit_points.text = str(self.hit_points)

        return tree
