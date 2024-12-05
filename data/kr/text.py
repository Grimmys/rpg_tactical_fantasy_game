STR_GAME_TITLE = """In the name of the Five Cats
    다섯 고양이의 이름으로"""

# Start scene
STR_NEW_GAME = "새 게임"
STR_LOAD_GAME = "불러오기"
STR_OPTIONS = "설정"
STR_EXIT_GAME = "게임 종료"
STR_SELECT_LEVEL = "레벨 선택"

# Close button
STR_CLOSE = "닫기"

# Load game menu
STR_LOAD_GAME_MENU = "불러오기"

# 게임 레벨 선택
STR_SELECT_LEVEL = "레벨 선택하기"


def f_SAVE_NUMBER(number: int):
    return f"세이브 {number}"

def f_RESTART_NUMBER(number: int):
    return f"다시 시도하기"


# Options menu
STR_OPTIONS_MENU = "설정"
STR_LANGUAGE_ = "언어 :"
STR_LANGUAGE = "언어"
STR_CHOOSE_LANGUAGE = "언어 선택"
STR_MOVE_SPEED_ = "이동 속도 :"
STR_LEVEL_MODE_ = "난이도 설정 :"
STR_SCREEN_MODE_ = "화면 모드 :"
STR_EASY_ = "쉬움"
STR_NORMAL_ = "보통"
STR_HARD_ = "어려움"
STR_NORMAL = "보통"
STR_FAST = "빠름"
STR_SLOW = "느림"
STR_WINDOW = "창모드"
STR_FULL = "전체화면"

# Save game menu
STR_SAVE_GAME_MENU = "저장하기"

STR_RESTART_TITLE = "다시 시도하겠습니까?"


# Level loading scene
def f_CHAPTER_NUMBER(number: int):
    return f"챕터 {number}"


def f_LEVEL_NUMBER_AND_NAME(number: int, name: str):
    return f"레벨 {number}: {name}"


# Main menu
STR_MAIN_MENU = "메인메뉴"
STR_SAVE = "저장"
STR_RESTART = "다시 시도"
STR_CHOICE_MODE = "난이도 설정"
STR_SUSPEND = "메인으로"
STR_START = "시작"
STR_DIARY = "일기장"
STR_END_TURN = "턴 종료"
STR_DEFAULT_DIARY_BODY_CONTENT = "기록된 활동 없음"

# Reward menu
STR_REWARD_CONGRATULATIONS = "축하합니다! 목표를 달성했습니다!"


def f_EARNED_GOLD(gold: int):
    return f"획득 골드: {gold} (모든 챕터)"


def f_EARNED_ITEMS(item):
    return f"획득한 아이템: {item}"


# Player menu
STR_INVENTORY = "인벤토리"
STR_EQUIPMENT = "장비"
STR_STATUS = "능력치"
STR_WAIT = "대기"
STR_VISIT = "방문"
STR_TRADE = "거래"
STR_OPEN_CHEST = "상자 열기"
STR_PICK_LOCK = "잠금 풀기"
STR_OPEN_DOOR = "문 열기"
STR_USE_PORTAL = "포탈 사용"
STR_DRINK = "마시기"
STR_TALK = "대화하기"
STR_TAKE = "이동"
STR_ATTACK = "공격"
STR_SELECT_AN_ACTION = "행동 선택"

# Inventory menu
STR_SHOPPING_SELLING = "상점 - 판매"


def f_UR_GOLD(gold):
    return f"소유 골드: {gold}"


def f_SHOP_GOLD(shop_balance):
    return f"상인 골드: {shop_balance}"


# Trade menu
STR_50G_TO_RIGHT = "50G ->"
STR_200G_TO_RIGHT = "200G ->"
STR_ALL_TO_RIGHT = "All ->"
STR_50G_TO_LEFT = "<- 50G"
STR_200G_TO_LEFT = "<- 200G"
STR_ALL_TO_LEFT = "<- All"


def f_GOLD_AT_END(player, gold):
    return f"{player}'의 골드: {gold}"


