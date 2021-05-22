from enum import Enum
import os
from typing import Union, Sequence

import pygame
from lxml import etree

from src.game_entities.entity import Entity
from src.gui.constant_sprites import constant_sprites


class DamageKind(Enum):
    PHYSICAL = 'Physical'
    SPIRITUAL = 'Spiritual'


class Destroyable(Entity):

    def __init__(self, name: str, pos: tuple[int, int], sprite: Union[str, pygame.Surface], hp: int,
                 defense: int, res: int) -> None:
        Entity.__init__(self, name, pos, sprite)
        self.hp_max: int = hp
        self.hit_points: int = hp
        self.defense: int = defense
        self.resistance: int = res
        self.attack_sfx: pygame.Sound = pygame.mixer.Sound(os.path.join('sound_fx', 'attack.ogg'))

    def display_hp(self, screen: pygame.Surface) -> None:
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

    def attacked(self, entity: Entity, damage: int,
                 kind: DamageKind, allies: Sequence[Entity]) -> int:
        if kind is DamageKind.SPIRITUAL:
            real_damage = damage - self.resistance
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

    def healed(self, value: int = None) -> int:
        if not value:
            # Full heal
            hp_recovered: int = self.hp_max - self.hit_points
        else:
            hp_recovered: int = value if self.hit_points + value <= self.hp_max \
                else self.hp_max - self.hit_points
        self.hit_points += hp_recovered
        return hp_recovered

    def save(self, tree_name: str) -> etree.Element:
        tree: etree.Element = Entity.save(self, tree_name)

        # Save current hp
        hit_points: etree.SubElement = etree.SubElement(tree, 'current_hp')
        hit_points.text = str(self.hit_points)

        return tree
