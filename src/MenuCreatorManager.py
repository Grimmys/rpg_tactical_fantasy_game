from src.Chest import Chest
from src.Character import Character
from src.Consumable import Consumable
from src.Equipment import Equipment
from src.Fountain import Fountain
from src.InfoBox import InfoBox
from src.Menus import *
from src.Mission import MissionType
from src.Player import Player
from src.Portal import Portal
from src.Shield import Shield
from src.Weapon import Weapon
from src.fonts import *
from src.constants import *

MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10


def create_shop_menu(items, gold):
    entries = []
    row = []
    for i, it in enumerate(items):
        entry = {'type': 'item_button', 'item': it, 'price': it.price, 'index': i, 'id': BuyMenu.INTERAC_BUY}
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []

    if row:
        entries.append(row)

    # Gold at end
    entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    return InfoBox("Shop - Buying", BuyMenu, "imgs/interface/PopUpMenu.png", entries,
                   ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)


def create_inventory_menu(items, gold, price=False):
    entries = []
    row = []
    method_id = SellMenu.INTERAC_SELL if price else InventoryMenu.INTERAC_ITEM
    for i, it in enumerate(items):
        entry = {'type': 'item_button', 'item': it, 'index': i, 'id': method_id}
        # Test if price should appeared
        if price and it:
            entry['price'] = it.price // 2 if it.price != 0 else 0
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []
    if row:
        entries.append(row)

    # Gold at end
    entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    title = "Shop - Selling" if price else "Inventory"
    menu_id = SellMenu if price else InventoryMenu
    title_color = ORANGE if price else WHITE
    return InfoBox(title, menu_id, "imgs/interface/PopUpMenu.png", entries,
                   ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION, title_color=title_color)


