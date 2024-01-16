"""
Defines static sprites at interpretation time.
The init_constant_sprites function should be called at the beginning of the application
after pygame initialization and after the initialization of at least one pygame window.
"""

import pygame

from src.constants import (BLACK, MAX_MAP_HEIGHT, MAX_MAP_WIDTH, TILE_SIZE,
                           WHITE)
from src.gui.fonts import fonts
from src.services.language import *

LANDING_OPACITY = 80
LANDING_SPRITE = "imgs/dungeon_crawl/misc/move.png"

ATTACKABLE_OPACITY = 80
ATTACKABLE_SPRITE = "imgs/dungeon_crawl/misc/attackable.png"

INTERACTION_OPACITY = 500
INTERACTION_SPRITE = "imgs/dungeon_crawl/misc/landing.png"

NEW_TURN_SPRITE = "imgs/interface/new_turn.png"

CRACKED_SPRITE = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"

FRAME_SPRITE = "imgs/interface/frame.png"

LIGHTLY_DAMAGED_SPRITE = "imgs/dungeon_crawl/misc/damage_meter_lightly_damaged.png"
MODERATELY_DAMAGED_SPRITE = (
    "imgs/dungeon_crawl/misc/damage_meter_moderately_damaged.png"
)
HEAVILY_DAMAGED_SPRITE = "imgs/dungeon_crawl/misc/damage_meter_heavily_damaged.png"
SEVERELY_DAMAGED_SPRITE = "imgs/dungeon_crawl/misc/damage_meter_severely_damaged.png"
ALMOST_DEAD_SPRITE = "imgs/dungeon_crawl/misc/damage_meter_almost_dead.png"

HP_BAR_SPRITE = "imgs/dungeon_crawl/misc/damage_meter_sample.png"

constant_sprites = {}


def init_constant_sprites() -> None:
    """
    Initialize all sprites by loading them into a pygame Surface.
    These sprites will be available in all modules by importing the constant_sprites dictionary.
    """
    constant_sprites["landing"] = pygame.transform.scale(
        pygame.image.load(LANDING_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE)
    )
    constant_sprites["attackable"] = pygame.transform.scale(
        pygame.image.load(ATTACKABLE_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE)
    )
    constant_sprites["interaction"] = pygame.transform.scale(
        pygame.image.load(INTERACTION_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE)
    )
    new_turn = pygame.image.load(NEW_TURN_SPRITE).convert_alpha()
    new_turn = pygame.transform.scale(
        new_turn.convert_alpha(),
        (int(new_turn.get_width() * 1.5), int(new_turn.get_height() * 1.5)),
    )
    constant_sprites["new_turn"] = new_turn
    constant_sprites["victory"] = new_turn.copy()
    constant_sprites["defeat"] = new_turn.copy()

    constant_sprites["new_turn_pos"] = (
        MAX_MAP_WIDTH / 2 - new_turn.get_width() / 2,
        MAX_MAP_HEIGHT / 2 - new_turn.get_height() / 2,
    )
    new_turn_text = fonts["TITLE_FONT"].render(STR_NEW_TURN, 1, WHITE)
    new_turn.blit(
        new_turn_text,
        (
            new_turn.get_width() / 2 - new_turn_text.get_width() / 2,
            new_turn.get_height() / 2 - new_turn_text.get_height() / 2,
        ),
    )

    constant_sprites["victory_pos"] = constant_sprites["new_turn_pos"]
    victory_text = fonts["TITLE_FONT"].render(STR_VICTORY, 1, WHITE)
    victory_text_position = (
        constant_sprites["victory"].get_width() / 2 - victory_text.get_width() / 2,
        constant_sprites["victory"].get_height() / 2 - victory_text.get_height() / 2,
    )
    constant_sprites["victory"].blit(victory_text, victory_text_position)

    constant_sprites["defeat_pos"] = constant_sprites["new_turn_pos"]
    defeat_text = fonts["TITLE_FONT"].render(STR_DEFEAT, 1, WHITE)
    defeat_text_pos = (
        constant_sprites["defeat"].get_width() / 2 - defeat_text.get_width() / 2,
        constant_sprites["defeat"].get_height() / 2 - defeat_text.get_height() / 2,
    )
    constant_sprites["defeat"].blit(defeat_text, defeat_text_pos)

    constant_sprites["cracked"] = pygame.transform.scale(
        pygame.image.load(CRACKED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE)
    )

    constant_sprites["frame"] = pygame.transform.scale(
        pygame.image.load(FRAME_SPRITE).convert_alpha(),
        (TILE_SIZE + 10, TILE_SIZE + 10),
    )
    constant_sprites["main_mission_text"] = fonts["SIDEBAR_TITLE_FONT"].render(
        STR_MAIN_MISSION, 1, BLACK
    )
    constant_sprites["secondaries_mission_text"] = fonts["SIDEBAR_TITLE_FONT"].render(
        STR_OPTIONAL_OBJECTIVES, 1, BLACK
    )

    constant_sprites["lightly_damaged"] = pygame.transform.scale(
        pygame.image.load(LIGHTLY_DAMAGED_SPRITE).convert_alpha(),
        (TILE_SIZE, TILE_SIZE),
    )
    constant_sprites["moderately_damaged"] = pygame.transform.scale(
        pygame.image.load(MODERATELY_DAMAGED_SPRITE).convert_alpha(),
        (TILE_SIZE, TILE_SIZE),
    )
    constant_sprites["heavily_damaged"] = pygame.transform.scale(
        pygame.image.load(HEAVILY_DAMAGED_SPRITE).convert_alpha(),
        (TILE_SIZE, TILE_SIZE),
    )
    constant_sprites["severely_damaged"] = pygame.transform.scale(
        pygame.image.load(SEVERELY_DAMAGED_SPRITE).convert_alpha(),
        (TILE_SIZE, TILE_SIZE),
    )
    constant_sprites["almost_dead"] = pygame.transform.scale(
        pygame.image.load(ALMOST_DEAD_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE)
    )

    constant_sprites["hp_bar"] = pygame.transform.scale(
        pygame.image.load(HP_BAR_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE)
    )
