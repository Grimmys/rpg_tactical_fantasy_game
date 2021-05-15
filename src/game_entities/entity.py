import re
from typing import Union

import pygame
from lxml import etree

from src.constants import TILE_SIZE


class Entity:
    def __init__(self, name: str, position: tuple[int, int], sprite: Union[str, pygame.Surface]) \
            -> None:
        self.name: str = name
        self.position: tuple[int, int] = position
        self.sprite: pygame.Surface = sprite if isinstance(sprite, pygame.Surface) \
            else pygame.transform.scale(pygame.image.load(sprite).convert_alpha(),
                                        (TILE_SIZE, TILE_SIZE))

    def display(self, screen: pygame.Surface) -> None:
        screen.blit(self.sprite, self.position)

    def get_rect(self) -> pygame.Rect:
        return self.sprite.get_rect(topleft=self.position)

    def __str__(self) -> str:
        string_entity: str = self.name.replace('_', ' ').title()
        string_entity = re.sub(r'[0-9]+', '', string_entity)  # Remove numbers like the id
        return string_entity.strip()

    def is_on_pos(self, position: tuple[int, int]) -> bool:
        return self.get_rect().collidepoint(position)

    def save(self, tree_name: str) -> etree.Element:
        # Build XML tree
        tree: etree.Element = etree.Element(tree_name)

        # Save name
        name: etree.SubElement = etree.SubElement(tree, 'name')
        name.text = self.name

        # Save position
        position: etree.SubElement = etree.SubElement(tree, 'position')
        x_coordinate: etree.SubElement = etree.SubElement(position, 'x')
        x_coordinate.text = str(self.position[0] // TILE_SIZE)
        y_coordinate: etree.SubElement = etree.SubElement(position, 'y')
        y_coordinate.text = str(self.position[1] // TILE_SIZE)

        return tree
