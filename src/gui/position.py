"""
Define Position data structure, corresponding to a 2D coordinate on a pygame Surface.
"""
from typing import Union

import pygame

Position = Union[pygame.Vector2, tuple[int, int]]
