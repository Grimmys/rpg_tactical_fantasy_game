from lxml import etree

from src.Item import Item
from src.Alteration import  Alteration


class Consumable(Item):
    def __init__(self, name, sprite, description, effect, power, duration):
        Item.__init__(self, name, sprite, description)
        self.effect = effect
        self.power = power
        self.duration = duration

    def use(self, player):
        msg = ""
        used = True
        player_name = player.get_name()
        if self.effect == 'heal':
            recovered_hp = player.healed(self.power)
            if recovered_hp > 0:
                msg = player_name + " recovered " + str(recovered_hp) + " HP"
                player.remove_item(self)
            else:
                msg = player_name + " is at full health and can't be healed !"
                used = False
        elif self.effect == 'speed':
            alteration_root = etree.parse("data/alterations/speed_up.xml").getroot()
            desc = alteration_root.find("info").text.strip().replace('{val}', str(self.power))
            alteration = Alteration('speed_up', self.effect, self.power, self.duration, desc)
            player.set_alteration(alteration)
            player.remove_item(self)
            msg = "The speed of " + player_name + " has been increased for " + str(self.duration) + " turns."
        return used, msg
