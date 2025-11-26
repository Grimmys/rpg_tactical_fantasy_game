STR_GAME_TITLE = "Au nom des Cinq Chats"

# Start scene
STR_NEW_GAME = "Nouvelle partie"
STR_LOAD_GAME = "Charger une partie"
STR_OPTIONS = "Options"
STR_EXIT_GAME = "Quitter le jeu"

# Close button
STR_CLOSE = "Fermer"
# Load game menu
STR_LOAD_GAME_MENU = "Charger une partie"


def f_SAVE_NUMBER(number: int):
    return f"Sauvegarde {number}"

# Options menu
STR_OPTIONS_MENU = "Options"
STR_LANGUAGE_ = "Langue :"
STR_LANGUAGE = "Langue"
STR_CHOOSE_LANGUAGE = "Choisir la langue"
STR_MOVE_SPEED_ = "Vitesse de déplacement :"
STR_SCREEN_MODE_ = "Mode d'écran :"
STR_NORMAL = "Normal"
STR_FAST = "Rapide"
STR_SLOW = "Lent"
STR_WINDOW = "Fenêtré"
STR_FULL = "Plein écran"

# Save game menu
STR_SAVE_GAME_MENU = "Enregistrer le jeu"

# Level loading scene
def f_CHAPTER_NUMBER(number: int):
    return f"Chapitre {number}"

def f_LEVEL_NUMBER_AND_NAME(number: int, name: str):
    return f"Niveau {number} : {name}"

# Main menu
STR_MAIN_MENU = "Menu principal"
STR_SAVE = "Sauvegarder"
STR_SUSPEND = "Suspendre"
STR_START = "Démarrer"
STR_DIARY = "Journal"
STR_END_TURN = "Fin du tour"
STR_DEFAULT_DIARY_BODY_CONTENT = "Aucun événement enregistré pour le moment"
# Reward menu
STR_REWARD_CONGRATULATIONS = "Félicitations ! L'objectif a été atteint !"


def f_EARNED_GOLD(gold: int):
    return f"Or gagné : {gold} (tous les personnages)"

def f_EARNED_ITEMS(item):
    return f"Objet gagné : {item}"

# Player menu
STR_INVENTORY = "Inventaire"
STR_EQUIPMENT = "Équipement"
STR_STATUS = "Statut"
STR_WAIT = "Attendre"
STR_VISIT = "Visiter"
STR_TRADE = "Échanger"
STR_OPEN_CHEST = "Ouvrir le coffre"
STR_PICK_LOCK = "Forcer la serrure"
STR_OPEN_DOOR = "Ouvrir la porte"
STR_USE_PORTAL = "Utiliser le portail"
STR_DRINK = "Boire"
STR_TALK = "Parler"
STR_TAKE = "Saisir"
STR_ATTACK = "Attaquer"
STR_SELECT_AN_ACTION = "Sélectionner une action"

# Inventory menu
STR_SHOPPING_SELLING = "Magasin - Vente"


def f_UR_GOLD(gold):
    return f"Votre or : {gold}"

def f_SHOP_GOLD(shop_balance):
    return f"Or du commerçant : {shop_balance}"

# Trade menu
STR_50G_TO_RIGHT = "50G ->"
STR_200G_TO_RIGHT = "200G ->"
STR_ALL_TO_RIGHT = "Tout ->"
STR_50G_TO_LEFT = "<- 50G"
STR_200G_TO_LEFT = "<- 200G"
STR_ALL_TO_LEFT = "<- Tout"


def f_GOLD_AT_END(player, gold):
    return f"Ton or : {gold} ({player})"

# Status menu
STR_NAME_ = "Nom :"
STR_SKILLS = "COMPÉTENCES"
STR_CLASS_ = "Classe :"
STR_RACE_ = "Race :"
STR_LEVEL_ = "Niveau :"
STR_XP_ = "  XP :"
STR_STATS = "STATISTIQUES"
STR_HP_ = "PV :"
STR_MOVE_ = "DÉPLACEMENT :"
STR_CONSTITUTION_ = "CONSTITUTION :"
STR_ATTACK_ = "ATTAQUE :"
STR_DEFENSE_ = "DÉFENSE :"
STR_MAGICAL_RES_ = "RÉSISTANCE MAGIQUE :"
STR_ALTERATIONS = "ALTÉRATIONS"
STR_NONE = "Aucun(e)"


