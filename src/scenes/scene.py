import pygame


class Scene:

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def display(self) -> None:
        pass

    def update_state(self) -> None:
        pass
