from src.Consumable import Consumable


class Potion(Consumable):
    def __init__(self, name, sprite, description, effect):
        Consumable.__init__(self, name, sprite, description, effect)