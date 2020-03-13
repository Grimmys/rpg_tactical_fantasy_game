from lxml import etree

from src.Entity import Entity
from src.constants import *


class Building(Entity):
    def __init__(self, name, pos, sprite, interaction={}):
        Entity.__init__(self, name, pos, sprite)
        self.interaction = interaction

    def interact(self, actor):
        entries = []

        if self.interaction == {}:
            entries.append([{'type': 'text', 'text': 'This house seems closed...', 'font': ITEM_DESC_FONT}])
        else:
            for talk in self.interaction['talks']:
                entries.append([{'type': 'text', 'text': talk, 'font': ITEM_DESC_FONT}])
            if self.interaction['gold'] > 0:
                actor.set_gold(actor.get_gold() + self.interaction['gold'])
                earn_text = '[You received ' + str(self.interaction['gold']) + ' gold]'
                entries.append([{'type': 'text', 'text': earn_text, 'font': ITEM_DESC_FONT, 'color': GREEN}])
            if self.interaction['item'] is not None:
                actor.set_item(self.interaction['item'])
                earn_text = '[You received ' + self.interaction['item'].get_formatted_name() + ']'
                entries.append([{'type': 'text', 'text': earn_text, 'font': ITEM_DESC_FONT, 'color': GREEN}])

            # Interaction could not been repeted : should be remove after been used
            self.remove_interaction()

        return entries

    def remove_interaction(self):
        self.interaction = {}

    def save(self):
        tree = Entity.save(self)

        # Save state
        state = etree.SubElement(tree, 'state')
        state.text = str(self.interaction == {})

        return tree
