"""
Defines Entity class, the base class of all game objects that could be display on the level map.
"""

import re
from typing import Union

import pygame

from src.constants import TILE_SIZE
from src.gui.position import Position
from src.services.language import *


class Entity:
    """
    An Entity is any game object that can take place on the level map. An Entity could be static,
    living or only be an object that player can interact with.

    Keyword arguments:
    name -- the name of the entity
    position -- the current position of the entity on screen
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen or
    the relative path to the visual representation of the entity

    Attributes:
    name -- the name of the entity
    position -- the current position of the entity on screen
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen, it should
    match the size of a tile
    """

    def __init__(
        self, name: str, position: Position, sprite: Union[str, pygame.Surface]
    ) -> None:
        self.name: str = name
        self.position: Position = position
        self.sprite: pygame.Surface = (
            sprite
            if isinstance(sprite, pygame.Surface)
            else pygame.transform.scale(
                pygame.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE)
            )
        )

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the entity on the given screen.

        Keyword arguments:
        screen -- the screen on which the entity should be drawn
        """
        screen.blit(self.sprite, self.position)

    def get_rect(self) -> pygame.Rect:
        """
        Return the pygame Rect of the sprite of the entity.
        """
        return self.sprite.get_rect(topleft=self.position)

    def __str__(self) -> str:
        """
        Return the formatted text version of the entity based on its name,
        underscores are replaced by spaces and numbers are removed.
        """
        try:
            string_entity: str = TRANSLATIONS["entity_names"][
                self.get_proper_entity_name(self.name).lower()
            ]
        except KeyError:
            string_entity: str = self.name.replace("_", " ").title()
            string_entity = self.get_proper_entity_name(string_entity)
        return string_entity.strip()

    def is_on_position(self, position: Position) -> bool:
        """
        Return whether the entity is colliding with the given position or not.

        Keyword arguments:
        position -- the given position that should be compared with the entity position
        """
        return self.get_rect().collidepoint(position)

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the entity in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        # Build XML tree
        tree: etree.Element = etree.Element(tree_name)

        # Save name
        name: etree.SubElement = etree.SubElement(tree, "name")
        name.text = self.name

        # Save position
        position: etree.SubElement = etree.SubElement(tree, "position")
        x_coordinate: etree.SubElement = etree.SubElement(position, "x")
        x_coordinate.text = str(int(self.position[0] // TILE_SIZE))
        y_coordinate: etree.SubElement = etree.SubElement(position, "y")
        y_coordinate.text = str(int(self.position[1] // TILE_SIZE))

        return tree

    @staticmethod
    def get_proper_entity_name(string_entity: str) -> str:
        """
        Return string that removed numbers like the id
        """
        return re.sub(r"[0-9]+", "", string_entity)
