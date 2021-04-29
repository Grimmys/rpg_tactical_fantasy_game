import random as rd

from lxml import etree

from src.game_entities.equipment import Equipment
from src.game_entities.destroyable import DamageKind
from src.game_entities.skill import SkillNature
from src.gui.tools import distance


class Weapon(Equipment):
    def __init__(self, name, sprite, description, price, equipped_sprite, atk, attack_kind, weight,
                 durability, reach, restrictions, possible_effects, strong_against, can_charge=False):
        Equipment.__init__(self, name, sprite, description, price, equipped_sprite, 'right_hand',
                           0, 0, atk, weight, restrictions)
        self.durability_max = durability
        self.durability = self.durability_max
        self.reach = reach
        self.attack_kind = DamageKind[attack_kind]
        self.effects = possible_effects
        self.strong_against = strong_against
        self.can_charge = can_charge

    def get_formatted_strong_against(self):
        return ", ".join([k.name.lower().capitalize() for k in self.strong_against])

    def hit(self, holder, target):
        multiplier = 1
        if self.can_charge:
            distance_traveled = distance(holder.old_pos, holder.pos)
            if distance_traveled >= 5:
                multiplier += 0.5 * ((distance_traveled - 2) // 3)
        for keyword in target.keywords:
            if keyword in self.strong_against:
                multiplier += 1
        return int(multiplier * self.atk)

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
                if skill.nature is SkillNature.ALTERATION_CHANCE_BOOST \
                        and eff['effect'].alteration in skill.alterations:
                    probability += skill.power

            if rd.randint(0, 100) < probability:
                effects.append(eff['effect'])
        return effects

    def save(self, tree_name):
        tree = Equipment.save(self, tree_name)

        # Save durability
        durability = etree.SubElement(tree, 'durability')
        durability.text = str(self.durability)

        return tree
