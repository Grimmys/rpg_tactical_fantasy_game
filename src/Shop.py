from lxml import etree

from src.Building import Building
from src.Menus import ShopMenu


class Shop(Building):
    def __init__(self, name, pos, sprite, interaction, items):
        Building.__init__(self, name, pos, sprite, interaction)
        self.items = items

    def interact(self, actor):
        entries = [[{'name': 'Buy', 'id': ShopMenu.BUY, 'type': 'button', 'args': [self]}],
                   [{'name': 'Sell', 'id': ShopMenu.SELL, 'type': 'button'}]]

        return entries

    def save(self, tree_name):
        tree = Building.save(self, tree_name)

        # Specify nature
        nature = etree.SubElement(tree, 'type')
        nature.text = 'shop'

        # Specify content
        items = etree.SubElement(tree, 'items')
        for it in self.items:
            item = etree.SubElement(items, 'item')
            name = etree.SubElement(item, 'name')
            name.text = it.name

        return tree
