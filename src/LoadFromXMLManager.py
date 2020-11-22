from lxml import etree

from src.Breakable import Breakable
from src.Character import Character
from src.Door import Door
from src.Gold import Gold
from src.Item import Item
from src.Player import Player
from src.Building import Building
from src.Chest import Chest
from src.Effect import Effect
from src.Equipment import Equipment
from src.Foe import Foe
from src.Fountain import Fountain
from src.Key import Key
from src.Mission import Mission, MissionType
from src.Portal import Portal
from src.Consumable import Consumable
from src.Potion import Potion
from src.Shield import Shield
from src.Shop import Shop
from src.Skill import Skill
from src.Spellbook import Spellbook
from src.Weapon import Weapon
from src.constants import TILE_SIZE

foes_infos = {}
fountains_infos = {}
skills_infos = {}

RACES_PATH = 'data/races.xml'
CLASSES_PATH = 'data/classes.xml'


def load_races():
    races = {}
    races_file = etree.parse(RACES_PATH).getroot()
    for race_el in races_file.findall('*'):
        race = {}
        cons = race_el.find('constitution')
        race['constitution'] = int(cons.text.strip()) if cons is not None else 0
        race['move'] = int(race_el.find('move').text.strip())
        race['skills'] = [(load_skill(skill.text.strip()) if not skill in skills_infos else skills_infos[skill])
                          for skill in race_el.findall('skills/skill/name')]
        races[race_el.tag] = race
    return races


def load_classes():
    classes = {}
    classes_file = etree.parse(CLASSES_PATH).getroot()
    for cl_el in classes_file.findall('*'):
        cl = {}
        cons = cl_el.find('constitution')
        cl['constitution'] = int(cons.text.strip()) if cons is not None else 0
        move = cl_el.find('move')
        cl['move'] = int(move.text.strip()) if move is not None else 0
        cl['stats_up'] = load_stats_up(cl_el)
        cl['skills'] = [(load_skill(skill.text.strip()) if not skill in skills_infos else skills_infos[skill])
                        for skill in cl_el.findall('skills/skill/name')]
        classes[cl_el.tag] = cl
    return classes


def load_stat_up(el, stat_name):
    return [int(val) for val in el.find('stats_up/' + stat_name).text.strip().split(',')]


def load_stats_up(el):
    return {
        'hp': load_stat_up(el, 'hp'),
        'def': load_stat_up(el, 'defense'),
        'res': load_stat_up(el, 'resistance'),
        'str': load_stat_up(el, 'strength')
    }


def load_skill(name):
    if name not in skills_infos:
        # Required dat
        skill_el = etree.parse('data/skills.xml').find(name)
        formatted_name = skill_el.find('name').text.strip()
        nature = skill_el.find('type').text.strip()
        desc = skill_el.find('info').text.strip()

        # Not required elements
        power = 0
        power_el = skill_el.find('power')
        if power_el is not None:
            power = int(power_el.text.strip())
        stats = []
        stats_el = skill_el.find('stats')
        if stats_el is not None:
            stats = [stat for stat in stats_el.text.replace(' ', '').split(',')]
        alterations = []
        alterations_el = skill_el.find('alteration')
        if alterations_el is not None:
            alterations = [alt for alt in alterations_el.text.replace(' ', '').split(',')]

        skills_infos[name] = Skill(name, formatted_name, nature, desc, power, stats, alterations)
    return skills_infos[name]


def load_placements(positions, gap_x, gap_y):
    placements = []
    for coords in positions:
        x = int(coords.find('x').text) * TILE_SIZE + gap_x
        y = int(coords.find('y').text) * TILE_SIZE + gap_y
        pos = (x, y)
        placements.append(pos)
    return placements