def f_DIV(partial, maximum):
    return f"{partial} / {maximum}"


# Item shop menu
STR_BUY = "Acheter"
STR_INFO = "Informations"

# Item buy menu
STR_SHOP_BUYING = "Magasin - Achat"

def f_PRICE_NUMBER(price):
    return f"Prix : {price}"

def f_QUANTITY_NUMBER(quantity):
    return f"Quantité : {quantity}"

# Item sell menu
STR_SELL = "Vendre"

# Item menu
STR_THROW = "Jeter"
STR_USE = "Utiliser"
STR_UNEQUIP = "Déséquiper"
STR_EQUIP = "Équiper"


# Item description stat
def f_STAT_NAME_(stat_name):
    return f"{stat_name}: "


# Item description menu
STR_RESERVED_TO = "RÉSERVÉ À"
STR_POWER = "PUISSANCE"
STR_DEFENSE = "DÉFENSE"
STR_MAGICAL_RES = "RÉSISTANCE MAGIQUE"
STR_TYPE_OF_DAMAGE = "TYPE DE DÉGÂTS"
STR_REACH = "PORTÉE"
STR_EFFECT = "EFFET"
STR_STRONG_AGAINST = "FORT CONTRE"
STR_PARRY_RATE = "TAUX DE PARADE"
STR_DURABILITY = "DURABILITÉ"
STR_WEIGHT = "POIDS"

# Status entity menu
STR_LOOT = "BUTIN"
STR_TYPE_ = "TYPE :"
STR_REACH_ = "PORTÉE :"


def f_LEVEL_NUMBER_ENTITY(level):
    return f"NIVEAU : {level}"

# Sidebar
STR_FOE = "ENNEMI"
STR_PLAYER = "JOUEUR"
STR_ALLY = "ALLIÉ"
STR_UNLIVING_ENTITY = "ENTITÉ SANS VIE"
STR_NAME_SIDEBAR_ = "NOM : "
STR_ALTERATIONS_ = "ALTÉRATIONS : "


def f_TURN_NUMBER_SIDEBAR(number_turns):
    return f"TOUR {number_turns}"


def f_LEVEL_NUMBER_SIDEBAR(level_id):
    return f"NIVEAU {level_id}"

# Chest menu
STR_CHEST = "Coffre"

# Alternation info menu
def f_TURNS_LEFT_NUMBER(turns_left):
    return f"Tours restants : {turns_left}"

# Ask save menu
STR_SAVE_THE_GAME_ = "Sauvegarder la partie ?"
STR_YES = "Oui"
STR_NO = "Non"


# src.game_entities.building
def f_YOU_RECEIVED_NUMBER_GOLD(gold):
    return f"[Vous avez reçu {gold} pièces d'or]"


def f_YOU_RECEIVED_ITEM(item):
    return f"[Vous avez reçu {item}]"

