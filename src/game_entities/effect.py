from lxml import etree

from src.game_entities.alteration import Alteration


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
            durable_effects = effs_el.text.strip().split(',') if effs_el is not None else []
            self.alteration = Alteration(self.name, abbr, self.power, self.duration,
                                         desc, durable_effects)

    def apply_on_ent(self, ent):
        msg = ''
        success = True
        if self.name == 'heal':
            recovered = ent.healed(self.power)
            if recovered > 0:
                msg = f'{ent} recovered {recovered} HP.'
            else:
                msg = f"{ent} is at full health and can't be healed!"
                success = False
        elif self.name == 'xp_up':
            msg = f'{ent} earned {self.power} XP'
            if ent.earn_xp(self.power):
                msg += f'. {ent} gained a level!'
        elif self.name == 'speed_up':
            ent.set_alteration(self.alteration)
            msg = f'The speed of {ent} has been increased for {self.duration} turns'
        elif self.name == 'strength_up':
            ent.set_alteration(self.alteration)
            msg = f'The strength of {ent} has been increased for {self.duration} turns'
        elif self.name == 'defense_up':
            ent.set_alteration(self.alteration)
            msg = f'The defense of {ent} has been increased for {self.duration} turns'
        elif self.name == 'stun':
            ent.set_alteration(self.alteration)
            msg = f'{ent} has been stunned for {self.duration} turns'
        return success, msg

    def get_formatted_desc(self):
        if self.name == 'heal':
            return f'Recover {self.power} HP'
        if self.name == 'xp_up':
            return f'Earn {self.power} XP'
        return self.alteration.description

    def __str__(self):
        return self.name.replace('_', ' ').title()
