import pygame as pg
from lxml import etree

from src.Character import Character
from src.constants import  *

SELECTED_SPRITE = 'imgs/dungeon_crawl/misc/cursor.png'
SELECTED_DISPLAY = pg.transform.scale(pg.image.load(SELECTED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))


class Player(Character):
    def __init__(self, name, sprite, hp, defense, res, max_move, strength, classes, equipments, race, gold, lvl=1,
                 compl_sprite=None):
        Character.__init__(self, name, (), sprite, hp, defense, res, max_move, strength, classes, equipments, None, lvl, race,
                           gold, compl_sprite)
        '''Possible states :
        - 0 : Waiting to be selected
        - 1 : Waiting to be moved
        - 2 : On move
        - 3 : Waiting an action post-move
        - 4 : Waiting a target selected to attack OR waiting an target to interact with
        - 5 : Turn finished'''
        self.old_pos = ()
        self.state = 0
        self.last_state = 5
        self.selected = False

        # Sprite displayed when player cannot be selected
        self.sprite_unavaible = self.sprite.copy()
        color_image = pg.Surface(self.sprite.get_size()).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavaible.blit(color_image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

        # Memorize normal state sprite
        self.normal_sprite = self.sprite

    def set_initial_pos(self, pos):
        self.pos = pos
        self.old_pos = pos

    def display(self, screen):
        Character.display(self, screen)
        if self.state in range(1, 4):
            screen.blit(SELECTED_DISPLAY, self.pos)

    def set_selected(self, is_selected):
        self.selected = is_selected
        self.state = 1 if is_selected else 0

    def get_state(self):
        return self.state

    def set_move(self, pos):
        Character.set_move(self, pos)
        self.old_pos = self.pos
        self.state = 2

    def move(self):
        Character.move(self)
        if not self.on_move:
            self.state = 3

    def cancel_move(self):
        self.state = 0
        self.pos = self.old_pos

    def cancel_interaction(self):
        self.state = 3

    def attack(self, ent):
        damages = Character.attack(self, ent)
        self.state = self.last_state
        return damages

    def turn_finished(self):
        self.state = self.last_state
        self.selected = False
        self.sprite = self.sprite_unavaible
        for eq in self.equipments:
            eq.set_grey()

    def new_turn(self):
        Character.new_turn(self)
        self.sprite = self.normal_sprite
        for eq in self.equipments:
            eq.unset_grey()

    def turn_is_finished(self):
        return self.state == self.last_state

    def choose_target(self):
        self.state = 4

    def choose_interaction(self):
        self.state = 4

    def save(self):
        # Build XML tree
        tree = etree.Element('player')

        # Save name
        name = etree.SubElement(tree, 'name')
        name.text = self.name

        # Save level
        level = etree.SubElement(tree, 'level')
        level.text = str(self.lvl)

        # Save class
        class_el = etree.SubElement(tree, 'class')
        class_el.text = self.classes[0]  # Currently, only first class is saved

        # Save race
        race = etree.SubElement(tree, 'race')
        race.text = self.race

        # Save exp
        exp = etree.SubElement(tree, 'exp')
        exp.text = str(self.xp)

        # Save stats
        hp_m = etree.SubElement(tree, 'hp')
        hp_m.text = str(self.hp_max)
        atk = etree.SubElement(tree, 'strength')
        atk.text = str(self.strength)
        defense = etree.SubElement(tree, 'defense')
        defense.text = str(self.defense)
        res = etree.SubElement(tree, 'res')
        res.text = str(self.res)
        move = etree.SubElement(tree, 'move')
        move.text = str(self.max_move)

        # Save current hp
        hp = etree.SubElement(tree, 'currentHp')
        hp.text = str(self.hp)

        # Save position
        pos = etree.SubElement(tree, 'position')
        x = etree.SubElement(pos, 'x')
        x.text = str(self.pos[0])
        y = etree.SubElement(pos, 'y')
        y.text = str(self.pos[1])

        # Save gold
        gold = etree.SubElement(tree, 'gold')
        gold.text = str(self.gold)

        # Save if turn is finished or not
        state = etree.SubElement(tree, 'turnFinished')
        state.text = str(self.turn_is_finished())

        # Save inventory
        inv = etree.SubElement(tree, 'inventory')
        for it in self.items:
            it_el = etree.SubElement(inv, 'item')
            it_name = etree.SubElement(it_el, 'name')
            it_name.text = it.get_name()

        # Save equipment
        equip = etree.SubElement(tree, 'equipments')
        for eq in self.equipments:
            eq_el = etree.SubElement(equip, 'equipment')
            eq_name = etree.SubElement(eq_el, 'name')
            eq_name.text = eq.get_name()

        return tree
