"""
Defines Character class, the class defining allied entities or even playable entities
"""

import math
import random
from typing import Union, Sequence, Any, Optional

import pygame
from lxml import etree

from src.game_entities.alteration import Alteration
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.item import Item
from src.game_entities.key import Key
from src.game_entities.shield import Shield
from src.game_entities.movable import Movable
from src.game_entities.destroyable import DamageKind
from src.game_entities.skill import Skill
from src.game_entities.weapon import Weapon
from src.gui.entries import Entries, Entry
from src.gui.fonts import fonts


class Character(Movable):
    """ """

    races_data: dict[str, dict[str, Any]] = {}
    classes_data: dict[str, dict[str, Any]] = {}

    @staticmethod
    def init_data(
        races: dict[str, dict[str, Any]], classes: dict[str, dict[str, Any]]
    ) -> None:
        """

        :param races:
        :param classes:
        """
        Character.races_data = races
        Character.classes_data = classes

    def __init__(
        self,
        name: str,
        position: tuple[int, int],
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
        interaction: dict[str, Any],
        complementary_sprite_link: str = None,
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
        self.interaction: dict[str, Any] = interaction
        self.join_team: bool = False
        self.reach_: Sequence[int] = [1]
        self.constitution: int = (
            Character.races_data[race]["constitution"]
            + Character.classes_data[classes[0]]["constitution"]
        )

    def talk(self, actor: Entity) -> Entries:
        """

        :param actor:
        :return:
        """
        self.join_team = self.interaction["join_team"]
        entries: Entries = []
        for line in self.interaction["dialog"]:
            entry_line: list[Entry] = [
                {"type": "text", "text": line, "font": fonts["ITEM_DESC_FONT"]}
            ]
            entries.append(entry_line)
        return entries

    def display(self, screen: pygame.Surface) -> None:
        """

        :param screen:
        """
        Movable.display(self, screen)
        for equipment in self.equipments:
            equipment.display(screen, self.position, True)

    def lvl_up(self) -> None:
        """ """
        Movable.lvl_up(self)
        self.stats_up()

    # TODO : refactor part of this code in Shield class
    def parried(self) -> bool:
        """

        :return:
        """
        for equipment in self.equipments:
            if isinstance(equipment, Shield):
                parried: bool = random.randint(0, 100) < equipment.parry
                if parried:
                    if equipment.used() <= 0:
                        self.remove_equipment(equipment)
                return parried
        return False

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
        for equipment in self.equipments:
            if kind is DamageKind.PHYSICAL:
                damage -= equipment.defense
            elif kind == DamageKind.SPIRITUAL:
                damage -= equipment.resistance
        return Movable.attacked(self, entity, damage, kind, allies)

    def attack(self, entity: Entity) -> int:
        """

        :param entity:
        :return:
        """
        damages: int = self.strength + self.get_stat_change("strength")
        weapon = self.get_weapon()
        if weapon:
            damages += weapon.hit(self, entity)
            if weapon.used() == 0:
                self.remove_equipment(weapon)
        return damages

    def stats_up(self, nb_lvl: int = 1) -> None:
        """

        :param nb_lvl:
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

        :return:
        """
        for equipment in self.equipments:
            if equipment.body_part == "right_hand":
                return equipment
        return None

    @property
    def reach(self) -> Sequence[int]:
        """

        :return:
        """
        reach: Sequence[int] = self.reach_
        weapon: Weapon = self.get_weapon()
        if weapon is not None:
            reach = weapon.reach
        return reach

    @property
    def attack_kind(self) -> DamageKind:
        """

        :return:
        """
        attack_kind: DamageKind = self._attack_kind
        weapon = self.get_weapon()
        if weapon is not None:
            attack_kind = weapon.attack_kind
        return attack_kind

    def get_equipment(self, index: int) -> Union[Equipment, bool]:
        """

        :param index:
        :return:
        """
        if index not in range(len(self.equipments)):
            return False
        return self.equipments[index]

    def has_equipment(self, equipment: Equipment) -> bool:
        """

        :param equipment:
        :return:
        """
        return equipment in self.equipments

    def get_formatted_classes(self) -> str:
        """

        :return:
        """
        formatted_string: str = ""
        for cls in self.classes:
            formatted_string += cls.capitalize() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_formatted_race(self) -> str:
        """

        :return:
        """
        return self.race.capitalize()

    def get_formatted_reach(self) -> str:
        """

        :return:
        """
        return ", ".join([str(reach) for reach in self.reach])

    # TODO : Refactor me ; I'm too long and return type looks too generic
    def equip(self, equipment: Equipment) -> int:
        """

        :param equipment:
        :return:
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

        :param equipment:
        :return:
        """
        # If the item has been appended to the inventory
        if self.set_item(equipment):
            self.remove_equipment(equipment)
            return True
        return False

    def remove_equipment(self, equipment: Equipment) -> Union[Equipment, None]:
        """

        :param equipment:
        :return:
        """
        for index, equip in enumerate(self.equipments):
            if equip.identifier == equipment.identifier:
                return self.equipments.pop(index)
        return None

    def get_stat_change(self, stat: str) -> int:
        """

        :param stat:
        :return:
        """
        malus: int = 0
        if stat == "speed":
            # Check if character as a malus due to equipment weight exceeding constitution
            total_weight: int = sum([equipment.weight for equipment in self.equipments])
            difference: int = total_weight - self.constitution
            malus: int = 0 if difference < 0 else -math.ceil(difference / 2)
        return malus + Movable.get_stat_change(self, stat)

    def remove_chest_key(self) -> None:
        """ """
        best_candidate: Union[Item, None] = None
        for item in self.items:
            if isinstance(item, Key) and item.for_chest:
                if not best_candidate:
                    best_candidate = item
                elif not item.for_door:
                    # If a key could be used to open a chest but not a door, it's better to use it
                    best_candidate = item
        self.items.remove(best_candidate)

    def remove_door_key(self) -> None:
        """ """
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
