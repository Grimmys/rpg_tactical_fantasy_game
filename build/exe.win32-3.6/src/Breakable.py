import pygame as pg

from src.Destroyable import Destroyable

TILE_SIZE = 48
CRACKED_SPRITE = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"
CRACKED = pg.transform.scale(pg.image.load(CRACKED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))


class Breakable(Destroyable):
    def __init__(self, name, pos, sprite, hp, defense, res):
        Destroyable.__init__(self, name, pos, sprite, hp, defense, res)

    def display(self, screen):
        Destroyable.display(self, screen)
        screen.blit(CRACKED, self.pos)