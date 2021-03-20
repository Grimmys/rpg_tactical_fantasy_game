from src.game_entities.item import Item

import pygame.mixer
import os


class Consumable(Item):
    def __init__(self, name, sprite, description, price, effects):
        Item.__init__(self, name, sprite, description, price)
        self.effects = effects

        self.drinksfx = pygame.mixer.Sound(os.path.join('sound_fx', 'potion.ogg'))

    def use(self, player):
        success = False
        msgs = []
        for eff in self.effects:
            sub_success, msg = eff.apply_on_ent(player)
            msgs.append(msg)
            if sub_success:
                success = True
        if success:
            pygame.mixer.Sound.play(self.drinksfx)
            player.remove_item(self)
        return success, msgs
