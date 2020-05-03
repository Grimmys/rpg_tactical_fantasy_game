from lxml import etree

from src.Alteration import Alteration


class Effect:
    def __init__(self, name, power, duration):
        self.name = name
        self.power = power
        self.duration = duration

    def apply_on_ent(self, ent):
        msg = ""
        success = True
        if self.name == 'heal':
            recovered = ent.healed(self.power)
            if recovered > 0:
                msg = ent.get_formatted_name() + " recovered " + str(recovered) + " HP."
            else:
                msg = ent.get_formatted_name() + " is at full health and can't be healed !"
                success = False
        elif self.name == 'speed':
            alteration_root = etree.parse("data/alterations/speed_up.xml").getroot()
            desc = alteration_root.find("info").text.strip().replace('{val}', str(self.power))
            alteration = Alteration('speed_up', self.name, self.power, self.duration, desc)
            ent.set_alteration(alteration)
            msg = "The speed of " + ent.get_formatted_name() + " has been increased for " + str(self.duration) + \
                  " turns."
        return success, msg

    def get_formatted_desc(self):
        string = ''
        if self.name == 'heal':
            string += 'Recover ' + str(self.power) + ' HP'
        return string
