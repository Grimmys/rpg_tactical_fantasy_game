from src.Entity import Entity


class Portal(Entity):
    def __init__(self, pos_first, sprite):
        Entity.__init__(self, "Portal", pos_first, sprite)
        self.linked_to = None

    @staticmethod
    def link_portals(p1, p2):
        p1.linked_to = p2
        p2.linked_to = p1
