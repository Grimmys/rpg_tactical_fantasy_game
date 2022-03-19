import pygame

from src.scenes.scene import Scene
from src.scenes.start_scene import StartScene


class SceneManager:

    def __init__(self, screen: pygame.Surface) -> None:
        self.active_scene: Scene = StartScene(screen)

    def process_game_iteration(self) -> bool:
        quit_game = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            elif event.type == pygame.MOUSEMOTION:
                self.active_scene.motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button in (1, 3):
                    quit_game = self.active_scene.click(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button in (1, 3):
                    self.active_scene.button_down(event.button, event.pos)
        self.active_scene.update_state()
        self.active_scene.display()
        return quit_game
