class Mission:
    def __init__(self, is_main, nature, positions, description, nb_players=1):
        self.main = is_main
        self.type = nature
        self.positions = positions
        self.desc = description
        self.ended = False

        self.restrictions = None
        if self.main:
            self.min_chars = nb_players
        self.succeeded_chars = []

    def is_main(self):
        return self.main

    def is_ended(self):
        return self.ended

    def get_description(self):
        return self.desc

    def get_type(self):
        return self.type

    def pos_is_valid(self, pos):
        return pos in self.positions

    def update_state(self, player=None):
        if self.type == 'position':
            self.succeeded_chars.append(player)
            if len(self.succeeded_chars) == self.min_chars:
                self.ended = True
        return True
