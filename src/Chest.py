from src.Entity import Entity

class Chest(Entity):
    def __init__(self, name, pos, sprite_close, sprite_open):
        Entity.__init__(self, name, pos, sprite_close)
        self.sprite_open = sprite_open