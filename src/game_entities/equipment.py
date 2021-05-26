"""
Defines Equipment class, an item that can be worn
by specific entities at a specific body part.
"""

from typing import Sequence

import pygame

from src.constants import TILE_SIZE, LIGHT_GREY
from src.game_entities.item import Item


class Equipment(Item):
    """

    """
    def __init__(self, name: str, sprite: str, description: str, price: int,
                 equipped_sprites: Sequence[str], body_part: str,
                 defense: int, resistance: int, attack: int, weight: int,
                 restrictions: dict[Sequence[str]]) -> None:
        Item.__init__(self, name, sprite, description, price)
        self.defense: int = defense
        self.resistance: int = resistance
        self.attack: int = attack
        self.weight: int = weight
        self.restrictions: dict[Sequence[str]] = restrictions
        self.body_part: str = body_part
        raw_equipped_sprite: pygame.Surface = pygame.image.load(equipped_sprites[0]).convert_alpha()
        self.equipped_sprite: pygame.Surface = pygame.transform.scale(raw_equipped_sprite,
                                                                      (TILE_SIZE, TILE_SIZE))
        if len(equipped_sprites) > 1:
            for sprite in equipped_sprites[1:]:
                self.equipped_sprite.blit(pygame.transform.scale(pygame.image.load(sprite)
                                                                 .convert_alpha(),
                                                                 (TILE_SIZE, TILE_SIZE)), (0, 0))

        # Used when character wearing the equipment cannot be selected
        self.sprite_unavailable: pygame.Surface = self.equipped_sprite.copy()
        color_image: pygame.Surface = pygame.Surface(self.sprite.get_size()).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.normal_sprite: pygame.Surface = self.equipped_sprite

    def get_formatted_restrictions(self) -> str:
        """

        :return:
        """
        formatted_string: str = ''
        for key in self.restrictions:
            if key in ('classes', 'races'):
                formatted_string += ', '.join([restriction.capitalize()
                                               for restriction in self.restrictions[key]]) + ', '

        return formatted_string[:-2]

    def display(self, screen: pygame.Surface, position: tuple[int, int], equipped: bool = False) \
            -> None:
        """

        :param screen:
        :param position:
        :param equipped:
        """
        sprite_to_blit: pygame.Surface = self.equipped_sprite if equipped else self.sprite
        screen.blit(sprite_to_blit, position)

    def set_grey(self) -> None:
        """

        """
        self.equipped_sprite = self.sprite_unavailable

    def unset_grey(self) -> None:
        """

        """
        self.equipped_sprite = self.normal_sprite
