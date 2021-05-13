import math
import random

from lxml import etree

from src.game_entities.key import Key
from src.game_entities.shield import Shield
from src.game_entities.movable import Movable
from src.game_entities.destroyable import DamageKind
from src.game_entities.weapon import Weapon
from src.gui.fonts import fonts


class Character(Movable):
    races_data = {}
    classes_data = {}

    @staticmethod
    def init_data(races, classes):
        Character.races_data = races
        Character.classes_data = classes

    def __init__(self, name, pos, sprite, hp, defense, res, strength, classes, equipments,
                 strategy, lvl, skills, alterations, race, gold, interaction, compl_sprite=None):
        Movable.__init__(self, name, pos, sprite, hp, defense, res,
                         Character.races_data[race]['move'] +
                         Character.classes_data[classes[0]]['move'],
                         strength, 'PHYSICAL', strategy, lvl, skills, alterations, compl_sprite)
        self.equipments = equipments
        self.classes = classes
        self.race = race
        self.gold = gold
        self.interaction = interaction
        self.join_team = False
        self.reach_ = [1]
        self.constitution = Character.races_data[race]['constitution'] + \
                            Character.classes_data[classes[0]]['constitution']

    def talk(self, actor):
        self.join_team = self.interaction['join_team']
        entries = []
        for line in self.interaction['dialog']:
            entry = [{'type': 'text', 'text': line, 'font': fonts['ITEM_DESC_FONT']}]
            entries.append(entry)
        return entries

    def display(self, screen):
        Movable.display(self, screen)
        for equipment in self.equipments:
            equipment.display(screen, self.position, True)

    def lvl_up(self):
        Movable.lvl_up(self)
        self.stats_up()

    # TODO : refactor part of this code in Shield class
    def parried(self):
        for equipment in self.equipments:
            if isinstance(equipment, Shield):
                parried = random.randint(0, 100) < equipment.parry
                if parried:
                    if equipment.used() <= 0:
                        self.remove_equipment(equipment)
                return parried
        return False

    def attacked(self, ent, damage, kind, allies):
        for equipment in self.equipments:
            if kind is DamageKind.PHYSICAL:
                damage -= equipment.defense
            elif kind == DamageKind.SPIRITUAL:
                damage -= equipment.res
        return Movable.attacked(self, ent, damage, kind, allies)

    def attack(self, ent):
        damages = self.strength + self.get_stat_change('strength')
        weapon = self.get_weapon()
        if weapon:
            damages += weapon.hit(self, ent)
            if weapon.used() == 0:
                self.remove_equipment(weapon)
        return damages

    def stats_up(self, nb_lvl=1):
        for _ in range(nb_lvl):
            hp_increased = random.choice(self.classes_data[self.classes[0]]['stats_up']['hp'])
            self.defense += random.choice(self.classes_data[self.classes[0]]['stats_up']['def'])
            self.res += random.choice(self.classes_data[self.classes[0]]['stats_up']['res'])
            self.strength += random.choice(self.classes_data[self.classes[0]]['stats_up']['str'])
            self.hp_max += hp_increased
            self.hit_points += hp_increased

    def get_weapon(self):
        for equipment in self.equipments:
            if equipment.body_part == 'right_hand':
                return equipment
        return None

    @property
    def reach(self):
        reach = self.reach_
        weapon = self.get_weapon()
        if weapon is not None:
            reach = weapon.reach
        return reach

    @property
    def attack_kind(self):
        attack_kind = self._attack_kind
        weapon = self.get_weapon()
        if weapon is not None:
            attack_kind = weapon.attack_kind
        return attack_kind

    def get_equipment(self, index):
        if index not in range(len(self.equipments)):
            return False
        return self.equipments[index]

    def has_equipment(self, equipment):
        return equipment in self.equipments

    def get_formatted_classes(self):
        formatted_string = ""
        for cls in self.classes:
            formatted_string += cls.capitalize() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_formatted_race(self):
        return self.race.capitalize()

    def get_formatted_reach(self):
        return ', '.join([str(reach) for reach in self.reach])

    def equip(self, equipment):
        # Verify if player could wear this equipment
        allowed = True
        if self.race == 'centaur' and not isinstance(equipment, (Shield, Weapon)):
            allowed = False
        if equipment.restrictions != {}:
            allowed = False
            if 'classes' in equipment.restrictions and \
                    (self.race != 'centaur' or isinstance(equipment, (Shield, Weapon))):
                for cls in equipment.restrictions['classes']:
                    if cls in self.classes:
                        allowed = True
                        break
            if 'races' in equipment.restrictions:
                for race in equipment.restrictions['races']:
                    if race == self.race:
                        allowed = True
                        break

        if allowed:
            self.remove_item(equipment)
            # Value to know if there was an equipped item at the slot taken by eq
            replacement = 0
            for equip in self.equipments:
                if equipment.body_part == equip.body_part:
                    self.remove_equipment(equip)
                    self.set_item(equip)
                    replacement = 1
            self.equipments.append(equipment)
            return replacement
        return -1

    def unequip(self, equipment):
        # If the item has been appended to the inventory
        if self.set_item(equipment):
            self.remove_equipment(equipment)
            return True
        return False

    def remove_equipment(self, equipment):
        for index, equip in enumerate(self.equipments):
            if equip.identifier == equipment.identifier:
                return self.equipments.pop(index)

    def get_stat_change(self, stat):
        malus = 0
        if stat == 'speed':
            # Check if character as a malus due to equipment weight exceeding constitution
            total_weight = sum([equipment.weight for equipment in self.equipments])
            diff = total_weight - self.constitution
            malus = 0 if diff < 0 else - math.ceil(diff / 2)
        return malus + Movable.get_stat_change(self, stat)

    def remove_chest_key(self):
        best_candidate = None
        for item in self.items:
            if isinstance(item, Key) and item.for_chest:
                if not best_candidate:
                    best_candidate = item
                elif not item.for_door:
                    # If a key could be used to open a chest but not a door, it's better to use it
                    best_candidate = item
        self.items.remove(best_candidate)

    def remove_door_key(self):
        best_candidate = None
        for item in self.items:
            if isinstance(item, Key) and item.for_door:
                if not best_candidate:
                    best_candidate = item
                elif not item.for_chest:
                    # If a key could be used to open a door but not a chest, it's better to use it
                    best_candidate = item
        self.items.remove(best_candidate)

    def save(self, tree_name):
        tree = Movable.save(self, tree_name)

        # Save class (if possible)
        if len(self.classes) > 0:
            class_el = etree.SubElement(tree, 'class')
            class_el.text = self.classes[0]  # Currently, only first class is saved if any

        # Save race
        race = etree.SubElement(tree, 'race')
        race.text = self.race

        # Save gold
        gold = etree.SubElement(tree, 'gold')
        gold.text = str(self.gold)

        # Save inventory
        inventory = etree.SubElement(tree, 'inventory')
        for item in self.items:
            inventory.append(item.save('item'))

        # Save equipment
        equipments = etree.SubElement(tree, 'equipment')
        for equipment in self.equipments:
            equipments.append(equipment.save(equipment.body_part))

        return tree
