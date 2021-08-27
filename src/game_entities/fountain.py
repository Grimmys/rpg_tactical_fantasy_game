from typing import List

import pygame
import pygame as pg
from lxml import etree

from src.game_entities.destroyable import Destroyable
from src.game_entities.effect import Effect
from src.game_entities.entity import Entity
from src.constants import TILE_SIZE
from src.gui.entries import Entries
from src.gui.fonts import fonts


class Fountain(Entity):
    """ """

    def __init__(
        self,
        name: str,
        position: tuple[int, int],
        sprite: str,
        sprite_empty: str,
        effect: Effect,
        times: int,
    ) -> None:
        super().__init__(name, position, sprite)
        self.effect: Effect = effect
        self.times: int = times
        self.sprite_empty: pygame.Surface = pg.transform.scale(
            pg.image.load(sprite_empty).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )

    def drink(self, entity: Destroyable) -> Entries:
        """

        Keyword arguments:
        entity --
        """
        entries: List[List[dict[str, str]]] = []
        if self.times > 0:
            result = self.effect.apply_on_ent(entity)
            if result[0]:
                self.times -= 1
                if self.times == 0:
                    self.sprite = self.sprite_empty
            entries.append(
                [{"type": "text", "text": result[1], "font": fonts["ITEM_DESC_FONT"]}]
            )
            entries.append(
                [
                    {
                        "type": "text",
                        "text": str(self.times) + " remaining uses.",
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            )
        else:
            entries.append(
                [
                    {
                        "type": "text",
                        "text": "The fountain is empty...",
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            )
        return entries

    def set_times(self, times: int) -> None:
        """

        Keyword arguments:
        times --
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
