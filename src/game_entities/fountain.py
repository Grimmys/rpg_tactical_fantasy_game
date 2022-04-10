"""
Defines Fountain class, a passive entity with which characters can interact to eventually earn bonus.
"""

from __future__ import annotations

import pygame
from lxml import etree
from pygamepopup.components import BoxElement, TextElement

from src.constants import TILE_SIZE
from src.game_entities.destroyable import Destroyable
from src.game_entities.effect import Effect
from src.game_entities.entity import Entity
from src.gui.fonts import fonts
from src.gui.position import Position


class Fountain(Entity):
    """
    A Fountain is a static entity where player characters can drink to earn a specific effect or a random one.

    Keyword arguments:
    name -- the name of the fountain
    position -- the current position of the fountain on screen
    sprite --  the relative path to the visual representation of the entity
    sprite_empty -- the relative path to the visual representation of the fountain when it couldn't be used anymore
    effect -- the effect that should be applied to the character interacting with the fountain
    times -- the number of times the fountain could be used until being empty

    Attributes:
    effect -- the effect that should be applied to the character interacting with the fountain
    times -- the number of times the fountain could be used until being empty
    sprite_empty -- the pygame Surface corresponding to the appearance of the fountain on screen when it is empty,
    it should match the size of a tile
    """

    def __init__(
        self,
        name: str,
        position: Position,
        sprite: str,
        sprite_empty: str,
        effect: Effect,
        times: int,
    ) -> None:
        super().__init__(name, position, sprite)
        self.effect: Effect = effect
        self.times: int = times
        self.sprite_empty: pygame.Surface = pygame.transform.scale(
            pygame.image.load(sprite_empty).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )

    def drink(self, entity: Destroyable) -> list[list[BoxElement]]:
        """
        Handle the interaction of an entity with the fountain.
        Return the dialog that should be displayed to the player.

        Keyword arguments:
        entity -- the entity drinking the content of the fountain
        """
        entries: list[list[BoxElement]] = []
        if self.times > 0:
            result = self.effect.apply_on_ent(entity)
            if result[0]:
                self.times -= 1
                if self.times == 0:
                    self.sprite = self.sprite_empty
            entries.append([TextElement(result[1], font=fonts["ITEM_DESC_FONT"])])
            entries.append(
                [
                    TextElement(
                        f"{self.times} remaining uses", font=fonts["ITEM_DESC_FONT"]
                    )
                ]
            )
        else:
            entries.append(
                [TextElement("The fountain is empty...", font=fonts["ITEM_DESC_FONT"])]
            )
        return entries

    def set_times(self, times: int) -> None:
        """
        Set the number of uses left to the one given.

        Keyword arguments:
        times -- the number of uses left to be set
        """
        self.times = times
        if self.times == 0:
            self.sprite = self.sprite_empty

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the fountain in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save remaining uses
        times: etree.SubElement = etree.SubElement(tree, "times")
        times.text = str(self.times)

        # Save type
        nature: etree.SubElement = etree.SubElement(tree, "type")
        nature.text = self.name

        return tree
