import random as rd

from src.Movable import Movable


class Foe(Movable):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, strategy, reach, xp_gain,
                 loot, lvl=1):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, strategy, lvl)
        self.reach = reach
        self.xp_gain = int(xp_gain * (1.1 ** (lvl - 1)))
        self.potential_loot = loot

    def stats_up(self, nb_lvl=1):
        for i in range(nb_lvl):
            self.hp_max += rd.randrange(1, 5)  # Gain between 0 and 4
            self.defense += rd.randrange(0, 2)  # Gain between 0 and 2
            self.res += rd.randrange(0, 2)  # Gain between 0 and 1
            self.strength += rd.randrange(0, 3)  # Gain between 0 and 2
            self.xp_gain = int(self.xp_gain * 1.1)

    def roll_for_loot(self):
        loot = []
        for (item, probability) in self.potential_loot:
            if rd.random() < probability:
                loot.append(item)
        return loot
