from src.Destroyable import Destroyable

ANIMATION_SPEED = 4
TIMER = 60
NB_ITEMS_MAX = 8

class Movable(Destroyable):
    XP_NEXT_LVL_BASE = 15

    def __init__(self, name, pos, sprite, hp, max_move, strength, lvl=1):
        Destroyable.__init__(self, name, pos, sprite, hp)
        self.max_move = max_move
        self.on_move = []
        self.timer = TIMER
        self.strength = strength
        self.res = 0
        self.defense = 0
        self.alterations = []
        self.lvl = lvl
        self.xp = 0
        self.xp_next_lvl = self.determine_xp_goal()
        self.alterations = []
        self.lvl = lvl
        self.state = 0
        self.items = []
        self.nb_items_max = NB_ITEMS_MAX

    def get_strength(self):
        return self.strength

    def get_resistance(self):
        return self.res

    def get_defense(self):
        return self.defense

    def get_max_moves(self):
        return self.max_move

    def set_move(self, path):
        self.on_move = path

    def get_move(self):
        return self.on_move

    def get_alterations(self):
        return self.alterations

    def get_formatted_alterations(self):
        formatted_string = ""
        for alteration in self.alterations:
            formatted_string += alteration.capitalize() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_lvl(self):
        return self.lvl

    def get_xp(self):
        return self.xp

    def determine_xp_goal(self):
        return int(Movable.XP_NEXT_LVL_BASE * pow(1.5, self.lvl - 1))

    def get_next_lvl_xp(self):
        return self.xp_next_lvl

    def get_item(self, index):
        if index not in range(len(self.items)):
            return False
        return self.items[index]

    def get_items(self):
        return self.items

    def set_item(self, item):
        if len(self.items) == NB_ITEMS_MAX:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item):
        id = item.get_id()
        for index, it in enumerate(self.items):
            if it.get_id() == id:
                return self.items.pop(index)

    def use_item(self, item):
        return item.use(self)

    def get_nb_items_max(self):
        return self.nb_items_max

    def move(self):
        self.timer -= ANIMATION_SPEED
        if self.timer <= 0:
            self.pos = self.on_move.pop(0)
            self.timer = TIMER

    # Should return damage dealt
    def attack(self, ent):
        return self.strength

    def new_turn(self):
        self.state = 0