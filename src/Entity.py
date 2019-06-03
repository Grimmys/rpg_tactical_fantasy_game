import pygame as pg

TILE_SIZE = 48

class Entity:
    def __init__(self, name, pos, sprite):
        self.name = name
        self.pos = pos
        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))

    def display(self, screen):
        screen.blit(self.sprite, self.pos)

    def get_pos(self):
        return self.pos

    def set_pos(self, pos):
        self.pos = pos

    def get_rect(self):
        return self.sprite.get_rect(topleft=(self.pos))

    def get_name(self):
        return self.name

    def get_formatted_name(self):
        return self.name.replace('_', ' ').title()

    def get_max_moves(self):
        return 0

    def get_sprite(self):
        return self.sprite

    def is_on_pos(self, pos):
        return self.get_rect().collidepoint(pos)