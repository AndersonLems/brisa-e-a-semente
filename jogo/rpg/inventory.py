"""Inventário de consumíveis."""
from .items import BY_ID


class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, item_id, n=1):
        self.items[item_id] = self.items.get(item_id, 0) + n

    def count(self, item_id):
        return self.items.get(item_id, 0)

    def use(self, item_id, player, level=None):
        if self.count(item_id) <= 0:
            return False
        if not BY_ID[item_id].use(player, level):
            return False
        self.items[item_id] -= 1
        return True

    def to_dict(self):
        return dict(self.items)

    @classmethod
    def from_dict(cls, data):
        inv = cls()
        inv.items = {k: int(v) for k, v in data.items() if k in BY_ID}
        return inv
