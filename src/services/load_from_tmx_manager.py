import pygame
import pytmx

from src.constants import TILE_SIZE


def parse_tiled_map(tmx_data, size: tuple[int, int]) -> pygame.Surface:
    map_ground = pygame.Surface(size)
    for layer in tmx_data.layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    map_ground.blit(pygame.transform.scale(tile, (TILE_SIZE, TILE_SIZE)),
                                    (x * TILE_SIZE, y * TILE_SIZE))
    return map_ground
