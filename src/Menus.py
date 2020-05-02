from enum import Enum, auto


#  > Generic interactions
class GenericActions(Enum):
    #    - To close any menu
    CLOSE = -1


# > Start menu
class StartMenu(Enum):
    #   - Launch new game
    NEW_GAME = auto()
    #   - Load game
    LOAD_GAME = auto()
    #   - Access to options screen
    OPTIONS = auto()
    #   - Exit game
    EXIT = auto()


# > Options menu
class OptionsMenu(Enum):
    #   - Modify movement speed
    CHANGE_MOVE_SPEED = auto()


# > Main menu options
class MainMenu(Enum):
    #   - Start game
    START = auto()
    #   - Save game
    SAVE = auto()
    #   - End current turn
    END_TURN = auto()
    #   - Go back to start screen
    SUSPEND = auto()


# > Main character menu
class CharacterMenu(Enum):
    #   - Access to inventory
    INV = auto()
    #   - Access to equipment
    EQUIPMENT = auto()
    #   - Access to status screen
    STATUS = auto()
    #   - End character's turn
    WAIT = auto()
    #   - Attack an opponent
    ATTACK = auto()
    #   - Open a chest
    OPEN_CHEST = auto()
    #   - Use
    USE_PORTAL = auto()
    #   - Drink in fountain
    DRINK = auto()
    #   - Visit a building
    VISIT = auto()
    #   - Talk to an ally or neutral character
    TALK = auto()
    #   - Valid mission position
    TAKE = auto()
    #   - Trade with other playable character
    TRADE = auto()


# > Inventory menu
class InventoryMenu(Enum):
    #   - Interact with item
    INTERAC_ITEM = auto()


# > Item menu
class ItemMenu(Enum):
    #   - Use item
    USE_ITEM = auto()
    #   - Get infos about item
    INFO_ITEM = auto()
    #   - Throw item
    THROW_ITEM = auto()
    #   - Equip item
    EQUIP_ITEM = auto()
    #   - Unequip item
    UNEQUIP_ITEM = auto()
    #   - Buy item
    BUY_ITEM = auto()
    #   - Sell item
    SELL_ITEM = auto()
    #   - Trade item
    TRADE_ITEM = auto()


# > Status menu
class StatusMenu(Enum):
    #   - Get infos about alteration
    INFO_ALTERATION = auto()


# > Equipment menu
class EquipmentMenu(Enum):
    #   - Interact with equipment
    INTERAC_EQUIPMENT = auto()


# > Trade menu
class TradeMenu(Enum):
    #   - Interact with item
    INTERAC_ITEM = auto()


# > Shop menu
class ShopMenu(Enum):
    #   - Accessing buy menu
    BUY = auto()
    #   - Accessing sell menu
    SELL = auto()


# > Buy menu
class BuyMenu(Enum):
    #   - Interact with item
    INTERAC_BUY = auto()


# > Sell menu
class SellMenu(Enum):
    #   - Interact with item
    INTERAC_SELL = auto()