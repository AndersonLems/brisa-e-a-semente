"""Progresso do jogador e salvamento em disco (JSON)."""
import json
import os

from ..config import SAVE_FILE
from .inventory import Inventory
from .stats import Stats


class Progress:
    def __init__(self):
        self.stats = Stats()
        self.inventory = Inventory()
        self.inventory.add("pocao_vida", 1)
        self.level_index = 0

    @staticmethod
    def has_save():
        return os.path.exists(SAVE_FILE)

    def save(self):
        os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
        data = {"level_index": self.level_index, "stats": self.stats.to_dict(),
                "inventory": self.inventory.to_dict()}
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls):
        prog = cls()
        try:
            with open(SAVE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            prog.stats = Stats.from_dict(data.get("stats", {}))
            prog.inventory = Inventory.from_dict(data.get("inventory", {}))
            prog.level_index = int(data.get("level_index", 0))
        except (OSError, ValueError):
            pass
        return prog
