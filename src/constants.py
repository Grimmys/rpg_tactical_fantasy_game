"""
Module to keep all the constants commonly used by other modules.

Can be imported from anywhere.
"""
import pygame

FRAME_RATE = 60

INITIAL_MAX = 10000

TILE_SIZE = 48
MENU_WIDTH = TILE_SIZE * 22
MENU_HEIGHT = 100

GRID_WIDTH = 22
GRID_HEIGHT = 14
MAX_MAP_WIDTH = GRID_WIDTH * TILE_SIZE
MAX_MAP_HEIGHT = GRID_HEIGHT * TILE_SIZE

WIN_WIDTH = MAX_MAP_WIDTH
WIN_HEIGHT = MAX_MAP_HEIGHT + MENU_HEIGHT

MAIN_WIN_WIDTH = 600
MAIN_WIN_HEIGHT = 600

# Colors
WHITE = pygame.Color("white")
BLACK = pygame.Color("black")
LIGHT_GREY = pygame.Color("grey59")
GREY = pygame.Color("grey50")
RED = pygame.Color("red")
GREEN = pygame.Color("green")
DARK_GREEN = pygame.Color("green4")
BLUE = pygame.Color("blue")
MIDNIGHT_BLUE = pygame.Color("midnightblue")
MARINE_BLUE = pygame.Color("royalblue4")
ORANGE = pygame.Color("orange")
YELLOW = pygame.Color("yellow4")
LIGHT_YELLOW = pygame.Color("yellow")
GOLD = pygame.Color("gold3")
BROWN = pygame.Color("brown4")
BROWN_RED = pygame.Color("brown")
MAROON = pygame.Color("maroon")
TURQUOISE = pygame.Color("turquoise")

# Display parameters
MARGIN_TOP = 10
MARGIN_BOX = 20

# Standard menus and buttons sizes
START_MENU_WIDTH = 500
ITEM_MENU_WIDTH = 700
BATTLE_SUMMARY_WIDTH = 600
DIALOG_WIDTH = 800
TRADE_MENU_WIDTH = 1050
ITEM_INFO_MENU_WIDTH = 800
ITEM_DELETE_MENU_WIDTH = 350
ACTION_MENU_WIDTH = 300
STATUS_MENU_WIDTH = 700
FOE_STATUS_MENU_WIDTH = 700
STATUS_INFO_MENU_WIDTH = 300
EQUIPMENT_MENU_WIDTH = 600
REWARD_MENU_WIDTH = 800
ITEM_BUTTON_SIZE = (280, TILE_SIZE + 30)
TRADE_ITEM_BUTTON_SIZE = (230, TILE_SIZE + 30)
EQUIP_BUTTON_SIZE = (250, TILE_SIZE + 30)
BUTTON_SIZE = (200, 60)

# Options default values
ANIMATION_SPEED = 4
SCREEN_SIZE = 2

# Value for kind of action on close button
UNFINAL_ACTION = 1
FINAL_ACTION = 2

# Number of save slots
SAVE_SLOTS = 3
