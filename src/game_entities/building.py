"""
Defines Building class, an entity that can be visited by the player
"""

from __future__ import annotations

import os
from typing import Optional

import pygame
from pygamepopup.components import BoxElement, TextElement

from src.constants import GREEN
from src.game_entities.character import Character
from src.game_entities.entity import Entity
from src.gui.fonts import fonts
from src.gui.position import Position
from src.services.language import *


class Building(Entity):
    """
    A Building represents a static entity that can be visited by the player.
    Someone could be in it or not, so a specific interaction could be linked to the visit of
    the house but is not mandatory.

    Keyword arguments:
    name -- the name of the building
    position -- the current position of the building on screen
    sprite_link -- the relative path to the visual representation of the building on screen
    interaction -- the data structure indicating what should happen the first time someone
    is visiting the building
    sprite -- the pygame Surface corresponding to the appearance of the building on screen,
    would be loaded from sprite_link if not provided

    Attributes:
    sprite_link -- the relative path to the visual representation of the building on screen
    interaction -- the data structure indicating what should happen the first time someone
    is visiting the building
    door_sfx -- the sound that should be started when someone is visiting the building
    talk_sfx -- the sound that should be started if someone is in the building and
    has something to say to the player
    gold_sfx -- the sound that should be started if some gold is given
    to the character visiting the building
    inventory_sfx -- the sound that should be started if one or more item(s) are given
    to the character visiting the building
    """

    def __init__(
        self,
        name: str,
        position: Position,
        sprite_link: str,
        interaction: Optional[dict[str, any]] = None,
        sprite: Optional[pygame.Surface] = None,
    ) -> None:
        super().__init__(name, position, sprite if sprite else sprite_link)
        self.sprite_link: str = sprite_link
        self.interaction: dict[str, any] = interaction
        self.door_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "door.ogg")
        )
        self.talk_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "talking.ogg")
        )
        self.gold_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "trade.ogg")
        )
        self.inventory_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "inventory.ogg")
        )

    def interact(self, actor: Character) -> list[list[BoxElement]]:
        """
        Manage the interaction of a character with the building.

        Start the sounds that should be played according to the situation.

        Add gold or item(s) to the character visiting the building if needed.

        Return the list of entries corresponding to the data that should be displayed on
        the player interface

        Keyword argument:
        actor -- the character visiting the building
        """
        entries: list[list[BoxElement]] = []

        if not self.interaction:
            pygame.mixer.Sound.play(self.door_sfx)
            entries.append(
                [TextElement(STR_THIS_HOUSE_SEEMS_CLOSED, font=fonts["ITEM_DESC_FONT"])]
            )
        else:
            pygame.mixer.Sound.play(self.talk_sfx)
            for talk in self.interaction["talks"]:
                entries.append([TextElement(talk, font=fonts["ITEM_DESC_FONT"])])
            if "gold" in self.interaction and self.interaction["gold"] > 0:
                pygame.mixer.Sound.play(self.gold_sfx)
                actor.gold += self.interaction["gold"]
                earn_text: str = f_YOU_RECEIVED_NUMBER_GOLD(self.interaction["gold"])
                entries.append(
                    [
                        TextElement(
                            earn_text, font=fonts["ITEM_DESC_FONT"], text_color=GREEN
                        )
                    ]
                )
            if "item" in self.interaction and self.interaction["item"]:
                pygame.mixer.Sound.play(self.inventory_sfx)
                actor.set_item(self.interaction["item"])
                earn_text: str = f_YOU_RECEIVED_ITEM(self.interaction["item"])
                entries.append(
                    [
                        TextElement(
                            earn_text, font=fonts["ITEM_DESC_FONT"], text_color=GREEN
                        )
                    ]
                )
            # Interaction could not been repeated : should be removed after being used
            self.remove_interaction()

        return entries

    def remove_interaction(self) -> None:
        """
        Remove the inner interaction of the building
        """
        self.interaction = None

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the building in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save state
        state: etree.SubElement = etree.SubElement(tree, "state")
        state.text = str(self.interaction is None)

        # Save sprite
        sprite: etree.SubElement = etree.SubElement(tree, "sprite")
        sprite.text = self.sprite_link

        # Save interaction
        if self.interaction:
            interaction: etree.SubElement = etree.SubElement(tree, "interaction")
            talks: etree.SubElement = etree.SubElement(interaction, "talks")
            for talk in self.interaction["talks"]:
                talk_tag: etree.SubElement = etree.SubElement(talks, "talk")
                talk_tag.text = talk
            if "gold" in self.interaction and self.interaction["gold"] > 0:
                gold: etree.SubElement = etree.SubElement(interaction, "gold")
                gold.text = str(self.interaction["gold"])
            if "item" in self.interaction and self.interaction["item"]:
                item: etree.SubElement = etree.SubElement(interaction, "item")
                item.text = self.interaction["item"].name

        return tree
