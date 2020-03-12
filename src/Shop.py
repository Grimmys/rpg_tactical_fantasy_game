
from src.Building import Building

SHOP_MENU_ID = 0
BUY_ACTION_ID = 0
SELL_ACTION_ID = 1


class Shop(Building):
    def __init__(self, name, pos, sprite, interaction, items):
        Building.__init__(self, name, pos, sprite, interaction)
        self.items = items

    def interact(self, actor):
        entries = [[{'name': 'Buy', 'id': BUY_ACTION_ID, 'type': 'button', 'args': [self]}],
                   [{'name': 'Sell', 'id': SELL_ACTION_ID, 'type': 'button'}]]

        return entries

    def get_items(self):
        return self.items
