from src.game_entities.item import Item


class Book(Item):
    """

    """
    def __init__(self, name: str, sprite: str, description: str, price: int):
        Item.__init__(self, name, sprite, description, price)
