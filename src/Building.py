from lxml import etree

from src.Entity import Entity
from src.constants import *
from src.fonts import *


class Building(Entity):
    def __init__(self, name, pos, sprite, interaction=None):
        Entity.__init__(self, name, pos, sprite)
        self.sprite_name = sprite
        self.interaction = interaction

    def interact(self, actor):
        entries = []

        if not self.interaction:
            entries.append([{'type': 'text', 'text': 'This house seems closed...', 'font': fonts['ITEM_DESC_FONT']}])
        else:
            for talk in self.interaction['talks']:
                entries.append([{'type': 'text', 'text': talk, 'font': fonts['ITEM_DESC_FONT']}])
            if self.interaction['gold'] > 0:
                actor.gold += self.interaction['gold']
                earn_text = '[You received ' + str(self.interaction['gold']) + ' gold]'
                entries.append([{'type': 'text', 'text': earn_text, 'font': fonts['ITEM_DESC_FONT'], 'color': GREEN}])
            if self.interaction['item'] is not None:
                actor.set_item(self.interaction['item'])
                earn_text = '[You received ' + self.interaction['item'].get_formatted_name() + ']'
                entries.append([{'type': 'text', 'text': earn_text, 'font': fonts['ITEM_DESC_FONT'], 'color': GREEN}])

            # Interaction could not been repeated : should be remove after been used
            self.remove_interaction()

        return entries

    def remove_interaction(self):
        self.interaction = None

    def save(self, tree_name):
        tree = Entity.save(self, tree_name)

        # Save state
        state = etree.SubElement(tree, 'state')
        state.text = str(self.interaction is None)

        # Save sprite
        sprite = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_name

        # Save interaction
        if not self.interaction:
            etree.SubElement(tree, 'uninteractable')
        else:
            interaction = etree.SubElement(tree, 'interaction')
            talks = etree.SubElement(interaction, 'talks')
            for t in self.interaction['talks']:
                talk = etree.SubElement(talks, 'talk')
                talk.text = t
            if self.interaction['gold'] > 0:
                gold = etree.SubElement(interaction, 'gold')
                gold.text = str(self.interaction['gold'])
            if self.interaction['item'] is not None:
                item = etree.SubElement(interaction, 'item')
                item.text = self.interaction['item'].name

        return tree
