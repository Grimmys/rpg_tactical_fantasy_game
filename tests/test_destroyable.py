import random as rd
import unittest

from src.game_entities.destroyable import DamageKind, Destroyable
from tests.random_data_library import (random_destroyable_entity,
                                       random_movable_entity)
from tests.tools import minimal_setup_for_game


class TestDestroyable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_destroyable(self):
        name = "destroyable"
        pos = (3, 2)
        sprite = "imgs/dungeon_crawl/monster/angel.png"
        hp = 10
        defense = 4
        res = 3
        destroyable = Destroyable(name, pos, sprite, hp, defense, res)
        self.assertEqual(name, destroyable.name)
        self.assertEqual(pos, destroyable.position)
        self.assertEqual("Destroyable", str(destroyable))
        self.assertEqual(hp, destroyable.hit_points_max)
        self.assertEqual(hp, destroyable.hit_points)
        self.assertEqual(defense, destroyable.defense)
        self.assertEqual(res, destroyable.resistance)
        self.assertTrue(destroyable.is_on_position(pos))

    def test_non_letal_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = rd.randint(0, destroyable.hit_points + destroyable.defense - 1)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hit_points)
        self.assertTrue(destroyable.hit_points > 0)

    def test_letal_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = destroyable.hit_points + destroyable.defense
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hit_points)
        self.assertEqual(destroyable.hit_points, 0)

    def test_more_than_letal_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = destroyable.hit_points + destroyable.defense + rd.randint(1, 20)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hit_points)
        self.assertEqual(destroyable.hit_points, 0)

    def test_negative_damage(self):
        destroyable = random_destroyable_entity()
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = rd.randint(-10, -1)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hit_points)
        self.assertEqual(destroyable.hit_points, destroyable.hit_points_max)

    def test_physical_and_spiritual_damage(self):
        destroyable = random_destroyable_entity(min_hp=30, max_defense=10, max_res=10)
        attacker = random_movable_entity()
        kind = DamageKind.PHYSICAL
        allies = []

        damage = rd.randint(10, 15)
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hit_points)
        self.assertEqual(
            destroyable.hit_points_max,
            destroyable.hit_points + damage - destroyable.defense,
        )

        # Destroyable entity is healed before next attack for simplify test
        destroyable.hit_points = destroyable.hit_points_max
        kind = DamageKind.SPIRITUAL
        returned_hp = destroyable.attacked(attacker, damage, kind, allies)

        self.assertEqual(returned_hp, destroyable.hit_points)
        self.assertEqual(
            destroyable.hit_points_max,
            destroyable.hit_points + damage - destroyable.resistance,
        )

    def test_full_heal(self):
        destroyable = random_destroyable_entity(min_hp=30)
        hp_max_init = destroyable.hit_points_max

        damage = rd.randint(2, 20)
        destroyable.hit_points -= damage
        recovered_hp = destroyable.healed()
        self.assertEqual(recovered_hp, damage)
        self.assertEqual(destroyable.hit_points_max, destroyable.hit_points)
        self.assertEqual(hp_max_init, destroyable.hit_points_max)

        damage = rd.randint(2, 20)
        destroyable.hit_points -= damage
        recovered_hp = destroyable.healed(damage)
        self.assertEqual(recovered_hp, damage)
        self.assertEqual(destroyable.hit_points_max, destroyable.hit_points)
        self.assertEqual(hp_max_init, destroyable.hit_points_max)

    def test_partial_heal(self):
        destroyable = random_destroyable_entity(min_hp=30)
        hp_max_init = destroyable.hit_points_max

        damage = rd.randint(11, 20)
        heal = rd.randint(1, 10)
        destroyable.hit_points -= damage
        recovered_hp = destroyable.healed(heal)
        self.assertEqual(recovered_hp, heal)
        self.assertEqual(
            destroyable.hit_points_max - damage + heal, destroyable.hit_points
        )
        self.assertEqual(hp_max_init, destroyable.hit_points_max)

    def test_more_than_possible_heal(self):
        destroyable = random_destroyable_entity(min_hp=30)
        hp_max_init = destroyable.hit_points_max

        damage = rd.randint(11, 20)
        destroyable.hit_points -= damage
        recovered_hp = destroyable.healed(damage + 30)
        self.assertEqual(recovered_hp, damage)
        self.assertEqual(destroyable.hit_points_max, destroyable.hit_points)
        self.assertEqual(hp_max_init, destroyable.hit_points_max)


if __name__ == "__main__":
    unittest.main()
