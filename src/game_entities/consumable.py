from __future__ import annotations
import os
from typing import Sequence, List

import pygame

from src.game_entities.effect import Effect
from src.game_entities.item import Item


class Consumable(Item):
    """

    """
    def __init__(self, name: str, sprite: str, description: str,
                 price: int, effects: Sequence[Effect]) -> None:
        super().__init__(name, sprite, description, price)
        self.effects: Sequence[Effect] = effects
        self.drink_sfx: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join('sound_fx',
                                                                             'potion.ogg'))

    def use(self, entity: Movable) -> tuple[bool, Sequence[str]]:  # NOQA
        success: bool = False
        msgs: List[str] = []
        for eff in self.effects:
            sub_success, msg = eff.apply_on_ent(entity)
            msgs.append(msg)
            if sub_success:
                success = True
        if success:
            pygame.mixer.Sound.play(self.drink_sfx)
            entity.remove_item(self)
        return success, msgs
