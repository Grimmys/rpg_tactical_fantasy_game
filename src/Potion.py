from src.Consumable import Consumable


class Potion(Consumable):
    def __init__(self, name, sprite, description, price, effect):
        Consumable.__init__(self, name, sprite, description, price, effect)
