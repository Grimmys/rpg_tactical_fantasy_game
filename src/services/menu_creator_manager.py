"""
Define functions creating a specific menu enveloping data from parameters.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Optional, Union

import pygame
from pygamepopup.components import (BoxElement, Button, DynamicButton, InfoBox,
                                    TextElement)
from pygamepopup.components.image_button import ImageButton

from src.constants import (ACTION_MENU_WIDTH, ANIMATION_SPEED,
                           BATTLE_SUMMARY_WIDTH, BLACK, DARK_GREEN,
                           DIALOG_WIDTH, EQUIPMENT_MENU_WIDTH,
                           FOE_STATUS_MENU_WIDTH, GOLD, GREEN,
                           ITEM_BUTTON_SIZE, ITEM_INFO_MENU_WIDTH,
                           ITEM_MENU_WIDTH, ORANGE, REWARD_MENU_WIDTH,
                           SAVE_SLOTS, SCREEN_SIZE, START_MENU_WIDTH,
                           STATUS_INFO_MENU_WIDTH, STATUS_MENU_WIDTH,
                           TILE_SIZE, TRADE_ITEM_BUTTON_SIZE, TRADE_MENU_WIDTH,
                           TURQUOISE, WHITE)
from src.game_entities.alteration import Alteration
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.consumable import Consumable
from src.game_entities.door import Door
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Foe
from src.game_entities.fountain import Fountain
from src.game_entities.item import Item
from src.game_entities.mission import Mission, MissionType
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.shield import Shield
from src.game_entities.skill import Skill
from src.game_entities.weapon import Weapon
from src.gui.fonts import fonts
from src.gui.position import Position
from src.gui.tools import determine_gauge_color
from src.services.language import *

MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10
INVENTORY_MENU_ID = "inventory"
SHOP_MENU_ID = "shop"
CHARACTER_ACTION_MENU_ID = "character_action"

close_function: Optional[Callable] = None


def create_shop_menu(
        interaction_callback: Callable,
        stock: Sequence[dict[str, Union[Item, int]]],
        gold: int,
        shop_balance: int) -> InfoBox:
    """
    Return the interface of a shop menu with user as the buyer.

    Keyword arguments:
    stock -- the collection of items that are available in the shop, with the quantity of each one
    gold -- the amount of gold that should be displayed at the bottom
    shop_balance -- the shopkeeper's gold, displayed at the bottom
    """
    element_grid = []
    row = []
    for item in stock:
        item_text_data = [
            f_PRICE_NUMBER(item["item"].price),
            f_QUANTITY_NUMBER(item["quantity"]),
        ]
        item_button = ImageButton(
            image_path=item["item"].sprite_path,
            title=str(item["item"]),
            size=ITEM_BUTTON_SIZE,
            frame_background_path="imgs/interface/blue_frame.png",
            frame_background_hover_path="imgs/interface/blue_frame.png",
            background_path="imgs/interface/item_frame.png",
            text_color=BLACK,
            complementary_text_lines=item_text_data,
        )
        item_button.callback = lambda button=item_button, item_reference=item[
            "item"
        ]: interaction_callback(item_reference, button)
        row.append(item_button)
        if len(row) == 2:
            element_grid.append(row)
            row = []

    if row:
        element_grid.append(row)

    # Gold at end
    player_gold_line = [TextElement(f_UR_GOLD(gold), font=fonts["ITEM_DESC_FONT"])]
    element_grid.append(player_gold_line)
    shop_gold_line = [TextElement(f_SHOP_GOLD(shop_balance), font=fonts["ITEM_DESC_FONT"])]
    element_grid.append(shop_gold_line)

    return InfoBox(
        STR_SHOP_BUYING,
        element_grid,
        width=ITEM_MENU_WIDTH,
        title_color=ORANGE,
        identifier=SHOP_MENU_ID,
    )


def create_inventory_menu(
        interaction_callback: Callable,
        items: Sequence[Item],
        gold: int,
        is_to_sell: bool = False,
) -> InfoBox:
    """
    Return the interface of a player inventory.

    Keyword arguments:
    items -- the collection of items of the player in order
    gold -- the amount of gold of the player
    is_to_sell -- a boolean value indicating if this interface should be for potentially sell items
    to the active shop or if it's only for looking at them
    """
    grid_elements = []
    row = []
    for item in items:
        additional_lines = []
        # Test if price should appear
        if is_to_sell and item:
            additional_lines.append(f_PRICE_NUMBER(item.resell_price))
        item_button = ImageButton(
            image_path=item.sprite_path if item else None,
            title=str(item) if item else "",
            size=ITEM_BUTTON_SIZE,
            disabled=not item,
            frame_background_path="imgs/interface/blue_frame.png",
            frame_background_hover_path="imgs/interface/blue_frame.png",
            background_path="imgs/interface/item_frame.png",
            text_color=BLACK,
            complementary_text_lines=additional_lines,
        )
        if is_to_sell:
            item_button.callback = (
                lambda button=item_button, item_reference=item: interaction_callback(
                    item_reference, button
                )
            )
        else:
            item_button.callback = (
                lambda button=item_button, item_reference=item: interaction_callback(
                    item_reference, button, is_equipped=False
                )
            )

        row.append(item_button)
        if len(row) == 2:
            grid_elements.append(row)
            row = []
    if row:
        grid_elements.append(row)

    # Gold at end
    gold_text = [TextElement(text=f_UR_GOLD(gold), font=fonts["ITEM_DESC_FONT"])]
    grid_elements.append(gold_text)

    if is_to_sell:
        title = STR_SHOPPING_SELLING
        title_color = ORANGE
        identifier = SHOP_MENU_ID
    else:
        title = STR_INVENTORY
        title_color = WHITE
        identifier = INVENTORY_MENU_ID
    return InfoBox(
        title,
        grid_elements,
        width=ITEM_MENU_WIDTH,
        title_color=title_color,
        identifier=identifier,
    )


def create_equipment_menu(
        interaction_callback: Callable, equipments: Sequence[Equipment]
) -> InfoBox:
    """
    Return the interface of a player equipment.

    Keyword arguments:
    equipments -- the collection of equipments currently equipped by the player
    """
    grid_elements = []
    body_parts = [["head"], ["body"], ["right_hand", "left_hand"], ["feet"]]
    for part in body_parts:
        row = []
        for member in part:
            equipment = None
            for potential_equipment in equipments:
                if member == potential_equipment.body_part:
                    equipment = potential_equipment
                    break
            element = ImageButton(
                image_path=equipment.sprite_path if equipment else None,
                title=str(equipment) if equipment else "",
                size=ITEM_BUTTON_SIZE,
                disabled=not equipment,
                frame_background_path="imgs/interface/blue_frame.png",
                frame_background_hover_path="imgs/interface/blue_frame.png",
                background_path="imgs/interface/item_frame.png",
                text_color=BLACK,
            )
            element.callback = lambda equipment_reference=equipment, button_linked=element: interaction_callback(
                equipment_reference, button_linked, is_equipped=True
            )
            row.append(element)
        grid_elements.append(row)
    return InfoBox(
        STR_EQUIPMENT,
        grid_elements,
        width=EQUIPMENT_MENU_WIDTH,
    )


def create_trade_menu(
        buttons_callback: dict[str, Callable], first_player: Player, second_player: Player
) -> InfoBox:
    """
    Return the interface for a trade between two players

    Keyword arguments:
    first_player -- the player who initiated the trade
    second_player -- the other player
    """
    # Extract data from players
    items_max = first_player.nb_items_max
    items_first = list(first_player.items)
    free_spaces = items_max - len(items_first)
    items_first += [None] * free_spaces

    items_max = first_player.nb_items_max
    items_second = list(second_player.items)
    free_spaces = items_max - len(items_second)
    items_second += [None] * free_spaces

    grid_elements = []
    # We assume that first player and second player items lists have the same size and are even
    for i in range(len(items_first) // 2):
        row = []
        for owner_i, items in enumerate([items_first, items_second]):
            for j in range(2):
                item_button = ImageButton(
                    image_path=items[i * 2 + j].sprite_path
                    if items[i * 2 + j]
                    else None,
                    title=str(items[i * 2 + j]) if items[i * 2 + j] else "",
                    size=TRADE_ITEM_BUTTON_SIZE,
                    disabled=not items[i * 2 + j],
                    frame_background_path="imgs/interface/blue_frame.png",
                    frame_background_hover_path="imgs/interface/blue_frame.png",
                    background_path="imgs/interface/item_frame.png",
                    text_color=BLACK,
                )
                item_button.callback = lambda button=item_button, item_reference=items[
                    i * 2 + j
                    ], owner=owner_i: buttons_callback["interact_item"](
                    item_reference,
                    button,
                    [first_player, second_player],
                    owner == 0,
                )
                row.append(item_button)
        grid_elements.append(row)

    # Buttons to trade gold
    trade_gold_row = [
        Button(
            title=STR_50G_TO_RIGHT,
            size=(90, 30),
            margin=(0, 0, 0, 0),
            font=fonts["ITEM_DESC_FONT"],
            callback=lambda: buttons_callback["send_gold"](
                first_player, second_player, True, 50
            ),
        ),
        Button(
            title=STR_200G_TO_RIGHT,
            size=(90, 30),
            margin=(0, 0, 0, 0),
            font=fonts["ITEM_DESC_FONT"],
            callback=lambda: buttons_callback["send_gold"](
                first_player, second_player, True, 200
            ),
        ),
        Button(
            title=STR_ALL_TO_RIGHT,
            size=(90, 30),
            margin=(0, 0, 0, 0),
            font=fonts["ITEM_DESC_FONT"],
            callback=lambda: buttons_callback["send_gold"](
                first_player, second_player, True, first_player.gold
            ),
        ),
        Button(
            title=STR_50G_TO_LEFT,
            size=(90, 30),
            margin=(0, 0, 0, 0),
            font=fonts["ITEM_DESC_FONT"],
            callback=lambda: buttons_callback["send_gold"](
                first_player, second_player, False, 50
            ),
        ),
        Button(
            title=STR_200G_TO_LEFT,
            size=(90, 30),
            margin=(0, 0, 0, 0),
            font=fonts["ITEM_DESC_FONT"],
            callback=lambda: buttons_callback["send_gold"](
                first_player, second_player, False, 200
            ),
        ),
        Button(
            title=STR_ALL_TO_LEFT,
            size=(90, 30),
            margin=(0, 0, 0, 0),
            font=fonts["ITEM_DESC_FONT"],
            callback=lambda: buttons_callback["send_gold"](
                first_player, second_player, False, second_player.gold
            ),
        ),
    ]
    grid_elements.append(trade_gold_row)

    # Gold at end
    gold_row = [
        TextElement(
            f_GOLD_AT_END(first_player, first_player.gold), font=fonts["ITEM_DESC_FONT"]
        ),
        TextElement(
            f_GOLD_AT_END(second_player, second_player.gold),
            font=fonts["ITEM_DESC_FONT"],
        ),
    ]
    grid_elements.append(gold_row)

    title = STR_TRADE
    title_color = WHITE
    return InfoBox(
        title,
        grid_elements,
        width=TRADE_MENU_WIDTH,
        has_vertical_separator=True,
        title_color=title_color,
    )


def create_status_menu(
        buttons_callback: dict[str, Callable], player: Player
) -> InfoBox:
    """
    Return the interface resuming the status of a player.

    Keyword arguments:
    player -- the concerned player
    """
    grid_elements = [
        [
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            TextElement(STR_NAME_, text_color=GREEN, font=fonts["ITALIC_ITEM_FONT"]),
            TextElement(str(player)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            TextElement(
                STR_SKILLS,
                text_color=DARK_GREEN,
                font=fonts["MENU_SUB_TITLE_FONT"],
                margin=(10, 0, 10, 0),
            ),
        ],
        [
            TextElement(STR_CLASS_, text_color=GREEN, font=fonts["ITALIC_ITEM_FONT"]),
            TextElement(player.get_formatted_classes()),
        ],
        [
            TextElement(STR_RACE_, text_color=GREEN, font=fonts["ITALIC_ITEM_FONT"]),
            TextElement(player.get_formatted_race()),
        ],
        [
            TextElement(STR_LEVEL_, text_color=GREEN, font=fonts["ITALIC_ITEM_FONT"]),
            TextElement(str(player.lvl)),
        ],
        [
            TextElement(STR_XP_, text_color=GOLD, font=fonts["ITALIC_ITEM_FONT"]),
            TextElement(f_DIV(player.experience, player.experience_to_lvl_up)),
        ],
        [
            TextElement(
                STR_STATS,
                text_color=DARK_GREEN,
                font=fonts["MENU_SUB_TITLE_FONT"],
                margin=(10, 0, 10, 0),
            ),
        ],
        [
            TextElement(STR_HP_, text_color=WHITE),
            TextElement(
                f_DIV(player.hit_points, player.hit_points_max),
                text_color=determine_gauge_color(
                    player.hit_points, player.hit_points_max, WHITE
                ),
            ),
        ],
        [
            TextElement(STR_MOVE_, text_color=WHITE),
            TextElement(
                str(player.max_moves) + player.get_formatted_stat_change("speed")
            ),
        ],
        [
            TextElement(STR_CONSTITUTION_, text_color=WHITE),
            TextElement(str(player.constitution)),
        ],
        [
            TextElement(STR_ATTACK_, text_color=WHITE),
            TextElement(
                str(player.strength) + player.get_formatted_stat_change("strength")
            ),
        ],
        [
            TextElement(STR_DEFENSE_, text_color=WHITE),
            TextElement(
                str(player.defense) + player.get_formatted_stat_change("defense")
            ),
        ],
        [
            TextElement(STR_MAGICAL_RES_, text_color=WHITE),
            TextElement(
                str(player.resistance) + player.get_formatted_stat_change("resistance")
            ),
        ],
        [
            TextElement(
                STR_ALTERATIONS,
                text_color=DARK_GREEN,
                font=fonts["MENU_SUB_TITLE_FONT"],
                margin=(10, 0, 10, 0),
            )
        ],
    ]

    if not player.alterations:
        grid_elements.append([TextElement(STR_NONE, text_color=WHITE)])
    for alteration in player.alterations:
        grid_elements.append(
            [
                Button(
                    title=str(alteration),
                    callback=lambda alteration_reference=alteration: buttons_callback[
                        "info_alteration"
                    ](alteration_reference),
                    no_background=True,
                    text_hover_color=TURQUOISE,
                ),
            ]
        )

    # Display skills
    line_index = 2
    for skill in player.skills:
        skill_displayed = Button(
            title=skill.formatted_name,
            margin=(0, 0, 0, 0),
            callback=lambda skill_reference=skill: buttons_callback["info_skill"](
                skill_reference
            ),
            no_background=True,
            text_hover_color=TURQUOISE,
        )
        grid_elements[line_index].append(skill_displayed)
        line_index += 1
    for j in range(line_index, len(grid_elements)):
        grid_elements[j].append(
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0))
        )

    return InfoBox(
        STR_STATUS,
        grid_elements,
        width=STATUS_MENU_WIDTH,
    )


def create_player_menu(
        buttons_callback: dict[str, Callable],
        player: Player,
        buildings: Sequence[Building],
        interactable_entities: Sequence[Entity],
        missions: Sequence[Mission],
        foes: Sequence[Foe],
) -> InfoBox:
    """
    Return the interface of a player menu.

    Keyword arguments:
    player -- the active player
    buildings -- the collection of buildings on the current level
    interactable_entities -- the collection of entities with which the player
    can interact on the current level
    missions -- the missions of the current level
    foes -- the foes that are still alive on the current level
    """
    grid_elements = [
        [Button(title=STR_INVENTORY, callback=buttons_callback["inventory"])],
        [Button(title=STR_EQUIPMENT, callback=buttons_callback["equipment"])],
        [Button(title=STR_STATUS, callback=buttons_callback["status"])],
        [Button(title=STR_WAIT, callback=buttons_callback["wait"])],
    ]

    # Options flags
    chest_option = False
    portal_option = False
    fountain_option = False
    talk_option = False
    trade_option = False
    pick_lock_option = False
    door_option = False

    case_pos = (player.position[0], player.position[1] - TILE_SIZE)
    if (0, 0) < case_pos < (MAP_WIDTH, MAP_HEIGHT):
        for building in buildings:
            if building.position == case_pos:
                grid_elements.insert(
                    0, [Button(title=STR_VISIT, callback=buttons_callback["visit"])]
                )
                break

    for entity in interactable_entities:
        if (
                abs(entity.position[0] - player.position[0])
                + abs(entity.position[1] - player.position[1])
                == TILE_SIZE
        ):
            if isinstance(entity, Player):
                if not trade_option:
                    grid_elements.insert(
                        0, [Button(title=STR_TRADE, callback=buttons_callback["trade"])]
                    )
                    trade_option = True
            elif isinstance(entity, Chest):
                if not entity.opened and not chest_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(
                                title=STR_OPEN_CHEST,
                                callback=buttons_callback["open_chest"],
                            )
                        ],
                    )
                    chest_option = True
                if "lock_picking" in player.skills and not pick_lock_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(
                                title=STR_PICK_LOCK,
                                callback=buttons_callback["pick_lock"],
                            )
                        ],
                    )
                    pick_lock_option = True
            elif isinstance(entity, Door):
                if not door_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(
                                title=STR_OPEN_DOOR,
                                callback=buttons_callback["open_door"],
                            )
                        ],
                    )
                    door_option = True
                if "lock_picking" in player.skills and not pick_lock_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(
                                title=STR_PICK_LOCK,
                                callback=buttons_callback["pick_lock"],
                            )
                        ],
                    )
                    pick_lock_option = True
            elif isinstance(entity, Portal):
                if not portal_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(
                                title=STR_USE_PORTAL,
                                callback=buttons_callback["use_portal"],
                            )
                        ],
                    )
                    portal_option = True
            elif isinstance(entity, Fountain):
                if not fountain_option:
                    grid_elements.insert(
                        0, [Button(title=STR_DRINK, callback=buttons_callback["drink"])]
                    )
                    fountain_option = True
            elif isinstance(entity, Character):
                if not talk_option:
                    grid_elements.insert(
                        0, [Button(title=STR_TALK, callback=buttons_callback["talk"])]
                    )
                    talk_option = True

    # Check if player is on mission position
    for mission in missions:
        if (
                mission.type is MissionType.POSITION
                or mission.type is MissionType.TOUCH_POSITION
        ):
            if mission.is_position_valid(player.position):
                grid_elements.insert(
                    0, [Button(title=STR_TAKE, callback=buttons_callback["take"])]
                )

    # Check if player could attack something, according to weapon range
    if player.can_attack():
        w_range = [1] if player.get_weapon() is None else player.get_weapon().reach
        end = False
        for foe in foes:
            for reach in w_range:
                if (
                        abs(foe.position[0] - player.position[0])
                        + abs(foe.position[1] - player.position[1])
                        == TILE_SIZE * reach
                ):
                    grid_elements.insert(
                        0,
                        [Button(title=STR_ATTACK, callback=buttons_callback["attack"])],
                    )
                    end = True
                    break
            if end:
                break

    return InfoBox(
        STR_SELECT_AN_ACTION,
        grid_elements,
        width=ACTION_MENU_WIDTH,
        element_linked=player.get_rect(),
        has_close_button=False,
        identifier=CHARACTER_ACTION_MENU_ID,
    )


def create_diary_menu(grid_elements: list[list[BoxElement]]) -> InfoBox:
    """
    Return the interface of the diary resuming the last battle logs of a specific player.

    Keyword arguments:
    entries -- the entries data structure containing all the data needed to build the interface
    """
    return InfoBox(
        STR_DIARY,
        grid_elements,
        width=BATTLE_SUMMARY_WIDTH,
    )


def create_main_menu(
        buttons_callback: dict[str, Callable],
        is_initialization_phase: bool,
        position: Position,
) -> InfoBox:
    """
    Return the interface of the main level menu.

    Keyword arguments:
    is_initialization_phase -- a boolean value indicating whether
    it is the initialization phase or not
    position -- the position where the pop-up should be on screen
    """
    # Transform pos tuple into rect
    tile = pygame.Rect(position[0], position[1], 1, 1)
    elements = [
        [Button(title=STR_SAVE, callback=buttons_callback["save"])],
        [Button(title=STR_SUSPEND, callback=buttons_callback["suspend"])],
    ]

    if is_initialization_phase:
        elements.append([Button(title=STR_START, callback=buttons_callback["start"])])
    else:
        elements.append([Button(title=STR_DIARY, callback=buttons_callback["diary"])])
        elements.append(
            [Button(title=STR_END_TURN, callback=buttons_callback["end_turn"])]
        )

    return InfoBox(
        STR_MAIN_MENU,
        elements,
        width=ACTION_MENU_WIDTH,
        element_linked=tile,
        has_close_button=False,
    )


def create_item_shop_menu(
        buttons_callback: dict[str, Callable], item_button_position: Position, item: Item
) -> InfoBox:
    """
    Return the interface of an item that is on sale in a shop.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    """
    element_grid = [
        [Button(title=STR_BUY, callback=buttons_callback["buy_item"])],
        [Button(title=STR_INFO, callback=buttons_callback["info_item"])],
    ]
    formatted_item_name = str(item)
    item_rect = pygame.Rect(
        item_button_position[0] - 20,
        item_button_position[1],
        ITEM_BUTTON_SIZE[0],
        ITEM_BUTTON_SIZE[1],
    )

    return InfoBox(
        formatted_item_name,
        element_grid,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
    )


def create_item_sell_menu(
        buttons_callback: dict[str, Callable], item_button_position: Position, item: Item
) -> InfoBox:
    """
    Return the interface of an item that is in a player inventory and can be sold in a shop.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    """
    element_grid = [
        [Button(title=STR_SELL, callback=buttons_callback["sell_item"])],
        [Button(title=STR_INFO, callback=buttons_callback["info_item"])],
    ]
    formatted_item_name = str(item)
    item_rect = pygame.Rect(
        item_button_position[0] - 20,
        item_button_position[1],
        ITEM_BUTTON_SIZE[0],
        ITEM_BUTTON_SIZE[1],
    )

    return InfoBox(
        formatted_item_name,
        element_grid,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
    )


def create_trade_item_menu(
        buttons_callback: dict[str, Callable],
        item_button_position: Position,
        item: Item,
        players: Sequence[Player],
        is_first_player_owner: bool,
) -> InfoBox:
    """
    Return the interface of an item that is in a player inventory
    and can be trade to another player.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    players -- the two players that are currently involve in the trade
    """
    grid_elements = [
        [Button(title=STR_INFO, callback=buttons_callback["info_item"])],
        [
            Button(
                title=STR_TRADE,
                callback=lambda: buttons_callback["trade_item"](
                    players[0], players[1], is_first_player_owner
                ),
            )
        ],
    ]
    formatted_item_name = str(item)

    item_rect = pygame.Rect(
        item_button_position[0] - 20,
        item_button_position[1],
        TRADE_ITEM_BUTTON_SIZE[0],
        TRADE_ITEM_BUTTON_SIZE[1],
    )

    return InfoBox(
        formatted_item_name,
        grid_elements,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
    )


def create_item_menu(
        buttons_callback: dict[str, Callable],
        item_button_rect: pygame.Rect,
        item: Item,
        is_equipped: bool = False,
) -> InfoBox:
    """
    Return the interface of an item of a player.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    is_equipped -- a boolean value indicating whether the item is currently equipped or not
    """
    element_grid = [
        [Button(title=STR_INFO, callback=buttons_callback["info_item"])],
        [Button(title=STR_THROW, callback=buttons_callback["throw_item"])],
    ]
    formatted_item_name = str(item)

    if isinstance(item, Consumable):
        element_grid.insert(
            0, [Button(title=STR_USE, callback=buttons_callback["use_item"])]
        )
    elif isinstance(item, Equipment):
        if is_equipped:
            element_grid.insert(
                0,
                [Button(title=STR_UNEQUIP, callback=buttons_callback["unequip_item"])],
            )
        else:
            element_grid.insert(
                0, [Button(title=STR_EQUIP, callback=buttons_callback["equip_item"])]
            )

    return InfoBox(
        formatted_item_name,
        element_grid,
        width=ACTION_MENU_WIDTH,
        element_linked=item_button_rect,
    )


def create_item_description_stat(
        stat_name: str, stat_value: str
) -> Sequence[BoxElement]:
    """
    Return the entry line for the formatted display of an item stat description.

    Keyword arguments:
    stat_name -- the name of the statistic
    stat_value -- the value of the statistic
    """
    return [
        TextElement(
            f_STAT_NAME_(stat_name), font=fonts["ITEM_DESC_FONT"], margin=(0, 0, 0, 100)
        ),
        TextElement(stat_value, font=fonts["ITEM_DESC_FONT"], margin=(0, 100, 0, 0)),
    ]


def create_item_description_menu(item: Item) -> InfoBox:
    """
    Return the interface for the full description of an item.

    Keyword arguments:
    item -- the concerned item
    """
    item_title = str(item)

    grid_elements = [
        [
            TextElement(
                item.description, font=fonts["ITEM_DESC_FONT"], margin=(20, 0, 20, 0)
            )
        ]
    ]

    if isinstance(item, Equipment):
        if item.restrictions != {}:
            grid_elements.append(
                create_item_description_stat(
                    STR_RESERVED_TO, item.get_formatted_restrictions()
                )
            )
        if item.attack > 0:
            grid_elements.append(
                create_item_description_stat(STR_POWER, str(item.attack))
            )
        if item.defense > 0:
            grid_elements.append(
                create_item_description_stat(STR_DEFENSE, str(item.defense))
            )
        if item.resistance > 0:
            grid_elements.append(
                create_item_description_stat(STR_MAGICAL_RES, str(item.resistance))
            )
        if isinstance(item, Weapon):
            # Compute reach
            reach_txt = ""
            for distance in item.reach:
                reach_txt += str(distance) + ", "
            reach_txt = reach_txt[: len(reach_txt) - 2]
            grid_elements.append(
                create_item_description_stat(
                    STR_TYPE_OF_DAMAGE,
                    TRANSLATIONS["attack_kinds"][
                        str(item.attack_kind.value).lower().replace(" ", "_")
                    ],
                )
            )
            grid_elements.append(create_item_description_stat(STR_REACH, reach_txt))
            for possible_effect in item.effects:
                grid_elements.append(
                    create_item_description_stat(
                        STR_EFFECT,
                        f'{possible_effect["effect"]} ({possible_effect["probability"]}%)',
                    )
                )
            strong_against_formatted = item.get_formatted_strong_against()
            if strong_against_formatted:
                grid_elements.append(
                    create_item_description_stat(
                        STR_STRONG_AGAINST, strong_against_formatted
                    )
                )
        if isinstance(item, Shield):
            grid_elements.append(
                create_item_description_stat(STR_PARRY_RATE, str(item.parry) + "%")
            )
        if isinstance(item, (Shield, Weapon)):
            grid_elements.append(
                create_item_description_stat(
                    STR_DURABILITY, f"{item.durability} / {item.durability_max}"
                )
            )
        grid_elements.append(create_item_description_stat(STR_WEIGHT, str(item.weight)))
    elif isinstance(item, Consumable):
        for effect in item.effects:
            grid_elements.append(
                create_item_description_stat(
                    STR_EFFECT, effect.get_formatted_description()
                )
            )

    return InfoBox(
        item_title,
        grid_elements,
        width=ITEM_INFO_MENU_WIDTH,
    )


def create_alteration_info_menu(alteration: Alteration) -> InfoBox:
    """
    Return the interface for the description of an alteration.

    Keyword arguments:
    alteration -- the concerned alteration
    """
    turns_left = alteration.get_turns_left()
    grid_elements = [
        [
            TextElement(
                alteration.description,
                font=fonts["ITEM_DESC_FONT"],
                margin=(20, 0, 20, 0),
            ),
        ],
        [
            TextElement(
                f_TURNS_LEFT_NUMBER(turns_left),
                font=fonts["ITEM_DESC_FONT"],
                margin=(0, 0, 10, 0),
                text_color=ORANGE,
            ),
        ],
    ]

    return InfoBox(
        str(alteration),
        grid_elements,
        width=STATUS_INFO_MENU_WIDTH,
    )


def create_skill_info_menu(skill: Skill) -> InfoBox:
    """
    Return the interface for the description of a skill.

    Keyword arguments:
    skill -- the concerned skill
    """
    grid_elements = [
        [
            TextElement(
                skill.description, font=fonts["ITEM_DESC_FONT"], margin=(20, 0, 20, 0)
            )
        ],
        [
            BoxElement(
                Position(0, 0), pygame.Surface((0, 0)), margin=(0, 0, 10, 0)
            )
        ],
    ]

    return InfoBox(
        skill.formatted_name,
        grid_elements,
        width=STATUS_INFO_MENU_WIDTH,
    )


def create_status_entity_menu(
        buttons_callback: dict[str, Callable], entity: Entity
) -> InfoBox:
    """
    Return the interface for the status screen of an entity.

    Keyword arguments:
    entity -- the concerned entity
    """
    keywords_display = (
        entity.get_formatted_keywords() if isinstance(entity, Foe) else ""
    )
    grid_elements: list[list[BoxElement]] = [
        [TextElement(keywords_display, font=fonts["ITALIC_ITEM_FONT"])],
        [TextElement(f_LEVEL_NUMBER_ENTITY(entity.lvl), font=fonts["ITEM_DESC_FONT"])],
        [
            TextElement(
                STR_ATTACK,
                font=fonts["MENU_SUB_TITLE_FONT"],
                text_color=DARK_GREEN,
                margin=(20, 0, 20, 0),
            ),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            TextElement(
                STR_LOOT,
                font=fonts["MENU_SUB_TITLE_FONT"],
                text_color=DARK_GREEN,
                margin=(20, 0, 20, 0),
            )
            if isinstance(entity, Foe)
            else BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_TYPE_),
            TextElement(
                TRANSLATIONS["attack_kinds"][str(entity.attack_kind.value).lower()]
            ),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_REACH_),
            TextElement(entity.get_formatted_reach()),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(
                STR_STATS,
                font=fonts["MENU_SUB_TITLE_FONT"],
                text_color=DARK_GREEN,
                margin=(10, 0, 10, 0),
            ),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            TextElement(
                STR_SKILLS,
                font=fonts["MENU_SUB_TITLE_FONT"],
                text_color=DARK_GREEN,
                margin=(10, 0, 10, 0),
            ),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_HP_),
            TextElement(
                f_DIV(entity.hit_points, entity.hit_points_max),
                text_color=determine_gauge_color(
                    entity.hit_points, entity.hit_points_max, WHITE
                ),
            ),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_MOVE_),
            TextElement(str(entity.max_moves)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_ATTACK_),
            TextElement(str(entity.strength)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_DEFENSE_),
            TextElement(str(entity.defense)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(STR_MAGICAL_RES_),
            TextElement(str(entity.resistance)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(Position(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement(
                STR_ALTERATIONS,
                font=fonts["MENU_SUB_TITLE_FONT"],
                text_color=DARK_GREEN,
                margin=(10, 0, 10, 0),
            ),
        ],
    ]

    if not entity.alterations:
        grid_elements.append([TextElement(STR_NONE)])
    for alteration in entity.alterations:
        grid_elements.append(
            [
                Button(
                    title=str(alteration),
                    callback=lambda alteration_reference=alteration: buttons_callback[
                        "info_alteration"
                    ](alteration_reference),
                    no_background=True,
                    text_hover_color=TURQUOISE,
                ),
            ]
        )

    if isinstance(entity, Foe):
        loot = entity.potential_loot
        line_index = 3
        for item, probability in loot:
            name = str(item)
            grid_elements[line_index][3] = TextElement(name)
            grid_elements[line_index][4] = TextElement(f" ({probability * 100} %)")
            line_index += 1

    # Display skills
    line_index = 8
    for skill in entity.skills:
        grid_elements[line_index][3] = Button(
            title=skill.formatted_name,
            margin=(0, 0, 0, 0),
            callback=lambda skill_reference=skill: buttons_callback["info_skill"](
                skill_reference
            ),
            no_background=True,
            text_hover_color=TURQUOISE,
        )
        line_index += 1

    return InfoBox(
        str(entity),
        grid_elements,
        width=FOE_STATUS_MENU_WIDTH,
    )


def create_event_dialog(dialog_element: dict[str, any]) -> InfoBox:
    """
    Return the interface of a dialog.

    Keyword arguments:
    dialog_element -- a data structure containing the title and the content of the dialog
    """
    elements = [
        [TextElement(talk, font=fonts["ITEM_DESC_FONT"])]
        for talk in dialog_element["talks"]
    ]
    return InfoBox(
        dialog_element["title"],
        elements,
        width=DIALOG_WIDTH,
        title_color=ORANGE,
        visible_on_background=False,
    )


def create_reward_menu(mission: Mission) -> InfoBox:
    """
    Return the interface for an accomplished mission.

    Keyword arguments:
    mission -- the concerned mission
    """
    grid_element = [
        [
            TextElement(
                STR_REWARD_CONGRATULATIONS,
                font=fonts["ITEM_DESC_FONT"],
            )
        ]
    ]
    if mission.gold:
        grid_element.append([TextElement(f_EARNED_GOLD(mission.gold))])
    for item in mission.items:
        grid_element.append([TextElement(f_EARNED_ITEMS(item))])

    return InfoBox(
        mission.description,
        grid_element,
        width=REWARD_MENU_WIDTH,
    )


def create_start_menu(buttons_callback: dict[str, Callable]) -> InfoBox:
    """
    Return the interface of the main menu of the game (in the start screen).
    """
    return InfoBox(
        STR_GAME_TITLE,
        [
            [
                Button(title=STR_NEW_GAME, callback=buttons_callback["new_game"]),
            ],
            [
                Button(title=STR_LOAD_GAME, callback=buttons_callback["load_menu"]),
            ],
            [
                Button(title=STR_OPTIONS, callback=buttons_callback["options_menu"]),
            ],
            [
                Button(title=STR_EXIT_GAME, callback=buttons_callback["exit_game"]),
            ],
        ],
        width=START_MENU_WIDTH,
        has_close_button=False,
    )


def load_parameter_button(
        formatted_name: str,
        values: Sequence[dict[str, int]],
        current_value: int,
        edit_parameter_callback: Callable,
) -> DynamicButton:
    """
    Return a DynamicButton permitting to handle the tweaking of a specific game parameter.

    Keyword arguments:
    formatted_name -- the formatted name of the parameter
    values -- the sequence of values that can be taken by the parameter
    current_value -- the current value of the parameter
    identifier -- the identifier of the parameter
    """
    current_value_index: int = 0

    for i, _ in enumerate(values):
        if values[i]["value"] == current_value:
            current_value_index = i

    return DynamicButton(
        base_title=formatted_name,
        values=values,
        callback=edit_parameter_callback,
        current_value_index=current_value_index,
    )


def create_options_menu(
        parameters: dict[str, int],
        modify_option_function: Callable,
) -> InfoBox:
    """
    Return the interface of the game options' menu.

    Keyword arguments:
    parameters -- the dictionary containing all parameters with their current value
    """

    return InfoBox(
        STR_OPTIONS_MENU,
        [
            [
                Button(
                    title=STR_LANGUAGE,
                    callback=lambda: modify_option_function("language"),
                ),
            ],
            [
                load_parameter_button(
                    STR_MOVE_SPEED_,
                    [
                        {"label": STR_SLOW, "value": ANIMATION_SPEED // 2},
                        {"label": STR_NORMAL, "value": ANIMATION_SPEED},
                        {"label": STR_FAST, "value": ANIMATION_SPEED * 2},
                    ],
                    parameters["move_speed"],
                    lambda value: modify_option_function("move_speed", value),
                ),
            ],
            [
                load_parameter_button(
                    STR_SCREEN_MODE_,
                    [
                        {"label": STR_WINDOW, "value": SCREEN_SIZE // 2},
                        {"label": STR_FULL, "value": SCREEN_SIZE},
                    ],
                    parameters["screen_size"],
                    lambda value: modify_option_function("screen_size", value),
                ),
            ],
        ],
        width=START_MENU_WIDTH,
    )


def create_load_menu(load_game_function: Callable) -> InfoBox:
    """
    Return the interface of the load game menu.
    """
    element_grid = []

    for i in range(SAVE_SLOTS):
        element_grid.append(
            [
                Button(
                    title=f_SAVE_NUMBER(i + 1),
                    callback=lambda slot_id=i: load_game_function(slot_id),
                )
            ]
        )

    return InfoBox(
        STR_LOAD_GAME_MENU,
        element_grid,
        width=START_MENU_WIDTH,
    )


def create_save_menu(save_game_function: Callable) -> InfoBox:
    """
    Return the interface of the save game menu
    """
    element_grid = []

    for i in range(SAVE_SLOTS):
        element_grid.append(
            [
                Button(
                    title=f_SAVE_NUMBER(i + 1),
                    callback=lambda slot_id=i: save_game_function(slot_id),
                )
            ]
        )

    return InfoBox(
        STR_SAVE_GAME_MENU,
        element_grid,
        width=START_MENU_WIDTH,
    )


def create_save_dialog(buttons_callback: dict[str, Callable]) -> InfoBox:
    """
    Return the interface of the save game reminder
    """
    element_grid = [
        [Button(title=STR_YES, callback=buttons_callback["yes"])],
        [Button(title=STR_NO, callback=buttons_callback["no"])],
    ]
    return InfoBox(
        STR_SAVE_THE_GAME_,
        element_grid,
        width=ACTION_MENU_WIDTH,
        has_close_button=False,
    )


def create_choose_language_menu(buttons_callback: Callable) -> InfoBox:
    """
    Return the interface to choose language
    """
    element_grid = [
        [
            Button(
                title="English",
                font=fonts["LANGUAGE_FONT"],
                callback=lambda: buttons_callback("en"),
            )
        ],
        [
            Button(
                title="中文简体",
                font=fonts["LANGUAGE_FONT"],
                callback=lambda: buttons_callback("zh_cn"),
            )
        ],
    ]
    return InfoBox(
        STR_CHOOSE_LANGUAGE,
        element_grid,
        width=ACTION_MENU_WIDTH,
        has_close_button=True,
    )
