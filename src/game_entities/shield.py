from src.game_entities.equipment import Equipment


class Shield(Equipment):
    def __init__(self, name, sprite, description, price, equipped_sprites, defense, weight, parry,
                 durability, restrictions):
        Equipment.__init__(self, name, sprite, description, price, equipped_sprites, 'left_hand',
                           defense, 0, 0, weight, restrictions)
        self.durability_max = durability
        self.durability = self.durability_max
        self.parry = parry

    def used(self):
        self.durability -= 1
        return self.durability
