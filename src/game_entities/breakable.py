"""
Defines Breakable class, a static Destroyable object that is an element of the background.
Generally, this class helps to represent breakable walls.
"""

from __future__ import annotations

import pygame
from lxml import etree

from src.game_entities.destroyable import Destroyable
from src.gui.constant_sprites import constant_sprites


class Breakable(Destroyable):
    """
    A Breakable represent an element of the background that can be destroyed, like a brittle wall.
    At display time, some cracks are added to the sprite of the entity to differentiate it from
    other elements that might be similar but un-breakable.

    Keyword arguments:
    position -- the current position of the entity on screen
    sprite -- the relative path to the visual representation of the entity
    hit_points -- the total of damage that the entity can take before disappearing
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks

    Attributes:
    sprite_link -- the relative path to the visual representation of the element
    """

    def __init__(
        self,
        position: tuple[int, int],
        sprite: str,
        hit_points: int,
        defense: int,
        resistance: int,
    ) -> None:
        super().__init__("Breakable", position, sprite, hit_points, defense, resistance)
        # Useful in case of saving
        self.sprite_link: str = sprite

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the entity on the given screen and adding some cracks on it to add emphasis to its
        fragile nature.

        Keyword arguments:
        screen -- the screen on which the entity should be drawn
        """
        super().display(screen)
        screen.blit(constant_sprites["cracked"], self.position)

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the breakable entity in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save sprite
        sprite: etree.SubElement = etree.SubElement(tree, "sprite")
        sprite.text = self.sprite_link

        return tree