# Status menu
STR_NAME_ = "이름 :"
STR_SKILLS = "스킬"
STR_CLASS_ = "직업 :"
STR_RACE_ = "종족 :"
STR_LEVEL_ = "레벨 :"
STR_XP_ = "  경험치 :"
STR_STATS = "능력치"
STR_HP_ = "체력 : "
STR_MOVE_ = "이동 :"
STR_CONSTITUTION_ = "내구력 :"
STR_ATTACK_ = "공격 :"
STR_DEFENSE_ = "방어 :"
STR_MAGICAL_RES_ = "마법 저항 :"
STR_ALTERATIONS = "변이"
STR_NONE = "없음"


def f_DIV(partial, maximum):
    return f"{partial} / {maximum}"


# Item shop menu
STR_BUY = "구매"
STR_INFO = "정보"

# Item buy menu
STR_SHOP_BUYING = "상점 - 구매"


def f_PRICE_NUMBER(price):
    return f"가격: {price}"


def f_QUANTITY_NUMBER(quantity):
    return f"수량: {quantity}"


# Item sell menu
STR_SELL = "판매"

# Item menu
STR_THROW = "버리기"
STR_USE = "사용"
STR_UNEQUIP = "착용해제"
STR_EQUIP = "착용"


# Item description stat
def f_STAT_NAME_(stat_name):
    return f"{stat_name}: "


# Item description menu
STR_RESERVED_TO = "사용직업"
STR_POWER = "공격력"
STR_DEFENSE = "방어력"
STR_MAGICAL_RES = "마법 저항"
STR_TYPE_OF_DAMAGE = "데미지 종류"
STR_REACH = "사거리"
STR_EFFECT = "효과"
STR_STRONG_AGAINST = "강한 대상"
STR_PARRY_RATE = "반격 확률"
STR_DURABILITY = "내구도"
STR_WEIGHT = "무게"

# Status entity menu
STR_LOOT = "전리품"
STR_TYPE_ = "종류 :"
STR_REACH_ = "사거리 :"


def f_LEVEL_NUMBER_ENTITY(level):
    return f"레벨 : {level}"


# Sidebar
STR_FOE = "적"
STR_PLAYER = "플레이어"
STR_ALLY = "아군"
STR_UNLIVING_ENTITY = "구조물"
STR_NAME_SIDEBAR_ = "이름 : "
STR_ALTERATIONS_ = "변이 : "


def f_TURN_NUMBER_SIDEBAR(number_turns):
    return f"턴 {number_turns}"


def f_LEVEL_NUMBER_SIDEBAR(level_id):
    return f"레벨 {level_id}"


# Chest menu
STR_CHEST = "상자"


# Alternation info menu
def f_TURNS_LEFT_NUMBER(turns_left):
    return f"남은 턴: {turns_left}"


# Ask save menu
STR_SAVE_THE_GAME_ = "저장하시겠습니까?"
STR_YES = "네"
STR_NO = "아니오"


# src.game_entities.building
def f_YOU_RECEIVED_NUMBER_GOLD(gold):
    return f"[{gold} 골드를 받았습니다.]"


def f_YOU_RECEIVED_ITEM(item):
    return f"[{item} 을 받았습니다.]"


