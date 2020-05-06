from src.Equipment import Equipment
from src.Destroyable import DamageKind


class Weapon(Equipment):
    def __init__(self, name, sprite, description, price, equipped_sprite, atk, attack_kind, weight,
                 durability, reach, restrictions):
        Equipment.__init__(self, name, sprite, description, price, equipped_sprite, 'right_hand',
                           0, 0, atk, weight, restrictions)
        self.durability_max = durability
        self.durability = self.durability_max
        self.reach = reach
        self.attack_kind = DamageKind[attack_kind]

    def used(self):
        self.durability -= 1
        return self.durability
