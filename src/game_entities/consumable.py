from src.game_entities.item import Item


class Consumable(Item):
    def __init__(self, name, sprite, description, price, effects):
        Item.__init__(self, name, sprite, description, price)
        self.effects = effects

    def use(self, player):
        success = False
        msgs = []
        for eff in self.effects:
            sub_success, msg = eff.apply_on_ent(player)
            msgs.append(msg)
            if sub_success:
                success = True
        if success:
            player.remove_item(self)
        return success, msgs