def load_all_entities(data, from_save, gap_x, gap_y):
    return {
        'allies': load_entities('character', data.findall('allies/ally'), from_save, gap_x, gap_y),
        'foes': load_entities('foe', data.findall('foes/foe'), from_save, gap_x, gap_y),
        'breakables': load_entities('breakable', data.findall('breakables/breakable'), from_save, gap_x, gap_y),
        'chests': load_entities('chest', data.findall('chests/chest'), from_save, gap_x, gap_y),
        'doors': load_entities('door', data.findall('doors/door'), from_save, gap_x, gap_y),
        'buildings': load_entities('building', data.findall('buildings/building'), from_save, gap_x, gap_y),
        'fountains': load_entities('fountain', data.findall('fountains/fountain'), from_save, gap_x, gap_y),
        'portals': load_entities('portal', data.findall('portals/couple'), from_save, gap_x, gap_y)
    }


def load_entities(ent_nature, data, from_save, gap_x, gap_y):
    collection = []

    for el in data:
        if ent_nature == 'character':
            ent = load_ally(el, from_save, gap_x, gap_y)
        elif ent_nature == 'foe':
            ent = load_foe(el, from_save, gap_x, gap_y)
        elif ent_nature == 'chest':
            ent = load_chest(el, from_save, gap_x, gap_y)
        elif ent_nature == 'door':
            ent = load_door(el, from_save, gap_x, gap_y)
        elif ent_nature == 'building':
            ent = load_building(el, from_save, gap_x, gap_y)
        elif ent_nature == 'portal':
            ent, ent2 = load_portal(el, gap_x, gap_y)
            collection.append(ent2)
        elif ent_nature == 'fountain':
            ent = load_fountain(el, from_save, gap_x, gap_y)
        elif ent_nature == 'breakable':
            ent = load_breakable(el, gap_x, gap_y)
        else:
            print("Unrecognized nature : " + str(ent_nature))
            ent = None
        collection.append(ent)
    return collection


def load_ally(ally, from_save, gap_x, gap_y):
    name = ally.find('name').text.strip()
    x = int(ally.find('position/x').text) * TILE_SIZE + gap_x
    y = int(ally.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)

    infos = etree.parse('data/characters.xml').find(name)

    # Static data
    sprite = 'imgs/' + infos.find('sprite').text.strip()
    race = infos.find('race').text.strip()
    classes = [infos.find('class').text.strip()]
    formatted_name = infos.find('name').text.strip()
    lvl = int(infos.find('level').text.strip())

    interaction_el = infos.find('interaction')
    dialog = []
    for talk in interaction_el.findall('talk'):
        dialog.append(talk.text.strip())
    interaction = {
        'dialog': dialog,
        'join_team': interaction_el.find('join_team') is not None
    }

    strategy = infos.find('strategy').text.strip()
    attack_kind = infos.find('attack_kind').text.strip()

    dynamic_data = infos
    if from_save:
        dynamic_data = ally
    hp = int(dynamic_data.find('hp').text.strip())
    strength = int(dynamic_data.find('strength').text.strip())
    defense = int(dynamic_data.find('defense').text.strip())
    res = int(dynamic_data.find('resistance').text.strip())
    gold = int(dynamic_data.find('gold').text.strip())

    equipments = []
    for eq in dynamic_data.findall('equipment/*'):
        equipments.append(parse_item_file(eq.text.strip()))

    if from_save:
        skills = [(load_skill(skill.text.strip())
                   if not skill.text.strip() in skills_infos else skills_infos[skill.text.strip()])
                  for skill in dynamic_data.findall('skills/skill/name')]
    else:
        skills = Character.classes_data[classes[0]]['skills'] + Character.races_data[race]['skills']

    loaded_ally = Character(formatted_name, pos, sprite, hp, defense, res, strength, attack_kind,
                            classes, equipments, strategy, lvl, skills, race, gold, interaction)

    inventory = infos.find('inventory')
    if inventory is not None:
        for it in inventory.findall('item'):
            item = parse_item_file(it.text.strip())
            loaded_ally.set_item(item)

    if from_save:
        current_hp = int(ally.find('current_hp').text.strip())
        loaded_ally.hp = current_hp

        xp = int(ally.find('exp').text.strip())
        loaded_ally.earn_xp(xp)
    else:
        # Up stats according to current lvl
        loaded_ally.stats_up(lvl - 1)
        # Restore hp due to lvl up
        loaded_ally.healed()

    return loaded_ally


