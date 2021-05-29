"""
Define functions creating a specific menu enveloping data from parameters.
"""

from typing import Sequence, Union, Callable

import pygame

from src.constants import TILE_SIZE, ITEM_MENU_WIDTH, \
    ORANGE, WHITE, ITEM_BUTTON_SIZE_EQ, \
    EQUIPMENT_MENU_WIDTH, TRADE_MENU_WIDTH, GREEN, YELLOW, RED, \
    DARK_GREEN, GOLD, TURQUOISE, STATUS_MENU_WIDTH, \
    ACTION_MENU_WIDTH, BATTLE_SUMMARY_WIDTH, ITEM_BUTTON_SIZE, \
    ITEM_INFO_MENU_WIDTH, STATUS_INFO_MENU_WIDTH, \
    FOE_STATUS_MENU_WIDTH, DIALOG_WIDTH, REWARD_MENU_WIDTH, \
    START_MENU_WIDTH, ANIMATION_SPEED, SCREEN_SIZE, SAVE_SLOTS
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
from src.services.menus import BuyMenu, SellMenu, InventoryMenu, EquipmentMenu, \
    TradeMenu, StatusMenu, CharacterMenu, MainMenu, ItemMenu, StartMenu, \
    OptionsMenu, SaveMenu, LoadMenu

MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10

close_function: Union[Callable, None] = None


def create_shop_menu(stock: Sequence[dict[str, Union[Item, int]]], gold: int) -> InfoBox:
    """
    Return the interface of a shop menu with user as the buyer.

    Keyword arguments:
    stock -- the collection of items that are available in the shop, with the quantity of each one
    gold -- the amount of gold that should be displayed at the bottom
    """
    entries = []
    row = []
    for item in stock:
        entry = {'type': 'item_button', 'item': item['item'], 'price': item['item'].price,
                 'quantity': item['quantity'], 'id': BuyMenu.INTERAC_BUY}
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []

    if row:
        entries.append(row)

    # Gold at end
    entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    return InfoBox("Shop - Buying", "imgs/interface/PopUpMenu.png", entries, id_type=BuyMenu,
                   width=ITEM_MENU_WIDTH, close_button=lambda: close_function(False),
                   title_color=ORANGE)


def create_inventory_menu(items: Sequence[Item], gold: int,
                          is_to_sell: bool = False) -> InfoBox:
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
    for i, it in enumerate(items):
        entry = {'type': 'item_button', 'item': it, 'index': i, 'id': method_id}
        # Test if price should appeared
        if is_to_sell and it:
            entry['price'] = it.resell_price
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []
    if row:
        entries.append(row)

    # Gold at end
    entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    title = "Shop - Selling" if is_to_sell else "Inventory"
    menu_id = SellMenu if is_to_sell else InventoryMenu
    title_color = ORANGE if is_to_sell else WHITE
    return InfoBox(title, "imgs/interface/PopUpMenu.png", entries, id_type=menu_id,
                   width=ITEM_MENU_WIDTH, close_button=lambda: close_function(False),
                   title_color=title_color)


def create_equipment_menu(equipments: Sequence[Equipment]) -> InfoBox:
    """
    Return the interface of a player equipment.

    Keyword arguments:
    equipments -- the collection of equipments currently equipped by the player
    """
    entries = []
    body_parts = [['head'], ['body'], ['right_hand', 'left_hand'], ['feet']]
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
            entry = {'type': 'item_button', 'item': equipment,
                     'index': index, 'size': ITEM_BUTTON_SIZE_EQ, 'id':
                         EquipmentMenu.INTERAC_EQUIPMENT}
            row.append(entry)
        entries.append(row)
    return InfoBox("Equipment", "imgs/interface/PopUpMenu.png", entries, id_type=EquipmentMenu,
                   width=EQUIPMENT_MENU_WIDTH, close_button=lambda: close_function(False))


