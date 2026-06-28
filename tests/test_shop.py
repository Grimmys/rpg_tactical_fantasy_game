import random as rd
import unittest

from pathlib import Path
from src.game_entities.shop import Shop
from tests.random_data_library import random_character_entity, random_item
from tests.tools import minimal_setup_for_game


class TestShop(unittest.TestCase):
    SHOP_NAME = "tavern"
    SHOP_POSITION = (3, 2)
    SHOP_SPRITE = Path("imgs", "houses", "blue_house.png")
    DEFAULT_BALANCE = 500

    @classmethod
    def setUpClass(cls):
        minimal_setup_for_game()

    def _shop(self, stock, balance=None, interaction=None):
        balance = self.DEFAULT_BALANCE if balance is None else balance
        return Shop(
            self.SHOP_NAME,
            self.SHOP_POSITION,
            self.SHOP_SPRITE,
            balance,
            stock,
            interaction,
        )

    @staticmethod
    def _actor(gold, items=None):
        actor = random_character_entity()
        actor.gold = gold
        actor.items = list(items) if items is not None else []
        return actor

    def test_init_shop(self):
        interaction = None
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = self._shop(items, interaction=interaction)
        self.assertEqual(self.SHOP_NAME, shop.name)
        self.assertEqual(self.SHOP_POSITION, shop.position)
        self.assertEqual("Tavern", str(shop))
        self.assertEqual(self.DEFAULT_BALANCE, shop.shop_balance)
        self.assertTrue(items[0] in shop.stock)
        self.assertTrue(items[1] in shop.stock)

    def test_interact(self):
        items = [
            {"item": random_item(), "quantity": rd.randint(1, 10)},
            {"item": random_item(), "quantity": rd.randint(1, 10)},
        ]
        shop = self._shop(items)
        actor = random_character_entity()
        shop.interact(actor)

    def test_buy_item(self):
        item_price = 100
        item_to_buy = random_item(price=item_price)
        item_quantity = 5
        items = [{"item": item_to_buy, "quantity": item_quantity}]
        shop = self._shop(items)
        buyer_gold = 200
        buyer = self._actor(buyer_gold)
        shop.interact(buyer)
        shop.buy(item_to_buy)

        self.assertEqual(buyer.gold, buyer_gold - item_price)
        self.assertEqual(shop.shop_balance, self.DEFAULT_BALANCE + item_price)
        self.assertEqual(len(buyer.items), 1)
        self.assertEqual(
            shop.get_item_entry(item_to_buy)["quantity"],
            item_quantity - 1,
        )

    def test_buy_all_items(self):
        item_price = 50
        item_to_buy = random_item(price=item_price)
        initial_quantity = 3
        items = [{"item": item_to_buy, "quantity": initial_quantity}]
        shop = self._shop(items)
        buyer_gold = 500
        buyer = self._actor(buyer_gold)
        shop.interact(buyer)
        self.assertIsNotNone(shop.get_item_entry(item_to_buy))
        self.assertEqual(shop.get_item_entry(item_to_buy)["quantity"], initial_quantity)
        for remaining in range(initial_quantity, 0, -1):
            shop.buy(item_to_buy)
            entry = shop.get_item_entry(item_to_buy)
            if remaining - 1 > 0:
                self.assertEqual(entry["quantity"], remaining - 1)
            else:
                self.assertIsNone(entry)
        self.assertIsNone(shop.get_item_entry(item_to_buy))
        self.assertEqual(len(shop.stock), 0)
        self.assertEqual(len(buyer.items), initial_quantity)
        self.assertEqual(buyer.gold, buyer_gold - (item_price * initial_quantity))

    def test_sell_item(self):
        items = [{"item": random_item(), "quantity": 5}]
        shop = self._shop(items)
        item_to_sell = random_item(price=100)
        seller_gold = 50
        seller = self._actor(seller_gold, [item_to_sell])
        shop.interact(seller)
        expected_resell_price = item_to_sell.resell_price
        success, _ = shop.sell(item_to_sell)
        self.assertTrue(success)
        self.assertEqual(seller.gold, seller_gold + expected_resell_price)
        self.assertEqual(
            shop.shop_balance,
            self.DEFAULT_BALANCE - expected_resell_price,
        )
        self.assertNotIn(item_to_sell, seller.items)

    def test_buy_item_not_enough_gold(self):
        item_price = 500
        item_to_buy = random_item(price=item_price)
        initial_quantity = 5
        items = [{"item": item_to_buy, "quantity": initial_quantity}]
        shop = self._shop(items)
        buyer_gold = 100
        buyer = self._actor(buyer_gold)
        shop.interact(buyer)
        shop.buy(item_to_buy)
        self.assertEqual(buyer.gold, buyer_gold)
        self.assertEqual(shop.shop_balance, self.DEFAULT_BALANCE)
        self.assertEqual(len(buyer.items), 0)
        self.assertEqual(
            shop.get_item_entry(item_to_buy)["quantity"],
            initial_quantity,
        )

    def test_sell_item_shop_cant_afford(self):
        shop_balance = 10
        items = [{"item": random_item(), "quantity": 5}]
        shop = self._shop(items, balance=shop_balance)
        item_to_sell = random_item(price=100)
        seller_gold = 50
        seller = self._actor(seller_gold, [item_to_sell])
        shop.interact(seller)
        success, _ = shop.sell(item_to_sell)
        self.assertFalse(success)
        self.assertEqual(seller.gold, seller_gold)
        self.assertEqual(shop.shop_balance, shop_balance)
        self.assertIn(item_to_sell, seller.items)


if __name__ == "__main__":
    unittest.main()
