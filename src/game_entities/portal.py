from __future__ import annotations
from typing import Union

from src.game_entities.entity import Entity


class Portal(Entity):
    def __init__(self, position: tuple[int, int], sprite: str) -> None:
        Entity.__init__(self, "Portal", position, sprite)
        self.linked_to: Union[Portal, None] = None

    @staticmethod
    def link_portals(first_portal: Portal, second_portal: Portal) -> None:
        first_portal.linked_to = second_portal
        second_portal.linked_to = first_portal
