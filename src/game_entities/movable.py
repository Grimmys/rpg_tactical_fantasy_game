from src.game_entities.destroyable import *
from enum import IntEnum, Enum, auto

from src.game_entities.skill import SkillNature

#beiba
import pygame.mixer
import os

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

    def __init__(self, name, pos, sprite, hp, defense, res, max_moves, strength, attack_kind, strategy, lvl=1,
                 skills=None, alterations=None, compl_sprite=None):
        Destroyable.__init__(self, name, pos, sprite, hp, defense, res)
        if skills is None:
            skills = []
        if alterations is None:
            alterations = []
        self._max_moves = max_moves
        self.on_move = []
        self.timer = TIMER
        self.strength = strength
        self.alterations = alterations
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

        self._attack_kind = DamageKind[attack_kind] if attack_kind is not None else None
        self.strategy = EntityStrategy[strategy]
        self.skills = skills

        #beiba
        pg.mixer.init()
        self.walksfx = pg.mixer.Sound(os.path.join('sound_fx', 'walk.ogg'))
        self.skltnsfx = pg.mixer.Sound(os.path.join('sound_fx', 'skeleton_walk.ogg'))
        self.ncrphgsfx = pg.mixer.Sound(os.path.join('sound_fx', 'necro_walk.ogg'))
        self.centsfx = pg.mixer.Sound(os.path.join('sound_fx', 'cent_walk.ogg'))

    def display(self, screen):
        Destroyable.display(self, screen)
        if self.state in range(EntityState.ON_MOVE, EntityState.HAVE_TO_ATTACK + 1):
            screen.blit(Movable.SELECTED_DISPLAY, self.pos)

    @property
    def attack_kind(self):
        return self._attack_kind

    def attacked(self, ent, damage, kind, allies):
        # Compute distance of all allies
        allies_dist = [(ally, (abs(self.pos[0] - ally.pos[0]) + abs(self.pos[1] - ally.pos[1])) // TILE_SIZE)
                       for ally in allies]

        # Check if stats are modified by some alterations
        temp_def_change = self.get_stat_change('defense')
        temp_res_change = self.get_stat_change('resistance')
        # Check if a skill is boosting stats during combat
        for skill in self.skills:
            if skill.nature is SkillNature.ALLY_BOOST and [ally[0] for ally in allies_dist if ally[1] == 1]:
                if 'defense' in skill.stats:
                    temp_def_change += skill.power
                if 'resistance' in skill.stats:
                    temp_res_change += skill.power
        # Apply boosts (including alterations changes)
        self.defense += temp_def_change
        self.res += temp_res_change

        # Resolve attack with boosted stats
        Destroyable.attacked(self, ent, damage, kind, allies)

        # Restore stats to normal
        self.defense -= temp_def_change
        self.res -= temp_res_change

        return self.hp

    def end_turn(self):
        self.state = EntityState.FINISHED
        # Remove all alterations that are finished
        self.alterations = [alt for alt in self.alterations if not alt.is_finished()]

    def turn_is_finished(self):
        return self.state == EntityState.FINISHED

    @property
    def max_moves(self):
        return self._max_moves

    def set_move(self, path):
        self.on_move = path
        self.state = EntityState.ON_MOVE

        #beiba
        if self.strategy == EntityStrategy.MANUAL:
            if self.name == "chrisemon":
                pygame.mixer.Sound.play(self.centsfx)
            else:
                pygame.mixer.Sound.play(self.walksfx)
        if self.name == "skeleton":
            if self.target is not None:
                pygame.mixer.Sound.play(self.skltnsfx)
        if self.name == "necrophage":
            if self.target is not None:
                pygame.mixer.Sound.play(self.ncrphgsfx)
        if self.name == "assassin":
            if self.target is not None:
                pygame.mixer.Sound.play(self.walksfx)

    def get_formatted_alterations(self):
        formatted_string = ""
        for alteration in self.alterations:
            formatted_string += str(alteration) + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_abbreviated_alterations(self):
        formatted_string = ""
        for alteration in self.alterations:
            formatted_string += alteration.abbreviated_name + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def set_alteration(self, alteration):
        self.alterations.append(alteration)

    def get_alterations_effect(self, eff):
        return list(filter(lambda alteration: alteration.name == eff, self.alterations))

    def get_stat_change(self, stat):
        # Check if character as a bonus due to alteration
        return sum(map(lambda alt: alt.power, self.get_alterations_effect(stat + '_up'))) - \
               sum(map(lambda alt: alt.power, self.get_alterations_effect(stat + '_down')))

    def get_formatted_stat_change(self, stat):
        change = self.get_stat_change(stat)
        if change > 0:
            return ' (+' + str(change) + ')'
        elif change < 0:
            return ' (' + str(change) + ')'
        return ''

    # The return value is a boolean indicating if the target gained a level
    def earn_xp(self, xp):
        self.xp += xp
        if self.xp >= self.xp_next_lvl:
            self.lvl_up()
            return True
        return False

    def determine_xp_goal(self):
        return int(Movable.XP_NEXT_LVL_BASE * pow(1.5, self.lvl - 1))

    def lvl_up(self):
        self.lvl += 1
        self.xp -= self.xp_next_lvl
        self.xp_next_lvl = self.determine_xp_goal()

    def get_item(self, index):
        return self.items[index] if 0 <= index < len(self.items) else False

    def has_free_space(self):
        return len(self.items) < NB_ITEMS_MAX

    def set_item(self, item):
        if self.has_free_space():
            self.items.append(item)
            return True
        return False

    def remove_item(self, item):
        for index, it in enumerate(self.items):
            if it.id == item.id:
                return self.items.pop(index)
        return -1

    def use_item(self, item):
        return item.use(self)

    def move(self):
        self.timer -= Movable.move_speed
        if self.timer <= 0:
            self.pos = self.on_move.pop(0)
            self.timer = TIMER
        if not self.on_move:
            self.state = EntityState.HAVE_TO_ATTACK

    def can_attack(self):
        # Check if no alteration forbids the entity to attack
        for alt in self.alterations:
            if 'no_attack' in alt.specificities:
                return False
        return True

    def act(self, possible_moves, targets):
        if self.state is EntityState.HAVE_TO_ACT:
            return self.determine_move(possible_moves, targets)
        elif self.state is EntityState.ON_MOVE:
            self.move()
        elif self.state is EntityState.HAVE_TO_ATTACK:
            attack = self.determine_attack(targets)
            if self.can_attack() and attack:
                return attack
            else:
                self.end_turn()
        return None

    def determine_attack(self, targets):
        temporary_attack = None
        for r in self.reach:
            for target in targets:
                if abs(self.pos[0] - target.pos[0]) + abs(self.pos[1] - target.pos[1]) == TILE_SIZE * r:
                    if self.target and target == self.target:
                        return target.pos
                    temporary_attack = target.pos
        return temporary_attack

    def determine_move(self, possible_moves, targets):
        self.target = None
        if self.strategy is EntityStrategy.SEMI_ACTIVE:
            for target, dist in targets.items():
                for r in self.reach:
                    for move in possible_moves:
                        # Try to find move next to one target
                        if abs(move[0] - target.pos[0]) + abs(move[1] - target.pos[1]) == TILE_SIZE * r:
                            self.target = target
                            return move
        elif self.strategy is EntityStrategy.ACTIVE:
            # Targets the nearest opponent
            self.target = min(targets.keys(), key=(lambda k: targets[k]))
            best_move = possible_moves[self.pos]
            min_dist = INITIAL_MAX
            for r in self.reach:
                for move in possible_moves:
                    # Search for the nearest move to target
                    dist = abs(move[0] - self.target.pos[0]) + abs(move[1] - self.target.pos[1]) - (TILE_SIZE * r)
                    if 0 <= dist < min_dist:
                        best_move = move
                        min_dist = dist
            return best_move
        return self.pos

    # Should return damage dealt
    def attack(self, ent):
        return self.strength

    def new_turn(self):
        self.state = EntityState.HAVE_TO_ACT
        # Increment alterations turns passed
        for alteration in self.alterations:
            alteration.increment()

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

        # Save alterations
        alterations = etree.SubElement(tree, 'alterations')
        for alteration in self.alterations:
            alterations.append(alteration.save('alteration'))

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
