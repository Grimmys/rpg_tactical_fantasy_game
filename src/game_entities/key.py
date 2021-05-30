from src.game_entities.item import Item


class Key(Item):
    """ """

    def __init__(
        self,
        name: str,
        sprite: str,
        description: str,
        price: int,
        for_chest: bool,
        for_door: bool,
    ) -> None:
        super().__init__(name, sprite, description, price)
        self.for_chest: bool = for_chest
        self.for_door: bool = for_door
