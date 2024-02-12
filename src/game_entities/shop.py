"""
Defines Shop class, a Building in which a player character can buy or sell stuff.
"""

from __future__ import annotations

import os
from copy import copy
from typing import Optional

import pygame.mixer
from lxml import etree
from pygamepopup.components import BoxElement, Button, InfoBox, TextElement

from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.item import Item
from src.gui.fonts import fonts
from src.gui.position import Position
from src.services import menu_creator_manager
from src.services.language import *


class Shop(Building):
    """
    A Shop is a Building in which items can be sold or bought.

    Keyword arguments:
    name -- the name of the shop
    position -- the current position of the shop on screen
    sprite_link -- the relative path to the visual representation of the shop
    stock -- the data structure containing all the available items to be bought with their associated quantity
    interaction -- the interaction that should be triggered when a character player try to interact with the shop
    sprite -- the pygame Surface corresponding to the appearance of the shop on screen,
    would be loaded from sprite_link if not provided

    Attributes:
    current_visitor -- the reference to the current character visiting the shop
    stock -- the data structure containing all the available items to be bought with their associated quantity
    menu -- the shop menu displaying all the items that could be bought
    gold_sfx -- the sound that should be started when an item is sold or bought
    shop_balance -- the amount of gold the shop has
    """

    interaction_callback = None
    buy_interface_callback = None
    sell_interface_callback = None

    def __init__(
        self,
        name: str,
        position: Position,
        sprite_link: str,
        shop_balance: int,
        stock: list[dict[str, any]],
        interaction: Optional[dict[str, any]] = None,
        sprite: Optional[pygame.Surface] = None,
    ) -> None:
        super().__init__(name, position, sprite_link, interaction, sprite)
        self.shop_balance = shop_balance
        self.current_visitor: Optional[Character] = None
        self.stock: list[dict[str, any]] = stock
        self.interaction: dict[str, any] = interaction
        self.menu: InfoBox = menu_creator_manager.create_shop_menu(
            Shop.interaction_callback, self.stock, 0, self.shop_balance
        )
        self.gold_sfx: pygame.mixer.Sound = pygame.mixer.Sound(
            os.path.join("sound_fx", "trade.ogg")
        )

    def get_item_entry(self, item: Item) -> Optional[dict[str, any]]:
        """
        Return the entry corresponding to one item

        Keyword arguments:
        item -- the concerned item
        """
        for entry in self.stock:
            if entry["item"].name == item.name:
                return entry
        return None

    def update_shop_menu(self, gold: int) -> None:
        """
        Update the shop menu with the actual stock and the new gold amount provided

        Keyword arguments:
        gold -- the new gold amount for the player that should be displayed
        """
        self.menu = menu_creator_manager.create_shop_menu(
            Shop.interaction_callback, self.stock, gold, self.shop_balance
        )

    def interact(self, actor: Character) -> list[list[BoxElement]]:
        """
        Manage the interaction of a character with the shop.

        Return the list of entries corresponding to the data that should be displayed on
        the player interface

        Keyword argument:
        actor -- the character visiting the shop
        """
        self.current_visitor = actor
        self.update_shop_menu(self.current_visitor.gold)

        grid_element: list[list[BoxElement]] = [
            [Button(title=STR_BUY, callback=Shop.buy_interface_callback)],
            [Button(title=STR_SELL, callback=Shop.sell_interface_callback)],
        ]

        if self.interaction:
            for talk in self.interaction["talks"]:
                pygame.mixer.Sound.play(self.talk_sfx)
                grid_element.append([TextElement(talk, font=fonts["ITEM_DESC_FONT"])])

        return grid_element

    # TODO: Return type of buy and sell methods should be coherent
    def buy(self, item: Item) -> str:
        """
        Handle the wish of purchase an item by a player character.

        Return the message that should be displayed to the player after the purchase tentative.

        Keyword arguments:
        actor -- the actor buying the item
        item -- the item that is being bought
        """
        if self.current_visitor.gold >= item.price:
            if len(self.current_visitor.items) < self.current_visitor.nb_items_max:
                pygame.mixer.Sound.play(self.gold_sfx)
                self.current_visitor.gold -= item.price
                self.current_visitor.set_item(copy(item))
                self.shop_balance += item.price
                entry: Optional[dict[str, any]] = self.get_item_entry(item)
                entry["quantity"] -= 1
                if entry["quantity"] <= 0:
                    self.stock.remove(entry)

                # Gold total amount and stock have been decreased: the screen should be updated
                self.update_shop_menu(self.current_visitor.gold)

                return STR_THE_ITEM_HAS_BEEN_BOUGHT
            return STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM
        return STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM

    def sell(self, item: Item) -> tuple[bool, str]:
        """
        Handle the tentative of selling an item by a player character.

        Return whether the item has been sold or not and the message that should be displayed to the player.

        Keyword arguments:
        actor -- the actor selling the item
        item -- the item that is being sold
        """
        if 0 < item.resell_price < self.shop_balance:
            self.current_visitor.remove_item(item)
            self.current_visitor.gold += item.resell_price
            self.shop_balance -= item.resell_price

            # Update shop screen content (gold total amount has been augmented)
            self.update_shop_menu(self.current_visitor.gold)

            return True, STR_THE_ITEM_HAS_BEEN_SOLD
        return False, STR_THIS_ITEM_CANT_BE_SOLD

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the shop in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Specify nature
        nature: etree.SubElement = etree.SubElement(tree, "type")
        nature.text = "shop"

        # Specify content
        items: etree.SubElement = etree.SubElement(tree, "items")
        for entry in self.stock:
            item: etree.SubElement = etree.SubElement(items, "item")

            name: etree.SubElement = etree.SubElement(item, "name")
            name.text = entry["item"].name

            quantity: etree.SubElement = etree.SubElement(item, "quantity")
            quantity.text = str(entry["quantity"])

        return tree
