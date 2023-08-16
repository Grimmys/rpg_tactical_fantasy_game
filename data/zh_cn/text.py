STR_GAME_TITLE = "以五猫之名"

# Start scene
STR_NEW_GAME = "新游戏"
STR_LOAD_GAME = "载入存档"
STR_OPTIONS = "选项"
STR_EXIT_GAME = "退出游戏"

# Close button
STR_CLOSE = "关闭"

# Load game menu
STR_LOAD_GAME_MENU = "载入存档"


def f_SAVE_NUMBER(serial_number: int):
    return f"存档 {serial_number}"


# Options menu
STR_OPTIONS_MENU = "选项"
STR_LANGUAGE_ = "语言："
STR_LANGUAGE = "语言"
STR_CHOOSE_LANGUAGE = "选择语言"
STR_MOVE_SPEED_ = "移动速度："
STR_SCREEN_MODE_ = "屏幕模式："
STR_NORMAL = "正常"
STR_FAST = "快速"
STR_SLOW = "慢速"
STR_WINDOW = "窗口化"
STR_FULL = "全屏"

# Save game menu
STR_SAVE_GAME_MENU = "保存游戏"


# Level loading scene
def f_CHAPTER_NUMBER(number: int):
    return f"第 {number} 章"


def f_LEVEL_NUMBER_AND_NAME(number: int, name: str):
    return f"第 {number} 关: {name}"


# Main menu
STR_MAIN_MENU = "主菜单"
STR_SAVE = "保存游戏"
STR_SUSPEND = "悬挂"
STR_START = "开始"
STR_DIARY = "日志"
STR_END_TURN = "下一回合"
STR_DEFAULT_DIARY_BODY_CONTENT = "No event has been recorded yet"


# Reward menu
STR_REWARD_CONGRATULATIONS = "恭喜！任务目标已完成！"


def f_EARNED_GOLD(gold: int):
    return f"获得金币: {gold} (所有人物)"


def f_EARNED_ITEMS(item):
    return f"获得物品: {item}"


# Player menu
STR_INVENTORY = "背包"
STR_EQUIPMENT = "装备"
STR_STATUS = "状态"
STR_WAIT = "等待"
STR_VISIT = "拜访"
STR_TRADE = "交易"
STR_OPEN_CHEST = "开箱子"
STR_PICK_LOCK = "撬锁"
STR_OPEN_DOOR = "开门"
STR_USE_PORTAL = "传送门"
STR_DRINK = "喝"
STR_TALK = "交谈"
STR_TAKE = "进入"
STR_ATTACK = "攻击"
STR_SELECT_AN_ACTION = "选择行为"

# Inventory menu
STR_SHOPPING_SELLING = "购入 - 卖出"  # "Shop - Selling"


def f_UR_GOLD(gold):
    return f"你的金币: {gold}"  # f"Your gold: {gold}"


# Trade menu
STR_50G_TO_RIGHT = "50 金币 ->"  # "50G ->"
STR_200G_TO_RIGHT = "200 金币 ->"
STR_ALL_TO_RIGHT = "全部金币 ->"
STR_50G_TO_LEFT = "<- 50 金币"
STR_200G_TO_LEFT = "<- 200 金币"
STR_ALL_TO_LEFT = "<- 全部金币"


def f_GOLD_AT_END(player, gold):
    return f"{player}的金币： {gold}"  # f"{player}'s gold: {gold}"


# Status menu
STR_NAME_ = "姓名："  # "Name :"
STR_SKILLS = "技能"  # "SKILLS"
STR_CLASS_ = "类型："  # "Class :"
STR_RACE_ = "种族："  # "Race :"
STR_LEVEL_ = "等级："  # "Level :"
STR_XP_ = "经验："  # "  XP :"
STR_STATS = "数值"  # "STATS"
STR_HP_ = "血量："  # "HP :"
STR_MOVE_ = "移动："  # "MOVE :"
STR_CONSTITUTION_ = "体质："  # "CONSTITUTION :"
STR_ATTACK_ = "攻击："  # "ATTACK :"
STR_DEFENSE_ = "防御："  # "DEFENSE :"
STR_MAGICAL_RES_ = "魔抗："  # "MAGICAL RES :"
STR_ALTERATIONS = "变更"  # "ALTERATIONS"
STR_NONE = "无"  # "None"


def f_DIV(partial, maximum):
    return f"{partial} / {maximum}"


