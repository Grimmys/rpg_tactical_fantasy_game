"""
Defines Sidebar class, an element of the GUI that will be display permanently
at the bottom of the screen.
"""
from collections.abc import Sequence

import pygame

from src.constants import BLACK, BROWN_RED, DARK_GREEN, MIDNIGHT_BLUE, RED
from src.game_entities.breakable import Breakable
from src.game_entities.character import Character
from src.game_entities.destroyable import Destroyable
from src.game_entities.entity import Entity
from src.game_entities.foe import Foe
from src.game_entities.mission import Mission
from src.game_entities.movable import Movable
from src.game_entities.player import Player
from src.gui.constant_sprites import constant_sprites
from src.gui.fonts import fonts
from src.gui.position import Position
from src.gui.tools import determine_gauge_color
from src.services.language import *

SHIFT = 2
SIDEBAR_SPRITE = "imgs/interface/sidebar.png"


class Sidebar:
    """
    This class is representing a Sidebar that could be used to display different information about
    the ongoing game.

    Unlike other interfaces, this interface should be permanently displayed
    and not disturb the progress of the game.

    Keyword arguments:
    size -- the size of the sidebar
    position -- the position of the sidebar on the screen
    missions -- the list of missions that should be accomplished by the players
    level_id -- id of the current level

    Attributes:
    size -- the size of the sidebar
    position -- the position of the sidebar on the screen
    sprite -- the pygame Surface representing the background of the sidebar
    missions -- the list of missions that should be accomplished by the players
    level_id -- id of the current level
    """

    def __init__(
        self,
        size: tuple[int, int],
        position: Position,
        missions: Sequence[Mission],
        level_id: int,
    ) -> None:
        self.size: tuple[int, int] = size
        self.position: Position = position
        self.sprite: pygame.Surface = pygame.transform.scale(
            pygame.image.load(SIDEBAR_SPRITE).convert_alpha(), size
        )
        self.missions: Sequence[Mission] = missions
        self.level_id: int = level_id

    def display(
        self, screen: pygame.Surface, number_turns: int, hovered_entity: Entity
    ) -> None:
        """
        Display the sidebar and all the expected information on the screen provided.

        Keyword arguments:
        screen -- the screen on which the elements should be displayed
        number_turns -- the current turn of the ongoing level
        hovered_entity -- the currently hovered entity if there is any
        """
        # Sidebar background
        screen.blit(self.sprite, self.position)

        # Turn indication
        turn_text: pygame.Surface = fonts["MENU_TITLE_FONT"].render(
            f_TURN_NUMBER_SIDEBAR(number_turns), True, BLACK
        )
        screen.blit(turn_text, (self.position[0] + 50, self.position[1] + 15))

        # Level indication
        turn_text: pygame.Surface = fonts["MENU_TITLE_FONT"].render(
            f_LEVEL_NUMBER_SIDEBAR(self.level_id), True, BLACK
        )
        screen.blit(turn_text, (self.position[0] + 50, self.position[1] + 50))

        # Main mission header
        screen.blit(
            constant_sprites["main_mission_text"],
            (self.position[0] + self.size[0] - 500, self.position[1] + 10),
        )
        # Secondaries missions header if any
        if len(self.missions) > 1:
            screen.blit(
                constant_sprites["secondaries_mission_text"],
                (self.position[0] + self.size[0] - 300, self.position[1] + 10),
            )
        # Missions
        vertical_shift: int = 0
        for mission in self.missions:
            mission_color = DARK_GREEN if mission.ended else BROWN_RED
            mission_description = fonts["MISSION_FONT"].render(
                f"> {mission.description}", True, mission_color
            )
            if mission.main:
                screen.blit(
                    mission_description,
                    (
                        self.position[0] + self.size[0] - 480,
                        self.position[1]
                        + 10
                        + constant_sprites["main_mission_text"].get_height(),
                    ),
                )
            else:
                screen.blit(
                    mission_description,
                    (
                        self.position[0] + self.size[0] - 280,
                        self.position[1]
                        + 10
                        + constant_sprites["secondaries_mission_text"].get_height()
                        + vertical_shift * mission_description.get_height(),
                    ),
                )
                vertical_shift += 1

        # Display the current information about the entity hovered
        if hovered_entity:
            # Set up color depending on entity's nature
            if isinstance(hovered_entity, Foe):
                nature: str = STR_FOE
                color: pygame.Color = RED
            elif isinstance(hovered_entity, Player):
                nature = STR_PLAYER
                color = MIDNIGHT_BLUE
            elif isinstance(hovered_entity, Character):
                nature = STR_ALLY
                color = DARK_GREEN
            else:
                nature = STR_UNLIVING_ENTITY
                color = BLACK

            # Display the entity nature
            nature_display: pygame.Surface = fonts["MISSION_FONT"].render(
                nature, True, color
            )
            nature_position: Position = (
                self.position[0]
                + self.size[0] / 4
                + constant_sprites["frame"].get_width() / 2
                - nature_display.get_width() / 2,
                self.position[1] + 5,
            )
            screen.blit(nature_display, nature_position)
            # Display the entity sprite in a frame
            frame_position: Position = (
                self.position[0] + self.size[0] // 4,
                self.position[1] + 5 + nature_display.get_height(),
            )
            screen.blit(constant_sprites["frame"], frame_position)
            entity_position: Position = (frame_position[0] + 5, frame_position[1] + 5)
            screen.blit(hovered_entity.sprite, entity_position)
            # If it is a character
            if isinstance(hovered_entity, Character):
                for equip in hovered_entity.equipments:
                    screen.blit(equip.equipped_sprite, entity_position)
            # If it is a breakable
            elif isinstance(hovered_entity, Breakable):
                screen.blit(constant_sprites["cracked"], entity_position)

            # Display basic information about the entity
            # Name
            text_position_x: int = (
                frame_position[0] + constant_sprites["frame"].get_width() + 15
            )
            name_pre_text: pygame.Surface = fonts["ITEM_FONT_STRONG"].render(
                STR_NAME_SIDEBAR_, True, color
            )
            screen.blit(name_pre_text, (text_position_x, frame_position[1]))
            name_text: pygame.Surface = fonts["ITEM_FONT_STRONG"].render(
                f"         {hovered_entity}", True, BLACK
            )
            screen.blit(name_text, (text_position_x, frame_position[1]))

            # HP if it's a destroyable entity
            if isinstance(hovered_entity, Destroyable):
                hit_points: int = hovered_entity.hit_points
                hit_points_max: int = hovered_entity.hit_points_max
                hit_points_pre_text: pygame.Surface = fonts["ITEM_FONT_STRONG"].render(
                    STR_HP_, True, color
                )
                text_position: Position = (
                    text_position_x,
                    frame_position[1]
                    + constant_sprites["frame"].get_height()
                    - hit_points_pre_text.get_height(),
                )
                screen.blit(hit_points_pre_text, text_position)
                hit_points_text: pygame.Surface = fonts["ITEM_FONT_STRONG"].render(
                    f"      {hit_points}",
                    True,
                    determine_gauge_color(hit_points, hit_points_max, BLACK),
                )
                screen.blit(hit_points_text, text_position)
                hp_post_text = fonts["ITEM_FONT_STRONG"].render(
                    f'      {" " * len(str(hit_points))} / {hit_points_max}',
                    True,
                    BLACK,
                )
                screen.blit(hp_post_text, text_position)

                # Display more information if it is a movable entity
                if isinstance(hovered_entity, Movable):
                    # Level
                    level_text: pygame.Surface = fonts["ITEM_FONT_STRONG"].render(
                        f"LVL : {hovered_entity.lvl}", True, BLACK
                    )
                    lvl_text_position_x: int = (
                        frame_position[0]
                        + constant_sprites["frame"].get_width() / 2
                        - level_text.get_width() / 2
                    )
                    screen.blit(
                        level_text,
                        (
                            lvl_text_position_x,
                            frame_position[1] + constant_sprites["frame"].get_height(),
                        ),
                    )

                    # Status
                    status_pre_text: pygame.Surface = fonts["ITEM_FONT_STRONG"].render(
                        STR_ALTERATIONS_, True, color
                    )
                    screen.blit(
                        status_pre_text,
                        (
                            text_position_x,
                            frame_position[1] + constant_sprites["frame"].get_height(),
                        ),
                    )
                    status_text = fonts["ITEM_FONT_STRONG"].render(
                        " " * 18 + hovered_entity.get_abbreviated_alterations(),
                        True,
                        BLACK,
                    )
                    screen.blit(
                        status_text,
                        (
                            text_position_x,
                            frame_position[1] + constant_sprites["frame"].get_height(),
                        ),
                    )

                    # Display more information if it is a character
                    if isinstance(hovered_entity, Character):
                        race: str = hovered_entity.get_formatted_race()
                        race_pre_text: pygame.Surface = fonts[
                            "ITEM_FONT_STRONG"
                        ].render(STR_RACE_, True, color)
                        screen.blit(
                            race_pre_text,
                            (
                                text_position_x,
                                frame_position[1]
                                + (fonts["ITEM_FONT_STRONG"].get_height() - SHIFT) * 2,
                            ),
                        )
                        race_text = fonts["ITEM_FONT_STRONG"].render(
                            f"        {race}", True, BLACK
                        )
                        screen.blit(
                            race_text,
                            (
                                text_position_x,
                                frame_position[1]
                                + (fonts["ITEM_FONT_STRONG"].get_height() - SHIFT) * 2,
                            ),
                        )

                        # Display more information if it is a player
                        if isinstance(hovered_entity, Player):
                            classes = hovered_entity.get_formatted_classes()
                            classes_pre_text = fonts["ITEM_FONT_STRONG"].render(
                                STR_CLASS_, True, color
                            )
                            screen.blit(
                                classes_pre_text,
                                (
                                    text_position_x,
                                    frame_position[1]
                                    + fonts["ITEM_FONT_STRONG"].get_height()
                                    - SHIFT,
                                ),
                            )
                            classes_text = fonts["ITEM_FONT_STRONG"].render(
                                "         " + classes, True, BLACK
                            )
                            screen.blit(
                                classes_text,
                                (
                                    text_position_x,
                                    frame_position[1]
                                    + fonts["ITEM_FONT_STRONG"].get_height()
                                    - SHIFT,
                                ),
                            )
