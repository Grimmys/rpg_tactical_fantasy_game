from src.Item import Item


class Consumable(Item):
    def __init__(self, name, sprite, description, effect, power):
        Item.__init__(self, name, sprite, description)
        self.effect = effect
        self.power = power

    def use(self, player):
        print(self.effect)
        print(self.effect == 'heal')
        if self.effect == 'heal':
            recovered_hp = player.healed(self.power)
            player_name = player.get_name()
            msg = ""
            used = True
            if recovered_hp > 0:
                msg = player_name + " recovered " + str(recovered_hp) + " HP"
                player.remove_item(self)
            else:
                msg = player_name + " is at full health and can't be healed !"
                used = False
            return used, msg
