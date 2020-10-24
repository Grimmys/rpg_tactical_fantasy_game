import random as rd

from src.Chest import Chest
from src.Item import Item

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def generate_random_string(min_len=4, max_len=8):
    size = rd.randint(min_len, max_len)
    return ''.join([rd.choice(ALPHABET) for _ in range(size)])


def random_item_or_gold(gold_prob=0.5):
    if rd.random() <= gold_prob:
        # Gold is not implemented for chests
        pass
    else:
        return random_item()


def random_item():
    name = generate_random_string()
    sample_img = 'imgs/dungeon_crawl/item/potion/yellow_new.png'
    desc = generate_random_string(min_len=10, max_len=100)
    cost = rd.randint(0, 1000)
    item = Item(name, sample_img, desc, cost)
    return item


def random_chest(item_set=None, nb_items=None, equal_probs=False, gold=False):
    pos = (0, 0)
    sprite_close = 'imgs/dungeon_crawl/dungeon/chest_2_closed.png'
    sprite_open = 'imgs/dungeon_crawl/dungeon/chest_2_open.png'
    if item_set:
        potential_items = item_set
    else:
        potential_items = []
        if not nb_items:
            nb_items = rd.randint(1, 10)
        for i in range(nb_items):
            if gold:
                item = random_item_or_gold()
            else:
                item = random_item()
            if not equal_probs:
                prob = rd.random()
            else:
                prob = 1 / nb_items
            potential_items.append((item, prob))
    return Chest(pos, sprite_close, sprite_open, potential_items)
