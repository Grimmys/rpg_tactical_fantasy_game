
from src.Entity import Entity


class Building(Entity):
    def __init__(self, name, pos, sprite, interaction=None):
        Entity.__init__(self, name, pos, sprite)
        self.interaction = interaction

    def interact(self, actor):
        if self.interaction is None:
            return "This house seems closed..."