# Item shop menu
STR_BUY = "购买"
STR_INFO = "信息"

# Item buy menu
STR_SHOP_BUYING = "商店 - 购买"


def f_PRICE_NUMBER(price):
    return f"价格: {price}"  # f"Price: {price}"


def f_QUANTITY_NUMBER(quantity):
    return f"数量：{quantity}"


# Item sell menu
STR_SELL = "卖出"  # "Sell"

# Item menu
STR_THROW = "丢弃"  # Throw
STR_USE = "使用"  # Use
STR_UNEQUIP = "卸下"
STR_EQUIP = "装备"


# Item description stat
def f_STAT_NAME_(stat_name):
    return f"{stat_name}："  # f"{stat_name}: "


# Item description menu
STR_RESERVED_TO = "装备给"  # "RESERVED TO"
STR_POWER = "力量"  # "POWER"
STR_DEFENSE = "防御"  # "DEFENSE"
STR_MAGICAL_RES = "魔抗"  # "MAGICAL RES"
STR_TYPE_OF_DAMAGE = "伤害类型"  # "TYPE OF DAMAGE"
STR_REACH = "攻击距离"  # "REACH"
STR_EFFECT = "效果"  # "EFFECT"
STR_STRONG_AGAINST = "克制"  # "STRONG AGAINST"
STR_PARRY_RATE = "格挡率"  # "PARRY RATE"
STR_DURABILITY = "持久性"  # "DURABILITY"
STR_WEIGHT = "重量"  # "WEIGHT"

# Status entity menu
STR_LOOT = "掉落物"  # "LOOT"
STR_TYPE_ = "类型："  # "TYPE :"
STR_REACH_ = "攻击距离："  # "REACH :"


def f_LEVEL_NUMBER_ENTITY(level):
    return f"等级：{level}"  # f"LEVEL : {level}"


# Sidebar
STR_FOE = "敌人"  # "FOE"
STR_PLAYER = "玩家"  # "PLAYER"
STR_ALLY = "盟友"  # "ALLY"
STR_UNLIVING_ENTITY = "无生命实体"  # "UNLIVING ENTITY"
STR_NAME_SIDEBAR_ = "名称："  # "NAME : "
STR_ALTERATIONS_ = "变更："  # "ALTERATIONS : "


def f_TURN_NUMBER_SIDEBAR(number_turns):
    return f"第 {number_turns} 回合"  # f"TURN {number_turns}"


def f_LEVEL_NUMBER_SIDEBAR(level_id):
    return f"第 {level_id} 关"  # f"LEVEL {level_id}"


# Chest menu
STR_CHEST = "箱子"  # "Chest"


# Alternation info menu
def f_TURNS_LEFT_NUMBER(turns_left):
    return f"剩余轮数：{turns_left}"


# Ask save menu
STR_SAVE_THE_GAME_ = "保存游戏？"
STR_YES = "是"
STR_NO = "否"


# src.game_entities.building
def f_YOU_RECEIVED_NUMBER_GOLD(gold):
    return f"[你得到了{gold}金币]"


def f_YOU_RECEIVED_ITEM(item):
    return f"[你得到了 {item}]"


