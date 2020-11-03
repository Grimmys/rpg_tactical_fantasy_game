import pygame as pg
from lxml import etree
import random

from src.Entity import Entity
from src.constants import TILE_SIZE

random.seed()


class Chest(Entity):
    def __init__(self, pos, sprite_close, sprite_open, potential_items):
        Entity.__init__(self, "Chest", pos, sprite_close)
        self.sprite_open_link = sprite_open
        self.sprite_close_link = sprite_close
        self.sprite_open = pg.transform.scale(pg.image.load(sprite_open).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        self.item = Chest.determine_item(potential_items)
        self.opened = False
        self.pick_lock_initiated = False

    @staticmethod
    def determine_item(potential_items):
        bag = []
        # probability : between 0.1 and 1
        for (item, probability) in potential_items:
            times = int(probability * 100)
            bag += [item] * times

        return random.choice(bag)

    def open(self):
        if not self.opened:
            self.sprite = self.sprite_open
            self.opened = True
            return self.item
        return None

    def save(self, tree_name):
        tree = Entity.save(self, tree_name)

        # Save state
        state = etree.SubElement(tree, 'state')
        state.text = str(self.opened)
        # Save sprites
        closed = etree.SubElement(tree, 'closed')
        closed_sprite = etree.SubElement(closed, 'sprite')
        closed_sprite.text = self.sprite_close_link

        opened = etree.SubElement(tree, 'opened')
        opened_sprite = etree.SubElement(opened, 'sprite')
        opened_sprite.text = self.sprite_open_link

        # Save content
        content = etree.SubElement(tree, 'contains')
        item = etree.SubElement(content, 'item')
        item.text = self.item.name

        return tree
