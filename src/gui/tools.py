from math import sqrt

from src.constants import TILE_SIZE


def blit_alpha(target, source, location, opacity):
    source.set_alpha(opacity)
    target.blit(source, location)


def distance(position, other_position):
    return sqrt((position[0] - other_position[0]) ** 2 + (position[1] - other_position[1]) ** 2) \
           // TILE_SIZE
