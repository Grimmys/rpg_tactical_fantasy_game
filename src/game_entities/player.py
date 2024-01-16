"""
Defines Player class, the class defining characters controlled by the player
"""

from __future__ import annotations

from collections.abc import Sequence
from enum import IntEnum, auto
from typing import Optional, Union

import pygame
from lxml import etree

from src.constants import LIGHT_GREY
from src.game_entities.alteration import Alteration
from src.game_entities.character import Character
from src.game_entities.consumable import Consumable
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.skill import Skill
from src.gui.position import Position
from src.services.menus import CharacterMenu


class PlayerState(IntEnum):
    """
    Defines the cycle of states for a player.
    """

    WAITING_SELECTION = auto()
    WAITING_MOVE = auto()
    ON_MOVE = auto()
    WAITING_POST_ACTION = auto()
    WAITING_POST_ACTION_UNCANCELLABLE = auto()
    WAITING_TARGET = auto()
    FINISHED = auto()


class Player(Character):
    """
    A Player is a Character controlled by the player.
    Each Player is part of the player's characters team.

    Keyword Arguments:
    name -- the name of the entity
    sprite -- the pygame Surface corresponding to the appearance of the entity on screen or
    the relative path to the visual representation of the entity
    hit_points -- the total of damage that the entity can take before disappearing
    defense -- the resistance of the entity from physical attacks
    resistance -- the resistance of the entity from spiritual attacks
    strength -- the raw strength of the entity
    classes -- the sequence of classes of the character
    equipments -- the list of equipment worn by the character
    race -- the character's race
    gold -- the amount of gold the character has
    lvl -- the current level of the entity
    skills -- the list of skills of the entity
    alterations -- the list of ongoing alterations affecting the entity
    complementary_sprite_link -- the relative path to the sprite that should be blitted on top of the base sprite

    Attributes:
    old_position -- the reference to the previous position of the player to be able to revert the last move if requested
    _selected -- whether the player is selected or not
    sprite_unavailable -- the sprite to be displayed when the player's turn is finished
    normal_sprite -- the reference to the default sprite
    current_action -- the ongoing action of the player if there is any
    """

    def __init__(
        self,
        name: str,
        sprite: Union[str, pygame.Surface],
        hit_points: int,
        defense: int,
        resistance: int,
        strength: int,
        classes: Sequence[str],
        equipments: list[Equipment],
        race: str,
        gold: int,
        lvl: int,
        skills: Sequence[Skill],
        alterations: list[Alteration],
        complementary_sprite_link: str = None,
    ):
        super().__init__(
            name,
            (-1, -1),
            sprite,
            hit_points,
            defense,
            resistance,
            strength,
            classes,
            equipments,
            "MANUAL",
            lvl,
            skills,
            alterations,
            race,
            gold,
            {},
            complementary_sprite_link,
        )
        self.state: PlayerState = PlayerState.WAITING_SELECTION
        self.old_position: tuple[int, int] = (-1, -1)
        self._selected: bool = False

        # Sprite displayed when player cannot be selected
        self.sprite_unavailable: pygame.Surface = self.sprite.copy()
        color_image: pygame.Surface = pygame.Surface(
            self.sprite.get_size()
        ).convert_alpha()
        color_image.fill(LIGHT_GREY)
        self.sprite_unavailable.blit(
            color_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )

        # Memorize normal state sprite
        self.normal_sprite: pygame.Surface = self.sprite

        # Memorize the current action performed by the player, it must be a value of CharacterMenu
        self.current_action: Optional[CharacterMenu] = None

    def set_initial_pos(self, position: Position) -> None:
        """
        Set the initial position of the player.

        Keyword arguments:
        position -- the position that should be set
        """
        self.position = position
        self.old_position = position

    def display(self, screen: pygame.Surface) -> None:
        """
        Display the player on the given screen.
        Also display on top of it the selected indicator if the player is currently active.

        Keyword arguments:
        screen -- the screen on which the player should be drawn
        """
        Character.display(self, screen)
        if self.state in range(
            PlayerState.WAITING_MOVE, PlayerState.WAITING_TARGET + 1
        ):
            screen.blit(Player.SELECTED_DISPLAY, self.position)

    @staticmethod
    def trade_gold(sender: Character, receiver: Character, amount: int) -> None:
        """
        Handle the trading of a specific amount of gold between two characters.

        Keyword arguments:
        sender -- the character sending the gold
        receiver -- the character that should receive the gold
        amount -- the amount of gold traded
        """
        if amount > sender.gold:
            amount = sender.gold
        sender.gold -= amount
        receiver.gold += amount

    @property
    def selected(self) -> bool:
        """Return whether the player is selected or not"""
        return self._selected

    @selected.setter
    def selected(self, is_selected: bool) -> None:
        """
        Set whether the player is selected or not.
        Change the current state of the player to match its selection status.

        Keyword arguments:
        is_selected -- whether the player is selected or not
        """
        self._selected = is_selected
        self.state = (
            PlayerState.WAITING_MOVE if is_selected else PlayerState.WAITING_SELECTION
        )

    def is_waiting_post_action(self) -> bool:
        """
        Return whether the player is waiting a post action or not
        """
        return (
            self.state is PlayerState.WAITING_POST_ACTION
            or self.state is PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        )

    def target_selected(self) -> None:
        """
        Change back the state to waiting an action and not waiting for the selection of a target
        """
        self.state = PlayerState.WAITING_POST_ACTION

    def set_move(self, path: Sequence[Position]) -> None:
        """
        Set the movement of the player to the given position

        Keyword arguments:
        path -- the ordered sequence of tiles that should be crossed by the entity
        """
        Character.set_move(self, path)
        self.state = PlayerState.ON_MOVE
        self.old_position = self.position

    def move(self) -> None:
        """
        Move the player by one tile.
        If the target position is reached, change the current state of the player.
        """
        if self.state is PlayerState.ON_MOVE:
            Character.move(self)
            if not self.on_move:
                self.state = PlayerState.WAITING_POST_ACTION

    def cancel_move(self) -> bool:
        """
        Try to cancel the last move action of the player.

        Return whether the move has been cancelled or not.
        """
        if self.state is not PlayerState.WAITING_POST_ACTION_UNCANCELLABLE:
            self.state = PlayerState.WAITING_SELECTION
            self.position = self.old_position
            return True
        return False

    def cancel_interaction(self) -> None:
        """
        Cancel interaction selection.
        """
        self.state = PlayerState.WAITING_POST_ACTION

    def use_item(self, item: Consumable) -> tuple[bool, Sequence[str]]:
        """
        Use the given consumable item.
        Change the player state if the item has successfully been used.

        Return whether the item has been used or not and the messages that should be sent to the player.

        Keyword arguments:
        item -- the item that should be consumed
        """
        used, result_msgs = Character.use_item(self, item)
        if used:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return used, result_msgs

    def equip(self, equipment: Equipment) -> int:
        """
        Equip the given equipment.

        Return whether the equipment has been equipped or not and if it replaced an another equipment.

        Keyword arguments:
        equipment -- the equipment that should be equipped
        """
        equipped: int = Character.equip(self, equipment)
        if equipped > -1:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return equipped

    def unequip(self, equipment: Equipment) -> bool:
        """
        Unequip the given equipment.

        Return whether the equipment has been unequipped or not.

        Keyword arguments:
        equipment -- the equipment that should be unequipped
        """
        unequipped = Character.unequip(self, equipment)
        if unequipped:
            self.state = PlayerState.WAITING_POST_ACTION_UNCANCELLABLE
        return unequipped

    def attack(self, entity: Entity) -> int:
        """
        Return the damage that should be dealt to the given entity during an attack.
        Change the state of the player to the last one (turn finished)

        Keyword arguments:
        entity -- the target of the attack
        """
        damages: int = Character.attack(self, entity)
        self.state = PlayerState.FINISHED
        return damages

    def end_turn(self) -> None:
        """Handle the end of the turn of the player"""
        self.state = PlayerState.FINISHED
        self._selected = False
        self.sprite = self.sprite_unavailable
        for equipment in self.equipments:
            equipment.set_grey()
        # Remove all alterations that are finished
        self.alterations = [
            alteration
            for alteration in self.alterations
            if not alteration.is_finished()
        ]

    def new_turn(self) -> None:
        """Handle the start of a new turn for the player"""
        Character.new_turn(self)
        self.state = PlayerState.WAITING_SELECTION
        self.sprite = self.normal_sprite
        for equipment in self.equipments:
            equipment.unset_grey()

    def turn_is_finished(self) -> bool:
        """Return whether the player turn is ended or not"""
        return self.state == PlayerState.FINISHED

    def choose_target(self) -> None:
        """Handle the selection of a target for an attack"""
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
        state: etree.SubElement = etree.SubElement(tree, "turnFinished")
        state.text = str(self.turn_is_finished())

        return tree
