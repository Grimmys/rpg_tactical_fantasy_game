import pygame as pg
from lxml import etree

from src.Destroyable import Destroyable
from src.constants import TILE_SIZE

CRACKED_SPRITE = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"
CRACKED = pg.transform.scale(pg.image.load(CRACKED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))


class Breakable(Destroyable):
    def __init__(self, name, pos, sprite, hp, defense, res):
        Destroyable.__init__(self, name, pos, sprite, hp, defense, res)
        # Useful in case of saving
        self.sprite_link = sprite

    def display(self, screen):
        Destroyable.display(self, screen)
        screen.blit(CRACKED, self.pos)

    def save(self):
        tree = Destroyable.save(self)

        # Save sprite
        sprite = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_link

        return tree