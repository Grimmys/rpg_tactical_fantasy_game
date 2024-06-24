from __future__ import annotations

from collections.abc import Sequence
from typing import Optional

from src.constants import TILE_SIZE
from src.game_entities.alteration import Alteration
from src.game_entities.breakable import Breakable
from src.game_entities.building import Building
from src.game_entities.character import Character
from src.game_entities.chest import Chest
from src.game_entities.consumable import Consumable
from src.game_entities.door import Door
from src.game_entities.effect import Effect
from src.game_entities.entity import Entity
from src.game_entities.equipment import Equipment
from src.game_entities.foe import Foe, Keyword
from src.game_entities.fountain import Fountain
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.game_entities.key import Key
from src.game_entities.player import Player
from src.game_entities.portal import Portal
from src.game_entities.potion import Potion
from src.game_entities.shield import Shield
from src.game_entities.shop import Shop
from src.game_entities.skill import Skill
from src.game_entities.spellbook import Spellbook
from src.game_entities.weapon import Weapon
from src.gui.position import Position
from src.services.language import *
from src.services.global_foes import link_foe_to_mission

foes_data = {}
fountains_data = {}
skills_data = {}

RACES_DATA_PATH = "data/races.xml"
CLASSES_DATA_PATH = "data/classes.xml"


def load_races() -> dict[str, dict[str, any]]:
    """

    :return:
    """
    races = {}
    races_file = etree.parse(RACES_DATA_PATH).getroot()
    for race_element in races_file.findall("*"):
        race = {}
        constitution = race_element.find("constitution")
        race["constitution"] = (
            int(constitution.text.strip()) if constitution is not None else 0
        )
        move = race_element.find("move")
        race["move"] = (
            int(race_element.find("move").text.strip()) if move is not None else 0
        )
        race["skills"] = [
            get_skill_data(skill.text.strip())
            for skill in race_element.findall("skills/skill/name")
        ]
        races[race_element.tag] = race
    return races


def load_classes() -> dict[str, dict[str, any]]:
    """

    :return:
    """
    classes = {}
    classes_file = etree.parse(CLASSES_DATA_PATH).getroot()
    for class_element in classes_file.findall("*"):
        class_data = {}
        constitution = class_element.find("constitution")
        class_data["constitution"] = (
            int(constitution.text.strip()) if constitution is not None else 0
        )
        move = class_element.find("move")
        class_data["move"] = int(move.text.strip()) if move is not None else 0
        class_data["stats_up"] = load_stats_up(class_element)
        class_data["skills"] = [
            get_skill_data(skill.text.strip())
            for skill in class_element.findall("skills/skill/name")
        ]
        classes[class_element.tag] = class_data
    return classes


def load_stat_up(element, stat_name) -> Sequence[int]:
    """

    :param element:
    :param stat_name:
    :return:
    """
    return [
        int(value)
        for value in element.find("stats_up/" + stat_name).text.strip().split(",")
    ]


def load_stats_up(element) -> dict[str, Sequence[int]]:
    """

    :param element:
    :return:
    """
    return {
        "hp": load_stat_up(element, "hp"),
        "def": load_stat_up(element, "defense"),
        "res": load_stat_up(element, "resistance"),
        "str": load_stat_up(element, "strength"),
    }


def get_skill_data(name) -> Skill:
    """

    :param name:
    :return:
    """
    if name not in skills_data:
        # Required data
        skill_element = etree.parse("data/skills.xml").find(name)
        formatted_name = skill_element.find("name/" + language)
        if formatted_name is not None:
            formatted_name = formatted_name.text.strip()
        else:
            formatted_name = skill_element.find("name/en").text.strip()
        nature = skill_element.find("type").text.strip()
        description = get_localized_string(skill_element.find("info")).strip()

        # Not required elements
        power = 0
        power_element = skill_element.find("power")
        if power_element is not None:
            power = int(power_element.text.strip())
        stats = []
        stats_element = skill_element.find("stats")
        if stats_element is not None:
            stats = list(stats_element.text.replace(" ", "").split(","))
        alterations = []
        alterations_element = skill_element.find("alteration")
        if alterations_element is not None:
            alterations = list(alterations_element.text.replace(" ", "").split(","))

        skills_data[name] = Skill(
            name, formatted_name, nature, description, power, stats, alterations
        )
    return skills_data[name]


def load_alteration(alteration_element) -> Alteration:
    """

    :param alteration_element:
    :return:
    """
    name = alteration_element.find("name").text.strip()
    abbreviation = alteration_element.find("abbr").text.strip()
    power = int(alteration_element.find("power").text.strip())
    duration = int(alteration_element.find("duration").text.strip())
    description = alteration_element.find("desc").text.strip()
    specificities = [
        spec.text.strip() for spec in alteration_element.findall("specs/spec")
    ]
    return Alteration(name, abbreviation, power, duration, description, specificities)


