import pygame as pg

from src.Item import Item

TILE_SIZE = 48


class Equipment(Item):
    def __init__(self, name, sprite, description, equipped_sprite, body_part, res, magic_res, atk, weight):
        Item.__init__(self, name, sprite, description)
        self.res = res
        self.magic_res = magic_res
        self.atk = atk
        self.weight = weight
        self.body_part = body_part
        self.equipped_sprite = pg.transform.scale(pg.image.load(equipped_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

    def display(self, screen, pos, equipped=False):
        sprite_to_blit = self.sprite
        if equipped:
            sprite_to_blit = self.equipped_sprite

        screen.blit(sprite_to_blit, pos)

    def get_equipped_sprite(self):
        return self.equipped_sprite

    def get_body_part(self):
        return self.body_part
