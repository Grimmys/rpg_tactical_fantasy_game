from lxml import etree

from src.game_entities.entity import Entity


class Door(Entity):
    """

    """
    def __init__(self, position: tuple[int, int], sprite: str, pick_lock_initiated: bool) -> None:
        Entity.__init__(self, "Door", position, sprite)
        self.sprite_name: str = sprite
        self.pick_lock_initiated: bool = pick_lock_initiated

    def save(self, tree_name: str) -> etree.Element:
        """

        :param tree_name:
        :return:
        """
        tree: etree.Element = Entity.save(self, tree_name)

        # Save sprite
        sprite: etree.SubElement = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_name

        # Save if pick lock has been initiated
        if self.pick_lock_initiated:
            etree.SubElement(tree, 'pick_lock_initiated')

        return tree
