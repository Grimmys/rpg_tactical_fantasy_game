STR_GAME_TITLE = "En el nombre de los Cinco Gatos"

# Start scene
STR_NEW_GAME = "Juego nuevo"
STR_LOAD_GAME = "Cargar juego"
STR_OPTIONS = "Opciones"
STR_EXIT_GAME = "Salir del juego"

# Close button
STR_CLOSE = "Cerrar"

# Load game menu
STR_LOAD_GAME_MENU = "Cargar juego"


def f_SAVE_NUMBER(number: int):
    return f"Guardardado {number}"


# Options menu
STR_OPTIONS_MENU = "Opciones"
STR_LANGUAGE_ = "Idioma :"
STR_LANGUAGE = "Idioma"
STR_CHOOSE_LANGUAGE = "Elegir idioma"
STR_MOVE_SPEED_ = "Velocidad de movimiento :"
STR_SCREEN_MODE_ = "Modo de pantalla :"
STR_NORMAL = "Normal"
STR_FAST = "Rápido"
STR_SLOW = "Lento"
STR_WINDOW = "Ventana"
STR_FULL = "Pantalla completa"

# Save game menu
STR_SAVE_GAME_MENU = "Guardar juego"


# Level loading scene
def f_CHAPTER_NUMBER(number: int):
    return f"Capítulo {number}"


def f_LEVEL_NUMBER_AND_NAME(number: int, name: str):
    return f"Nivel {number}: {name}"


# Main menu
STR_MAIN_MENU = "Menú principal"
STR_SAVE = "Guardar"
STR_SUSPEND = "Suspender"
STR_START = "Iniciar"
STR_DIARY = "Diario"
STR_END_TURN = "Fin del turno"
STR_DEFAULT_DIARY_BODY_CONTENT = "No se ha registrado ningún evento aún"

# Reward menu
STR_REWARD_CONGRATULATIONS = "¡Felicidades! ¡El objetivo ha sido completado!"


def f_EARNED_GOLD(gold: int):
    return f"Ganó oro: {gold} (todos los personajes)"


def f_EARNED_ITEMS(item):
    return f"Objeto ganado: {item}"


# Player menu
STR_INVENTORY = "Inventario"
STR_EQUIPMENT = "Equipo"
STR_STATUS = "Estado"
STR_WAIT = "Esperar"
STR_VISIT = "Visitar"
STR_TRADE = "Comerciar"
STR_OPEN_CHEST = "Abrir cofre"
STR_PICK_LOCK = "Forzar la cerradura"
STR_OPEN_DOOR = "Abrir puerta"
STR_USE_PORTAL = "Usar portal"
STR_DRINK = "Beber"
STR_TALK = "Hablar"
STR_TAKE = "Tomar"
STR_ATTACK = "Atacar"
STR_SELECT_AN_ACTION = "Seleccionar una acción"

# Inventory menu
STR_SHOPPING_SELLING = "Tienda - Venta"


def f_UR_GOLD(gold):
    return f"Tu oro: {gold}"


def f_SHOP_GOLD(shop_balance):
    return f"Oro del comerciante: {shop_balance}"


# Trade menu
STR_50G_TO_RIGHT = "50G ->"
STR_200G_TO_RIGHT = "200G ->"
STR_ALL_TO_RIGHT = "Todo ->"
STR_50G_TO_LEFT = "<- 50G"
STR_200G_TO_LEFT = "<- 200G"
STR_ALL_TO_LEFT = "<- Todo"


def f_GOLD_AT_END(player, gold):
    return f"Tu oro: {gold} ({player})"


# Status menu
STR_NAME_ = "Nombre :"
STR_SKILLS = "HABILIDADES"
STR_CLASS_ = "Clase :"
STR_RACE_ = "Raza :"
STR_LEVEL_ = "Nivel :"
STR_XP_ = "  XP :"
STR_STATS = "ESTADÍSTICAS"
STR_HP_ = "HP :"
STR_MOVE_ = "MOVIMIENTO :"
STR_CONSTITUTION_ = "CONSTITUCIÓN :"
STR_ATTACK_ = "ATAQUE :"
STR_DEFENSE_ = "DEFENSA :"
STR_MAGICAL_RES_ = "RESISTENCIA MÁGICA :"
STR_ALTERATIONS = "ALTERACIONES"
STR_NONE = "Ninguno"


