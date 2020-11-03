from lxml import etree

from src.Alteration import Alteration


class Effect:
    def __init__(self, name, power, duration):
        self.name = name
        self.power = power
        self.duration = duration
        if self.name == 'speed_up' or self.name == 'strength_up' or self.name == 'defense_up':
            alteration_root = etree.parse("data/alterations.xml").find(name)
            desc = alteration_root.find("info").text.strip().replace('{val}', str(self.power))
            abbr = alteration_root.find("abbreviated_name").text.strip()
            self.alteration = Alteration(self.name, abbr, self.power, self.duration, desc)
        elif self.name == 'stun':
            alteration_root = etree.parse("data/alterations.xml").find(name)
            desc = alteration_root.find("info").text.strip()
            abbr = alteration_root.find("abbreviated_name").text.strip()
            effs_el = alteration_root.find("effects")
            effects = effs_el.text.strip().split(',') if effs_el is not None else []
            self.alteration = Alteration(self.name, abbr, self.power, self.duration, desc, effects)

    def apply_on_ent(self, ent):
        msg = ""
        success = True
        if self.name == 'heal':
            recovered = ent.healed(self.power)
            if recovered > 0:
                msg = str(ent) + " recovered " + str(recovered) + " HP."
            else:
                msg = str(ent) + " is at full health and can't be healed !"
                success = False
        elif self.name == 'speed_up':
            ent.set_alteration(self.alteration)
            msg = "The speed of " + str(ent) + " has been increased for " + str(self.duration) + \
                  " turns"
        elif self.name == 'strength_up':
            ent.set_alteration(self.alteration)
            msg = "The strength of " + str(ent) + " has been increased for " + str(self.duration) + \
                  " turns"
        elif self.name == 'defense_up':
            ent.set_alteration(self.alteration)
            msg = "The defense of " + str(ent) + " has been increased for " + str(self.duration) + \
                  " turns"
        elif self.name == 'stun':
            ent.set_alteration(self.alteration)
            msg = str(ent) + " has been stunned for " + str(self.duration) + " turns"
        return success, msg

    def get_formatted_desc(self):
        if self.name == 'heal':
            return 'Recover ' + str(self.power) + ' HP'
        else:
            return self.alteration.desc

    def get_formatted_name(self):
        return self.name.replace('_', ' ').title()
