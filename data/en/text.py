STR_GAME_TITLE = "In the name of the Five Cats"

# Start scene
STR_NEW_GAME = "New game"
STR_LOAD_GAME = "Load game"
STR_OPTIONS = "Options"
STR_EXIT_GAME = "Exit game"

# Close button
STR_CLOSE = "Close"

# Load game menu
STR_LOAD_GAME_MENU = "Load Game"


def f_SAVE_NUMBER(number: int):
    return f"Save {number}"


# Options menu
STR_OPTIONS_MENU = "Options"
STR_LANGUAGE_ = "Language :"
STR_LANGUAGE = "Language"
STR_CHOOSE_LANGUAGE = "Choose Language"
STR_MOVE_SPEED_ = "Move speed :"
STR_SCREEN_MODE_ = "Screen mode :"
STR_NORMAL = "Normal"
STR_FAST = "Fast"
STR_SLOW = "Slow"
STR_WINDOW = "Window"
STR_FULL = "Full"

# Save game menu
STR_SAVE_GAME_MENU = "Save Game"


# Level loading scene
def f_CHAPTER_NUMBER(number: int):
    return f"Chapter {number}"


def f_LEVEL_NUMBER_AND_NAME(number: int, name: str):
    return f"Level {number}: {name}"


# Main menu
STR_MAIN_MENU = "Main Menu"
STR_SAVE = "Save"
STR_SUSPEND = "Suspend"
STR_START = "Start"
STR_DIARY = "Diary"
STR_END_TURN = "End turn"
STR_DEFAULT_DIARY_BODY_CONTENT = "No event has been recorded yet"

# Reward menu
STR_REWARD_CONGRATULATIONS = "Congratulations! Objective has been completed!"


def f_EARNED_GOLD(gold: int):
    return f"Earned gold: {gold} (all characters)"


def f_EARNED_ITEMS(item):
    return f"Earned item: {item}"


# Player menu
STR_INVENTORY = "Inventory"
STR_EQUIPMENT = "Equipment"
STR_STATUS = "Status"
STR_WAIT = "Wait"
STR_VISIT = "Visit"
STR_TRADE = "Trade"
STR_OPEN_CHEST = "Open Chest"
STR_PICK_LOCK = "Pick Lock"
STR_OPEN_DOOR = "Open Door"
STR_USE_PORTAL = "Use Portal"
STR_DRINK = "Drink"
STR_TALK = "Talk"
STR_TAKE = "Take"
STR_ATTACK = "Attack"
STR_SELECT_AN_ACTION = "Select an action"

# Inventory menu
STR_SHOPPING_SELLING = "Shop - Selling"


def f_UR_GOLD(gold):
    return f"Your gold: {gold}"


def f_SHOP_GOLD(shop_balance):
    return f"Shopkeeper gold: {shop_balance}"


# Trade menu
STR_50G_TO_RIGHT = "50G ->"
STR_200G_TO_RIGHT = "200G ->"
STR_ALL_TO_RIGHT = "All ->"
STR_50G_TO_LEFT = "<- 50G"
STR_200G_TO_LEFT = "<- 200G"
STR_ALL_TO_LEFT = "<- All"


def f_GOLD_AT_END(player, gold):
    return f"{player}'s gold: {gold}"


# Status menu
STR_NAME_ = "Name :"
STR_SKILLS = "SKILLS"
STR_CLASS_ = "Class :"
STR_RACE_ = "Race :"
STR_LEVEL_ = "Level :"
STR_XP_ = "  XP :"
STR_STATS = "STATS"
STR_HP_ = "HP :"
STR_MOVE_ = "MOVE :"
STR_CONSTITUTION_ = "CONSTITUTION :"
STR_ATTACK_ = "ATTACK :"
STR_DEFENSE_ = "DEFENSE :"
STR_MAGICAL_RES_ = "MAGICAL RES :"
STR_ALTERATIONS = "ALTERATIONS"
STR_NONE = "None"


def f_DIV(partial, maximum):
    return f"{partial} / {maximum}"


# Item shop menu
STR_BUY = "Buy"
STR_INFO = "Info"

# Item buy menu
STR_SHOP_BUYING = "Shop - Buying"


def f_PRICE_NUMBER(price):
    return f"Price: {price}"


def f_QUANTITY_NUMBER(quantity):
    return f"Quantity: {quantity}"


# Item sell menu
STR_SELL = "Sell"

# Item menu
STR_THROW = "Throw"
STR_USE = "Use"
STR_UNEQUIP = "Unequip"
STR_EQUIP = "Equip"


# Item description stat
def f_STAT_NAME_(stat_name):
    return f"{stat_name}: "


# Item description menu
STR_RESERVED_TO = "RESERVED TO"
STR_POWER = "POWER"
STR_DEFENSE = "DEFENSE"
STR_MAGICAL_RES = "MAGICAL RES"
STR_TYPE_OF_DAMAGE = "TYPE OF DAMAGE"
STR_REACH = "REACH"
STR_EFFECT = "EFFECT"
STR_STRONG_AGAINST = "STRONG AGAINST"
STR_PARRY_RATE = "PARRY RATE"
STR_DURABILITY = "DURABILITY"
STR_WEIGHT = "WEIGHT"

