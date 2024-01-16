"""
Defines Foe class, a hostile entity which targets players and allies.
"""

from __future__ import annotations

import random as rd
from collections.abc import Sequence
from enum import Enum, auto
from typing import Optional, Union

import pygame

from src.game_entities.alteration import Alteration
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.movable import Movable
from src.gui.position import Position
from src.services.language import *


class Keyword(Enum):
    """
    Enumeration of possible keywords for a Foe.
    A foe can have multiple different keywords.
    """

    LARGE = auto()
    CAVALRY = auto()
    FLY = auto()
    SMALL = auto()
    MUTANT = auto()
    UNDEAD = auto()


class Foe(Movable):
    """
    A Foe is any kind of movable entity that is on the opposite side of the player.

    Keyword arguments:
    name -- the name of the foe
    position -- the current position of the entity on screen
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen or
    the relative path to the visual representation of the entity
    hit_points -- the total of damage that the entity can take before disappearing
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks
    max_moves -- the max number of tiles that could be crossed by the entity during one movement
    strength -- the raw strength of the entity
    attack_kind -- the kind of damage dealt by the entity
    strategy -- the strategy of the entity if it's controlled by the AI
    reach -- the range of reach of the entity
    xp_gain -- the amount of experience earned by the player character killing the foe
    loot -- the sequence of items looted when the foe is killed
    keywords -- the sequence of keywords designating the foe
    lvl -- the current level of the entity
    alterations -- the sequence of alterations affecting the foe
    target_of_mission -- the id of the mission where the foe is the target if there is any

    Attributes:
    reach -- the range of reach of the entity
    xp_gain -- the amount of experience earned by the player character killing the foe
    potential_loot -- the sequence of items that might be looted when the foe is killed
    keywords -- the sequence of keywords designating the foe
    target_of_mission -- the id of the mission where the foe is the target if there is any
    """

    grow_rates: dict[str, dict[str, Sequence[int]]] = {}

    def __init__(
        self,
        name: str,
        position: Position,
        sprite: Union[str, pygame.Surface],
        hit_points: int,
        defense: int,
        resistance: int,
        max_move: int,
        strength: int,
        attack_kind: str,
        strategy: str,
        reach: Sequence[int],
        xp_gain: int,
        loot: Sequence[tuple[Item, float]],
        keywords: Optional[Sequence[Keyword]] = None,
        lvl: int = 1,
        alterations: Optional[Sequence[Alteration]] = None,
        target_of_mission: Optional[str] = None,
    ) -> None:
        super().__init__(
            name,
            position,
            sprite,
            hit_points,
            defense,
            resistance,
            max_move,
            strength,
            attack_kind,
            strategy,
            lvl,
            alterations=alterations,
        )
        self.reach: Sequence[int] = reach
        self.xp_gain: int = int(xp_gain * (1.1 ** (lvl - 1)))
        self.potential_loot: Sequence[tuple[Item, float]] = loot
        self.keywords: Sequence[Keyword] = [] if keywords is None else keywords
        self.target_of_mission: Optional[str] = target_of_mission

    def stats_up(self, levels_earned: int = 1) -> None:
        """
        Randomly upgrade each stat for each level earned by the foe

        Keyword arguments:
        levels_earned -- the number of times the stats should be upgraded
        """
        grow_rates: dict[str, Sequence[int]] = Foe.grow_rates[self.name]
        for _ in range(levels_earned):
            self.hit_points_max += rd.choice(grow_rates["hp"])
            self.defense += rd.choice(grow_rates["def"])
            self.resistance += rd.choice(grow_rates["res"])
            self.strength += rd.choice(grow_rates["str"])
            self.xp_gain = int(self.xp_gain * 1.1)

    def roll_for_loot(self) -> Sequence[Item]:
        """
        Roll the list of items that would be loot by the entity killing the foe

        Return the loot list
        """
        loot: list[Item] = []
        for item, probability in self.potential_loot:
            if rd.random() < probability:
                loot.append(item)
        return loot

    def get_formatted_keywords(self) -> str:
        """Return the list of keywords of the foe in a formatted version"""
        formatted_string: str = ""
        for keyword in self.keywords:
            try:
                formatted_string += (
                    TRANSLATIONS["foe_keywords"][keyword.name.lower()] + ", "
                )
            except KeyError:
                formatted_string += keyword.name.lower().capitalize() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_formatted_reach(self) -> str:
        """
        Return range of the reach of the foe in a formatted
        version
        """
        return ", ".join([str(reach) for reach in self.reach])

    def save(self, tree_name) -> etree.Element:
        """
        Save the current state of the foe in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save loot
        loot_element: etree.SubElement = etree.SubElement(tree, "loot")
        for item, probability in self.potential_loot:
            if isinstance(item, Gold):
                item_element: etree.SubElement = etree.SubElement(loot_element, "gold")
                item_name = etree.SubElement(item_element, "amount")
                item_name.text = str(item.amount)
            else:
                item_element: etree.SubElement = etree.SubElement(loot_element, "item")
                item_name = etree.SubElement(item_element, "name")
                item_name.text = item.name
            it_probability: etree.SubElement = etree.SubElement(
                item_element, "probability"
            )
            it_probability.text = str(probability)

        # Save mission link
        if self.target_of_mission is not None:
            mission_element = etree.SubElement(tree, "mission_target")
            mission_element.text = self.target_of_mission
        return tree
