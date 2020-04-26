from src.Item import Item


class Book(Item):
    def __init__(self, name, sprite, description, price):
        Item.__init__(self, name, sprite, description, price)
