import pygame as pg

from src.Item import Item
from src.constants import *


class Equipment(Item):

    def __init__(self, name, sprite, description, equipped_sprite, body_part, res, magic_res, atk, weight):
        Item.__init__(self, name, sprite, description)
        self.res = res
        self.magic_res = magic_res
        self.atk = atk
        self.weight = weight
        self.body_part = body_part
        self.equipped_sprite = pg.transform.scale(pg.image.load(equipped_sprite).convert_alpha(),
                                                  (TILE_SIZE, TILE_SIZE))

        # Used when character wearing the equipment cannot be selected
        self.sprite_unavailable = self.equipped_sprite.copy()
        color_image = pg.Surface(self.sprite.get_size()).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        self.normal_sprite = self.equipped_sprite

    def display(self, screen, pos, equipped=False):
        sprite_to_blit = self.sprite
        if equipped:
            sprite_to_blit = self.equipped_sprite

        screen.blit(sprite_to_blit, pos)

    def get_equipped_sprite(self):
        return self.equipped_sprite

    def get_body_part(self):
        return self.body_part

    def set_grey(self):
        self.equipped_sprite = self.sprite_unavailable

    def unset_grey(self):
        self.equipped_sprite = self.normal_sprite