# Messages
STR_ERROR_NOT_ENOUGH_TILES_TO_SET_PLAYERS = (
    "오류 ! 충분한 타일이 없습니다..."
)
STR_GAME_HAS_BEEN_SAVED = "저장되었습니다"
STR_ITEM_HAS_BEEN_ADDED_TO_UR_INVENTORY = "인벤토리에 추가되었습니다"
STR_YOU_FOUND_IN_THE_CHEST = "상자에서 발견했습니다"
STR_DOOR_HAS_BEEN_OPENED = "문이 열렸습니다"
STR_YOU_HAVE_NO_FREE_SPACE_IN_YOUR_INVENTORY = (
    "인벤토리에 공간이 부족합니다"
)
STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO = "Started picking, one more turn to go"
STR_THERE_IS_NO_FREE_SQUARE_AROUND_THE_OTHER_PORTAL = (
    "다른 포탈 주변에 빈 공간이 없습니다"
)
STR_BUT_THERE_IS_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_TAKE_IT = (
    "인벤토리에 공간이 부족합니다!"
)
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_DOOR = "문 열쇠가 없습니다"
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_CHEST = "상자 열쇠가 없습니다"
STR_ITEM_HAS_BEEN_TRADED = "아이템이 거래되었습니다"
STR_ITEM_HAS_BEEN_THROWN_AWAY = "아이템을 버렸습니다"
STR_THE_ITEM_CANNOT_BE_UNEQUIPPED_NOT_ENOUGH_SPACE_IN_UR_INVENTORY = (
    "장비 착용 불가 : 인벤토리에 공간이 없습니다."
)
STR_THE_ITEM_HAS_BEEN_UNEQUIPPED = "장비 해제됨"
STR_THE_ITEM_HAS_BEEN_EQUIPPED = "장비 착용됨"
STR_PREVIOUS_EQUIPPED_ITEM_HAS_BEEN_ADDED_TO_YOUR_INVENTORY = (
    "이전 착용장비가 인벤토리에 추가되었습니다"
)
STR_THE_ITEM_HAS_BEEN_BOUGHT = "아이템 구매됨."
STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM = (
    "인벤토리에 빈 공간이 없습니다."
)
STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM = "골드가 부족합니다."
STR_THE_ITEM_HAS_BEEN_SOLD = "아이템이 판매되었습니다"
STR_THIS_ITEM_CANT_BE_SOLD = "상인이 당신의 물건을 살 자금이 부족합니다!"
STR_THIS_HOUSE_SEEMS_CLOSED = "이 집은 잠긴 것 같다..."


def f_ATTACKER_ATTACKED_TARGET_BUT_PARRIED(attacker, target):
    return f"{attacker} 가 {target} 공격... 하지만 {target}가 막았다!"

def f_ATTACKER_DEALT_DAMAGE_TO_TARGET(attacker, target, damage):
    return f"{attacker} 가 {target}에게 {damage} 데미지를 주었다"


def f_TARGET_DIED(target):
    return f"{target}가 죽었다!"


def f_TARGET_DROPPED_ITEM(target, item):
    return f"{target}가 {item} 을/를 떨어트렸다"


def f_TARGET_HAS_NOW_NUMBER_HP(target, hp):
    return f"{target} 의 현재 체력 {hp}"


def f_ATTACKER_EARNED_NUMBER_XP(attacker, experience):
    return f"{attacker} 가 {experience} 경험치 획득"


def f_ATTACKER_GAINED_A_LEVEL(attacker):
    return f"{attacker} 레벨이 상승했다!"


def f_ITEM_CANNOT_BE_TRADED_NOT_ENOUGH_PLACE_IN_RECEIVERS_INVENTORY(receiver):
    return f"아이템 거래 불가: {receiver} 의 인벤토리 부족"


def f_THIS_ITEM_CANNOT_BE_EQUIPPED_PLAYER_DOESNT_SATISFY_THE_REQUIREMENTS(
    selected_player,
):
    return f"아이템 착용 불가: {selected_player} 가 조건을 만족하지 않음"


# Constant sprites
STR_NEW_TURN = "새로운 턴 !"
STR_VICTORY = "승리 !"
STR_DEFEAT = "패배 !"
STR_MAIN_MISSION = "메인 미션"
STR_OPTIONAL_OBJECTIVES = "선택 목표"


# effect.py
def f_ENTITY_RECOVERED_NUMBER_HP(entity, recovered):
    return f"{entity} 가 {recovered} 체력 회복."


def f_ENTITY_IS_AT_FULL_HEALTH_AND_CANT_BE_HEALED(entity):
    return f"{entity} 의 체력이 최대이고 회복할 수 없습니다!"


def f_ENTITY_EARNED_NUMBER_XP(entity, power):
    return f"{entity} 가 {power} 경험치 획득"


def f_ENTITY_GAINED_A_LEVEL(entity):
    return f". {entity} 가 레벨업!"


def f_THE_SPEED_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} 의 속도가 {duration} 턴 동안 증가했다"


