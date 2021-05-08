from src.game_entities.entity import Entity


class Portal(Entity):
    def __init__(self, pos_first, sprite):
        Entity.__init__(self, "Portal", pos_first, sprite)
        self.linked_to = None

    @staticmethod
    def link_portals(first_portal, second_portal):
        first_portal.linked_to = second_portal
        second_portal.linked_to = first_portal
