import unittest

from src.game_entities.equipment import Equipment
from tests.random_data_library import random_equipment
from tests.tools import minimal_setup_for_game


class TestEquipment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_equipment(self):
        name = "dark_boots"
        sprite = "imgs/dungeon_crawl/item/armor/feet/dark_boots.png"
        description = "Well... Those are dark boots"
        price = 250
        equipped_sprite = "imgs/dungeon_crawl/player/boots/middle_gray.png"
        body_part = "feet"
        defense = 2
        resistance = 1
        attack = 0
        weight = 1
        restrictions = {}
        equipment = Equipment(
            name,
            sprite,
            description,
            price,
            [equipped_sprite],
            body_part,
            defense,
            resistance,
            attack,
            weight,
            restrictions,
        )
        self.assertEqual(name, equipment.name)
        self.assertEqual(description, equipment.description)
        self.assertEqual("Dark Boots", str(equipment))
        self.assertEqual(price, equipment.price)
        self.assertEqual(price // 2, equipment.resell_price)
        self.assertEqual(defense, equipment.defense)
        self.assertEqual(resistance, equipment.resistance)
        self.assertEqual(attack, equipment.attack)
        self.assertEqual(weight, equipment.weight)
        self.assertDictEqual(restrictions, equipment.restrictions)

    def test_formatted_restrictions(self):
        equipment = random_equipment(
            restrictions={
                "classes": ["warrior", "ranger", "spy"],
                "races": ["human", "dwarf"],
            }
        )
        self.assertEqual(
            "Warrior, Ranger, Spy, Human, Dwarf", equipment.get_formatted_restrictions()
        )


if __name__ == "__main__":
    unittest.main()
