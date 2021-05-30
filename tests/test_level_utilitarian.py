import shutil
import unittest
import random as rd

import pygame as pg

from src.scenes.start_screen import StartScreen
from src.constants import MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT, TILE_SIZE
from src.services import menu_creator_manager
from tests.test_start_screen import (
    LOAD_GAME_BUTTON_POS,
    LEFT_BUTTON,
    LOAD_FIRST_SLOT_BUTTON_POS,
)
from tests.tools import minimal_setup_for_game


class TestLevel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()
        cls.save_path = "saves/save_0.xml"

    def setUp(self):
        # Window parameters
        screen = pg.display.set_mode((MAIN_WIN_WIDTH, MAIN_WIN_HEIGHT))
        self.start_screen = StartScreen(screen)
        self.start_screen.display()

    def import_save_file(self, import_path):
        """

        :param import_path:
        """
        shutil.copyfile(import_path, self.save_path)
        self.start_screen.click(LEFT_BUTTON, LOAD_GAME_BUTTON_POS)
        self.start_screen.display()
        self.start_screen.click(LEFT_BUTTON, LOAD_FIRST_SLOT_BUTTON_POS)
        self.level = self.start_screen.level

    def simulate_trade_item(
        self, item, active_player, other_player, is_active_the_sender
    ):
        """

        :param item:
        :param active_player:
        :param other_player:
        :param is_active_the_sender:
        """
        # Store the current menu before making trade
        self.level.background_menus.append((self.level.active_menu, False))
        self.level.interact(active_player, other_player, ())
        self.level.interact_trade_item(
            item, (0, 0), (active_player, other_player), is_active_the_sender
        )
        self.level.trade_item(active_player, other_player, is_active_the_sender)
        self.level.execute_action(self.level.close_active_menu)
        self.level.execute_action(self.level.close_active_menu)

    def test_distance_between_two_entities(self):
        # Import simple save file
        self.import_save_file("tests/test_saves/simple_save.xml")

        players = self.level.players
        foe = self.level.entities["foes"][0]
        entities_with_dist = self.level.distance_between_all(foe, players)

        self.assertEqual(5, entities_with_dist[players[0]])

    def test_distance_between_many_entities(self):
        # Import complete save file
        self.import_save_file("tests/test_saves/complete_first_level_save.xml")

        players = self.level.players
        foes = self.level.entities["foes"]

        raimund = None
        braern = None
        thokdrum = None
        for player in players:
            pos = (player.position[0] // TILE_SIZE, player.position[1] // TILE_SIZE)
            if pos == (17, 10):
                raimund = player
            elif pos == (16, 9):
                braern = player
            elif pos == (16, 10):
                thokdrum = player

        specific_skeleton = None
        specific_necrophage = None
        for f in foes:
            pos = (f.position[0] // TILE_SIZE, f.position[1] // TILE_SIZE)
            if pos == (12, 8):
                specific_skeleton = f
            if pos == (13, 5):
                specific_necrophage = f

        entities_with_dist = self.level.distance_between_all(specific_skeleton, players)
        self.assertEqual(12, entities_with_dist[raimund])
        self.assertEqual(4, entities_with_dist[braern])
        self.assertEqual(5, entities_with_dist[thokdrum])

        entities_with_dist = self.level.distance_between_all(
            specific_necrophage, players
        )
        self.assertEqual(8, entities_with_dist[raimund])
        self.assertEqual(6, entities_with_dist[braern])
        self.assertEqual(7, entities_with_dist[thokdrum])

    def test_cancel_movement_after_trade_item_sent(self):
        # Import complete save file
        self.import_save_file("tests/test_saves/complete_first_level_save.xml")

        players = self.level.players

        active_player = [player for player in players if player.name == "raimund"][0]
        receiver_player = [player for player in players if player.name == "braern"][0]
        self.level.selected_player = active_player

        item = rd.choice(active_player.items)

        # Open character menu
        self.level.active_menu = menu_creator_manager.create_player_menu(
            {"inventory": None, "equipment": None, "status": None, "wait": None},
            active_player,
            [],
            [],
            [],
            [],
        )

        # Make trade (send item from active player to receiver player)
        self.simulate_trade_item(item, active_player, receiver_player, True)

        self.assertFalse(item in active_player.items)
        self.assertTrue(item in receiver_player.items)

        # Cancel active player turn
        self.level.right_click()

        self.assertTrue(item in active_player.items)
        self.assertFalse(item in receiver_player.items)

    def test_cancel_movement_after_trade_item_received(self):
        # Import complete save file
        self.import_save_file("tests/test_saves/complete_first_level_save.xml")

        players = self.level.players

        active_player = [player for player in players if player.name == "raimund"][0]
        sender_player = [player for player in players if player.name == "braern"][0]
        self.level.selected_player = active_player

        item = rd.choice(sender_player.items)

        # Open character menu
        self.level.active_menu = menu_creator_manager.create_player_menu(
            {"inventory": None, "equipment": None, "status": None, "wait": None},
            active_player,
            [],
            [],
            [],
            [],
        )

        # Make trade (send item from active player to receiver player)
        self.simulate_trade_item(item, active_player, sender_player, False)

        self.assertTrue(item in active_player.items)
        self.assertFalse(item in sender_player.items)

        # Cancel active player turn
        self.level.right_click()

        self.assertFalse(item in active_player.items)
        self.assertTrue(item in sender_player.items)

    def test_cancel_movement_after_trade_items_sent_and_received(self):
        # Import complete save file
        self.import_save_file("tests/test_saves/complete_first_level_save.xml")

        players = self.level.players

        active_player = [player for player in players if player.name == "raimund"][0]
        trade_partner_player = [
            player for player in players if player.name == "braern"
        ][0]
        self.level.selected_player = active_player

        item = rd.choice(trade_partner_player.items)
        second_item = rd.choice(active_player.items)

        # Open character menu
        self.level.active_menu = menu_creator_manager.create_player_menu(
            {"inventory": None, "equipment": None, "status": None, "wait": None},
            active_player,
            [],
            [],
            [],
            [],
        )

        # Make trade (send item from active player to receiver player)
        self.simulate_trade_item(item, active_player, trade_partner_player, False)
        self.simulate_trade_item(second_item, active_player, trade_partner_player, True)

        self.assertTrue(item in active_player.items)
        self.assertFalse(item in trade_partner_player.items)
        self.assertFalse(second_item in active_player.items)
        self.assertTrue(second_item in trade_partner_player.items)

        # Cancel active player turn
        self.level.right_click()

        self.assertFalse(item in active_player.items)
        self.assertTrue(item in trade_partner_player.items)
        self.assertTrue(second_item in active_player.items)
        self.assertFalse(second_item in trade_partner_player.items)

    @unittest.skip
    def test_cancel_movement_after_trade_gold_sent(self):
        pass

    @unittest.skip
    def test_cancel_movement_after_trade_gold_received(self):
        pass

    @unittest.skip
    def test_cancel_movement_after_trade_items_and_gold_sent_and_received(self):
        pass


if __name__ == "__main__":
    unittest.main()
