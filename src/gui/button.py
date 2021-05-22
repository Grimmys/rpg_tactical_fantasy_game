from src.gui.box_element import BoxElement


class Button(BoxElement):
    """

    """
    def __init__(self, method_id, args, size, position, sprite, sprite_hover, margin, linked_object=None):
        BoxElement.__init__(self, position, None, margin)

        self.size = size
        self.method_id = method_id
        self.args = args
        self.sprite = sprite
        self.sprite_hover = sprite_hover
        self.content = self.sprite
        self.linked_object = linked_object

    def set_hover(self, hover):
        """

        :param hover:
        """
        self.content = self.sprite_hover if hover else self.sprite

    def action_triggered(self):
        """

        :return:
        """
        return self.method_id, (self.position, self.linked_object, self.args)