def f_DIV(partial, maximum):
    return f"{partial} / {maximum}"


# Item shop menu
STR_BUY = "Comprar"
STR_INFO = "Información"

# Item buy menu
STR_SHOP_BUYING = "Tienda - Comprando"


def f_PRICE_NUMBER(price):
    return f"Precio: {price}"


def f_QUANTITY_NUMBER(quantity):
    return f"Cantidad: {quantity}"


# Item sell menu
STR_SELL = "Vender"

# Item menu
STR_THROW = "Tirar"
STR_USE = "Usar"
STR_UNEQUIP = "Desequipar"
STR_EQUIP = "Equipar"


# Item description stat
def f_STAT_NAME_(stat_name):
    return f"{stat_name}: "


# Item description menu
STR_RESERVED_TO = "RESERVADO A"
STR_POWER = "POTENCIA"
STR_DEFENSE = "DEFENSA"
STR_MAGICAL_RES = "RESISTENCIA MÁGICA"
STR_TYPE_OF_DAMAGE = "TIPO DE DAÑO"
STR_REACH = "ALCANCE"
STR_EFFECT = "EFECTO"
STR_STRONG_AGAINST = "FUERTE CONTRA"
STR_PARRY_RATE = "TASA DE PARADA"
STR_DURABILITY = "DURABILIDAD"
STR_WEIGHT = "PESO"

# Status entity menu
STR_LOOT = "BOTÍN"
STR_TYPE_ = "TIPO :"
STR_REACH_ = "ALCANCE :"


def f_LEVEL_NUMBER_ENTITY(level):
    return f"NIVEL : {level}"


# Sidebar
STR_FOE = "ENEMIGO"
STR_PLAYER = "JUGADOR"
STR_ALLY = "ALIADO"
STR_UNLIVING_ENTITY = "ENTIDAD SIN VIDA"
STR_NAME_SIDEBAR_ = "NOMBRE : "
STR_ALTERATIONS_ = "ALTERACIONES : "


def f_TURN_NUMBER_SIDEBAR(number_turns):
    return f"TURNO {number_turns}"


def f_LEVEL_NUMBER_SIDEBAR(level_id):
    return f"NIVEL {level_id}"


# Chest menu
STR_CHEST = "Cofre"


# Alternation info menu
def f_TURNS_LEFT_NUMBER(turns_left):
    return f"Turnos restantes: {turns_left}"


# Ask save menu
STR_SAVE_THE_GAME_ = "¿Guardar el juego?"
STR_YES = "Sí"
STR_NO = "No"


# src.game_entities.building
def f_YOU_RECEIVED_NUMBER_GOLD(gold):
    return f"[Has recibido {gold} piezas de oro]"


def f_YOU_RECEIVED_ITEM(item):
    return f"[Has recibido {item}]"


