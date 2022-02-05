"""
Defines Potion class, a specific category of Consumable items.
"""

from src.game_entities.consumable import Consumable


class Potion(Consumable):
    """
    As for now, a Potion is equal to a Consumable in all ways, except that it could be treated differently by
    some sellers or characters.

    Keyword arguments:
    name -- the name of the potion
    sprite -- the relative path to the visual representation of the potion
    description -- the description of the potion that may be displayed on an interface
    price -- the price of the potion
    effects -- the sequence of effects that will or might be applied to the consumer of the potion
    """
