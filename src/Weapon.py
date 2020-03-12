from src.Equipment import Equipment


class Weapon(Equipment):
    def __init__(self, name, sprite, description, price, equipped_sprite, atk, attack_kind, weight, durability, reach):
        Equipment.__init__(self, name, sprite, description, price, equipped_sprite, 'right_hand', 0, 0, atk, weight)
        self.durability_max = durability
        self.durability = self.durability_max
        self.reach = reach
        self.attack_kind = attack_kind

    def get_attack_kind(self):
        return self.attack_kind

    def get_range(self):
        return self.reach

    def used(self):
        self.durability -= 1
        return self.durability
