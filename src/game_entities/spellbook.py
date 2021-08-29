"""
Defines Spellbook class, a Book used to cast spells.
"""

from src.game_entities.book import Book


class Spellbook(Book):
    """
    A Spellbook is a Book containing one spell that can be cast by some characters.

    Keyword arguments:
    name -- the name of the spellbook
    sprite -- the relative path to the visual representation of the spellbook
    description -- the description of the spellbook that may be displayed on an interface
    price -- the price of the spellbook
    spell -- the name of the spell of the spellbook

    Attributes:
    spell -- the name of the spell of the spellbook
    """

    def __init__(
        self, name: str, sprite: str, description: str, price: int, spell: str
    ):
        super().__init__(name, sprite, description, price)
        self.spell: str = spell
