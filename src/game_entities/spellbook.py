from src.game_entities.book import Book


class Spellbook(Book):
    """

    """
    def __init__(self, name: str, sprite: str, description: str, price: int, spell: str):
        super().__init__(name, sprite, description, price)
        self.spell: str = spell
