import re

import pygame as pg
from lxml import etree

from src.constants import TILE_SIZE


class Entity:
    def __init__(self, name, pos, sprite):
        self.name = name
        self.pos = pos
        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

    def display(self, screen):
        screen.blit(self.sprite, self.pos)

    def get_rect(self):
        return self.sprite.get_rect(topleft=self.pos)

    def __str__(self):
        s = self.name.replace('_', ' ').title()
        return re.sub(r'[0-9]+', '', s)  # Remove numbers like the id

    def get_formatted_name(self):
        s = self.name.replace('_', ' ').title()
        return re.sub(r'[0-9]+', '', s)  # Remove numbers like the id

    def is_on_pos(self, pos):
        return self.get_rect().collidepoint(pos)

    def save(self, tree_name):
        # Build XML tree
        tree = etree.Element(tree_name)

        # Save name
        name = etree.SubElement(tree, 'name')
        name.text = self.name

        # Save position
        pos = etree.SubElement(tree, 'position')
        x = etree.SubElement(pos, 'x')
        x.text = str(self.pos[0] // TILE_SIZE)
        y = etree.SubElement(pos, 'y')
        y.text = str(self.pos[1] // TILE_SIZE)

        return tree