def load_placements(positions, gap_x, gap_y) -> Sequence[Position]:
    """

    :param positions:
    :param gap_x:
    :param gap_y:
    :return:
    """
    placements = []
    for coordinates in positions:
        x_coordinate = int(coordinates.find("x").text) * TILE_SIZE + gap_x
        y_coordinate = int(coordinates.find("y").text) * TILE_SIZE + gap_y
        placements.append(Position(x_coordinate, y_coordinate))
    return placements


def load_all_entities_from_save(data, gap_x, gap_y) -> dict[str, list[Entity]]:
    """

    :param data:
    :param gap_x:
    :param gap_y:
    :return:
    """
    return {
        "allies": load_entities_from_save(
            "character", data.findall("allies/ally"), gap_x, gap_y
        ),
        "foes": load_entities_from_save("foe", data.findall("foes/foe"), gap_x, gap_y),
        "breakables": load_entities_from_save(
            "breakable", data.findall("breakables/breakable"), gap_x, gap_y
        ),
        "chests": load_entities_from_save(
            "chest", data.findall("chests/chest"), gap_x, gap_y
        ),
        "doors": load_entities_from_save(
            "door", data.findall("doors/door"), gap_x, gap_y
        ),
        "buildings": load_entities_from_save(
            "building", data.findall("buildings/building"), gap_x, gap_y
        ),
        "fountains": load_entities_from_save(
            "fountain", data.findall("fountains/fountain"), gap_x, gap_y
        ),
        "portals": load_entities_from_save(
            "portal", data.findall("portals/couple"), gap_x, gap_y
        ),
    }


def load_entities_from_save(entity_nature, data, gap_x, gap_y) -> list[Entity]:
    """

    :param entity_nature:
    :param data:
    :param gap_x:
    :param gap_y:
    :return:
    """
    collection = []

    for element in data:
        # TODO: Too many branches for a similar behaviour, need refactoring (mapping?)
        if entity_nature == "character":
            entity = load_ally_from_save(element, gap_x, gap_y)
        elif entity_nature == "foe":
            entity = load_foe_from_save(element, gap_x, gap_y)
        elif entity_nature == "chest":
            entity = load_chest_from_save(element, gap_x, gap_y)
        elif entity_nature == "door":
            entity = load_door_from_save(element, gap_x, gap_y)
        elif entity_nature == "building":
            entity = load_building_from_save(element, gap_x, gap_y)
        elif entity_nature == "portal":
            entity, other_entity = load_portal_from_save(element, gap_x, gap_y)
            collection.append(other_entity)
        elif entity_nature == "fountain":
            entity = load_fountain_from_save(element, gap_x, gap_y)
        elif entity_nature == "breakable":
            entity = load_breakable_from_save(element, gap_x, gap_y)
        else:
            print(f"Unrecognized nature : {entity_nature}")
            entity = None
        collection.append(entity)
    return collection


def load_artificial_entity_from_save(entity, data, gap_x, gap_y, extension_path=""):
    """

    :param entity:
    :param data:
    :param gap_x:
    :param gap_y:
    :param extension_path:
    :return:
    """
    name = entity.find("name").text.strip()

    # Static data
    sprite = "imgs/" + extension_path + data.find("sprite").text.strip()
    strategy = data.find("strategy").text.strip()

    # Dynamic data
    x_coordinate = int(entity.find("position/x").text) * TILE_SIZE + gap_x
    y_coordinate = int(entity.find("position/y").text) * TILE_SIZE + gap_y
    position = Position(x_coordinate, y_coordinate)

    level_element = (
        entity.find("level") if entity.find("level") is not None else data.find("level")
    )
    lvl = int(level_element.text.strip())
    specific_strategy = entity.find("strategy")
    if specific_strategy is not None:
        strategy = specific_strategy.text.strip()

    dynamic_data = entity
    hit_points = int(dynamic_data.find("hp").text.strip())
    strength = int(dynamic_data.find("strength").text.strip())
    defense = int(dynamic_data.find("defense").text.strip())
    resistance = int(dynamic_data.find("resistance").text.strip())
    alterations = []
    for alteration in dynamic_data.findall("alterations/alteration"):
        alterations.append(load_alteration(alteration))

    return {
        "name": name,
        "sprite": sprite,
        "strategy": strategy,
        "position": position,
        "level": lvl,
        "hp": hit_points,
        "strength": strength,
        "defense": defense,
        "resistance": resistance,
        "alterations": alterations,
    }


