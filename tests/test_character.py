import unittest

from src.game_entities.character import Character
from src.game_entities.movable import DamageKind
from tests.random_data_library import (random_character_entity,
                                       random_equipment, random_foe_entity,
                                       random_shield, random_weapon)
from tests.tools import minimal_setup_for_game


class TestCharacter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_character(self):
        name = "character_test"
        pos = (3, 2)
        sprite = "imgs/characs/jist.png"
        hp = 10
        defense = 4
        res = 3
        strength = 2
        classes = ["innkeeper"]
        equipments = []
        strategy = "STATIC"
        lvl = 3
        skills = []
        alterations = []
        race = "human"
        gold = 500
        interaction = {
            "dialog": [
                "Hurry up ! Leave the village from the west, and enter the necropolis.",
                "The clock is ticking... The ogre's bones must be returned to their "
                "original place.",
            ],
            "join_team": False,
        }
        character_test = Character(
            name,
            pos,
            sprite,
            hp,
            defense,
            res,
            strength,
            classes,
            equipments,
            strategy,
            lvl,
            skills,
            alterations,
            race,
            gold,
            interaction,
        )
        self.assertEqual(equipments, character_test.equipments)
        self.assertEqual(classes, character_test.classes)
        self.assertEqual(race, character_test.race)
        self.assertEqual(gold, character_test.gold)
        self.assertFalse(character_test.join_team)
        self.assertEqual(int, type(character_test.constitution))

    def test_talk_to_character(self):
        interaction = {
            "dialog": [
                "Hurry up ! Leave the village from the west, and enter the necropolis.",
                "The clock is ticking... The ogre's bones must be returned to their "
                "original place.",
            ],
            "join_team": False,
        }
        actor = random_character_entity()
        character_test = random_character_entity(interaction=interaction)
        entries = character_test.talk(actor)
        self.assertEqual(2, len(entries))

    def test_talk_to_recruitable_character(self):
        interaction = {
            "dialog": [
                "Hurry up ! Leave the village from the west, and enter the necropolis.",
                "The clock is ticking... The ogre's bones must be returned to their "
                "original place.",
            ],
            "join_team": True,
        }
        actor = random_character_entity()
        character_test = random_character_entity(interaction=interaction)
        character_test.talk(actor)
        self.assertTrue(character_test.join_team)

    def test_lvl_up(self):
        character_test = random_character_entity(lvl=3)
        hp_before = character_test.hit_points_max
        character_test.lvl_up()
        self.assertEqual(4, character_test.lvl)
        self.assertNotEqual(hp_before, character_test.hit_points_max)

    def test_parried(self):
        parry_rate = 100
        equipments = [random_shield(parry_rate=parry_rate)]
        character_test = random_character_entity(equipments=equipments)
        self.assertTrue(character_test.parried())

        parry_rate = 0
        equipments = [random_shield(parry_rate=parry_rate)]
        character_test.equipments = equipments
        self.assertFalse(character_test.parried())

    def test_attacked_while_having_equipments(self):
        defense = 2
        res = 3
        equipments = [random_equipment(defense=defense, res=res)]
        character_test = random_character_entity(equipments=equipments)

        # Physical attack
        damage = character_test.defense + 5
        character_test.attacked(random_foe_entity(), damage, DamageKind.PHYSICAL, [])
        self.assertEqual(character_test.hit_points_max - 3, character_test.hit_points)

        character_test.healed()

        # Mental attack
        damage = character_test.resistance + 5
        character_test.attacked(random_foe_entity(), damage, DamageKind.SPIRITUAL, [])
        self.assertEqual(character_test.hit_points_max - 2, character_test.hit_points)

    def test_attack_with_weapon(self):
        weapon = random_weapon(strong_against=[])
        equipments = [weapon]
        character_test = random_character_entity(equipments=equipments)

        self.assertEqual(
            character_test.strength + weapon.attack,
            character_test.attack(random_foe_entity()),
        )
