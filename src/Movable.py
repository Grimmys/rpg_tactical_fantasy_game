import pygame as pg
from lxml import etree

from src.constants import *
from src.Destroyable import Destroyable
from src.Key import Key

TIMER = 60
NB_ITEMS_MAX = 8


class Movable(Destroyable):
    XP_NEXT_LVL_BASE = 15
    move_speed = ANIMATION_SPEED

    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, lvl=1, compl_sprite=None):
        Destroyable.__init__(self, name, pos, sprite, hp, defense, res)
        self.max_move = max_move
        self.on_move = []
        self.timer = TIMER
        self.strength = strength
        self.alterations = []
        self.lvl = lvl
        self.xp = 0
        self.xp_next_lvl = self.determine_xp_goal()
        self.state = 0
        self.items = []
        self.nb_items_max = NB_ITEMS_MAX
        if compl_sprite:
            compl = pg.transform.scale(pg.image.load(compl_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
            self.sprite.blit(compl, (0, 0))

    def get_strength(self):
        return self.strength

    def get_max_moves(self):
        alterations = self.get_alterations_effect('speed')
        max = self.max_move
        for alt in alterations:
            max += alt.get_power()
        return max

    def set_move(self, path):
        self.on_move = path

    def get_move(self):
        return self.on_move

    def get_alterations(self):
        return self.alterations

    def get_formatted_alterations(self):
        formatted_string = ""
        for alteration in self.alterations:
            formatted_string += alteration.get_formatted_name() + ", "
        if formatted_string == "":
            return "None"
        return formatted_string[:-2]

    def set_alteration(self, alteration):
        self.alterations.append(alteration)

    def get_alterations_effect(self, eff):
        return [alteration for alteration in self.alterations if alteration.get_effect() == eff]

    def get_lvl(self):
        return self.lvl

    def get_xp(self):
        return self.xp

    def earn_xp(self, xp):
        self.xp += xp
        if self.xp >= self.xp_next_lvl:
            self.lvl_up()

    def determine_xp_goal(self):
        return int(Movable.XP_NEXT_LVL_BASE * pow(1.5, self.lvl - 1))

    def get_next_lvl_xp(self):
        return self.xp_next_lvl

    def lvl_up(self):
        self.lvl += 1
        self.xp -= self.xp_next_lvl
        self.xp_next_lvl = self.determine_xp_goal()

    def get_item(self, index):
        if index not in range(len(self.items)):
            return False
        return self.items[index]

    def get_items(self):
        # Return a new list based on items to avoid content alteration
        return list(self.items)

    def has_free_space(self):
        return len(self.items) < NB_ITEMS_MAX

    def set_item(self, item):
        if not self.has_free_space:
            return False
        self.items.append(item)
        return True

    def set_items(self, items):
        self.items = items

    def remove_item(self, item):
        id = item.get_id()
        for index, it in enumerate(self.items):
            if it.get_id() == id:
                return self.items.pop(index)

    def remove_key(self):
        for index, it in enumerate(self.items):
            if isinstance(it, Key):
                return self.items.pop(index)

    def use_item(self, item):
        return item.use(self)

    def get_nb_items_max(self):
        return self.nb_items_max

    def move(self):
        self.timer -= Movable.move_speed
        if self.timer <= 0:
            self.pos = self.on_move.pop(0)
            self.timer = TIMER

    # Should return damage dealt
    def attack(self, ent):
        return self.strength

    def new_turn(self):
        self.state = 0
        # Verify if any alteration is finished
        for alteration in self.alterations:
            if alteration.increment():
                self.alterations.remove(alteration)

    def save(self):
        tree = Destroyable.save(self)

        # Save position
        pos = etree.SubElement(tree, 'position')
        x = etree.SubElement(pos, 'x')
        x.text = str(self.pos[0] // TILE_SIZE)
        y = etree.SubElement(pos, 'y')
        y.text = str(self.pos[1] // TILE_SIZE)

        # Save level
        level = etree.SubElement(tree, 'level')
        level.text = str(self.lvl)

        # Save exp
        exp = etree.SubElement(tree, 'exp')
        exp.text = str(self.xp)

        # Save stats
        hp_m = etree.SubElement(tree, 'hp')
        hp_m.text = str(self.hp_max)
        atk = etree.SubElement(tree, 'strength')
        atk.text = str(self.strength)
        defense = etree.SubElement(tree, 'def')
        defense.text = str(self.defense)
        res = etree.SubElement(tree, 'res')
        res.text = str(self.res)
        move = etree.SubElement(tree, 'move')
        move.text = str(self.max_move)

        return tree

