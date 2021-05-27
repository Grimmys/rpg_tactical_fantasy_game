from src.game_entities.item import Item


class Book(Item):
    """

    """
    def __init__(self, name: str, sprite: str, description: str, price: int):
        super().__init__(name, sprite, description, price)
