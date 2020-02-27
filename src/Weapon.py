from src.Equipment import Equipment


class Weapon(Equipment):
    def __init__(self, name, sprite, description, equipped_sprite, atk, weight, durability, reach):
        Equipment.__init__(self, name, sprite, description, equipped_sprite, 'right_hand', 0, 0, atk, weight)
        self.durability_max = durability
        self.durability = self.durability_max
        self.reach = reach

    def get_power(self):
        return self.atk

    def get_range(self):
        return self.reach

    def used(self):
        self.durability -= 1
        return self.durability
