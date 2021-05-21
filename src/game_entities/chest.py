import os
import random
from typing import Sequence, List, Union

import pygame
from lxml import etree

from src.game_entities.entity import Entity
from src.constants import TILE_SIZE
from src.game_entities.item import Item

random.seed()


class Chest(Entity):
    def __init__(self, position: tuple[int, int], sprite_close: str, sprite_open: str,
                 potential_items: Sequence[tuple[Item, float]]) -> None:
        Entity.__init__(self, "Chest", position, sprite_close)
        self.sprite_open_link: str = sprite_open
        self.sprite_close_link: str = sprite_close
        self.sprite_open: pygame.Surface = pygame.transform.scale(
            pygame.image.load(sprite_open).convert_alpha(),
            (TILE_SIZE, TILE_SIZE))
        self.item: Item = Chest.determine_item(potential_items)
        self.opened: bool = False
        self.pick_lock_initiated: bool = False
        self.chest_sfx: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join('sound_fx',
                                                                             'chest.ogg'))

    @staticmethod
    def determine_item(potential_items: Sequence[tuple[Item, float]]) -> Item:
        bag: List[Item] = []
        # probability : between 0.1 and 1
        for (item, probability) in potential_items:
            times = int(probability * 100)
            bag += [item] * times

        return random.choice(bag)

    def open(self) -> Union[Item, None]:
        if not self.opened:
            self.sprite = self.sprite_open
            self.opened = True
            pygame.mixer.Sound.play(self.chest_sfx)
            return self.item
        return None

    def save(self, tree_name: str) -> etree.Element:
        tree: etree.Element = Entity.save(self, tree_name)

        # Save state
        state: etree.SubElement = etree.SubElement(tree, 'state')
        state.text = str(self.opened)
        # Save sprites
        closed: etree.SubElement = etree.SubElement(tree, 'closed')
        closed_sprite = etree.SubElement(closed, 'sprite')
        closed_sprite.text = self.sprite_close_link

        opened: etree.SubElement = etree.SubElement(tree, 'opened')
        opened_sprite = etree.SubElement(opened, 'sprite')
        opened_sprite.text = self.sprite_open_link

        # Save content
        content: etree.SubElement = etree.SubElement(tree, 'contains')
        item: etree.SubElement = etree.SubElement(content, 'item')
        item.text = self.item.name

        return tree
