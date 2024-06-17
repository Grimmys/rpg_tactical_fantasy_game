import random

from src.constants import MAIN_WIN_HEIGHT, MAIN_WIN_WIDTH, TILE_SIZE
from src.game_entities.alteration import Alteration
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.destroyable import Destroyable
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Foe, Keyword
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.movable import Movable
from src.game_entities.objective import Objective
from src.game_entities.player import Player
from src.game_entities.shield import Shield
from src.game_entities.weapon import Weapon
from src.gui.position import Position

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
STATS = ("strength", "defense", "resistance", "speed")
EFFECTS = (
    "no_attack",
    "speed_up",
    "strength_up",
    "defense_up",
    "resistance_up",
    "hp_up",
)


def random_boolean():
    return random.choice([True, False])


def random_string(min_len=4, max_len=10):
    """

    :param min_len:
    :param max_len:
    :return:
    """
    size = random.randint(min_len, max_len)
    return "".join([random.choice(ALPHABET) for _ in range(size)])


def random_position() -> Position:
    """

    :return:
    """
    return Position(
        random.randrange(0, MAIN_WIN_WIDTH // TILE_SIZE) * TILE_SIZE,
        random.randrange(0, MAIN_WIN_HEIGHT // TILE_SIZE) * TILE_SIZE,
    )


def random_item_attributes(price):
    """

    :param price:
    :return:
    """
    return {
        "name": random_string(),
        "sample_img": "imgs/dungeon_crawl/item/potion/yellow_new.png",
        "desc": random_string(min_len=10, max_len=100),
        "cost": price if price else random.randint(0, 1000),
    }


def random_item(price=None):
    """

    :param price:
    :return:
    """
    attrs = random_item_attributes(price)
    return Item(attrs["name"], attrs["sample_img"], attrs["desc"], attrs["cost"])


def random_gold():
    """

    :return:
    """
    amount = random.randint(10, 1000)
    return Gold(amount)


def random_item_or_gold(gold_prob=0.3):
    """

    :param gold_prob:
    :return:
    """
    if random.random() <= gold_prob:
        return random_gold()
    else:
        return random_item()


def random_equipment_attributes(
    price, durability, atk=None, defense=None, res=None, restrictions=None
):
    """

    :param price:
    :param durability:
    :param atk:
    :param defense:
    :param res:
    :param restrictions:
    :return:
    """
    attrs = random_item_attributes(price)
    attrs["weight"] = random.randint(1, 10)
    attrs["durability"] = durability if durability else random.randint(10, 60)
    attrs["restrictions"] = {} if restrictions is None else restrictions
    attrs["body_part"] = random.choice(["head", "body", "feet"])
    attrs["defense"] = random.randint(1, 10) if defense is None else defense
    attrs["res"] = random.randint(1, 10) if res is None else res
    attrs["atk"] = random.randint(1, 10) if atk is None else atk
    return attrs


def random_equipment(
    price=None, durability=None, atk=None, defense=None, res=None, restrictions=None
):
    """

    :param price:
    :param durability:
    :param atk:
    :param defense:
    :param res:
    :param restrictions:
    :return:
    """
    attrs = random_equipment_attributes(
        price, durability, atk, defense, res, restrictions
    )
    return Equipment(
        attrs["name"],
        attrs["sample_img"],
        attrs["desc"],
        attrs["cost"],
        [attrs["sample_img"]],
        attrs["body_part"],
        attrs["defense"],
        attrs["res"],
        attrs["atk"],
        attrs["weight"],
        attrs["restrictions"],
    )


def random_weapon_attributes(
    price, durability, atk, strong_against, attack_kind, charge
):
    """

    :param price:
    :param durability:
    :param atk:
    :param strong_against:
    :param attack_kind:
    :param charge:
    :return:
    """
    attrs = random_equipment_attributes(price, durability, atk)
    attrs["attack_kind"] = (
        random.choice(["PHYSICAL", "SPIRITUAL"]) if attack_kind is None else attack_kind
    )
    attrs["reach"] = random.choice([[1], [1, 2], [2]])
    attrs["effects"] = []
    attrs["strong_against"] = (
        [random.choice(list(Keyword))] if strong_against is None else strong_against
    )
    attrs["charge"] = charge
    return attrs


def random_weapon(
    price=None,
    durability=None,
    atk=None,
    strong_against=None,
    attack_kind=None,
    charge=False,
):
    """

    :param price:
    :param durability:
    :param atk:
    :param strong_against:
    :param attack_kind:
    :param charge:
    :return:
    """
    attrs = random_weapon_attributes(
        price, durability, atk, strong_against, attack_kind, charge
    )
    return Weapon(
        attrs["name"],
        attrs["sample_img"],
        attrs["desc"],
        attrs["cost"],
        [attrs["sample_img"]],
        attrs["atk"],
        attrs["attack_kind"],
        attrs["weight"],
        attrs["durability"],
        attrs["reach"],
        attrs["restrictions"],
        attrs["effects"],
        attrs["strong_against"],
        attrs["charge"],
    )


def random_shield_attributes(price, durability, parry_rate):
    """

    :param price:
    :param durability:
    :param parry_rate:
    :return:
    """
    attrs = random_equipment_attributes(price, durability)
    attrs["parry"] = random.randint(1, 100) if parry_rate is None else parry_rate
    return attrs


def random_shield(price=None, durability=None, parry_rate=None):
    """

    :param price:
    :param durability:
    :param parry_rate:
    :return:
    """
    attrs = random_shield_attributes(price, durability, parry_rate)
    return Shield(
        attrs["name"],
        attrs["sample_img"],
        attrs["desc"],
        attrs["cost"],
        [attrs["sample_img"]],
        attrs["defense"],
        attrs["weight"],
        attrs["parry"],
        attrs["durability"],
        attrs["restrictions"],
    )


def random_chest(item_set=None, nb_items=None, equal_probs=False, gold_proportion=0.3):
    """

    :param item_set:
    :param nb_items:
    :param equal_probs:
    :param gold_proportion:
    :return:
    """
    position = random_position()
    sprite_close = "imgs/dungeon_crawl/dungeon/chest_2_closed.png"
    sprite_open = "imgs/dungeon_crawl/dungeon/chest_2_open.png"
    if item_set:
        potential_items = item_set
    else:
        potential_items = []
        if not nb_items:
            nb_items = random.randint(1, 10)
        for i in range(nb_items):
            item = random_item_or_gold(gold_proportion)
            if not equal_probs:
                probability = random.randint(1, 100) / 100
            else:
                probability = 1 / nb_items
            potential_items.append((item, probability))
    return Chest(position, sprite_close, sprite_open, potential_items)


def random_destroyable_attributes(min_hp, max_hp, max_defense, max_res, name):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :return:
    """
    return {
        "name": name if name else random_string(),
        "pos": random_position(),
        "sprite": "imgs/dungeon_crawl/monster/angel.png",
        "hp": random.randint(min_hp, max_hp),
        "defense": random.randint(0, max_defense),
        "res": random.randint(0, max_res),
    }


def random_destroyable_entity(
    min_hp=10, max_hp=30, max_defense=10, max_res=10, name=None
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :return:
    """
    attributes = random_destroyable_attributes(
        min_hp, max_hp, max_defense, max_res, name
    )
    return Destroyable(
        attributes["name"],
        attributes["pos"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["res"],
    )


def random_movable_attributes(min_hp, max_hp, max_defense, max_res, name):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :return:
    """
    attributes = random_destroyable_attributes(
        min_hp, max_hp, max_defense, max_res, name
    )
    attributes["max_moves"] = random.randint(0, 12)
    attributes["strength"] = random.randint(0, 20)
    attributes["attack_kind"] = random.choice(["PHYSICAL", "SPIRITUAL"])
    attributes["strategy"] = random.choice(
        ["STATIC", "PASSIVE", "SEMI_ACTIVE", "ACTIVE", "MANUAL"]
    )
    return attributes


def random_movable_entity(min_hp=10, max_hp=30, max_defense=10, max_res=10, name=None):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :return:
    """
    attributes = random_movable_attributes(min_hp, max_hp, max_defense, max_res, name)
    return Movable(
        attributes["name"],
        attributes["pos"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["res"],
        attributes["max_moves"],
        attributes["strength"],
        attributes["attack_kind"],
        attributes["strategy"],
    )


def random_character_attributes(
    min_hp,
    max_hp,
    max_defense,
    max_res,
    name,
    lvl,
    equipments,
    classes,
    race,
    interaction,
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :param lvl:
    :param equipments:
    :param classes:
    :param race:
    :param interaction:
    :return:
    """
    attributes = random_movable_attributes(min_hp, max_hp, max_defense, max_res, name)
    attributes["classes"] = (
        classes if classes else [random.choice(list(Character.classes_data.keys()))]
    )
    attributes["race"] = (
        race if race else random.choice(list(Character.races_data.keys()))
    )
    attributes["equipments"] = equipments if equipments else []
    attributes["lvl"] = lvl if lvl else random.randint(1, 10)
    attributes["skills"] = []
    attributes["gold"] = random.randint(10, 1000)
    attributes["interaction"] = interaction
    return attributes


def random_character_entity(
    min_hp=10,
    max_hp=30,
    max_defense=10,
    max_res=10,
    name=None,
    lvl=None,
    equipments=None,
    classes=None,
    race=None,
    interaction=None,
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :param lvl:
    :param equipments:
    :param classes:
    :param race:
    :param interaction:
    :return:
    """
    attributes = random_character_attributes(
        min_hp,
        max_hp,
        max_defense,
        max_res,
        name,
        lvl,
        equipments,
        classes,
        race,
        interaction,
    )
    return Character(
        attributes["name"],
        attributes["pos"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["res"],
        attributes["strength"],
        attributes["classes"],
        attributes["equipments"],
        attributes["strategy"],
        attributes["lvl"],
        attributes["skills"],
        [],
        attributes["race"],
        attributes["gold"],
        attributes["interaction"],
    )


def random_foe_attributes(
    min_hp, max_hp, max_defense, max_res, name, reach, keywords, loot
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :param reach:
    :param keywords:
    :param loot:
    :return:
    """
    attributes = random_movable_attributes(min_hp, max_hp, max_defense, max_res, name)
    attributes["reach"] = (
        reach if reach else random.choice([[1], [2], [1, 2], [3], [1, 2, 3]])
    )
    attributes["xp_gain"] = random.randint(10, 300)
    attributes["lvl"] = random.randint(1, 10)
    attributes["loot"] = (
        loot
        if loot
        else [
            (random_item_or_gold(), random.random())
            for _ in range(random.randint(1, 5))
        ]
    )
    attributes["keywords"] = (
        [random.choice(list(Keyword))] if keywords is None else keywords
    )
    attributes["alterations"] = []
    return attributes


def random_foe_entity(
    min_hp=10,
    max_hp=30,
    max_defense=10,
    max_res=10,
    name=None,
    reach=None,
    keywords=None,
    loot=None,
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :param reach:
    :param keywords:
    :param loot:
    :return:
    """
    attributes = random_foe_attributes(
        min_hp, max_hp, max_defense, max_res, name, reach, keywords, loot
    )
    return Foe(
        attributes["name"],
        attributes["pos"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["res"],
        attributes["max_moves"],
        attributes["strength"],
        attributes["attack_kind"],
        attributes["strategy"],
        attributes["reach"],
        attributes["xp_gain"],
        attributes["loot"],
        attributes["keywords"],
        attributes["lvl"],
        attributes["alterations"],
    )


def random_player_attributes(
    min_hp, max_hp, max_defense, max_res, name, lvl, equipments, classes, race
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :param lvl:
    :param equipments:
    :param classes:
    :param race:
    :return:
    """
    attrs = random_character_attributes(
        min_hp, max_hp, max_defense, max_res, name, lvl, equipments, classes, race, None
    )
    return attrs


def random_player_entity(
    min_hp=10,
    max_hp=30,
    max_defense=10,
    max_res=10,
    name=None,
    lvl=None,
    equipments=None,
    classes=None,
    race=None,
    items=None,
):
    """

    :param min_hp:
    :param max_hp:
    :param max_defense:
    :param max_res:
    :param name:
    :param lvl:
    :param equipments:
    :param classes:
    :param race:
    :param items:
    :return:
    """
    if items is None:
        items = []
    attributes = random_player_attributes(
        min_hp, max_hp, max_defense, max_res, name, lvl, equipments, classes, race
    )
    player = Player(
        attributes["name"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["res"],
        attributes["strength"],
        attributes["classes"],
        attributes["equipments"],
        attributes["race"],
        attributes["gold"],
        attributes["lvl"],
        attributes["skills"],
        [],
    )
    player.set_initial_pos(attributes["pos"])
    for item in items:
        player.set_item(item)
    return player


def random_entities(entity_kind, min_number=1, max_number=10):
    """

    :param entity_kind:
    :param min_number:
    :param max_number:
    :return:
    """
    if entity_kind is Foe:
        random_entity_callback = random_foe_entity
    else:
        random_entity_callback = random_player_entity
    return [
        random_entity_callback() for _ in range(random.randint(min_number, max_number))
    ]


def random_building(
    is_interactive=True,
    min_talks=1,
    max_talks=10,
    min_gold=0,
    gold=True,
    item=True,
):
    """

    :param is_interactive:
    :param min_talks:
    :param max_talks:
    :param min_gold:
    :param gold:
    :param item:
    :return:
    """
    name = random_string()
    position = random_position()
    sprite = "imgs/houses/blue_house.png"
    interaction = None
    if is_interactive:
        talks_el = [
            random_string(min_len=10, max_len=100)
            for _ in range(random.randint(min_talks, max_talks))
        ]
        interaction = {
            "talks": talks_el,
            "gold": random.randint(min_gold, 1000) if gold else 0,
            "item": random_item() if item else None,
        }
    return Building(name, position, sprite, interaction)


def random_stock():
    """

    :return:
    """
    stock = []
    nb_items = random.randint(1, 10)
    for _ in range(nb_items):
        stock.append({"item": random_item(), "quantity": random.randint(1, 10)})
    return stock


def random_shop():
    """ """
    pass


def random_effect():
    """

    :return:
    """
    return random.choice(EFFECTS)


def random_alteration(name=None, effects=None, min_duration=1, max_duration=5):
    """

    :param name:
    :param effects:
    :param min_duration:
    :param max_duration:
    :return:
    """
    name = name if name else random_string()
    abbr = random_string(2, 4)
    power = random.randint(1, 5)
    duration = random.randint(min_duration, max_duration)
    desc = random_string(10, 30)
    effects = (
        effects
        if effects
        else list(set([random_effect() for _ in range(random.randint(1, 5))]))
    )

    return Alteration(name, abbr, power, duration, desc, effects)


def random_objective(name=None, position=None):
    name = name if name else random_string()
    position = position if position else random_position()
    sprite = "imgs/dungeon_crawl/dungeon/gateways/abyssal_stair.png"

    return Objective(name, position, sprite, random_boolean())
