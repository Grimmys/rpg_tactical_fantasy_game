from lxml import etree

from src.Breakable import Breakable
from src.Building import Building
from src.Character import Character
from src.Chest import Chest
from src.Effect import Effect
from src.Equipment import Equipment
from src.Foe import Foe
from src.Fountain import Fountain
from src.Key import Key
from src.Mission import Mission, MissionType
from src.Player import Player
from src.Portal import Portal
from src.Potion import Potion
from src.Shield import Shield
from src.Shop import Shop
from src.Spellbook import Spellbook
from src.Weapon import Weapon
from src.constants import TILE_SIZE

foes_infos = {}
fountains_infos = {}


def load_placements(positions, gap_x, gap_y):
    placements = []
    for coords in positions:
        x = int(coords.find('x').text) * TILE_SIZE + gap_x
        y = int(coords.find('y').text) * TILE_SIZE + gap_y
        pos = (x, y)
        placements.append(pos)
    return placements


def load_all_entities(data, from_save, gap_x, gap_y):
    return {'allies': load_entities(Character, data.findall('allies/ally'), from_save, gap_x, gap_y),
            'foes': load_entities(Foe, data.findall('foes/foe'), from_save, gap_x, gap_y),
            'breakables': load_entities(Breakable, data.findall('breakables/breakable'), from_save, gap_x, gap_y),
            'chests': load_entities(Chest, data.findall('chests/chest'), from_save, gap_x, gap_y),
            'buildings': load_entities(Building, data.findall('buildings/building'), from_save, gap_x, gap_y),
            'fountains': load_entities(Fountain, data.findall('fountains/fountain'), from_save, gap_x, gap_y),
            'portals': load_entities(Portal, data.findall('portals/couple'), from_save, gap_x, gap_y)
            }


def load_entities(ent_nature, data, from_save, gap_x, gap_y):
    collection = []

    for el in data:
        if ent_nature is Character:
            ent = load_ally(el, from_save, gap_x, gap_y)
        elif ent_nature is Foe:
            ent = load_foe(el, from_save, gap_x, gap_y)
        elif ent_nature is Chest:
            ent = load_chest(el, from_save, gap_x, gap_y)
        elif ent_nature is Building:
            ent = load_building(el, from_save, gap_x, gap_y)
        elif ent_nature is Portal:
            ent, ent2 = load_portal(el, gap_x, gap_y)
            collection.append(ent2)
        elif ent_nature is Fountain:
            ent = load_fountain(el, from_save, gap_x, gap_y)
        elif ent_nature is Breakable:
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
    lvl = int(ally.find('level').text.strip())

    infos = etree.parse('data/characters.xml').find(name)

    # Static data
    sprite = 'imgs/characs/' + infos.find('sprite').text.strip()
    race = infos.find('race').text.strip()
    formatted_name = infos.find('name').text.strip()

    talks = infos.find('talks')
    dialog = []
    for talk in talks.findall('talk'):
        dialog.append(talk.text.strip())

    strategy = infos.find('strategy').text.strip()
    attack_kind = infos.find('attack_kind').text.strip()

    stats_tree = infos
    if from_save:
        stats_tree = ally
    hp = int(stats_tree.find('hp').text.strip())
    move = int(stats_tree.find('move').text.strip())
    strength = int(stats_tree.find('strength').text.strip())
    defense = int(stats_tree.find('def').text.strip())
    res = int(stats_tree.find('res').text.strip())
    gold = int(stats_tree.find('gold').text.strip())

    loaded_ally = Character(formatted_name, pos, sprite, hp, defense, res, move, strength, attack_kind,
                            [], [], strategy, lvl, race, gold, dialog)

    if from_save:
        current_hp = int(ally.find('currentHp').text.strip())
        loaded_ally.set_current_hp(current_hp)

        xp = int(ally.find('exp').text.strip())
        loaded_ally.earn_xp(xp)
    return loaded_ally