def create_trade_menu(first_player: Player, second_player: Player) -> InfoBox:
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
                entry = {'type': 'item_button', 'item': items[i * 2 + j],
                         'index': i, 'subtype': 'trade', 'id': method_id,
                         'args': [first_player, second_player, owner_i]}
                row.append(entry)
        entries.append(row)

    # Buttons to trade gold
    method_id = TradeMenu.SEND_GOLD
    entry = [
        {'type': 'button', 'name': '50G ->', 'size': (90, 30),
         'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 0, 50]},
        {'type': 'button', 'name': '200G ->', 'size': (90, 30),
         'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 0, 200]},
        {'type': 'button', 'name': 'All ->', 'size': (90, 30),
         'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 0, first_player.gold]},
        {'type': 'button', 'name': '<- 50G', 'size': (90, 30),
         'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 1, 50]},
        {'type': 'button', 'name': '<- 200G', 'size': (90, 30),
         'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 1, 200]},
        {'type': 'button', 'name': '<- All', 'size': (90, 30),
         'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 1, second_player.gold]}]
    entries.append(entry)

    # Gold at end
    entry = [{'type': 'text', 'text': str(first_player) + '\'s gold : ' + str(first_player.gold),
              'font': fonts['ITEM_DESC_FONT']},
             {'type': 'text', 'text': str(second_player) + '\'s gold : ' + str(second_player.gold),
              'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    title = "Trade"
    menu_id = TradeMenu
    title_color = WHITE
    return InfoBox(title, "imgs/interface/PopUpMenu.png", entries, id_type=menu_id,
                   width=TRADE_MENU_WIDTH, close_button=lambda: close_function(False),
                   separator=True, title_color=title_color)


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


def create_status_menu(player: Player) -> InfoBox:
    """
    Return the interface resuming the status of a player.

    Keyword arguments:
    player -- the concerned player
    """
    entries = [
        [{}, {'type': 'text', 'color': GREEN, 'text': 'Name :', 'font': fonts['ITALIC_ITEM_FONT']},
         {'type': 'text', 'text': str(player)}, {}],
        [{}, {}, {'type': 'text', 'color': DARK_GREEN, 'text': 'SKILLS',
                  'font': fonts['MENU_SUB_TITLE_FONT'], 'margin': (10, 0, 10, 0)}],
        [{'type': 'text', 'color': GREEN, 'text': 'Class :', 'font': fonts['ITALIC_ITEM_FONT']},
         {'type': 'text', 'text': player.get_formatted_classes()}],
        [{'type': 'text', 'color': GREEN, 'text': 'Race :', 'font': fonts['ITALIC_ITEM_FONT']},
         {'type': 'text', 'text': player.get_formatted_race()}],
        [{'type': 'text', 'color': GREEN, 'text': 'Level :', 'font': fonts['ITALIC_ITEM_FONT']},
         {'type': 'text', 'text': str(player.lvl)}],
        [{'type': 'text', 'color': GOLD, 'text': '   XP :', 'font': fonts['ITALIC_ITEM_FONT']},
         {'type': 'text', 'text': f'{player.experience} / {player.experience_to_lvl_up}'}],
        [{'type': 'text', 'color': DARK_GREEN, 'text': 'STATS',
          'font': fonts['MENU_SUB_TITLE_FONT'], 'margin': (10, 0, 10, 0)}],
        [{'type': 'text', 'color': WHITE, 'text': 'HP :'},
         {'type': 'text', 'text': f'{player.hit_points} / {player.hit_points_max}',
          'color': determine_hp_color(player.hit_points, player.hit_points_max)}],
        [{'type': 'text', 'color': WHITE, 'text': 'MOVE :'},
         {'type': 'text',
          'text': str(player.max_moves) + player.get_formatted_stat_change('speed')}],
        [{'type': 'text', 'color': WHITE, 'text': 'CONSTITUTION :'},
         {'type': 'text', 'text': str(player.constitution)}],
        [{'type': 'text', 'color': WHITE, 'text': 'ATTACK :'},
         {'type': 'text',
          'text': str(player.strength) + player.get_formatted_stat_change('strength')}],
        [{'type': 'text', 'color': WHITE, 'text': 'DEFENSE :'},
         {'type': 'text',
          'text': str(player.defense) + player.get_formatted_stat_change('defense')}],
        [{'type': 'text', 'color': WHITE, 'text': 'MAGICAL RES :'},
         {'type': 'text',
          'text': str(player.resistance) + player.get_formatted_stat_change('resistance')}],
        [{'type': 'text', 'color': DARK_GREEN, 'text': 'ALTERATIONS',
          'font': fonts['MENU_SUB_TITLE_FONT'],
          'margin': (10, 0, 10, 0)}]]

    alts = player.alterations
    if not alts:
        entries.append([{'type': 'text', 'color': WHITE, 'text': 'None'}])
    for alt in alts:
        entries.append([{'type': 'text_button', 'name': str(alt), 'id': StatusMenu.INFO_ALTERATION,
                         'color': WHITE, 'color_hover': TURQUOISE, 'obj': alt}])

    # Display skills
    i = 2
    for skill in player.skills:
        skill_displayed = {'type': 'text_button', 'name': skill.formatted_name,
                           'id': StatusMenu.INFO_SKILL,
                           'color': WHITE, 'color_hover': TURQUOISE, 'obj': skill}
        entries[i].append(skill_displayed)
        i += 1
    for j in range(i, len(entries)):
        entries[j].append({})

    return InfoBox("Status", "imgs/interface/PopUpMenu.png", entries, id_type=StatusMenu,
                   width=STATUS_MENU_WIDTH, close_button=lambda: close_function(False))


def create_player_menu(buttons_callback: dict[str, Callable], player: Player,
                       buildings: Sequence[Building], interactable_entities: Sequence[Entity],
                       missions: Sequence[Mission], foes: Sequence[Foe]) -> InfoBox:
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
    entries = [[{'name': 'Inventory', 'callback': buttons_callback['inventory']}],
               [{'name': 'Equipment', 'callback': buttons_callback['equipment']}],
               [{'name': 'Status', 'callback': buttons_callback['status']}],
               [{'name': 'Wait', 'callback': buttons_callback['wait']}]]

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
                entries.insert(0, [{'name': 'Visit', 'callback': buttons_callback['visit']}])
                break

    for entity in interactable_entities:
        if abs(entity.position[0] - player.position[0]) + abs(
                entity.position[1] - player.position[1]) == TILE_SIZE:
            if isinstance(entity, Player):
                if not trade_option:
                    entries.insert(0, [{'name': 'Trade', 'callback': buttons_callback['trade']}])
                    trade_option = True
            elif isinstance(entity, Chest):
                if not entity.opened and not chest_option:
                    entries.insert(0, [{'name': 'Open Chest', 'callback': buttons_callback['open_chest']}]
                                   )
                    chest_option = True
                if 'lock_picking' in player.skills and not pick_lock_option:
                    entries.insert(0, [{'name': 'Pick Lock', 'callback': buttons_callback['pick_lock']}])
                    pick_lock_option = True
            elif isinstance(entity, Door):
                if not door_option:
                    entries.insert(0, [{'name': 'Open Door', 'callback': buttons_callback['open_door']}])
                    door_option = True
                if 'lock_picking' in player.skills and not pick_lock_option:
                    entries.insert(0, [{'name': 'Pick Lock', 'callback': buttons_callback['pick_lock']}])
                    pick_lock_option = True
            elif isinstance(entity, Portal):
                if not portal_option:
                    entries.insert(0, [{'name': 'Use Portal', 'callback': buttons_callback['use_portal']}]
                                   )
                    portal_option = True
            elif isinstance(entity, Fountain):
                if not fountain_option:
                    entries.insert(0, [{'name': 'Drink', 'callback': buttons_callback['drink']}])
                    fountain_option = True
            elif isinstance(entity, Character):
                if not talk_option:
                    entries.insert(0, [{'name': 'Talk', 'callback': buttons_callback['talk']}])
                    talk_option = True

    # Check if player is on mission position
    for mission in missions:
        if mission.type is MissionType.POSITION or mission.type is MissionType.TOUCH_POSITION:
            if mission.is_position_valid(player.position):
                entries.insert(0, [{'name': 'Take', 'callback': buttons_callback['take']}])

    # Check if player could attack something, according to weapon range
    if player.can_attack():
        w_range = [1] if player.get_weapon() is None else player.get_weapon().reach
        end = False
        for foe in foes:
            for reach in w_range:
                if abs(foe.position[0] - player.position[0]) + abs(
                        foe.position[1] - player.position[1]) == TILE_SIZE * reach:
                    entries.insert(0, [{'name': 'Attack', 'callback': buttons_callback['attack']}])
                    end = True
                    break
            if end:
                break

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("Select an action", "imgs/interface/PopUpMenu.png", entries,
                   id_type=CharacterMenu, width=ACTION_MENU_WIDTH, element_linked=player.get_rect())


def create_diary_menu(entries: Entries) -> InfoBox:
    """
    Return the interface of the diary resuming the last battle logs of a specific player.

    Keyword arguments:
    entries -- the entries data structure containing all the data needed to build the interface
    """
    return InfoBox("Diary", "imgs/interface/PopUpMenu.png", entries, width=BATTLE_SUMMARY_WIDTH,
                   close_button=lambda: close_function(False))


def create_main_menu(buttons_callback: dict[str, Callable],
                     is_initialization_phase: bool, position: Position) -> InfoBox:
    """
    Return the interface of the main level menu.

    Keyword arguments:
    is_initialization_phase -- a boolean value indicating whether
    it is the initialization phase or not
    position -- the position where the pop-up should be on screen
    """
    # Transform pos tuple into rect
    tile = pygame.Rect(position[0], position[1], 1, 1)
    entries = [[{'name': 'Save', 'callback': buttons_callback['save']}],
               [{'name': 'Suspend', 'callback': buttons_callback['suspend']}]]

    if is_initialization_phase:
        entries.append([{'name': 'Start', 'callback': buttons_callback['start']}])
    else:
        entries.append([{'name': 'Diary', 'callback': buttons_callback['diary']}]),
        entries.append([{'name': 'End Turn', 'callback': buttons_callback['end_turn']}])

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("Main Menu", "imgs/interface/PopUpMenu.png", entries, id_type=MainMenu,
                   width=ACTION_MENU_WIDTH, element_linked=tile)


def create_item_shop_menu(item_button_position: Position, item: Item) -> InfoBox:
    """
    Return the interface of an item that is on sale in a shop.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    """
    entries = [
        [{'name': 'Buy', 'id': ItemMenu.BUY_ITEM, 'type': 'button'}],
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
    ]
    formatted_item_name = str(item)
    item_rect = pygame.Rect(item_button_position[0] - 20, item_button_position[1],
                            ITEM_BUTTON_SIZE[0], ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, "imgs/interface/PopUpMenu.png", entries, id_type=ItemMenu,
                   width=ACTION_MENU_WIDTH, element_linked=item_rect, close_button=lambda: close_function(False))


def create_item_sell_menu(item_button_position: Position, item: Item) -> InfoBox:
    """
    Return the interface of an item that is in a player inventory and can be sold in a shop.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    """
    entries = [
        [{'name': 'Sell', 'id': ItemMenu.SELL_ITEM, 'type': 'button'}],
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
    ]
    formatted_item_name = str(item)
    item_rect = pygame.Rect(item_button_position[0] - 20, item_button_position[1],
                            ITEM_BUTTON_SIZE[0], ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, "imgs/interface/PopUpMenu.png", entries, id_type=ItemMenu,
                   width=ACTION_MENU_WIDTH, element_linked=item_rect, close_button=lambda: close_function(False))


def create_trade_item_menu(item_button_position: Position,
                           item: Item, players: Sequence[Player]) -> InfoBox:
    """
    Return the interface of an item that is in a player inventory
    and can be trade to another player.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    players -- the two players that are currently involve in the trade
    """
    entries = [
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
        [{'name': 'Trade', 'id': ItemMenu.TRADE_ITEM, 'args': players}]
    ]
    formatted_item_name = str(item)

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    item_rect = pygame.Rect(item_button_position[0] - 20, item_button_position[1],
                            ITEM_BUTTON_SIZE[0], ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, "imgs/interface/PopUpMenu.png", entries, id_type=ItemMenu,
                   width=ACTION_MENU_WIDTH, element_linked=item_rect, close_button=lambda: close_function(False))


def create_item_menu(item_button_position: Position, item: Item,
                     is_equipped: bool = False) -> InfoBox:
    """
    Return the interface of an item of a player.

    Keyword arguments:
    item_button_position -- the position of the item (so the pop-up could be displayed beside it)
    item -- the concerned item
    is_equipped -- a boolean value indicating whether the item is currently equipped or not
    """
    entries = [
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
        [{'name': 'Throw', 'id': ItemMenu.THROW_ITEM}]
    ]
    formatted_item_name = str(item)

    if isinstance(item, Consumable):
        entries.insert(0, [{'name': 'Use', 'id': ItemMenu.USE_ITEM}])
    elif isinstance(item, Equipment):
        if is_equipped:
            entries.insert(0, [{'name': 'Unequip', 'id': ItemMenu.UNEQUIP_ITEM}])
        else:
            entries.insert(0, [{'name': 'Equip', 'id': ItemMenu.EQUIP_ITEM}])

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    item_rect = pygame.Rect(item_button_position[0] - 20, item_button_position[1],
                            ITEM_BUTTON_SIZE[0], ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, "imgs/interface/PopUpMenu.png", entries, id_type=ItemMenu,
                   width=ACTION_MENU_WIDTH, element_linked=item_rect, close_button=lambda: close_function(False))


def create_item_description_stat(stat_name: str, stat_value: str) -> EntryLine:
    """
    Return the entry line for the formatted display of an item stat description.

    Keyword arguments:
    stat_name -- the name of the statistic
    stat_value -- the value of the statistic
    """
    return [{'type': 'text', 'text': f'{stat_name} : ', 'font': fonts['ITEM_DESC_FONT'],
             'margin': (0, 0, 0, 100)},
            {'type': 'text', 'text': stat_value, 'font': fonts['ITEM_DESC_FONT'],
             'margin': (0, 100, 0, 0)}]


def create_item_description_menu(item: Item) -> InfoBox:
    """
    Return the interface for the full description of an item.

    Keyword arguments:
    item -- the concerned item
    """
    item_title = str(item)

    entries = [[{'type': 'text', 'text': item.description, 'font': fonts['ITEM_DESC_FONT'],
                 'margin': (20, 0, 20, 0)}]]

    if isinstance(item, Equipment):
        if item.restrictions != {}:
            entries.append(create_item_description_stat('RESERVED TO',
                                                        item.get_formatted_restrictions()))
        if item.attack > 0:
            entries.append(create_item_description_stat('POWER', str(item.attack)))
        if item.defense > 0:
            entries.append(create_item_description_stat('DEFENSE', str(item.defense)))
        if item.resistance > 0:
            entries.append(create_item_description_stat('MAGICAL RES', str(item.resistance)))
        if isinstance(item, Weapon):
            # Compute reach
            reach_txt = ""
            for distance in item.reach:
                reach_txt += str(distance) + ', '
            reach_txt = reach_txt[:len(reach_txt) - 2]
            entries.append(create_item_description_stat('TYPE OF DAMAGE',
                                                        str(item.attack_kind.value)))
            entries.append(create_item_description_stat('REACH', reach_txt))
            for possible_effect in item.effects:
                entries.append(create_item_description_stat(
                    'EFFECT', f'{possible_effect["effect"]} ({possible_effect["probability"]}%)'))
            strong_against_formatted = item.get_formatted_strong_against()
            if strong_against_formatted:
                entries.append(create_item_description_stat('STRONG AGAINST',
                                                            strong_against_formatted))
        if isinstance(item, Shield):
            entries.append(create_item_description_stat('PARRY RATE', str(item.parry) + '%'))
        if isinstance(item, (Shield, Weapon)):
            entries.append(create_item_description_stat(
                'DURABILITY', f'{item.durability} / {item.durability_max}'))
        entries.append(create_item_description_stat('WEIGHT', str(item.weight)))
    elif isinstance(item, Consumable):
        for effect in item.effects:
            entries.append(create_item_description_stat('EFFECT', effect.get_formatted_desc()))

    return InfoBox(item_title, "imgs/interface/PopUpMenu.png", entries, width=ITEM_INFO_MENU_WIDTH,
                   close_button=lambda: close_function(False))


def create_alteration_info_menu(alteration: Alteration) -> InfoBox:
    """
    Return the interface for the description of an alteration.

    Keyword arguments:
    alteration -- the concerned alteration
    """
    turns_left = alteration.get_turns_left()
    entries = [[{'type': 'text', 'text': alteration.description,
                 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}],
               [{'type': 'text', 'text': f'Turns left : {turns_left}',
                 'font': fonts['ITEM_DESC_FONT'], 'margin': (0, 0, 10, 0), 'color': ORANGE}]]

    return InfoBox(str(alteration), "imgs/interface/PopUpMenu.png", entries,
                   width=STATUS_INFO_MENU_WIDTH, close_button=lambda: close_function(False))


def create_skill_info_menu(skill: Skill) -> InfoBox:
    """
    Return the interface for the description of a skill.

    Keyword arguments:
    skill -- the concerned skill
    """
    entries = [[{'type': 'text', 'text': skill.description,
                 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}],
               [{'type': 'text', 'text': '', 'margin': (0, 0, 10, 0)}]]

    return InfoBox(skill.formatted_name, "imgs/interface/PopUpMenu.png", entries,
                   width=STATUS_INFO_MENU_WIDTH, close_button=lambda: close_function(False))


def create_status_entity_menu(entity: Entity) -> InfoBox:
    """
    Return the interface for the status screen of an entity.

    Keyword arguments:
    entity -- the concerned entity
    """
    keywords_display = entity.get_formatted_keywords() if isinstance(entity, Foe) else ''
    entries = [[{'type': 'text', 'text': keywords_display,
                 'font': fonts['ITALIC_ITEM_FONT']}],
               [{'type': 'text', 'text': f'LEVEL : {entity.lvl}', 'font': fonts['ITEM_DESC_FONT']}],
               [{'type': 'text', 'text': 'ATTACK',
                 'font': fonts['MENU_SUB_TITLE_FONT'], 'color': DARK_GREEN,
                 'margin': (20, 0, 20, 0)}, {}, {},
                {'type': 'text', 'text': 'LOOT',
                 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'color': DARK_GREEN,
                 'margin': (20, 0, 20, 0)}
                if isinstance(entity, Foe) else {}, {}],
               [{'type': 'text', 'text': 'TYPE :'},
                {'type': 'text', 'text': str(entity.attack_kind.value)}, {}, {}, {}],
               [{'type': 'text', 'text': 'REACH :'},
                {'type': 'text', 'text': entity.get_formatted_reach()}, {}, {}, {}],
               [{}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}],
               [{'type': 'text', 'text': 'STATS',
                 'font': fonts['MENU_SUB_TITLE_FONT'], 'color': DARK_GREEN,
                 'margin': (10, 0, 10, 0)}, {}, {}, {'type': 'text', 'text': 'SKILLS',
                                                     'font': fonts['MENU_SUB_TITLE_FONT'],
                                                     'color': DARK_GREEN,
                                                     'margin': (10, 0, 10, 0)}, {}],
               [{'type': 'text', 'text': 'HP :'},
                {'type': 'text', 'text': f'{entity.hit_points} / {entity.hit_points_max}',
                 'color': determine_hp_color(entity.hit_points, entity.hit_points_max)},
                {}, {}, {}],
               [{'type': 'text', 'text': 'MOVE :'},
                {'type': 'text', 'text': str(entity.max_moves)}, {}, {}, {}],
               [{'type': 'text', 'text': 'ATTACK :'},
                {'type': 'text', 'text': str(entity.strength)}, {}, {}, {}],
               [{'type': 'text', 'text': 'DEFENSE :'},
                {'type': 'text', 'text': str(entity.defense)}, {}, {}, {}],
               [{'type': 'text', 'text': 'MAGICAL RES :'},
                {'type': 'text', 'text': str(entity.resistance)}, {}, {}, {}],
               [{'type': 'text', 'text': 'ALTERATIONS',
                 'font': fonts['MENU_SUB_TITLE_FONT'], 'color': DARK_GREEN,
                 'margin': (10, 0, 10, 0)}]]

    alts = entity.alterations
    if not alts:
        entries.append([{'type': 'text', 'text': 'None'}])
    for alt in alts:
        entries.append([{'type': 'text_button', 'name': str(alt), 'id': StatusMenu.INFO_ALTERATION,
                         'color': WHITE,
                         'color_hover': TURQUOISE, 'obj': alt}])

    if isinstance(entity, Foe):
        loot = entity.potential_loot
        i = 3
        for (item, probability) in loot:
            name = str(item)
            entries[i][3] = {'type': 'text', 'text': name}
            entries[i][4] = {'type': 'text', 'text': f' ({probability * 100} %)'}
            i += 1

    # Display skills
    i = 7
    for skill in entity.skills:
        entries[i][3] = {'type': 'text', 'text': '> ' + skill.formatted_name}
        i += 1

    return InfoBox(str(entity), "imgs/interface/PopUpMenu.png", entries, StatusMenu,
                   FOE_STATUS_MENU_WIDTH, close_button=lambda: close_function(False))


def create_event_dialog(dialog_element: dict[str, any]) -> InfoBox:
    """
    Return the interface of a dialog.

    Keyword arguments:
    dialog_element -- a data structure containing the title and the content of the dialog
    """
    entries = [[{'type': 'text', 'text': talk, 'font': fonts['ITEM_DESC_FONT']}]
               for talk in dialog_element['talks']]
    return InfoBox(dialog_element['title'], "imgs/interface/PopUpMenu.png", entries,
                   width=DIALOG_WIDTH, close_button=lambda: close_function(False),
                   title_color=ORANGE)


def create_reward_menu(mission: Mission) -> InfoBox:
    """
    Return the interface for an accomplished mission.

    Keyword arguments:
    mission -- the concerned mission
    """
    entries = [
        [{'type': 'text', 'text': 'Congratulations! Objective has been completed!',
          'font': fonts['ITEM_DESC_FONT']}]]
    if mission.gold:
        entries.append([{'type': 'text', 'text': f'Earned gold : {mission.gold} (all characters)'}])
    for item in mission.items:
        entries.append([{'type': 'text', 'text': f'Earned item : {item}'}])

    return InfoBox(mission.description, "imgs/interface/PopUpMenu.png", entries,
                   width=REWARD_MENU_WIDTH, close_button=lambda: close_function(False))


def create_start_menu(buttons_callback: dict[str, Callable]) -> InfoBox:
    """
    Return the interface of the main menu of the game (in the start screen).
    """
    entries = [[{'name': 'New game', 'callback': buttons_callback['new_game']}],
               [{'name': 'Load game', 'callback': buttons_callback['load_menu']}],
               [{'name': 'Options', 'callback': buttons_callback['options_menu']}],
               [{'name': 'Exit game', 'callback': buttons_callback['exit_game']}]]

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("In the name of the Five Cats", "imgs/interface/PopUpMenu.png", entries,
                   id_type=StartMenu, width=START_MENU_WIDTH)


def load_parameter_entry(formatted_name: str, values: Sequence[dict[str, int]], current_value: int,
                         edit_parameter_callback: Callable) -> Entry:
    """
    Return an entry corresponding to the data of a specific game parameter.

    Keyword arguments:
    formatted_name -- the formatted name of the parameter
    values -- the sequence of values that can be taken by the parameter
    current_value -- the current value of the parameter
    identifier -- the identifier of the parameter
    """
    entry = {'type': 'parameter_button', 'name': formatted_name, 'values': values,
             'callback': edit_parameter_callback, 'current_value_ind': 0}

    for i in range(len(entry['values'])):
        if entry['values'][i]['value'] == current_value:
            entry['current_value_ind'] = i

    return entry


def create_options_menu(parameters: dict[str, int], modify_option_function: Callable) -> InfoBox:
    """
    Return the interface of the game options menu.

    Keyword arguments:
    parameters -- the dictionary containing all parameters with their current value
    """
    entries = [[load_parameter_entry("Move speed :",
                                     [{'label': 'Slow', 'value': ANIMATION_SPEED // 2},
                                      {'label': 'Normal', 'value': ANIMATION_SPEED},
                                      {'label': 'Fast', 'value': ANIMATION_SPEED * 2}],
                                     parameters['move_speed'],
                                     lambda value: modify_option_function('move_speed', value))],
               [load_parameter_entry("Screen mode :",
                                     [{'label': 'Window', 'value': SCREEN_SIZE // 2},
                                      {'label': 'Full', 'value': SCREEN_SIZE}],
                                     parameters['screen_size'],
                                     lambda value: modify_option_function('screen_size', value))]]

    return InfoBox("Options", "imgs/interface/PopUpMenu.png", entries, id_type=OptionsMenu,
                   width=START_MENU_WIDTH, close_button=close_function)


def create_load_menu(load_game_function: Callable) -> InfoBox:
    """
    Return the interface of the load game menu.
    """
    entries = []

    for i in range(SAVE_SLOTS):
        entries.append([{'type': 'button', 'name': 'Save ' + str(i + 1),
                         'callback': lambda slot_id=i: load_game_function(slot_id)}])

    return InfoBox("Load Game", "imgs/interface/PopUpMenu.png", entries, id_type=LoadMenu,
                   width=START_MENU_WIDTH, close_button=close_function)


def create_save_menu(save_game_function: Callable) -> InfoBox:
    """
    Return the interface of the save game menu
    """
    entries = []

    for i in range(SAVE_SLOTS):
        entries.append(
            [{'type': 'button', 'name': 'Save ' + str(i + 1),
              'callback': lambda slot_id=i: save_game_function(slot_id)}])

    return InfoBox("Save Game", "imgs/interface/PopUpMenu.png", entries, id_type=SaveMenu,
                   width=START_MENU_WIDTH, close_button=lambda: close_function(False))
