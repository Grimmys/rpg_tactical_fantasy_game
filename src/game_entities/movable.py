"""
Defines Movable class and enum classes for representing entity states and entity strategies,
different classes handling the management of entities that can move, only living entities as for now.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from enum import Enum, IntEnum, auto
from typing import Optional, Union

import pygame
from lxml import etree

from src.constants import ANIMATION_SPEED, INITIAL_MAX, TILE_SIZE
from src.game_entities.alteration import Alteration
from src.game_entities.consumable import Consumable
from src.game_entities.destroyable import DamageKind, Destroyable
from src.game_entities.entity import Entity
from src.game_entities.item import Item
from src.game_entities.skill import Skill, SkillNature
from src.gui.position import Position
from src.services.language import TRANSLATIONS

TIMER = 60
NB_ITEMS_MAX = 8


class EntityState(IntEnum):
    """
    Defines the cycle of states for a movable entity.
    """

    HAVE_TO_ACT = auto()
    ON_MOVE = auto()
    HAVE_TO_ATTACK = auto()
    FINISHED = auto()


class EntityStrategy(Enum):
    """
    Defines the different possible strategies of a movable entity controlled by the artificial intelligence.
    """

    # Entity will never move, just attack if possible
    STATIC = auto()
    # Entity will react to attacks, and pursue opponent if it's trying to flee
    PASSIVE = auto()
    # Entity will only move if an opponent is at reach
    SEMI_ACTIVE = auto()
    # Entity always move to get closer to opponents
    ACTIVE = auto()
    # Entity is controlled by a human player
    MANUAL = auto()


class Movable(Destroyable):
    """
    A Movable is simply a Destroyable entity that can move.
    It is the basic class for all living entities.

    Keyword arguments:
    name -- the name of the entity
    position -- the current position of the entity on screen
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen or
    the relative path to the visual representation of the entity
    hit_points -- the total of damage that the entity can take before disappearing
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks
    max_moves -- the max number of tiles that could be crossed by the entity during one movement
    strength -- the raw strength of the entity
    attack_kind -- the kind of damage dealt by the entity
    strategy -- the strategy of the entity if it's controlled by the AI
    lvl -- the current level of the entity
    skills -- the list of skills of the entity
    alterations -- the list of ongoing alterations affecting the entity
    complementary_sprite_link -- the relative path to the sprite that should be blitted on top of the base sprite

    Attributes:
    _max_moves -- the max number of tiles that could be crossed by the entity during one movement
    on_move -- the stack of the different positions through which the entity should pass for the current movement
    _timer -- the time until the entity move to the next tile during a movement
    strength -- the raw strength of the entity
    alterations -- the list of ongoing alterations affecting the entity
    lvl -- the current level of the entity
    experience -- the current amount of experience earned
    experience_to_lvl_up -- the amount of experience left to earn before next level
    items -- the list of items in the inventory
    nb_items_max -- the size of the inventory
    state -- the current state of the entity
    target -- the target of the current attack if there is any
    _attack_kind -- the kind of damage dealt by the entity
    strategy -- the strategy of the entity if it's controlled by the AI
    skills -- the list of skills of the entity
    walk_sfx -- the sound started when the entity is moving
    skeleton_sfx -- the sound started when a skeleton is moving
    necrophage_sfx -- the sound started when a necrophage is moving
    centaur_sfx -- the sound started when a centaur is moving
    """

    SELECTED_DISPLAY: pygame.Surface = None
    XP_NEXT_LVL_BASE: int = 15
    move_speed: int = ANIMATION_SPEED

    @staticmethod
    def init_constant_sprites() -> None:
        """
        Initialize the generic sprites.
        This operation should be called after the initialization of a pygame window.
        """
        selected_sprite: str = "imgs/dungeon_crawl/misc/cursor.png"
        Movable.SELECTED_DISPLAY = pygame.transform.scale(
            pygame.image.load(selected_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE)
        )

    def __init__(
        self,
        name: str,
        position: Position,
        sprite: Union[str, pygame.Surface],
        hit_points: int,
        defense: int,
        resistance: int,
        max_moves: int,
        strength: int,
        attack_kind: str,
        strategy: str,
        lvl: int = 1,
        skills: Optional[Sequence[Skill]] = None,
        alterations: Optional[Sequence[Alteration]] = None,
        complementary_sprite_link: Optional[str] = None,
    ) -> None:
        super().__init__(name, position, sprite, hit_points, defense, resistance)
        if skills is None:
            skills = []
        if alterations is None:
            alterations = []
        self._max_moves: int = max_moves
        self.on_move: list[Position] = []
        self._timer: int = TIMER
        self.strength: int = strength
        self.alterations: list[Alteration] = alterations
        self.lvl: int = lvl
        self.experience: int = 0
        self.experience_to_lvl_up: int = self.determine_xp_goal()
        self.items: list[Item] = []
        self.nb_items_max: int = NB_ITEMS_MAX
        self.state: EntityState = EntityState.HAVE_TO_ACT
        self.target: Optional[Entity] = None
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

        self.walk_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "walk.ogg")
        )
        self.skeleton_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "skeleton_walk.ogg")
        )
        self.necrophage_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "necro_walk.ogg")
        )
        self.centaur_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
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
        Return the kind of damage dealt by the entity
        """
        return self._attack_kind

    def attacked(
        self, entity: Entity, damage: int, kind: DamageKind, allies: Sequence[Entity]
    ) -> int:
        """
        Compute how much the entity should take and reduce the hit points of
        the entity by this value.

        Return the current hit points of the entity after applying the damage.

        Keyword arguments:
        entity -- the other entity that is attacking the entity
        damage -- the attack's power
        kind -- the nature of the attack
        allies -- the allies of the entity
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
        """
        Handle the end of the turn of the entity
        """
        self.state = EntityState.FINISHED
        # Remove all alterations that are finished
        self.alterations = [alt for alt in self.alterations if not alt.is_finished()]

    def turn_is_finished(self) -> bool:
        """
        Return whether entity's turn is finished or not
        """
        return self.state == EntityState.FINISHED

    @property
    def max_moves(self) -> int:
        """
        Return the max amount of tiles that can be crossed by the entity.
        """
        return self._max_moves

    def set_move(self, path: Sequence[Position]) -> None:
        """
        Set the current movement of the entity to the one given

        Play a walking sound according to the nature of the entity.

        Keyword arguments:
        path -- the ordered sequence of tiles that should be crossed by the entity
        """
        self.on_move = path
        self.state = EntityState.ON_MOVE

        # TODO: the determination of which sound should be started shouldn't be done according to the entity's name
        #  but rather according to specific attribute like the race
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
        Return the list of alterations in a formatted
        way
        """
        formatted_string: str = ""
        for alteration in self.alterations:
            try:
                formatted_string += (
                    TRANSLATIONS["alterations"][
                        str(alteration).lower().replace(" ", "_")
                    ]
                    + ", "
                )
            except KeyError:
                formatted_string += str(alteration) + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_abbreviated_alterations(self) -> str:
        """
        Return the list of alterations in an abbreviated
        way
        """
        formatted_string: str = ""
        for alteration in self.alterations:
            formatted_string += alteration.abbreviated_name + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def set_alteration(self, alteration: Alteration) -> None:
        """
        Add a new alteration to the list of alterations.

        Keyword arguments:
        alteration -- the alteration that should be added
        """
        self.alterations.append(alteration)

    def get_alterations_effect(self, eff: str) -> list[Alteration]:
        """
        Return the list of effects suffered by the entity.
        """
        return list(filter(lambda alteration: alteration.name == eff, self.alterations))

    def get_stat_change(self, stat: str) -> int:
        """
        Return the current modifier for the given statistic.

        Keyword argument:
        stat -- the name of the state for which the modifier should be returned
        """
        # Check if character as a bonus due to alteration
        return sum(
            map(lambda alt: alt.power, self.get_alterations_effect(stat + "_up"))
        ) - sum(map(lambda alt: alt.power, self.get_alterations_effect(stat + "_down")))

    def get_formatted_stat_change(self, stat: str) -> str:
        """
        Return the current modifier for the given statistic in a formatted way.

        Keyword argument:
        stat -- the name of the state for which the modifier should be returned
        """
        change: int = self.get_stat_change(stat)
        if change > 0:
            return f" (+{change})"
        if change < 0:
            return f" ({change})"
        return ""

    def earn_xp(self, experience: int) -> bool:
        """
        Handle the earning of experience.

        Return whether the entity level up or not.

        Keyword arguments:
        experience -- the amount of earned xp
        """
        self.experience += experience
        if self.experience >= self.experience_to_lvl_up:
            self.lvl_up()
            return True
        return False

    def determine_xp_goal(self) -> int:
        """
        Compute and return the amount of experience that should be earned until next level.
        """
        return int(Movable.XP_NEXT_LVL_BASE * pow(1.5, self.lvl - 1))

    def lvl_up(self) -> None:
        """
        Handle the up of the level by one.
        """
        self.lvl += 1
        self.experience -= self.experience_to_lvl_up
        self.experience_to_lvl_up = self.determine_xp_goal()

    # TODO: should return None if there is no Item found instead of False
    def get_item(self, index: int) -> Union[Item, bool]:
        """
        Return the item located at the given index of the inventory.
        Return False if no item is found at this index.

        Keyword argument:
        index -- the index of the item that should be retrieved
        """
        return self.items[index] if 0 <= index < len(self.items) else False

    def has_free_space(self) -> bool:
        """
        Return whether there is place for more items or not.
        """
        return len(self.items) < NB_ITEMS_MAX

    def set_item(self, item: Item) -> bool:
        """
        Add a new item to the inventory if there is enough place.
        Return whether the item has been added or not.

        Keyword arguments:
        item -- the item that should be added
        """
        if self.has_free_space():
            self.items.append(item)
            return True
        return False

    # TODO: should return None if there is no Item found instead of -1
    def remove_item(self, item_to_remove: Item) -> Union[Item, int]:
        """
        Remove the given item from the entity's inventory and return it.

        Keyword argument:
        item_to_remove -- the item that should be removed
        """
        for index, item in enumerate(self.items):
            if item.identifier == item_to_remove.identifier:
                return self.items.pop(index)
        return -1

    def use_item(self, item: Consumable) -> tuple[bool, Sequence[str]]:
        """
        Consume the given item.
        Return whether the item has been used or not and
        the sequence of messages that should be displayed to the player.

        Keyword arguments:
        item -- the item that should be consumed
        """
        return item.use(self)

    def move(self) -> None:
        """
        Decrease the current timer according to move speed and move the entity by one tile if it's time for.
        Change the state of the entity if the movement is finished.
        """
        self._timer -= Movable.move_speed
        if self._timer <= 0:
            self.position = self.on_move.pop(0)
            self._timer = TIMER
        if not self.on_move:
            self.state = EntityState.HAVE_TO_ATTACK

    def can_attack(self) -> bool:
        """
        Return whether the entity can attack or not
        """
        # Check if no alteration forbids the entity to attack
        for alt in self.alterations:
            if "no_attack" in alt.specificities:
                return False
        return True

    def act(
        self, possible_moves: dict[Position, int], targets: dict[Entity, int]
    ) -> Optional[Position]:
        """
        Determine what action should be done by the entity controlled by AI.
        The action is determined according to the current state of the entity.

        Return the selected tile for the move / attack if any should be selected.

        Keyword arguments:
        possible_moves -- the collection of tiles that could be reached by the entity
        with their associated distance from the entity
        targets -- the collection of entities that could be attacked with their associated distance from the entity
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

    def determine_attack(self, targets: Sequence[Entity]) -> Optional[Position]:
        """
        Determine which entity should be attacked by the entity controlled by AI.

        Return the position of the attacked entity if any.

        Keyword arguments:
        targets -- the sequence of entities that could be attacked
        """
        temporary_attack: Optional[Position] = None
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

    def determine_move(
        self, possible_moves: dict[Position, int], targets: dict[Entity, int]
    ) -> Position:
        """
        Determine which movement should be selected by the entity controlled by AI.
        Change the current target of the entity if needed.

        Return the selected tile for the move.

        Keyword arguments:
        possible_moves -- the collection of tiles that could be reached by the entity
        with their associated distance from the entity
        targets -- the collection of entities that could be attacked with their associated distance from the entity
        """
        self.target: Optional[Position] = None
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
            best_move = self.position
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

    def attack(self, entity: Entity) -> int:
        """
        Return the damage that should be dealt to the given entity during an attack.

        Keyword arguments:
        entity -- the target of the attack
        """
        return self.strength

    def new_turn(self) -> None:
        """
        Handle the beginning of a new turn for the entity
        """
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
