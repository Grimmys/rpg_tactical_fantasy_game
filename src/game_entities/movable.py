from enum import IntEnum, auto, Enum
import os
from typing import Union, Sequence

import pygame
from lxml import etree

from src.constants import TILE_SIZE, ANIMATION_SPEED, INITIAL_MAX
from src.game_entities.alteration import Alteration
from src.game_entities.consumable import Consumable
from src.game_entities.destroyable import Destroyable, DamageKind
from src.game_entities.entity import Entity
from src.game_entities.item import Item
from src.game_entities.skill import SkillNature, Skill

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
    """ """

    SELECTED_DISPLAY: pygame.Surface = None
    XP_NEXT_LVL_BASE: int = 15
    move_speed: int = ANIMATION_SPEED

    @staticmethod
    def init_constant_sprites() -> None:
        """ """
        selected_sprite: str = "imgs/dungeon_crawl/misc/cursor.png"
        Movable.SELECTED_DISPLAY = pygame.transform.scale(
            pygame.image.load(selected_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )

    def __init__(
        self,
        name: str,
        position: tuple[int, int],
        sprite: Union[str, pygame.Surface],
        hit_points: int,
        defense: int,
        resistance: int,
        max_moves: int,
        strength: int,
        attack_kind: str,
        strategy: str,
        lvl: int = 1,
        skills: Sequence[Skill] = None,
        alterations: Sequence[Alteration] = None,
        complementary_sprite_link: str = None,
    ) -> None:
        super().__init__(name, position, sprite, hit_points, defense, resistance)
        if skills is None:
            skills = []
        if alterations is None:
            alterations = []
        self._max_moves: int = max_moves
        self.on_move: list[tuple[int, int]] = []
        self.timer: int = TIMER
        self.strength: int = strength
        self.alterations: list[Alteration] = alterations
        self.lvl: int = lvl
        self.experience: int = 0
        self.experience_to_lvl_up: int = self.determine_xp_goal()
        self.items: list[Item] = []
        self.nb_items_max: int = NB_ITEMS_MAX
        self.state: EntityState = EntityState.HAVE_TO_ACT
        self.target: Union[Entity, None] = None
        if complementary_sprite_link:
            complementary_sprite: pygame.Surface = pygame.transform.scale(
                pygame.image.load(complementary_sprite_link).convert_alpha(),
                (TILE_SIZE, TILE_SIZE),
            )
            self.sprite.blit(complementary_sprite, (0, 0))

        self._attack_kind: DamageKind = (
            DamageKind[attack_kind] if attack_kind is not None else None
        )
        self.strategy: EntityStrategy = EntityStrategy[strategy]
        self.skills: Sequence[Skill] = skills

        self.walk_sfx: pygame.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "walk.ogg")
        )
        self.skeleton_sfx: pygame.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "skeleton_walk.ogg")
        )
        self.necrophage_sfx: pygame.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "necro_walk.ogg")
        )
        self.centaur_sfx: pygame.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "cent_walk.ogg")
        )

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the movable entity on the given screen.
        Also display an indicator if the entity is currently active.

        Keyword arguments:
        screen -- the screen on which the movable entity should be drawn
        """
        Destroyable.display(self, screen)
        if self.state in range(EntityState.ON_MOVE, EntityState.HAVE_TO_ATTACK + 1):
            screen.blit(Movable.SELECTED_DISPLAY, self.position)

    @property
    def attack_kind(self) -> DamageKind:
        """

        :return:
        """
        return self._attack_kind

    def attacked(
        self, entity: Entity, damage: int, kind: DamageKind, allies: Sequence[Entity]
    ) -> int:
        """

        :param entity:
        :param damage:
        :param kind:
        :param allies:
        :return:
        """
        # Compute distance of all allies
        allies_dist: Sequence[tuple[Entity, int]] = [
            (
                ally,
                (
                    abs(self.position[0] - ally.position[0])
                    + abs(self.position[1] - ally.position[1])
                )
                // TILE_SIZE,
            )
            for ally in allies
        ]

        # Check if stats are modified by some alterations
        temp_def_change: int = self.get_stat_change("defense")
        temp_res_change: int = self.get_stat_change("resistance")
        # Check if a skill is boosting stats during combat
        for skill in self.skills:
            if skill.nature is SkillNature.ALLY_BOOST and [
                ally[0] for ally in allies_dist if ally[1] == 1
            ]:
                if "defense" in skill.stats:
                    temp_def_change += skill.power
                if "resistance" in skill.stats:
                    temp_res_change += skill.power
        # Apply boosts (including alterations changes)
        self.defense += temp_def_change
        self.resistance += temp_res_change

        # Resolve attack with boosted stats
        Destroyable.attacked(self, entity, damage, kind, allies)

        # Restore stats to normal
        self.defense -= temp_def_change
        self.resistance -= temp_res_change

        return self.hit_points

    def end_turn(self) -> None:
        """ """
        self.state = EntityState.FINISHED
        # Remove all alterations that are finished
        self.alterations = [alt for alt in self.alterations if not alt.is_finished()]

    def turn_is_finished(self) -> bool:
        """

        :return:
        """
        return self.state == EntityState.FINISHED

    @property
    def max_moves(self) -> int:
        """

        :return:
        """
        return self._max_moves

    def set_move(self, path: Sequence[tuple[int, int]]) -> None:
        """

        :param path:
        """
        self.on_move = path
        self.state = EntityState.ON_MOVE

        if self.strategy == EntityStrategy.MANUAL:
            if self.name == "chrisemon":
                pygame.mixer.Sound.play(self.centaur_sfx)
            else:
                pygame.mixer.Sound.play(self.walk_sfx)
        elif self.target is not None:
            if self.name == "skeleton":
                pygame.mixer.Sound.play(self.skeleton_sfx)
            elif self.name == "necrophage":
                pygame.mixer.Sound.play(self.necrophage_sfx)
            elif self.name == "assassin":
                pygame.mixer.Sound.play(self.walk_sfx)

    def get_formatted_alterations(self) -> str:
        """

        :return:
        """
        formatted_string: str = ""
        for alteration in self.alterations:
            formatted_string += str(alteration) + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_abbreviated_alterations(self) -> str:
        """

        :return:
        """
        formatted_string: str = ""
        for alteration in self.alterations:
            formatted_string += alteration.abbreviated_name + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def set_alteration(self, alteration: Alteration) -> None:
        """

        :param alteration:
        """
        self.alterations.append(alteration)

    def get_alterations_effect(self, eff: str) -> list[Alteration]:
        """

        :param eff:
        :return:
        """
        return list(filter(lambda alteration: alteration.name == eff, self.alterations))

    def get_stat_change(self, stat: str) -> int:
        """

        :param stat:
        :return:
        """
        # Check if character as a bonus due to alteration
        return sum(
            map(lambda alt: alt.power, self.get_alterations_effect(stat + "_up"))
        ) - sum(map(lambda alt: alt.power, self.get_alterations_effect(stat + "_down")))

    def get_formatted_stat_change(self, stat: str) -> str:
        """

        :param stat:
        :return:
        """
        change: int = self.get_stat_change(stat)
        if change > 0:
            return " (+" + str(change) + ")"
        if change < 0:
            return " (" + str(change) + ")"
        return ""

    # The return value is a boolean indicating if the target gained a level
    def earn_xp(self, xp: int) -> bool:
        """

        :param xp:
        :return:
        """
        self.experience += xp
        if self.experience >= self.experience_to_lvl_up:
            self.lvl_up()
            return True
        return False

    def determine_xp_goal(self) -> int:
        """

        :return:
        """
        return int(Movable.XP_NEXT_LVL_BASE * pow(1.5, self.lvl - 1))

    def lvl_up(self) -> None:
        """ """
        self.lvl += 1
        self.experience -= self.experience_to_lvl_up
        self.experience_to_lvl_up = self.determine_xp_goal()

    def get_item(self, index: int) -> Item:
        """

        :param index:
        :return:
        """
        return self.items[index] if 0 <= index < len(self.items) else False

    def has_free_space(self) -> bool:
        """

        :return:
        """
        return len(self.items) < NB_ITEMS_MAX

    def set_item(self, item: Item) -> bool:
        """

        :param item:
        :return:
        """
        if self.has_free_space():
            self.items.append(item)
            return True
        return False

    def remove_item(self, item_to_remove: Item) -> Item:
        """

        :param item_to_remove:
        :return:
        """
        for index, item in enumerate(self.items):
            if item.identifier == item_to_remove.identifier:
                return self.items.pop(index)
        return -1

    def use_item(self, item: Consumable) -> tuple[bool, Sequence[str]]:
        """

        :param item:
        :return:
        """
        return item.use(self)

    def move(self) -> None:
        """ """
        self.timer -= Movable.move_speed
        if self.timer <= 0:
            self.position = self.on_move.pop(0)
            self.timer = TIMER
        if not self.on_move:
            self.state = EntityState.HAVE_TO_ATTACK

    def can_attack(self) -> bool:
        """

        :return:
        """
        # Check if no alteration forbids the entity to attack
        for alt in self.alterations:
            if "no_attack" in alt.specificities:
                return False
        return True

    def act(
        self, possible_moves: Sequence[tuple[int, int]], targets: Sequence[Entity]
    ) -> Union[tuple[int, int], None]:
        """

        :param possible_moves:
        :param targets:
        :return:
        """
        if self.state is EntityState.HAVE_TO_ACT:
            return self.determine_move(possible_moves, targets)
        if self.state is EntityState.ON_MOVE:
            self.move()
        elif self.state is EntityState.HAVE_TO_ATTACK:
            attack = self.determine_attack(targets)
            if self.can_attack() and attack:
                return attack
            self.end_turn()
        return None

    def determine_attack(self, targets: Sequence[Entity]) -> tuple[int, int]:
        """

        :param targets:
        :return:
        """
        temporary_attack: Union[tuple[int, int], None] = None
        for distance in self.reach:
            for target in targets:
                if (
                    abs(self.position[0] - target.position[0])
                    + abs(self.position[1] - target.position[1])
                    == TILE_SIZE * distance
                ):
                    if self.target and target == self.target:
                        return target.position
                    temporary_attack = target.position
        return temporary_attack

    def determine_move(self, possible_moves, targets) -> tuple[int, int]:
        """

        :param possible_moves:
        :param targets:
        :return:
        """
        self.target: Union[tuple[int, int], None] = None
        if self.strategy is EntityStrategy.SEMI_ACTIVE:
            for target, dist in targets.items():
                for distance in self.reach:
                    for move in possible_moves:
                        # Try to find move next to one target
                        if (
                            abs(move[0] - target.position[0])
                            + abs(move[1] - target.position[1])
                            == TILE_SIZE * distance
                        ):
                            self.target = target
                            return move
        elif self.strategy is EntityStrategy.ACTIVE:
            # Targets the nearest opponent
            self.target = min(targets.keys(), key=(lambda k: targets[k]))
            best_move = possible_moves[self.position]
            min_dist = INITIAL_MAX
            for distance in self.reach:
                for move in possible_moves:
                    # Search for the nearest move to target
                    dist = (
                        abs(move[0] - self.target.position[0])
                        + abs(move[1] - self.target.position[1])
                        - (TILE_SIZE * distance)
                    )
                    if 0 <= dist < min_dist:
                        best_move = move
                        min_dist = dist
            return best_move
        return self.position

    # Should return damage dealt
    def attack(self, entity: Entity) -> int:
        """

        :param entity:
        :return:
        """
        return self.strength

    def new_turn(self) -> None:
        """ """
        self.state = EntityState.HAVE_TO_ACT
        # Increment alterations turns passed
        for alteration in self.alterations:
            alteration.increment()

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the movable entity in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save level
        level: etree.SubElement = etree.SubElement(tree, "level")
        level.text = str(self.lvl)

        # Save exp
        experience: etree.SubElement = etree.SubElement(tree, "exp")
        experience.text = str(self.experience)

        # Save strategy
        strategy: etree.SubElement = etree.SubElement(tree, "strategy")
        strategy.text = self.strategy.name

        # Save skills
        skills: etree.SubElement = etree.SubElement(tree, "skills")
        for skill in self.skills:
            skill_el: etree.SubElement = etree.SubElement(skills, "skill")
            skill_name = etree.SubElement(skill_el, "name")
            skill_name.text = str(skill)

        # Save alterations
        alterations: etree.SubElement = etree.SubElement(tree, "alterations")
        for alteration in self.alterations:
            alterations.append(alteration.save("alteration"))

        # Save stats
        hit_points_max: etree.SubElement = etree.SubElement(tree, "hp")
        hit_points_max.text = str(self.hit_points_max)
        atk: etree.SubElement = etree.SubElement(tree, "strength")
        atk.text = str(self.strength)
        defense: etree.SubElement = etree.SubElement(tree, "defense")
        defense.text = str(self.defense)
        res: etree.SubElement = etree.SubElement(tree, "resistance")
        res.text = str(self.resistance)
        move: etree.SubElement = etree.SubElement(tree, "move")
        move.text = str(self._max_moves)

        return tree