# Messages
STR_ERROR_NOT_ENOUGH_TILES_TO_SET_PLAYERS = (
    "错误！没有足够的地图空间来安置玩家..."  # "Error ! Not enough free tiles to set players..."
)
STR_GAME_HAS_BEEN_SAVED = "游戏已保存"  # "Game has been saved"
STR_ITEM_HAS_BEEN_ADDED_TO_UR_INVENTORY = (
    "物品已放入背包"  # "Item has been added to your inventory"
)
STR_YOU_FOUND_IN_THE_CHEST = "你在箱子中找到了"  # "You found in the chest"
STR_DOOR_HAS_BEEN_OPENED = "门已打开了"  # "Door has been opened"
STR_YOU_HAVE_NO_FREE_SPACE_IN_YOUR_INVENTORY = (
    "背包没有剩余的空间了"  # "You have no free space in your inventory"
)
STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO = (
    "开始撬锁，需要一个回合结束"  # "Started picking, one more turn to go"
)
STR_THERE_IS_NO_FREE_SQUARE_AROUND_THE_OTHER_PORTAL = (
    "传送门的另一侧被堵死了"  # "There is no free square around the other portal"
)
STR_BUT_THERE_IS_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_TAKE_IT = (
    "但背包里没有足够的空间来装它了！"  # But there is not enough space in inventory to take it!"
)
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_DOOR = "你没有打开门的钥匙"  # "You have no key to open a door"
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_CHEST = "你没有打开箱子的钥匙"  # "You have no key to open a chest"
STR_ITEM_HAS_BEEN_TRADED = "物品已被交易"  # "Item has been traded"
STR_ITEM_HAS_BEEN_THROWN_AWAY = "物品已被丢弃"  # "Item has been thrown away"
STR_THE_ITEM_CANNOT_BE_UNEQUIPPED_NOT_ENOUGH_SPACE_IN_UR_INVENTORY = "不能卸下装备：背包中没有足够的空间"  # "The item can't be unequipped : Not enough space in your inventory."
STR_THE_ITEM_HAS_BEEN_UNEQUIPPED = "装备已卸下"  # "The item has been unequipped"
STR_THE_ITEM_HAS_BEEN_EQUIPPED = "物品已被装备"  # "The item has been equipped"
STR_PREVIOUS_EQUIPPED_ITEM_HAS_BEEN_ADDED_TO_YOUR_INVENTORY = (
    "先前装备的物品已被放入背包中"  # "Previous equipped item has been added to your inventory"
)
STR_THE_ITEM_HAS_BEEN_BOUGHT = "物品已购入"
STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM = "背包里没有足够的空间来购买这个物品"
STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM = "没有足够的金币来购买这件物品"
STR_THE_ITEM_HAS_BEEN_SOLD = "物品已被卖出"
STR_THIS_ITEM_CANT_BE_SOLD = "这个物品不能被卖出"
STR_THIS_HOUSE_SEEMS_CLOSED = "这个房子看起来关门了"


def f_ATTACKER_ATTACKED_TARGET_BUT_PARRIED(attacker, target):
    return f"{attacker}攻击了{target}...但是{target}闪避了"  # f"{attacker} attacked {target}... But {target} parried!"


def f_ATTACKER_DEALT_DAMAGE_TO_TARGET(attacker, target, damage):
    return f"{attacker}给{target}造成了{damage}点伤害"  # f"{attacker} dealt {damage} damage to {target}"


def f_TARGET_DIED(target):
    return f"{target}死了！"  # f"{target} died!"


def f_TARGET_DROPPED_ITEM(target, item):
    return f"{target}掉落了{item}"  # f"{target} dropped {item}"


def f_TARGET_HAS_NOW_NUMBER_HP(target, hp):
    return f"{target}现在有{hp}点血量"  # f"{target} has now {hp} HP"


def f_ATTACKER_EARNED_NUMBER_XP(attacker, experience):
    return f"{attacker}得到了{experience}点经验"  # f"{attacker} earned {experience} XP"


def f_ATTACKER_GAINED_A_LEVEL(attacker):
    return f"{attacker}升级了！"  # f"{attacker} gained a level!"


def f_ITEM_CANNOT_BE_TRADED_NOT_ENOUGH_PLACE_IN_RECEIVERS_INVENTORY(receiver):
    return f"不能完成交易：{receiver}的背包中没有足够的空间"  # f"Item can't be traded: not enough place in {receiver}'s inventory"


def f_THIS_ITEM_CANNOT_BE_EQUIPPED_PLAYER_DOESNT_SATISFY_THE_REQUIREMENTS(
    selected_player,
):
    return f"这件物品不能被装备：{selected_player}不满足条件"  # f"This item can't be equipped: {selected_player} doesn't satisfy the requirements"


# Constant sprites
STR_NEW_TURN = "新的回合 ！"
STR_VICTORY = "胜利 ！"
STR_DEFEAT = "失败 ！"
STR_MAIN_MISSION = "主要任务"
STR_OPTIONAL_OBJECTIVES = "次要任务"


# effect.py
def f_ENTITY_RECOVERED_NUMBER_HP(entity, recovered):
    return f"{entity}恢复了{recovered}点血量"  # f"{entity} recovered {recovered} HP."


def f_ENTITY_IS_AT_FULL_HEALTH_AND_CANT_BE_HEALED(entity):
    return (
        f"{entity}正处于满血状态，不能被治愈"  # f"{entity} is at full health and can't be healed!"
    )


def f_ENTITY_EARNED_NUMBER_XP(entity, power):
    return f"{entity}得到了{power}点经验"  # f"{entity} earned {power} XP"


def f_ENTITY_GAINED_A_LEVEL(entity):
    return f"。{entity}升级了！"  # f". {entity} gained a level!"


