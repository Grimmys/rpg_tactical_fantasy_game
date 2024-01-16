"""
Defines Portal class, an entity that is working by pair and that could teleport movable entities.
"""

from __future__ import annotations

from typing import Optional

from src.game_entities.entity import Entity
from src.gui.position import Position


class Portal(Entity):
    """
    A Portal is always linked to another Portal.
    When a movable entity is interacting with a member of a portal pair, it would likely be teleported to the other
    member of the pair.

    Keyword arguments:
    position -- the position of the portal
    sprite -- the relative path to the visual representation of the portal

    Attributes:
    linked_to -- the second member of the pair
    """

    def __init__(self, position: Position, sprite: str) -> None:
        super().__init__("Portal", position, sprite)
        self.linked_to: Optional[Portal] = None

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
