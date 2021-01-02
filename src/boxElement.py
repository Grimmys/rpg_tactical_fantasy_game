import pygame as pg


class BoxElement:
    def __init__(self, pos, content, margin=(0, 0, 0, 0)):
        self.pos = pos
        self.content = content
        if self.content:
            self.size = (self.content.get_width(), self.content.get_height())
        else:
            self.size = (0, 0)
        self.margin = {'TOP': margin[0], 'BOTTOM': margin[2], 'LEFT': margin[3], 'RIGHT': margin[1]}

    def get_width(self):
        return self.margin['LEFT'] + self.size[0] + self.margin['RIGHT']

    def get_height(self):
        return self.margin['TOP'] + self.size[1] + self.margin['BOTTOM']

    def get_margin_top(self):
        return self.margin['TOP']

    def get_margin_bottom(self):
        return self.margin['BOTTOM']

    def get_margin_left(self):
        return self.margin['LEFT']

    def get_margin_right(self):
        return self.margin['RIGHT']

    def get_rect(self):
        return pg.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def display(self, win):
        win.blit(self.content, (self.pos[0] + self.margin['LEFT'], self.pos[1]))
