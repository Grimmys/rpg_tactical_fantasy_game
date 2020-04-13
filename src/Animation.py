

class Animation:
    def __init__(self, sprites_pos, timer):
        self.sprites_pos = sprites_pos
        self.timer_max = timer
        self.timer = timer
        self.current_frame = self.sprites_pos.pop(0)

    def anim(self):
        self.timer -= 1
        if self.timer == 0:
            if self.sprites_pos:
                self.timer = self.timer_max
                self.current_frame = self.sprites_pos.pop(0)
            else:
                return True
        return False

    def display(self, win):
        win.blit(self.current_frame['sprite'], self.current_frame['pos'])
