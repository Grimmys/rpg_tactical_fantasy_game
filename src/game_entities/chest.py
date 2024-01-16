"""
Defines Chest class, corresponding to an entity that could be opened by a player and containing gold
or items.
"""

from __future__ import annotations

import os
import random
from collections.abc import Sequence
from typing import Optional

import pygame
from lxml import etree

from src.constants import TILE_SIZE
from src.game_entities.entity import Entity
from src.game_entities.item import Item
from src.gui.position import Position

random.seed()


class Chest(Entity):
    """
    A Chest is an entity that contains an item.
    It can be open by a character if he has a valid key or
    has a skill permitting to open such a chest.

    Keyword arguments:
    position -- the current position of the entity on screen
    sprite_close -- the relative path to the visual representation of the chest when closed
    sprite_open -- the relative path to the visual representation of the chest when opened
    potential_items -- the items that could be found in the chest
    sprite -- the pygame Surface corresponding to the appearance of the chest on screen,
    would be loaded from sprite_close if not provided

    Attributes:
    sprite_close_link -- the relative path to the visual representation of the chest when closed
    sprite_open_link -- the relative path to the visual representation of the chest when opened
    sprite_open -- the pygame Surface corresponding to the representation on screen of the chest
    when opened
    item -- the item that is hidden in the chest
    opened -- a boolean value indicating whether the chest is opened or not
    pick_lock_initiated -- a boolean value indicating whether a character has begun
    to pick lock the chest or not
    chest_sfx -- the sound that should be started when the chest is opening
    """

    def __init__(
        self,
        position: Position,
        sprite_close: str,
        sprite_open: str,
        potential_items: Sequence[tuple[Item, float]],
        sprite: Optional[pygame.Surface] = None,
    ) -> None:
        super().__init__("Chest", position, sprite if sprite else sprite_close)
        self.sprite_close_link: str = sprite_close
        self.sprite_open_link: str = sprite_open
        self.sprite_open: pygame.Surface = pygame.transform.scale(
            pygame.image.load(sprite_open).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )
        self.item: Item = Chest.determine_item(potential_items)
        self.opened: bool = False
        self.pick_lock_initiated: bool = False
        self.chest_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "chest.ogg")
        )

    @staticmethod
    def determine_item(potential_items: Sequence[tuple[Item, float]]) -> Item:
        """
        Determine randomly which item will be contained by the chest

        Return the selected item

        Keyword arguments:
        potential_items -- a sequence of potential items that could be in the chest with
        their probability to be the one selected
        """
        bag: list[Item] = []
        # probability : between 0.1 and 1
        for item, probability in potential_items:
            times = int(probability * 100)
            bag += [item] * times

        return random.choice(bag)

    def open(self) -> Optional[Item]:
        """
        Open the chest if it's not already opened.
        The current sprite is changed to the one where the chest is opened.

        Start the sound corresponding to the opening of the chest.

        Return the item that is in the chest.
        """
        if not self.opened:
            self.sprite = self.sprite_open
            self.opened = True
            pygame.mixer.Sound.play(self.chest_sfx)
            return self.item
        return None

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the chest in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save state
        state: etree.SubElement = etree.SubElement(tree, "state")
        state.text = str(self.opened)
        # Save sprites
        closed: etree.SubElement = etree.SubElement(tree, "closed")
        closed_sprite = etree.SubElement(closed, "sprite")
        closed_sprite.text = self.sprite_close_link

        opened: etree.SubElement = etree.SubElement(tree, "opened")
        opened_sprite = etree.SubElement(opened, "sprite")
        opened_sprite.text = self.sprite_open_link

        # Save content
        content: etree.SubElement = etree.SubElement(tree, "contains")
        item: etree.SubElement = etree.SubElement(content, "item")
        item.text = self.item.name

        return tree
