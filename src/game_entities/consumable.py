import os
from typing import Sequence, List

import pygame

from src.game_entities.effect import Effect
from src.game_entities.item import Item
from src.game_entities.player import Player


class Consumable(Item):
    def __init__(self, name: str, sprite: str, description: str,
                 price: int, effects: Sequence[Effect]) -> None:
        Item.__init__(self, name, sprite, description, price)
        self.effects: Sequence[Effect] = effects
        self.drink_sfx: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join('sound_fx',
                                                                             'potion.ogg'))

    def use(self, player: Player) -> tuple[bool, Sequence[str]]:
        success: bool = False
        msgs: List[str] = []
        for eff in self.effects:
            sub_success, msg = eff.apply_on_ent(player)
            msgs.append(msg)
            if sub_success:
                success = True
        if success:
            pygame.mixer.Sound.play(self.drink_sfx)
            player.remove_item(self)
        return success, msgs
