from lxml import etree

from src.Item import Item
from src.Alteration import  Alteration


class Consumable(Item):
    def __init__(self, name, sprite, description, effect):
        Item.__init__(self, name, sprite, description)
        self.effect = effect

    def use(self, player):
        result = self.effect.apply_on_ent(player)
        if result[0]:
            player.remove_item(self)
        return result[0], result[1]
