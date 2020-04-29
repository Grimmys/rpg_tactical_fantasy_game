from src.BoxElement import BoxElement


class Button(BoxElement):
    def __init__(self, method_id, args, size, pos, sprite, sprite_hover, margin, linked_object=None):
        BoxElement.__init__(self, pos, None, margin)

        self.size = size
        self.method_id = method_id
        self.args = args
        self.sprite = sprite
        self.sprite_hover = sprite_hover
        self.content = self.sprite
        self.linked_object = linked_object

    def set_hover(self, hover):
        self.content = self.sprite_hover if hover else self.sprite

    def action_triggered(self):
        return self.method_id, (self.pos, self.linked_object, self.args)
