"""
Defines Consumable class, an item that can be consumed by an entity and that might disappear after
"""

from __future__ import annotations

import os
from collections.abc import Sequence

import pygame

from src.game_entities.effect import Effect
from src.game_entities.item import Item


class Consumable(Item):
    """
    A Consumable is an item that can be used by an entity and generally has a
    limited number of uses.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    effects -- the sequence of effects that will happen when using the consumable

    Attributes:
    effects -- the sequence of effects that will happen when using the consumable
    drink_sfx -- the sound that should be started when someone use the consumable
    """

    def __init__(
        self,
        name: str,
        sprite: str,
        description: str,
        price: int,
        effects: Sequence[Effect],
    ) -> None:
        super().__init__(name, sprite, description, price)
        self.effects: Sequence[Effect] = effects
        self.drink_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "potion.ogg")
        )