# Status entity menu
STR_LOOT = "LOOT"
STR_TYPE_ = "TYPE :"
STR_REACH_ = "REACH :"


def f_LEVEL_NUMBER_ENTITY(level):
    return f"LEVEL : {level}"


# Sidebar
STR_FOE = "FOE"
STR_PLAYER = "PLAYER"
STR_ALLY = "ALLY"
STR_UNLIVING_ENTITY = "UNLIVING ENTITY"
STR_NAME_SIDEBAR_ = "NAME : "
STR_ALTERATIONS_ = "ALTERATIONS : "


def f_TURN_NUMBER_SIDEBAR(number_turns):
    return f"TURN {number_turns}"


def f_LEVEL_NUMBER_SIDEBAR(level_id):
    return f"LEVEL {level_id}"


# Chest menu
STR_CHEST = "Chest"


# Alternation info menu
def f_TURNS_LEFT_NUMBER(turns_left):
    return f"Turns left: {turns_left}"


# Ask save menu
STR_SAVE_THE_GAME_ = "Save the Game?"
STR_YES = "Yes"
STR_NO = "No"


# src.game_entities.building
def f_YOU_RECEIVED_NUMBER_GOLD(gold):
    return f"[You received {gold} gold]"


def f_YOU_RECEIVED_ITEM(item):
    return f"[You received {item}]"


# Messages
STR_ERROR_NOT_ENOUGH_TILES_TO_SET_PLAYERS = (
    "Error ! Not enough free tiles to set players..."
)
STR_GAME_HAS_BEEN_SAVED = "Game has been saved"
STR_ITEM_HAS_BEEN_ADDED_TO_UR_INVENTORY = "Item has been added to your inventory"
STR_YOU_FOUND_IN_THE_CHEST = "You found in the chest"
STR_DOOR_HAS_BEEN_OPENED = "Door has been opened"
STR_YOU_HAVE_NO_FREE_SPACE_IN_YOUR_INVENTORY = (
    "You have no free space in your inventory"
)
STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO = "Started picking, one more turn to go"
STR_THERE_IS_NO_FREE_SQUARE_AROUND_THE_OTHER_PORTAL = (
    "There is no free square around the other portal"
)
STR_BUT_THERE_IS_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_TAKE_IT = (
    "But there is not enough space in inventory to take it!"
)
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_DOOR = "You have no key to open a door"
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_CHEST = "You have no key to open a chest"
STR_ITEM_HAS_BEEN_TRADED = "Item has been traded"
STR_ITEM_HAS_BEEN_THROWN_AWAY = "Item has been thrown away"
STR_THE_ITEM_CANNOT_BE_UNEQUIPPED_NOT_ENOUGH_SPACE_IN_UR_INVENTORY = (
    "The item can't be unequipped : Not enough space in your inventory."
)
STR_THE_ITEM_HAS_BEEN_UNEQUIPPED = "The item has been unequipped"
STR_THE_ITEM_HAS_BEEN_EQUIPPED = "The item has been equipped"
STR_PREVIOUS_EQUIPPED_ITEM_HAS_BEEN_ADDED_TO_YOUR_INVENTORY = (
    "Previous equipped item has been added to your inventory"
)
STR_THE_ITEM_HAS_BEEN_BOUGHT = "The item has been bought."
STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM = (
    "Not enough space in inventory to buy this item."
)
STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM = "Not enough gold to buy this item."
STR_THE_ITEM_HAS_BEEN_SOLD = "The item has been sold."
STR_THIS_ITEM_CANT_BE_SOLD = "The vendor lacks the funds to buy from you!"
STR_THIS_HOUSE_SEEMS_CLOSED = "This house seems closed..."


def f_ATTACKER_ATTACKED_TARGET_BUT_PARRIED(attacker, target):
    return f"{attacker} attacked {target}... But {target} parried!"


def f_ATTACKER_DEALT_DAMAGE_TO_TARGET(attacker, target, damage):
    return f"{attacker} dealt {damage} damage to {target}"


def f_TARGET_DIED(target):
    return f"{target} died!"


def f_TARGET_DROPPED_ITEM(target, item):
    return f"{target} dropped {item}"


def f_TARGET_HAS_NOW_NUMBER_HP(target, hp):
    return f"{target} has now {hp} HP"


def f_ATTACKER_EARNED_NUMBER_XP(attacker, experience):
    return f"{attacker} earned {experience} XP"


def f_ATTACKER_GAINED_A_LEVEL(attacker):
    return f"{attacker} gained a level!"


def f_ITEM_CANNOT_BE_TRADED_NOT_ENOUGH_PLACE_IN_RECEIVERS_INVENTORY(receiver):
    return f"Item can't be traded: not enough place in {receiver}'s inventory"


def f_THIS_ITEM_CANNOT_BE_EQUIPPED_PLAYER_DOESNT_SATISFY_THE_REQUIREMENTS(
    selected_player,
):
    return f"This item can't be equipped: {selected_player} doesn't satisfy the requirements"


