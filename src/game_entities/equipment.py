import pygame

from src.constants import TILE_SIZE, LIGHT_GREY
from src.game_entities.item import Item


class Equipment(Item):

    def __init__(self, name, sprite, description, price, equipped_sprites, body_part,
                 defense, res, atk, weight, restrictions):
        Item.__init__(self, name, sprite, description, price)
        self.defense = defense
        self.res = res
        self.atk = atk
        self.weight = weight
        self.restrictions = restrictions
        self.body_part = body_part
        raw_equipped_sprite = pygame.image.load(equipped_sprites[0]).convert_alpha()
        self.equipped_sprite = pygame.transform.scale(raw_equipped_sprite, (TILE_SIZE, TILE_SIZE))
        if len(equipped_sprites) > 1:
            for sprite in equipped_sprites[1:]:
                self.equipped_sprite.blit(pygame.transform.scale(pygame.image.load(sprite)
                                                                 .convert_alpha(),
                                          (TILE_SIZE, TILE_SIZE)), (0, 0))

        # Used when character wearing the equipment cannot be selected
        self.sprite_unavailable = self.equipped_sprite.copy()
        color_image = pygame.Surface(self.sprite.get_size()).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.normal_sprite = self.equipped_sprite

    def get_formatted_restrictions(self):
        formatted_string = ''
        for key in self.restrictions:
            if key in ('classes', 'races'):
                formatted_string += ', '.join([restriction.capitalize()
                                               for restriction in self.restrictions[key]]) + ', '

        return formatted_string[:-2]

    def display(self, screen, position, equipped=False):
        sprite_to_blit = self.equipped_sprite if equipped else self.sprite
        screen.blit(sprite_to_blit, position)

    def set_grey(self):
        self.equipped_sprite = self.sprite_unavailable

    def unset_grey(self):
        self.equipped_sprite = self.normal_sprite