# Messages
STR_ERROR_NOT_ENOUGH_TILES_TO_SET_PLAYERS = (
    "Error ! No hay suficientes tiles libres para colocar jugadores..."
)
STR_GAME_HAS_BEEN_SAVED = "El juego ha sido guardado"
STR_ITEM_HAS_BEEN_ADDED_TO_UR_INVENTORY = "El objeto ha sido añadido a tu inventario"
STR_YOU_FOUND_IN_THE_CHEST = "Has encontrado en el cofre"
STR_DOOR_HAS_BEEN_OPENED = "La puerta ha sido abierta"
STR_YOU_HAVE_NO_FREE_SPACE_IN_YOUR_INVENTORY = (
    "No tienes espacio libre en tu inventario"
)
STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO = "Comenzaste a forzar, un turno más para ir"
STR_THERE_IS_NO_FREE_SQUARE_AROUND_THE_OTHER_PORTAL = (
    "No hay un cuadrado libre alrededor del otro portal"
)
STR_BUT_THERE_IS_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_TAKE_IT = (
    "Pero no hay suficiente espacio en el inventario para tomarlo!"
)
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_DOOR = "No tienes llave para abrir una puerta"
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_CHEST = "No tienes llave para abrir un cofre"
STR_ITEM_HAS_BEEN_TRADED = "El objeto ha sido intercambiado"
STR_ITEM_HAS_BEEN_THROWN_AWAY = "El objeto ha sido tirado"
STR_THE_ITEM_CANNOT_BE_UNEQUIPPED_NOT_ENOUGH_SPACE_IN_UR_INVENTORY = (
    "El objeto no puede ser desequipado: No hay suficiente espacio en tu inventario."
)
STR_THE_ITEM_HAS_BEEN_UNEQUIPPED = "El objeto ha sido desequipado"
STR_THE_ITEM_HAS_BEEN_EQUIPPED = "El objeto ha sido equipado"
STR_PREVIOUS_EQUIPPED_ITEM_HAS_BEEN_ADDED_TO_YOUR_INVENTORY = (
    "El objeto previamente equipado ha sido añadido a tu inventario"
)
STR_THE_ITEM_HAS_BEEN_BOUGHT = "El objeto ha sido comprado."
STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM = (
    "No hay suficiente espacio en el inventario para comprar este objeto."
)
STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM = "No hay suficiente oro para comprar este objeto."
STR_THE_ITEM_HAS_BEEN_SOLD = "El objeto ha sido vendido."
STR_THIS_ITEM_CANT_BE_SOLD = "¡El vendedor no tiene fondos para comprarte!"
STR_THIS_HOUSE_SEEMS_CLOSED = "Esta casa parece estar cerrada..."


def f_ATTACKER_ATTACKED_TARGET_BUT_PARRIED(attacker, target):
    return f"{attacker} atacó a {target}... Pero {target} paró el ataque."


def f_ATTACKER_DEALT_DAMAGE_TO_TARGET(attacker, target, damage):
    return f"{attacker} infligió {damage} de daño a {target}"


def f_TARGET_DIED(target):
    return f"{target} ha muerto!"


def f_TARGET_DROPPED_ITEM(target, item):
    return f"{target} ha soltado {item}"


def f_TARGET_HAS_NOW_NUMBER_HP(target, hp):
    return f"{target} ahora tiene {hp} HP"


def f_ATTACKER_EARNED_NUMBER_XP(attacker, experience):
    return f"{attacker} ha ganado {experience} XP"


def f_ATTACKER_GAINED_A_LEVEL(attacker):
    return f"{attacker} ha subido de nivel!"


def f_ITEM_CANNOT_BE_TRADED_NOT_ENOUGH_PLACE_IN_RECEIVERS_INVENTORY(receiver):
    return f"El objeto no puede ser intercambiado: no hay suficiente espacio en el inventario de {receiver}"


def f_THIS_ITEM_CANNOT_BE_EQUIPPED_PLAYER_DOESNT_SATISFY_THE_REQUIREMENTS(
    selected_player,
):
    return f"El objeto no puede ser equipado: {selected_player} no cumple con los requisitos"


# Constant sprites
STR_NEW_TURN = "¡NUEVO TURNO!"
STR_VICTORY = "¡VICTORIA!"
STR_DEFEAT = "¡DERROTA!"
STR_MAIN_MISSION = "MISIÓN PRINCIPAL"
STR_OPTIONAL_OBJECTIVES = "OBJETIVOS OPCIONALES"


# effect.py
def f_ENTITY_RECOVERED_NUMBER_HP(entity, recovered):
    return f"{entity} ha recuperado {recovered} HP."


def f_ENTITY_IS_AT_FULL_HEALTH_AND_CANT_BE_HEALED(entity):
    return f"{entity} está a plena salud y no puede ser curado."


def f_ENTITY_EARNED_NUMBER_XP(entity, power):
    return f"{entity} ha ganado {power} XP"


def f_ENTITY_GAINED_A_LEVEL(entity):
    return f"{entity} ha subido de nivel!"


def f_THE_SPEED_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"La velocidad de {entity} ha sido aumentada durante {duration} turnos."


def f_THE_STRENGTH_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"La fuerza de {entity} ha sido aumentada durante {duration} turnos."


def f_THE_DEFENSE_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"La defensa de {entity} ha sido aumentada durante {duration} turnos."


def f_ENTITY_HAS_BEEN_STUNNED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} ha sido aturdido durante {duration} turnos."


