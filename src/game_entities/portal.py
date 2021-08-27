from __future__ import annotations
from typing import Union

from src.game_entities.entity import Entity


class Portal(Entity):
    """ """

    def __init__(self, position: tuple[int, int], sprite: str) -> None:
        super().__init__("Portal", position, sprite)
        self.linked_to: Union[Portal, None] = None

    @staticmethod
    def link_portals(first_portal: Portal, second_portal: Portal) -> None:
        """
        Link two portals between them in both ways.

        Keyword arguments:
        first_portal -- the first concerned portal
        second_portal -- the other concerned portal
        """
        first_portal.linked_to = second_portal
        second_portal.linked_to = first_portal
