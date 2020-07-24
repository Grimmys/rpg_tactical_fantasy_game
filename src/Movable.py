from src.Destroyable import *
from src.Key import Key
from enum import IntEnum, Enum, auto

from src.Skill import SkillNature

TIMER = 60
NB_ITEMS_MAX = 8


class EntityState(IntEnum):
    HAVE_TO_ACT = auto()
    ON_MOVE = auto()
    HAVE_TO_ATTACK = auto()
    FINISHED = auto()


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

    def __init__(self, name, pos, sprite, hp, defense, res, max_moves, strength, attack_kind, strategy, lvl=1, skills=[],
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
        self.skills = skills

    def display(self, screen):
        Destroyable.display(self, screen)
        if self.state in range(EntityState.ON_MOVE, EntityState.HAVE_TO_ATTACK + 1):
            screen.blit(Movable.SELECTED_DISPLAY, self.pos)

    def attacked(self, ent, damages, kind, allies):
        # Compute distance of all allies
        allies_dist = [(ally, (abs(self.pos[0] - ally.pos[0]) + abs(self.pos[1] - ally.pos[1])) // TILE_SIZE)
                       for ally in allies]

        # Check if a skill is boosting stats during combat
        temp_def_boost = 0
        temp_res_boost = 0
        for skill in self.skills:
            if skill.nature is SkillNature.ALLY_BOOST and [ally[0] for ally in allies_dist if ally[1] == 1]:
                if 'defense' in skill.stats:
                    temp_def_boost += skill.power
                if 'resistance' in skill.stats:
                    temp_res_boost += skill.power
        # Apply boosts
        self.defense += temp_def_boost
        self.res += temp_res_boost

        # Resolve attack with boosted stats
        Destroyable.attacked(self, ent, damages, kind, allies)

        # Restore stats to normal
        self.defense -= temp_def_boost
        self.res -= temp_res_boost

        return self.hp

    def end_turn(self):
        self.state = EntityState.FINISHED

    def turn_is_finished(self):
        return self.state == EntityState.FINISHED

    def get_formatted_reach(self):
        return ', '.join([str(reach) for reach in self.reach])

    @property
    def max_moves(self):
        return self._max_moves

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
        return [alteration for alteration in self.alterations if alteration.name == eff]

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

    def remove_chest_key(self):
        best_candidate = None
        for it in self.items:
            if isinstance(it, Key) and it.for_chest:
                if not best_candidate:
                    best_candidate = it
                elif not it.for_door:
                    # If a key could be used to open a chest but not a door, it's better to use it
                    best_candidate = it
        self.items.remove(best_candidate)

    def remove_door_key(self):
        best_candidate = None
        for it in self.items:
            if isinstance(it, Key) and it.for_door:
                if not best_candidate:
                    best_candidate = it
                elif not it.for_chest:
                    # If a key could be used to open a door but not a chest, it's better to use it
                    best_candidate = it
        self.items.remove(best_candidate)

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
                for d in self.reach:
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

        # Save strategy
        strategy = etree.SubElement(tree, 'strategy')
        strategy.text = self.strategy.name

        # Save skills
        skills = etree.SubElement(tree, 'skills')
        for skill in self.skills:
            skill_el = etree.SubElement(skills, 'skill')
            skill_name = etree.SubElement(skill_el, 'name')
            skill_name.text = str(skill)

        # Save stats
        hp_m = etree.SubElement(tree, 'hp')
        hp_m.text = str(self.hp_max)
        atk = etree.SubElement(tree, 'strength')
        atk.text = str(self.strength)
        defense = etree.SubElement(tree, 'defense')
        defense.text = str(self.defense)
        res = etree.SubElement(tree, 'resistance')
        res.text = str(self.res)
        move = etree.SubElement(tree, 'move')
        move.text = str(self._max_moves)

        return tree
