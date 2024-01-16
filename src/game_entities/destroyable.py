"""
Defines Destroyable class, an entity that could be destroyed.
"""

import os
from collections.abc import Sequence
from enum import Enum
from typing import Union

import pygame
from lxml import etree

from src.game_entities.entity import Entity
from src.gui.constant_sprites import constant_sprites
from src.gui.position import Position


class DamageKind(Enum):
    """
    Defines the different kind of damage that could be done to a destroyable entity.
    """

    PHYSICAL = "Physical"
    SPIRITUAL = "Spiritual"


class Destroyable(Entity):
    """
    A Destroyable is simply an entity that can take damage and eventually disappear after
    taking too much damage.

    Keyword arguments:
    name -- the name of the entity
    position -- the current position of the entity on screen
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen or
    the relative path to the visual representation of the entity
    hit_points -- the total of damage that the entity can take before disappearing
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks

    Attributes:
    hit_points_max -- the maximum of hit points the entity could have
    hit_points -- the current number of hit points of the entity
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks
    attack_sfx -- the sound that should be started when the entity is taking physical damage
    """

    def __init__(
        self,
        name: str,
        position: Position,
        sprite: Union[str, pygame.Surface],
        hit_points: int,
        defense: int,
        resistance: int,
    ) -> None:
        super().__init__(name, position, sprite)
        self.hit_points_max: int = hit_points
        self.hit_points: int = hit_points
        self.defense: int = defense
        self.resistance: int = resistance
        self.attack_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "attack.ogg")
        )

    def display_hit_points(self, screen: pygame.Surface) -> None:
        """
        Displays a bar indicating the ratio of hit points of the entity relatively to
        the maximum it could have.

        Keyword arguments:
        screen -- the screen on which the bar should be drawn
        """
        if self.hit_points != self.hit_points_max:
            damage_bar = constant_sprites["lightly_damaged"]
            if self.hit_points < self.hit_points_max * 0.1:
                damage_bar = constant_sprites["almost_dead"]
            elif self.hit_points < self.hit_points_max * 0.25:
                damage_bar = constant_sprites["severely_damaged"]
            elif self.hit_points < self.hit_points_max * 0.5:
                damage_bar = constant_sprites["heavily_damaged"]
            elif self.hit_points < self.hit_points_max * 0.75:
                damage_bar = constant_sprites["moderately_damaged"]
            damage_bar = pygame.transform.scale(
                damage_bar,
                (
                    int(
                        damage_bar.get_width() * (self.hit_points / self.hit_points_max)
                    ),
                    damage_bar.get_height(),
                ),
            )
            screen.blit(constant_sprites["hp_bar"], self.position)
            screen.blit(damage_bar, self.position)

    def attacked(
        self, entity: Entity, damage: int, kind: DamageKind, allies: Sequence[Entity]
    ) -> int:
        """
        Compute how much the entity should take and reduce the hit points of
        the entity by this value.

        Play a sound according to the kind of the damage.

        Return the current hit points of the entity after applying the damage.

        Keyword arguments:
        entity -- the other entity that is attacking the entity
        damage -- the attack's power
        kind -- the nature of the attack
        allies -- the allies of the entity
        """
        if kind is DamageKind.SPIRITUAL:
            real_damage = damage - self.resistance
        elif kind is DamageKind.PHYSICAL:
            real_damage = damage - self.defense
            pygame.mixer.Sound.play(self.attack_sfx)
        else:
            print(f"Error : Invalid kind of attack : {kind}")
            raise SystemError
        if real_damage < 0:
            real_damage = 0
        elif real_damage > self.hit_points:
            real_damage = self.hit_points
        self.hit_points -= real_damage
        return self.hit_points

    def healed(self, value: int = None) -> int:
        """
        Heal the entity by the given amount. If the amount is superior to the maximum of hit points,
        the entity is fully healed.

        Return the number of hit points recovered.

        Keyword arguments:
        value -- the number of hit points that should be recovered
        """
        if not value:
            # Full heal
            hp_recovered: int = self.hit_points_max - self.hit_points
        else:
            hp_recovered: int = (
                value
                if self.hit_points + value <= self.hit_points_max
                else self.hit_points_max - self.hit_points
            )
        self.hit_points += hp_recovered
        return hp_recovered

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the destroyable entity in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save current hp
        hit_points: etree.SubElement = etree.SubElement(tree, "current_hp")
        hit_points.text = str(self.hit_points)

        return tree
