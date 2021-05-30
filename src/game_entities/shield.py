from typing import Sequence

from lxml import etree

from src.game_entities.equipment import Equipment


class Shield(Equipment):
    """ """

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
        restrictions: dict[Sequence[str]],
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

        :return:
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
