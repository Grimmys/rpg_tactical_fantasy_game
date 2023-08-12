"""
Defines Alteration class, permitting to temporarily modify the state of a living-entity.
"""

from lxml import etree

from src.services.language import TRANSLATIONS


class Alteration:
    """
    An Alteration is representing a status that will stay on the entity for one or more turns.

    Keyword arguments:
    name -- the name of the alteration
    abbreviated_name -- the abbreviated version of the alteration name
    power -- the power of the alteration if it's something that is modifying a statistic for example
    duration -- the duration of the alteration
    description -- the description of the alteration, can be displayed on an interface to give
    information to the player about the alteration
    specificities -- describes some specific data related to the alteration

    Attributes:
    name -- the name of the alteration
    abbreviated_name -- the abbreviated version of the alteration name
    power -- the power of the alteration if it's something that is modifying a statistic for example
    duration -- the duration of the alteration
    time -- the number of turns since the alteration exists
    description -- the description of the alteration, can be displayed on an interface to give
    information to the player about the alteration
    specificities -- describes some specific data related to the alteration
    """

    def __init__(
        self,
        name: str,
        abbreviated_name: str,
        power: int,
        duration: int,
        description: str,
        specificities: any = None,
    ) -> None:
        if specificities is None:
            specificities = []
        self.name: str = name
        self.abbreviated_name: str = abbreviated_name
        self.power: int = power
        self.duration: int = duration
        self.time: int = 0
        self.description: str = description
        self.specificities: any = specificities

    def get_turns_left(self) -> int:
        """
        Return the number of turns left before the end of the alteration
        """
        return self.duration - self.time

    def increment(self) -> None:
        """
        Increment the number of turns of existence by one
        """
        self.time += 1

    def is_finished(self) -> bool:
        """
        Return whether the alteration is ended or not
        """
        return self.time >= self.duration

    def __str__(self) -> str:
        try:
            return TRANSLATIONS["alterations"][self.name]
        except KeyError:
            return self.name.replace("_", " ").capitalize()

    def __eq__(self, name: str) -> bool:
        return self.name == name

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the alteration in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = etree.Element(tree_name)

        alteration_name: etree.SubElement = etree.SubElement(tree, "name")
        alteration_name.text = self.name
        alteration_abbreviation: etree.SubElement = etree.SubElement(tree, "abbr")
        alteration_abbreviation.text = self.abbreviated_name
        alteration_power: etree.SubElement = etree.SubElement(tree, "power")
        alteration_power.text = str(self.power)
        alteration_duration: etree.SubElement = etree.SubElement(tree, "duration")
        alteration_duration.text = str(self.duration)
        alteration_description: etree.SubElement = etree.SubElement(tree, "desc")
        alteration_description.text = self.description
        alteration_specificities: etree.SubElement = etree.SubElement(tree, "specs")
        for specificity in self.specificities:
            specificity_element: etree.SubElement = etree.SubElement(
                alteration_specificities, "spec"
            )
            specificity_element.text = specificity

        return tree