def load_foe(foe, from_save, gap_x, gap_y):
    name = foe.find('name').text.strip()
    if name not in foes_infos:
        foes_infos[name] = etree.parse('data/foes.xml').find(name)

    # Load grow rates of this kind of foe - if not already loaded - in the class
    if name not in Foe.grow_rates:
        Foe.grow_rates[name] = load_stats_up(foes_infos[name])

    # Static data
    sprite = 'imgs/dungeon_crawl/monster/' + foes_infos[name].find('sprite').text.strip()
    xp_gain = int(foes_infos[name].find('xp_gain').text.strip())
    strategy = foes_infos[name].find('strategy').text.strip()
    foe_range = foes_infos[name].find('reach')
    reach = [int(reach) for reach in foe_range.text.strip().split(',')] if foe_range is not None else [1]
    attack_kind = foes_infos[name].find('attack_kind').text.strip()
    loot = [(parse_item_file(it.find('name').text.strip()), float(it.find('probability').text))
            for it in foes_infos[name].findall('loot/item')]
    gold_looted = foes_infos[name].find('loot/gold')
    if gold_looted is not None:
        loot.append((Gold(int(gold_looted.find('amount').text)), float(gold_looted.find('probability').text)))

    # Dynamic data
    x = int(foe.find('position/x').text) * TILE_SIZE + gap_x
    y = int(foe.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    lvl = int(foe.find('level').text.strip())
    if from_save:
        # Overwrite static loaded loot
        loot = [(parse_item_file(it.find('name').text.strip()), float(it.find('probability').text))
                for it in foe.findall('loot/item')]
        gold_looted = foe.find('loot/gold')
        if gold_looted is not None:
            loot.append((Gold(int(gold_looted.find('amount').text)), float(gold_looted.find('probability').text)))
    else:
        dynamic_loot = [(parse_item_file(it.find('name').text.strip()), 1.0) for it in foe.findall('loot/item')]
        loot.extend(dynamic_loot)
        gold_looted = foe.find('loot/gold')
        if gold_looted is not None:
            loot.extend([(Gold(int(gold_looted.find('amount').text)), 1.0)])
    specific_strategy = foe.find('strategy')
    if specific_strategy is not None:
        strategy = specific_strategy.text.strip()

    stats_tree = foes_infos[name]
    if from_save:
        stats_tree = foe
    hp = int(stats_tree.find('hp').text.strip())
    move = int(stats_tree.find('move').text.strip())
    strength = int(stats_tree.find('strength').text.strip())
    defense = int(stats_tree.find('defense').text.strip())
    res = int(stats_tree.find('resistance').text.strip())

    loaded_foe = Foe(name, pos, sprite, hp, defense, res, move, strength, attack_kind, strategy, reach, xp_gain, loot,
                     lvl)

    if from_save:
        current_hp = int(foe.find('current_hp').text.strip())
        loaded_foe.hp = current_hp

        xp = int(foe.find('exp').text.strip())
        loaded_foe.earn_xp(xp)
    else:
        # Up stats according to current lvl
        loaded_foe.stats_up(lvl - 1)
        # Restore hp due to lvl up
        loaded_foe.healed()
    return loaded_foe


def load_chest(chest, from_save, gap_x, gap_y):
    # Static data
    x = int(chest.find('position/x').text) * TILE_SIZE + gap_x
    y = int(chest.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    sprite_closed = chest.find('closed/sprite').text.strip()
    sprite_opened = chest.find('opened/sprite').text.strip()

    # Dynamic data
    potential_items = []
    if from_save:
        opened = chest.find('state').text.strip() == "True"
        it_name = chest.find('contains/item').text.strip()
        it = parse_item_file(it_name)

        potential_items.append((it, 1.0))
    else:
        for item in chest.xpath("contains/item"):
            it_name = item.find('name').text.strip()
            it = parse_item_file(it_name)
            probability = float(item.find('probability').text)

            potential_items.append((it, probability))
        for gold in chest.xpath("contains/gold"):
            amount = int(gold.find('amount').text)
            probability = float(gold.find('probability').text)
            it = Gold(amount)
            potential_items.append((it, probability))
        opened = False

    loaded_chest = Chest(pos, sprite_closed, sprite_opened, potential_items)

    if opened:
        loaded_chest.open()

    return loaded_chest


def load_door(door, from_save, gap_x, gap_y):
    # Static data
    x = int(door.find('position/x').text) * TILE_SIZE + gap_x
    y = int(door.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    sprite = door.find('sprite').text.strip()

    # Dynamic data
    pick_lock_initiated = False
    if from_save:
        pick_lock_initiated = door.find('pick_lock_initiated') is not None

    loaded_door = Door(pos, sprite, pick_lock_initiated)
    return loaded_door


def load_building(building, from_save, gap_x, gap_y):
    # Static data
    name = building.find('name').text.strip()
    x = int(building.find('position/x').text) * TILE_SIZE + gap_x
    y = int(building.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    sprite = building.find('sprite').text.strip()
    interaction = building.find('interaction')
    interaction_el = {}
    if interaction is not None:
        talks = interaction.find('talks')
        if talks is not None:
            interaction_el['talks'] = []
            for talk in talks.findall('talk'):
                interaction_el['talks'].append(talk.text.strip())
        else:
            interaction_el['talks'] = []
        interaction_el['gold'] = \
            int(interaction.find('gold').text.strip()) if interaction.find('gold') is not None else 0
        interaction_el['item'] = parse_item_file(interaction.find('item').text.strip()) \
            if interaction.find('item') is not None else None

    nature = building.find('type')
    if nature is not None:
        nature = nature.text.strip()
        if nature == "shop":
            stock = []
            for it in building.findall('items/item'):
                entry = {'item': parse_item_file(it.find('name').text.strip()),
                         'quantity': int(it.find('quantity').text.strip())
                         }
                stock.append(entry)
            loaded_building = Shop(name, pos, sprite, None, stock)
        else:
            print("Error : building type isn't recognized : ", type)
            raise SystemError
    else:
        loaded_building = Building(name, pos, sprite, interaction_el)

    # Dynamic data
    if from_save:
        locked = building.find('state').text.strip()
        if locked == "True":
            loaded_building.remove_interaction()

    return loaded_building


def load_obstacles(tree, gap_x, gap_y):
    loaded_obstacles = []
    for positions in tree.findall('positions'):
        fixed_y = positions.find('y')
        if fixed_y is not None:
            fixed_y = int(fixed_y.text) * TILE_SIZE + gap_y
            from_x = int(positions.find('from_x').text) * TILE_SIZE + gap_x
            to_x = int(positions.find('to_x').text) * TILE_SIZE + gap_x
            for i in range(from_x, to_x + TILE_SIZE, TILE_SIZE):
                pos = (i, fixed_y)
                loaded_obstacles.append(pos)
        else:
            fixed_x = int(positions.find('x').text) * TILE_SIZE + gap_x
            from_y = int(positions.find('from_y').text) * TILE_SIZE + gap_y
            to_y = int(positions.find('to_y').text) * TILE_SIZE + gap_y
            for i in range(from_y, to_y + TILE_SIZE, TILE_SIZE):
                pos = (fixed_x, i)
                loaded_obstacles.append(pos)

    for obstacle in tree.findall('position'):
        x = int(obstacle.find('x').text) * TILE_SIZE + gap_x
        y = int(obstacle.find('y').text) * TILE_SIZE + gap_y
        pos = (x, y)
        loaded_obstacles.append(pos)
    return loaded_obstacles


def load_mission(mission_xml, is_main, nb_players, gap_x, gap_y):
    nature = MissionType[mission_xml.find('type').text]
    desc = mission_xml.find('description').text.strip()
    positions = []
    if nature is MissionType.POSITION or nature is MissionType.TOUCH_POSITION:
        for coords in mission_xml.findall('position'):
            x = int(coords.find('x').text) * TILE_SIZE + gap_x
            y = int(coords.find('y').text) * TILE_SIZE + gap_y
            positions.append((x, y))
    min_players = mission_xml.find('nb_players')
    if min_players is not None:
        min_players = int(min_players.text.strip())
    else:
        min_players = nb_players
    if is_main:
        gold_reward = 0
        items_reward = []
    else:
        # If mission is not main, a reward is associated
        gold_reward = mission_xml.find('reward/gold')
        if gold_reward is not None:
            gold_reward = int(gold_reward.text.strip())
        items_reward = mission_xml.findall('reward/item')
        if items_reward is not None:
            items_reward = [parse_item_file(item) for item in items_reward]
    turn_limit = mission_xml.find('turns')
    if turn_limit is not None:
        turn_limit = int(turn_limit.text.strip())
    return Mission(is_main, nature, positions, desc, min_players, turn_limit, gold_reward, items_reward)


def load_missions(tree, players, gap_x, gap_y):
    loaded_missions = []
    #  > Load main mission
    main_mission = tree.find('missions/main')
    mission = load_mission(main_mission, True, len(players), gap_x, gap_y)
    loaded_missions.append(mission)
    main_mission = mission
    #   > Load secondary missions
    for mission_xml in tree.findall('missions/mission'):
        loaded_missions.append(load_mission(mission_xml, False, len(players), gap_x, gap_y))
    return loaded_missions, main_mission


def load_portal(portal_couple, gap_x, gap_y):
    first_x = int(portal_couple.find('first/position/x').text) * TILE_SIZE + gap_x
    first_y = int(portal_couple.find('first/position/y').text) * TILE_SIZE + gap_y
    first_pos = (first_x, first_y)
    second_x = int(portal_couple.find('second/position/x').text) * TILE_SIZE + gap_x
    second_y = int(portal_couple.find('second/position/y').text) * TILE_SIZE + gap_y
    second_pos = (second_x, second_y)
    sprite = 'imgs/dungeon_crawl/' + portal_couple.find('sprite').text.strip()
    first_portal = Portal(first_pos, sprite)
    second_portal = Portal(second_pos, sprite)
    Portal.link_portals(first_portal, second_portal)
    return first_portal, second_portal


def load_fountain(fountain, from_save, gap_x, gap_y):
    name = fountain.find('type').text.strip()
    x = int(fountain.find('position/x').text) * TILE_SIZE + gap_x
    y = int(fountain.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    if name not in fountains_infos:
        fountains_infos[name] = etree.parse('data/fountains/' + name + '.xml').getroot()
    sprite = 'imgs/dungeon_crawl/' + fountains_infos[name].find('sprite').text.strip()
    sprite_empty = 'imgs/dungeon_crawl/' + fountains_infos[name].find('sprite_empty').text.strip()
    effect_name = fountains_infos[name].find('effect').text.strip()
    power = int(fountains_infos[name].find('power').text.strip())
    duration = int(fountains_infos[name].find('duration').text.strip())
    effect = Effect(effect_name, power, duration)
    times = int(fountains_infos[name].find('times').text.strip())

    loaded_fountain = Fountain(name, pos, sprite, sprite_empty, effect, times)

    if from_save:
        # Load remaining uses from saved data
        times = int(fountain.find('times').text.strip())
        loaded_fountain.set_times(times)

    return loaded_fountain


def load_breakable(breakable, gap_x, gap_y):
    # Static data
    x = int(breakable.find('position/x').text) * TILE_SIZE + gap_x
    y = int(breakable.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    sprite = 'imgs/dungeon_crawl/dungeon/' + breakable.find('sprite').text.strip()
    hp = int(breakable.find('current_hp').text.strip())

    return Breakable(pos, sprite, hp, 0, 0)


def load_restrictions(restrictions_el):
    restrictions = {}
    if restrictions_el is None:
        return restrictions

    classes = restrictions_el.find('classes')
    if classes is not None:
        restrictions['classes'] = classes.text.strip().split(',')
    races = restrictions_el.find('races')
    if races is not None:
        restrictions['races'] = races.text.strip().split(',')

    return restrictions


def load_events(events_el, gap_x, gap_y):
    events = {}

    for event in events_el:
        events[event.tag] = {}
        dialog_els = event.findall('dialog')
        if dialog_els:
            events[event.tag]['dialogs'] = []
            for dialog_el in dialog_els:
                title_el = dialog_el.find('title')
                events[event.tag]['dialogs'].append({
                    'title': title_el.text.strip() if title_el is not None else '',
                    'talks': [talk.text.strip() for talk in dialog_el.find('talks').findall('talk')]
                })
        new_players_els = event.findall('new_player')
        if new_players_els:
            events[event.tag]['new_players'] = [{
                'name': player_el.find('name').text.strip(),
                'position': (int(player_el.find('position/x').text.strip()) * TILE_SIZE + gap_x,
                             int(player_el.find('position/y').text.strip()) * TILE_SIZE + gap_y)
            } for player_el in new_players_els]

    return events


def load_player(el, from_save):
    name = el.find("name").text.strip()
    level = el.find('level')
    if level is None:
        # If level is not specified, default value is 1
        level = 1
    else:
        level = int(level.text.strip())
    p_class = el.find("class").text.strip()
    race = el.find("race").text.strip()
    gold = int(el.find("gold").text.strip())
    exp = int(el.find("exp").text.strip()) if from_save else 0
    hp = int(el.find("hp").text.strip())
    strength = int(el.find("strength").text.strip())
    defense = int(el.find("defense").text.strip())
    res = int(el.find("resistance").text.strip())
    current_hp = int(el.find("current_hp").text.strip()) if from_save else hp
    inv = []
    for it in el.findall("inventory/item"):
        it_name = it.text.strip()
        item = parse_item_file(it_name)
        inv.append(item)

    equipments = []
    for eq in el.findall("equipment/*"):
        eq_name = eq.text.strip()
        eq = parse_item_file(eq_name)
        equipments.append(eq)

    if from_save:
        skills = [(load_skill(skill.text.strip())
                   if skill.text.strip() not in skills_infos
                   else skills_infos[skill.text.strip()])
                  for skill in el.findall('skills/skill/name')]
        tree = etree.parse("data/characters.xml").getroot()
        player_t = tree.xpath(name)[0]
    else:
        skills = Character.classes_data[p_class]['skills'] + Character.races_data[race]['skills']
        player_t = el

    # -- Reading of the XML file for default character's values (i.e. sprites)
    sprite = 'imgs/' + player_t.find('sprite').text.strip()
    compl_sprite = player_t.find('complement_sprite')
    if compl_sprite is not None:
        compl_sprite = 'imgs/' + compl_sprite.text.strip()

    p = Player(name, sprite, hp, defense, res, strength, [p_class], equipments, race, gold, level,
               skills, compl_sprite=compl_sprite)
    p.earn_xp(exp)
    p.items = inv
    p.hp = current_hp
    if from_save:
        pos = (int(el.find("position/x").text.strip()) * TILE_SIZE,
               int(el.find("position/y").text.strip()) * TILE_SIZE)
        p.pos = pos
        state = el.find("turnFinished").text.strip()
        if state == "True":
            p.end_turn()
    else:
        # Up stats according to current lvl
        p.stats_up(level - 1)
        # Restore hp due to lvl up
        p.healed()

    return p


def load_players(data):
    players = []
    for player_el in data.findall('players/player'):
        players.append(load_player(player_el, True))
    return players


def load_escaped_players(data):
    players = []
    for player_el in data.findall('escaped_players/player'):
        players.append(load_player(player_el, True))
    return players


def init_player(name):
    # -- Reading of the XML file
    tree = etree.parse("data/characters.xml").getroot()
    player_t = tree.xpath(name)[0]
    return load_player(player_t, False)


def load_weapon_effect(eff):
    loaded_eff = {}

    # Load effect
    name = eff.find('name').text.strip()
    power_el = eff.find('power')
    power = int(power_el.text.strip()) if power_el is not None else 0
    duration_el = eff.find('duration')
    duration = int(duration_el.text.strip()) if duration_el is not None else 0
    loaded_eff['effect'] = Effect(name, power, duration)

    # Load probability
    loaded_eff['probability'] = int(float(eff.find('probability').text.strip()) * 100)

    return loaded_eff


def parse_item_file(name):
    # Retrieve data root for item
    it_tree_root = etree.parse('data/items.xml').getroot().find('.//' + name)

    sprite = 'imgs/dungeon_crawl/item/' + it_tree_root.find('sprite').text.strip()
    info = it_tree_root.find('info').text.strip()
    price = it_tree_root.find('price')
    if price is not None:
        price = int(price.text.strip())
    else:
        price = 0
    category = it_tree_root.find('category').text.strip()

    if category == 'potion' or category == 'consumable':
        effects = []
        for eff in it_tree_root.findall('.//effect'):
            effect_name = eff.find('type').text.strip()
            pow_el = eff.find('power')
            power = int(pow_el.text.strip()) if pow_el is not None else 0
            duration_el = eff.find('duration')
            duration = int(duration_el.text.strip()) if duration_el is not None else 0
            effects.append(Effect(effect_name, power, duration))
        item = Potion(name, sprite, info, price, effects) if category == 'potion' else \
            Consumable(name, sprite, info, price, effects)
    elif category == 'armor':
        body_part = it_tree_root.find('bodypart').text.strip()
        defense_el = it_tree_root.find('def')
        defense = int(defense_el.text.strip()) if defense_el is not None else 0
        weight = int(it_tree_root.find('weight').text.strip())
        eq_sprites = it_tree_root.find('equipped_sprites')
        if eq_sprites is not None:
            equipped_sprites = []
            for eq_sprite in eq_sprites.findall('sprite'):
                equipped_sprites.append('imgs/dungeon_crawl/player/' + eq_sprite.text.strip())
        else:
            equipped_sprites = ['imgs/dungeon_crawl/player/' + it_tree_root.find(
                'equipped_sprite').text.strip()]
        restrictions = load_restrictions(it_tree_root.find('restrictions'))
        item = Equipment(name, sprite, info, price, equipped_sprites, body_part, defense, 0, 0,
                         weight, restrictions)
    elif category == 'shield':
        parry = int(float(it_tree_root.find('parry_rate').text.strip()) * 100)
        defense_el = it_tree_root.find('def')
        defense = int(defense_el.text.strip()) if defense_el is not None else 0
        fragility = int(it_tree_root.find('fragility').text.strip())
        weight = int(it_tree_root.find('weight').text.strip())
        equipped_sprite = ['imgs/dungeon_crawl/player/hand_left/' + it_tree_root.find(
            'equipped_sprite').text.strip()]
        restrictions = load_restrictions(it_tree_root.find('restrictions'))
        item = Shield(name, sprite, info, price, equipped_sprite, defense, weight, parry, fragility, restrictions)
    elif category == 'weapon':
        power = int(it_tree_root.find('power').text.strip())
        attack_kind = it_tree_root.find('kind').text.strip()
        weight = int(it_tree_root.find('weight').text.strip())
        fragility = int(it_tree_root.find('fragility').text.strip())
        w_range = [int(reach) for reach in it_tree_root.find('range').text.strip().split(',')]
        equipped_sprite = ['imgs/dungeon_crawl/player/hand_right/' + it_tree_root.find(
            'equipped_sprite').text.strip()]
        restrictions = load_restrictions(it_tree_root.find('restrictions'))
        effects = it_tree_root.find('effects')
        possible_effects = []
        if effects is not None:
            possible_effects = [load_weapon_effect(eff) for eff in effects.findall('effect')]
        item = Weapon(name, sprite, info, price, equipped_sprite, power, attack_kind, weight, fragility,
                      w_range, restrictions, possible_effects)
    elif category == 'key':
        for_chest = it_tree_root.find('open_chest') is not None
        for_door = it_tree_root.find('open_door') is not None
        item = Key(name, sprite, info, price, for_chest, for_door)
    elif category == 'spellbook':
        spell = it_tree_root.find('effect').text.strip()
        item = Spellbook(name, sprite, info, price, spell)
    else:
        # No special category
        item = Item(name, sprite, info, price)

    return item
