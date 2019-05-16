from src.Entity import Entity

class Portals(Entity):
    def __init__(self, name, pos_first, pos_second, sprite):
        Entity.__init__(self, name, pos_first, sprite)
        self.pos_second = pos_second

    def display(self, screen):
        Entity.display(self, screen)
        screen.blit(self.sprite, self.pos_second)

    def get_pos(self):
        return [self.pos, self.pos_second]