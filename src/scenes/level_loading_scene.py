"""
Define LevelLoadingScene class, the scene responsible of displaying basic information about the level that is starting.
"""

from typing import Optional

import pygame

from src.constants import WHITE
from src.gui.animation import Animation, FrameDescription
from src.gui.fonts import fonts
from src.scenes.level_scene import LevelScene
from src.scenes.scene import Scene

DELAY_BETWEEN_FRAMES = 120


class LevelLoadingScene(Scene):
    """
    This scene is always loaded right before a level scene.
    It is responsible of displaying generic information about the next level to get the player ready for it.

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
        self.animation: Optional[Animation] = Animation(self.load_level_introduction_animation_frames(),
                                                        DELAY_BETWEEN_FRAMES)

    def load_level_introduction_animation_frames(self) -> list[FrameDescription]:
        """
        Load all the frames for the loading screen animation.

        Return the ordered list of frames.
        """
        level_name_rendering = fonts["LEVEL_TITLE_FONT"].render(f"Level {self.level.number}", True, WHITE)
        level_title_screen = self.screen.copy()
        level_title_screen.blit(level_name_rendering, (level_title_screen.get_width() // 2 -
                                                       level_name_rendering.get_width() // 2,
                                                       level_title_screen.get_height() // 2 -
                                                       level_name_rendering.get_height() // 2))
        main_frame = {"sprite": level_title_screen, "position": pygame.Vector2(0, 0)}
        return [main_frame]

    def display(self) -> None:
        """
        Display the animation if it is not finished.
        """
        if self.animation:
            self.animation.display(self.screen)

    def update_state(self) -> bool:
        """
        Update the animation.

        Return whether the scene should be ended or not.
        """
        if self.animation and self.animation.animate():
            self.animation = None

        return not self.animation
