from lxml import etree

from src.game_entities.destroyable import Destroyable
from src.gui.constantSprites import constant_sprites


class Breakable(Destroyable):

    def __init__(self, pos, sprite, hp, defense, res):
        Destroyable.__init__(self, "Breakable", pos, sprite, hp, defense, res)
        # Useful in case of saving
        self.sprite_link = sprite

    def display(self, screen):
        Destroyable.display(self, screen)
        screen.blit(constant_sprites['cracked'], self.pos)

    def save(self, tree_name):
        tree = Destroyable.save(self, tree_name)

        # Save sprite
        sprite = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_link

        return tree