def f_RECOVER_NUMBER_HP(power):
    return f"Recuperar {power} HP"


def f_EARN_NUMBER_XP(power):
    return f"Ganar {power} XP"


TRANSLATIONS = {
    "items": {
        "key": "Llave",
        "bones": "Huesos",
        "topaz": "Topacio",
        "iron_ring": "Anillo de Hierro",
        "monster_meat": "Carne de Monstruo",
        "life_potion": "Poción de Vida",
        "speed_potion": "Poción de Velocidad",
        "rabbit_step_potion": "Poción de Paso de Conejo",
        "strength_potion": "Poción de Fuerza",
        "vigor_potion": "Poción de Vigor",
        "scroll_of_knowledge": "Voluta de Conocimiento",
        "scroll_of_cerberus": "Voluta de Cerberus",
        "chest_key": "Llave de Cofre",
        "door_key": "Llave de Puerta",
        "green_book": "Libro Verde",
        "poket_knife": "Cuchillo de Bolsillo",
        "dagger": "Daga",
        "club": "Clava",
        "short_sword": "Espada Corta",
        "wooden_spear": "Pica de Madera",
        "halberd": "Hacha de Guerra",
        "pickaxe": "Pico",
        "wooden_bow": "Arco de Madera",
        "basic_bow": "Arco Básico",
        "wooden_staff": "Bastón de Madera",
        "necromancer_staff": "Bastón de Nigromante",
        "plumed_helmet": "Casco Plumado",
        "black_hood": "Capucha Negra",
        "helmet": "Casco",
        "horned_helmet": "Casco Cornudo",
        "gold_helmet": "Casco de Oro",
        "chainmail": "Cota de Malla",
        "leather_armor": "Armadura de Cuero",
        "scale_mail": "Armadura de Escamas",
        "gold_armor": "Armadura de Oro",
        "spy_outfit": "Disfraz de Espía",
        "barding_magenta": "Barding Magenta",
        "brown_boots": "Botas Marrones",
        "black_boots": "Botas Negras",
        "gold_boots": "Botas de Oro",
        "wooden_shield": "Escudo de Madera",
        "pocket_knife": "Cuchillo de Bolsillo",
        "basic_spear": "Pica Básica",
        "basic_halberd": "Hacha de Guerra Básica",
    },
    "effects": {
        "defense_up": "Defensa aumentada",
        "strength_up": "Fuerza aumentada",
        "speed_up": "Velocidad aumentada",
        "stun": "Aturdido",
        "no_attack": "Sin ataque",
    },
    "alterations": {
        "defense_up": "Defensa aumentada",
        "strength_up": "Fuerza aumentada",
        "speed_up": "Velocidad aumentada",
        "stun": "Aturdido",
        "no_attack": "Sin ataque",
    },
    "races_and_classes": {
        # Races
        "human": "Humano",
        "elf": "Elfo",
        "dwarf": "Enano",
        "centaur": "Centauro",
        "gnome": "Gnomo",
        # Classes
        "warrior": "Guerrero",
        "ranger": "Guardabosques",
        "spy": "Espía",
    },
    "foe_keywords": {
        "undead": "No Muerto",
        "large": "Grande",
        "cavalry": "Caballería",
        "mutant": "Mutante",
        "fly": "Volador",
        "none": "Ninguno",
    },
    "entity_names": {
        "skeleton": "Esqueleto",
        "skeleton_cobra": "Esqueleto Cobra",
        "necrophage": "Necrofago",
        "lich_boss": "Jefe Lich",
        "mutant_bee": "Abeja Mutante",
        "mutant_lizard": "Lagarto Mutante",
        "mutant_cultist": "Cultista Mutante",
        "mutant_ant": "Hormiga Mutante",
        "obstacle": "Obstáculo",
        "shop": "Tienda",
        "house": "Casa",
        "chest": "Cofre",
        "healer": "Sanador",
        "tavern": "Taberna",
        "door": "Puerta",
        "altar": "Altar",
        "armory": "Armería",
        "apothecary": "Boticario",
    },
    "attack_kinds": {
        "physical": "Físico",
        "spiritual": "Espiritual",
    },
}
