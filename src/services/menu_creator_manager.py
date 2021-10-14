"""
Define functions creating a specific menu enveloping data from parameters.
"""

from typing import Sequence, Union, Callable, Optional

import pygame
from pygamepopup.components import InfoBox as new_InfoBox, Button, DynamicButton, TextElement, BoxElement

from src.constants import (
    TILE_SIZE,
    ITEM_MENU_WIDTH,
    ORANGE,
    WHITE,
    ITEM_BUTTON_SIZE_EQ,
    EQUIPMENT_MENU_WIDTH,
    TRADE_MENU_WIDTH,
    GREEN,
    YELLOW,
    RED,
    DARK_GREEN,
    GOLD,
    TURQUOISE,
    STATUS_MENU_WIDTH,
    ACTION_MENU_WIDTH,
    BATTLE_SUMMARY_WIDTH,
    ITEM_BUTTON_SIZE,
    ITEM_INFO_MENU_WIDTH,
    STATUS_INFO_MENU_WIDTH,
    FOE_STATUS_MENU_WIDTH,
    DIALOG_WIDTH,
    REWARD_MENU_WIDTH,
    START_MENU_WIDTH,
    ANIMATION_SPEED,
    SCREEN_SIZE,
    SAVE_SLOTS,
)
from src.game_entities.alteration import Alteration
from src.game_entities.building import Building
from src.game_entities.chest import Chest
from src.game_entities.character import Character
from src.game_entities.consumable import Consumable
from src.game_entities.door import Door
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Foe
from src.game_entities.fountain import Fountain
from src.game_entities.item import Item
from src.game_entities.skill import Skill
from src.gui.entries import Entries, Entry, EntryLine
from src.gui.fonts import fonts
from src.gui.info_box import InfoBox
from src.game_entities.mission import MissionType, Mission
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.shield import Shield
from src.game_entities.weapon import Weapon
from src.gui.position import Position
from src.services.menus import (
    BuyMenu,
    SellMenu,
    InventoryMenu,
    EquipmentMenu,
    TradeMenu,
    StatusMenu,
    CharacterMenu,
    MainMenu,
    ItemMenu,
    StartMenu,
    OptionsMenu,
    SaveMenu,
    LoadMenu,
)

MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10

close_function: Optional[Callable] = None


