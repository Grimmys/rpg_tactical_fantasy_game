"""
Defines Shield class, an Equipment permitting to eventually parry opponent attacks.
"""

from __future__ import annotations

from collections.abc import Sequence

from lxml import etree

from src.game_entities.equipment import Equipment


class Shield(Equipment):
    """
    A Shield is an Equipment that could be worn on the left arm of a character to parry opponent attacks.
    The parrying chances are based on pure probabilities.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    equipped_sprites -- the ordered sequence of relative paths to the sprites that should be blitted
    on top of the character wearing the equipment
    wearing the equipment
    defense -- the defense bonus granted by the equipment
    weight -- the weight of the equipment
    parry -- the probability to parry an attack
    durability -- the total number of uses until the shield breaks
    restrictions -- the sequence of restrictions about the characters that can wear the equipment

    Attributes:
    durability_max -- the initial and maximum durability of the weapon
    durability -- the current number of uses left
    parry -- the probability to parry an attack
    """

    def __init__(
        self,
        name: str,
        sprite: str,
        description: str,
        price: int,
        equipped_sprites: Sequence[str],
        defense: int,
        weight: int,
        parry: float,
        durability: int,
        restrictions: dict[str, Sequence[str]],
    ) -> None:
        super().__init__(
            name,
            sprite,
            description,
            price,
            equipped_sprites,
            "left_hand",
            defense,
            0,
            0,
            weight,
            restrictions,
        )
        self.durability_max: int = durability
        self.durability: int = self.durability_max
        self.parry: float = parry

    def used(self) -> int:
        """
        Handle the deterioration of the shield after any use.

        Return the number of uses left after application of the deterioration.
        """
        self.durability -= 1
        self.resell_price = int(
            (self.price // 2) * (self.durability / self.durability_max)
        )
        return self.durability

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the shield in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save durability
        durability: int = etree.SubElement(tree, "durability")
        durability.text = str(self.durability)

        return tree
