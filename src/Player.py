from lxml import etree
from enum import IntEnum, auto

from src.Character import Character
from src.constants import *


class PlayerState(IntEnum):
    WAITING_SELECTION = auto()
    WAITING_MOVE = auto()
    ON_MOVE = auto()
    WAITING_POST_ACTION = auto()
    WAITING_POST_ACTION_UNCANCELLABLE = auto()
    WAITING_TARGET = auto()
    FINISHED = auto()


class Player(Character):
    def __init__(self, name, sprite, hp, defense, res, strength, classes, equipments, race, gold, lvl,
                 skills, compl_sprite=None):
        Character.__init__(self, name, (), sprite, hp, defense, res, strength, None,
                           classes, equipments, 'MANUAL', lvl, skills, race, gold, compl_sprite)
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

        # Memorize the current action performed by the player, it must be a value of CharacterMenu
        self.current_action = None

    def set_initial_pos(self, pos):
        self.pos = pos
        self.old_pos = pos

    def display(self, screen):
        Character.display(self, screen)
        if self.state in range(PlayerState.WAITING_MOVE, PlayerState.WAITING_TARGET + 1):
            screen.blit(Player.SELECTED_DISPLAY, self.pos)

    @staticmethod
    def trade_gold(sender, receiver, amount):
        if amount > sender.gold:
            amount = sender.gold
        sender.gold -= amount
        receiver.gold += amount

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
        if self.state is not PlayerState.WAITING_POST_ACTION_UNCANCELLABLE:
            self.state = PlayerState.WAITING_SELECTION
            self.pos = self.old_pos
            return True
        return False

    def cancel_interaction(self):
        self.state = PlayerState.WAITING_POST_ACTION

    def use_item(self, item):
        used, result_msg = Character.use_item(self, item)
        if used:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return used, result_msg

    def equip(self, eq):
        equipped = Character.equip(self, eq)
        if equipped > -1:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return equipped

    def unequip(self, eq):
        unequipped = Character.unequip(self, eq)
        if unequipped:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return unequipped

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

        return tree
