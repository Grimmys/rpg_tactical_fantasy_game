from src.Entity import Entity

class Fountain(Entity):
    def __init__(self, name, pos, sprite):
        Entity.__init__(self, name, pos, sprite)