from src.Movable import Movable
from src.constants import TILE_SIZE
import math

STATIC = 0
PASSIVE = 1
SEMI_ACTIVE = 2
ACTIVE = 3


class Foe(Movable):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, xp_gain, strategy, lvl=1):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, lvl)
        '''Possible states :
                - 0 : Have to act
                - 1 : On move
                - 2 : Have to attack
                - 3 : Turn finished
        '''
        self.state = 0
        self.xp_gain = xp_gain
        '''Possible strategies :
                - STATIC : Foe will never move, just attack if possible
                - PASSIVE : Foe will react to attacks, and pursue opponent if it's trying to flee
                - SEMI_ACTIVE : Foe will only move if an opponent is at reach
                - ACTIVE : Foe always move to get closer from opponents'''
        self.strategy = strategy

    def get_state(self):
        return self.state

    def get_xp_obtained(self):
        return self.xp_gain

    def set_move(self, pos):
        Movable.set_move(self, pos)
        self.state = 1

    def move(self):
        Movable.move(self)
        if not self.on_move:
            self.state = 2

    def determine_move(self, targets, possible_moves, possible_attacks):
        if self.strategy == SEMI_ACTIVE:
            for attack in possible_attacks:
                for move in possible_moves:
                    # Try to find move next to possible attack
                    if abs(move[0] - attack[0]) + abs(move[1] - attack[1]) == TILE_SIZE:
                        return move
        if self.strategy == ACTIVE:
            # TODO
            pass
        elif self.strategy == PASSIVE:
            # TODO
            pass
        return self.pos

    def end_turn(self):
        self.state = 3
