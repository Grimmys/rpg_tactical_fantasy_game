from src.Item import Item


class Key(Item):
    def __init__(self, name, sprite, description, price):
        Item.__init__(self, name, sprite, description, price)
