"""
Defines fonts that will be used all over the application.
The init_fonts function should be called at the beginning of the application
after pygame initialization.
"""
import pygame

from src.services.language import *

fonts: dict[str, pygame.font.Font] = {}


def init_fonts() -> None:
    """
    Load all fonts registered in fonts_description.
    System font will be load if the keyword 'default' is present in the description provided.
    These fonts will be available in all modules by importing fonts dictionary.
    """
    for font_name, font in fonts_description.items():
        if "default" in font:
            # Use pygame's default font
            fonts[font_name] = pygame.font.SysFont("arial", 20, True)
        else:
            fonts[font_name] = pygame.font.Font(font["name"], font["size"])
