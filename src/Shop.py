
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
