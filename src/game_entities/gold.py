"""
Defines Gold class, the special item permitting to representing gold as chest or mission reward.
"""

from src.game_entities.item import Item


class Gold(Item):
    """
    Gold is the concrete representation of a gold reward for the player.

    Keyword arguments:
    amount -- the amount of gold represented

    Attributes:
    amount -- the amount of gold represented
    """

    def __init__(self, amount: int) -> None:
        super().__init__(
            str(amount) + " Gold",
            "imgs/dungeon_crawl/item/gold/gold_pile_10.png",
            "Gold could be used to buy some items or other services",
            0,
        )
        self.amount: int = amount
