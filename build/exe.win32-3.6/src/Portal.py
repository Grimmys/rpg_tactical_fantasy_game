from src.Entity import Entity


class Portal(Entity):
    def __init__(self, name, pos_first, sprite):
        Entity.__init__(self, name, pos_first, sprite)
        self.linked_to = None

    def get_linked_portal(self):
        return self.linked_to

    @staticmethod
    def link_portals(p1, p2):
        p1.linked_to = p2
        p2.linked_to = p1
