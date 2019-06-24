import pygame as pg

from src.Character import Character
from src.Movable import Movable
from src.Breakable import Breakable


MENU_TITLE_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 26)
ITEM_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 18)
MISSION_FONT = pg.font.Font('fonts/_bitmap_font____romulus_by_pix3m-d6aokem.ttf', 20)
ITALIC_ITEM_FONT = pg.font.Font('fonts/minya_nouvelle_it.ttf', 14)

TILE_SIZE = 48

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
YELLOW = (143, 143, 5)
BROWN = (139, 69, 19)
MAROON = (128, 0, 0)
BROWN_RED = (165, 42, 42)
GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
MIDNIGHT_BLUE = (25, 25, 112)

CRACKED_SPRITE = "imgs/dungeon_crawl/dungeon/wall/destroyed_wall.png"
CRACKED = pg.transform.scale(pg.image.load(CRACKED_SPRITE).convert_alpha(), (TILE_SIZE, TILE_SIZE))


FRAME_SPRITE = 'imgs/interface/frame.png'
FRAME = pg.transform.scale(pg.image.load(FRAME_SPRITE).convert_alpha(), (TILE_SIZE + 10, TILE_SIZE + 10))

class Sidebar():
    def __init__(self, size, pos, sprite, missions):
        self.size = size
        self.pos = pos
        self.sprite = pg.transform.scale(pg.image.load(sprite).convert_alpha(), size)
        self.missions = missions
        for mission in self.missions:
            if mission.is_main():
                self.main_mission = mission
                self.missions.remove(mission)
                break

    @staticmethod
    def determine_hp_color(hp, hp_max):
        if hp == hp_max:
            return BLACK
        if hp >= hp_max * 0.75:
            return GREEN
        if hp >= hp_max * 0.5:
            return YELLOW
        if hp >= hp_max * 0.30:
            return ORANGE
        else:
            return RED

    def display(self, win, nb_turn, ent):
        # Sidebar background
        win.blit(self.sprite, self.pos)

        # Turn indication
        turn_text = MENU_TITLE_FONT.render("TURN " + str(nb_turn), 1, BLACK)
        win.blit(turn_text, (self.pos[0] + 50, self.pos[1] + 15))

        # Missions
        main_mission_text = MENU_TITLE_FONT.render("MAIN MISSION", 1, BLACK)
        win.blit(main_mission_text, (self.pos[0] + self.size[0] - 250,
                                     self.pos[1] + 10))

        mission_color = GREEN if self.main_mission.is_ended else BROWN_RED
        main_mission_desc = MISSION_FONT.render("> " + self.main_mission.get_description(), 1, BROWN_RED)
        win.blit(main_mission_desc, (self.pos[0] + self.size[0] - 230,
                                     self.pos[1] + 10 + main_mission_text.get_height()))

        # Display the current informations about the entity hovered
        if ent:
            # Display the ent sprite in a frame
            frame_pos = (self.pos[0] + self.size[0] / 3, self.pos[1] + self.size[1] / 2 - FRAME.get_height() / 2)
            win.blit(FRAME, frame_pos)
            ent_pos = (frame_pos[0] + 5, frame_pos[1] + 5)
            win.blit(ent.get_sprite(), ent_pos)
            # If it is a character
            if isinstance(ent, Character):
                for equip in ent.get_equipments():
                    win.blit(equip.get_equipped_sprite(), ent_pos)
            # If it is a breakable
            elif isinstance(ent, Breakable):
                win.blit(CRACKED, ent_pos)

            # Display basic informations about the ent
            # Name
            text_pos_x = frame_pos[0] + FRAME.get_width() + 15
            name_pre_text = ITEM_FONT.render("NAME : ", 1, MIDNIGHT_BLUE)
            win.blit(name_pre_text, (text_pos_x, frame_pos[1]))
            name_text = ITEM_FONT.render("         " + ent.get_formatted_name(), 1, BLACK)
            win.blit(name_text, (text_pos_x, frame_pos[1]))

            # HP
            hp = ent.get_hp()
            hp_max = ent.get_hp_max()
            hp_pre_text = ITEM_FONT.render("HP : ", 1, MIDNIGHT_BLUE)
            hp_text_pos = (text_pos_x, frame_pos[1] + FRAME.get_height() - hp_pre_text.get_height())
            win.blit(hp_pre_text, hp_text_pos)
            hp_text = ITEM_FONT.render("      " + str(hp), 1, Sidebar.determine_hp_color(hp, hp_max))
            win.blit(hp_text, hp_text_pos)
            hp_post_text = ITEM_FONT.render("      " + " " * len(str(hp)) + " / " + str(hp_max), 1, BLACK)
            win.blit(hp_post_text, hp_text_pos)

            # Display more informations if it is a movable entity
            if isinstance(ent, Movable):
                # Level
                level_text = ITEM_FONT.render("LVL : " + str(ent.get_lvl()), 1, BLACK)
                lvl_text_pos_x = frame_pos[0] + FRAME.get_width() / 2 - level_text.get_width() / 2
                win.blit(level_text, (lvl_text_pos_x, frame_pos[1] + FRAME.get_height()))

                # Status
                status_pre_text = ITEM_FONT.render("ALTERATIONS : ", 1, MIDNIGHT_BLUE)
                win.blit(status_pre_text, (text_pos_x, frame_pos[1] + FRAME.get_height()))
                status_text = ITEM_FONT.render("                  " + ent.get_formatted_alterations(), 1, BLACK)
                win.blit(status_text, (text_pos_x, frame_pos[1] + FRAME.get_height()))

            # Display more informations if it is a character
            if isinstance(ent, Character):
                classes = ent.get_formatted_classes()
                classes_pre_text = ITEM_FONT.render("CLASS : ", 1, MIDNIGHT_BLUE)
                win.blit(classes_pre_text, (text_pos_x, frame_pos[1] + ITEM_FONT.get_height()))
                classes_text = ITEM_FONT.render("         " + classes, 1, BLACK)
                win.blit(classes_text, (text_pos_x, frame_pos[1] + ITEM_FONT.get_height()))
