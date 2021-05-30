"""
Defines fonts that will be used all over the application.
The init_fonts function should be called at the beginning of the application
after pygame initialization.
"""
from typing import Union

import pygame

fonts_description: dict[str, dict[str, Union[str, int]]] = {
    "BUTTON_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 16,
    },
    "ITEM_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 18,
    },
    "ITEM_FONT_HOVER": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 19,
    },
    "ITEM_FONT_STRONG": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 18,
    },
    "MISSION_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 20,
    },
    "MENU_SUB_TITLE_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 22,
    },
    "ITEM_DESC_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 24,
    },
    "MENU_TITLE_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 26,
    },
    "TITLE_FONT": {
        "name": "fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf",
        "size": 46,
    },
    "ITALIC_ITEM_FONT": {"name": "fonts/minya_nouvelle_it.ttf", "size": 14},
    "ITALIC_ITEM_FONT_HOVER": {"name": "fonts/minya_nouvelle_it.ttf", "size": 16},
    "FPS_FONT": {"default": True},
}

fonts: dict[str, pygame.font.Font] = {}


def init_fonts() -> None:
    """
    Load all fonts registred in fonts_description.
    System font will be load if the keyword 'default' is present in the description provided.
    These fonts will be available in all modules by importing the fonts dictionary.
    """
    global fonts
    for font in fonts_description:
        if "default" in fonts_description[font]:
            # Use pygame's default font
            fonts[font] = pygame.font.SysFont("arial", 20, True)
        else:
            fonts[font] = pygame.font.Font(
                fonts_description[font]["name"], fonts_description[font]["size"]
            )
