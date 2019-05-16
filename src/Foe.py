from src.Movable import Movable

class Foe(Movable):
    def __init__(self, name, pos, sprite, hp, max_move, strength, lvl=1):
        Movable.__init__(self, name, pos, sprite, hp, max_move, strength, lvl)
        '''Possible states :
                - 0 : Have to act
                - 1 : On move
                - 2 : Have to attack
                - 3 : Turn finished
        '''
        self.state = 0

    def get_state(self):
        return self.state

    def set_move(self, pos):
        Movable.set_move(self, pos)
        self.state = 1

    def move(self):
        Movable.move(self)
        if not self.on_move:
            self.state = 2

    def end_turn(self):
        self.state = 3