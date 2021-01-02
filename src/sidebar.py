from src.foe import Foe
from src.fonts import fonts
from src.destroyable import Destroyable
from src.player import Player
from src.character import Character
from src.movable import Movable
from src.breakable import Breakable
from src.constants import *

SHIFT = 2
SIDEBAR_SPRITE = 'imgs/interface/sidebar.png'
CRACKED = None
FRAME = None
MAIN_MISSION_TEXT = None
SECONDARIES_MISSION_TEXT = None


class Sidebar:
    @staticmethod
    def init_constant_sprites():
        global CRACKED, FRAME, MAIN_MISSION_TEXT, SECONDARIES_MISSION_TEXT
        cracked_sprite = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"
        CRACKED = pg.transform.scale(pg.image.load(cracked_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        frame_sprite = 'imgs/interface/frame.png'
        FRAME = pg.transform.scale(pg.image.load(frame_sprite).convert_alpha(), (TILE_SIZE + 10, TILE_SIZE + 10))
        MAIN_MISSION_TEXT = fonts['MENU_TITLE_FONT'].render("MAIN MISSION", 1, BLACK)
        SECONDARIES_MISSION_TEXT = fonts['MENU_TITLE_FONT'].render("OPTIONAL OBJECTIVES", 1, BLACK)

    def __init__(self, size, pos, missions):
        self.size = size
        self.pos = pos
        self.sprite = pg.transform.scale(pg.image.load(SIDEBAR_SPRITE).convert_alpha(), size)
        self.missions = missions

    @staticmethod
    def determine_hp_color(hp, hp_max):
        if hp == hp_max:
            return BLACK
        if hp >= hp_max * 0.75:
            return DARK_GREEN
        if hp >= hp_max * 0.5:
            return YELLOW
        if hp >= hp_max * 0.30:
            return ORANGE
        else:
            return RED

    def display(self, win, nb_turn, ent, nb_level):
        # Sidebar background
        win.blit(self.sprite, self.pos)

        # Turn indication
        turn_text = fonts['MENU_TITLE_FONT'].render("TURN " + str(nb_turn), 1, BLACK)
        win.blit(turn_text, (self.pos[0] + 50, self.pos[1] + 15))

        # Level indication
        turn_text = fonts['MENU_TITLE_FONT'].render("LEVEL " + str(nb_level), 1, BLACK)
        win.blit(turn_text, (self.pos[0] + 50, self.pos[1] + 50))

        # Main mission header
        win.blit(MAIN_MISSION_TEXT, (self.pos[0] + self.size[0] - 500,
                                     self.pos[1] + 10))
        # Secondaries missions header if any
        if len(self.missions) > 1:
            win.blit(SECONDARIES_MISSION_TEXT, (self.pos[0] + self.size[0] - 300,
                                                self.pos[1] + 10))
        # Missions
        vertical_shift = 0
        for mission in self.missions:
            mission_color = DARK_GREEN if mission.ended else BROWN_RED
            mission_desc = fonts['MISSION_FONT'].render("> " + mission.desc, 1, mission_color)
            if mission.main:
                win.blit(mission_desc, (self.pos[0] + self.size[0] - 480,
                                             self.pos[1] + 10 + MAIN_MISSION_TEXT.get_height()))
            else:
                win.blit(mission_desc, (self.pos[0] + self.size[0] - 280,
                                            self.pos[1] + 10 + SECONDARIES_MISSION_TEXT.get_height() + vertical_shift * mission_desc.get_height()))
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
            nature_pos = (self.pos[0] + self.size[0] / 4 + FRAME.get_width() / 2 - nature_display.get_width() / 2,
                          self.pos[1] + 5)
            win.blit(nature_display, nature_pos)
            # Display the entity sprite in a frame
            frame_pos = (self.pos[0] + self.size[0] / 4, self.pos[1] + 5 + nature_display.get_height())
            win.blit(FRAME, frame_pos)
            ent_pos = (frame_pos[0] + 5, frame_pos[1] + 5)
            win.blit(ent.sprite, ent_pos)
            # If it is a character
            if isinstance(ent, Character):
                for equip in ent.equipments:
                    win.blit(equip.equipped_sprite, ent_pos)
            # If it is a breakable
            elif isinstance(ent, Breakable):
                win.blit(CRACKED, ent_pos)

            # Display basic information about the ent
            # Name
            text_pos_x = frame_pos[0] + FRAME.get_width() + 15
            name_pre_text = fonts['ITEM_FONT_STRONG'].render("NAME : ", 1, color)
            win.blit(name_pre_text, (text_pos_x, frame_pos[1]))
            name_text = fonts['ITEM_FONT_STRONG'].render("         " + str(ent), 1, BLACK)
            win.blit(name_text, (text_pos_x, frame_pos[1]))

            # HP if it's a destroyable entity
            if isinstance(ent, Destroyable):
                hp = ent.hp
                hp_max = ent.hp_max
                hp_pre_text = fonts['ITEM_FONT_STRONG'].render("HP : ", 1, color)
                hp_text_pos = (text_pos_x, frame_pos[1] + FRAME.get_height() - hp_pre_text.get_height())
                win.blit(hp_pre_text, hp_text_pos)
                hp_text = fonts['ITEM_FONT_STRONG'].render("      " + str(hp), 1, Sidebar.determine_hp_color(hp, hp_max))
                win.blit(hp_text, hp_text_pos)
                hp_post_text = fonts['ITEM_FONT_STRONG'].render("      " + " " * len(str(hp)) + " / " + str(hp_max),
                                                                1, BLACK)
                win.blit(hp_post_text, hp_text_pos)

                # Display more information if it is a movable entity
                if isinstance(ent, Movable):
                    # Level
                    level_text = fonts['ITEM_FONT_STRONG'].render("LVL : " + str(ent.lvl), 1, BLACK)
                    lvl_text_pos_x = frame_pos[0] + FRAME.get_width() / 2 - level_text.get_width() / 2
                    win.blit(level_text, (lvl_text_pos_x, frame_pos[1] + FRAME.get_height()))

                    # Status
                    status_pre_text = fonts['ITEM_FONT_STRONG'].render("ALTERATIONS : ", 1, color)
                    win.blit(status_pre_text, (text_pos_x, frame_pos[1] + FRAME.get_height()))
                    status_text = fonts['ITEM_FONT_STRONG'].render(" " * 18 + ent.get_abbreviated_alterations(),
                                                                   1, BLACK)
                    win.blit(status_text, (text_pos_x, frame_pos[1] + FRAME.get_height()))

                    # Display more information if it is a character
                    if isinstance(ent, Character):
                        race = ent.get_formatted_race()
                        race_pre_text = fonts['ITEM_FONT_STRONG'].render("RACE : ", 1, color)
                        win.blit(race_pre_text,
                                 (text_pos_x, frame_pos[1] + (fonts['ITEM_FONT_STRONG'].get_height() - SHIFT) * 2))
                        race_text = fonts['ITEM_FONT_STRONG'].render("        " + race, 1, BLACK)
                        win.blit(race_text,
                                 (text_pos_x, frame_pos[1] + (fonts['ITEM_FONT_STRONG'].get_height() - SHIFT) * 2))

                        # Display more information if it is a player
                        if isinstance(ent, Player):
                            classes = ent.get_formatted_classes()
                            classes_pre_text = fonts['ITEM_FONT_STRONG'].render("CLASS : ", 1, color)
                            win.blit(classes_pre_text,
                                     (text_pos_x, frame_pos[1] + fonts['ITEM_FONT_STRONG'].get_height() - SHIFT))
                            classes_text = fonts['ITEM_FONT_STRONG'].render("         " + classes, 1, BLACK)
                            win.blit(classes_text, (text_pos_x, frame_pos[1] + fonts['ITEM_FONT_STRONG'].get_height() - SHIFT))
