import random as rd
import pygame as pg
from lxml import etree

from src.Movable import Movable
from src.constants import *

ITEM_DESC_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 24)

class Character(Movable):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, attack_kind, classes, equipments, strategy, lvl,
                 race, gold, talk,
                 compl_sprite=None):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, strategy, lvl, compl_sprite)
        '''Possible states :
                - 0 : Have to act
                - 1 : On move
                - 2 : Have to attack
                - 3 : Turn finished
        '''

        self.equipments = equipments
        self.classes = classes
        self.race = race
        self.gold = gold
        self.dialog = talk
        self.attack_kind = attack_kind

    def talk(self, actor):
        entries = []
        for s in self.dialog:
            entry = [{'type': 'text', 'text': s, 'font': ITEM_DESC_FONT}]
            entries.append(entry)
        return entries

    def get_attack_kind(self):
        return self.attack_kind

    def set_move(self, pos):
        Movable.set_move(self, pos)
        self.state = 1

    def move(self):
        Movable.move(self)
        if not self.on_move:
            self.state = 2

    def end_turn(self):
        self.state = 3

    def display(self, screen):
        Movable.display(self, screen)
        for eq in self.equipments:
            eq.display(screen, self.pos, True)

    def lvl_up(self):
        Movable.lvl_up(self)
        self.stats_up()

    def attacked(self, ent, damages, kind):
        for eq in self.equipments:
            if kind == PHYSICAL:
                damages -= eq.get_def()
            elif kind == SPIRITUAL:
                damages -= eq.get_res()
        return Movable.attacked(self, ent, damages, kind)

    def attack(self, ent):
        damages = self.strength
        weapon = self.get_weapon()
        if weapon:
            damages += weapon.get_power()
            if weapon.used() == 0:
                self.remove_equipment(weapon)
        return damages

    def stats_up(self, nb_lvl=1):
        for i in range(nb_lvl):
            if self.classes[0] == 'warrior':
                self.hp_max += rd.randrange(1, 5)  # Gain between 0 and 4
                self.defense += rd.randrange(0, 3)  # Gain between 0 and 2
                self.res += rd.randrange(0, 2)  # Gain between 0 and 1
                self.strength += rd.randrange(0, 3)  # Gain between 0 and 2
            elif self.classes[0] == 'ranger':
                self.hp_max += rd.randrange(1, 5)  # Gain between 0 and 4
                self.defense += rd.randrange(0, 4)  # Gain between 0 and 3
                self.res += rd.randrange(0, 2)  # Gain between 0 and 1
                self.strength += rd.randrange(0, 2)  # Gain between 0 and 1
            else:
                print("Error : Invalid class")

    def get_weapon(self):
        for eq in self.equipments:
            if eq.body_part == 'right_hand':
                return eq
        return None

    def get_equipments(self):
        # Return a new list based on equipments to avoid content alteration
        return list(self.equipments)

    def get_equipment(self, index):
        if index not in range(len(self.equipments)):
            return False
        return self.equipments[index]

    def get_gold(self):
        return self.gold

    def has_equipment(self, eq):
        return eq in self.equipments

    def get_classes(self):
        return self.classes

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
        for equip in self.equipments:
            if eq.body_part == equip.body_part:
                return False
        self.equipments.append(eq)
        self.remove_item(eq)
        return True

    def unequip(self, eq):
        # If the item has been appended to the inventory
        if self.set_item(eq):
            self.remove_equipment(eq)
            return True
        return False

    def remove_equipment(self, eq):
        id = eq.get_id()
        for index, equip in enumerate(self.equipments):
            if equip.get_id() == id:
                return self.equipments.pop(index)

    def save(self):
        tree = Movable.save(self)

        # Save gold
        gold = etree.SubElement(tree, 'gold')
        gold.text = str(self.gold)

        return tree