# Messages
STR_ERROR_NOT_ENOUGH_TILES_TO_SET_PLAYERS = (
    "Erreur ! Il n'y a pas assez de tuiles libres pour placer les joueurs..."
)
STR_GAME_HAS_BEEN_SAVED = "Le jeu a été enregistré"
STR_ITEM_HAS_BEEN_ADDED_TO_UR_INVENTORY = "L'objet a été ajouté à ton inventaire"
STR_YOU_FOUND_IN_THE_CHEST = "Vous avez trouvé dans le coffre"
STR_DOOR_HAS_BEEN_OPENED = "La porte a été ouverte"
STR_YOU_HAVE_NO_FREE_SPACE_IN_YOUR_INVENTORY = (
    "Vous n'avez pas d'espace libre dans votre inventaire"
)
STR_STARTED_PICKING_ONE_MORE_TURN_TO_GO = "Vous avez commencé à forcer, un tour de plus pour y arriver"
STR_THERE_IS_NO_FREE_SQUARE_AROUND_THE_OTHER_PORTAL = (
    "Il n'y a pas de case libre autour de l'autre portail"
)
STR_BUT_THERE_IS_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_TAKE_IT = (
    "Mais il n'y a pas assez d'espace dans l'inventaire pour le prendre !"
)
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_DOOR = "Vous n'avez pas de clé pour ouvrir une porte"
STR_YOU_HAVE_NO_KEY_TO_OPEN_A_CHEST = "Vous n'avez pas de clé pour ouvrir un coffre"
STR_ITEM_HAS_BEEN_TRADED = "L'objet a été échangé"
STR_ITEM_HAS_BEEN_THROWN_AWAY = "L'objet a été jeté"
STR_THE_ITEM_CANNOT_BE_UNEQUIPPED_NOT_ENOUGH_SPACE_IN_UR_INVENTORY = (
    "L'objet ne peut pas être déséquipé : il n'y a pas assez d'espace dans votre inventaire."
)
STR_THE_ITEM_HAS_BEEN_UNEQUIPPED = "L'objet a été déséquipé"
STR_THE_ITEM_HAS_BEEN_EQUIPPED = "L'objet a été équipé"
STR_PREVIOUS_EQUIPPED_ITEM_HAS_BEEN_ADDED_TO_YOUR_INVENTORY = (
    "L'objet précédemment équipé a été ajouté à votre inventaire"
)
STR_THE_ITEM_HAS_BEEN_BOUGHT = "L'objet a été acheté"
STR_NOT_ENOUGH_SPACE_IN_INVENTORY_TO_BUY_THIS_ITEM = (
    "Il n'y a pas assez d'espace dans l'inventaire pour acheter cet objet."
)
STR_NOT_ENOUGH_GOLD_TO_BY_THIS_ITEM = "Il n'y a pas assez d'or pour acheter cet objet."
STR_THE_ITEM_HAS_BEEN_SOLD = "L'objet a été vendu."
STR_THIS_ITEM_CANT_BE_SOLD = "Le vendeur n'a pas les fonds pour acheter cet objet !"
STR_THIS_HOUSE_SEEMS_CLOSED = "Cette maison semble être verrouillée..."


def f_ATTACKER_ATTACKED_TARGET_BUT_PARRIED(attacker, target):
    return f"{attacker} a attaqué {target}... Mais {target} a paré l'attaque."


def f_ATTACKER_DEALT_DAMAGE_TO_TARGET(attacker, target, damage):
    return f"{attacker} a infligé {damage} de dégâts à {target}"

def f_TARGET_DIED(target):
    return f"{target} est mort !"

def f_TARGET_DROPPED_ITEM(target, item):
    return f"{target} a laissé tomber {item}"

def f_TARGET_HAS_NOW_NUMBER_HP(target, hp):
    return f"{target} a maintenant {hp} PV"

def f_ATTACKER_EARNED_NUMBER_XP(attacker, experience):
    return f"{attacker} a gagné {experience} XP"

def f_ATTACKER_GAINED_A_LEVEL(attacker):
    return f"{attacker} a monté de niveau !"

def f_ITEM_CANNOT_BE_TRADED_NOT_ENOUGH_PLACE_IN_RECEIVERS_INVENTORY(receiver):
    return f"L'objet ne peut pas être échangé : il n'y a pas assez d'espace dans l'inventaire de {receiver}."

def f_THIS_ITEM_CANNOT_BE_EQUIPPED_PLAYER_DOESNT_SATISFY_THE_REQUIREMENTS(
    selected_player,
):
    return f"L'objet ne peut pas être équipé : {selected_player} ne satisfait pas aux exigences."


# Constant sprites
STR_NEW_TURN = "NOUVEAU TOUR !"
STR_VICTORY = "VICTOIRE !"
STR_DEFEAT = "DÉFAITE !"
STR_MAIN_MISSION = "MISSION PRINCIPALE"
STR_OPTIONAL_OBJECTIVES = "OBJECTIFS OPTIONNELS"

# effect.py
def f_ENTITY_RECOVERED_NUMBER_HP(entity, recovered):
    return f"{entity} a récupéré {recovered} PV."


def f_ENTITY_IS_AT_FULL_HEALTH_AND_CANT_BE_HEALED(entity):
    return f"{entity} est en pleine santé et ne peut pas être soigné."

def f_ENTITY_EARNED_NUMBER_XP(entity, power):
    return f"{entity} a gagné {power} XP"

def f_ENTITY_GAINED_A_LEVEL(entity):
    return f"{entity} a monté de niveau !"

def f_THE_SPEED_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"La vitesse de {entity} a été augmentée pendant {duration} tours."

def f_THE_STRENGTH_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"La force de {entity} a été augmentée pendant {duration} tours."

def f_THE_DEFENSE_OF_ENTITY_HAS_BEEN_INCREASED_FOR_NUMBER_TURNS(entity, duration):
    return f"La défense de {entity} a été augmentée pendant {duration} tours."

