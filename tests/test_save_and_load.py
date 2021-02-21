import unittest
import random as rd

from src.game_entities.foe import Keyword
from src.game_entities.gold import Gold
from src.game_entities.item import Item
from src.services.loadFromXMLManager import load_ally, load_alteration, load_foe, parse_item_file
from tests.random_data_library import random_character_entity, random_alteration, random_foe_entity, random_item, \
    random_gold, random_equipment
from tests.tools import minimal_setup_for_game


class TestSaveAndLoad(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_save_and_load_alteration(self):
        alteration = random_alteration()

        alteration_saved = alteration.save('alteration')
        loaded_alteration = load_alteration(alteration_saved)

        self.assertEqual(alteration.name, loaded_alteration.name)
        self.assertEqual(alteration.abbreviated_name, loaded_alteration.abbreviated_name)
        self.assertEqual(alteration.power, loaded_alteration.power)
        self.assertEqual(alteration.duration, loaded_alteration.duration)
        self.assertEqual(alteration.desc, loaded_alteration.desc)
        self.assertEqual(alteration.specificities, loaded_alteration.specificities)

    def test_save_and_load_character(self):
        interaction = {
            'dialog': ["Hurry up ! Leave the village from the west, and enter the necropolis.",
                       "The clock is ticking... The ogre's bones must be returned to their original place."],
            'join_team': False
        }
        character = random_character_entity(name='jist', classes=['innkeeper'], race='human', interaction=interaction)
        character_saved = character.save('ally')
        loaded_character = load_ally(character_saved, True, 0, 0)
        self.assertEqual(character.name, loaded_character.name)
        self.assertEqual(character.pos, loaded_character.pos)
        self.assertEqual(character.hp, loaded_character.hp)
        self.assertEqual(character.defense, loaded_character.defense)
        self.assertEqual(character.res, loaded_character.res)
        self.assertEqual(character.strength, loaded_character.strength)
        self.assertEqual(character.classes, loaded_character.classes)
        self.assertEqual(character.equipments, loaded_character.equipments)
        self.assertEqual(character.strategy, loaded_character.strategy)
        self.assertEqual(character.lvl, loaded_character.lvl)
        self.assertEqual(character.skills, loaded_character.skills)
        self.assertEqual(character.race, loaded_character.race)
        self.assertEqual(character.gold, loaded_character.gold)
        self.assertEqual(character.interaction, loaded_character.interaction)
        self.assertEqual(character.join_team, loaded_character.join_team)
        self.assertEqual(character.alterations, loaded_character.alterations)

    def test_save_and_load_character_with_alterations(self):
        character = random_character_entity(name="jist", classes=['innkeeper'])
        alteration = random_alteration()
        other_alteration = random_alteration()

        character.set_alteration(alteration)
        character.set_alteration(other_alteration)
        character_saved = character.save('ally')
        loaded_character = load_ally(character_saved, True, 0, 0)

        self.assertEqual(character.alterations, loaded_character.alterations)

    def test_save_and_load_foe(self):
        foe = random_foe_entity(name="skeleton_cobra", reach=[2], keywords=[Keyword.CAVALRY], loot=[(parse_item_file('monster_meat'), rd.random()), (random_gold(), rd.random())])
        foe_saved = foe.save('foe')
        loaded_foe = load_foe(foe_saved, True, 0, 0)
        self.assertEqual(foe.name, loaded_foe.name)
        self.assertEqual(foe.pos, loaded_foe.pos)
        self.assertEqual(foe.hp, loaded_foe.hp)
        self.assertEqual(foe.defense, loaded_foe.defense)
        self.assertEqual(foe.res, loaded_foe.res)
        self.assertEqual(foe.strength, loaded_foe.strength)
        self.assertEqual(foe.strategy, loaded_foe.strategy)
        self.assertEqual(foe.lvl, loaded_foe.lvl)
        self.assertEqual(foe.skills, loaded_foe.skills)
        self.assertEqual(foe.reach, loaded_foe.reach)
        self.assertEqual(foe.keywords, loaded_foe.keywords)
        self.assertEqual(foe.alterations, loaded_foe.alterations)
        self.assertEqual(foe.potential_loot, loaded_foe.potential_loot)