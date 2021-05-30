from lxml import etree

from src.game_entities.alteration import Alteration


class Effect:
    """ """

    def __init__(self, name, power, duration):
        self.name = name
        self.power = power
        self.duration = duration
        if (
            self.name == "speed_up"
            or self.name == "strength_up"
            or self.name == "defense_up"
        ):
            alteration_root = etree.parse("data/alterations.xml").find(name)
            desc = (
                alteration_root.find("info")
                .text.strip()
                .replace("{val}", str(self.power))
            )
            abbr = alteration_root.find("abbreviated_name").text.strip()
            self.alteration = Alteration(
                self.name, abbr, self.power, self.duration, desc
            )
        elif self.name == "stun":
            alteration_root = etree.parse("data/alterations.xml").find(name)
            desc = alteration_root.find("info").text.strip()
            abbr = alteration_root.find("abbreviated_name").text.strip()
            effs_el = alteration_root.find("effects")
            durable_effects = (
                effs_el.text.strip().split(",") if effs_el is not None else []
            )
            self.alteration = Alteration(
                self.name, abbr, self.power, self.duration, desc, durable_effects
            )

    def apply_on_ent(self, entity):
        """

        :param entity:
        :return:
        """
        msg = ""
        success = True
        if self.name == "heal":
            recovered = entity.healed(self.power)
            if recovered > 0:
                msg = f"{entity} recovered {recovered} HP."
            else:
                msg = f"{entity} is at full health and can't be healed!"
                success = False
        elif self.name == "xp_up":
            msg = f"{entity} earned {self.power} XP"
            if entity.earn_xp(self.power):
                msg += f". {entity} gained a level!"
        elif self.name == "speed_up":
            entity.set_alteration(self.alteration)
            msg = f"The speed of {entity} has been increased for {self.duration} turns"
        elif self.name == "strength_up":
            entity.set_alteration(self.alteration)
            msg = (
                f"The strength of {entity} has been increased for {self.duration} turns"
            )
        elif self.name == "defense_up":
            entity.set_alteration(self.alteration)
            msg = (
                f"The defense of {entity} has been increased for {self.duration} turns"
            )
        elif self.name == "stun":
            entity.set_alteration(self.alteration)
            msg = f"{entity} has been stunned for {self.duration} turns"
        return success, msg

    def get_formatted_desc(self):
        """

        :return:
        """
        if self.name == "heal":
            return f"Recover {self.power} HP"
        if self.name == "xp_up":
            return f"Earn {self.power} XP"
        return self.alteration.description

    def __str__(self):
        return self.name.replace("_", " ").title()
