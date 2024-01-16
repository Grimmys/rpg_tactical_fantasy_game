"""
Defines Weapon class, specific equipment with which an entity can attack.
"""

from __future__ import annotations

import random
from collections.abc import Sequence

from lxml import etree

from src.game_entities.destroyable import DamageKind
from src.game_entities.effect import Effect
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Keyword
from src.game_entities.skill import SkillNature
from src.gui.tools import distance
from src.services.language import TRANSLATIONS


class Weapon(Equipment):
    """
    A Weapon is an Equipment that can be used to perform an attack.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    equipped_sprites -- the ordered sequence of relative paths to the sprites that should be blitted
    on top of the character wearing the equipment
    wearing the weapon
    attack -- the power of the weapon
    attack_kind -- the kind of attack that could be done with the weapon
    weight -- the weight of the weapon
    durability -- the total number of uses until the weapon breaks
    reach -- the range of the reach of the weapon
    restrictions -- the sequence of restrictions about the characters that can bear the weapon
    possible_effects -- the list of the possible effects that can be applied to the target of an attack
    strong_against -- the list of things against which the weapon is stronger
    can_charge -- whether it is possible to charge or not with the weapon

    Attributes:
    durability_max -- the initial and maximum durability of the weapon
    durability -- the current number of uses left
    reach -- the range of the reach of the weapon
    attack_kind -- the kind of attack that could be done with the weapon
    effects -- the list of the possible effects that can be applied to the target of an attack
    strong_against -- the list of things against which the weapon is stronger
    can_charge -- whether it is possible to charge or not with the weapon
    """

    def __init__(
        self,
        name: str,
        sprite: str,
        description: str,
        price: int,
        equipped_sprite: Sequence[str],
        attack: int,
        attack_kind,
        weight: int,
        durability: int,
        reach: Sequence[int],
        restrictions: dict[str, Sequence[str]],
        possible_effects: Sequence[dict[str, any]],
        strong_against: Sequence[Keyword],
        can_charge: bool = False,
    ):
        super().__init__(
            name,
            sprite,
            description,
            price,
            equipped_sprite,
            "right_hand",
            0,
            0,
            attack,
            weight,
            restrictions,
        )
        self.durability_max: int = durability
        self.durability: int = self.durability_max
        self.reach: Sequence[int] = reach
        self.attack_kind: DamageKind = DamageKind[attack_kind]
        self.effects: Sequence[dict[str, any]] = possible_effects
        self.strong_against: Sequence[Keyword] = strong_against
        self.can_charge: bool = can_charge

    def get_formatted_strong_against(self):
        """Return the list of keywords against which the weapon is stronger in a formatted way"""
        return ", ".join(
            [
                TRANSLATIONS["foe_keywords"][keyword.name.lower().replace(" ", "_")]
                for keyword in self.strong_against
            ]
        )

    def hit(self, holder, target) -> int:
        """
        Handle the hit of an entity with the weapon.
        Return the damage dealt by the attack.

        Keyword arguments:
        holder -- the bearer of the weapon
        target -- the target of the attack
        """
        multiplier = 1
        if self.can_charge:
            distance_traveled = distance(holder.old_position, holder.position)
            if distance_traveled >= 5:
                multiplier += 0.5 * ((distance_traveled - 2) // 3)
        for keyword in target.keywords:
            if keyword in self.strong_against:
                multiplier += 1
        return int(multiplier * self.attack)

    def used(self) -> int:
        """
        Handle the deterioration of the weapon after any use.

        Return the number of uses left after application of the deterioration.
        """
        self.durability -= 1
        self.resell_price = int(
            (self.price // 2) * (self.durability / self.durability_max)
        )
        return self.durability

    def apply_effects(
        self, user: Character, target: Destroyable  # NOQA
    ) -> Sequence[Effect]:
        """
        Check if some effects from the list of possible effects are triggered after the use of the weapon

        Return the list of triggered effects

        Keyword arguments:
        user -- the bearer of the weapon
        target -- the target of the ongoing attack
        """
        # Try to trigger one or more effects
        effects = []
        for effect in self.effects:
            probability = effect["probability"]
            for skill in user.skills:
                if (
                    skill.nature is SkillNature.ALTERATION_CHANCE_BOOST
                    and effect["effect"].alteration in skill.alterations
                ):
                    probability += skill.power

            if random.randint(0, 100) < probability:
                effects.append(effect["effect"])
        return effects

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the weapon in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save durability
        durability = etree.SubElement(tree, "durability")
        durability.text = str(self.durability)

        return tree
