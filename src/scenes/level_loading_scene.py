"""
Define LevelLoadingScene class, the scene responsible of displaying basic information about the level that is starting.
"""

from typing import Optional

import pygame

from src.constants import WHITE
from src.gui.animation import Frame
from src.gui.fade_in_out_animation import FadeInOutAnimation
from src.gui.fonts import fonts
from src.gui.position import Position
from src.scenes.level_scene import LevelScene
from src.scenes.scene import Scene
from src.services.language import *

DELAY_BETWEEN_FRAMES = 2
TITLE_VISIBILITY_DURATION = 120

CHAPTER_LEVEL_SEPARATION_HEIGHT = 100


class LevelLoadingScene(Scene):
    """
    This scene is always loaded right before a level scene.
    It is responsible for displaying generic information about the next level to get the player ready for it while
    the level is being loaded.

    Keyword arguments:
    screen -- the pygame Surface related to the scene
    level -- the level related to this loading scene

    Attributes:
    level -- the level related to this loading scene
    animation -- the loading screen animation currently being performed
    """

    def __init__(self, screen: pygame.Surface, level: LevelScene) -> None:
        super().__init__(screen)
        self.level: LevelScene = level
        self.animation: Optional[FadeInOutAnimation] = FadeInOutAnimation(
            self._load_level_introduction_animation_frame(), TITLE_VISIBILITY_DURATION
        )

    def _load_level_introduction_animation_frame(self) -> Frame:
        """
        Load the frame for the loading screen animation.

        Return the loaded frame.
        """
        level_title_rendering = self._generate_level_title_rendering()

        level_title_screen = pygame.Surface(self.screen.get_size())
        level_title_screen.blit(
            level_title_rendering,
            (
                level_title_screen.get_width() // 2
                - level_title_rendering.get_width() // 2,
                level_title_screen.get_height() // 2
                - level_title_rendering.get_height() // 2,
            ),
        )

        return Frame(level_title_screen, Position(0, 0), DELAY_BETWEEN_FRAMES)

    def _generate_level_title_rendering(self) -> pygame.Surface:
        """
        Render chapter and level name.

        Return the surface containing the rendered text.
        """
        chapter_rendering = fonts["LEVEL_TITLE_FONT"].render(
            f_CHAPTER_NUMBER(self.level.chapter), True, WHITE
        )

        level_name_rendering = fonts["LEVEL_TITLE_FONT"].render(
            f_LEVEL_NUMBER_AND_NAME(self.level.number, self.level.name), True, WHITE
        )

        surface_size = (
            max(chapter_rendering.get_width(), level_name_rendering.get_width()),
            chapter_rendering.get_height()
            + CHAPTER_LEVEL_SEPARATION_HEIGHT
            + level_name_rendering.get_height(),
        )
        level_title_rendering = pygame.Surface(surface_size)
        level_title_rendering.blit(
            chapter_rendering,
            (
                level_title_rendering.get_width() // 2
                - chapter_rendering.get_width() // 2,
                0,
            ),
        )
        level_title_rendering.blit(
            level_name_rendering,
            (
                level_title_rendering.get_width() // 2
                - level_name_rendering.get_width() // 2,
                chapter_rendering.get_height() + CHAPTER_LEVEL_SEPARATION_HEIGHT,
            ),
        )

        return level_title_rendering

    def display(self) -> None:
        """
        Display the animation if it is not finished.
        """
        if self.animation:
            self.animation.display(self.screen)

    def update_state(self) -> bool:
        """
        Proceed to loading of level content if needed.
        Update the animation.

        Return whether the scene should be ended or not.
        """
        if not self.level.is_loaded and self.animation.is_fade_in_finished:
            self.level.load_level_content()

        if self.animation and self.animation.animate():
            self.animation = None

        return not self.animation
