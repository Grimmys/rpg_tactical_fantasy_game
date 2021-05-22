from typing import Sequence

from src.game_entities.consumable import Consumable
from src.game_entities.effect import Effect


class Potion(Consumable):
    """

    """
    def __init__(self, name: str, sprite: str, description: str,
                 price: int, effects: Sequence[Effect]) -> None:
        Consumable.__init__(self, name, sprite, description, price, effects)