def load_artificial_entity(
        name: str,
        data: etree.Element,
        position: Position,
        level: Optional[int] = None,
        strategy: Optional[str] = None,
        extension_path: str = "",
):
    # Static data
    sprite = "imgs/" + extension_path + data.find("sprite").text.strip()
    if strategy is None:
        strategy = data.find("strategy").text.strip()

    # Dynamic data
    if level is None:
        level = int(data.find("level").text.strip())
    hit_points = int(data.find("hp").text.strip())
    strength = int(data.find("strength").text.strip())
    defense = int(data.find("defense").text.strip())
    resistance = int(data.find("resistance").text.strip())
    alterations = []
    for alteration in data.findall("alterations/alteration"):
        alterations.append(load_alteration(alteration))

    return {
        "name": name,
        "sprite": sprite,
        "strategy": strategy,
        "position": position,
        "level": level,
        "hp": hit_points,
        "strength": strength,
        "defense": defense,
        "resistance": resistance,
        "alterations": alterations,
    }


def load_ally_from_save(ally_element, gap_x, gap_y):
    """

    :param ally_element:
    :param gap_x:
    :param gap_y:
    :return:
    """
    name = ally_element.find("name").text.strip()
    generic_data = etree.parse("data/characters.xml").find(name)

    attributes = load_artificial_entity_from_save(
        ally_element, generic_data, gap_x, gap_y
    )

    # Static data character
    race = generic_data.find("race").text.strip()
    classes = [generic_data.find("class").text.strip()]
    interaction_element = generic_data.find("interaction")
    dialog = []
    for talk in interaction_element.findall("talk"):
        dialog.append(get_localized_string(talk).strip())
    interaction = {
        "dialog": dialog,
        "join_team": interaction_element.find("join_team") is not None,
    }

    # Dynamic data character
    dynamic_data = ally_element
    gold = int(dynamic_data.find("gold").text.strip())

    equipments = []
    for equipment in dynamic_data.findall("equipment/*"):
        equipments.append(load_item(equipment))

    skills = [
        (
            get_skill_data(skill.text.strip())
            if not skill.text.strip() in skills_data
            else skills_data[skill.text.strip()]
        )
        for skill in dynamic_data.findall("skills/skill/name")
    ]

    loaded_ally = Character(
        attributes["name"],
        attributes["position"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["resistance"],
        attributes["strength"],
        classes,
        equipments,
        attributes["strategy"],
        attributes["level"],
        skills,
        attributes["alterations"],
        race,
        gold,
        interaction,
    )

    for item in dynamic_data.findall("inventory/item"):
        item_loaded = load_item(item)
        loaded_ally.set_item(item_loaded)

    current_hit_points = int(ally_element.find("current_hp").text.strip())
    loaded_ally.hit_points = current_hit_points

    experience = int(ally_element.find("exp").text.strip())
    loaded_ally.earn_xp(experience)

    return loaded_ally


def load_ally(name: str, position: Position) -> Character:
    generic_data = etree.parse("data/characters.xml").find(name)

    attributes = load_artificial_entity(name, generic_data, position)

    # Static data character
    race = generic_data.find("race").text.strip()
    classes = [generic_data.find("class").text.strip()]
    interaction_element = generic_data.find("interaction")
    dialog = []
    for talk in interaction_element.findall("talk"):
        dialog.append(get_localized_string(talk).strip())
    interaction = {
        "dialog": dialog,
        "join_team": interaction_element.find("join_team") is not None,
    }

    # Dynamic data character
    gold = int(generic_data.find("gold").text.strip())

    equipments = []
    for equipment in generic_data.findall("equipment/*"):
        equipment_loaded = parse_item_file(equipment.text.strip())
        equipments.append(equipment_loaded)

    skills = (
            Character.classes_data[classes[0]]["skills"]
            + Character.races_data[race]["skills"]
    )

    loaded_ally = Character(
        attributes["name"],
        attributes["position"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["resistance"],
        attributes["strength"],
        classes,
        equipments,
        attributes["strategy"],
        attributes["level"],
        skills,
        attributes["alterations"],
        race,
        gold,
        interaction,
    )

    for item in generic_data.findall("inventory/item"):
        item_loaded = parse_item_file(item.text.strip())

        loaded_ally.set_item(item_loaded)

    # Up stats according to current lvl
    loaded_ally.stats_up(attributes["level"] - 1)
    # Restore hp due to lvl up
    loaded_ally.healed()

    return loaded_ally


def load_foe_from_save(foe_element, gap_x, gap_y):
    """

    :param foe_element:
    :param gap_x:
    :param gap_y:
    :return:
    """
    name = foe_element.find("name").text.strip()
    if name not in foes_data:
        foes_data[name] = etree.parse("data/foes.xml").find(name)
        # Load grow rates of this kind of foe in the class
        Foe.grow_rates[name] = load_stats_up(foes_data[name])

    attributes = load_artificial_entity_from_save(
        foe_element, foes_data[name], gap_x, gap_y, "dungeon_crawl/monster/"
    )

    # Static data foe
    xp_gain = int(foes_data[name].find("xp_gain").text.strip())
    foe_range = foes_data[name].find("reach")
    reach = (
        [int(reach) for reach in foe_range.text.strip().split(",")]
        if foe_range is not None
        else [1]
    )
    attack_kind = foes_data[name].find("attack_kind").text.strip()
    loot = [
        (
            parse_item_file(item.find("name").text.strip()),
            float(item.find("probability").text),
        )
        for item in foes_data[name].findall("loot/item")
    ]
    gold_looted = foes_data[name].find("loot/gold")
    if gold_looted is not None:
        loot.append(
            (
                Gold(int(gold_looted.find("amount").text)),
                float(gold_looted.find("probability").text),
            )
        )
    keywords_element = foes_data[name].find("keywords")
    keywords = (
        [
            Keyword[keyword.upper()]
            for keyword in keywords_element.text.strip().split(",")
        ]
        if keywords_element is not None
        else []
    )
    move = int(foes_data[name].find("move").text.strip())

    # Dynamic data foe
    # Overwrite static loaded loot
    loot = [
        (
            parse_item_file(item.find("name").text.strip()),
            float(item.find("probability").text),
        )
        for item in foe_element.findall("loot/item")
    ]
    gold_looted = foe_element.find("loot/gold")
    if gold_looted is not None:
        loot.append(
            (
                Gold(int(gold_looted.find("amount").text)),
                float(gold_looted.find("probability").text),
            )
        )

    mission_target_element = foe_element.find("mission_target")
    mission_target = (
        mission_target_element.text.strip()
        if mission_target_element is not None
        else None
    )

    loaded_foe = Foe(
        attributes["name"],
        attributes["position"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["resistance"],
        move,
        attributes["strength"],
        attack_kind,
        attributes["strategy"],
        reach,
        xp_gain,
        loot,
        keywords,
        attributes["level"],
        attributes["alterations"],
        mission_target,
    )

    current_hp = int(foe_element.find("current_hp").text.strip())
    loaded_foe.hit_points = current_hp

    experience = int(foe_element.find("exp").text.strip())
    loaded_foe.earn_xp(experience)

    if mission_target is not None:
        link_foe_to_mission(loaded_foe, mission_target)

    return loaded_foe


def load_foe(
        name: str,
        position: Position,
        level: int,
        strategy: Optional[str],
        specific_loot: Sequence[Item],
        mission_target: str,
) -> Foe:
    if name not in foes_data:
        foes_data[name] = etree.parse("data/foes.xml").find(name)
        # Load grow rates of this kind of foe in the class
        Foe.grow_rates[name] = load_stats_up(foes_data[name])

    attributes = load_artificial_entity(
        name, foes_data[name], position, level, strategy, "dungeon_crawl/monster/"
    )

    # Static data foe
    xp_gain = int(foes_data[name].find("xp_gain").text.strip())
    foe_range = foes_data[name].find("reach")
    reach = (
        [int(reach) for reach in foe_range.text.strip().split(",")]
        if foe_range is not None
        else [1]
    )
    attack_kind = foes_data[name].find("attack_kind").text.strip()
    loot = [
               (
                   parse_item_file(item.find("name").text.strip()),
                   float(item.find("probability").text),
               )
               for item in foes_data[name].findall("loot/item")
           ] + [(item, 1.0) for item in specific_loot]
    gold_looted = foes_data[name].find("loot/gold")
    if gold_looted is not None:
        loot.append(
            (
                Gold(int(gold_looted.find("amount").text)),
                float(gold_looted.find("probability").text),
            )
        )
    keywords_element = foes_data[name].find("keywords")
    keywords = (
        [
            Keyword[keyword.upper()]
            for keyword in keywords_element.text.strip().split(",")
        ]
        if keywords_element is not None
        else []
    )
    move = int(foes_data[name].find("move").text.strip())

    loaded_foe = Foe(
        attributes["name"],
        attributes["position"],
        attributes["sprite"],
        attributes["hp"],
        attributes["defense"],
        attributes["resistance"],
        move,
        attributes["strength"],
        attack_kind,
        attributes["strategy"],
        reach,
        xp_gain,
        loot,
        keywords,
        attributes["level"],
        attributes["alterations"],
        mission_target,
    )

    # Up stats according to current lvl
    loaded_foe.stats_up(attributes["level"] - 1)
    # Restore hp due to lvl up
    loaded_foe.healed()

    return loaded_foe


def load_chest_from_save(chest, gap_x, gap_y):
    """

    :param chest:
    :param gap_x:
    :param gap_y:
    :return:
    """
    # Static data
    x_coordinate = int(chest.find("position/x").text) * TILE_SIZE + gap_x
    y_coordinate = int(chest.find("position/y").text) * TILE_SIZE + gap_y
    position = Position(x_coordinate, y_coordinate)
    sprite_closed = chest.find("closed/sprite").text.strip()
    sprite_opened = chest.find("opened/sprite").text.strip()

    # Dynamic data
    potential_items = []
    opened = chest.find("state").text.strip() == "True"
    it_name = chest.find("contains/item").text.strip()
    item = parse_item_file(it_name)

    potential_items.append((item, 1.0))

    loaded_chest = Chest(position, sprite_closed, sprite_opened, potential_items)

    if opened:
        loaded_chest.open()

    return loaded_chest


def load_door_from_save(door, gap_x, gap_y):
    """

    :param door:
    :param gap_x:
    :param gap_y:
    :return:
    """
    # Static data
    x_coordinate = int(door.find("position/x").text) * TILE_SIZE + gap_x
    y_coordinate = int(door.find("position/y").text) * TILE_SIZE + gap_y
    position = Position(x_coordinate, y_coordinate)
    sprite = door.find("sprite").text.strip()

    # Dynamic data
    pick_lock_initiated = door.find("pick_lock_initiated") is not None

    loaded_door = Door(position, sprite, pick_lock_initiated)
    return loaded_door


def load_building_from_save(building, gap_x, gap_y, shop_balance=500):
    """

    :param building:
    :param gap_x:
    :param gap_y:
    :param shop_balance:
    :return:
    """
    # Static data
    name = building.find("name").text.strip()
    x_coordinate = int(building.find("position/x").text) * TILE_SIZE + gap_x
    y_coordinate = int(building.find("position/y").text) * TILE_SIZE + gap_y
    position = Position(x_coordinate, y_coordinate)
    sprite = building.find("sprite").text.strip()
    interaction = building.find("interaction")
    interaction_element = {}
    if interaction is not None:
        talks = interaction.find("talks")
        if talks is not None:
            interaction_element["talks"] = []
            for talk in talks.findall("talk"):
                interaction_element["talks"].append(get_localized_string(talk).strip())
        else:
            interaction_element["talks"] = []
        interaction_element["gold"] = (
            int(interaction.find("gold").text.strip())
            if interaction.find("gold") is not None
            else 0
        )
        interaction_element["item"] = (
            parse_item_file(interaction.find("item").text.strip())
            if interaction.find("item") is not None
            else None
        )

    nature = building.find("type")
    if nature is not None:
        nature = nature.text.strip()
        if nature == "shop":
            stock = []
            for item in building.findall("items/item"):
                entry = {
                    "item": parse_item_file(item.find("name").text.strip()),
                    "quantity": int(item.find("quantity").text.strip()),
                }
                stock.append(entry)
            loaded_building = Shop(name, position, sprite, shop_balance, stock, interaction_element)

        else:
            print("Error : building type isn't recognized : ", type)
            raise SystemError
    else:
        loaded_building = Building(name, position, sprite, interaction_element)

    # Dynamic data
    locked = building.find("state").text.strip()
    if locked == "True":
        loaded_building.remove_interaction()

    return loaded_building


def load_obstacles(tree, gap_x, gap_y):
    """

    :param tree:
    :param gap_x:
    :param gap_y:
    :return:
    """
    loaded_obstacles = []
    for positions in tree.findall("positions"):
        fixed_y = positions.find("y")
        if fixed_y is not None:
            fixed_y = int(fixed_y.text) * TILE_SIZE + gap_y
            from_x = int(positions.find("from_x").text) * TILE_SIZE + gap_x
            to_x = int(positions.find("to_x").text) * TILE_SIZE + gap_x
            for i in range(from_x, to_x + TILE_SIZE, TILE_SIZE):
                pos = (i, fixed_y)
                loaded_obstacles.append(pos)
        else:
            fixed_x = int(positions.find("x").text) * TILE_SIZE + gap_x
            from_y = int(positions.find("from_y").text) * TILE_SIZE + gap_y
            to_y = int(positions.find("to_y").text) * TILE_SIZE + gap_y
            for i in range(from_y, to_y + TILE_SIZE, TILE_SIZE):
                pos = (fixed_x, i)
                loaded_obstacles.append(pos)

    for obstacle in tree.findall("position"):
        x_coordinate = int(obstacle.find("x").text) * TILE_SIZE + gap_x
        y_coordinate = int(obstacle.find("y").text) * TILE_SIZE + gap_y
        pos = (x_coordinate, y_coordinate)
        loaded_obstacles.append(pos)
    return loaded_obstacles


def load_portal_from_save(portal_couple, gap_x, gap_y):
    """

    :param portal_couple:
    :param gap_x:
    :param gap_y:
    :return:
    """
    first_x = int(portal_couple.find("first/position/x").text) * TILE_SIZE + gap_x
    first_y = int(portal_couple.find("first/position/y").text) * TILE_SIZE + gap_y
    first_position = Position(first_x, first_y)
    second_x = int(portal_couple.find("second/position/x").text) * TILE_SIZE + gap_x
    second_y = int(portal_couple.find("second/position/y").text) * TILE_SIZE + gap_y
    second_position = Position(second_x, second_y)
    sprite = "imgs/dungeon_crawl/" + portal_couple.find("sprite").text.strip()
    first_portal = Portal(first_position, sprite)
    second_portal = Portal(second_position, sprite)
    Portal.link_portals(first_portal, second_portal)
    return first_portal, second_portal


def load_fountain_from_save(fountain, gap_x, gap_y):
    """

    :param fountain:
    :param gap_x:
    :param gap_y:
    :return:
    """
    name = fountain.find("type").text.strip()
    x_coordinate = int(fountain.find("position/x").text) * TILE_SIZE + gap_x
    y_coordinate = int(fountain.find("position/y").text) * TILE_SIZE + gap_y
    position = Position(x_coordinate, y_coordinate)
    if name not in fountains_data:
        fountains_data[name] = etree.parse("data/fountains.xml").find(name)
    sprite = "imgs/dungeon_crawl/" + fountains_data[name].find("sprite").text.strip()
    sprite_empty = (
            "imgs/dungeon_crawl/" + fountains_data[name].find("sprite_empty").text.strip()
    )
    effect_name = fountains_data[name].find("effect").text.strip()
    power = int(fountains_data[name].find("power").text.strip())
    duration = int(fountains_data[name].find("duration").text.strip())
    effect = Effect(effect_name, power, duration)
    times = int(fountains_data[name].find("times").text.strip())

    loaded_fountain = Fountain(name, position, sprite, sprite_empty, effect, times)

    # Load remaining uses from saved data
    times = int(fountain.find("times").text.strip())
    loaded_fountain.set_times(times)

    return loaded_fountain


def load_fountain(name: str, position: Position) -> Fountain:
    if name not in fountains_data:
        fountains_data[name] = etree.parse("data/fountains.xml").find(name)

    sprite = "imgs/dungeon_crawl/" + fountains_data[name].find("sprite").text.strip()
    sprite_empty = (
            "imgs/dungeon_crawl/" + fountains_data[name].find("sprite_empty").text.strip()
    )

    effect_name = fountains_data[name].find("effect").text.strip()
    power = int(fountains_data[name].find("power").text.strip())
    duration = int(fountains_data[name].find("duration").text.strip())
    effect = Effect(effect_name, power, duration)
    times = int(fountains_data[name].find("times").text.strip())

    return Fountain(name, position, sprite, sprite_empty, effect, times)


def load_breakable_from_save(breakable, gap_x, gap_y):
    """

    :param breakable:
    :param gap_x:
    :param gap_y:
    :return:
    """
    # Static data
    x_coordinate = int(breakable.find("position/x").text) * TILE_SIZE + gap_x
    y_coordinate = int(breakable.find("position/y").text) * TILE_SIZE + gap_y
    pos = (x_coordinate, y_coordinate)
    sprite = "imgs/dungeon_crawl/dungeon/" + breakable.find("sprite").text.strip()
    hit_points = int(breakable.find("current_hp").text.strip())

    return Breakable(pos, sprite, hit_points, 0, 0)


def load_restrictions(restrictions_element):
    """

    :param restrictions_element:
    :return:
    """
    restrictions = {}
    if restrictions_element is None:
        return restrictions

    classes = restrictions_element.find("classes")
    if classes is not None:
        restrictions["classes"] = classes.text.strip().split(",")
    races = restrictions_element.find("races")
    if races is not None:
        restrictions["races"] = races.text.strip().split(",")

    return restrictions


def load_events(events_el, gap_x, gap_y):
    """

    :param events_el:
    :param gap_x:
    :param gap_y:
    :return:
    """
    events = {}
    for event in events_el:
        events[event.tag] = {}
        dialog_els = event.findall("dialog")
        if dialog_els:
            events[event.tag]["dialogs"] = []
            for dialog_element in dialog_els:
                title_element = dialog_element.find("title")
                events[event.tag]["dialogs"].append(
                    {
                        "title": title_element.text.strip()
                        if title_element is not None
                        else "",
                        "talks": [
                            talk.text.strip()
                            for talk in dialog_element.find("talks").findall("talk")
                        ],
                    }
                )
        new_players_elements = event.findall("new_player")
        if new_players_elements:
            events[event.tag]["new_players"] = [
                {
                    "name": player_element.find("name").text.strip(),
                    "position": Position(
                        int(player_element.find("position/x").text.strip()) * TILE_SIZE
                        + gap_x,
                        int(player_element.find("position/y").text.strip()) * TILE_SIZE
                        + gap_y,
                    ),
                }
                for player_element in new_players_elements
            ]

    return events


def load_player(player_element, from_save):
    """

    :param player_element:
    :param from_save:
    :return:
    """
    name = player_element.find("name").text.strip()
    level = player_element.find("level")
    if level is None:
        # If level is not specified, default value is 1
        level = 1
    else:
        level = int(level.text.strip())
    player_class = player_element.find("class").text.strip()
    race = player_element.find("race").text.strip()
    gold = int(player_element.find("gold").text.strip())
    experience = int(player_element.find("exp").text.strip()) if from_save else 0
    hit_points = int(player_element.find("hp").text.strip())
    strength = int(player_element.find("strength").text.strip())
    defense = int(player_element.find("defense").text.strip())
    res = int(player_element.find("resistance").text.strip())
    current_hp = (
        int(player_element.find("current_hp").text.strip()) if from_save else hit_points
    )
    inventory = []
    for item in player_element.findall("inventory/item"):
        item_loaded = (
            load_item(item) if from_save else parse_item_file(item.text.strip())
        )
        inventory.append(item_loaded)

    equipments = []
    for equipment in player_element.findall("equipment/*"):
        eq_loaded = (
            load_item(equipment)
            if from_save
            else parse_item_file(equipment.text.strip())
        )
        equipments.append(eq_loaded)

    alterations = []
    if from_save:
        skills = [
            (
                get_skill_data(skill.text.strip())
                if skill.text.strip() not in skills_data
                else skills_data[skill.text.strip()]
            )
            for skill in player_element.findall("skills/skill/name")
        ]
        for alteration in player_element.findall("alterations/alteration"):
            alterations.append(load_alteration(alteration))
        tree = etree.parse("data/characters.xml").getroot()
        player_t = tree.xpath(name)[0]
    else:
        skills = (
                Character.classes_data[player_class]["skills"]
                + Character.races_data[race]["skills"]
        )
        player_t = player_element

    # -- Reading of the XML file for default character's values (i.e. sprites)
    sprite = "imgs/" + player_t.find("sprite").text.strip()
    compl_sprite = player_t.find("complement_sprite")
    if compl_sprite is not None:
        compl_sprite = "imgs/" + compl_sprite.text.strip()

    player = Player(
        name,
        sprite,
        hit_points,
        defense,
        res,
        strength,
        [player_class],
        equipments,
        race,
        gold,
        level,
        skills,
        alterations,
        complementary_sprite_link=compl_sprite,
    )
    player.earn_xp(experience)
    player.items = inventory
    player.hit_points = current_hp
    if from_save:
        position = Position(
            int(player_element.find("position/x").text.strip()) * TILE_SIZE,
            int(player_element.find("position/y").text.strip()) * TILE_SIZE,
        )
        player.position = position
        state = player_element.find("turnFinished").text.strip()
        if state == "True":
            player.end_turn()
    else:
        # Up stats according to current lvl
        player.stats_up(level - 1)
        # Restore hp due to lvl up
        player.healed()

    return player


def load_players(data):
    """

    :param data:
    :return:
    """
    players = []
    for player_element in data.findall("players/player"):
        players.append(load_player(player_element, True))
    return players


def load_escaped_players(data):
    """

    :param data:
    :return:
    """
    players = []
    for player_element in data.findall("escaped_players/player"):
        players.append(load_player(player_element, True))
    return players


def init_player(name):
    """

    :param name:
    :return:
    """
    # -- Reading of the XML file
    tree = etree.parse("data/characters.xml").getroot()
    player_t = tree.xpath(name)[0]
    return load_player(player_t, False)


def load_weapon_effect(eff):
    """

    :param eff:
    :return:
    """
    loaded_effect = {}

    # Load effect
    name = eff.find("name").text.strip()
    power_element = eff.find("power")
    power = int(power_element.text.strip()) if power_element is not None else 0
    duration_element = eff.find("duration")
    duration = int(duration_element.text.strip()) if duration_element is not None else 0
    loaded_effect["effect"] = Effect(name, power, duration)

    # Load probability
    loaded_effect["probability"] = int(
        float(eff.find("probability").text.strip()) * 100
    )

    return loaded_effect


def load_item(data):
    """

    :param data:
    :return:
    """
    name = data.find("name").text.strip()

    # Retrieve static data
    item = parse_item_file(name)
    item.resell_price = int(data.find("value").text.strip())
    if isinstance(item, (Shield, Weapon)):
        item.durability = int(data.find("durability").text.strip())

    return item


def parse_item_file(name):
    """

    :param name:
    :return:
    """
    # Retrieve data root for item
    item_tree_root = etree.parse("data/items.xml").getroot().find(".//" + name)

    sprite = "imgs/dungeon_crawl/item/" + item_tree_root.find("sprite").text.strip()
    info = get_localized_string(item_tree_root.find("info")).strip()
    price = item_tree_root.find("price")
    if price is not None:
        price = int(price.text.strip())
    else:
        price = 0
    category = item_tree_root.find("category").text.strip()

    if category in ("potion", "consumable"):
        effects = []
        for effect in item_tree_root.findall(".//effect"):
            effect_name = effect.find("type").text.strip()
            power_element = effect.find("power")
            power = int(power_element.text.strip()) if power_element is not None else 0
            duration_element = effect.find("duration")
            duration = (
                int(duration_element.text.strip())
                if duration_element is not None
                else 0
            )
            effects.append(Effect(effect_name, power, duration))
        item = (
            Potion(name, sprite, info, price, effects)
            if category == "potion"
            else Consumable(name, sprite, info, price, effects)
        )
    elif category == "armor":
        body_part = item_tree_root.find("bodypart").text.strip()
        defense_element = item_tree_root.find("def")
        defense = (
            int(defense_element.text.strip()) if defense_element is not None else 0
        )
        weight = int(item_tree_root.find("weight").text.strip())
        equipment_sprites = item_tree_root.find("equipped_sprites")
        if equipment_sprites is not None:
            equipped_sprites = []
            for eq_sprite in equipment_sprites.findall("sprite"):
                equipped_sprites.append(
                    "imgs/dungeon_crawl/player/" + eq_sprite.text.strip()
                )
        else:
            equipped_sprites = [
                "imgs/dungeon_crawl/player/"
                + item_tree_root.find("equipped_sprite").text.strip()
            ]
        restrictions = load_restrictions(item_tree_root.find("restrictions"))
        item = Equipment(
            name,
            sprite,
            info,
            price,
            equipped_sprites,
            body_part,
            defense,
            0,
            0,
            weight,
            restrictions,
        )
    elif category == "shield":
        parry = int(float(item_tree_root.find("parry_rate").text.strip()) * 100)
        defense_element = item_tree_root.find("def")
        defense = (
            int(defense_element.text.strip()) if defense_element is not None else 0
        )
        fragility = int(item_tree_root.find("fragility").text.strip())
        weight = int(item_tree_root.find("weight").text.strip())
        equipped_sprite = [
            "imgs/dungeon_crawl/player/hand_left/"
            + item_tree_root.find("equipped_sprite").text.strip()
        ]
        restrictions = load_restrictions(item_tree_root.find("restrictions"))
        item = Shield(
            name,
            sprite,
            info,
            price,
            equipped_sprite,
            defense,
            weight,
            parry,
            fragility,
            restrictions,
        )
    elif category == "weapon":
        power = int(item_tree_root.find("power").text.strip())
        attack_kind = item_tree_root.find("kind").text.strip()
        weight = int(item_tree_root.find("weight").text.strip())
        fragility = int(item_tree_root.find("fragility").text.strip())
        weapon_range = [
            int(reach) for reach in item_tree_root.find("range").text.strip().split(",")
        ]
        equipped_sprite = [
            "imgs/dungeon_crawl/player/hand_right/"
            + item_tree_root.find("equipped_sprite").text.strip()
        ]
        restrictions = load_restrictions(item_tree_root.find("restrictions"))
        effects = item_tree_root.find("effects")
        possible_effects = []
        if effects is not None:
            possible_effects = [
                load_weapon_effect(eff) for eff in effects.findall("effect")
            ]

        keywords_element = item_tree_root.find("strong_against/keywords")
        strong_against = (
            [
                Keyword[keyword.upper()]
                for keyword in keywords_element.text.strip().split(",")
            ]
            if keywords_element is not None
            else []
        )

        item = Weapon(
            name,
            sprite,
            info,
            price,
            equipped_sprite,
            power,
            attack_kind,
            weight,
            fragility,
            weapon_range,
            restrictions,
            possible_effects,
            strong_against,
        )
    elif category == "key":
        for_chest = item_tree_root.find("open_chest") is not None
        for_door = item_tree_root.find("open_door") is not None
        item = Key(name, sprite, info, price, for_chest, for_door)
    elif category == "spellbook":
        spell = item_tree_root.find("effect").text.strip()
        item = Spellbook(name, sprite, info, price, spell)
    else:
        # No special category
        item = Item(name, sprite, info, price)

    return item
