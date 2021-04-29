import unittest

import random as rd

from src.game_entities.destroyable import Destroyable, DamageKind
from tests.random_data_library import random_destroyable_entity, random_movable_entity
from tests.tools import minimal_setup_for_game

NB_TESTS_FOR_PROPORTIONS = 1000


class TestDestroyable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_destroyable(self):
        name = 'destroyable'
        pos = (3, 2)
        sprite = 'imgs/dungeon_crawl/monster/angel.bmp'
        hp = 10
        defense = 4
        res = 3
        destroyable = Destroyable(name, pos, sprite, hp, defense, res)
        self.assertEqual(name, destroyable.name)
        self.assertEqual(pos, destroyable.pos)
        self.assertEqual('Destroyable', str(destroyable))
        self.assertEqual(hp, destroyable.hp_max)
        self.assertEqual(hp, destroyable.hp)
        self.assertEqual(defense, destroyable.defense)
        self.assertEqual(res, destroyable.res)
        self.assertTrue(destroyable.is_on_pos(pos))

    def test_non_letal_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = rd.randint(0, destroyable.hp + destroyable.defense - 1)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hp)
        self.assertTrue(destroyable.hp > 0)

    def test_letal_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = destroyable.hp + destroyable.defense
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hp)
        self.assertEqual(destroyable.hp, 0)

    def test_more_than_letal_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = destroyable.hp + destroyable.defense + rd.randint(1, 20)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hp)
        self.assertEqual(destroyable.hp, 0)

    def test_negative_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = rd.randint(-10, -1)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hp)
        self.assertEqual(destroyable.hp, destroyable.hp_max)

    def test_physical_and_spiritual_damage(self):
        destroyable = random_destroyable_entity(min_hp=30, max_defense=10, max_res=10)
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = rd.randint(10, 15)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hp)
        self.assertEqual(destroyable.hp_max, destroyable.hp + damage - destroyable.defense)

        # Destroyable entity is healed before next attack for simplify test
        destroyable.hp = destroyable.hp_max
        kind = DamageKind.SPIRITUAL
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hp)
        self.assertEqual(destroyable.hp_max, destroyable.hp + damage - destroyable.res)

    def test_full_heal(self):
        destroyable = random_destroyable_entity(min_hp=30)
        hp_max_init = destroyable.hp_max

        damage = rd.randint(2, 20)
        destroyable.hp -= damage
        recovered_hp = destroyable.healed()
        self.assertEqual(recovered_hp, damage)
        self.assertEqual(destroyable.hp_max, destroyable.hp)
        self.assertEqual(hp_max_init, destroyable.hp_max)

        damage = rd.randint(2, 20)
        destroyable.hp -= damage
        recovered_hp = destroyable.healed(damage)
        self.assertEqual(recovered_hp, damage)
        self.assertEqual(destroyable.hp_max, destroyable.hp)
        self.assertEqual(hp_max_init, destroyable.hp_max)

    def test_partial_heal(self):
        destroyable = random_destroyable_entity(min_hp=30)
        hp_max_init = destroyable.hp_max

        damage = rd.randint(11, 20)
        heal = rd.randint(1, 10)
        destroyable.hp -= damage
        recovered_hp = destroyable.healed(heal)
        self.assertEqual(recovered_hp, heal)
        self.assertEqual(destroyable.hp_max - damage + heal, destroyable.hp)
        self.assertEqual(hp_max_init, destroyable.hp_max)

    def test_more_than_possible_heal(self):
        destroyable = random_destroyable_entity(min_hp=30)
        hp_max_init = destroyable.hp_max

        damage = rd.randint(11, 20)
        destroyable.hp -= damage
        recovered_hp = destroyable.healed(damage + 30)
        self.assertEqual(recovered_hp, damage)
        self.assertEqual(destroyable.hp_max, destroyable.hp)
        self.assertEqual(hp_max_init, destroyable.hp_max)


if __name__ == '__main__':
    unittest.main()
