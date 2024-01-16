"""
Defines Character class, the class defining allied entities or even playable entities
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence
from typing import Optional, Union

import pygame
from pygamepopup.components import BoxElement, TextElement

from src.game_entities.alteration import Alteration
from src.game_entities.destroyable import DamageKind
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.item import Item
from src.game_entities.key import Key
from src.game_entities.movable import Movable
from src.game_entities.shield import Shield
from src.game_entities.skill import Skill
from src.game_entities.weapon import Weapon
from src.gui.fonts import fonts
from src.gui.position import Position
from src.services.language import *


class Character(Movable):
    """
    A Character is a living entity that can be controlled by the player (but that could also be controlled by the AI
    and then be an ally).
    Each Character has specificities like classes or race, and can equip items.

    Keyword Arguments:
    name -- the name of the entity
    position -- the current position of the entity on screen
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen or
    the relative path to the visual representation of the entity
    hit_points -- the total of damage that the entity can take before disappearing
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks
    strength -- the raw strength of the entity
    classes -- the sequence of classes of the character
    equipments -- the list of equipment worn by the character
    strategy -- the strategy of the entity if it's controlled by the AI
    lvl -- the current level of the entity
    skills -- the list of skills of the entity
    alterations -- the list of ongoing alterations affecting the entity
    race -- the character's race
    gold -- the amount of gold the character has
    interaction -- the event that should be triggered when the player try to interact with the entity
    complementary_sprite_link -- the relative path to the sprite that should be blitted on top of the base sprite

    Attributes:
    equipments -- the list of equipment worn by the character
    classes -- the sequence of classes of the character
    race -- the character's race
    gold -- the amount of gold the character has
    interaction -- the event that should be triggered when the player try to interact with the entity
    join_team -- whether the character can join the team or not
    reach_ -- the range of reach of the entity
    constitution -- the global constitution of the character used to know its capacity to bear items
    """

    races_data: dict[str, dict[str, any]] = {}
    classes_data: dict[str, dict[str, any]] = {}

    @staticmethod
    def init_data(
        races: dict[str, dict[str, any]], classes: dict[str, dict[str, any]]
    ) -> None:
        """
        Initialize the generic data collections for Character.
        This method should be called only once and before any use of this class.

        Keyword arguments:
        races -- the data structure containing all the data about existing races
        classes -- the data structure containing all the data about existing classes
        """
        Character.races_data = races
        Character.classes_data = classes

    def __init__(
        self,
        name: str,
        position: Position,
        sprite: Union[str, pygame.Surface],
        hit_points: int,
        defense: int,
        resistance: int,
        strength: int,
        classes: Sequence[str],
        equipments: list[Equipment],
        strategy: str,
        lvl: int,
        skills: Sequence[Skill],
        alterations: list[Alteration],
        race: str,
        gold: int,
        interaction: dict[str, any],
        complementary_sprite_link: Optional[str] = None,
    ):
        super().__init__(
            name,
            position,
            sprite,
            hit_points,
            defense,
            resistance,
            Character.races_data[race]["move"]
            + Character.classes_data[classes[0]]["move"],
            strength,
            "PHYSICAL",
            strategy,
            lvl,
            skills,
            alterations,
            complementary_sprite_link,
        )
        self.equipments: list[Equipment] = equipments
        self.classes: Sequence[str] = classes
        self.race: str = race
        self.gold: int = gold
        self.interaction: dict[str, any] = interaction
        self.join_team: bool = False
        self.reach_: Sequence[int] = [1]
        self.constitution: int = (
            Character.races_data[race]["constitution"]
            + Character.classes_data[classes[0]]["constitution"]
        )

    def talk(self, actor: Entity) -> list[list[BoxElement]]:
        """
        Compute the dialog that should be displayed to the player when trying to interact with the entity.

        Return the computed dialog.

        Keyword arguments:
        actor -- the player character which initiated the interaction
        """
        self.join_team = self.interaction["join_team"]
        element_grid: list[list[BoxElement]] = []
        for line in self.interaction["dialog"]:
            elements_line: list[BoxElement] = [
                TextElement(line, font=fonts["ITEM_DESC_FONT"])
            ]
            element_grid.append(elements_line)
        return element_grid

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the character on the given screen.
        Also display on top of it its equipment.

        Keyword arguments:
        screen -- the screen on which the movable entity should be drawn
        """
        Movable.display(self, screen)
        for equipment in self.equipments:
            equipment.display(screen, self.position, True)

    def lvl_up(self) -> None:
        """
        Handle the up of the level by one.
        Increase the statistics.
        """
        Movable.lvl_up(self)
        self.stats_up()

    # TODO : refactor part of this code in Shield class
    def parried(self) -> bool:
        """
        Compute and return whether the character parried the ongoing attack or not.
        """
        for equipment in self.equipments:
            if isinstance(equipment, Shield):
                parried: bool = random.randint(1, 100) <= equipment.parry
                if parried:
                    if equipment.used() <= 0:
                        self.remove_equipment(equipment)
                return parried
        return False

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
        for equipment in self.equipments:
            if kind is DamageKind.PHYSICAL:
                damage -= equipment.defense
            elif kind == DamageKind.SPIRITUAL:
                damage -= equipment.resistance
        return Movable.attacked(self, entity, damage, kind, allies)

    def attack(self, entity: Entity) -> int:
        """
        Return the damage that should be dealt to the given entity during an attack.

        Keyword arguments:
        entity -- the target of the attack
        """
        damage: int = self.strength + self.get_stat_change("strength")
        weapon = self.get_weapon()
        if weapon:
            damage += weapon.hit(self, entity)
            if weapon.used() == 0:
                self.remove_equipment(weapon)
        return damage

    def stats_up(self, nb_lvl: int = 1) -> None:
        """
        Compute the increasing of each statistics for each level up.

        Keyword arguments:
        nb_lvl -- the number of levels earned
        """
        for _ in range(nb_lvl):
            hp_increased: int = random.choice(
                self.classes_data[self.classes[0]]["stats_up"]["hp"]
            )
            self.defense += random.choice(
                self.classes_data[self.classes[0]]["stats_up"]["def"]
            )
            self.resistance += random.choice(
                self.classes_data[self.classes[0]]["stats_up"]["res"]
            )
            self.strength += random.choice(
                self.classes_data[self.classes[0]]["stats_up"]["str"]
            )
            self.hit_points_max += hp_increased
            self.hit_points += hp_increased

    def get_weapon(self) -> Optional[Weapon]:
        """
        Return the weapon born by the character.
        """
        for equipment in self.equipments:
            if equipment.body_part == "right_hand":
                return equipment
        return None

    @property
    def reach(self) -> Sequence[int]:
        """
        Return the range of reach of the character.
        """
        reach: Sequence[int] = self.reach_
        weapon: Weapon = self.get_weapon()
        if weapon is not None:
            reach = weapon.reach
        return reach

    @property
    def attack_kind(self) -> DamageKind:
        """
        Return the kind of damage dealt by the character.
        """
        attack_kind: DamageKind = self._attack_kind
        weapon = self.get_weapon()
        if weapon is not None:
            attack_kind = weapon.attack_kind
        return attack_kind

    def get_equipment(self, index: int) -> Union[Equipment, bool]:
        """
        Return the equipment located at the given index.
        Return False if there is no equipment at this index.

        Keyword argument:
        index -- the index to look for
        """
        if index not in range(len(self.equipments)):
            return False
        return self.equipments[index]

    def has_exact_equipment(self, equipment: Equipment) -> bool:
        """
        Return whether the character wears the given exact instance of the equipment or not

        Keyword argument:
        equipment -- the equipment to look for
        """
        return equipment.identifier in map(lambda eq: eq.identifier, self.equipments)

    def get_formatted_classes(self) -> str:
        """
        Return the list of classes in a formatted
        way
        """
        formatted_string: str = ""
        for cls in self.classes:
            try:
                formatted_string += TRANSLATIONS["races_and_classes"][cls] + ", "
            except KeyError:
                formatted_string += cls.capitalize() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_formatted_race(self) -> str:
        """
        Return the race in a formatted
        way
        """
        try:
            return TRANSLATIONS["races_and_classes"][self.race]
        except KeyError:
            return self.race.capitalize()

    def get_formatted_reach(self) -> str:
        """
        Return the reach in a formatted
        way
        """
        return ", ".join([str(reach) for reach in self.reach])

    # TODO : Refactor me ; I'm too long and return type looks too generic
    def equip(self, equipment: Equipment) -> int:
        """
        Handle the equipment of the given equipment.
        Return whether the equipment has been successfully equipped or not, and if it replaced another equipment.

        Keyword argument:
        equipment -- the equipment to be equipped
        """
        # Verify if player could wear this equipment
        allowed: bool = True
        if self.race == "centaur" and not isinstance(equipment, (Shield, Weapon)):
            allowed = False
        if equipment.restrictions != {}:
            allowed = False
            if "classes" in equipment.restrictions and (
                self.race != "centaur" or isinstance(equipment, (Shield, Weapon))
            ):
                for cls in equipment.restrictions["classes"]:
                    if cls in self.classes:
                        allowed = True
                        break
            if "races" in equipment.restrictions:
                for race in equipment.restrictions["races"]:
                    if race == self.race:
                        allowed = True
                        break

        if allowed:
            self.remove_item(equipment)
            # Value to know if there was an equipped item at the slot taken by eq
            replacement: int = 0
            for equip in self.equipments:
                if equipment.body_part == equip.body_part:
                    self.remove_equipment(equip)
                    self.set_item(equip)
                    replacement = 1
            self.equipments.append(equipment)
            return replacement
        return -1

    def unequip(self, equipment: Equipment) -> bool:
        """
        Handle the unequipment of the given equipment.
        Return whether the equipment has been successfully unequipped or not.

        Keyword argument:
        equipment -- the equipment to be unequipped
        """
        # If the item has been appended to the inventory
        if self.set_item(equipment):
            self.remove_equipment(equipment)
            return True
        return False

    def remove_equipment(self, equipment: Equipment) -> Optional[Equipment]:
        """
        Remove the given equipment from the list of equipments of the character and return it.
        """
        for index, equip in enumerate(self.equipments):
            if equip.identifier == equipment.identifier:
                return self.equipments.pop(index)
        return None

    def get_stat_change(self, stat: str) -> int:
        """
        Return the current modifier for the given statistic.

        Keyword argument:
        stat -- the name of the state for which the modifier should be returned
        """
        malus: int = 0
        if stat == "speed":
            # Check if character as a malus due to equipment weight exceeding constitution
            total_weight: int = sum([equipment.weight for equipment in self.equipments])
            difference: int = total_weight - self.constitution
            malus: int = 0 if difference < 0 else -math.ceil(difference / 2)
        return malus + Movable.get_stat_change(self, stat)

    def remove_chest_key(self) -> None:
        """
        Remove the first chest key found in the inventory if there is any
        """
        best_candidate: Optional[Item] = None
        for item in self.items:
            if isinstance(item, Key) and item.for_chest:
                if not best_candidate:
                    best_candidate = item
                elif not item.for_door:
                    # If a key could be used to open a chest but not a door, it's better to use it
                    best_candidate = item
        self.items.remove(best_candidate)

    def remove_door_key(self) -> None:
        """
        Remove the first door key found in the inventory if there is any
        """
        best_candidate: Union[Item, None] = None
        for item in self.items:
            if isinstance(item, Key) and item.for_door:
                if not best_candidate:
                    best_candidate = item
                elif not item.for_chest:
                    # If a key could be used to open a door but not a chest, it's better to use it
                    best_candidate = item
        self.items.remove(best_candidate)

    def save(self, tree_name: etree.Element) -> etree.Element:
        """
        Save the current state of the character in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save class (if possible)
        if len(self.classes) > 0:
            class_el: etree.Element = etree.SubElement(tree, "class")
            class_el.text = self.classes[
                0
            ]  # Currently, only first class is saved if any

        # Save race
        race: etree.Element = etree.SubElement(tree, "race")
        race.text = self.race

        # Save gold
        gold: etree.Element = etree.SubElement(tree, "gold")
        gold.text = str(self.gold)

        # Save inventory
        inventory: etree.Element = etree.SubElement(tree, "inventory")
        for item in self.items:
            inventory.append(item.save("item"))

        # Save equipment
        equipments: etree.Element = etree.SubElement(tree, "equipment")
        for equipment in self.equipments:
            equipments.append(equipment.save(equipment.body_part))

        return tree
