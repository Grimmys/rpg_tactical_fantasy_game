from src.equipment import Equipment
from src.destroyable import DamageKind

import random as rd

from src.skill import SkillNature


class Weapon(Equipment):
    def __init__(self, name, sprite, description, price, equipped_sprite, atk, attack_kind, weight,
                 durability, reach, restrictions, possible_effects):
        Equipment.__init__(self, name, sprite, description, price, equipped_sprite, 'right_hand',
                           0, 0, atk, weight, restrictions)
        self.durability_max = durability
        self.durability = self.durability_max
        self.reach = reach
        self.attack_kind = DamageKind[attack_kind]
        self.effects = possible_effects

    def used(self):
        self.durability -= 1
        self.resell_price = int((self.price // 2) * (self.durability / self.durability_max))
        return self.durability

    def applied_effects(self, user, target):
        # Try to trigger one or more effects
        effects = []
        for eff in self.effects:
            probability = eff['probability']
            for skill in user.skills:
                if skill.nature is SkillNature.ALTERATION_CHANCE_BOOST and eff['effect'].alteration in skill.alterations:
                    probability += skill.power

            if rd.randint(0, 100) < probability:
                effects.append(eff['effect'])
        return effects
