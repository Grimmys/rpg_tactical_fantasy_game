"""
Defines Skill class, the class describing the definition of the skills of player characters.
"""

from collections.abc import Sequence
from enum import Enum, auto
from typing import Optional

from src.game_entities.alteration import Alteration
from src.services.language import TRANSLATIONS


class SkillNature(Enum):
    MULTIPLE_ATTACKS = auto()
    ACTIVE = auto()
    ALLY_BOOST = auto()
    ALTERATION_CHANCE_BOOST = auto()


class Skill:
    """
    A Skill is a special capacity that a player character can have.

    Keyword arguments:
    name -- the name of the skill
    formatted_name -- the name of the skill in a formatted way to be displayed to the player
    nature -- the type of the skill
    description -- the description of the skill
    power -- the strength of the skill
    stats -- the list of statistics concerned by the skill effect
    alterations -- the list of alterations concerned by the skill effect

    Attributes:
    name -- the name of the skill
    formatted_name -- the name of the skill in a formatted way to be displayed to the player
    nature -- the type of the skill
    description -- the description of the skill
    power -- the strength of the skill
    stats -- the list of statistics concerned by the skill effect
    alterations -- the list of alterations concerned by the skill effect
    """

    def __init__(
        self,
        name: str,
        formatted_name: str,
        nature: SkillNature,
        description: str,
        power: int = 0,
        stats: Optional[Sequence[str]] = None,
        alterations: Optional[Sequence[Alteration]] = None,
    ):
        if alterations is None:
            alterations = []
        if stats is None:
            stats = []
        self.name: str = name
        self.formatted_name: str = formatted_name
        self.nature: SkillNature = SkillNature[nature]
        self.description: str = description
        self.power: int = power
        self.stats: Optional[Sequence[str]] = stats
        self.alterations: Optional[Sequence[Alteration]] = alterations

    def __eq__(self, name):
        return self.name == name

    def __str__(self):
        return self.name
