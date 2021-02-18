import random as rd
from enum import Enum, auto

from lxml import etree

from src.game_entities.gold import Gold
from src.game_entities.movable import Movable


class Keyword(Enum):
    LARGE = auto()
    CAVALRY = auto()
    FLY = auto()
    SMALL = auto()
    MUTANT = auto()
    UNDEAD = auto()


class Foe(Movable):
    grow_rates = {}

    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, strategy, reach, xp_gain,
                 loot, keywords=None, lvl=1, alterations=None):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, strategy, lvl, alterations=alterations)
        self.reach = reach
        self.xp_gain = int(xp_gain * (1.1 ** (lvl - 1)))
        self.potential_loot = loot
        self.keywords = []
        if keywords:
            self.keywords = [Keyword[k.upper()] for k in keywords]

    def stats_up(self, nb_lvl=1):
        grow_rates = Foe.grow_rates[self.name]
        for i in range(nb_lvl):
            self.hp_max += rd.choice(grow_rates['hp'])
            self.defense += rd.choice(grow_rates['def'])
            self.res += rd.choice(grow_rates['res'])
            self.strength += rd.choice(grow_rates['str'])
            self.xp_gain = int(self.xp_gain * 1.1)

    def roll_for_loot(self):
        loot = []
        for (item, probability) in self.potential_loot:
            if rd.random() < probability:
                loot.append(item)
        return loot

    def get_formatted_keywords(self):
        return ", ".join([k.name.lower().capitalize() for k in self.keywords])

    def get_formatted_reach(self):
        return ', '.join([str(reach) for reach in self.reach])

    def save(self, tree_name):
        tree = Movable.save(self, tree_name)

        # Save loot
        loot = etree.SubElement(tree, "loot")
        for (item, probability) in self.potential_loot:
            if isinstance(item, Gold):
                it_el = etree.SubElement(loot, 'gold')
                it_name = etree.SubElement(it_el, 'amount')
                it_name.text = str(item.amount)
            else:
                it_el = etree.SubElement(loot, 'item')
                it_name = etree.SubElement(it_el, 'name')
                it_name.text = item.name
            it_probability = etree.SubElement(it_el, 'probability')
            it_probability.text = str(probability)

        return tree
