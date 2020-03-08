import random as rd

from src.Movable import Movable


class Foe(Movable):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, xp_gain, strategy, lvl=1):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, strategy, lvl)
        '''Possible states :
                - 0 : Have to act
                - 1 : On move
                - 2 : Have to attack
                - 3 : Turn finished
        '''

        self.xp_gain = xp_gain * (1.1 * lvl - 1)
        self.attack_kind = attack_kind

    def get_xp_obtained(self):
        return self.xp_gain

    def get_attack_kind(self):
        return self.attack_kind

    def set_move(self, pos):
        Movable.set_move(self, pos)
        self.state = 1

    def move(self):
        Movable.move(self)
        if not self.on_move:
            self.state = 2

    def end_turn(self):
        self.state = 3

    def stats_up(self, nb_lvl=1):
        for i in range(nb_lvl):
            self.hp_max += rd.randrange(1, 5)  # Gain between 0 and 4
            self.defense += rd.randrange(0, 2)  # Gain between 0 and 2
            self.res += rd.randrange(0, 2)  # Gain between 0 and 1
            self.strength += rd.randrange(0, 3)  # Gain between 0 and 2
            self.xp_gain = int(self.xp_gain * 1.1)