def create_equipment_menu(equipments):
    entries = []
    body_parts = [['head'], ['body'], ['right_hand', 'left_hand'], ['feet']]
    for part in body_parts:
        row = []
        for member in part:
            entry = {'type': 'item_button', 'item': None, 'index': -1,
                     'id': EquipmentMenu.INTERAC_EQUIPMENT}
            for i, eq in enumerate(equipments):
                if member == eq.body_part:
                    entry = {'type': 'item_button', 'item': eq, 'index': i,
                             'id': EquipmentMenu.INTERAC_EQUIPMENT}
            row.append(entry)
        entries.append(row)
    return InfoBox("Equipment", EquipmentMenu, "imgs/interface/PopUpMenu.png", entries,
                   EQUIPMENT_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_trade_menu(first_player, second_player):
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
                entry = {'type': 'item_button', 'item': items[i * 2 + j], 'index': i, 'subtype': 'trade',
                         'id': method_id, 'args': [first_player, second_player, owner_i]}
                row.append(entry)
        entries.append(row)

    # Gold at end
    entry = [{'type': 'text', 'text': first_player.get_formatted_name() + '\'s gold : ' + str(first_player.gold),
              'font': fonts['ITEM_DESC_FONT']},
             {'type': 'text', 'text': second_player.get_formatted_name() + '\'s gold : ' + str(second_player.gold),
             'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    title = "Trade"
    menu_id = TradeMenu
    title_color = WHITE
    return InfoBox(title, menu_id, "imgs/interface/PopUpMenu.png", entries,
                   TRADE_MENU_WIDTH, close_button=UNFINAL_ACTION, sep=True, title_color=title_color)


def determine_hp_color(hp, hp_max):
    if hp == hp_max:
        return WHITE
    if hp >= hp_max * 0.75:
        return GREEN
    if hp >= hp_max * 0.5:
        return YELLOW
    if hp >= hp_max * 0.30:
        return ORANGE
    else:
        return RED


def create_status_menu(player):
    entries = [[{'type': 'text', 'color': GREEN, 'text': 'Name :', 'font': fonts['ITALIC_ITEM_FONT']},
                {'type': 'text', 'text': player.get_formatted_name()}],
               [{'type': 'text', 'color': GREEN, 'text': 'Class :', 'font': fonts['ITALIC_ITEM_FONT']},
                {'type': 'text', 'text': player.get_formatted_classes()}],
               [{'type': 'text', 'color': GREEN, 'text': 'Race :', 'font': fonts['ITALIC_ITEM_FONT']},
                {'type': 'text', 'text': player.get_formatted_race()}],
               [{'type': 'text', 'color': GREEN, 'text': 'Level :', 'font': fonts['ITALIC_ITEM_FONT']},
                {'type': 'text', 'text': str(player.lvl)}],
               [{'type': 'text', 'color': GOLD, 'text': '   XP :', 'font': fonts['ITALIC_ITEM_FONT']},
                {'type': 'text', 'text': str(player.xp) + ' / ' + str(player.xp_next_lvl)}],
               [{'type': 'text', 'color': WHITE, 'text': 'STATS', 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'margin': (10, 0, 10, 0)}],
               [{'type': 'text', 'color': WHITE, 'text': 'HP :'},
                {'type': 'text', 'text': str(player.hp) + ' / ' + str(player.hp_max),
                 'color': determine_hp_color(player.hp, player.hp_max)}],
               [{'type': 'text', 'color': WHITE, 'text': 'MOVE :'},
                {'type': 'text', 'text': str(player.max_moves)}],
               [{'type': 'text', 'color': WHITE, 'text': 'ATTACK :'},
                {'type': 'text', 'text': str(player.strength)}],
               [{'type': 'text', 'color': WHITE, 'text': 'DEFENSE :'},
                {'type': 'text', 'text': str(player.defense)}],
               [{'type': 'text', 'color': WHITE, 'text': 'MAGICAL RES :'},
                {'type': 'text', 'text': str(player.res)}],
               [{'type': 'text', 'color': WHITE, 'text': 'ALTERATIONS', 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'margin': (10, 0, 10, 0)}]]

    alts = player.alterations
    if not alts:
        entries.append([{'type': 'text', 'color': WHITE, 'text': 'None'}])
    for alt in alts:
        entries.append([{'type': 'text_button', 'name': alt.get_formatted_name(), 'id': StatusMenu.INFO_ALTERATION,
                         'color': WHITE, 'color_hover': TURQUOISE, 'obj': alt}])

    return InfoBox("Status", StatusMenu, "imgs/interface/PopUpMenu.png", entries,
                   STATUS_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_player_menu(player, buildings, interact_entities, missions, foes):
    entries = [[{'name': 'Inventory', 'id': CharacterMenu.INV}],
               [{'name': 'Equipment', 'id': CharacterMenu.EQUIPMENT}],
               [{'name': 'Status', 'id': CharacterMenu.STATUS}], [{'name': 'Wait', 'id': CharacterMenu.WAIT}]]

    # Options flags
    chest_option = False
    portal_option = False
    fountain_option = False
    talk_option = False
    trade_option = False

    case_pos = (player.pos[0], player.pos[1] - TILE_SIZE)
    if (0, 0) < case_pos < (MAP_WIDTH, MAP_HEIGHT):
        for building in buildings:
            if building.pos == case_pos:
                entries.insert(0, [{'name': 'Visit', 'id': CharacterMenu.VISIT}])
                break

    for ent in interact_entities:
        if abs(ent.pos[0] - player.pos[0]) + abs(ent.pos[1] - player.pos[1]) == TILE_SIZE:
            if isinstance(ent, Player):
                if not trade_option:
                    entries.insert(0, [{'name': 'Trade', 'id': CharacterMenu.TRADE}])
                    trade_option = True
            elif isinstance(ent, Chest):
                if not ent.opened and not chest_option:
                    entries.insert(0, [{'name': 'Open', 'id': CharacterMenu.OPEN_CHEST}])
                    chest_option = True
            elif isinstance(ent, Portal):
                if not portal_option:
                    entries.insert(0, [{'name': 'Use Portal', 'id': CharacterMenu.USE_PORTAL}])
                    portal_option = True
            elif isinstance(ent, Fountain):
                if not fountain_option:
                    entries.insert(0, [{'name': 'Drink', 'id': CharacterMenu.DRINK}])
                    fountain_option = True
            elif isinstance(ent, Character):
                if not talk_option:
                    entries.insert(0, [{'name': 'Talk', 'id': CharacterMenu.TALK}])
                    talk_option = True

    # Check if player is on mission position
    for mission in missions:
        if mission.type is MissionType.POSITION:
            if mission.pos_is_valid(player.pos):
                entries.insert(0, [{'name': 'Take', 'id': CharacterMenu.TAKE}])

    # Check if player could attack something, according to weapon range
    w_range = [1] if player.get_weapon() is None else player.get_weapon().reach
    end = False
    for foe in foes:
        for reach in w_range:
            if abs(foe.pos[0] - player.pos[0]) + abs(foe.pos[1] - player.pos[1]) == TILE_SIZE * reach:
                entries.insert(0, [{'name': 'Attack', 'id': CharacterMenu.ATTACK}])
                end = True
                break
        if end:
            break

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("Select an action", CharacterMenu, "imgs/interface/PopUpMenu.png",
                   entries, ACTION_MENU_WIDTH, el_rect_linked=player.get_rect())


def create_main_menu(initialization_phase, pos):
    # Transform pos tuple into rect
    tile = pg.Rect(pos[0], pos[1], 1, 1)
    entries = [[{'name': 'Save', 'id': MainMenu.SAVE}],
               [{'name': 'Suspend', 'id': MainMenu.SUSPEND}]]

    if initialization_phase:
        entries.append([{'name': 'Start', 'id': MainMenu.START}])
    else:
        entries.append([{'name': 'End Turn', 'id': MainMenu.END_TURN}])

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("Main Menu", MainMenu, "imgs/interface/PopUpMenu.png", entries,
                   ACTION_MENU_WIDTH, el_rect_linked=tile)


def create_item_shop_menu(item_button_pos, item, price):
    entries = [
        [{'name': 'Buy', 'id': ItemMenu.BUY_ITEM, 'type': 'button', 'args': [price]}],
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
    ]
    formatted_item_name = item.get_formatted_name()
    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                   entries, ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_item_sell_menu(item_button_pos, item, price):
    entries = [
        [{'name': 'Sell', 'id': ItemMenu.SELL_ITEM, 'type': 'button', 'args': [price]}],
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
    ]
    formatted_item_name = item.get_formatted_name()
    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                   entries, ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_trade_item_menu(item_button_pos, item, players):
    entries = [
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
        [{'name': 'Trade', 'id': ItemMenu.TRADE_ITEM, 'args': players}]
    ]
    formatted_item_name = item.get_formatted_name()

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                   entries,
                   ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_item_menu(item_button_pos, item, is_equipped=False):
    entries = [
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
        [{'name': 'Throw', 'id': ItemMenu.THROW_ITEM}]
    ]
    formatted_item_name = item.get_formatted_name()

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

    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.png",
                   entries,
                   ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_item_desc_stat(stat_name, stat_value):
    return [{'type': 'text', 'text': stat_name + ' : ', 'font': fonts['ITEM_DESC_FONT'], 'margin': (0, 0, 0, 200)},
            {'type': 'text', 'text': stat_value, 'font': fonts['ITEM_DESC_FONT'], 'margin': (0, 200, 0, 0)}]


def create_item_desc_menu(item):
    item_title = item.get_formatted_name()

    entries = [[{'type': 'text', 'text': item.desc, 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}]]

    if isinstance(item, Equipment):
        if item.restrictions != {}:
            entries.append(create_item_desc_stat('RESERVED TO', item.get_formatted_restrictions()))
        if item.atk > 0:
            entries.append(create_item_desc_stat('POWER', str(item.atk)))
        if item.defense > 0:
            entries.append(create_item_desc_stat('DEFENSE', str(item.defense)))
        if item.res > 0:
            entries.append(create_item_desc_stat('MAGICAL RES', str(item.res)))
        if isinstance(item, Weapon):
            # Compute reach
            reach_txt = ""
            for nb in item.reach:
                reach_txt += str(nb) + ', '
            reach_txt = reach_txt[:len(reach_txt) - 2]
            entries.append(create_item_desc_stat('TYPE OF DAMAGE', str(item.attack_kind.value)))
            entries.append(create_item_desc_stat('REACH', reach_txt))
        if isinstance(item, Shield):
            entries.append(create_item_desc_stat('PARRY RATE', str(item.parry) + '%'))
        if isinstance(item, Weapon) or isinstance(item, Shield):
            entries.append(create_item_desc_stat('DURABILITY', str(item.durability) + ' / ' + str(item.durability_max)))
        entries.append(create_item_desc_stat('WEIGHT', str(item.weight)))
    elif isinstance(item, Consumable):
        entries.append(create_item_desc_stat('EFFECT', item.effect.get_formatted_desc()))

    return InfoBox(item_title, "", "imgs/interface/PopUpMenu.png", entries,
                   ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_alteration_info_menu(alteration):
    formatted_name = alteration.get_formatted_name()

    turns_left = alteration.get_turns_left()
    entries = [[{'type': 'text', 'text': alteration.desc, 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}],
               [{'type': 'text', 'text': 'Turns left : ' + str(turns_left), 'font': fonts['ITEM_DESC_FONT'],
                 'margin': (0, 0, 10, 0), 'color': ORANGE}]]

    return InfoBox(formatted_name, "", "imgs/interface/PopUpMenu.png", entries,
                   STATUS_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_foe_menu(foe):
    formatted_name = foe.get_formatted_name()

    entries = [[{'type': 'text', 'text': 'Level :', 'margin': (10, 0, 0, 0)},
                {'type': 'text', 'text': str(foe.lvl), 'margin': (10, 0, 0, 0)}],
               [{'type': 'text', 'text': 'ATTACK', 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'margin': (10, 0, 10, 0)}],
               [{'type': 'text', 'text': 'TYPE :'},
                {'type': 'text', 'text': str(foe.attack_kind.value)}],
               [{'type': 'text', 'text': 'REACH :'},
                {'type': 'text', 'text': foe.get_formatted_reach()}],
               [{'type': 'text', 'text': 'STATS', 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'margin': (10, 0, 10, 0)}],
               [{'type': 'text', 'text': 'HP :'},
                {'type': 'text', 'text': str(foe.hp) + ' / ' + str(foe.hp_max),
                 'color': determine_hp_color(foe.hp, foe.hp_max)}],
               [{'type': 'text', 'text': 'MOVE :'},
                {'type': 'text', 'text': str(foe.max_moves)}],
               [{'type': 'text', 'text': 'ATTACK :'},
                {'type': 'text', 'text': str(foe.strength)}],
               [{'type': 'text', 'text': 'DEFENSE :'},
                {'type': 'text', 'text': str(foe.defense)}],
               [{'type': 'text', 'text': 'MAGICAL RES :'},
                {'type': 'text', 'text': str(foe.res)}],
               [{'type': 'text', 'text': 'ALTERATIONS', 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'margin': (10, 0, 10, 0)}]]

    alts = foe.alterations

    if not alts:
        entries.append([{'type': 'text', 'text': 'None'}])

    for alt in alts:
        entries.append([{'type': 'text_button', 'name': alt.get_formatted_name(), 'id': StatusMenu.INFO_ALTERATION,
                         'color_hover': TURQUOISE, 'obj': alt}])

    return InfoBox(formatted_name, "", "imgs/interface/PopUpMenu.png", entries,
                   STATUS_MENU_WIDTH, close_button=UNFINAL_ACTION)
