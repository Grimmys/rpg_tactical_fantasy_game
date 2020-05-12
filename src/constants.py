"""Module to keep all the constants commonly used by other modules.

Can be imported from anywhere. Where more than one constant is needed, import * for ease of use.

"""
import pygame as pg

TILE_SIZE = 48
MENU_WIDTH = TILE_SIZE * 22
MENU_HEIGHT = 100

MAX_MAP_WIDTH = 22 * TILE_SIZE
MAX_MAP_HEIGHT = 12 * TILE_SIZE

WIN_WIDTH = MAX_MAP_WIDTH
WIN_HEIGHT = MAX_MAP_HEIGHT + MENU_HEIGHT

MAIN_WIN_WIDTH = 800
MAIN_WIN_HEIGHT = 800

# Colors
WHITE = pg.Color('white')
BLACK = pg.Color('black')
LIGHT_GREY = pg.Color('grey59')
GREY = pg.Color('grey50')
RED = pg.Color('red')
GREEN = pg.Color('green')
DARK_GREEN = pg.Color('green4')
BLUE = pg.Color('blue')
MIDNIGHT_BLUE = pg.Color('midnightblue')
MARINE_BLUE = pg.Color('royalblue4')
ORANGE = pg.Color('orange')
YELLOW = pg.Color('yellow4')
LIGHT_YELLOW = pg.Color('yellow')
GOLD = pg.Color('gold3')
BROWN = pg.Color('brown4')
BROWN_RED = pg.Color('brown')
MAROON = pg.Color('maroon')
TURQUOISE = pg.Color('turquoise')

# Display parameters
MARGIN_TOP = 10
MARGIN_BOX = 20

# Standard menus and buttons sizes
START_MENU_WIDTH = 500
ITEM_MENU_WIDTH = 600
BATTLE_SUMMARY_WIDTH = 600
DIALOG_WIDTH = 800
TRADE_MENU_WIDTH = 1050
ITEM_INFO_MENU_WIDTH = 800
ITEM_DELETE_MENU_WIDTH = 350
ACTION_MENU_WIDTH = 200
STATUS_MENU_WIDTH = 300
STATUS_INFO_MENU_WIDTH = 500
EQUIPMENT_MENU_WIDTH = 600
BUTTON_MENU_SIZE = (150, 30)
ITEM_BUTTON_SIZE = (250, TILE_SIZE + 30)
TRADE_ITEM_BUTTON_SIZE = (230, TILE_SIZE + 30)
EQUIP_BUTTON_SIZE = (250, TILE_SIZE + 30)
BUTTON_SIZE = (150, 30)
CLOSE_BUTTON_SIZE = (150, 50)


# Options default values
ANIMATION_SPEED = 4

# Value for kind of action on close button
UNFINAL_ACTION = 1
FINAL_ACTION = 2
