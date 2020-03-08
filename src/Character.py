from src.Movable import Movable

import random as rd


class Character(Movable):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, classes, equipments, strategy, lvl, race, gold,
                 compl_sprite=None):
        Movable.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, strategy, lvl, compl_sprite)
        self.equipments = equipments
        self.classes = classes
        self.race = race
        self.gold = gold

    def display(self, screen):
        Movable.display(self, screen)
        for eq in self.equipments:
            eq.display(screen, self.pos, True)

    def lvl_up(self):
        Movable.lvl_up(self)
        self.stats_up()

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
                self.hp_max += rd.randrange(0, 5)  # Gain between 0 and 4
                self.defense += rd.randrange(0, 3)  # Gain between 0 and 2
                self.res += rd.randrange(0, 2)  # Gain between 0 and 1
                self.strength += rd.randrange(0, 3)  # Gain between 0 and 2
            elif self.classes[0] == 'ranger':
                self.hp_max += rd.randrange(0, 5)  # Gain between 0 and 4
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
