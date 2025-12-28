import random as rd
import unittest

from src.game_entities.shop import Shop
from tests.random_data_library import random_character_entity, random_item
from tests.tools import minimal_setup_for_game


class TestShop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def test_init_shop(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        interaction = None
        shop_balance = 500
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, shop_balance, items, interaction)
        self.assertEqual(name, shop.name)
        self.assertEqual(pos, shop.position)
        self.assertEqual("Tavern", str(shop))
        self.assertEqual(shop_balance, shop.shop_balance)
        self.assertTrue(items[0] in shop.stock)
        self.assertTrue(items[1] in shop.stock)

    def test_interact(self):
        name = "tavern"
        pos = (3, 2)
        sprite = "imgs/houses/blue_house.png"
        shop_balance = 500
        interaction = None
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = Shop(name, pos, sprite, shop_balance, items, interaction)
        actor = random_character_entity()
        shop.interact(actor)
        # No assert for the moment

    def test_buy_item(self):
        # Setup: Create a shop with a known item and price
        item_price = 100
        item_to_buy = random_item(price=item_price)
        item_quantity = 5
        shop_balance = 500
        items = [{"item": item_to_buy, "quantity": item_quantity}]
        shop = Shop("tavern", (3, 2), "imgs/houses/blue_house.png", shop_balance, items, None)

        # Setup: Create a character with enough gold
        buyer = random_character_entity()
        buyer.gold = 200
        buyer.items = []  # Clear inventory

        # Interact to set current_visitor
        shop.interact(buyer)

        # Store initial values
        buyer_gold_before = buyer.gold
        shop_balance_before = shop.shop_balance
        buyer_items_before = len(buyer.items)
        item_quantity_before = shop.get_item_entry(item_to_buy)["quantity"]

        # Act: Buy the item
        result_message = shop.buy(item_to_buy)

        # Assert: Purchase was successful
        self.assertEqual(buyer.gold, buyer_gold_before - item_price)
        self.assertEqual(shop.shop_balance, shop_balance_before + item_price)
        self.assertEqual(len(buyer.items), buyer_items_before + 1)
        self.assertEqual(shop.get_item_entry(item_to_buy)["quantity"], item_quantity_before - 1)

    def test_buy_all_items(self):
        # Setup: Create a shop with an item that has 3 in stock
        item_price = 50
        item_to_buy = random_item(price=item_price)
        initial_quantity = 3
        items = [{"item": item_to_buy, "quantity": initial_quantity}]
        shop = Shop("tavern", (3, 2), "imgs/houses/blue_house.png", 500, items, None)

        # Setup: Create a character with enough gold to buy all items
        buyer = random_character_entity()
        buyer.gold = 500
        buyer.items = []

        # Interact to set current_visitor
        shop.interact(buyer)

        # Verify item is in stock before purchase
        self.assertIsNotNone(shop.get_item_entry(item_to_buy))
        self.assertEqual(shop.get_item_entry(item_to_buy)["quantity"], initial_quantity)

        # Act: Buy all items one by one
        for i in range(initial_quantity):
            shop.buy(item_to_buy)
            expected_remaining = initial_quantity - (i + 1)
            
            if expected_remaining > 0:
                # Item should still be in stock with reduced quantity
                self.assertEqual(shop.get_item_entry(item_to_buy)["quantity"], expected_remaining)
            else:
                # Item should be removed from stock entirely
                self.assertIsNone(shop.get_item_entry(item_to_buy))

        # Assert: Final state - item completely removed from stock
        self.assertIsNone(shop.get_item_entry(item_to_buy))
        self.assertEqual(len(shop.stock), 0)
        self.assertEqual(len(buyer.items), initial_quantity)
        self.assertEqual(buyer.gold, 500 - (item_price * initial_quantity))

    def test_sell_item(self):
        # Setup: Create a shop with some balance
        shop_balance = 500
        items = [{"item": random_item(), "quantity": 5}]
        shop = Shop("tavern", (3, 2), "imgs/houses/blue_house.png", shop_balance, items, None)

        # Setup: Create a character with an item to sell
        item_to_sell = random_item(price=100)  # resell_price will be 50 (half of price)
        seller = random_character_entity()
        seller.gold = 50
        seller.items = [item_to_sell]

        # Interact to set current_visitor
        shop.interact(seller)

        # Store initial values
        seller_gold_before = seller.gold
        shop_balance_before = shop.shop_balance
        expected_resell_price = item_to_sell.resell_price

        # Act: Sell the item
        success, message = shop.sell(item_to_sell)

        # Assert: Sale was successful
        self.assertTrue(success)
        self.assertEqual(seller.gold, seller_gold_before + expected_resell_price)
        self.assertEqual(shop.shop_balance, shop_balance_before - expected_resell_price)
        self.assertNotIn(item_to_sell, seller.items)

    def test_buy_item_not_enough_gold(self):
        # Setup: Create a shop with an expensive item
        item_price = 500
        item_to_buy = random_item(price=item_price)
        items = [{"item": item_to_buy, "quantity": 5}]
        shop = Shop("tavern", (3, 2), "imgs/houses/blue_house.png", 500, items, None)

        # Setup: Create a character with insufficient gold
        buyer = random_character_entity()
        buyer.gold = 100  # Less than item price
        buyer.items = []

        # Interact to set current_visitor
        shop.interact(buyer)

        # Store initial values
        buyer_gold_before = buyer.gold
        shop_balance_before = shop.shop_balance
        item_quantity_before = shop.get_item_entry(item_to_buy)["quantity"]

        # Act: Attempt to buy the item
        result_message = shop.buy(item_to_buy)

        # Assert: Purchase failed - nothing changed
        self.assertEqual(buyer.gold, buyer_gold_before)
        self.assertEqual(shop.shop_balance, shop_balance_before)
        self.assertEqual(len(buyer.items), 0)
        self.assertEqual(shop.get_item_entry(item_to_buy)["quantity"], item_quantity_before)

    def test_sell_item_shop_cant_afford(self):
        # Setup: Create a shop with very low balance
        shop_balance = 10
        items = [{"item": random_item(), "quantity": 5}]
        shop = Shop("tavern", (3, 2), "imgs/houses/blue_house.png", shop_balance, items, None)

        # Setup: Create a character with an item worth more than shop can afford
        item_to_sell = random_item(price=100)  # resell_price will be 50, more than shop's 10
        seller = random_character_entity()
        seller.gold = 50
        seller.items = [item_to_sell]

        # Interact to set current_visitor
        shop.interact(seller)

        # Store initial values
        seller_gold_before = seller.gold
        shop_balance_before = shop.shop_balance

        # Act: Attempt to sell the item
        success, message = shop.sell(item_to_sell)

        # Assert: Sale failed - nothing changed
        self.assertFalse(success)
        self.assertEqual(seller.gold, seller_gold_before)
        self.assertEqual(shop.shop_balance, shop_balance_before)
        self.assertIn(item_to_sell, seller.items)


if __name__ == "__main__":
    unittest.main()
