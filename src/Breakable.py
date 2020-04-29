import pygame as pg
from lxml import etree

from src.Destroyable import Destroyable
from src.constants import TILE_SIZE

CRACKED = None


class Breakable(Destroyable):
    @staticmethod
    def init_constant_sprites():
        global CRACKED
        cracked_sprite = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"
        CRACKED = pg.transform.scale(pg.image.load(cracked_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

    def __init__(self, pos, sprite, hp, defense, res):
        Destroyable.__init__(self, "Breakable", pos, sprite, hp, defense, res)
        # Useful in case of saving
        self.sprite_link = sprite

    def display(self, screen):
        Destroyable.display(self, screen)
        screen.blit(CRACKED, self.pos)

    def save(self, tree_name):
        tree = Destroyable.save(self, tree_name)

        # Save sprite
        sprite = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_link

        return tree
