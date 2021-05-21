from lxml import etree


class Alteration:
    def __init__(self, name, abbr, power, duration, description, specificities=None):
        if specificities is None:
            specificities = []
        self.name = name
        self.abbreviated_name = abbr
        self.power = power
        self.duration = duration
        self.time = 0
        self.description = description
        self.specificities = specificities

    def get_turns_left(self):
        return self.duration - self.time

    def increment(self):
        self.time += 1

    def is_finished(self):
        return self.time >= self.duration

    def __str__(self):
        return self.name.replace('_', ' ').capitalize()

    def __eq__(self, o):
        return self.name == o

    def save(self, tree_name):
        tree = etree.Element(tree_name)

        alteration_name = etree.SubElement(tree, 'name')
        alteration_name.text = self.name
        alteration_abbr = etree.SubElement(tree, 'abbr')
        alteration_abbr.text = self.abbreviated_name
        alteration_power = etree.SubElement(tree, 'power')
        alteration_power.text = str(self.power)
        alteration_duration = etree.SubElement(tree, 'duration')
        alteration_duration.text = str(self.duration)
        alteration_desc = etree.SubElement(tree, 'desc')
        alteration_desc.text = self.description
        alteration_specs = etree.SubElement(tree, 'specs')
        for spec in self.specificities:
            spec_el = etree.SubElement(alteration_specs, 'spec')
            spec_el.text = spec

        return tree
