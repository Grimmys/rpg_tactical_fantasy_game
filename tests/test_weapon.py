import unittest

from src.game_entities.destroyable import DamageKind
from src.game_entities.foe import Keyword
from src.game_entities.weapon import Weapon
from tests.random_data_library import random_weapon, random_foe_entity
from tests.tools import minimal_setup_for_game

NB_TESTS_FOR_PROPORTIONS = 100


class TestWeapon(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_weapon(self):
        name = 'short_sword'
        sprite = 'imgs/dungeon_crawl/item/weapon/short_sword_2_old.png'
        description = 'A basic little sword, but one that can already prove very useful'
        price = 500
        equipped_sprite = ['imgs/dungeon_crawl/player/hand_right/short_sword.png']
        durability = 40
        reach = [1]
        power = 4
        kind = 'PHYSICAL'
        weight = 2
        restrictions = []
        possible_effects = []
        strong_against = [Keyword.LARGE]
        sword = Weapon(name, sprite, description, price, equipped_sprite, power, kind, weight, durability, reach,
                       restrictions, possible_effects, strong_against)
        self.assertEqual(name, sword.name)
        self.assertEqual(description, sword.desc)
        self.assertEqual('Short Sword', str(sword))
        self.assertEqual(price, sword.price)
        self.assertEqual(price // 2, sword.resell_price)
        self.assertEqual(durability, sword.durability_max)
        self.assertEqual(durability, sword.durability)
        self.assertEqual(reach, sword.reach)
        self.assertEqual(power, sword.atk)
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
        weapon = random_weapon(atk=power)
        self.assertEqual(power, weapon.hit(random_foe_entity()))

    def test_stronger_against_specific_entity_kind(self):
        power = 5
        strong_against = [Keyword.LARGE]
        weapon = random_weapon(atk=power, strong_against=strong_against)

        normal_foe = random_foe_entity()
        self.assertEqual(power, weapon.hit(normal_foe))

        vulnerable_foe = random_foe_entity(keywords=[Keyword.LARGE])
        self.assertEqual(power * 2, weapon.hit(vulnerable_foe))

    def test_stronger_against_multiple_entity_kinds(self):
        power = 4
        strong_against = [Keyword.LARGE, Keyword.CAVALRY]
        weapon = random_weapon(atk=power, strong_against=strong_against)

        non_vulnerable_foe = random_foe_entity(keywords=[Keyword.SMALL])
        self.assertEqual(power, weapon.hit(non_vulnerable_foe))

        vulnerable_foe = random_foe_entity(keywords=[Keyword.LARGE])
        self.assertEqual(power * 2, weapon.hit(vulnerable_foe))

        super_vulnerable_foe = random_foe_entity(keywords=[Keyword.CAVALRY, Keyword.LARGE])
        self.assertEqual(power * 3, weapon.hit(super_vulnerable_foe))


if __name__ == '__main__':
    unittest.main()
