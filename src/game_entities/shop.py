from copy import copy
import os
from typing import Sequence, Union, List

import pygame.mixer
from lxml import etree

from src.game_entities.character import Character
from src.game_entities.item import Item
from src.gui.infoBox import InfoBox
from src.services import menuCreatorManager
from src.game_entities.building import Building
from src.services.menus import ShopMenu


class Shop(Building):
    def __init__(self, name: str, position: tuple[int, int], sprite: str,
                 interaction: dict[str, any], stock: List[dict[str, any]]) -> None:
        Building.__init__(self, name, position, sprite, interaction)
        self.stock: List[dict[str, any]] = stock
        self.menu: InfoBox = menuCreatorManager.create_shop_menu(self.stock, 0)
        self.gold_sfx: pygame.mixer.Sound = pygame.mixer.Sound(os.path.join('sound_fx',
                                                                            'trade.ogg'))

    def get_item_entry(self, item: Item) -> Union[dict[str, any], None]:
        for entry in self.stock:
            if entry['item'].name == item.name:
                return entry
        return None

    def update_shop_menu(self, gold: int) -> None:
        for row in self.menu.entries:
            for entry in row:
                if entry['type'] == 'item_button':
                    item: Union[dict[str, any], None] = self.get_item_entry(entry['item'])
                    if item:
                        entry['quantity'] = item['quantity']
                    else:
                        row.remove(entry)
                        if len(row) == 0:
                            self.menu.entries.remove(row)
                if entry['type'] == 'text':
                    entry['text'] = 'Your gold : ' + str(gold)
        self.menu.update_content(self.menu.entries)

    def interact(self, actor: Character) -> Sequence[Sequence[dict[str, str]]]:
        self.update_shop_menu(actor.gold)

        entries: Sequence[Sequence[dict[str, str]]] = [[{'name': 'Buy', 'id': ShopMenu.BUY,
                                                         'type': 'button', 'args': [self]}],
                                                       [{'name': 'Sell', 'id': ShopMenu.SELL,
                                                         'type': 'button'}]]
        return entries

    # TODO: Return type of buy and sell methods should be coherent
    def buy(self, actor: Character, item: Item) -> str:
        if actor.gold >= item.price:
            if len(actor.items) < actor.nb_items_max:
                pygame.mixer.Sound.play(self.gold_sfx)

                actor.gold -= item.price
                actor.set_item(copy(item))

                entry: Union[dict[str, any], None] = self.get_item_entry(item)
                entry['quantity'] -= 1
                if entry['quantity'] <= 0:
                    self.stock.remove(entry)

                # Gold total amount and stock have been decreased: the screen should be updated
                self.update_shop_menu(actor.gold)

                return "The item has been bought."
            return "Not enough space in inventory to buy this item."
        return "Not enough gold to buy this item."

    def sell(self, actor: Character, item: Item) -> tuple[bool, str]:
        if item.resell_price > 0:
            actor.remove_item(item)
            actor.gold += item.resell_price

            # Update shop screen content (gold total amount has been augmented)
            self.update_shop_menu(actor.gold)

            return True, "The item has been sold."
        return False, "This item can't be sold !"

    def save(self, tree_name: str) -> etree.Element:
        tree: etree.Element = Building.save(self, tree_name)

        # Specify nature
        nature: etree.SubElement = etree.SubElement(tree, 'type')
        nature.text = 'shop'

        # Specify content
        items: etree.SubElement = etree.SubElement(tree, 'items')
        for entry in self.stock:
            item: etree.SubElement = etree.SubElement(items, 'item')

            name: etree.SubElement = etree.SubElement(item, 'name')
            name.text = entry['item'].name

            quantity: etree.SubElement = etree.SubElement(item, 'quantity')
            quantity.text = str(entry['quantity'])

        return tree
