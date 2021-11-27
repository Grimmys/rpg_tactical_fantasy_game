"""
Defines Shop class, a Building in which a player character can buy or sell stuff.
"""

from copy import copy
import os
from typing import Optional

import pygame.mixer
from lxml import etree

from src.game_entities.character import Character
from src.game_entities.item import Item
from src.gui.entries import Entries
from src.gui.fonts import fonts
from src.gui.info_box import InfoBox
from src.services import menu_creator_manager
from src.game_entities.building import Building


class Shop(Building):
    """
    A Shop is a Building in which items can be sold or bought.

    Keyword arguments:
    name -- the name of the shop
    position -- the current position of the shop on screen
    sprite -- the relative path to the visual representation of the shop
    interaction -- the interaction that should be triggered when a character player try to interact with the shop
    stock -- the data structure containing all the available items to be bought with their associated quantity

    Attributes:
    stock -- the data structure containing all the available items to be bought with their associated quantity
    menu -- the shop menu displaying all the items that could be bought
    gold_sfx -- the sound that should be started when an item is sold or bought
    """

    interaction_callback = None
    buy_interface_callback = None
    sell_interface_callback = None

    def __init__(
        self,
        name: str,
        position: tuple[int, int],
        sprite: str,
        interaction: dict[str, any],
        stock: list[dict[str, any]],
    ) -> None:
        super().__init__(name, position, sprite, interaction)
        self.stock: list[dict[str, any]] = stock
        self.interaction: dict[str, any] = interaction
        self.menu: InfoBox = menu_creator_manager.create_shop_menu(
            Shop.interaction_callback, self.stock, 0
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
        for row in self.menu.entries:
            for entry in row:
                if entry["type"] == "item_button":
                    item: Optional[dict[str, any]] = self.get_item_entry(
                        entry["item"]
                    )
                    if item:
                        entry["quantity"] = item["quantity"]
                    else:
                        row.remove(entry)
                        if len(row) == 0:
                            self.menu.entries.remove(row)
                if entry["type"] == "text":
                    entry["text"] = f"Your gold : {gold}"
        self.menu.update_content(self.menu.entries)

    def interact(self, actor: Character) -> Entries:
        """
        Manage the interaction of a character with the shop.

        Return the list of entries corresponding to the data that should be displayed on
        the player interface

        Keyword argument:
        actor -- the character visiting the shop
        """
        self.update_shop_menu(actor.gold)

        entries: Entries = [
            [
                {
                    "name": "Buy",
                    "callback": Shop.buy_interface_callback,
                    "type": "button",
                }
            ],
            [
                {
                    "name": "Sell",
                    "callback": Shop.sell_interface_callback,
                    "type": "button",
                }
            ],
        ]

        if not self.interaction:
            pygame.mixer.Sound.play(self.door_sfx)
            entries.append(
                [
                    {
                        "type": "text",
                        "text": "This shop seems closed...",
                        "font": fonts["ITEM_DESC_FONT"],
                    }
                ]
            )
        else:
            for talk in self.interaction["talks"]:
                pygame.mixer.Sound.play(self.talk_sfx)
                entries.append(
                    [{"type": "text", "text": talk, "font": fonts["ITEM_DESC_FONT"]}]
                )

        return entries

    # TODO: Return type of buy and sell methods should be coherent
    def buy(self, actor: Character, item: Item) -> str:
        """
        Handle the wish of purchase an item by a player character.

        Return the message that should be displayed to the player after the purchase tentative.

        Keyword arguments:
        actor -- the actor buying the item
        item -- the item that is being bought
        """
        if actor.gold >= item.price:
            if len(actor.items) < actor.nb_items_max:
                pygame.mixer.Sound.play(self.gold_sfx)

                actor.gold -= item.price
                actor.set_item(copy(item))

                entry: Optional[dict[str, any]] = self.get_item_entry(item)
                entry["quantity"] -= 1
                if entry["quantity"] <= 0:
                    self.stock.remove(entry)

                # Gold total amount and stock have been decreased: the screen should be updated
                self.update_shop_menu(actor.gold)

                return "The item has been bought."
            return "Not enough space in inventory to buy this item."
        return "Not enough gold to buy this item."

    def sell(self, actor: Character, item: Item) -> tuple[bool, str]:
        """
        Handle the tentative of selling an item by a player character.

        Return whether the item has been sold or not and the message that should be displayed to the player.

        Keyword arguments:
        actor -- the actor selling the item
        item -- the item that is being sold
        """
        if item.resell_price > 0:
            actor.remove_item(item)
            actor.gold += item.resell_price

            # Update shop screen content (gold total amount has been augmented)
            self.update_shop_menu(actor.gold)

            return True, "The item has been sold."
        return False, "This item can't be sold !"

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
