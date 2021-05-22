import pygame

from src.constants import BLACK, YELLOW, ORANGE, RED, DARK_GREEN, BROWN_RED, MIDNIGHT_BLUE
from src.game_entities.foe import Foe
from src.gui.constant_sprites import constant_sprites
from src.gui.fonts import fonts
from src.game_entities.destroyable import Destroyable
from src.game_entities.player import Player
from src.game_entities.character import Character
from src.game_entities.movable import Movable
from src.game_entities.breakable import Breakable

SHIFT = 2
SIDEBAR_SPRITE = 'imgs/interface/sidebar.png'


class Sidebar:
    """

    """
    def __init__(self, size, pos, missions, nb_level):
        self.size = size
        self.pos = pos
        self.sprite = pygame.transform.scale(pygame.image.load(SIDEBAR_SPRITE).convert_alpha(),
                                             size)
        self.missions = missions
        self.nb_level = nb_level

    @staticmethod
    def determine_hp_color(hit_points, hit_points_max):
        """

        :param hit_points:
        :param hit_points_max:
        :return:
        """
        if hit_points == hit_points_max:
            return BLACK
        if hit_points >= hit_points_max * 0.75:
            return DARK_GREEN
        if hit_points >= hit_points_max * 0.5:
            return YELLOW
        if hit_points >= hit_points_max * 0.30:
            return ORANGE
        return RED

    def display(self, win, nb_turn, ent):
        """

        :param win:
        :param nb_turn:
        :param ent:
        """
        # Sidebar background
        win.blit(self.sprite, self.pos)

        # Turn indication
        turn_text = fonts['MENU_TITLE_FONT'].render("TURN " + str(nb_turn), 1, BLACK)
        win.blit(turn_text, (self.pos[0] + 50, self.pos[1] + 15))

        # Level indication
        turn_text = fonts['MENU_TITLE_FONT'].render("LEVEL " + str(self.nb_level), 1, BLACK)
        win.blit(turn_text, (self.pos[0] + 50, self.pos[1] + 50))

        # Main mission header
        win.blit(constant_sprites['main_mission_text'], (self.pos[0] + self.size[0] - 500,
                                                         self.pos[1] + 10))
        # Secondaries missions header if any
        if len(self.missions) > 1:
            win.blit(constant_sprites['secondaries_mission_text'],
                     (self.pos[0] + self.size[0] - 300,
                      self.pos[1] + 10))
        # Missions
        vertical_shift = 0
        for mission in self.missions:
            mission_color = DARK_GREEN if mission.ended else BROWN_RED
            mission_desc = fonts['MISSION_FONT'].render("> " + mission.description, 1, mission_color)
            if mission.main:
                win.blit(mission_desc, (self.pos[0] + self.size[0] - 480,
                                        self.pos[1] + 10 + constant_sprites[
                                            'main_mission_text'].get_height()))
            else:
                win.blit(mission_desc, (self.pos[0] + self.size[0] - 280,
                                        self.pos[1] + 10 + constant_sprites[
                                            'secondaries_mission_text'].get_height() +
                                        vertical_shift * mission_desc.get_height()))
                vertical_shift += 1

        # Display the current information about the entity hovered
        if ent:
            # Set up color depending of entity's nature
            if isinstance(ent, Foe):
                nature = 'FOE'
                color = RED
            elif isinstance(ent, Player):
                nature = 'PLAYER'
                color = MIDNIGHT_BLUE
            elif isinstance(ent, Character):
                nature = 'ALLY'
                color = DARK_GREEN
            else:
                nature = 'UNLIVING ENTITY'
                color = BLACK

            # Display the entity nature
            nature_display = fonts['MISSION_FONT'].render(nature, 1, color)
            nature_pos = (
                self.pos[0] + self.size[0] / 4 + constant_sprites[
                    'frame'].get_width() / 2 - nature_display.get_width() / 2,
                self.pos[1] + 5)
            win.blit(nature_display, nature_pos)
            # Display the entity sprite in a frame
            frame_pos = (
                self.pos[0] + self.size[0] / 4, self.pos[1] + 5 + nature_display.get_height())
            win.blit(constant_sprites['frame'], frame_pos)
            ent_pos = (frame_pos[0] + 5, frame_pos[1] + 5)
            win.blit(ent.sprite, ent_pos)
            # If it is a character
            if isinstance(ent, Character):
                for equip in ent.equipments:
                    win.blit(equip.equipped_sprite, ent_pos)
            # If it is a breakable
            elif isinstance(ent, Breakable):
                win.blit(constant_sprites['cracked'], ent_pos)

            # Display basic information about the ent
            # Name
            text_pos_x = frame_pos[0] + constant_sprites['frame'].get_width() + 15
            name_pre_text = fonts['ITEM_FONT_STRONG'].render("NAME : ", 1, color)
            win.blit(name_pre_text, (text_pos_x, frame_pos[1]))
            name_text = fonts['ITEM_FONT_STRONG'].render("         " + str(ent), 1, BLACK)
            win.blit(name_text, (text_pos_x, frame_pos[1]))

            # HP if it's a destroyable entity
            if isinstance(ent, Destroyable):
                hit_points = ent.hit_points
                hit_points_max = ent.hp_max
                hit_points_pre_text = fonts['ITEM_FONT_STRONG'].render("HP : ", 1, color)
                text_position = (
                    text_pos_x,
                    frame_pos[1] + constant_sprites['frame'].get_height()
                    - hit_points_pre_text.get_height())
                win.blit(hit_points_pre_text, text_position)
                hit_points_text = fonts['ITEM_FONT_STRONG'].render("      " + str(hit_points), 1,
                                                                   Sidebar.determine_hp_color(
                                                                       hit_points,
                                                                       hit_points_max))
                win.blit(hit_points_text, text_position)
                hp_post_text = fonts['ITEM_FONT_STRONG'].render(
                    f'      {" " * len(str(hit_points))} / {hit_points_max}',
                    1, BLACK)
                win.blit(hp_post_text, text_position)

                # Display more information if it is a movable entity
                if isinstance(ent, Movable):
                    # Level
                    level_text = fonts['ITEM_FONT_STRONG'].render("LVL : " + str(ent.lvl), 1, BLACK)
                    lvl_text_pos_x = frame_pos[0] + constant_sprites[
                        'frame'].get_width() / 2 - level_text.get_width() / 2
                    win.blit(level_text, (
                        lvl_text_pos_x, frame_pos[1] + constant_sprites['frame'].get_height()))

                    # Status
                    status_pre_text = fonts['ITEM_FONT_STRONG'].render("ALTERATIONS : ", 1, color)
                    win.blit(status_pre_text,
                             (text_pos_x, frame_pos[1] + constant_sprites['frame'].get_height()))
                    status_text = fonts['ITEM_FONT_STRONG'].render(
                        " " * 18 + ent.get_abbreviated_alterations(),
                        1, BLACK)
                    win.blit(status_text,
                             (text_pos_x, frame_pos[1] + constant_sprites['frame'].get_height()))

                    # Display more information if it is a character
                    if isinstance(ent, Character):
                        race = ent.get_formatted_race()
                        race_pre_text = fonts['ITEM_FONT_STRONG'].render("RACE : ", 1, color)
                        win.blit(race_pre_text,
                                 (text_pos_x, frame_pos[1] + (
                                         fonts['ITEM_FONT_STRONG'].get_height() - SHIFT) * 2))
                        race_text = fonts['ITEM_FONT_STRONG'].render("        " + race, 1, BLACK)
                        win.blit(race_text,
                                 (text_pos_x, frame_pos[1] + (
                                         fonts['ITEM_FONT_STRONG'].get_height() - SHIFT) * 2))

                        # Display more information if it is a player
                        if isinstance(ent, Player):
                            classes = ent.get_formatted_classes()
                            classes_pre_text = fonts['ITEM_FONT_STRONG'].render("CLASS : ", 1,
                                                                                color)
                            win.blit(classes_pre_text,
                                     (text_pos_x, frame_pos[1] + fonts[
                                         'ITEM_FONT_STRONG'].get_height() - SHIFT))
                            classes_text = fonts['ITEM_FONT_STRONG'].render("         " + classes,
                                                                            1, BLACK)
                            win.blit(classes_text,
                                     (text_pos_x, frame_pos[1] + fonts[
                                         'ITEM_FONT_STRONG'].get_height() - SHIFT))
