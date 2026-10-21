"""Atributos de RPG: nível, experiência, vida, mana, ataque e defesa."""


class Stats:
    ABILITIES = {
        2: "Rajada de Vento (C)",
        3: "Pulo Duplo",
        5: "Rajada Tripla",
    }

    def __init__(self):
        self.level = 1
        self.xp = 0
        self.base_hp = 20
        self.base_mp = 10
        self.base_attack = 2
        self.base_defense = 0
        self.bonus_hp = 0
        self.bonus_attack = 0
        self.bonus_defense = 0
        self.coins = 0
        self.lives = 3
        self.upgrades = set()

    # --- totais (base + equipamentos) ------------------------------------
    @property
    def max_hp(self):
        return self.base_hp + self.bonus_hp

    @property
    def max_mp(self):
        return self.base_mp

    @property
    def attack(self):
        return self.base_attack + self.bonus_attack

    @property
    def defense(self):
        return self.base_defense + self.bonus_defense

    # --- habilidades desbloqueadas por nível -----------------------------
    @property
    def has_magic(self):
        return self.level >= 2

    @property
    def has_double_jump(self):
        return self.level >= 3

    @property
    def has_triple_bolt(self):
        return self.level >= 5

    # --- experiência -----------------------------------------------------
    def xp_to_next(self):
        return 12 + (self.level - 1) * 10

    def gain_xp(self, amount):
        """Soma XP e devolve a lista de novos níveis alcançados."""
        self.xp += amount
        gained = []
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level += 1
            self.base_hp += 5
            self.base_mp += 2
            self.base_attack += 1
            if self.level % 2 == 1:
                self.base_defense += 1
            gained.append(self.level)
        return gained

    # --- persistência ----------------------------------------------------
    FIELDS = ("level", "xp", "base_hp", "base_mp", "base_attack", "base_defense",
              "bonus_hp", "bonus_attack", "bonus_defense", "coins", "lives")

    def to_dict(self):
        data = {f: getattr(self, f) for f in self.FIELDS}
        data["upgrades"] = sorted(self.upgrades)
        return data

    @classmethod
    def from_dict(cls, data):
        st = cls()
        for f in cls.FIELDS:
            if f in data:
                setattr(st, f, data[f])
        st.upgrades = set(data.get("upgrades", []))
        return st
