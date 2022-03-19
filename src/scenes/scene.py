import pygame

from src.gui.position import Position


class Scene:

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen

    def display(self) -> None:
        pass

    def update_state(self) -> None:
        pass

    def motion(self, position: Position) -> None:
        pass

    def click(self, button: int, position: Position) -> bool:
        pass

    def button_down(self, button: int, position: Position) -> None:
        pass
