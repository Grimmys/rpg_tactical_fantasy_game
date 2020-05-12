from lxml import etree
import random as rd

from src.Shield import Shield
from src.Movable import Movable
from src.Destroyable import DamageKind
from src.Weapon import Weapon
from src.fonts import fonts


class Character(Movable):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, classes, equipments,
                 strategy, lvl, race, gold, talk, compl_sprite=None):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, strategy,
                         lvl, compl_sprite)
        self.equipments = equipments
        self.classes = classes
        self.race = race
        self.gold = gold
        self.dialog = talk

    def talk(self, actor):
        entries = []
        for s in self.dialog:
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

    def parried(self):
        for eq in self.equipments:
            if isinstance(eq, Shield):
                parried = rd.randint(0, 100) < eq.parry
                if parried:
                    if eq.used() <= 0:
                        self.remove_equipment(eq)
                return parried
        return False

    def attacked(self, ent, damages, kind):
        for eq in self.equipments:
            if kind is DamageKind.PHYSICAL:
                damages -= eq.defense
            elif kind == DamageKind.SPIRITUAL:
                damages -= eq.res
        return Movable.attacked(self, ent, damages, kind)

    def attack(self, ent):
        damages = self.strength
        weapon = self.get_weapon()
        if weapon:
            damages += weapon.atk
            if weapon.used() == 0:
                self.remove_equipment(weapon)
        return damages

    def stats_up(self, nb_lvl=1):
        for i in range(nb_lvl):
            if self.classes[0] == 'warrior':
                self.hp_max += rd.randint(1, 4)  # Gain between 1 and 4
                self.defense += rd.randint(0, 2)  # Gain between 0 and 2
                self.res += rd.randint(0, 1)  # Gain between 0 and 1
                self.strength += rd.randint(0, 2)  # Gain between 0 and 2
            elif self.classes[0] == 'ranger':
                self.hp_max += rd.randint(1, 4)  # Gain between 1 and 4
                self.defense += rd.randint(0, 3)  # Gain between 0 and 3
                self.res += rd.randint(0, 1)  # Gain between 0 and 1
                self.strength += rd.randint(0, 1)  # Gain between 0 and 1
            else:
                print("Error : Invalid class")

    def get_weapon(self):
        for eq in self.equipments:
            if eq.body_part == 'right_hand':
                return eq
        return None

    def get_reach(self):
        reach = Movable.get_reach(self)
        w = self.get_weapon()
        if w is not None:
            reach = w.reach
        return reach

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

    def equip(self, eq):
        # Verify if player could wear this equipment
        allowed = True
        if self.race == 'centaur' and not(isinstance(eq, Weapon) or isinstance(eq, Shield)):
            allowed = False
        if eq.restrictions != {}:
            allowed = False
            if 'classes' in eq.restrictions and self.race != 'centaur':
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

        return tree
