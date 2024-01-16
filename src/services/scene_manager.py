"""
Define SceneManager class, the orchestrator of the communication between every different scene.
"""

from __future__ import annotations

import pygame

from src.constants import MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH
from src.scenes.level_loading_scene import LevelLoadingScene
from src.scenes.level_scene import LevelScene, LevelStatus
from src.scenes.scene import QuitActionKind, Scene
from src.scenes.start_scene import StartScene


class SceneManager:
    """
    The scene manager supervises the ordering of all scenes and decides
    which one should be the current active scene.
    It processes any evolution of the active scene at each game iteration.

    Keyword arguments:
    screen -- the pygame Surface corresponding to the initial scene of the game

    Attributes:
    active_scene -- the current active scene that should handle all incoming events
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.active_scene: Scene = StartScene(screen)

    def process_game_iteration(self) -> QuitActionKind:
        """
        Handle a single game iteration.
        Extract every ongoing event and delegate them to the active scene.
        Update the state of the active scene.

        Return whether the game should be ended or not.
        """
        quit_game = QuitActionKind.CONTINUE
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return QuitActionKind.QUIT
            elif event.type == pygame.MOUSEMOTION:
                self.active_scene.motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    quit_game = self.active_scene.click(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    self.active_scene.button_down(event.button, event.pos)
            elif event.type == pygame.KEYDOWN:
                self.active_scene.key_down(event.key)
        if self.active_scene.update_state():
            self.start_new_scene()
            return QuitActionKind.CONTINUE
        self.active_scene.display()
        return quit_game

    def start_new_scene(self) -> None:
        """
        Switch to a new scene.
        Check what was the previous scene to determine which scene should be the next one depending on the context.
        """
        if isinstance(self.active_scene, StartScene):
            self.active_scene = LevelLoadingScene(
                self.active_scene.level.screen, self.active_scene.level
            )
            return

        if isinstance(self.active_scene, LevelLoadingScene):
            self.active_scene = self.active_scene.level
            return

        if isinstance(self.active_scene, LevelScene):
            next_level_number = self.active_scene.number + 1
            if (
                self.active_scene.game_phase is LevelStatus.ENDED_VICTORY
                and next_level_number in LevelScene.IDS
            ):
                team = self.active_scene.escaped_players + self.active_scene.players
                for player in team:
                    player.healed(player.hit_points_max)
                    player.new_turn()
                level_screen = StartScene.generate_level_window()
                level = LevelScene(
                    level_screen,
                    f"maps/level_{next_level_number}/",
                    next_level_number,
                    players=team,
                )
                self.active_scene = LevelLoadingScene(level_screen, level)
            else:
                self.active_scene = StartScene(
                    pygame.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
                )
