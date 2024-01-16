"""
Defines Equipment class, an item that can be worn
by specific entities at a specific body part.
"""

from __future__ import annotations

from collections.abc import Sequence

import pygame

from src.constants import LIGHT_GREY, TILE_SIZE
from src.game_entities.item import Item
from src.services.language import TRANSLATIONS


class Equipment(Item):
    """
    Equipment is an Item that can be equipped on some Characters.
    It may give any kind of bonus to the bearer.

    Keyword arguments:
    name -- the name of the item
    sprite -- the relative path to the visual representation of the item
    description -- the description of the item that might be displayed on an interface
    price -- the standard price of the item in a shop, optional if the item can't be sold or bought
    equipped_sprites -- the ordered sequence of relative paths to the sprites that should be blitted
    on top of the character wearing the equipment
    wearing the equipment
    body_part -- the body part on which the equipment should be worn
    defense -- the defense bonus granted by the equipment
    resistance -- the resistance bonus granted by the equipment
    attack -- the attack bonus granted by the equipment
    weight -- the weight of the equipment
    restrictions -- the sequence of restrictions about the characters that can wear the equipment

    Attributes:
    defense -- the defense bonus granted by the equipment
    resistance -- the resistance bonus granted by the equipment
    attack -- the attack bonus granted by the equipment
    weight -- the weight of the equipment
    restrictions -- the sequence of restrictions about the characters that can wear the equipment
    body_part -- the body part on which the equipment should be worn
    equipped_sprite -- the current sprite of the equipment when worn by a character
    sprite_unavailable -- the sprite of the equipment with a slightly opaque filter on it
    normal_sprite -- the default sprite of the equipment
    """

    def __init__(
        self,
        name: str,
        sprite: str,
        description: str,
        price: int,
        equipped_sprites: Sequence[str],
        body_part: str,
        defense: int,
        resistance: int,
        attack: int,
        weight: int,
        restrictions: dict[str, Sequence[str]],
    ) -> None:
        super().__init__(name, sprite, description, price)
        self.defense: int = defense
        self.resistance: int = resistance
        self.attack: int = attack
        self.weight: int = weight
        self.restrictions: dict[str, Sequence[str]] = restrictions
        self.body_part: str = body_part
        raw_equipped_sprite: pygame.Surface = pygame.image.load(
            equipped_sprites[0]
        ).convert_alpha()
        self.equipped_sprite: pygame.Surface = pygame.transform.scale(
            raw_equipped_sprite, (TILE_SIZE, TILE_SIZE)
        )
        if len(equipped_sprites) > 1:
            for equipped_sprite in equipped_sprites[1:]:
                self.equipped_sprite.blit(
                    pygame.transform.scale(
                        pygame.image.load(equipped_sprite).convert_alpha(),
                        (TILE_SIZE, TILE_SIZE),
                    ),
                    (0, 0),
                )

        # Used when character wearing the equipment cannot be selected
        self.sprite_unavailable: pygame.Surface = self.equipped_sprite.copy()
        color_image: pygame.Surface = pygame.Surface(
            self.sprite.get_size()
        ).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(
            color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
        self.normal_sprite: pygame.Surface = self.equipped_sprite

    def get_formatted_restrictions(self) -> str:
        """
        Return the list of restrictions about which characters could wear or not the equipment in a formatted
        way
        """
        formatted_string: str = ""
        for key in self.restrictions:
            if key in ("classes", "races"):
                formatted_string += (
                    ", ".join(
                        [
                            TRANSLATIONS["races_and_classes"][
                                restriction.lower().replace(" ", "_")
                            ]
                            for restriction in self.restrictions[key]
                        ]
                    )
                    + ", "
                )

        return formatted_string[:-2]

    def display(
        self, screen: pygame.Surface, position: tuple[int, int], equipped: bool = False
    ) -> None:
        """
        Display the equipment on the given screen.

        Keyword arguments:
        screen -- the screen on which the equipment should be drawn
        position -- the position on screen where the equipment should be displayed
        equipped -- whether it's the equipped version (on a character) or
        the item version on a menu that should be displayed
        """
        sprite_to_blit: pygame.Surface = (
            self.equipped_sprite if equipped else self.sprite
        )
        screen.blit(sprite_to_blit, position)

    def set_grey(self) -> None:
        """Set grey version of the equipment sprite as the visible one"""
        self.equipped_sprite = self.sprite_unavailable

    def unset_grey(self) -> None:
        """Restore the default equipment sprite as the visible one"""
        self.equipped_sprite = self.normal_sprite
