from src.Item import Item


class Consumable(Item):
    def __init__(self, name, sprite, description, price, effect):
        Item.__init__(self, name, sprite, description, price)
        self.effect = effect

    def use(self, player):
        result = self.effect.apply_on_ent(player)
        if result[0]:
            player.remove_item(self)
        return result[0], result[1]
