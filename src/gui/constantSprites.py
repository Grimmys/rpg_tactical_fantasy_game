import pygame as pg

from src.gui.fonts import fonts
from src.constants import TILE_SIZE, MAX_MAP_WIDTH, MAX_MAP_HEIGHT, WHITE, BLACK

LANDING_OPACITY = 80
LANDING_SPRITE = 'imgs/dungeon_crawl/misc/move.bmp'

ATTACKABLE_OPACITY = 80
ATTACKABLE_SPRITE = 'imgs/dungeon_crawl/misc/attackable.bmp'

INTERACTION_OPACITY = 500
INTERACTION_SPRITE = 'imgs/dungeon_crawl/misc/landing.bmp'

NEW_TURN_SPRITE = 'imgs/interface/new_turn.bmp'

CRACKED_SPRITE = 'imgs/dungeon_crawl/dungeon/wall/destroyed_wall.bmp'

FRAME_SPRITE = 'imgs/interface/frame.bmp'

LIGHTLY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_lightly_damaged.bmp'
MODERATELY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_moderately_damaged.bmp'
HEAVILY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_heavily_damaged.bmp'
SEVERELY_DAMAGED_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_severely_damaged.bmp'
ALMOST_DEAD_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_almost_dead.bmp'

HP_BAR_SPRITE = 'imgs/dungeon_crawl/misc/damage_meter_sample.bmp'

constant_sprites = {}


def init_constant_sprites():
    constant_sprites['landing'] = pg.transform.scale(pg.image.load(LANDING_SPRITE).convert_alpha(),
                                                     (TILE_SIZE, TILE_SIZE))
    constant_sprites['attackable'] = pg.transform.scale(pg.image.load(ATTACKABLE_SPRITE).convert_alpha(),
                                                        (TILE_SIZE, TILE_SIZE))
    constant_sprites['interaction'] = pg.transform.scale(pg.image.load(INTERACTION_SPRITE).convert_alpha(),
                                                         (TILE_SIZE, TILE_SIZE))
    NEW_TURN = pg.image.load(NEW_TURN_SPRITE).convert_alpha()
    NEW_TURN = pg.transform.scale(NEW_TURN.convert_alpha(), (int(NEW_TURN.get_width() * 1.5),
                                                             int(NEW_TURN.get_height() * 1.5)))
    constant_sprites['new_turn'] = NEW_TURN
    constant_sprites['victory'] = NEW_TURN.copy()
    constant_sprites['defeat'] = NEW_TURN.copy()

    constant_sprites['new_turn_pos'] = (MAX_MAP_WIDTH / 2 - NEW_TURN.get_width() / 2, MAX_MAP_HEIGHT / 2 - NEW_TURN.get_height() / 2)
    NEW_TURN_TEXT = fonts['TITLE_FONT'].render("NEW TURN !", 1, WHITE)
    NEW_TURN.blit(NEW_TURN_TEXT, (NEW_TURN.get_width() / 2 - NEW_TURN_TEXT.get_width() / 2,
                    NEW_TURN.get_height() / 2 - NEW_TURN_TEXT.get_height() / 2))

    constant_sprites['victory_pos'] = constant_sprites['new_turn_pos']
    VICTORY_TEXT = fonts['TITLE_FONT'].render("VICTORY !", 1, WHITE)
    VICTORY_TEXT_POS = (constant_sprites['victory'].get_width() / 2 - VICTORY_TEXT.get_width() / 2,
                        constant_sprites['victory'].get_height() / 2 - VICTORY_TEXT.get_height() / 2)
    constant_sprites['victory'].blit(VICTORY_TEXT, VICTORY_TEXT_POS)

    constant_sprites['defeat_pos'] = constant_sprites['new_turn_pos']
    defeat_text = fonts['TITLE_FONT'].render("DEFEAT !", 1, WHITE)
    defeat_text_pos = (constant_sprites['defeat'].get_width() / 2 - defeat_text.get_width() / 2,
                       constant_sprites['defeat'].get_height() / 2 - defeat_text.get_height() / 2)
    constant_sprites['defeat'].blit(defeat_text, defeat_text_pos)

    constant_sprites['cracked'] = pg.transform.scale(pg.image.load(CRACKED_SPRITE).convert_alpha(),
                                                     (TILE_SIZE, TILE_SIZE))

    constant_sprites['frame'] = pg.transform.scale(pg.image.load(FRAME_SPRITE).convert_alpha(),
                                                   (TILE_SIZE + 10, TILE_SIZE + 10))
    constant_sprites['main_mission_text'] = fonts['MENU_TITLE_FONT'].render("MAIN MISSION", 1, BLACK)
    constant_sprites['secondaries_mission_text'] = fonts['MENU_TITLE_FONT'].render("OPTIONAL OBJECTIVES", 1, BLACK)

    constant_sprites['lightly_damaged'] = pg.transform.scale(pg.image.load(LIGHTLY_DAMAGED_SPRITE).convert_alpha(),
                                                             (TILE_SIZE, TILE_SIZE))
    constant_sprites['moderately_damaged'] = pg.transform.scale(
        pg.image.load(MODERATELY_DAMAGED_SPRITE).convert_alpha(),
        (TILE_SIZE, TILE_SIZE))
    constant_sprites['heavily_damaged'] = pg.transform.scale(pg.image.load(HEAVILY_DAMAGED_SPRITE).convert_alpha(),
                                                             (TILE_SIZE, TILE_SIZE))
    constant_sprites['severely_damaged'] = pg.transform.scale(pg.image.load(SEVERELY_DAMAGED_SPRITE).convert_alpha(),
                                                              (TILE_SIZE, TILE_SIZE))
    constant_sprites['almost_dead'] = pg.transform.scale(pg.image.load(ALMOST_DEAD_SPRITE).convert_alpha(),
                                                         (TILE_SIZE, TILE_SIZE))

    constant_sprites['hp_bar'] = pg.transform.scale(pg.image.load(HP_BAR_SPRITE).convert_alpha(),
                                                    (TILE_SIZE, TILE_SIZE))
