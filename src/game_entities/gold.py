from src.game_entities.item import Item


class Gold(Item):
    """ """

    def __init__(self, amount: int) -> None:
        super().__init__(
            str(amount) + " Gold",
            "imgs/dungeon_crawl/item/gold/gold_pile_10.png",
            "Gold could be used to buy some items or other services",
            0,
        )
        self.amount: int = amount