def create_shop_menu(
        interaction_callback: Callable,
        stock: Sequence[dict[str, Union[Item, int]]],
        gold: int,
) -> InfoBox:
    """
    Return the interface of a shop menu with user as the buyer.

    Keyword arguments:
    stock -- the collection of items that are available in the shop, with the quantity of each one
    gold -- the amount of gold that should be displayed at the bottom
    """
    entries = []
    row = []
    for item in stock:
        entry = {
            "type": "item_button",
            "item": item["item"],
            "price": item["item"].price,
            "quantity": item["quantity"],
            "callback": lambda button_position, item_reference=item[
                "item"
            ]: interaction_callback(item_reference, button_position),
        }
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []

    if row:
        entries.append(row)

    # Gold at end
    entry = [
        {"type": "text", "text": f"Your gold : {gold}", "font": fonts["ITEM_DESC_FONT"]}
    ]
    entries.append(entry)

    return InfoBox(
        "Shop - Buying",
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=BuyMenu,
        width=ITEM_MENU_WIDTH,
        close_button=lambda: close_function(False),
        title_color=ORANGE,
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
    entries = []
    row = []
    method_id = SellMenu.INTERAC_SELL if is_to_sell else InventoryMenu.INTERAC_ITEM
    for i, item in enumerate(items):
        if is_to_sell:
            callback = (
                lambda button_position, item_reference=item: interaction_callback(
                    item_reference, button_position
                )
            )
        else:
            callback = (
                lambda button_position, item_reference=item: interaction_callback(
                    item_reference, button_position, is_equipped=False
                )
            )
        entry = {"type": "item_button", "item": item, "index": i, "callback": callback}
        # Test if price should appeared
        if is_to_sell and item:
            entry["price"] = item.resell_price
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []
    if row:
        entries.append(row)

    # Gold at end
    entry = [
        {
            "type": "text",
            "text": "Your gold : " + str(gold),
            "font": fonts["ITEM_DESC_FONT"],
        }
    ]
    entries.append(entry)

    title = "Shop - Selling" if is_to_sell else "Inventory"
    menu_id = SellMenu if is_to_sell else InventoryMenu
    title_color = ORANGE if is_to_sell else WHITE
    return InfoBox(
        title,
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=menu_id,
        width=ITEM_MENU_WIDTH,
        close_button=lambda: close_function(False),
        title_color=title_color,
    )


def create_equipment_menu(
        interaction_callback: Callable, equipments: Sequence[Equipment]
) -> InfoBox:
    """
    Return the interface of a player equipment.

    Keyword arguments:
    equipments -- the collection of equipments currently equipped by the player
    """
    entries = []
    body_parts = [["head"], ["body"], ["right_hand", "left_hand"], ["feet"]]
    for part in body_parts:
        row = []
        for member in part:
            equipment = None
            index = -1
            for i, potential_equipment in enumerate(equipments):
                if member == potential_equipment.body_part:
                    equipment = potential_equipment
                    index = i
                    break
            entry = {
                "type": "item_button",
                "item": equipment,
                "index": index,
                "size": ITEM_BUTTON_SIZE_EQ,
                "callback": lambda button_position, equipment_reference=equipment: interaction_callback(
                    equipment_reference, button_position, is_equipped=True
                ),
            }
            row.append(entry)
        entries.append(row)
    return InfoBox(
        "Equipment",
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=EquipmentMenu,
        width=EQUIPMENT_MENU_WIDTH,
        close_button=lambda: close_function(False),
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

    entries = []
    method_id = TradeMenu.INTERAC_ITEM
    # We assume that first player and second player items lists have the same size and are even
    for i in range(len(items_first) // 2):
        row = []
        for owner_i, items in enumerate([items_first, items_second]):
            for j in range(2):
                entry = {
                    "type": "item_button",
                    "item": items[i * 2 + j],
                    "index": i,
                    "subtype": "trade",
                    "callback": lambda button_position, item_reference=items[
                        i * 2 + j
                        ], owner=owner_i: buttons_callback["interact_item"](
                        item_reference,
                        button_position,
                        [first_player, second_player],
                        owner == 0,
                    ),
                }
                row.append(entry)
        entries.append(row)

    # Buttons to trade gold
    method_id = TradeMenu.SEND_GOLD
    entry = [
        {
            "type": "button",
            "name": "50G ->",
            "size": (90, 30),
            "margin": (30, 0, 0, 0),
            "font": fonts["ITEM_DESC_FONT"],
            "callback": lambda: buttons_callback["send_gold"](
                first_player, second_player, True, 50
            ),
        },
        {
            "type": "button",
            "name": "200G ->",
            "size": (90, 30),
            "margin": (30, 0, 0, 0),
            "font": fonts["ITEM_DESC_FONT"],
            "callback": lambda: buttons_callback["send_gold"](
                first_player, second_player, True, 200
            ),
        },
        {
            "type": "button",
            "name": "All ->",
            "size": (90, 30),
            "margin": (30, 0, 0, 0),
            "font": fonts["ITEM_DESC_FONT"],
            "callback": lambda: buttons_callback["send_gold"](
                first_player, second_player, True, first_player.gold
            ),
        },
        {
            "type": "button",
            "name": "<- 50G",
            "size": (90, 30),
            "margin": (30, 0, 0, 0),
            "font": fonts["ITEM_DESC_FONT"],
            "callback": lambda: buttons_callback["send_gold"](
                first_player, second_player, False, 50
            ),
        },
        {
            "type": "button",
            "name": "<- 200G",
            "size": (90, 30),
            "margin": (30, 0, 0, 0),
            "font": fonts["ITEM_DESC_FONT"],
            "callback": lambda: buttons_callback["send_gold"](
                first_player, second_player, False, 200
            ),
        },
        {
            "type": "button",
            "name": "<- All",
            "size": (90, 30),
            "margin": (30, 0, 0, 0),
            "font": fonts["ITEM_DESC_FONT"],
            "callback": lambda: buttons_callback["send_gold"](
                first_player, second_player, False, second_player.gold
            ),
        },
    ]
    entries.append(entry)

    # Gold at end
    entry = [
        {
            "type": "text",
            "text": str(first_player) + "'s gold : " + str(first_player.gold),
            "font": fonts["ITEM_DESC_FONT"],
        },
        {
            "type": "text",
            "text": str(second_player) + "'s gold : " + str(second_player.gold),
            "font": fonts["ITEM_DESC_FONT"],
        },
    ]
    entries.append(entry)

    title = "Trade"
    menu_id = TradeMenu
    title_color = WHITE
    return InfoBox(
        title,
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=menu_id,
        width=TRADE_MENU_WIDTH,
        close_button=lambda: close_function(False),
        separator=True,
        title_color=title_color,
    )


def determine_hp_color(hit_points: int, hit_points_max: int) -> pygame.Color:
    """
    Return the color that should be used to display the hp bar of a player according to the ratio
    hit points / hit points max.

    Keyword arguments:
    hit_points -- the current hit points of the entity
    hit_points_max -- the maximum hit points of the entity
    """
    if hit_points == hit_points_max:
        return WHITE
    if hit_points >= hit_points_max * 0.75:
        return GREEN
    if hit_points >= hit_points_max * 0.5:
        return YELLOW
    if hit_points >= hit_points_max * 0.30:
        return ORANGE
    return RED


def create_status_menu(
        buttons_callback: dict[str, Callable], player: Player
) -> InfoBox:
    """
    Return the interface resuming the status of a player.

    Keyword arguments:
    player -- the concerned player
    """
    entries = [
        [
            {},
            {
                "type": "text",
                "color": GREEN,
                "text": "Name :",
                "font": fonts["ITALIC_ITEM_FONT"],
            },
            {"type": "text", "text": str(player)},
            {},
        ],
        [
            {},
            {},
            {
                "type": "text",
                "color": DARK_GREEN,
                "text": "SKILLS",
                "font": fonts["MENU_SUB_TITLE_FONT"],
                "margin": (10, 0, 10, 0),
            },
        ],
        [
            {
                "type": "text",
                "color": GREEN,
                "text": "Class :",
                "font": fonts["ITALIC_ITEM_FONT"],
            },
            {"type": "text", "text": player.get_formatted_classes()},
        ],
        [
            {
                "type": "text",
                "color": GREEN,
                "text": "Race :",
                "font": fonts["ITALIC_ITEM_FONT"],
            },
            {"type": "text", "text": player.get_formatted_race()},
        ],
        [
            {
                "type": "text",
                "color": GREEN,
                "text": "Level :",
                "font": fonts["ITALIC_ITEM_FONT"],
            },
            {"type": "text", "text": str(player.lvl)},
        ],
        [
            {
                "type": "text",
                "color": GOLD,
                "text": "   XP :",
                "font": fonts["ITALIC_ITEM_FONT"],
            },
            {
                "type": "text",
                "text": f"{player.experience} / {player.experience_to_lvl_up}",
            },
        ],
        [
            {
                "type": "text",
                "color": DARK_GREEN,
                "text": "STATS",
                "font": fonts["MENU_SUB_TITLE_FONT"],
                "margin": (10, 0, 10, 0),
            }
        ],
        [
            {"type": "text", "color": WHITE, "text": "HP :"},
            {
                "type": "text",
                "text": f"{player.hit_points} / {player.hit_points_max}",
                "color": determine_hp_color(player.hit_points, player.hit_points_max),
            },
        ],
        [
            {"type": "text", "color": WHITE, "text": "MOVE :"},
            {
                "type": "text",
                "text": str(player.max_moves)
                        + player.get_formatted_stat_change("speed"),
            },
        ],
        [
            {"type": "text", "color": WHITE, "text": "CONSTITUTION :"},
            {"type": "text", "text": str(player.constitution)},
        ],
        [
            {"type": "text", "color": WHITE, "text": "ATTACK :"},
            {
                "type": "text",
                "text": str(player.strength)
                        + player.get_formatted_stat_change("strength"),
            },
        ],
        [
            {"type": "text", "color": WHITE, "text": "DEFENSE :"},
            {
                "type": "text",
                "text": str(player.defense)
                        + player.get_formatted_stat_change("defense"),
            },
        ],
        [
            {"type": "text", "color": WHITE, "text": "MAGICAL RES :"},
            {
                "type": "text",
                "text": str(player.resistance)
                        + player.get_formatted_stat_change("resistance"),
            },
        ],
        [
            {
                "type": "text",
                "color": DARK_GREEN,
                "text": "ALTERATIONS",
                "font": fonts["MENU_SUB_TITLE_FONT"],
                "margin": (10, 0, 10, 0),
            }
        ],
    ]

    if not player.alterations:
        entries.append([{"type": "text", "color": WHITE, "text": "None"}])
    for alteration in player.alterations:
        entries.append(
            [
                {
                    "type": "text_button",
                    "name": str(alteration),
                    "callback": lambda alteration_reference=alteration: buttons_callback[
                        "info_alteration"
                    ](
                        alteration_reference
                    ),
                    "color": WHITE,
                    "color_hover": TURQUOISE,
                    "obj": alteration,
                }
            ]
        )

    # Display skills
    i = 2
    for skill in player.skills:
        skill_displayed = {
            "type": "text_button",
            "name": skill.formatted_name,
            "callback": lambda skill_reference=skill: buttons_callback["info_skill"](
                skill_reference
            ),
            "color": WHITE,
            "color_hover": TURQUOISE,
            "obj": skill,
        }
        entries[i].append(skill_displayed)
        i += 1
    for j in range(i, len(entries)):
        entries[j].append({})

    return InfoBox(
        "Status",
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=StatusMenu,
        width=STATUS_MENU_WIDTH,
        close_button=lambda: close_function(False),
    )


def create_player_menu(
        buttons_callback: dict[str, Callable],
        player: Player,
        buildings: Sequence[Building],
        interactable_entities: Sequence[Entity],
        missions: Sequence[Mission],
        foes: Sequence[Foe],
) -> new_InfoBox:
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
        [Button(title="Inventory", callback=buttons_callback["inventory"])],
        [Button(title="Equipment", callback=buttons_callback["equipment"])],
        [Button(title="Status", callback=buttons_callback["status"])],
        [Button(title="Wait", callback=buttons_callback["wait"])],
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
                    0, [Button(title="Visit", callback=buttons_callback["visit"])]
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
                        0, [Button(title="Trade", callback=buttons_callback["trade"])]
                    )
                    trade_option = True
            elif isinstance(entity, Chest):
                if not entity.opened and not chest_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(title="Open Chest", callback=buttons_callback["open_chest"])
                        ],
                    )
                    chest_option = True
                if "lock_picking" in player.skills and not pick_lock_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(title="Pick Lock", callback=buttons_callback["pick_lock"])
                        ],
                    )
                    pick_lock_option = True
            elif isinstance(entity, Door):
                if not door_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(title="Open Door", callback=buttons_callback["open_door"])
                        ],
                    )
                    door_option = True
                if "lock_picking" in player.skills and not pick_lock_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(title="Pick Lock", callback=buttons_callback["pick_lock"])
                        ],
                    )
                    pick_lock_option = True
            elif isinstance(entity, Portal):
                if not portal_option:
                    grid_elements.insert(
                        0,
                        [
                            Button(title="Use Portal", callback=buttons_callback["use_portal"])
                        ],
                    )
                    portal_option = True
            elif isinstance(entity, Fountain):
                if not fountain_option:
                    grid_elements.insert(
                        0, [Button(title="Drink", callback=buttons_callback["drink"])]
                    )
                    fountain_option = True
            elif isinstance(entity, Character):
                if not talk_option:
                    grid_elements.insert(
                        0, [Button(title="Talk", callback=buttons_callback["talk"])]
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
                    0, [Button(title="Take", callback=buttons_callback["take"])]
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
                        0, [Button(title="Attack", callback=buttons_callback["attack"])]
                    )
                    end = True
                    break
            if end:
                break

    return new_InfoBox(
        "Select an action",
        grid_elements,
        width=ACTION_MENU_WIDTH,
        element_linked=player.get_rect(),
    )


