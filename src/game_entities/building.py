import os

import pygame
from lxml import etree

from src.constants import GREEN
from src.game_entities.entity import Entity
from src.gui.fonts import fonts


class Building(Entity):
    def __init__(self, name, position, sprite, interaction=None):
        Entity.__init__(self, name, position, sprite)
        self.sprite_name = sprite
        self.interaction = interaction

        self.door_sfx = pygame.mixer.Sound(os.path.join('sound_fx', 'door.ogg'))
        self.gold_sfx = pygame.mixer.Sound(os.path.join('sound_fx', 'trade.ogg'))
        self.talk_sfx = pygame.mixer.Sound(os.path.join('sound_fx', 'talking.ogg'))
        self.inventory_sfx = pygame.mixer.Sound(os.path.join('sound_fx', 'inventory.ogg'))

    def interact(self, actor):
        entries = []

        if not self.interaction:
            pygame.mixer.Sound.play(self.door_sfx)
            entries.append([{'type': 'text', 'text': 'This house seems closed...', 'font': fonts['ITEM_DESC_FONT']}])
        else:
            for talk in self.interaction['talks']:
                pygame.mixer.Sound.play(self.talk_sfx)
                entries.append([{'type': 'text', 'text': talk, 'font': fonts['ITEM_DESC_FONT']}])
            if self.interaction['gold'] > 0:
                pygame.mixer.Sound.play(self.gold_sfx)
                actor.gold += self.interaction['gold']
                earn_text = f'[You received {self.interaction["gold"]} gold]'
                entries.append([{'type': 'text', 'text': earn_text, 'font': fonts['ITEM_DESC_FONT'], 'color': GREEN}])
            if self.interaction['item'] is not None:
                pygame.mixer.Sound.play(self.inventory_sfx)
                actor.set_item(self.interaction['item'])
                earn_text = f'[You received {self.interaction["item"]}]'
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