def load_foe(foe, from_save, gap_x, gap_y):
    name = foe.find('name').text.strip()
    x = int(foe.find('position/x').text) * TILE_SIZE + gap_x
    y = int(foe.find('position/y').text) * TILE_SIZE + gap_y
    pos = (x, y)
    lvl = int(foe.find('level').text.strip())

    if name not in foes_infos:
        foes_infos[name] = etree.parse('data/foes/' + name + '.xml').getroot()

    # Static data
    sprite = 'imgs/dungeon_crawl/monster/' + foes_infos[name].find('sprite').text.strip()
    xp_gain = int(foes_infos[name].find('xp_gain').text.strip())
    strategy = foes_infos[name].find('strategy').text.strip()
    foe_range = foes_infos[name].find('reach')
    reach = [int(reach) for reach in foe_range.text.strip().split(',')] if foe_range is not None else [1]

    attack_kind = foes_infos[name].find('attack_kind').text.strip()

    stats_tree = foes_infos[name]
    if from_save:
        stats_tree = foe

    hp = int(stats_tree.find('hp').text.strip())
    move = int(stats_tree.find('move').text.strip())
    strength = int(stats_tree.find('strength').text.strip())
    defense = int(stats_tree.find('def').text.strip())
    res = int(stats_tree.find('res').text.strip())

    loaded_foe = Foe(name, pos, sprite, hp, defense, res, move, strength, attack_kind, strategy, reach, xp_gain, lvl)

    if from_save:
        current_hp = int(foe.find('currentHp').text.strip())
        loaded_foe.set_current_hp(current_hp)

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

        potential_items.append((1.0, it))
    else:
        for item in chest.xpath("contains/item"):
            it_name = item.find('name').text.strip()
            it = parse_item_file(it_name)
            proba = float(item.find('probability').text)

            potential_items.append((proba, it))
        opened = False

    loaded_chest = Chest(pos, sprite_closed, sprite_opened, potential_items)

    if opened:
        loaded_chest.open()

    return loaded_chest


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
            items = []
            for it in building.findall('items/item/name'):
                items.append(parse_item_file(it.text.strip()))
            loaded_building = Shop(name, pos, sprite, None, items)
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


def load_missions(tree, players, gap_x, gap_y):
    loaded_missions = []
    #  > Load main mission
    main_mission = tree.find('missions/main')
    nature = MissionType[main_mission.find('type').text]
    main = True
    positions = []
    desc = main_mission.find('description').text.strip()
    nb_players = len(players)
    if nature is MissionType.POSITION:
        for coords in main_mission.findall('position'):
            x = int(coords.find('x').text) * TILE_SIZE + gap_x
            y = int(coords.find('y').text) * TILE_SIZE + gap_y
            pos = (x, y)
            positions.append(pos)
    mission = Mission(main, nature, positions, desc, nb_players)
    loaded_missions.append(mission)
    main_mission = mission
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
    hp = int(breakable.find('currentHp').text.strip())

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
        dialog_el = event.find('dialog')
        if dialog_el is not None:
            events[event.tag]['dialog'] = {
                'title': dialog_el.find('title').text.strip(),
                'talks': [talk.text.strip() for talk in dialog_el.find('talks').findall('talk')]
            }
        new_player_el = event.find('new_player')
        if new_player_el is not None:
            events[event.tag]['new_player'] = {
                'name': new_player_el.find('name').text.strip(),
                'position': (int(new_player_el.find('position/x').text.strip()) * TILE_SIZE + gap_x,
                             int(new_player_el.find('position/y').text.strip()) * TILE_SIZE + gap_y)
            }

    return events


def load_player(name):
    # -- Reading of the XML file
    tree = etree.parse("data/characters.xml").getroot()
    player_t = tree.xpath(name)[0]
    player_class = player_t.find('class').text.strip()
    race = player_t.find('race').text.strip()
    lvl = player_t.find('level')
    if lvl is None:
        # If lvl is not informed, default value is assumes to be 1
        lvl = 1
    else:
        lvl = int(lvl.text.strip())
    defense = int(player_t.find('initDef').text.strip())
    res = int(player_t.find('initRes').text.strip())
    hp = int(player_t.find('initHP').text.strip())
    strength = int(player_t.find('initStrength').text.strip())
    move = int(player_t.find('move').text.strip())
    sprite = 'imgs/dungeon_crawl/player/' + player_t.find('sprite').text.strip()
    compl_sprite = player_t.find('complementSprite')
    if compl_sprite is not None:
        compl_sprite = 'imgs/dungeon_crawl/player/' + compl_sprite.text.strip()

    equipment = player_t.find('equipment')
    equipments = []
    for eq in equipment.findall('*'):
        equipments.append(parse_item_file(eq.text.strip()))
    gold = int(player_t.find('gold').text.strip())

    # Creating player instance
    player = Player(name, sprite, hp, defense, res, move, strength, [player_class], equipments, race, gold, lvl,
                    compl_sprite=compl_sprite)

    # Up stats according to current lvl
    player.stats_up(lvl - 1)
    # Restore hp due to lvl up
    player.healed()

    inventory = player_t.find('inventory')
    for it in inventory.findall('item'):
        item = parse_item_file(it.text.strip())
        player.set_item(item)

    return player


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

    item = None
    if category == 'potion':
        effect_name = it_tree_root.find('effect').text.strip()
        power = int(it_tree_root.find('power').text.strip())
        duration = int(it_tree_root.find('duration').text.strip())
        effect = Effect(effect_name, power, duration)
        item = Potion(name, sprite, info, price, effect)
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
        item = Weapon(name, sprite, info, price, equipped_sprite, power, attack_kind, weight, fragility,
                      w_range, restrictions)
    elif category == 'key':
        item = Key(name, sprite, info, price)
    elif category == 'spellbook':
        spell = it_tree_root.find('effect').text.strip()
        item = Spellbook(name, sprite, info, price, spell)

    return item
