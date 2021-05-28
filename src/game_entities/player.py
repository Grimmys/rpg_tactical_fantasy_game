from enum import IntEnum, auto
from typing import Union, Sequence

import pygame
from lxml import etree

from src.constants import LIGHT_GREY
from src.game_entities.alteration import Alteration
from src.game_entities.character import Character
from src.game_entities.consumable import Consumable
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.skill import Skill
from src.services.menus import CharacterMenu


class PlayerState(IntEnum):
    WAITING_SELECTION = auto()
    WAITING_MOVE = auto()
    ON_MOVE = auto()
    WAITING_POST_ACTION = auto()
    WAITING_POST_ACTION_UNCANCELLABLE = auto()
    WAITING_TARGET = auto()
    FINISHED = auto()


class Player(Character):
    """

    """
    def __init__(self, name: str, sprite: Union[str, pygame.Surface], hit_points: int, defense: int,
                 resistance: int, strength: int, classes: Sequence[str], equipments: list[Equipment],
                 race: str, gold: int, lvl: int, skills: Sequence[Skill],
                 alterations: list[Alteration], complementary_sprite_link: str = None):
        super().__init__(name, (-1, -1), sprite, hit_points, defense, resistance, strength,
                         classes, equipments, 'MANUAL', lvl, skills, alterations,
                         race, gold, {}, complementary_sprite_link)
        self.state: PlayerState = PlayerState.WAITING_SELECTION
        self.old_position: tuple[int, int] = (-1, -1)
        self._selected: bool = False

        # Sprite displayed when player cannot be selected
        self.sprite_unavailable: pygame.Surface = self.sprite.copy()
        color_image: pygame.Surface = pygame.Surface(self.sprite.get_size()).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Memorize normal state sprite
        self.normal_sprite: pygame.Surface = self.sprite

        # Memorize the current action performed by the player, it must be a value of CharacterMenu
        self.current_action: Union[CharacterMenu, None] = None

    def set_initial_pos(self, position: tuple[int, int]) -> None:
        """

        :param position:
        """
        self.position = position
        self.old_position = position

    def display(self, screen: pygame.Surface) -> None:
        """

        :param screen:
        """
        Character.display(self, screen)
        if self.state in range(PlayerState.WAITING_MOVE, PlayerState.WAITING_TARGET + 1):
            screen.blit(Player.SELECTED_DISPLAY, self.position)

    @staticmethod
    def trade_gold(sender: Character, receiver: Character, amount: int) -> None:
        """

        :param sender:
        :param receiver:
        :param amount:
        """
        if amount > sender.gold:
            amount = sender.gold
        sender.gold -= amount
        receiver.gold += amount

    @property
    def selected(self) -> bool:
        """

        :return:
        """
        return self._selected

    @selected.setter
    def selected(self, is_selected: bool) -> None:
        self._selected = is_selected
        self.state = PlayerState.WAITING_MOVE if is_selected else PlayerState.WAITING_SELECTION

    def set_move(self, position: Sequence[tuple[int, int]]) -> None:
        """

        :param position:
        """
        Character.set_move(self, position)
        self.state = PlayerState.ON_MOVE
        self.old_position = self.position

    def move(self) -> bool:
        """

        :return:
        """
        if self.state is PlayerState.ON_MOVE:
            Character.move(self)
            if not self.on_move:
                self.state = PlayerState.WAITING_POST_ACTION
                return True
        return False

    def cancel_move(self) -> bool:
        """

        :return:
        """
        if self.state is not PlayerState.WAITING_POST_ACTION_UNCANCELLABLE:
            self.state = PlayerState.WAITING_SELECTION
            self.position = self.old_position
            return True
        return False

    def cancel_interaction(self) -> None:
        """

        """
        self.state = PlayerState.WAITING_POST_ACTION

    def use_item(self, item: Consumable) -> tuple[bool, Sequence[str]]:
        """

        :param item:
        :return:
        """
        used, result_msgs = Character.use_item(self, item)
        if used:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return used, result_msgs

    def equip(self, equipment: Equipment) -> int:
        """

        :param equipment:
        :return:
        """
        equipped: int = Character.equip(self, equipment)
        if equipped > -1:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return equipped

    def unequip(self, equipment: Equipment) -> int:
        """

        :param equipment:
        :return:
        """
        unequipped = Character.unequip(self, equipment)
        if unequipped:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return unequipped

    def attack(self, entity: Entity) -> int:
        """

        :param entity:
        :return:
        """
        damages: int = Character.attack(self, entity)
        self.state = PlayerState.FINISHED
        return damages

    def end_turn(self) -> None:
        """

        """
        self.state = PlayerState.FINISHED
        self._selected = False
        self.sprite = self.sprite_unavailable
        for eq in self.equipments:
            eq.set_grey()
        # Remove all alterations that are finished
        self.alterations = [alt for alt in self.alterations if not alt.is_finished()]

    def new_turn(self) -> None:
        """

        """
        Character.new_turn(self)
        self.state = PlayerState.WAITING_SELECTION
        self.sprite = self.normal_sprite
        for equipment in self.equipments:
            equipment.unset_grey()

    def turn_is_finished(self) -> bool:
        """

        :return:
        """
        return self.state == PlayerState.FINISHED

    def choose_target(self) -> None:
        """

        """
        self.state = PlayerState.WAITING_TARGET

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the player in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        # Build XML tree
        tree: etree.Element = super().save(tree_name)

        # Save if turn is finished or not
        state: etree.SubElement = etree.SubElement(tree, 'turnFinished')
        state.text = str(self.turn_is_finished())

        return tree