# Constant sprites
STR_NEW_TURN = "NEW TURN !"
STR_VICTORY = "VICTORY !"
STR_DEFEAT = "DEFEAT !"
STR_MAIN_MISSION = "MAIN MISSION"
STR_OPTIONAL_OBJECTIVES = "OPTIONAL OBJECTIVES"


# effect.py
def f_ENTITY_RECOVERED_NUMBER_HP(entity, recovered):
    return f"{entity} recovered {recovered} HP."


def f_ENTITY_IS_AT_FULL_HEALTH_AND_CANT_BE_HEALED(entity):
    return f"{entity} is at full health and can't be healed!"


def f_ENTITY_EARNED_NUMBER_XP(entity, power):
    return f"{entity} earned {power} XP"


def f_ENTITY_GAINED_A_LEVEL(entity):
    return f". {entity} gained a level!"


def f_THE_SPEED_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"The speed of {entity} has been increased for {duration} turns"


def f_THE_STRENGTH_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"The strength of {entity} has been increased for {duration} turns"


def f_THE_DEFENSE_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"The defense of {entity} has been increased for {duration} turns"


def f_ENTITY_HAS_BEEN_STUNNED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} has been stunned for {duration} turns"


def f_RECOVER_NUMBER_HP(power):
    return f"Recover {power} HP"


def f_EARN_NUMBER_XP(power):
    return f"Earn {power} XP"


TRANSLATIONS = {
    "items": {
        "key": "Key",
        "bones": "Bones",
        "topaz": "Topaz",
        "iron_ring": "Iron Ring",
        "monster_meat": "Monster Meat",
        "life_potion": "Life Potion",
        "speed_potion": "Speed Potion",
        "rabbit_step_potion": "Rabbit Step Potion",
        "strength_potion": "Strength Potion",
        "vigor_potion": "Vigor Potion",
        "scroll_of_knowledge": "Scroll of Knowledge",
        "scroll_of_cerberus": "Scroll of Cerberus",
        "chest_key": "Chest Key",
        "door_key": "Door Key",
        "green_book": "Green Book",
        "poket_knife": "Poket Knife",
        "dagger": "Dagger",
        "club": "Club",
        "short_sword": "Short Sword",
        "wooden_spear": "Wooden Spear",
        "halberd": "Halberd",
        "pickaxe": "Pickaxe",
        "wooden_bow": "Wooden Bow",
        "basic_bow": "Basic Bow",
        "wooden_staff": "Wooden Staff",
        "necromancer_staff": "Necromancer Staff",
        "plumed_helmet": "Plumed Helmet",
        "black_hood": "Black Hood",
        "helmet": "Helmet",
        "horned_helmet": "Horned Helmet",
        "gold_helmet": "Gold Helmet",
        "chainmail": "Chainmail",
        "leather_armor": "Leather Armor",
        "scale_mail": "Scale Mail",
        "gold_armor": "Gold Armor",
        "spy_outfit": "Spu Outfit",
        "barding_magenta": "Barding Magenta",
        "brown_boots": "Brown Boots",
        "black_boots": "Black Boots",
        "gold_boots": "Gold Boots",
        "wooden_shield": "Wooden Shield",
        "pocket_knife": "Pocket Knife",
        "basic_spear": "Basic Spear",
        "basic_halberd": "Basic Halberd",
    },
    "effects": {
        "defense_up": "Defense up",
        "strength_up": "Strength up",
        "speed_up": "Speed up",
        "stun": "Stun",
        "no_attack": "No attack",
    },
    "alterations": {
        "defense_up": "Defense up",
        "strength_up": "Strength up",
        "speed_up": "Speed up",
        "stun": "Stun",
        "no_attack": "No attack",
    },
    "races_and_classes": {
        # Races
        "human": "Human",
        "elf": "Elf",
        "dwarf": "Dwarf",
        "centaur": "Centaur",
        "gnome": "Gnome",
        # Classes
        "warrior": "Warrior",
        "ranger": "Ranger",
        "spy": "Spy",
    },
    "foe_keywords": {
        "undead": "Undead",
        "large": "Large",
        "cavalry": "Cavalry",
        "mutant": "Mutant",
        "fly": "Fly",
        "none": "None",
    },
    "entity_names": {
        "skeleton": "Skeleton",
        "skeleton_cobra": "Skeleton Cobra",
        "necrophage": "Necrophage",
        "lich_boss": "Lich Boss",
        "mutant_bee": "Mutant Bee",
        "mutant_lizard": "Mutant Lizard",
        "mutant_cultist": "Mutant Cultist",
        "mutant_ant": "Mutant Ant",
        "obstacle": "Obstacle",
        "shop": "Shop",
        "house": "House",
        "chest": "Chest",
        "healer": "Healer",
        "tavern": "Tavern",
        "door": "Door",
        "altar": "Altar",
        "armory": "Armory",
        "apothecary": "Apothecary",
    },
    "attack_kinds": {
        "physical": "Physical",
        "spiritual": "Spiritual",
    },
}