def f_ENTITY_HAS_BEEN_STUNNED_FOR_NUMBER_TURNS(entity, duration):
    return f"{entity} a été étourdi pendant {duration} tours."

def f_RECOVER_NUMBER_HP(power):
    return f"Soigne {power} PV"

def f_EARN_NUMBER_XP(power):
    return f"Donne {power} XP"

TRANSLATIONS = {
    "items": {
        "key": "Clé",
        "bones": "Os",
        "topaz": "Topaze",
        "iron_ring": "Anneau de Fer",
        "monster_meat": "Viande de Monstre",
        "life_potion": "Potion de Vie",
        "speed_potion": "Potion de Vitesse",
        "rabbit_step_potion": "Potion Allure de Lapin",
        "strength_potion": "Potion de Force",
        "vigor_potion": "Potion de Vigueur",
        "scroll_of_knowledge": "Parchemin de Connaissance",
        "scroll_of_cerberus": "Parchemin de Cerbère",
        "chest_key": "Clé de Coffre",
        "door_key": "Clé de Porte",
        "green_book": "Livre Vert",
        "poket_knife": "Couteau de Poche",
        "dagger": "Dague",
        "club": "Massue",
        "short_sword": "Épée Courte",
        "wooden_spear": "Lance en Bois",
        "halberd": "Hallebarde",
        "pickaxe": "Pioche",
        "wooden_bow": "Arc en Bois",
        "basic_bow": "Arc Simple",
        "wooden_staff": "Bâton en Bois",
        "necromancer_staff": "Bâton de Nécromancien",
        "plumed_helmet": "Casque Plumet",
        "black_hood": "Capuche Noire",
        "helmet": "Casque",
        "horned_helmet": "Casque Cornu",
        "gold_helmet": "Casque d'Or",
        "chainmail": "Cotte de Mailles",
        "leather_armor": "Armure en Cuir",
        "scale_mail": "Armure d'Écailles",
        "gold_armor": "Armure d'Or",
        "spy_outfit": "Tenue d'Espion",
        "barding_magenta": "Bardure Magenta",
        "brown_boots": "Bottes Marron",
        "black_boots": "Bottes Noires",
        "gold_boots": "Bottes d'Or",
        "wooden_shield": "Bouclier en Bois",
        "pocket_knife": "Couteau de Poche",
        "basic_spear": "Lance Basique",
        "basic_halberd": "Hallebarde Basique",
    },
    "effects": {
        "defense_up": "Défense augmentée",
        "strength_up": "Force augmentée",
        "speed_up": "Vitesse augmentée",
        "stun": "Étourdi",
        "no_attack": "Pas d'attaque",
    },
    "alterations": {
        "defense_up": "Défense augmentée",
        "strength_up": "Force augmentée",
        "speed_up": "Vitesse augmentée",
        "stun": "Étourdi",
        "no_attack": "Pas d'attaque",
    },
    "races_and_classes": {
        # Races
        "human": "Humain",
        "elf": "Elfe",
        "dwarf": "Nain",
        "centaur": "Centaure",
        "gnome": "Gnome",
        # Classes
        "warrior": "Guerrier",
        "ranger": "Rôdeur",
        "spy": "Espion",
    },
    "foe_keywords": {
        "undead": "Mort-vivant",
        "large": "Massif",
        "cavalry": "Cavalerie",
        "mutant": "Mutant",
        "fly": "Volant",
        "none": "Aucun",
    },
    "entity_names": {
        "skeleton": "Squelette",
        "skeleton_cobra": "Cobra Squelette",
        "necrophage": "Nécrophage",
        "lich_boss": "Boss Lich",
        "mutant_bee": "Abeille Mutante",
        "mutant_lizard": "Lézard Mutant",
        "mutant_cultist": "Cultiste Mutant",
        "mutant_ant": "Fourmi Mutante",
        "obstacle": "Obstacle",
        "shop": "Boutique",
        "house": "Maison",
        "chest": "Coffre",
        "healer": "Soigneur",
        "tavern": "Taverne",
        "door": "Porte",
        "altar": "Autel",
        "armory": "Armurerie",
        "apothecary": "Apothicaire",
    },
    "attack_kinds": {
        "physical": "Physique",
        "spiritual": "Spirituel",
    },
}
