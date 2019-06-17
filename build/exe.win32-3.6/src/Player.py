import pygame as pg

from src.Character import Character

TILE_SIZE = 48
SELECTED_SPRITE = 'imgs/dungeon_crawl/misc/cursor.png'
SELECTED_DISPLAY = pg.transform.scale(pg.image.load(SELECTED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))

class Player(Character):
    def __init__(self, name, pos, sprite, hp, defense, res, max_move, strength, classes, equipments, lvl=1):
        Character.__init__(self, name, pos, sprite, hp, defense, res, max_move, strength, classes, equipments, lvl)
        '''Possible states :
        - 0 : Waiting to be selected
        - 1 : Waiting to be moved
        - 2 : On move
        - 3 : Waiting an action post-move
        - 4 : Waiting a target selected to attack OR waiting an target to interact with
        - 5 : Turn finished'''
        self.state = 0
        self.last_state = 5
        self.selected = False

    def display(self, screen):
        Character.display(self, screen)
        if self.state in range(1, 4):
            screen.blit(SELECTED_DISPLAY, self.pos)

    def set_selected(self, is_selected):
        self.selected = is_selected
        self.state = 1 if is_selected else 0

    def get_state(self):
        return self.state

    def set_move(self, pos):
        Character.set_move(self, pos)
        self.state = 2

    def move(self):
        Character.move(self)
        if not self.on_move:
            self.state = 3

    def attack(self, ent):
        damages = Character.attack(self, ent)
        self.state = self.last_state
        return damages

    def turn_finished(self):
        if self.state < 3:
            print("Error ! Player could not had finished his turn now")
        self.state = self.last_state
        self.selected = False

    def turn_is_finished(self):
        return self.state == self.last_state

    def choose_target(self):
        self.state = 4

    def choose_interaction(self):
        self.state = 4