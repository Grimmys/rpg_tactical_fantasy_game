from src.game_entities.chest import Chest
from src.game_entities.character import Character
from src.game_entities.consumable import Consumable
from src.game_entities.door import Door
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Foe
from src.game_entities.fountain import Fountain
from src.gui.infoBox import InfoBox
from src.services.menus import *
from src.game_entities.mission import MissionType
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.shield import Shield
from src.game_entities.weapon import Weapon
from src.gui.fonts import *
from src.constants import *

MAP_WIDTH = TILE_SIZE * 20
MAP_HEIGHT = TILE_SIZE * 10


def create_shop_menu(stock, gold):
    entries = []
    row = []
    for i, it in enumerate(stock):
        entry = {'type': 'item_button', 'item': it['item'], 'price': it['item'].price, 'quantity': it['quantity'],
                 'index': i, 'id': BuyMenu.INTERAC_BUY}
        row.append(entry)
        if len(row) == 2:
            entries.append(row)
            row = []

    if row:
        entries.append(row)

    # Gold at end
    entry = [{'type': 'text', 'text': 'Your gold : ' + str(gold), 'font': fonts['ITEM_DESC_FONT']}]
    entries.append(entry)

    return InfoBox("Shop - Buying", BuyMenu, "imgs/interface/PopUpMenu.bmp", entries,
                   ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)


def create_inventory_menu(items, gold, for_sell=False):
    entries = []
    row = []
    method_id = SellMenu.INTERAC_SELL if for_sell else InventoryMenu.INTERAC_ITEM
    for i, it in enumerate(items):
        entry = {'type': 'item_button', 'item': it, 'index': i, 'id': method_id}
        # Test if price should appeared
        if for_sell and it:
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

    title = "Shop - Selling" if for_sell else "Inventory"
    menu_id = SellMenu if for_sell else InventoryMenu
    title_color = ORANGE if for_sell else WHITE
    return InfoBox(title, menu_id, "imgs/interface/PopUpMenu.bmp", entries,
                   ITEM_MENU_WIDTH, close_button=UNFINAL_ACTION, title_color=title_color)


