import random as rd

from src.game_entities.alteration import Alteration
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.destroyable import Destroyable
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.movable import Movable
from src.game_entities.weapon import Weapon
from src.constants import TILE_SIZE, MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
STATS = ('strength', 'defense', 'resistance', 'speed')
EFFECTS = ('no_attack', 'speed_up', 'strength_up', 'defense_up', 'resistance_up', 'hp_up')


def random_string(min_len=4, max_len=10):
    size = rd.randint(min_len, max_len)
    return ''.join([rd.choice(ALPHABET) for _ in range(size)])


def random_pos():
    return rd.randrange(0, MAIN_WIN_WIDTH // TILE_SIZE) * TILE_SIZE, \
           rd.randrange(0, MAIN_WIN_HEIGHT // TILE_SIZE) * TILE_SIZE


def random_item_or_gold(gold_prob=0.3):
    if rd.random() <= gold_prob:
        amount = rd.randint(10, 1000)
        return Gold(amount)
    else:
        return random_item()


def random_item_attributes(price):
    return {'name': random_string(),
            'sample_img': 'imgs/dungeon_crawl/item/potion/yellow_new.png',
            'desc': random_string(min_len=10, max_len=100),
            'cost': rd.randint(0, 1000) if price is None else price}


def random_item(price=None):
    attrs = random_item_attributes(price)
    return Item(attrs['name'], attrs['sample_img'], attrs['desc'], attrs['cost'])


def random_weapon_attributes(price, durability):
    attrs = random_item_attributes(price)
    attrs['power'] = rd.randint(1, 10)
    attrs['attack_kind'] = rd.choice(['PHYSICAL', 'SPIRITUAL'])
    attrs['weight'] = rd.randint(1, 10)
    attrs['durability'] = rd.randint(10, 60) if durability is None else durability
    attrs['reach'] = rd.choice([[1], [1, 2], [2]])
    attrs['restrictions'] = []
    attrs['effects'] = []
    return attrs


def random_weapon(price=None, durability=None):
    attrs = random_weapon_attributes(price, durability)
    return Weapon(attrs['name'], attrs['sample_img'], attrs['desc'], attrs['cost'], [attrs['sample_img']],
                  attrs['power'], attrs['attack_kind'], attrs['weight'], attrs['durability'], attrs['reach'],
                  attrs['restrictions'], attrs['effects'])


def random_chest(item_set=None, nb_items=None, equal_probs=False, gold_proportion=0.3):
    pos = random_pos()
    sprite_close = 'imgs/dungeon_crawl/dungeon/chest_2_closed.png'
    sprite_open = 'imgs/dungeon_crawl/dungeon/chest_2_open.png'
    if item_set:
        potential_items = item_set
    else:
        potential_items = []
        if not nb_items:
            nb_items = rd.randint(1, 10)
        for i in range(nb_items):
            item = random_item_or_gold(gold_proportion)
            if not equal_probs:
                prob = rd.random()
            else:
                prob = 1 / nb_items
            potential_items.append((item, prob))
    return Chest(pos, sprite_close, sprite_open, potential_items)


def random_destroyable_attributes(min_hp, max_defense, max_res, name):
    return {'name': name if name else random_string(), 'pos': random_pos(),
            'sprite': 'imgs/dungeon_crawl/monster/angel.png',
            'hp': rd.randint(min_hp, 30), 'defense': rd.randint(0, max_defense), 'res': rd.randint(0, max_res)}


def random_destroyable_entity(min_hp=10, max_defense=10, max_res=10, name=None):
    attrs = random_destroyable_attributes(min_hp, max_defense, max_res, name)
    return Destroyable(attrs['name'], attrs['pos'], attrs['sprite'], attrs['hp'], attrs['defense'], attrs['res'])


def random_movable_attributes(min_hp, max_defense, max_res, name):
    attrs = random_destroyable_attributes(min_hp, max_defense, max_res, name)
    attrs['max_moves'] = rd.randint(0, 12)
    attrs['strength'] = rd.randint(0, 20)
    attrs['attack_kind'] = rd.choice(['PHYSICAL', 'SPIRITUAL'])
    attrs['strategy'] = rd.choice(['STATIC', 'PASSIVE', 'SEMI_ACTIVE', 'ACTIVE', 'MANUAL'])
    return attrs


def random_movable_entity(min_hp=10, max_defense=10, max_res=10, name=None):
    attrs = random_movable_attributes(min_hp, max_defense, max_res, name)
    return Movable(attrs['name'], attrs['pos'], attrs['sprite'], attrs['hp'], attrs['defense'], attrs['res'],
                   attrs['max_moves'], attrs['strength'], attrs['attack_kind'], attrs['strategy'])


def random_character_attributes(min_hp, max_defense, max_res, name, classes, race, interaction):
    attrs = random_movable_attributes(min_hp, max_defense, max_res, name)
    attrs['classes'] = classes if classes else [rd.choice(list(Character.classes_data.keys()))]
    attrs['race'] = race if race else rd.choice(list(Character.races_data.keys()))
    attrs['equipments'] = []
    attrs['lvl'] = rd.randint(1, 10)
    attrs['skills'] = []
    attrs['gold'] = rd.randint(10, 1000)
    attrs['interaction'] = interaction
    return attrs


def random_character_entity(min_hp=10, max_defense=10, max_res=10, name=None, classes=None, race=None,
                            interaction=None):
    attrs = random_character_attributes(min_hp, max_defense, max_res, name, classes, race, interaction)
    return Character(attrs['name'], attrs['pos'], attrs['sprite'], attrs['hp'], attrs['defense'], attrs['res'],
                     attrs['strength'], attrs['classes'], attrs['equipments'], attrs['strategy'],
                     attrs['lvl'], attrs['skills'], [], attrs['race'], attrs['gold'], attrs['interaction'])


def random_building(is_interactive=True, min_talks=0, max_talks=10, talks=True, min_gold=0, gold=True, item=True):
    name = random_string()
    pos = random_pos()
    sprite = 'imgs/houses/blue_house.png'
    interaction = {}
    if is_interactive:
        talks_el = [random_string(min_len=10, max_len=100) for _ in range(rd.randint(min_talks, max_talks))]
        interaction = {
            'talks': talks_el if talks else [],
            'gold': rd.randint(min_gold, 1000) if gold else 0,
            'item': random_item() if item else None
        }
    return Building(name, pos, sprite, interaction)


def random_stock():
    stock = []
    nb_items = rd.randint(1, 10)
    for _ in range(nb_items):
        stock.append({'item': random_item(), 'quantity': rd.randint(1, 10)})
    return stock


def random_shop():
    pass


def random_effect():
    return rd.choice(EFFECTS)


def random_alteration(name=None, effects=None, min_duration=1, max_duration=5):
    name = name if name else random_string()
    abbr = random_string(2, 4)
    power = rd.randint(1, 5)
    duration = rd.randint(min_duration, max_duration)
    desc = random_string(10, 30)
    effects = effects if effects else list(set([random_effect() for _ in range(rd.randint(1, 5))]))

    return Alteration(name, abbr, power, duration, desc, effects)
