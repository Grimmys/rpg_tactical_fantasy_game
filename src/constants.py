"""Module to keep all the constants commonly used by other modules.

Can be imported from anywhere. Where more than one constant is needed, import * for ease of use.

"""
import pygame as pg

TILE_SIZE = 48
MENU_WIDTH = TILE_SIZE * 20
MENU_HEIGHT = 100
WIN_WIDTH = TILE_SIZE * 20
WIN_HEIGHT = TILE_SIZE * 10 + MENU_HEIGHT

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GREY = (150, 150, 150)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MIDNIGHT_BLUE = (75, 75, 212)
MARINE_BLUE = (34, 61, 200)
ORANGE = (255, 140, 0)
YELLOW = (143, 143, 5)
LIGHT_YELLOW = (255, 255, 0)
GOLD = (200, 172, 34)
BROWN = (139, 69, 19)
BROWN_RED = (165, 42, 42)
MAROON = (128, 0, 0)
TURQUOISE = (64, 224, 208)

# Fonts
TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 46)
MENU_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 26)
MENU_SUB_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 22)
ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 16)
ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 24)
ITALIC_ITEM_FONT = pg.font.Font('fonts/minya_nouvelle_it.ttf', 14)

# Standard menu size
ITEM_MENU_WIDTH = 550


ANIMATION_SPEED = 4

# Types of damages
PHYSICAL = 0
SPIRITUAL = 1

# Value for kind of action on close button
UNFINAL_ACTION = 1
FINAL_ACTION = 2