import unittest

from src.constants import TILE_SIZE
from src.game_entities.destroyable import DamageKind
from src.game_entities.foe import Keyword
from src.game_entities.weapon import Weapon
from tests.random_data_library import (random_foe_entity, random_player_entity,
                                       random_weapon)
from tests.tools import minimal_setup_for_game


class TestWeapon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_weapon(self):
        name = "short_sword"
        sprite = "imgs/dungeon_crawl/item/weapon/short_sword_2_old.png"
        description = "A basic little sword, but one that can already prove very useful"
        price = 500
        equipped_sprite = ["imgs/dungeon_crawl/player/hand_right/short_sword.png"]
        durability = 40
        reach = [1]
        power = 4
        kind = "PHYSICAL"
        weight = 2
        restrictions = []
        possible_effects = []
        strong_against = [Keyword.LARGE]
        sword = Weapon(
            name,
            sprite,
            description,
            price,
            equipped_sprite,
            power,
            kind,
            weight,
            durability,
            reach,
            restrictions,
            possible_effects,
            strong_against,
        )
        self.assertEqual(name, sword.name)
        self.assertEqual(description, sword.description)
        self.assertEqual("Short Sword", str(sword))
        self.assertEqual(price, sword.price)
        self.assertEqual(price // 2, sword.resell_price)
        self.assertEqual(durability, sword.durability_max)
        self.assertEqual(durability, sword.durability)
        self.assertEqual(reach, sword.reach)
        self.assertEqual(power, sword.attack)
        self.assertEqual(DamageKind[kind], sword.attack_kind)
        self.assertEqual(weight, sword.weight)
        self.assertEqual(restrictions, sword.restrictions)
        self.assertEqual(possible_effects, sword.effects)
        self.assertEqual(strong_against, sword.strong_against)

    def test_decreasing_durability(self):
        durability = 40
        weapon = random_weapon(durability=durability)
        self.assertEqual(durability, weapon.durability)
        self.assertEqual(durability, weapon.durability_max)

        for i in range(durability):
            current_durability = weapon.durability
            weapon.used()
            self.assertEqual(current_durability - 1, weapon.durability)

        self.assertEqual(0, weapon.durability)

    def test_resell_price_following_durability(self):
        price = 500
        durability = 40
        weapon = random_weapon(price=price, durability=durability)
        self.assertEqual(price // 2, weapon.resell_price)
        self.assertEqual(durability, weapon.durability)
        self.assertEqual(durability, weapon.durability_max)

        for i in range(durability):
            before_use_price = weapon.resell_price
            weapon.used()
            self.assertTrue(weapon.resell_price < before_use_price)

        self.assertEqual(0, weapon.resell_price)

    def test_hit_power(self):
        power = 3
        strong_against = []
        weapon = random_weapon(atk=power, strong_against=strong_against)
        self.assertEqual(power, weapon.hit(random_player_entity(), random_foe_entity()))

    def test_stronger_against_specific_entity_kind(self):
        power = 5
        strong_against = [Keyword.LARGE]
        weapon = random_weapon(atk=power, strong_against=strong_against)

        normal_foe = random_foe_entity(keywords=[])
        self.assertEqual(power, weapon.hit(random_player_entity(), normal_foe))

        vulnerable_foe = random_foe_entity(keywords=[Keyword.LARGE])
        self.assertEqual(power * 2, weapon.hit(random_player_entity(), vulnerable_foe))

    def test_stronger_against_multiple_entity_kinds(self):
        power = 4
        strong_against = [Keyword.LARGE, Keyword.CAVALRY]
        weapon = random_weapon(atk=power, strong_against=strong_against)

        non_vulnerable_foe = random_foe_entity(keywords=[Keyword.SMALL])
        self.assertEqual(power, weapon.hit(random_player_entity(), non_vulnerable_foe))

        vulnerable_foe = random_foe_entity(keywords=[Keyword.LARGE])
        self.assertEqual(power * 2, weapon.hit(random_player_entity(), vulnerable_foe))

        super_vulnerable_foe = random_foe_entity(
            keywords=[Keyword.CAVALRY, Keyword.LARGE]
        )
        self.assertEqual(
            power * 3, weapon.hit(random_player_entity(), super_vulnerable_foe)
        )

    def test_charge_bonus(self):
        power = 4
        spear = random_weapon(atk=power, attack_kind="PHYSICAL", charge=True)
        player = random_player_entity()
        player.strength = 5
        attacked_ent = random_foe_entity(
            min_hp=1000, max_hp=1000, max_defense=0, keywords=[]
        )
        player.equip(spear)
        # No charge
        self.assertEqual(player.strength + spear.attack, player.attack(attacked_ent))

        # Charge
        player.position = (
            player.old_position[0] + 5 * TILE_SIZE,
            player.old_position[1],
        )
        self.assertEqual(
            player.strength + int(spear.attack * 1.5), player.attack(attacked_ent)
        )

        # Stronger charge
        player.position = (
            player.old_position[0] + 8 * TILE_SIZE,
            player.old_position[1],
        )
        self.assertEqual(
            player.strength + int(spear.attack * 2), player.attack(attacked_ent)
        )

    def test_no_charge_bonus_for_weapon_with_no_charge(self):
        power = 4
        weapon = random_weapon(atk=power, attack_kind="PHYSICAL", charge=False)
        player = random_player_entity()
        player.strength = 5
        attacked_ent = random_foe_entity(
            min_hp=1000, max_hp=1000, max_defense=0, keywords=[]
        )
        player.equip(weapon)

        # No charge bonus even if there is a " charge "
        player.position = (
            player.old_position[0] + 5 * TILE_SIZE,
            player.old_position[1],
        )
        self.assertEqual(player.strength + weapon.attack, player.attack(attacked_ent))


if __name__ == "__main__":
    unittest.main()