def create_diary_menu(grid_elements: list[list[BoxElement]]) -> InfoBox:
    """
    Return the interface of the diary resuming the last battle logs of a specific player.

    Keyword arguments:
    entries -- the entries data structure containing all the data needed to build the interface
    """
    return new_InfoBox(
        "Diary",
        grid_elements,
        width=BATTLE_SUMMARY_WIDTH,
    )


def create_main_menu(
        buttons_callback: dict[str, Callable],
        is_initialization_phase: bool,
        position: Position,
) -> new_InfoBox:
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
        [Button(title="Save", callback=buttons_callback["save"])],
        [Button(title="Suspend", callback=buttons_callback["suspend"])],
    ]

    if is_initialization_phase:
        elements.append([Button(title="Start", callback=buttons_callback["start"])])
    else:
        elements.append([Button(title="Diary", callback=buttons_callback["diary"])]),
        elements.append([Button(title="End Turn", callback=buttons_callback["end_turn"])])

    return new_InfoBox(
        "Main Menu",
        elements,
        width=ACTION_MENU_WIDTH,
        element_linked=tile,
        has_close_button=False
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
    entries = [
        [{"name": "Buy", "callback": buttons_callback["buy_item"], "type": "button"}],
        [{"name": "Info", "callback": buttons_callback["info_item"], "type": "button"}],
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
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=ItemMenu,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
        close_button=lambda: close_function(False),
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
    entries = [
        [{"name": "Sell", "callback": buttons_callback["sell_item"], "type": "button"}],
        [{"name": "Info", "callback": buttons_callback["info_item"], "type": "button"}],
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
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=ItemMenu,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
        close_button=lambda: close_function(False),
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
    entries = [
        [{"name": "Info", "callback": buttons_callback["info_item"]}],
        [
            {
                "name": "Trade",
                "callback": lambda: buttons_callback["trade_item"](
                    players[0], players[1], is_first_player_owner
                ),
            }
        ],
    ]
    formatted_item_name = str(item)

    for row in entries:
        for entry in row:
            entry["type"] = "button"

    item_rect = pygame.Rect(
        item_button_position[0] - 20,
        item_button_position[1],
        ITEM_BUTTON_SIZE[0],
        ITEM_BUTTON_SIZE[1],
    )

    return InfoBox(
        formatted_item_name,
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=ItemMenu,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
        close_button=lambda: close_function(False),
    )


def create_item_menu(
        buttons_callback: dict[str, Callable],
        item_button_position: Position,
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
    entries = [
        [{"name": "Info", "callback": buttons_callback["info_item"]}],
        [{"name": "Throw", "callback": buttons_callback["throw_item"]}],
    ]
    formatted_item_name = str(item)

    if isinstance(item, Consumable):
        entries.insert(0, [{"name": "Use", "callback": buttons_callback["use_item"]}])
    elif isinstance(item, Equipment):
        if is_equipped:
            entries.insert(
                0, [{"name": "Unequip", "callback": buttons_callback["unequip_item"]}]
            )
        else:
            entries.insert(
                0, [{"name": "Equip", "callback": buttons_callback["equip_item"]}]
            )

    for row in entries:
        for entry in row:
            entry["type"] = "button"

    item_rect = pygame.Rect(
        item_button_position[0] - 20,
        item_button_position[1],
        ITEM_BUTTON_SIZE[0],
        ITEM_BUTTON_SIZE[1],
    )

    return InfoBox(
        formatted_item_name,
        "imgs/interface/PopUpMenu.png",
        entries,
        id_type=ItemMenu,
        width=ACTION_MENU_WIDTH,
        element_linked=item_rect,
        close_button=lambda: close_function(False),
    )


def create_item_description_stat(stat_name: str, stat_value: str) -> EntryLine:
    """
    Return the entry line for the formatted display of an item stat description.

    Keyword arguments:
    stat_name -- the name of the statistic
    stat_value -- the value of the statistic
    """
    return [
        {
            "type": "text",
            "text": f"{stat_name} : ",
            "font": fonts["ITEM_DESC_FONT"],
            "margin": (0, 0, 0, 100),
        },
        {
            "type": "text",
            "text": stat_value,
            "font": fonts["ITEM_DESC_FONT"],
            "margin": (0, 100, 0, 0),
        },
    ]


def create_item_description_menu(item: Item) -> InfoBox:
    """
    Return the interface for the full description of an item.

    Keyword arguments:
    item -- the concerned item
    """
    item_title = str(item)

    entries = [
        [
            {
                "type": "text",
                "text": item.description,
                "font": fonts["ITEM_DESC_FONT"],
                "margin": (20, 0, 20, 0),
            }
        ]
    ]

    if isinstance(item, Equipment):
        if item.restrictions != {}:
            entries.append(
                create_item_description_stat(
                    "RESERVED TO", item.get_formatted_restrictions()
                )
            )
        if item.attack > 0:
            entries.append(create_item_description_stat("POWER", str(item.attack)))
        if item.defense > 0:
            entries.append(create_item_description_stat("DEFENSE", str(item.defense)))
        if item.resistance > 0:
            entries.append(
                create_item_description_stat("MAGICAL RES", str(item.resistance))
            )
        if isinstance(item, Weapon):
            # Compute reach
            reach_txt = ""
            for distance in item.reach:
                reach_txt += str(distance) + ", "
            reach_txt = reach_txt[: len(reach_txt) - 2]
            entries.append(
                create_item_description_stat(
                    "TYPE OF DAMAGE", str(item.attack_kind.value)
                )
            )
            entries.append(create_item_description_stat("REACH", reach_txt))
            for possible_effect in item.effects:
                entries.append(
                    create_item_description_stat(
                        "EFFECT",
                        f'{possible_effect["effect"]} ({possible_effect["probability"]}%)',
                    )
                )
            strong_against_formatted = item.get_formatted_strong_against()
            if strong_against_formatted:
                entries.append(
                    create_item_description_stat(
                        "STRONG AGAINST", strong_against_formatted
                    )
                )
        if isinstance(item, Shield):
            entries.append(
                create_item_description_stat("PARRY RATE", str(item.parry) + "%")
            )
        if isinstance(item, (Shield, Weapon)):
            entries.append(
                create_item_description_stat(
                    "DURABILITY", f"{item.durability} / {item.durability_max}"
                )
            )
        entries.append(create_item_description_stat("WEIGHT", str(item.weight)))
    elif isinstance(item, Consumable):
        for effect in item.effects:
            entries.append(
                create_item_description_stat("EFFECT", effect.get_formatted_description())
            )

    return InfoBox(
        item_title,
        "imgs/interface/PopUpMenu.png",
        entries,
        width=ITEM_INFO_MENU_WIDTH,
        close_button=lambda: close_function(False),
    )


def create_alteration_info_menu(alteration: Alteration) -> InfoBox:
    """
    Return the interface for the description of an alteration.

    Keyword arguments:
    alteration -- the concerned alteration
    """
    turns_left = alteration.get_turns_left()
    entries = [
        [
            {
                "type": "text",
                "text": alteration.description,
                "font": fonts["ITEM_DESC_FONT"],
                "margin": (20, 0, 20, 0),
            }
        ],
        [
            {
                "type": "text",
                "text": f"Turns left : {turns_left}",
                "font": fonts["ITEM_DESC_FONT"],
                "margin": (0, 0, 10, 0),
                "color": ORANGE,
            }
        ],
    ]

    return InfoBox(
        str(alteration),
        "imgs/interface/PopUpMenu.png",
        entries,
        width=STATUS_INFO_MENU_WIDTH,
        close_button=lambda: close_function(False),
    )


def create_skill_info_menu(skill: Skill) -> InfoBox:
    """
    Return the interface for the description of a skill.

    Keyword arguments:
    skill -- the concerned skill
    """
    entries = [
        [
            {
                "type": "text",
                "text": skill.description,
                "font": fonts["ITEM_DESC_FONT"],
                "margin": (20, 0, 20, 0),
            }
        ],
        [{"type": "text", "text": "", "margin": (0, 0, 10, 0)}],
    ]

    return InfoBox(
        skill.formatted_name,
        "imgs/interface/PopUpMenu.png",
        entries,
        width=STATUS_INFO_MENU_WIDTH,
        close_button=lambda: close_function(False),
    )


def create_status_entity_menu(alteration_callback: Callable, entity: Entity) -> InfoBox:
    """
    Return the interface for the status screen of an entity.

    Keyword arguments:
    entity -- the concerned entity
    """
    keywords_display = (
        entity.get_formatted_keywords() if isinstance(entity, Foe) else ""
    )
    elements: list[list[BoxElement]] = [
        [
            TextElement(keywords_display, font=fonts["ITALIC_ITEM_FONT"])
        ],
        [
            TextElement(f"LEVEL : {entity.lvl}", font=fonts["ITEM_DESC_FONT"])
        ],
        [
            TextElement("ATTACK", font=fonts["MENU_SUB_TITLE_FONT"], text_color=DARK_GREEN, margin=(20, 0, 20, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            TextElement("LOOT", font=fonts["MENU_SUB_TITLE_FONT"], text_color=DARK_GREEN, margin=(20, 0, 20, 0)) if isinstance(entity, Foe) else {},
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("TYPE :"),
            TextElement(str(entity.attack_kind.value)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("REACH :"),
            TextElement(entity.get_formatted_reach()),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("STATS", font=fonts["MENU_SUB_TITLE_FONT"], text_color=DARK_GREEN, margin=(10, 0, 10, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            TextElement("SKILLS", font=fonts["MENU_SUB_TITLE_FONT"], text_color=DARK_GREEN, margin=(10, 0, 10, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("HP :"),
            TextElement(f"{entity.hit_points} / {entity.hit_points_max}", text_color=determine_hp_color(entity.hit_points, entity.hit_points_max)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("MOVE :"),
            TextElement(str(entity.max_moves)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("ATTACK :"),
            TextElement(str(entity.strength)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("DEFENSE :"),
            TextElement(str(entity.defense)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("MAGICAL RES :"),
            TextElement(str(entity.resistance)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
            BoxElement(pygame.Vector2(0, 0), pygame.Surface((0, 0)), (0, 0, 0, 0)),
        ],
        [
            TextElement("ALTERATIONS", font=fonts["MENU_SUB_TITLE_FONT"], text_color=DARK_GREEN, margin=(10, 0, 10, 0)),
        ],
    ]

    # TODO: Add Alteration callbacks
    if not entity.alterations:
        elements.append([TextElement("None")])
    for alteration in entity.alterations:
        elements.append(
            [
                TextElement(str(alteration), text_color=WHITE),
            ]
        )

    if isinstance(entity, Foe):
        loot = entity.potential_loot
        i = 3
        for (item, probability) in loot:
            name = str(item)
            elements[i][3] = TextElement(name)
            elements[i][4] = TextElement(f" ({probability * 100} %)")
            i += 1

    # Display skills
    i = 7
    for skill in entity.skills:
        elements[i][3] = TextElement(f"> {skill.formatted_name}")
        i += 1

    return new_InfoBox(
        str(entity),
        elements,
        width=FOE_STATUS_MENU_WIDTH,
    )


def create_event_dialog(dialog_element: dict[str, any]) -> new_InfoBox:
    """
    Return the interface of a dialog.

    Keyword arguments:
    dialog_element -- a data structure containing the title and the content of the dialog
    """
    elements = [
        [TextElement(talk, font=fonts["ITEM_DESC_FONT"])]
        for talk in dialog_element["talks"]
    ]
    return new_InfoBox(
        dialog_element["title"],
        elements,
        width=DIALOG_WIDTH,
        title_color=ORANGE,
        visible_on_background=False
    )


def create_reward_menu(mission: Mission) -> InfoBox:
    """
    Return the interface for an accomplished mission.

    Keyword arguments:
    mission -- the concerned mission
    """
    entries = [
        [
            {
                "type": "text",
                "text": "Congratulations! Objective has been completed!",
                "font": fonts["ITEM_DESC_FONT"],
            }
        ]
    ]
    if mission.gold:
        entries.append(
            [{"type": "text", "text": f"Earned gold : {mission.gold} (all characters)"}]
        )
    for item in mission.items:
        entries.append([{"type": "text", "text": f"Earned item : {item}"}])

    return InfoBox(
        mission.description,
        "imgs/interface/PopUpMenu.png",
        entries,
        width=REWARD_MENU_WIDTH,
        close_button=lambda: close_function(False),
    )


def create_start_menu(buttons_callback: dict[str, Callable]) -> InfoBox:
    """
    Return the interface of the main menu of the game (in the start screen).
    """
    return new_InfoBox(
        "In the name of the Five Cats",
        [
            [
                Button(
                    title="New game",
                    callback=buttons_callback["new_game"]
                ),
            ],
            [
                Button(
                    title="Load game",
                    callback=buttons_callback["load_menu"]
                ),
            ],
            [
                Button(
                    title="Options",
                    callback=buttons_callback["options_menu"]
                ),
            ],
            [
                Button(
                    title="Exit game",
                    callback=buttons_callback["exit_game"]
                ),
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

    for i in range(len(values)):
        if values[i]["value"] == current_value:
            current_value_index = i

    return DynamicButton(
        base_title=formatted_name,
        values=values,
        callback=edit_parameter_callback,
        current_value_index=current_value_index
    )


def create_options_menu(
        parameters: dict[str, int], modify_option_function: Callable
) -> InfoBox:
    """
    Return the interface of the game options menu.

    Keyword arguments:
    parameters -- the dictionary containing all parameters with their current value
    """

    return new_InfoBox(
        "Options",
        [
            [
                load_parameter_button(
                    "Move speed :",
                    [
                        {"label": "Slow", "value": ANIMATION_SPEED // 2},
                        {"label": "Normal", "value": ANIMATION_SPEED},
                        {"label": "Fast", "value": ANIMATION_SPEED * 2},
                    ],
                    parameters["move_speed"],
                    lambda value: modify_option_function("move_speed", value),
                ),
            ],
            [
                load_parameter_button(
                    "Screen mode :",
                    [
                        {"label": "Window", "value": SCREEN_SIZE // 2},
                        {"label": "Full", "value": SCREEN_SIZE},
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
                    title=f"Save {i+1}",
                    callback=lambda slot_id=i: load_game_function(slot_id)
                )
            ]
        )

    return new_InfoBox(
        "Load Game",
        element_grid,
        width=START_MENU_WIDTH
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
                    title=f"Save {i+1}",
                    callback=lambda slot_id=i: save_game_function(slot_id),
                )
            ]
        )

    return new_InfoBox(
        "Save Game",
        element_grid,
        width=START_MENU_WIDTH
    )
