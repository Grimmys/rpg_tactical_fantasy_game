from lxml import etree
from enum import IntEnum

from src.Character import Character
from src.constants import *


class PlayerState(IntEnum):
    WAITING_SELECTION = 0
    WAITING_MOVE = 1
    ON_MOVE = 2
    WAITING_POST_ACTION = 3
    WAITING_TARGET = 4
    FINISHED = 5


class Player(Character):
    def __init__(self, name, sprite, hp, defense, res, max_move, strength, classes, equipments, race, gold, lvl=1,
                 compl_sprite=None):
        Character.__init__(self, name, (), sprite, hp, defense, res, max_move, strength, None,
                           classes, equipments, 'MANUAL', lvl, race, gold, compl_sprite)
        self.state = PlayerState.WAITING_SELECTION
        self.old_pos = ()
        self._selected = False

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
        if self.state in range(PlayerState.WAITING_MOVE, PlayerState.WAITING_TARGET + 1):
            screen.blit(Player.SELECTED_DISPLAY, self.pos)

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, is_selected):
        self._selected = is_selected
        self.state = PlayerState.WAITING_MOVE if is_selected else PlayerState.WAITING_SELECTION

    def set_move(self, pos):
        Character.set_move(self, pos)
        self.state = PlayerState.ON_MOVE
        self.old_pos = self.pos

    def move(self):
        if self.state is PlayerState.ON_MOVE:
            Character.move(self)
            if not self.on_move:
                self.state = PlayerState.WAITING_POST_ACTION
                return True
        return False

    def cancel_move(self):
        self.state = PlayerState.WAITING_SELECTION
        self.pos = self.old_pos

    def cancel_interaction(self):
        self.state = PlayerState.WAITING_POST_ACTION

    def attack(self, ent):
        damages = Character.attack(self, ent)
        self.state = PlayerState.FINISHED
        return damages

    def turn_finished(self):
        self.state = PlayerState.FINISHED
        self._selected = False
        self.sprite = self.sprite_unavaible
        for eq in self.equipments:
            eq.set_grey()

    def new_turn(self):
        Character.new_turn(self)
        self.state = PlayerState.WAITING_SELECTION
        self.sprite = self.normal_sprite
        for eq in self.equipments:
            eq.unset_grey()

    def turn_is_finished(self):
        return self.state == PlayerState.FINISHED

    def choose_target(self):
        self.state = PlayerState.WAITING_TARGET

    def save(self, tree_name):
        # Build XML tree
        tree = Character.save(self, tree_name)

        # Save if turn is finished or not
        state = etree.SubElement(tree, 'turnFinished')
        state.text = str(self.turn_is_finished())

        # Save inventory
        inv = etree.SubElement(tree, 'inventory')
        for it in self.items:
            it_el = etree.SubElement(inv, 'item')
            it_name = etree.SubElement(it_el, 'name')
            it_name.text = it.name

        # Save equipment
        equip = etree.SubElement(tree, 'equipments')
        for eq in self.equipments:
            eq_el = etree.SubElement(equip, 'equipment')
            eq_name = etree.SubElement(eq_el, 'name')
            eq_name.text = eq.name

        return tree
