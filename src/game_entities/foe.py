"""
Defines Foe class, an hostile entity which targets players and allies.
"""

import random as rd
from enum import Enum, auto
from typing import Union, Sequence

import pygame
from lxml import etree

from src.game_entities.alteration import Alteration
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.movable import Movable


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
    """ """

    grow_rates: dict[str, dict[str, Sequence[int]]] = {}

    def __init__(
        self,
        name: str,
        position: tuple[int, int],
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
        keywords: Sequence[Keyword] = None,
        lvl: int = 1,
        alterations: Sequence[Alteration] = None,
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

    def stats_up(self, nb_lvl: int = 1) -> None:
        """

        :param nb_lvl:
        """
        grow_rates: dict[str, Sequence[int]] = Foe.grow_rates[self.name]
        for _ in range(nb_lvl):
            self.hit_points_max += rd.choice(grow_rates["hp"])
            self.defense += rd.choice(grow_rates["def"])
            self.resistance += rd.choice(grow_rates["res"])
            self.strength += rd.choice(grow_rates["str"])
            self.xp_gain = int(self.xp_gain * 1.1)

    def roll_for_loot(self) -> Sequence[Item]:
        """

        :return:
        """
        loot: list[Item] = []
        for (item, probability) in self.potential_loot:
            if rd.random() < probability:
                loot.append(item)
        return loot

    def get_formatted_keywords(self) -> str:
        """

        :return:
        """
        return ", ".join(
            [keyword.name.lower().capitalize() for keyword in self.keywords]
        )

    def get_formatted_reach(self) -> str:
        """

        :return:
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
        loot: etree.SubElement = etree.SubElement(tree, "loot")
        for (item, probability) in self.potential_loot:
            if isinstance(item, Gold):
                it_el: etree.SubElement = etree.SubElement(loot, "gold")
                it_name = etree.SubElement(it_el, "amount")
                it_name.text = str(item.amount)
            else:
                it_el: etree.SubElement = etree.SubElement(loot, "item")
                it_name = etree.SubElement(it_el, "name")
                it_name.text = item.name
            it_probability: etree.SubElement = etree.SubElement(it_el, "probability")
            it_probability.text = str(probability)

        return tree
