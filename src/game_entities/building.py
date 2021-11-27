"""
Defines Building class, an entity that can be visited by the player
"""

import os

import pygame
from lxml import etree

from src.constants import GREEN
from src.game_entities.character import Character
from src.game_entities.entity import Entity
from src.gui.entries import Entries
from src.gui.fonts import fonts


class Building(Entity):
    """
    A Building represents a static entity that can be visited by the player.
    Someone could be in it or not, so a specific interaction could be linked to the visit of
    the house but is not mandatory.

    Keyword arguments:
    name -- the name of the building
    position -- the current position of the building on screen
    sprite -- the pygame Surface corresponding to the appearance of the building on screen
    interaction -- the data structure indicating what should happen the first time someone
    is visiting the building

    Attributes:
    sprite_link -- the relative path to the visual representation of the element
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
        position: tuple[int, int],
        sprite: str,
        interaction: dict[str, any] = None,
    ) -> None:
        super().__init__(name, position, sprite)
        self.sprite_link: str = sprite
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

    def interact(self, actor: Character) -> Entries:
        """
        Manage the interaction of a character with the building.

        Start the sounds that should be played according to the situation.

        Add gold or item(s) to the character visiting the building if needed.

        Return the list of entries corresponding to the data that should be displayed on
        the player interface

        Keyword argument:
        actor -- the character visiting the building
        """
        entries: Entries = []

        if not self.interaction:
            pygame.mixer.Sound.play(self.door_sfx)
            entries.append(
                [
                    {
                        "type": "text",
                        "text": "This house seems closed...",
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            )
        else:
            for talk in self.interaction["talks"]:
                pygame.mixer.Sound.play(self.talk_sfx)
                entries.append(
                    [{"type": "text", "text": talk, "font": fonts["ITEM_DESC_FONT"]}]
                )
            if self.interaction["gold"] > 0:
                pygame.mixer.Sound.play(self.gold_sfx)
                actor.gold += self.interaction["gold"]
                earn_text: str = f'[You received {self.interaction["gold"]} gold]'
                entries.append(
                    [
                        {
                            "type": "text",
                            "text": earn_text,
                            "font": fonts["ITEM_DESC_FONT"],
                            "color": GREEN,
                        }
                    ]
                )
            if self.interaction["item"] is not None:
                pygame.mixer.Sound.play(self.inventory_sfx)
                actor.set_item(self.interaction["item"])
                earn_text: str = f'[You received {self.interaction["item"]}]'
                entries.append(
                    [
                        {
                            "type": "text",
                            "text": earn_text,
                            "font": fonts["ITEM_DESC_FONT"],
                            "color": GREEN,
                        }
                    ]
                )
            # Interaction could not been repeated : should be remove after been used
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
            if self.interaction["gold"] > 0:
                gold: etree.SubElement = etree.SubElement(interaction, "gold")
                gold.text = str(self.interaction["gold"])
            if self.interaction["item"] is not None:
                item: etree.SubElement = etree.SubElement(interaction, "item")
                item.text = self.interaction["item"].name

        return tree
