from lxml import etree

from src.game_entities.entity import Entity
from src.constants import *
from src.gui.fonts import *

#beiba
import pygame.mixer
import os

class Building(Entity):
    def __init__(self, name, pos, sprite, interaction=None):
        Entity.__init__(self, name, pos, sprite)
        self.sprite_name = sprite
        self.interaction = interaction

        pg.mixer.init()
        self.doorsfx = pg.mixer.Sound(os.path.join('sound_fx', 'door.ogg'))
        self.goldsfx = pg.mixer.Sound(os.path.join('sound_fx', 'trade.ogg'))
        self.talksfx = pg.mixer.Sound(os.path.join('sound_fx', 'talking.ogg'))
        self.invsfx = pg.mixer.Sound(os.path.join('sound_fx', 'inventory.ogg'))

    def interact(self, actor):
        entries = []

        if not self.interaction:
            pygame.mixer.Sound.play(self.doorsfx)
            entries.append([{'type': 'text', 'text': 'This house seems closed...', 'font': fonts['ITEM_DESC_FONT']}])
        else:
            for talk in self.interaction['talks']:
                pygame.mixer.Sound.play(self.talksfx)
                entries.append([{'type': 'text', 'text': talk, 'font': fonts['ITEM_DESC_FONT']}])
            if self.interaction['gold'] > 0:
                pygame.mixer.Sound.play(self.goldsfx)
                actor.gold += self.interaction['gold']
                earn_text = '[You received ' + str(self.interaction['gold']) + ' gold]'
                entries.append([{'type': 'text', 'text': earn_text, 'font': fonts['ITEM_DESC_FONT'], 'color': GREEN}])
            if self.interaction['item'] is not None:
                pygame.mixer.Sound.play(self.invsfx)
                actor.set_item(self.interaction['item'])
                earn_text = '[You received ' + str(self.interaction['item']) + ']'
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
        if self.interaction:
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
