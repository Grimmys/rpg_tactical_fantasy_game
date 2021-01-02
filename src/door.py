from lxml import etree

from src.entity import Entity


class Door(Entity):
    def __init__(self, pos, sprite, pick_lock_initiated):
        Entity.__init__(self, "Door", pos, sprite)
        self.sprite_name = sprite
        self.pick_lock_initiated = pick_lock_initiated

    def save(self, tree_name):
        tree = Entity.save(self, tree_name)

        # Save sprite
        sprite = etree.SubElement(tree, 'sprite')
        sprite.text = self.sprite_name

        # Save if pick lock has been initiated
        if self.pick_lock_initiated:
            etree.SubElement(tree, 'pick_lock_initiated')

        return tree