def f_THE_STRENGTH_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} 의 공격력이 {duration} 턴 동안 증가했다"


def f_THE_DEFENSE_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} 의 방어가 {duration} 턴 동안 증가했다"


def f_ENTITY_HAS_BEEN_STUNNED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} 가 {duration} 턴 동안 기절했다"


def f_RECOVER_NUMBER_HP(power):
    return f"체력 {power} 회복"


def f_EARN_NUMBER_XP(power):
    return f"{power} 경험치 획득"


TRANSLATIONS = {
    "items": {
        "key": "열쇠",
        "bones": "뼈",
        "topaz": "토파즈",
        "iron_ring": "철제 반지",
        "monster_meat": "몬스터 고기",
        "life_potion": "생명 물약",
        "speed_potion": "속도 물약",
        "rabbit_step_potion": "토끼 걸음 물약",
        "strength_potion": "힘의 물약",
        "vigor_potion": "활력 물약",
        "scroll_of_knowledge": "지식의 두루마리",
        "scroll_of_cerberus": "케르베로스의 두루마리",
        "chest_key": "상자 열쇠",
        "door_key": "문 열쇠",
        "green_book": "초록색 책",
        "poket_knife": "주머니 칼",
        "dagger": "단검",
        "club": "곤봉",
        "short_sword": "소검",
        "wooden_spear": "나무 창",
        "halberd": "미늘창",
        "pickaxe": "곡괭이",
        "wooden_bow": "나무 활",
        "basic_bow": "활",
        "wooden_staff": "나무 스태프",
        "necromancer_staff": "사령술사 스태프",
        "plumed_helmet": "깃털 장식 헬멧",
        "black_hood": "검은 두건",
        "helmet": "헬멧",
        "horned_helmet": "뿔 장식 헬멧",
        "gold_helmet": "금 헬멧",
        "chainmail": "사슬갑옷",
        "leather_armor": "가죽 갑옷",
        "scale_mail": "비늘 갑옷",
        "gold_armor": "금 갑옷",
        "spy_outfit": "스파이 옷",
        "barding_magenta": "마젠타 색 갑옷",
        "brown_boots": "갈색 신발",
        "black_boots": "검은색 신발",
        "gold_boots": "금색 신발",
        "wooden_shield": "나무 방패",
        "pocket_knife": "주머니 칼",
        "basic_spear": "창",
        "basic_halberd": "기본 미늘창",
    },
    "effects": {
        "defense_up": "방어력 상승",
        "strength_up": "공격력 상승",
        "speed_up": "속도 상승",
        "stun": "기절",
        "no_attack": "공격 불가",
    },
    "alterations": {
        "defense_up": "방어력 상승",
        "strength_up": "공격력 상승",
        "speed_up": "속도 상승",
        "stun": "기절",
        "no_attack": "공격 불가",
    },
    "races_and_classes": {
        # Races
        "human": " 인간",
        "elf": "엘프",
        "dwarf": "드워프",
        "centaur": "켄타우루스",
        "gnome": "노움",
        # Classes
        "warrior": "전사",
        "ranger": "궁수",
        "spy": "스파이",
    },
    "foe_keywords": {
        "undead": "언데드",
        "large": "대형",
        "cavalry": "기병",
        "mutant": "돌연변이",
        "fly": "비행",
        "none": "없음",
    },
    "entity_names": {
        "skeleton": "스켈레톤",
        "skeleton_cobra": "스켈레톤 뱀",
        "necrophage": "네크로페이지",
        "lich_boss": "리치 보스",
        "mutant_bee": "돌연변이 벌",
        "mutant_lizard": "돌연변이 도마뱀",
        "mutant_cultist": "돌연변이 광신도",
        "mutant_ant": "돌연변이 개미",
        "obstacle": "장애물",
        "shop": "상점",
        "house": "집",
        "chest": "상자",
        "healer": "제보바람H",
        "tavern": "술집",
        "door": "문",
        "altar": "제단",
        "armory": "무기점",
        "apothecary": "제보바람AP",
    },
    "attack_kinds": {
        "physical": "물리",
        "spiritual": "마법",
    },
}
