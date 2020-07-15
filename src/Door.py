from src.Entity import Entity


class Door(Entity):
    def __init__(self, pos, sprite):
        Entity.__init__(self, "Door", pos, sprite)
        self.pick_lock_initiated = False
