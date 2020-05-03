from src.Item import Item


class Consumable(Item):
    def __init__(self, name, sprite, description, price, effect):
        Item.__init__(self, name, sprite, description, price)
        self.effect = effect

    def use(self, player):
        success, msg = self.effect.apply_on_ent(player)
        if success:
            player.remove_item(self)
        return success, msg
