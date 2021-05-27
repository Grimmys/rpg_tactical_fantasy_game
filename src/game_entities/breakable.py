import pygame
from lxml import etree

from src.game_entities.destroyable import Destroyable
from src.gui.constant_sprites import constant_sprites


class Breakable(Destroyable):
    """

    """
    def __init__(self, position: tuple[int, int], sprite: str,
                 hit_points: int, defense: int, resistance: int) -> None:
        super().__init__("Breakable", position, sprite, hit_points, defense, resistance)
        # Useful in case of saving
        self.sprite_link: str = sprite

    def display(self, screen: pygame.Surface) -> None:
        """

        :param screen:
        """
        Destroyable.display(self, screen)
        screen.blit(constant_sprites['cracked'], self.position)

    def save(self, tree_name: str) -> etree.Element:
        """
        Save the current state of the breakable entity in XML format.

        Return the result of this generation.

        Keyword arguments:
        tree_name -- the name that should be given to the root element of the generated XML.
        """
        tree: etree.Element = super().save(tree_name)

        # Save sprite
        sprite: etree.SubElement = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_link

        return tree