def f_THE_SPEED_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity}的速度在{duration}个回合内提升"  # f"The speed of {entity} has been increased for {self.duration} turns"


def f_THE_STRENGTH_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity}的力量在{duration}个回合内提升"  # f"The strength of {entity} has been increased for {self.duration} turns"


def f_THE_DEFENSE_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity}的防御在{duration}个回合内提升"  # f"The defense of {entity} has been increased for {self.duration} turns"


def f_ENTITY_HAS_BEEN_STUNNED_FOR_NUMBER_TURNS(entity, duration):
    return (
        f"{entity}被击晕了{duration}回合"  # f"{entity} has been stunned for {duration} turns"
    )


def f_RECOVER_NUMBER_HP(power):
    return f"恢复{power}点血量"  # f"Recover {power} HP"


def f_EARN_NUMBER_XP(power):
    return f"获得{power}点经验"  # f"Earn {power} XP"


TRANSLATIONS = {
    "items": {
        "key": "钥匙",
        "bones": "骨头",
        "topaz": "黄玉",
        "iron_ring": "铁戒指",
        "monster_meat": "怪物肉",
        "life_potion": "生命药水",
        "speed_potion": "速度药水",
        "rabbit_step_potion": "兔子步药水",
        "strength_potion": "力量药水",
        "vigor_potion": "活力药水",
        "scroll_of_knowledge": "知识卷轴",
        "scroll_of_cerberus": "地狱犬卷轴",
        "chest_key": "箱子钥匙",
        "door_key": "门钥匙",
        "green_book": "绿皮书",
        "poket_knife": "口袋刀",
        "dagger": "匕首",
        "club": "木棒",
        "short_sword": "短剑",
        "wooden_spear": "木矛",
        "halberd": "戟",
        "pickaxe": "镐子",
        "wooden_bow": "木弓",
        "basic_bow": "基础的弓",
        "wooden_staff": "木法杖",
        "necromancer_staff": "死灵法杖",
        "plumed_helmet": "羽毛头盔",
        "black_hood": "黑头罩",
        "helmet": "头盔",
        "horned_helmet": "带角头盔",
        "gold_helmet": "金头盔",
        "chainmail": "链甲",
        "leather_armor": "皮盔甲",
        "scale_mail": "规模邮件",
        "gold_armor": "金盔甲",
        "spy_outfit": "间谍装",
        "barding_magenta": "洋红马甲",
        "brown_boots": "棕靴子",
        "black_boots": "黑靴子",
        "gold_boots": "金靴子",
        "wooden_shield": "木盾牌",
        "pocket_knife": "小刀",
        "basic_spear": "基础的矛",
        "basic_halberd": "基础的戟",
    },
    "effects": {
        "defense_up": "防御提升",
        "strength_up": "力量提升",
        "speed_up": "速度提升",
        "stun": "晕厥",
        "no_attack": "不能攻击",
    },
    "alterations": {
        "defense_up": "防御提升",
        "strength_up": "力量提升",
        "speed_up": "速度提升",
        "stun": "晕厥",
        "no_attack": "不能攻击",
    },
    "races_and_classes": {
        # Races
        "human": "人类",
        "elf": "小精灵",
        "dwarf": "矮人",
        "centaur": "半人马",
        "gnome": "侏儒",
        # Classes
        "warrior": "战士",
        "ranger": "游骑兵",
        "spy": "间谍",
    },
    "foe_keywords": {
        "undead": "不死族",
        "large": "大型",
        "cavalry": "骑兵",
        "mutant": "变异体",
        "fly": "飞行体",
        "none": "无",
    },
    "entity_names": {
        "skeleton": "骷髅",
        "skeleton_cobra": "骷髅蟒",
        "necrophage": "死灵",
        "lich_boss": "Lich灵主",
        "mutant_bee": "变异蜜蜂",
        "mutant_lizard": "变异蜥蜴",
        "mutant_cultist": "变异邪教徒",
        "mutant_ant": "变异蚂蚁",
        "obstacle": "障碍",
        "shop": "商店",
        "house": "房子",
        "chest": "箱子",
        "healer": "愈伤池",
        "tavern": "酒馆",
        "door": "门",
        "altar": "祭坛",
        "armory": "军械店",
        "apothecary": "药剂店",
    },
    "attack_kinds": {
        "physical": "物理",
        "spiritual": "精神",
    },
}
