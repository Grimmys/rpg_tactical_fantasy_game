from src.Book import Book


class Spellbook(Book):
    def __init__(self, name, sprite, description, spell):
        Book.__init__(self, name, sprite, description)
        self.spell = spell