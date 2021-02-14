from src.game_entities.consumable import Consumable


class Potion(Consumable):
    def __init__(self, name, sprite, description, price, effects):
        Consumable.__init__(self, name, sprite, description, price, effects)
