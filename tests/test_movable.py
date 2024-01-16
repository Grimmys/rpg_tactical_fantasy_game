import random as rd
import unittest

from src.game_entities.movable import DamageKind, EntityStrategy, Movable
from tests.random_data_library import (STATS, random_alteration, random_item,
                                       random_movable_entity, random_string)
from tests.tools import minimal_setup_for_game


class TestMovable(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_movable(self):
        name = "movable0"
        pos = (3, 2)
        sprite = "imgs/dungeon_crawl/monster/angel.png"
        hp = 10
        defense = 4
        res = 3
        max_moves = 5
        strength = 2
        attack_kind = "PHYSICAL"
        strategy = "STATIC"
        movable_entity = Movable(
            name,
            pos,
            sprite,
            hp,
            defense,
            res,
            max_moves,
            strength,
            attack_kind,
            strategy,
        )
        self.assertTrue(movable_entity.is_on_position(pos))
        self.assertEqual(max_moves, movable_entity.max_moves)
        self.assertEqual(strength, movable_entity.strength)
        self.assertEqual(DamageKind[attack_kind], movable_entity.attack_kind)
        self.assertEqual(EntityStrategy[strategy], movable_entity.strategy)
        self.assertEqual(1, movable_entity.lvl)
        self.assertEqual(0, movable_entity.experience)
        self.assertEqual(0, len(movable_entity.alterations))
        self.assertEqual(0, len(movable_entity.items))
        self.assertEqual(0, len(movable_entity.skills))
        self.assertFalse(movable_entity.turn_is_finished())
        self.assertTrue(movable_entity.has_free_space())
        self.assertTrue(movable_entity.can_attack())
        self.assertEqual("None", movable_entity.get_formatted_alterations())
        self.assertEqual("None", movable_entity.get_abbreviated_alterations())
        self.assertEqual("", movable_entity.get_formatted_stat_change(rd.choice(STATS)))

    def test_end_turn(self):
        movable_entity = random_movable_entity()

        self.assertFalse(movable_entity.turn_is_finished())
        movable_entity.end_turn()
        self.assertTrue(movable_entity.turn_is_finished())

    def test_simple_move(self):
        movable_entity = random_movable_entity()

        new_pos = (
            movable_entity.position[0] + rd.randint(1, 20),
            movable_entity.position[1] + rd.randint(1, 20),
        )
        movable_entity.set_move([new_pos])
        movable_entity._timer = 0
        movable_entity.move()

        self.assertTrue(movable_entity.is_on_position(new_pos))

    def test_new_alteration(self):
        movable_entity = random_movable_entity()
        alteration = random_alteration(name="alt_test")

        self.assertEqual(0, len(movable_entity.alterations))
        self.assertEqual(0, len(movable_entity.get_alterations_effect("alt_test")))
        movable_entity.set_alteration(alteration)
        self.assertEqual(1, len(movable_entity.alterations))
        self.assertEqual(1, len(movable_entity.get_alterations_effect("alt_test")))
        self.assertEqual(0, len(movable_entity.get_alterations_effect(random_string())))

    def test_different_alterations(self):
        movable_entity = random_movable_entity()
        alteration = random_alteration(name="alt_test")
        alteration_bis = random_alteration(name="alt_test_bis")

        self.assertEqual(0, len(movable_entity.alterations))
        self.assertEqual(0, len(movable_entity.get_alterations_effect("alt_test")))
        self.assertEqual(0, len(movable_entity.get_alterations_effect("alt_test_bis")))
        movable_entity.set_alteration(alteration)
        self.assertEqual(1, len(movable_entity.get_alterations_effect("alt_test")))
        self.assertEqual(0, len(movable_entity.get_alterations_effect("alt_test_bis")))
        movable_entity.set_alteration(alteration_bis)
        self.assertEqual(1, len(movable_entity.get_alterations_effect("alt_test")))
        self.assertEqual(1, len(movable_entity.get_alterations_effect("alt_test_bis")))

        # Test formatted alterations rendering
        self.assertEqual(
            f"{alteration}, {alteration_bis}",
            movable_entity.get_formatted_alterations(),
        )
        self.assertEqual(
            f"{alteration.abbreviated_name}, {alteration_bis.abbreviated_name}",
            movable_entity.get_abbreviated_alterations(),
        )

    def test_stat_up(self):
        movable_entity = random_movable_entity()
        stat = rd.choice(STATS)
        other_stat = rd.choice(tuple(filter(lambda s: s != stat, STATS)))
        stat_up_alteration = random_alteration(
            name=stat + "_up", effects=[stat + "_up"]
        )

        self.assertEqual(0, movable_entity.get_stat_change(stat))
        self.assertEqual(0, movable_entity.get_stat_change(other_stat))
        movable_entity.set_alteration(stat_up_alteration)
        self.assertEqual(stat_up_alteration.power, movable_entity.get_stat_change(stat))
        self.assertEqual(0, movable_entity.get_stat_change(other_stat))

        # Test formatted stat change rendering
        self.assertEqual(
            f" (+{stat_up_alteration.power})",
            movable_entity.get_formatted_stat_change(stat),
        )

    def test_stat_down(self):
        movable_entity = random_movable_entity()
        stat = rd.choice(STATS)
        stat_down_alteration = random_alteration(
            name=stat + "_down", effects=[stat + "_down"]
        )

        movable_entity.set_alteration(stat_down_alteration)
        # Test formatted stat change rendering
        self.assertEqual(
            f" (-{stat_down_alteration.power})",
            movable_entity.get_formatted_stat_change(stat),
        )

    def test_earn_xp(self):
        movable_entity = random_movable_entity()
        old_lvl = movable_entity.lvl
        earned_xp = rd.randint(1, movable_entity.experience_to_lvl_up - 1)

        self.assertEqual(0, movable_entity.experience)
        self.assertFalse(movable_entity.earn_xp(earned_xp))
        self.assertEqual(old_lvl, movable_entity.lvl)
        self.assertEqual(earned_xp, movable_entity.experience)

    def test_earn_multiple_times_xp(self):
        movable_entity = random_movable_entity()
        old_lvl = movable_entity.lvl
        earned_xp = rd.randint(1, (movable_entity.experience_to_lvl_up // 2) - 1)
        earned_xp_bis = rd.randint(1, (movable_entity.experience_to_lvl_up // 2) - 1)

        self.assertEqual(0, movable_entity.experience)
        self.assertFalse(movable_entity.earn_xp(earned_xp))
        self.assertEqual(old_lvl, movable_entity.lvl)
        self.assertEqual(earned_xp, movable_entity.experience)
        self.assertFalse(movable_entity.earn_xp(earned_xp_bis))
        self.assertEqual(old_lvl, movable_entity.lvl)
        self.assertEqual(earned_xp + earned_xp_bis, movable_entity.experience)

    def test_lvl_up(self):
        movable_entity = random_movable_entity()
        old_lvl = movable_entity.lvl
        old_xp_required = movable_entity.experience_to_lvl_up
        earned_xp = old_xp_required

        self.assertEqual(0, movable_entity.experience)
        self.assertTrue(movable_entity.earn_xp(earned_xp))
        self.assertEqual(old_lvl + 1, movable_entity.lvl)
        self.assertEqual(0, movable_entity.experience)
        self.assertTrue(old_xp_required < movable_entity.experience_to_lvl_up)

    def test_more_xp_than_needed(self):
        movable_entity = random_movable_entity()
        old_lvl = movable_entity.lvl
        old_xp_required = movable_entity.experience_to_lvl_up
        sup_xp_amount = rd.randint(1, 30)
        earned_xp = old_xp_required + sup_xp_amount

        self.assertEqual(0, movable_entity.experience)
        self.assertTrue(movable_entity.earn_xp(earned_xp))
        self.assertEqual(old_lvl + 1, movable_entity.lvl)
        self.assertEqual(sup_xp_amount, movable_entity.experience)
        self.assertTrue(old_xp_required < movable_entity.experience_to_lvl_up)

    def test_add_item(self):
        movable_entity = random_movable_entity()
        item = random_item()

        self.assertTrue(movable_entity.has_free_space())
        self.assertEqual(0, len(movable_entity.items))
        self.assertTrue(movable_entity.set_item(item))
        self.assertEqual(1, len(movable_entity.items))
        self.assertEqual(item, movable_entity.get_item(0))
        self.assertFalse(movable_entity.get_item(1))

    def test_remove_item(self):
        movable_entity = random_movable_entity()
        item = random_item()

        self.assertTrue(movable_entity.has_free_space())
        self.assertEqual(0, len(movable_entity.items))
        self.assertTrue(movable_entity.set_item(item))
        self.assertEqual(item, movable_entity.remove_item(item))
        self.assertEqual(0, len(movable_entity.items))
        self.assertFalse(movable_entity.get_item(0))

    def test_add_multiple_items(self):
        movable_entity = random_movable_entity()
        item = random_item()
        other_item = random_item()

        self.assertTrue(movable_entity.has_free_space())
        self.assertEqual(0, len(movable_entity.items))
        self.assertTrue(movable_entity.set_item(item))
        self.assertTrue(movable_entity.set_item(other_item))
        self.assertEqual(2, len(movable_entity.items))
        self.assertEqual(item, movable_entity.get_item(0))
        self.assertEqual(other_item, movable_entity.get_item(1))

    def test_attacked(self):
        attacked_entity = random_movable_entity()
        attacker_entity = random_movable_entity()
        damage = rd.randint(attacked_entity.hit_points // 2, attacked_entity.hit_points)

        hp_left = attacked_entity.attacked(
            attacker_entity, damage, DamageKind["PHYSICAL"], []
        )
        self.assertEqual(hp_left, attacked_entity.hit_points)
        hp_expected = (
            attacked_entity.hit_points_max - damage + attacked_entity.defense
            if hp_left < attacked_entity.hit_points_max
            else attacked_entity.hit_points_max
        )
        self.assertEqual(hp_expected, hp_left)

    def test_alteration_boost_defense(self):
        attacked_entity = random_movable_entity()
        attacker_entity = random_movable_entity()
        damage = rd.randint(attacked_entity.hit_points // 2, attacked_entity.hit_points)
        boost_alteration = random_alteration(name="defense_up", effects=["defense_up"])

        attacked_entity.set_alteration(boost_alteration)
        hp_left = attacked_entity.attacked(
            attacker_entity, damage, DamageKind["PHYSICAL"], []
        )
        self.assertEqual(hp_left, attacked_entity.hit_points)
        hp_expected = (
            attacked_entity.hit_points_max
            - damage
            + attacked_entity.defense
            + boost_alteration.power
            if hp_left < attacked_entity.hit_points_max
            else attacked_entity.hit_points_max
        )
        self.assertEqual(hp_expected, hp_left)
