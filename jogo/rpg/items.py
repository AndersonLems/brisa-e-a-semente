"""Itens de RPG vendidos pelo mercador: consumíveis, equipamentos e vidas."""


class RPGItem:
    id = ""
    name = ""
    description = ""
    price = 0

    def can_buy(self, progress):
        """Devolve (pode_comprar, motivo)."""
        if progress.stats.coins < self.price:
            return False, "Sementes insuficientes"
        return True, ""

    def buy(self, progress):
        progress.stats.coins -= self.price
        self.on_buy(progress)

    def on_buy(self, progress):
        raise NotImplementedError

    def status_label(self, progress):
        return ""


class Consumable(RPGItem):
    """Vai para o inventário e é usado depois."""

    def on_buy(self, progress):
        progress.inventory.add(self.id)

    def status_label(self, progress):
        return f"x{progress.inventory.count(self.id)}"

    def use(self, player, level):
        """Aplica o efeito; devolve False se não fez sentido usar agora."""
        raise NotImplementedError


class HealthPotion(Consumable):
    id = "pocao_vida"
    name = "Poção de Vida"
    description = "Recupera 15 HP. Use com a tecla 1."
    price = 8
    HEAL = 15

    def use(self, player, level):
        if player.hp >= player.max_hp:
            return False
        healed = player.heal(self.HEAL)
        if level:
            level.particles.text(player.centerx, player.y - 10, f"+{healed} HP", (255, 120, 140))
        return True


class ManaElixir(Consumable):
    id = "elixir_mana"
    name = "Elixir de Mana"
    description = "Recupera 10 MP. Use com a tecla 2."
    price = 6
    RESTORE = 10

    def use(self, player, level):
        if player.mp >= player.stats.max_mp:
            return False
        before = player.mp
        player.mp = min(player.stats.max_mp, player.mp + self.RESTORE)
        if level:
            level.particles.text(player.centerx, player.y - 10, f"+{player.mp - before} MP", (120, 180, 255))
        return True


class Equipment(RPGItem):
    """Melhoria permanente, comprada uma única vez."""
    attack = 0
    defense = 0
    hp = 0

    def can_buy(self, progress):
        if self.id in progress.stats.upgrades:
            return False, "Você já possui"
        return super().can_buy(progress)

    def on_buy(self, progress):
        st = progress.stats
        st.upgrades.add(self.id)
        st.bonus_attack += self.attack
        st.bonus_defense += self.defense
        st.bonus_hp += self.hp

    def status_label(self, progress):
        return "ADQUIRIDO" if self.id in progress.stats.upgrades else ""


class WindBlade(Equipment):
    id = "lamina_vento"
    name = "Lâmina de Vento"
    description = "Ponta de cristal para o cajado. +2 de ataque."
    price = 25
    attack = 2


class BarkAmulet(Equipment):
    id = "amuleto_casca"
    name = "Amuleto de Casca"
    description = "Feito da casca do ipê-roxo. +1 de defesa."
    price = 20
    defense = 1


class IpeHeart(Equipment):
    id = "coracao_ipe"
    name = "Coração de Ipê"
    description = "Uma flor eterna que fortalece a alma. +10 HP máximo."
    price = 30
    hp = 10


class ExtraLife(RPGItem):
    id = "folha_vida"
    name = "Folha da Vida"
    description = "Ganha uma vida extra imediatamente."
    price = 20

    def on_buy(self, progress):
        progress.stats.lives += 1

    def status_label(self, progress):
        return f"vidas: {progress.stats.lives}"


CATALOG = [HealthPotion(), ManaElixir(), ExtraLife(), WindBlade(), BarkAmulet(), IpeHeart()]
BY_ID = {item.id: item for item in CATALOG}
