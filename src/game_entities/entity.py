import re

import pygame
from lxml import etree

from src.constants import TILE_SIZE


class Entity:
    def __init__(self, name, position, sprite):
        self.name = name
        self.position = position
        self.sprite = sprite if isinstance(sprite, pygame.Surface) \
            else pygame.transform.scale(pygame.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

    def display(self, screen):
        screen.blit(self.sprite, self.position)

    def get_rect(self):
        return self.sprite.get_rect(topleft=self.position)

    def __str__(self):
        string_entity = self.name.replace('_', ' ').title()
        string_entity = re.sub(r'[0-9]+', '', string_entity)  # Remove numbers like the id
        return string_entity.strip()

    def is_on_pos(self, position):
        return self.get_rect().collidepoint(position)

    def save(self, tree_name):
        # Build XML tree
        tree = etree.Element(tree_name)

        # Save name
        name = etree.SubElement(tree, 'name')
        name.text = self.name

        # Save position
        position = etree.SubElement(tree, 'position')
        x_coordinate = etree.SubElement(position, 'x')
        x_coordinate.text = str(self.position[0] // TILE_SIZE)
        y_coordinate = etree.SubElement(position, 'y')
        y_coordinate.text = str(self.position[1] // TILE_SIZE)

        return tree
