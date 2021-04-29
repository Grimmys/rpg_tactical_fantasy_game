from src.game_entities.book import Book


class Spellbook(Book):
    def __init__(self, name, sprite, description, price, spell):
        Book.__init__(self, name, sprite, description, price)
        self.spell = spell
