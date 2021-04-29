import math

from lxml import etree
import random as rd

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
                         Character.races_data[race]['move'] + Character.classes_data[classes[0]]['move'],
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
        for s in self.interaction['dialog']:
            entry = [{'type': 'text', 'text': s, 'font': fonts['ITEM_DESC_FONT']}]
            entries.append(entry)
        return entries

    def display(self, screen):
        Movable.display(self, screen)
        for eq in self.equipments:
            eq.display(screen, self.pos, True)

    def lvl_up(self):
        Movable.lvl_up(self)
        self.stats_up()

    # TODO : refactor part of this code in Shield class
    def parried(self):
        for eq in self.equipments:
            if isinstance(eq, Shield):
                parried = rd.randint(0, 100) < eq.parry
                if parried:
                    if eq.used() <= 0:
                        self.remove_equipment(eq)
                return parried
        return False

    def attacked(self, ent, damage, kind, allies):
        for eq in self.equipments:
            if kind is DamageKind.PHYSICAL:
                damage -= eq.defense
            elif kind == DamageKind.SPIRITUAL:
                damage -= eq.res
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
        for i in range(nb_lvl):
            hp_increased = rd.choice(Character.classes_data[self.classes[0]]['stats_up']['hp'])
            self.defense += rd.choice(Character.classes_data[self.classes[0]]['stats_up']['def'])
            self.res += rd.choice(Character.classes_data[self.classes[0]]['stats_up']['res'])
            self.strength += rd.choice(Character.classes_data[self.classes[0]]['stats_up']['str'])
            self.hp_max += hp_increased
            self.hp += hp_increased

    def get_weapon(self):
        for eq in self.equipments:
            if eq.body_part == 'right_hand':
                return eq
        return None

    @property
    def reach(self):
        reach = self.reach_
        w = self.get_weapon()
        if w is not None:
            reach = w.reach
        return reach

    @property
    def attack_kind(self):
        attack_kind = self._attack_kind
        w = self.get_weapon()
        if w is not None:
            attack_kind = w.attack_kind
        return attack_kind

    def get_equipment(self, index):
        if index not in range(len(self.equipments)):
            return False
        return self.equipments[index]

    def has_equipment(self, eq):
        return eq in self.equipments

    def get_formatted_classes(self):
        formatted_string = ""
        for cl in self.classes:
            formatted_string += cl.capitalize() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def get_formatted_race(self):
        return self.race.capitalize()

    def get_formatted_reach(self):
        return ', '.join([str(reach) for reach in self.reach])

    def equip(self, eq):
        # Verify if player could wear this equipment
        allowed = True
        if self.race == 'centaur' and not (isinstance(eq, Weapon) or isinstance(eq, Shield)):
            allowed = False
        if eq.restrictions != {}:
            allowed = False
            if 'classes' in eq.restrictions and (self.race != 'centaur' or isinstance(eq, Weapon) or isinstance(eq, Shield)):
                for cl in eq.restrictions['classes']:
                    if cl in self.classes:
                        allowed = True
                        break
            if 'races' in eq.restrictions:
                for race in eq.restrictions['races']:
                    if race == self.race:
                        allowed = True
                        break

        if allowed:
            self.remove_item(eq)
            # Value to know if there was an equipped item at the slot taken by eq
            replacement = 0
            for equip in self.equipments:
                if eq.body_part == equip.body_part:
                    self.remove_equipment(equip)
                    self.set_item(equip)
                    replacement = 1
            self.equipments.append(eq)
            return replacement
        return -1

    def unequip(self, eq):
        # If the item has been appended to the inventory
        if self.set_item(eq):
            self.remove_equipment(eq)
            return True
        return False

    def remove_equipment(self, eq):
        for index, equip in enumerate(self.equipments):
            if equip.id == eq.id:
                return self.equipments.pop(index)

    def get_stat_change(self, stat):
        malus = 0
        if stat == 'speed':
            # Check if character as a malus to his movement due to equipment total weight exceeding constitution
            total_weight = sum([eq.weight for eq in self.equipments])
            diff = total_weight - self.constitution
            malus = 0 if diff < 0 else - math.ceil(diff / 2)
        return malus + Movable.get_stat_change(self, stat)

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
