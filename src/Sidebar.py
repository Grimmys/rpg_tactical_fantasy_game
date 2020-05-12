from src.fonts import fonts
from src.Destroyable import Destroyable
from src.Player import Player
from src.Character import Character
from src.Movable import Movable
from src.Breakable import Breakable
from src.constants import *

SHIFT = 2
SIDEBAR_SPRITE = 'imgs/interface/sidebar.png'
CRACKED = None
FRAME = None


class Sidebar:
    @staticmethod
    def init_constant_sprites():
        global CRACKED, FRAME
        cracked_sprite = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"
        CRACKED = pg.transform.scale(pg.image.load(cracked_sprite).convert_alpha(), (TILE_SIZE, TILE_SIZE))
        frame_sprite = 'imgs/interface/frame.png'
        FRAME = pg.transform.scale(pg.image.load(frame_sprite).convert_alpha(), (TILE_SIZE + 10, TILE_SIZE + 10))

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

        # Missions
        for mission in self.missions:
            if mission.main:
                main_mission_text = fonts['MENU_TITLE_FONT'].render("MAIN MISSION", 1, BLACK)
                win.blit(main_mission_text, (self.pos[0] + self.size[0] - 250,
                                             self.pos[1] + 10))

                mission_color = DARK_GREEN if mission.ended else BROWN_RED
                main_mission_desc = fonts['MISSION_FONT'].render("> " + mission.desc, 1, mission_color)
                win.blit(main_mission_desc, (self.pos[0] + self.size[0] - 230,
                                             self.pos[1] + 10 + main_mission_text.get_height()))
            else:
                print("SECONDARY MISSION DISPLAY : TODO")

        # Display the current information about the entity hovered
        if ent:
            # Display the ent sprite in a frame
            frame_pos = (self.pos[0] + self.size[0] / 3, self.pos[1] + self.size[1] / 2 - FRAME.get_height() / 2)
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
            name_pre_text = fonts['ITEM_FONT_STRONG'].render("NAME : ", 1, MIDNIGHT_BLUE)
            win.blit(name_pre_text, (text_pos_x, frame_pos[1]))
            name_text = fonts['ITEM_FONT_STRONG'].render("         " + ent.get_formatted_name(), 1, BLACK)
            win.blit(name_text, (text_pos_x, frame_pos[1]))

            # HP if it's a destroyable entity
            if isinstance(ent, Destroyable):
                hp = ent.hp
                hp_max = ent.hp_max
                hp_pre_text = fonts['ITEM_FONT_STRONG'].render("HP : ", 1, MIDNIGHT_BLUE)
                hp_text_pos = (text_pos_x, frame_pos[1] + FRAME.get_height() - hp_pre_text.get_height())
                win.blit(hp_pre_text, hp_text_pos)
                hp_text = fonts['ITEM_FONT_STRONG'].render("      " + str(hp), 1, Sidebar.determine_hp_color(hp, hp_max))
                win.blit(hp_text, hp_text_pos)
                hp_post_text = fonts['ITEM_FONT_STRONG'].render("      " + " " * len(str(hp)) + " / " + str(hp_max), 1, BLACK)
                win.blit(hp_post_text, hp_text_pos)

                # Display more information if it is a movable entity
                if isinstance(ent, Movable):
                    # Level
                    level_text = fonts['ITEM_FONT_STRONG'].render("LVL : " + str(ent.lvl), 1, BLACK)
                    lvl_text_pos_x = frame_pos[0] + FRAME.get_width() / 2 - level_text.get_width() / 2
                    win.blit(level_text, (lvl_text_pos_x, frame_pos[1] + FRAME.get_height()))

                    # Status
                    status_pre_text = fonts['ITEM_FONT_STRONG'].render("ALTERATIONS : ", 1, MIDNIGHT_BLUE)
                    win.blit(status_pre_text, (text_pos_x, frame_pos[1] + FRAME.get_height()))
                    status_text = fonts['ITEM_FONT_STRONG'].render("                  " + ent.get_formatted_alterations(),
                                                          1, BLACK)
                    win.blit(status_text, (text_pos_x, frame_pos[1] + FRAME.get_height()))

                    # Display more information if it is a character
                    if isinstance(ent, Character):
                        race = ent.get_formatted_race()
                        race_pre_text = fonts['ITEM_FONT_STRONG'].render("RACE : ", 1, MIDNIGHT_BLUE)
                        win.blit(race_pre_text,
                                 (text_pos_x, frame_pos[1] + (fonts['ITEM_FONT_STRONG'].get_height() - SHIFT) * 2))
                        race_text = fonts['ITEM_FONT_STRONG'].render("        " + race, 1, BLACK)
                        win.blit(race_text, (text_pos_x, frame_pos[1] + (fonts['ITEM_FONT_STRONG'].get_height() - SHIFT) * 2))

                        # Display more information if it is a player
                        if isinstance(ent, Player):
                            classes = ent.get_formatted_classes()
                            classes_pre_text = fonts['ITEM_FONT_STRONG'].render("CLASS : ", 1, MIDNIGHT_BLUE)
                            win.blit(classes_pre_text,
                                     (text_pos_x, frame_pos[1] + fonts['ITEM_FONT_STRONG'].get_height() - SHIFT))
                            classes_text = fonts['ITEM_FONT_STRONG'].render("         " + classes, 1, BLACK)
                            win.blit(classes_text, (text_pos_x, frame_pos[1] + fonts['ITEM_FONT_STRONG'].get_height() - SHIFT))