def create_equipment_menu(equipments):
    entries = []
    body_parts = [['head'], ['body'], ['right_hand', 'left_hand'], ['feet']]
    for part in body_parts:
        row = []
        for member in part:
            equipment = None
            index = -1
            for i, eq in enumerate(equipments):
                if member == eq.body_part:
                    equipment = eq
                    index = i
                    break
            entry = {'type': 'item_button', 'item': equipment, 'index': index, 'size': ITEM_BUTTON_SIZE_EQ,
                     'id': EquipmentMenu.INTERAC_EQUIPMENT}
            row.append(entry)
        entries.append(row)
    return InfoBox("Equipment", EquipmentMenu, "imgs/interface/PopUpMenu.bmp", entries,
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

    # Buttons to trade gold
    method_id = TradeMenu.SEND_GOLD
    entry = [
        {'type': 'button', 'name': '50G ->', 'size': (90, 30), 'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 0, 50]},
        {'type': 'button', 'name': '200G ->', 'size': (90, 30), 'margin': (30, 0, 0, 0),
         'font': fonts['ITEM_DESC_FONT'], 'id': method_id, 'args': [first_player, second_player, 0, 200]},
        {'type': 'button', 'name': 'All ->', 'size': (90, 30), 'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 0, first_player.gold]},
        {'type': 'button', 'name': '<- 50G', 'size': (90, 30), 'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
         'id': method_id, 'args': [first_player, second_player, 1, 50]},
        {'type': 'button', 'name': '<- 200G', 'size': (90, 30), 'margin': (30, 0, 0, 0),
         'font': fonts['ITEM_DESC_FONT'], 'id': method_id, 'args': [first_player, second_player, 1, 200]},
        {'type': 'button', 'name': '<- All', 'size': (90, 30), 'margin': (30, 0, 0, 0), 'font': fonts['ITEM_DESC_FONT'],
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
    return InfoBox(title, menu_id, "imgs/interface/PopUpMenu.bmp", entries,
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
    entries = [[{}, {'type': 'text', 'color': GREEN, 'text': 'Name :', 'font': fonts['ITALIC_ITEM_FONT']},
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
                {'type': 'text', 'text': str(player.xp) + ' / ' + str(player.xp_next_lvl)}],
               [{'type': 'text', 'color': DARK_GREEN, 'text': 'STATS', 'font': fonts['MENU_SUB_TITLE_FONT'],
                 'margin': (10, 0, 10, 0)}],
               [{'type': 'text', 'color': WHITE, 'text': 'HP :'},
                {'type': 'text', 'text': str(player.hp) + ' / ' + str(player.hp_max),
                 'color': determine_hp_color(player.hp, player.hp_max)}],
               [{'type': 'text', 'color': WHITE, 'text': 'MOVE :'},
                {'type': 'text', 'text': str(player.max_moves) + player.get_formatted_stat_change('speed')}],
               [{'type': 'text', 'color': WHITE, 'text': 'CONSTITUTION :'},
                {'type': 'text', 'text': str(player.constitution)}],
               [{'type': 'text', 'color': WHITE, 'text': 'ATTACK :'},
                {'type': 'text', 'text': str(player.strength) + player.get_formatted_stat_change('strength')}],
               [{'type': 'text', 'color': WHITE, 'text': 'DEFENSE :'},
                {'type': 'text', 'text': str(player.defense) + player.get_formatted_stat_change('defense')}],
               [{'type': 'text', 'color': WHITE, 'text': 'MAGICAL RES :'},
                {'type': 'text', 'text': str(player.res) + player.get_formatted_stat_change('resistance')}],
               [{'type': 'text', 'color': DARK_GREEN, 'text': 'ALTERATIONS', 'font': fonts['MENU_SUB_TITLE_FONT'],
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
        skill_displayed = {'type': 'text_button', 'name': skill.formatted_name, 'id': StatusMenu.INFO_SKILL,
                           'color': WHITE, 'color_hover': TURQUOISE, 'obj': skill}
        entries[i].append(skill_displayed)
        i += 1
    for j in range(i, len(entries)):
        entries[j].append({})

    return InfoBox("Status", StatusMenu, "imgs/interface/PopUpMenu.bmp", entries,
                   STATUS_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_player_menu(player, buildings, interact_entities, missions, foes):
    entries = [[{'name': 'Inventory', 'id': CharacterMenu.INV}],
               [{'name': 'Equipment', 'id': CharacterMenu.EQUIPMENT}],
               [{'name': 'Status', 'id': CharacterMenu.STATUS}],
               [{'name': 'Wait', 'id': CharacterMenu.WAIT}]]

    # Options flags
    chest_option = False
    portal_option = False
    fountain_option = False
    talk_option = False
    trade_option = False
    pick_lock_option = False
    door_option = False

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
                    entries.insert(0, [{'name': 'Open Chest', 'id': CharacterMenu.OPEN_CHEST}])
                    chest_option = True
                if 'lock_picking' in player.skills and not pick_lock_option:
                    entries.insert(0, [{'name': 'Pick Lock', 'id': CharacterMenu.PICK_LOCK}])
                    pick_lock_option = True
            elif isinstance(ent, Door):
                if not door_option:
                    entries.insert(0, [{'name': 'Open Door', 'id': CharacterMenu.OPEN_DOOR}])
                    door_option = True
                if 'lock_picking' in player.skills and not pick_lock_option:
                    entries.insert(0, [{'name': 'Pick Lock', 'id': CharacterMenu.PICK_LOCK}])
                    pick_lock_option = True
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
        if mission.type is MissionType.POSITION or mission.type is MissionType.TOUCH_POSITION:
            if mission.pos_is_valid(player.pos):
                entries.insert(0, [{'name': 'Take', 'id': CharacterMenu.TAKE}])

    # Check if player could attack something, according to weapon range
    if player.can_attack():
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

    return InfoBox("Select an action", CharacterMenu, "imgs/interface/PopUpMenu.bmp",
                   entries, ACTION_MENU_WIDTH, el_rect_linked=player.get_rect())


def create_diary_menu(entries):
    return InfoBox("Diary", "", "imgs/interface/PopUpMenu.bmp", entries, BATTLE_SUMMARY_WIDTH,
                   close_button=UNFINAL_ACTION)


def create_main_menu(initialization_phase, pos):
    # Transform pos tuple into rect
    tile = pg.Rect(pos[0], pos[1], 1, 1)
    entries = [[{'name': 'Save', 'id': MainMenu.SAVE}],
               [{'name': 'Suspend', 'id': MainMenu.SUSPEND}]]

    if initialization_phase:
        entries.append([{'name': 'Start', 'id': MainMenu.START}])
    else:
        entries.append([{'name': 'Diary', 'id': MainMenu.DIARY}]),
        entries.append([{'name': 'End Turn', 'id': MainMenu.END_TURN}])

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("Main Menu", MainMenu, "imgs/interface/PopUpMenu.bmp", entries,
                   ACTION_MENU_WIDTH, el_rect_linked=tile)


def create_item_shop_menu(item_button_pos, item):
    entries = [
        [{'name': 'Buy', 'id': ItemMenu.BUY_ITEM, 'type': 'button'}],
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
    ]
    formatted_item_name = str(item)
    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.bmp",
                   entries, ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_item_sell_menu(item_button_pos, item):
    entries = [
        [{'name': 'Sell', 'id': ItemMenu.SELL_ITEM, 'type': 'button'}],
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM, 'type': 'button'}]
    ]
    formatted_item_name = str(item)
    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.bmp",
                   entries, ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_trade_item_menu(item_button_pos, item, players):
    entries = [
        [{'name': 'Info', 'id': ItemMenu.INFO_ITEM}],
        [{'name': 'Trade', 'id': ItemMenu.TRADE_ITEM, 'args': players}]
    ]
    formatted_item_name = str(item)

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.bmp",
                   entries,
                   ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_item_menu(item_button_pos, item, is_equipped=False):
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

    item_rect = pg.Rect(item_button_pos[0] - 20, item_button_pos[1], ITEM_BUTTON_SIZE[0],
                        ITEM_BUTTON_SIZE[1])

    return InfoBox(formatted_item_name, ItemMenu, "imgs/interface/PopUpMenu.bmp",
                   entries,
                   ACTION_MENU_WIDTH, el_rect_linked=item_rect, close_button=UNFINAL_ACTION)


def create_item_desc_stat(stat_name, stat_value):
    return [{'type': 'text', 'text': stat_name + ' : ', 'font': fonts['ITEM_DESC_FONT'], 'margin': (0, 0, 0, 100)},
            {'type': 'text', 'text': stat_value, 'font': fonts['ITEM_DESC_FONT'], 'margin': (0, 100, 0, 0)}]


def create_item_desc_menu(item):
    item_title = str(item)

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
            for possible_effect in item.effects:
                entries.append(create_item_desc_stat('EFFECT', str(possible_effect['effect']) +
                                                     ' (' + str(possible_effect['probability']) + '%)'))
            strong_against_formatted = item.get_formatted_strong_against()
            if strong_against_formatted:
                entries.append(create_item_desc_stat('STRONG AGAINST', strong_against_formatted))
        if isinstance(item, Shield):
            entries.append(create_item_desc_stat('PARRY RATE', str(item.parry) + '%'))
        if isinstance(item, Weapon) or isinstance(item, Shield):
            entries.append(create_item_desc_stat('DURABILITY', str(item.durability) + ' / ' + str(item.durability_max)))
        entries.append(create_item_desc_stat('WEIGHT', str(item.weight)))
    elif isinstance(item, Consumable):
        for eff in item.effects:
            entries.append(create_item_desc_stat('EFFECT', eff.get_formatted_desc()))

    return InfoBox(item_title, "", "imgs/interface/PopUpMenu.bmp", entries,
                   ITEM_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_alteration_info_menu(alteration):
    turns_left = alteration.get_turns_left()
    entries = [[{'type': 'text', 'text': alteration.desc, 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}],
               [{'type': 'text', 'text': 'Turns left : ' + str(turns_left), 'font': fonts['ITEM_DESC_FONT'],
                 'margin': (0, 0, 10, 0), 'color': ORANGE}]]

    return InfoBox(str(alteration), "", "imgs/interface/PopUpMenu.bmp", entries,
                   STATUS_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_skill_info_menu(skill):
    entries = [[{'type': 'text', 'text': skill.desc, 'font': fonts['ITEM_DESC_FONT'], 'margin': (20, 0, 20, 0)}],
               [{'type': 'text', 'text': '', 'margin': (0, 0, 10, 0)}]]

    return InfoBox(skill.formatted_name, "", "imgs/interface/PopUpMenu.bmp", entries,
                   STATUS_INFO_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_status_entity_menu(ent):
    keywords_display = ent.get_formatted_keywords() if isinstance(ent, Foe) else ''
    entries = [[{'type': 'text', 'text': keywords_display, 'font': fonts['ITALIC_ITEM_FONT']}],
               [{'type': 'text', 'text': 'LEVEL : ' + str(ent.lvl), 'font': fonts['ITEM_DESC_FONT']}],
               [{'type': 'text', 'text': 'ATTACK', 'font': fonts['MENU_SUB_TITLE_FONT'], 'color': DARK_GREEN,
                 'margin': (20, 0, 20, 0)}, {}, {}, {'type': 'text', 'text': 'LOOT',
                                                     'font': fonts['MENU_SUB_TITLE_FONT'],
                                                     'color': DARK_GREEN,
                                                     'margin': (20, 0, 20, 0)} if isinstance(ent, Foe) else {}, {}],
               [{'type': 'text', 'text': 'TYPE :'},
                {'type': 'text', 'text': str(ent.attack_kind.value)}, {}, {}, {}],
               [{'type': 'text', 'text': 'REACH :'},
                {'type': 'text', 'text': ent.get_formatted_reach()}, {}, {}, {}],
               [{}, {}, {}, {}, {}],
               [{}, {}, {}, {}, {}],
               [{'type': 'text', 'text': 'STATS', 'font': fonts['MENU_SUB_TITLE_FONT'], 'color': DARK_GREEN,
                 'margin': (10, 0, 10, 0)}, {}, {}, {'type': 'text', 'text': 'SKILLS',
                                                     'font': fonts['MENU_SUB_TITLE_FONT'],
                                                     'color': DARK_GREEN,
                                                     'margin': (10, 0, 10, 0)}, {}],
               [{'type': 'text', 'text': 'HP :'},
                {'type': 'text', 'text': str(ent.hp) + ' / ' + str(ent.hp_max),
                 'color': determine_hp_color(ent.hp, ent.hp_max)}, {}, {}, {}],
               [{'type': 'text', 'text': 'MOVE :'},
                {'type': 'text', 'text': str(ent.max_moves)}, {}, {}, {}],
               [{'type': 'text', 'text': 'ATTACK :'},
                {'type': 'text', 'text': str(ent.strength)}, {}, {}, {}],
               [{'type': 'text', 'text': 'DEFENSE :'},
                {'type': 'text', 'text': str(ent.defense)}, {}, {}, {}],
               [{'type': 'text', 'text': 'MAGICAL RES :'},
                {'type': 'text', 'text': str(ent.res)}, {}, {}, {}],
               [{'type': 'text', 'text': 'ALTERATIONS', 'font': fonts['MENU_SUB_TITLE_FONT'], 'color': DARK_GREEN,
                 'margin': (10, 0, 10, 0)}]]

    alts = ent.alterations
    if not alts:
        entries.append([{'type': 'text', 'text': 'None'}])
    for alt in alts:
        entries.append([{'type': 'text_button', 'name': str(alt), 'id': StatusMenu.INFO_ALTERATION,
                         'color': WHITE,
                         'color_hover': TURQUOISE, 'obj': alt}])

    if isinstance(ent, Foe):
        loot = ent.potential_loot
        i = 3
        for (item, probability) in loot:
            name = str(item)
            entries[i][3] = {'type': 'text', 'text': name}
            entries[i][4] = {'type': 'text', 'text': ' (' + str(probability * 100) + '%)'}
            i += 1

    # Display skills
    i = 7
    for skill in ent.skills:
        entries[i][3] = {'type': 'text', 'text': '> ' + skill.formatted_name}
        i += 1

    return InfoBox(str(ent), StatusMenu, "imgs/interface/PopUpMenu.bmp", entries,
                   FOE_STATUS_MENU_WIDTH, close_button=UNFINAL_ACTION)


def create_event_dialog(dialog_el):
    entries = [[{'type': 'text', 'text': s, 'font': fonts['ITEM_DESC_FONT']}]
               for s in dialog_el['talks']]
    return InfoBox(dialog_el['title'], "", "imgs/interface/PopUpMenu.bmp",
                   entries, DIALOG_WIDTH, close_button=UNFINAL_ACTION, title_color=ORANGE)


def create_reward_menu(mission):
    entries = [
        [{'type': 'text', 'text': 'Congratulations ! Objective has been completed !', 'font': fonts['ITEM_DESC_FONT']}]]
    if mission.gold:
        entries.append([{'type': 'text', 'text': 'Earned gold : ' + str(mission.gold) + ' (all characters)'}])
    for item in mission.items:
        entries.append([{'type': 'text', 'text': 'Earned item : ' + str(item)}])

    return InfoBox(mission.desc, "", "imgs/interface/PopUpMenu.bmp", entries, REWARD_MENU_WIDTH,
                   close_button=UNFINAL_ACTION)


def create_start_menu():
    entries = [[{'name': 'New game', 'id': StartMenu.NEW_GAME}], [{'name': 'Load game', 'id': StartMenu.LOAD_GAME}],
               [{'name': 'Options', 'id': StartMenu.OPTIONS}], [{'name': 'Exit game', 'id': StartMenu.EXIT}]]

    for row in entries:
        for entry in row:
            entry['type'] = 'button'

    return InfoBox("In the name of the Five Cats", StartMenu,
                   "imgs/interface/PopUpMenu.bmp", entries, START_MENU_WIDTH)


def load_parameter_entry(formatted_name, values, current_value, identifier):
    entry = {'type': 'parameter_button', 'name': formatted_name, 'values': values, 'id': identifier,
             'current_value_ind': 0}

    for i in range(len(entry['values'])):
        if entry['values'][i]['value'] == current_value:
            entry['current_value_ind'] = i

    return entry


def create_options_menu(params):
    entries = [[load_parameter_entry("Move speed : ",
                                     [{'label': 'Slow', 'value': ANIMATION_SPEED // 2},
                                      {'label': 'Normal', 'value': ANIMATION_SPEED},
                                      {'label': 'Fast', 'value': ANIMATION_SPEED * 2}],
                                     params['move_speed'],
                                     OptionsMenu.CHANGE_MOVE_SPEED)],
               [load_parameter_entry("Screen mode : ",
                                     [{'label': 'Window', 'value': SCREEN_SIZE // 2},
                                      {'label': 'Full', 'value': SCREEN_SIZE}],
                                     params['screen_size'],
                                     OptionsMenu.CHANGE_SCREEN_SIZE)], 
               [load_parameter_entry("Difficluty : ", 
                                     [{'label': '0.1', 'value': DIFFICULTY},
                                     {'label': '0.2', 'value': DIFFICULTY + 0.1},
                                     {'label': '0.3', 'value': DIFFICULTY + 0.2},
                                     {'label': '0.4', 'value': DIFFICULTY + 0.3},
                                     {'label': '0.5', 'value': DIFFICULTY + 0.4},
                                     {'label': '0.6', 'value': DIFFICULTY + 0.5},                                     
                                     {'label': '0.7', 'value': DIFFICULTY + 0.6},
                                     {'label': '0.8', 'value': DIFFICULTY + 0.7},                                     
                                     {'label': '0.9', 'value': DIFFICULTY + 0.8},
                                     {'label': '1.0', 'value': DIFFICULTY + 0.9},                                                                          
                                     ],
                                     params['difficulty'],
                                     OptionsMenu.CHANGE_DIFFICULTY)]]

    return InfoBox("Options", OptionsMenu,
                   "imgs/interface/PopUpMenu.bmp", entries, START_MENU_WIDTH, close_button=1)


def create_load_menu():
    entries = []

    for i in range(SAVE_SLOTS):
        entries.append([{'type': 'button', 'name': 'Save ' + str(i + 1), 'id': LoadMenu.LOAD, 'args': [i]}])

    return InfoBox("Load Game", LoadMenu,
                   "imgs/interface/PopUpMenu.bmp", entries, START_MENU_WIDTH, close_button=1)


def create_save_menu():
    entries = []

    for i in range(SAVE_SLOTS):
        entries.append([{'type': 'button', 'name': 'Save ' + str(i + 1), 'id': SaveMenu.SAVE, 'args': [i]}])

    return InfoBox("Save Game", SaveMenu,
                   "imgs/interface/PopUpMenu.bmp", entries, START_MENU_WIDTH, close_button=1)
