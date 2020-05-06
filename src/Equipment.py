from src.Item import Item
from src.constants import *


class Equipment(Item):

    def __init__(self, name, sprite, description, price, equipped_sprites, body_part, defense, res, atk, weight,
                 restrictions):
        Item.__init__(self, name, sprite, description, price)
        self.defense = defense
        self.res = res
        self.atk = atk
        self.weight = weight
        self.restrictions = restrictions
        self.body_part = body_part
        self.equipped_sprite = pg.transform.scale(pg.image.load(equipped_sprites[0]).convert_alpha(),
                                                  (TILE_SIZE, TILE_SIZE))
        if len(equipped_sprites) > 1:
            for sp in equipped_sprites[1:]:
                self.equipped_sprite.blit(pg.transform.scale(pg.image.load(sp).convert_alpha(),
                                          (TILE_SIZE, TILE_SIZE)), (0, 0))

        # Used when character wearing the equipment cannot be selected
        self.sprite_unavailable = self.equipped_sprite.copy()
        color_image = pg.Surface(self.sprite.get_size()).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
        self.normal_sprite = self.equipped_sprite

    def get_formatted_restrictions(self):
        formatted_string = ''
        for key in self.restrictions:
            if key == 'classes':
                formatted_string += ', '.join([s.capitalize() for s in self.restrictions[key]])

        return formatted_string

    def display(self, screen, pos, equipped=False):
        sprite_to_blit = self.sprite
        if equipped:
            sprite_to_blit = self.equipped_sprite

        screen.blit(sprite_to_blit, pos)

    def set_grey(self):
        self.equipped_sprite = self.sprite_unavailable

    def unset_grey(self):
        self.equipped_sprite = self.normal_sprite
