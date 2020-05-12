from src.Destroyable import *
from src.Key import Key
from enum import IntEnum, Enum, auto

TIMER = 60
NB_ITEMS_MAX = 8


class EntityState(IntEnum):
    HAVE_TO_ACT = 0
    ON_MOVE = 1
    HAVE_TO_ATTACK = 2
    FINISHED = 3


class EntityStrategy(Enum):
    # Entity will never move, just attack if possible
    STATIC = auto()
    # Entity will react to attacks, and pursue opponent if it's trying to flee
    PASSIVE = auto()
    # Entity will only move if an opponent is at reach
    SEMI_ACTIVE = auto()
    # Entity always move to get closer from opponents
    ACTIVE = auto()
    # Entity is controlled by an human player
    MANUAL = auto()


class Movable(Destroyable):
    SELECTED_DISPLAY = None
    XP_NEXT_LVL_BASE = 15
    move_speed = ANIMATION_SPEED

    @staticmethod
    def init_constant_sprites():
        selected_sprite = 'imgs/dungeon_crawl/misc/cursor.png'
        Movable.SELECTED_DISPLAY = pg.transform.scale(pg.image.load(selected_sprite).convert_alpha(),
                                                      (TILE_SIZE, TILE_SIZE))

    def __init__(self, name, pos, sprite, hp, defense, res, max_moves, strength, attack_kind, strategy, lvl=1,
                 compl_sprite=None):
        Destroyable.__init__(self, name, pos, sprite, hp, defense, res)
        self._max_moves = max_moves
        self.on_move = []
        self.timer = TIMER
        self.strength = strength
        self.alterations = []
        self.lvl = lvl
        self.xp = 0
        self.xp_next_lvl = self.determine_xp_goal()
        self.items = []
        self.nb_items_max = NB_ITEMS_MAX
        self.state = EntityState.HAVE_TO_ACT
        self.target = None
        if compl_sprite:
            compl = pg.transform.scale(pg.image.load(compl_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
            self.sprite.blit(compl, (0, 0))

        self.attack_kind = DamageKind[attack_kind] if attack_kind is not None else None
        self.strategy = EntityStrategy[strategy]

    def display(self, screen):
        Destroyable.display(self, screen)
        if self.state in range(EntityState.ON_MOVE, EntityState.HAVE_TO_ATTACK + 1):
            screen.blit(Movable.SELECTED_DISPLAY, self.pos)

    def end_turn(self):
        self.state = EntityState.FINISHED

    def turn_is_finished(self):
        return self.state == EntityState.FINISHED

    def get_reach(self):
        return [1]

    def get_formatted_reach(self):
        return ', '.join([str(reach) for reach in self.get_reach()])

    @property
    def max_moves(self):
        alterations = self.get_alterations_effect('speed')
        maximum = self._max_moves
        for alt in alterations:
            maximum += alt.power
        return maximum

    def set_move(self, path):
        self.on_move = path
        self.state = EntityState.ON_MOVE

    def get_formatted_alterations(self):
        formatted_string = ""
        for alteration in self.alterations:
            formatted_string += alteration.get_formatted_name() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def set_alteration(self, alteration):
        self.alterations.append(alteration)

    def get_alterations_effect(self, eff):
        return [alteration for alteration in self.alterations if alteration.get_effect() == eff]

    def earn_xp(self, xp):
        self.xp += xp
        if self.xp >= self.xp_next_lvl:
            self.lvl_up()

    def determine_xp_goal(self):
        return int(Movable.XP_NEXT_LVL_BASE * pow(1.5, self.lvl - 1))

    def lvl_up(self):
        self.lvl += 1
        self.xp -= self.xp_next_lvl
        self.xp_next_lvl = self.determine_xp_goal()

    def get_item(self, index):
        if index not in range(len(self.items)):
            return False
        return self.items[index]

    def has_free_space(self):
        return len(self.items) < NB_ITEMS_MAX

    def set_item(self, item):
        if not self.has_free_space:
            return False
        self.items.append(item)
        return True

    def remove_item(self, item):
        for index, it in enumerate(self.items):
            if it.id == item.id:
                return self.items.pop(index)

    def remove_key(self):
        for index, it in enumerate(self.items):
            if isinstance(it, Key):
                return self.items.pop(index)

    def use_item(self, item):
        return item.use(self)

    def move(self):
        self.timer -= Movable.move_speed
        if self.timer <= 0:
            self.pos = self.on_move.pop(0)
            self.timer = TIMER
        if not self.on_move:
            self.state = EntityState.HAVE_TO_ATTACK

    def act(self, possible_moves, targets):
        if self.state is EntityState.HAVE_TO_ACT:
            return self.determine_move(possible_moves, targets)
        elif self.state is EntityState.ON_MOVE:
            self.move()
        elif self.state is EntityState.HAVE_TO_ATTACK:
            if self.target:
                return self.target.pos
            else:
                self.end_turn()
        return None

    def determine_move(self, possible_moves, targets):
        self.target = None
        if self.strategy is EntityStrategy.SEMI_ACTIVE:
            for target in targets:
                for d in self.get_reach():
                    for move in possible_moves:
                        # Try to find move next to one target
                        if abs(move[0] - target.pos[0]) + abs(move[1] - target.pos[1]) == TILE_SIZE * d:
                            self.target = target
                            return move
        if self.strategy is EntityStrategy.ACTIVE:
            # TODO
            pass
        elif self.strategy is EntityStrategy.PASSIVE:
            # TODO
            pass
        return self.pos

    # Should return damage dealt
    def attack(self, ent):
        return self.strength

    def new_turn(self):
        self.state = EntityState.HAVE_TO_ACT
        # Verify if any alteration is finished
        for alteration in self.alterations:
            if alteration.increment():
                self.alterations.remove(alteration)

    def save(self, tree_name):
        tree = Destroyable.save(self, tree_name)

        # Save level
        level = etree.SubElement(tree, 'level')
        level.text = str(self.lvl)

        # Save exp
        exp = etree.SubElement(tree, 'exp')
        exp.text = str(self.xp)

        # Save stats
        hp_m = etree.SubElement(tree, 'hp')
        hp_m.text = str(self.hp_max)
        atk = etree.SubElement(tree, 'strength')
        atk.text = str(self.strength)
        defense = etree.SubElement(tree, 'def')
        defense.text = str(self.defense)
        res = etree.SubElement(tree, 'res')
        res.text = str(self.res)
        move = etree.SubElement(tree, 'move')
        move.text = str(self._max_moves)

        return tree
