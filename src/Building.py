
from src.Entity import Entity
from src.constants import *


class Building(Entity):
    def __init__(self, name, pos, sprite, interaction=None):
        Entity.__init__(self, name, pos, sprite)
        self.interaction = interaction

    def interact(self, actor):
        entries = []

        if self.interaction is None:
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

        return entries
