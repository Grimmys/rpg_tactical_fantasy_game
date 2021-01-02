from src.item import Item


class Key(Item):
    def __init__(self, name, sprite, description, price, for_chest, for_door):
        Item.__init__(self, name, sprite, description, price)
        self.for_chest = for_chest
        self.for_door = for_door
